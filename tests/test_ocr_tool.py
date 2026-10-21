"""Tests for the Tesseract-backed OCR tool.

Image fixtures are generated with ImageMagick's ``convert`` so the suite does
not need to ship binary fixtures. Everything skips cleanly when the host lacks
the required binaries.
"""

import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_tools.ocr_tool import (
    _available_languages,
    ocr_image,
    ocr_languages,
    ocr_pdf,
)

HAVE_TESSERACT = shutil.which("tesseract") is not None
HAVE_CONVERT = shutil.which("convert") is not None


def make_image(path: Path, text: str) -> bool:
    """Renders ``text`` into a white PNG using ImageMagick. Returns success."""
    result = subprocess.run(
        [
            "convert", "-size", "900x260", "xc:white", "-pointsize", "40",
            "-fill", "black", "-annotate", "+25+110", text, str(path),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and path.exists()


@unittest.skipUnless(HAVE_TESSERACT, "tesseract binary not installed")
class TestOCRTool(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_languages_reported(self):
        result = ocr_languages()
        self.assertIn("Available OCR languages", result)
        self.assertIn("eng", result)

    def test_available_languages_non_empty(self):
        self.assertIn("eng", _available_languages())

    def test_missing_file_returns_error(self):
        result = ocr_image(str(self.tmp / "nope.png"))
        self.assertIn("file not found", result)

    def test_empty_path_returns_error(self):
        self.assertIn("no input file path", ocr_image(""))

    def test_unsupported_extension_returns_error(self):
        target = self.tmp / "notes.txt"
        target.write_text("plain text")
        self.assertIn("unsupported image type", ocr_image(str(target)))

    def test_unknown_language_returns_error(self):
        target = self.tmp / "img.png"
        target.write_bytes(b"not an image")
        self.assertIn("is not installed", ocr_image(str(target), language="klingon"))

    @unittest.skipUnless(HAVE_CONVERT, "ImageMagick convert not installed")
    def test_extracts_known_text(self):
        target = self.tmp / "sample.png"
        self.assertTrue(make_image(target, "OmniAssist OCR 391"))
        text = ocr_image(str(target))
        self.assertIn("OmniAssist", text)
        self.assertIn("391", text)

    @unittest.skipUnless(HAVE_CONVERT, "ImageMagick convert not installed")
    def test_blank_image_reports_no_text(self):
        target = self.tmp / "blank.png"
        subprocess.run(["convert", "-size", "300x120", "xc:white", str(target)], capture_output=True)
        self.assertIn("no text", ocr_image(str(target)))

    @unittest.skipUnless(HAVE_CONVERT, "ImageMagick convert not installed")
    def test_ocr_image_routes_pdf_extension(self):
        """A .pdf path must not be treated as an image."""
        target = self.tmp / "doc.pdf"
        target.write_bytes(b"%PDF-1.4 not really a pdf")
        result = ocr_image(str(target))
        self.assertNotIn("unsupported image type", result)

    def test_ocr_pdf_rejects_non_pdf(self):
        target = self.tmp / "img.png"
        target.write_bytes(b"x")
        self.assertIn("expects a .pdf", ocr_pdf(str(target)))

    @unittest.skipUnless(HAVE_CONVERT, "ImageMagick convert not installed")
    def test_ocr_pdf_bad_max_pages(self):
        target = self.tmp / "doc.pdf"
        target.write_bytes(b"%PDF-1.4")
        self.assertIn("max_pages must be an integer", ocr_pdf(str(target), max_pages="lots"))


@unittest.skipUnless(HAVE_TESSERACT and shutil.which("pdftoppm") and shutil.which("gs"), "pdf toolchain missing")
class TestOCRPDF(unittest.TestCase):
    """Builds a real PDF with Ghostscript and reads it back through the tool.

    ImageMagick cannot write PDFs on hosts where the Ghostscript delegate is
    disabled by security policy, so the fixture is produced directly by gs.
    """

    POSTSCRIPT = """%!PS
/Helvetica findfont 40 scalefont setfont
72 650 moveto (__TEXT__) show
showpage
"""

    def _make_pdf(self, tmp: Path, text: str) -> Path:
        ps_file = tmp / "page.ps"
        ps_file.write_text(self.POSTSCRIPT.replace("__TEXT__", text))
        pdf_file = tmp / "doc.pdf"
        subprocess.run(
            ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
             f"-sOutputFile={pdf_file}", str(ps_file)],
            capture_output=True, text=True, timeout=60,
        )
        return pdf_file

    def test_pdf_text_is_extracted(self):
        with TemporaryDirectory() as tmp:
            pdf = self._make_pdf(Path(tmp), "OmniAssist PDF 42")
            if not pdf.exists() or pdf.stat().st_size == 0:
                self.skipTest("ghostscript could not produce a PDF fixture")
            text = ocr_pdf(str(pdf), max_pages=1)
            self.assertIn("OmniAssist", text)
            self.assertIn("42", text)
            self.assertIn("page 1", text)

    def test_pdf_page_limit_respected(self):
        with TemporaryDirectory() as tmp:
            pdf = self._make_pdf(Path(tmp), "OmniAssist page one")
            if not pdf.exists() or pdf.stat().st_size == 0:
                self.skipTest("ghostscript could not produce a PDF fixture")
            text = ocr_pdf(str(pdf), max_pages=1)
            self.assertNotIn("page 2", text)

    def test_ocr_image_dispatches_pdf(self):
        with TemporaryDirectory() as tmp:
            pdf = self._make_pdf(Path(tmp), "OmniAssist dispatch")
            if not pdf.exists() or pdf.stat().st_size == 0:
                self.skipTest("ghostscript could not produce a PDF fixture")
            self.assertIn("OmniAssist", ocr_image(str(pdf)))


if __name__ == "__main__":
    unittest.main()
