"""Convert PDFs into Obsidian-flavoured Markdown with extracted assets."""

from __future__ import annotations

import argparse
import json
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Optional, Tuple

import fitz  # PyMuPDF

from . import md_postprocess
from .md_postprocess import LineInfo
from .ocr_fallback import OcrResult, ocr_image_bytes, ocr_page
from .table_extract import extract_tables

MONO_HINTS = ("mono", "courier", "consolas", "code", "menlo")


def setup_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )


def parse_pages(pages: Optional[str], page_count: int) -> List[int]:
    if not pages:
        return list(range(1, page_count + 1))
    selected: List[int] = []
    for chunk in pages.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_str, end_str = chunk.split("-", 1)
            start = int(start_str)
            end = int(end_str)
            selected.extend(range(start, end + 1))
        else:
            selected.append(int(chunk))
    return [page for page in selected if 1 <= page <= page_count]


def extract_metadata(doc: fitz.Document) -> Dict[str, Optional[str]]:
    meta = doc.metadata
    return {
        "title": meta.get("title"),
        "author": meta.get("author"),
        "creator": meta.get("creator"),
        "producer": meta.get("producer"),
        "creationDate": meta.get("creationDate"),
        "modDate": meta.get("modDate"),
        "page_count": doc.page_count,
    }


def _is_mono_font(font_name: str) -> bool:
    lower = font_name.lower()
    return any(hint in lower for hint in MONO_HINTS)


def _extract_lines(page: fitz.Page) -> Tuple[List[LineInfo], List[Tuple[fitz.Rect, str]]]:
    text_dict = page.get_text("dict")
    lines: List[LineInfo] = []
    blocks_for_captions: List[Tuple[fitz.Rect, str]] = []

    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        block_bbox = fitz.Rect(block.get("bbox"))
        line_texts: List[str] = []
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            text = "".join(span.get("text", "") for span in spans)
            text = text.replace("\u00a0", " ")
            max_size = max(span.get("size", 0) for span in spans)
            font_name = spans[0].get("font", "")
            is_mono = any(_is_mono_font(span.get("font", "")) for span in spans)
            bbox = fitz.Rect(line.get("bbox"))
            lines.append(
                LineInfo(
                    text=text,
                    font_size=float(max_size),
                    font_name=font_name,
                    x0=float(bbox.x0),
                    y0=float(bbox.y0),
                    is_mono=is_mono,
                )
            )
            line_texts.append(text.strip())
        if line_texts:
            blocks_for_captions.append((block_bbox, " ".join(line_texts).strip()))

    lines.sort(key=lambda item: (item.y0, item.x0))
    return lines, blocks_for_captions


def _median_font_size(lines: Iterable[LineInfo]) -> float:
    sizes = [line.font_size for line in lines]
    return median(sizes) if sizes else 0.0


