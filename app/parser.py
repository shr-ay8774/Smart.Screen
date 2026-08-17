from io import BytesIO
from pathlib import Path
import re


def clean_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(file_bytes))

    return clean_text(
        "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    )


def extract_docx(file_bytes: bytes) -> str:
    from docx import Document

    document = Document(BytesIO(file_bytes))

    return clean_text(
        "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )
    )


def extract_resume(file_name: str, file_bytes: bytes) -> str:
    suffix = Path(file_name).suffix.lower()

    if suffix == ".pdf":
        return extract_pdf(file_bytes)

    if suffix == ".docx":
        return extract_docx(file_bytes)

    raise ValueError(
        "Unsupported file type. Upload PDF or DOCX."
    )
