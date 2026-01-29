# PDF to Obsidian Design Notes

## Goals
- Stream page-by-page extraction to minimize memory usage.
- Preserve text layout and formatting (headings, code blocks, tables, images).
- Generate Obsidian-friendly Markdown with page markers.

## Heuristics
- Headings inferred by font-size ratios relative to page median size.
- Code blocks inferred by monospaced fonts, indentation, and symbol density.
- Callouts inferred by Note/Warning/Tip/Important prefixes.
- OCR only when text extraction yields minimal content.

## Output Layout
- `page.md` appended incrementally.
- `images/` and `tables/` contain extracted assets.
- `manifest.json` tracks per-page outputs and OCR usage.
- `metadata.json` stores PDF metadata.

## Performance
- Avoid full-document loads; process per-page with PyMuPDF.
- OCR and heavy operations optionally run in a worker process (accurate mode).
- Resume uses manifest.json to skip already processed pages unless `--force`.