def _write_page_json(out_dir: Path, page_number: int, lines: List[LineInfo]) -> None:
    payload = {
        "page": page_number,
        "lines": [asdict(line) for line in lines],
    }
    json_path = out_dir / "logs" / f"page_{page_number:04d}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _select_caption(blocks: List[Tuple[fitz.Rect, str]], image_rect: fitz.Rect) -> Optional[str]:
    candidates = []
    for rect, text in blocks:
        if rect.y0 >= image_rect.y1 and rect.y0 - image_rect.y1 <= 60:
            candidates.append((rect.y0 - image_rect.y1, text))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def extract_images(
    doc: fitz.Document,
    page: fitz.Page,
    blocks: List[Tuple[fitz.Rect, str]],
    out_dir: Path,
    page_number: int,
) -> List[Dict[str, str]]:
    images: List[Dict[str, str]] = []
    image_list = page.get_images(full=True)
    for index, image in enumerate(image_list, start=1):
        xref = image[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        image_path = out_dir / "images" / f"p{page_number:04d}_img{index:02d}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(image_path))
        pix = None

        rects = page.get_image_rects(xref)
        caption = None
        if rects:
            caption = _select_caption(blocks, rects[0])
        images.append({"path": str(Path("images") / image_path.name), "caption": caption or ""})
    return images


def _should_ocr(lines: List[LineInfo], body_size: float) -> bool:
    text = " ".join(line.text for line in lines).strip()
    if len(text) < 20:
        return True
    if body_size == 0:
        return True
    return False


def _run_ocr(page: fitz.Page, mode: str) -> OcrResult:
    if mode == "accurate":
        pix = page.get_pixmap(dpi=300)
        image_bytes = pix.tobytes("png")
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(ocr_image_bytes, image_bytes, "eng")
            return future.result()
    return ocr_page(page, dpi=220, lang="eng")


def _insert_frontmatter(page_md: Path, metadata: Dict[str, Optional[str]]) -> None:
    if page_md.exists():
        return
    title = metadata.get("title") or "PDF Notes"
    frontmatter = [
        "---",
        f"title: {title}",
        "---",
        "",
        "<!-- toc -->",
        "",
    ]
    page_md.write_text("\n".join(frontmatter), encoding="utf-8")


def process_pdf(
    input_path: Path,
    out_dir: Path,
    mode: str,
    pages: Optional[str],
    force: bool,
    toc: bool,
) -> None:
    start_time = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "tables").mkdir(parents=True, exist_ok=True)
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)

    setup_logging(out_dir / "logs" / "extraction.log")

    doc = fitz.open(str(input_path))
    metadata = extract_metadata(doc)

    metadata_path = out_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists() and not force:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"pages": {}, "warnings": [], "ocr_pages": []}

    page_md = out_dir / "page.md"
    if force and page_md.exists():
        page_md.unlink()

    _insert_frontmatter(page_md, metadata)

    selected_pages = parse_pages(pages, doc.page_count)
    for page_number in selected_pages:
        if str(page_number) in manifest.get("pages", {}):
            logging.info("Skipping page %s (already processed)", page_number)
            continue

        logging.info("Processing page %s", page_number)
        page = doc.load_page(page_number - 1)
        lines, caption_blocks = _extract_lines(page)
        body_size = _median_font_size(lines)

        ocr_result = OcrResult(text="", used_ocr=False, engine=None)
        if _should_ocr(lines, body_size):
            ocr_result = _run_ocr(page, mode)
            if ocr_result.used_ocr and ocr_result.text:
                lines.append(
                    LineInfo(
                        text=ocr_result.text,
                        font_size=body_size or 10.0,
                        font_name="OCR",
                        x0=0.0,
                        y0=float(page.rect.y1),
                        is_mono=False,
                    )
                )

        lines.sort(key=lambda item: (item.y0, item.x0))
        _write_page_json(out_dir, page_number, lines)

        images = extract_images(doc, page, caption_blocks, out_dir, page_number)

        tables = []
        for table in extract_tables(input_path, page_number, out_dir / "tables", mode):
            tables.append(
                {
                    "markdown": table.markdown,
                    "csv_path": str(Path("tables") / table.csv_path.name) if table.csv_path else None,
                    "engine": table.engine,
                }
            )

        markdown_lines = md_postprocess.build_markdown(
            lines,
            page_number,
            images=images,
            tables=tables,
            ocr_used=ocr_result.used_ocr,
        )
        with page_md.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(markdown_lines))
            handle.write("\n")

        manifest["pages"][str(page_number)] = {
            "images": images,
            "tables": tables,
            "ocr": ocr_result.used_ocr,
        }
        if ocr_result.used_ocr:
            manifest["ocr_pages"].append(page_number)

        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if toc and page_md.exists():
        page_lines = page_md.read_text(encoding="utf-8").splitlines()
        updated = md_postprocess.insert_toc(page_lines)
        page_md.write_text("\n".join(updated), encoding="utf-8")

    duration = time.time() - start_time
    manifest["duration_seconds"] = duration
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PDF to Obsidian Markdown")
    parser.add_argument("--input", required=True, type=Path, help="Input PDF path")
    parser.add_argument("--out_dir", required=True, type=Path, help="Output directory")
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast")
    parser.add_argument("--pages", help="Page selection, e.g. 1-3,5")
    parser.add_argument("--force", action="store_true", help="Force reprocessing")
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    args = parser.parse_args()

    process_pdf(args.input, args.out_dir, args.mode, args.pages, args.force, args.toc)


if __name__ == "__main__":
    main()
