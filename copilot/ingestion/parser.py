from pathlib import Path
from pypdf import PdfReader


def parse_markdown(file_path: Path) -> dict:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return {
        "file": file_path.name,
        "type": "markdown",
        "text": text.strip()
    }


def parse_pdf(file_path: Path) -> dict:
    reader = PdfReader(str(file_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        pages.append({"page": i, "text": extracted.strip()})
    full_text = "\n".join(p["text"] for p in pages)
    return {
        "file": file_path.name,
        "type": "pdf",
        "text": full_text.strip(),
        "pages": pages
    }


def parse_file(file_path: Path) -> dict | None:
    suffix = file_path.suffix.lower()
    if suffix == ".md":
        return parse_markdown(file_path)
    elif suffix == ".pdf":
        return parse_pdf(file_path)
    return None