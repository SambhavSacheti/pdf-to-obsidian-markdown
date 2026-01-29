"""Table extraction helpers with graceful degradation."""

from __future__ import annotations

import csv
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class TableResult:
    index: int
    markdown: Optional[str]
    csv_path: Optional[Path]
    engine: str


def _camelot_available() -> bool:
    return importlib.util.find_spec("camelot") is not None


def _pdfplumber_available() -> bool:
    return importlib.util.find_spec("pdfplumber") is not None


def _rows_to_markdown(rows: List[List[str]]) -> Optional[str]:
    if not rows:
        return None
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []
    header_line = "| " + " | ".join(cell.strip() for cell in header) + " |"
    separator = "| " + " | ".join("---" for _ in header) + " |"
    lines = [header_line, separator]
    for row in body:
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(cell.strip() for cell in padded) + " |")
    return "\n".join(lines)


def _write_csv(rows: List[List[str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def extract_tables(pdf_path: Path, page_number: int, out_dir: Path, mode: str) -> List[TableResult]:
    results: List[TableResult] = []
    table_index = 1

    if mode == "accurate" and _camelot_available():
        import camelot  # type: ignore

        tables = camelot.read_pdf(str(pdf_path), pages=str(page_number))
        for table in tables:
            csv_path = out_dir / f"p{page_number:04d}_table{table_index:02d}.csv"
            table.to_csv(str(csv_path), index=False)
            markdown = _rows_to_markdown(table.data)
            results.append(TableResult(index=table_index, markdown=markdown, csv_path=csv_path, engine="camelot"))
            table_index += 1

    if results:
        return results

    if _pdfplumber_available():
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(pdf_path)) as pdf:
            page = pdf.pages[page_number - 1]
            tables = page.extract_tables()
            for rows in tables or []:
                csv_path = out_dir / f"p{page_number:04d}_table{table_index:02d}.csv"
                _write_csv(rows, csv_path)
                markdown = _rows_to_markdown(rows)
                results.append(TableResult(index=table_index, markdown=markdown, csv_path=csv_path, engine="pdfplumber"))
                table_index += 1

    return results
