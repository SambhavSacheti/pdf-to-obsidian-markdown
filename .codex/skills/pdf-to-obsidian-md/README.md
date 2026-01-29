# pdf-to-obsidian-md

Convert long software-engineering PDFs into a single Obsidian-flavoured Markdown file with extracted images and tables.

## Quick start

```bash
python -m scripts.pdf_to_obsidian --input path/to/doc.pdf --out_dir out
```

## Outputs

```
<out_dir>/
  page.md
  images/
  tables/
  metadata.json
  manifest.json
  logs/extraction.log
```

## Optional flags

- `--mode fast|accurate`: Use accurate mode for better OCR/table extraction.
- `--pages 1-3,8`: Process a subset of pages.
- `--force`: Re-run extraction from scratch.
- `--toc`: Insert a generated table of contents into `page.md`.
