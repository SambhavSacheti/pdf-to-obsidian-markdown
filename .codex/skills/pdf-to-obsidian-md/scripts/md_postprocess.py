"""Post-processing utilities for Obsidian-flavoured Markdown."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable, List, Optional


@dataclass
class LineInfo:
    text: str
    font_size: float
    font_name: str
    x0: float
    y0: float
    is_mono: bool


def _median_font_size(lines: Iterable[LineInfo]) -> float:
    sizes = [line.font_size for line in lines]
    return median(sizes) if sizes else 0.0


def _heading_level(line: LineInfo, body_size: float) -> Optional[int]:
    if body_size <= 0:
        return None
    if line.font_size >= body_size * 1.6:
        return 1
    if line.font_size >= body_size * 1.35:
        return 2
    if line.font_size >= body_size * 1.15:
        return 3
    return None


def _symbol_density(text: str) -> float:
    if not text:
        return 0.0
    symbols = sum(1 for ch in text if not ch.isalnum() and not ch.isspace())
    return symbols / max(len(text), 1)


def _is_code_line(line: LineInfo) -> bool:
    if line.is_mono:
        return True
    if line.text.startswith("    "):
        return True
    if _symbol_density(line.text) > 0.2 and len(line.text) > 6:
        return True
    return False


def _callout_for(text: str) -> Optional[str]:
    lowered = text.lower()
    if lowered.startswith("note:"):
        return "note"
    if lowered.startswith("warning:"):
        return "warning"
    if lowered.startswith("tip:"):
        return "tip"
    if lowered.startswith("important:"):
        return "important"
    return None


def build_markdown(
    lines: List[LineInfo],
    page_number: int,
    images: List[dict],
    tables: List[dict],
    ocr_used: bool,
    default_code_language: str = "csharp",
) -> List[str]:
    body_size = _median_font_size(lines)
    output: List[str] = [f"<!-- page: {page_number} -->"]

    if ocr_used:
        output.extend([
            "> [!note]",
            "> OCR-derived content for this page.",
            "",
        ])

    in_code_block = False
    for line in lines:
        text = line.text.strip()
        if not text:
            if in_code_block:
                output.append("")
            continue

        if _is_code_line(line):
            if not in_code_block:
                output.append(f"```{default_code_language}")
                in_code_block = True
            output.append(line.text.rstrip())
            continue

        if in_code_block:
            output.append("```")
            output.append("")
            in_code_block = False

        callout = _callout_for(text)
        if callout:
            body = text.split(":", 1)[-1].strip()
            output.extend([f"> [!{callout}]", f"> {body}", ""])
            continue

        heading_level = _heading_level(line, body_size)
        if heading_level:
            output.append(f"{'#' * heading_level} {text}")
        else:
            output.append(text)

    if in_code_block:
        output.append("```")
        output.append("")

    if images:
        output.append("")
        for image in images:
            alt_text = image.get("caption") or f"Page {page_number} image"
            output.append(f"![{alt_text}]({image['path']})")
        output.append("")

    if tables:
        output.append("")
        for table in tables:
            if table.get("markdown"):
                output.append(table["markdown"])
                output.append("")
            elif table.get("csv_path"):
                output.append(f"[Table data]({table['csv_path']})")
                output.append("")

    return output


def generate_toc(markdown_lines: List[str]) -> List[str]:
    toc_lines: List[str] = []
    for line in markdown_lines:
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            anchor = title.lower().replace(" ", "-")
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return toc_lines


def insert_toc(markdown_lines: List[str]) -> List[str]:
    toc = generate_toc(markdown_lines)
    output: List[str] = []
    inserted = False
    for line in markdown_lines:
        output.append(line)
        if line.strip() == "<!-- toc -->" and not inserted:
            output.extend(toc)
            output.append("")
            inserted = True
    return output
