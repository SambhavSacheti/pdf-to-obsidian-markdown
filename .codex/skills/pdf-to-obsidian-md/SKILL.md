---
name: pdf-to-obsidian-md
description: Convert a PDF (especially long software-engineering documentation) into Obsidian-flavoured Markdown with preserved headings, code blocks, tables, and extracted images; use when asked to transform PDFs into Markdown notes.
---

# PDF to Obsidian Markdown

Use this skill to convert long, technical PDFs into a single Obsidian-ready Markdown document with extracted assets and validation.

## When to use this skill

- Convert a large software engineering PDF book into Obsidian Markdown.
- Extract text, code blocks, tables, and images into structured Markdown.

## Inputs, outputs, constraints

- **Inputs**: PDF file path
- **Outputs**: `page.md`, `images/`, `metadata.json`, `manifest.json`, `logs/extraction.log`.
- **Constraints**: Stream page-by-page; avoid full in-memory loads; write incremental outputs; preserve text verbatim.

## Command examples

```bash
python -m scripts.pdf_to_obsidian --input docs/guide.pdf --out_dir out
python -m scripts.pdf_to_obsidian --input docs/guide.pdf --out_dir out --mode accurate
python -m scripts.pdf_to_obsidian --input docs/guide.pdf --out_dir out --pages 1-5,12
python -m scripts.pdf_to_obsidian --input docs/guide.pdf --out_dir out --force --toc
```

## Workflow

1. **Extract metadata** with PyMuPDF and write `metadata.json`.
2. **Process pages sequentially**:
   - Extract text blocks, spans, bounding boxes, and font info.
   - Detect headings.
   - Extract images (full resolution) and nearby captions.
   - Extract tables with `camelot` or `pdfplumber` if available.
   - Extract code blocks (critical)
     - Detect csharp code blocks using the keywords dictionary `references/csharp-keywords.md`
     - Detect code using heuristics:
       - monospaced fonts
       - indentation patterns
       - symbol density
       - preserve verbatim text
       - fence with language tag
       - default language: csharp
   - Append Markdown for each page with `<!-- page: N -->` markers.
3. **Post-process** to Obsidian Markdown:
   - Convert Note/Warning/Tip/Important blocks into callouts.
   - Preserve code blocks with fences and language tag.
   - Include image links and table markdown/CSV fallback.
4. **Validate** using `scripts/validate_output.py` when needed.
5. **Resume support**: reuse `manifest.json` unless `--force` is set.

## Obsidian Markdown rules

- Use standard Markdown headings (`#`, `##`, `###`).
- Use callouts: `> [!note]`, `> [!warning]`, `> [!tip]`, `> [!important]`.
- Use fenced code blocks with language (default `csharp`).
- Embed images as `![alt](images/p0001_img01.png)`.
- Keep page markers `<!-- page: N -->`.
- Avoid paraphrasing or rewriting text.

## Troubleshooting

- **Tables missing**: install `pdfplumber` or `camelot-py[cv]` for better extraction.
- **Incorrect headings**: adjust font-size heuristics in `scripts/md_postprocess.py`.
- **Resume issues**: delete `manifest.json` or use `--force` to regenerate.

## Resources

- `scripts/pdf_to_obsidian.py`: main entry point.
- `scripts/table_extract.py`: table extraction helpers.
- `scripts/md_postprocess.py`: Markdown post-processing.
- `scripts/validate_output.py`: output validation.
- `assets/md_template.md`: starter Markdown template.
- `references/design-notes.md`: heuristic notes and design decisions.
