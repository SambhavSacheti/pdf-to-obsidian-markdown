"""OCR fallback helpers for scanned or empty PDF pages."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OcrResult:
    text: str
    used_ocr: bool
    engine: Optional[str] = None


def _tesseract_available() -> bool:
    return importlib.util.find_spec("pytesseract") is not None


def _ocr_bytes(image_bytes: bytes, lang: str) -> str:
    import pytesseract  # type: ignore

    try:
        return pytesseract.image_to_string(image_bytes, lang=lang)
    except TypeError:
        from PIL import Image  # type: ignore
        from io import BytesIO

        image = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang=lang)


def ocr_page(page, dpi: int = 250, lang: str = "eng") -> OcrResult:
    """Run OCR on a PyMuPDF page.

    Args:
        page: fitz.Page instance.
        dpi: Render DPI for OCR.
        lang: Tesseract language.
    """
    if not _tesseract_available():
        return OcrResult(text="", used_ocr=False, engine=None)

    pix = page.get_pixmap(dpi=dpi)
    image_bytes = pix.tobytes("png")
    text = _ocr_bytes(image_bytes, lang)
    return OcrResult(text=text.strip(), used_ocr=True, engine="tesseract")


def ocr_image_bytes(image_bytes: bytes, lang: str = "eng") -> OcrResult:
    if not _tesseract_available():
        return OcrResult(text="", used_ocr=False, engine=None)
    text = _ocr_bytes(image_bytes, lang)
    return OcrResult(text=text.strip(), used_ocr=True, engine="tesseract")
