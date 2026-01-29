from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def _build_pdf(pdf_path: Path, image_path: Path) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, "Sample Heading")
    c.setFont("Helvetica", 11)
    c.drawString(72, 690, "Note: This is a note for Obsidian.")
    c.setFont("Courier", 10)
    c.drawString(72, 660, "public void HelloWorld() {")
    c.drawString(72, 645, "    Console.WriteLine(\"Hi\");")
    c.drawString(72, 630, "}")
    c.drawImage(str(image_path), 72, 540, width=120, height=60)
    c.showPage()
    c.save()


def _build_image(image_path: Path) -> None:
    from PIL import Image

    image = Image.new("RGB", (120, 60), color=(120, 160, 200))
    image.save(image_path)


def test_smoke(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    image_path = tmp_path / "sample.png"
    _build_image(image_path)
    _build_pdf(pdf_path, image_path)

    out_dir = tmp_path / "out"
    skill_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.pdf_to_obsidian",
            "--input",
            str(pdf_path),
            "--out_dir",
            str(out_dir),
            "--mode",
            "fast",
        ],
        cwd=skill_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    page_md = out_dir / "page.md"
    assert page_md.exists()
    content = page_md.read_text(encoding="utf-8")
    assert "Sample Heading" in content
    assert "```csharp" in content
    assert "<!-- page: 1 -->" in content

    image_dir = out_dir / "images"
    referenced = [line for line in content.splitlines() if line.startswith("![")]
    assert referenced, "Expected image reference in markdown"
    assert any(path.suffix == ".png" for path in image_dir.iterdir())
