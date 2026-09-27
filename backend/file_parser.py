"""Safe, non-executing extraction for supported email document formats."""
from __future__ import annotations

import io
from email import policy
from email.parser import BytesParser
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader


ALLOWED = {".eml", ".txt", ".pdf", ".docx"}
MAX_BYTES = 8 * 1024 * 1024


def parse_upload(filename: str, data: bytes) -> dict[str, str]:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Unsupported file. Use .eml, .txt, .pdf, or .docx.")
    if not data or len(data) > MAX_BYTES:
        raise ValueError("File is empty or larger than the 8 MB limit.")
    if suffix == ".eml":
        return _parse_eml(data)
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        body = "\n".join(page.extract_text() or "" for page in reader.pages)
        return {"sender": "", "subject": Path(filename).stem, "body": body.strip()}
    if suffix == ".docx":
        document = Document(io.BytesIO(data))
        body = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return {"sender": "", "subject": Path(filename).stem, "body": body.strip()}
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    sender = next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("from:")), "")
    subject = next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("subject:")), Path(filename).stem)
    body = text if not sender and not subject else text
    return {"sender": sender, "subject": subject, "body": body.strip()}


def _parse_eml(data: bytes) -> dict[str, str]:
    message = BytesParser(policy=policy.default).parsebytes(data)
    parts: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                parts.append(part.get_content())
            elif part.get_content_type() == "text/html" and not part.get_filename() and not parts:
                parts.append(BeautifulSoup(part.get_content(), "html.parser").get_text(" "))
    else:
        content = message.get_content()
        parts.append(BeautifulSoup(content, "html.parser").get_text(" ") if message.get_content_type() == "text/html" else content)
    return {"sender": message.get("From", ""), "subject": message.get("Subject", ""), "body": "\n".join(parts).strip()}