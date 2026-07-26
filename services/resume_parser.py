from pathlib import Path

import fitz


class ResumeParseError(ValueError):
    pass


def extract_pdf_text(path):
    try:
        document = fitz.open(Path(path))
        if document.page_count == 0:
            raise ResumeParseError("This PDF has no pages.")
        text = "\n".join(page.get_text() for page in document)
        document.close()
    except (fitz.FileDataError, RuntimeError, OSError) as exc:
        raise ResumeParseError("The uploaded file is not a readable PDF.") from exc
    if not text.strip():
        raise ResumeParseError("This PDF does not contain selectable text. Upload a text-based resume PDF.")
    return text.strip()
