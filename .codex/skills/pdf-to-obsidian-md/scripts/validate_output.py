"""Validate generated Obsidian Markdown output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List


def _balanced_code_fences(lines: List[str]) -> bool:
    fence_count = sum(1 for line in lines if line.strip().startswith("```"))
    return fence_count % 2 == 0


def _collect_image_paths(lines: List[str]) -> List[str]:
    paths: List[str] = []
    for line in lines:
        if line.startswith("![") and "](" in line:
            path = line.split("](", 1)[1].rstrip(")")
            paths.append(path)
    return paths


def validate_output(out_dir: Path) -> int:
    page_md = out_dir / "page.md"
    if not page_md.exists():
        print("page.md missing")
        return 1

    lines = page_md.read_text(encoding="utf-8").splitlines()
    errors = 0

    if not _balanced_code_fences(lines):
        print("Unbalanced code fences detected")
        errors += 1

    for path in _collect_image_paths(lines):
        if not (out_dir / path).exists():
            print(f"Missing image: {path}")
            errors += 1

    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "pages" not in manifest:
            print("Manifest missing pages entry")
            errors += 1

    if errors == 0:
        print("Validation passed")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate pdf-to-obsidian output")
    parser.add_argument("--out_dir", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(validate_output(args.out_dir))


if __name__ == "__main__":
    main()
