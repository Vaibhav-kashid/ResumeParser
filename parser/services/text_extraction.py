"""Extract raw text from an uploaded PDF or DOCX resume file."""
import os

import pdfplumber
from docx import Document


def extract_text(file_path):
    """Return extracted plain text for a .pdf or .docx file.

    Raises ValueError for unsupported file types, and a plain
    Exception (bubbled up to the caller) if the file is corrupt.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext == ".docx":
        return _extract_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please upload a PDF or DOCX file.")


def _extract_from_pdf(file_path):
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    text = "\n".join(text_parts)
    if not text.strip():
        raise ValueError(
            "No extractable text found. This PDF may be a scanned image "
            "without a text layer (OCR is not yet supported)."
        )
    return text


def _extract_from_docx(file_path):
    document = Document(file_path)
    parts = [p.text for p in document.paragraphs if p.text.strip()]
    # Also pull text out of any tables in the resume
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    parts.append(cell.text)
    text = "\n".join(parts)
    if not text.strip():
        raise ValueError("No extractable text found in this DOCX file.")
    return text
