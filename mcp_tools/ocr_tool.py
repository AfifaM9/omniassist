"""OCR tooling backed by the host Tesseract binary.

Tesseract is invoked as a subprocess instead of through a Python binding
(``pytesseract``) so the agent keeps working on hosts where only the CLI
package is installed. Every entry point degrades to a readable error string
rather than raising, matching the other tools in this package.
"""

import os
import shutil
import subprocess
import tempfile

TESSERACT_TIMEOUT = 120
DEFAULT_LANGUAGE = "eng"
SUPPORTED_IMAGE_EXTENSIONS = {
    ".bmp", ".gif", ".jpe", ".jpeg", ".jpg", ".pbm", ".pgm", ".png",
    ".pnm", ".ppm", ".tif", ".tiff", ".webp",
}


def _tesseract_binary():
    """Returns the path to the tesseract binary, or None when unavailable."""
    return shutil.which("tesseract")


def _available_languages():
    """Returns the set of language codes Tesseract can currently load."""
    binary = _tesseract_binary()
    if not binary:
        return set()
    try:
        result = subprocess.run(
            [binary, "--list-langs"], capture_output=True, text=True, timeout=TESSERACT_TIMEOUT
        )
    except Exception:
        return set()
    lines = (result.stdout or "").splitlines()
    return {line.strip() for line in lines[1:] if line.strip()}


def ocr_languages() -> str:
    """Lists the OCR language packs installed on this host."""
    if not _tesseract_binary():
        return "OCR unavailable: the 'tesseract' binary is not installed on this host."
    languages = sorted(_available_languages())
    if not languages:
        return "OCR available, but no language packs are installed."
    return f"Available OCR languages: {', '.join(languages)}"


def _validate(file_path: str, language: str):
    """Shared precondition checks. Returns an error string, or None when valid."""
    if not _tesseract_binary():
        return "OCR unavailable: the 'tesseract' binary is not installed on this host."
    if not file_path or not str(file_path).strip():
        return "OCR Error: no input file path was provided."
    if not os.path.isfile(file_path):
        return f"OCR Error: file not found: {file_path}"
    if not language or not str(language).strip():
        return "OCR Error: no OCR language was provided."
    languages = _available_languages()
    if languages and language not in languages:
        return (
            f"OCR Error: language '{language}' is not installed "
            f"(available: {', '.join(sorted(languages))})."
        )
    return None


def _run_tesseract(source_path: str, language: str) -> str:
    """Runs tesseract over a single image and returns the extracted text."""
    try:
        result = subprocess.run(
            [_tesseract_binary(), source_path, "stdout", "-l", language],
            capture_output=True,
            text=True,
            timeout=TESSERACT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"OCR Error: extraction timed out after {TESSERACT_TIMEOUT} seconds."
    except Exception as e:
        return f"OCR Error: {e}"

    text = (result.stdout or "").strip()
    if not text:
        detail = (result.stderr or "").strip().splitlines()
        hint = detail[-1] if detail else "no text recognised"
        return f"OCR produced no text (image may be blank or unreadable): {hint}"
    return text


def ocr_image(file_path: str, language: str = DEFAULT_LANGUAGE) -> str:
    """Extracts text from an image (or PDF) file using Tesseract OCR."""
    if str(file_path).lower().endswith(".pdf"):
        return ocr_pdf(file_path, language=language)

    error = _validate(file_path, language)
    if error:
        return error

    extension = os.path.splitext(file_path)[1].lower()
    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_EXTENSIONS))
        return f"OCR Error: unsupported image type '{extension}'. Supported: {supported}"

    return _run_tesseract(file_path, language)


def ocr_pdf(file_path: str, language: str = DEFAULT_LANGUAGE, max_pages: int = 5) -> str:
    """Extracts text from the first ``max_pages`` pages of a PDF via Tesseract."""
    error = _validate(file_path, language)
    if error:
        return error

    if not str(file_path).lower().endswith(".pdf"):
        return "OCR Error: ocr_pdf expects a .pdf file path."

    try:
        max_pages = max(1, int(max_pages))
    except (TypeError, ValueError):
        return "OCR Error: max_pages must be an integer."

    rasterizer = shutil.which("pdftoppm")
    if not rasterizer:
        return "OCR Error: PDF OCR requires 'pdftoppm' (poppler-utils), which is not installed."

    workdir = tempfile.mkdtemp(prefix="omniassist_ocr_")
    try:
        result = subprocess.run(
            [rasterizer, "-r", "200", "-png", "-l", str(max_pages), file_path, os.path.join(workdir, "page")],
            capture_output=True,
            text=True,
            timeout=TESSERACT_TIMEOUT,
        )
        if result.returncode != 0 and not os.listdir(workdir):
            detail = (result.stderr or "").strip().splitlines()
            return f"OCR Error: could not rasterise PDF: {detail[-1] if detail else 'unknown failure'}"

        pages = sorted(os.listdir(workdir))
        if not pages:
            return "OCR Error: PDF produced no renderable pages."

        chunks = []
        for index, page in enumerate(pages, start=1):
            text = _run_tesseract(os.path.join(workdir, page), language)
            chunks.append(f"--- page {index} ---\n{text}")
        return "\n\n".join(chunks)
    except subprocess.TimeoutExpired:
        return f"OCR Error: PDF rasterisation timed out after {TESSERACT_TIMEOUT} seconds."
    except Exception as e:
        return f"OCR Error: {e}"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
