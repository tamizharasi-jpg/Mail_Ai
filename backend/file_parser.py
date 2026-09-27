"""Safe, non-executing extraction for supported email document formats."""
from __future__ import annotations

import csv
import io
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader


ALLOWED = {".eml", ".txt", ".pdf", ".docx", ".csv"}
MAX_BYTES = 8 * 1024 * 1024

_SENDER_KEYS = ("sender", "from", "from_email", "sender_email", "email")
_SUBJECT_KEYS = ("subject", "title", "email_subject")
_BODY_KEYS = ("body", "message", "text", "content", "email_body", "email")


def parse_upload(filename: str, data: bytes) -> list[dict[str, str]]:
    """Return a list of parseable emails.

    A single file can contain multiple messages (CSV rows or several inline
    emails in a text file); each one becomes its own analysis record downstream.
    """
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Unsupported file. Use .eml, .txt, .pdf, .docx, or .csv.")
    if not data or len(data) > MAX_BYTES:
        raise ValueError("File is empty or larger than the 8 MB limit.")
    if suffix == ".eml":
        return [_parse_eml(data)]
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        body = "\n".join(page.extract_text() or "" for page in reader.pages)
        return [{"sender": "", "subject": Path(filename).stem, "body": body.strip()}]
    if suffix == ".docx":
        document = Document(io.BytesIO(data))
        body = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return [{"sender": "", "subject": Path(filename).stem, "body": body.strip()}]
    if suffix == ".csv":
        return _parse_csv(data, filename)
    return _parse_text(data, filename)


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


def _parse_text(data: bytes, filename: str) -> list[dict[str, str]]:
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        raise ValueError("The text file is empty.")
    blocks = _split_text_emails(text)
    parsed = [_extract_text_block(block, filename) for block in blocks]
    return [entry for entry in parsed if entry["body"] or entry["subject"]]


def _split_text_emails(text: str) -> list[str]:
    """Split a plain-text document into individual email blocks."""
    if re.match(r"^From ", text, re.MULTILINE):
        parts = [p.strip() for p in re.split(r"\n(?=From )", text) if p.strip()]
        if len(parts) > 1:
            return parts
    from_headers = re.findall(r"(?mi)^From:\s", text)
    if len(from_headers) >= 2:
        parts = [p.strip() for p in re.split(r"\n(?=From:\s)", text, flags=re.IGNORECASE) if p.strip()]
        if len(parts) > 1:
            return parts
    for delim in ("\n---\n", "\n===\n", "\n***\n", "\n===EMAIL===\n"):
        if delim in text:
            parts = [p.strip() for p in text.split(delim) if p.strip()]
            if len(parts) > 1:
                return parts
    return [text]


def _extract_text_block(block: str, filename: str) -> dict[str, str]:
    lines = block.splitlines()
    sender = _first_header(lines, "from")
    subject = _first_header(lines, "subject") or Path(filename).stem
    body = _strip_headers(block)
    return {"sender": sender, "subject": subject, "body": body.strip()}


def _first_header(lines: list[str], name: str) -> str:
    prefix = f"{name.lower()}:"
    for line in lines[:40]:
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def _strip_headers(block: str) -> str:
    header_re = re.compile(r"^(?:from|to|cc|bcc|subject|date|reply-to|content-type|mime-version|message-id):", re.IGNORECASE)
    lines = block.splitlines()
    body_start = 0
    in_headers = True
    for i, line in enumerate(lines):
        if in_headers and (not line.strip() or not header_re.match(line)):
            body_start = i + 1 if not line.strip() else i
            break
        if not header_re.match(line):
            in_headers = False
            body_start = i
            break
    body = "\n".join(lines[body_start:]).strip()
    return body or block.strip()


def _parse_csv(data: bytes, filename: str) -> list[dict[str, str]]:
    """One email per CSV row. Columns are matched case-insensitively."""
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV must include a header row with subject or body columns.")
    normalized = {(name or "").strip().lower(): name for name in reader.fieldnames if name}
    sender_key = next((normalized[k] for k in _SENDER_KEYS if k in normalized), None)
    subject_key = next((normalized[k] for k in _SUBJECT_KEYS if k in normalized), None)
    body_key = next((normalized[k] for k in _BODY_KEYS if k in normalized), None)
    if not subject_key and not body_key:
        raise ValueError("CSV needs at least a subject, body, message, text, or content column.")
    rows: list[dict[str, str]] = []
    stem = Path(filename).stem
    for index, row in enumerate(reader, start=1):
        sender = (row.get(sender_key) or "").strip() if sender_key else ""
        subject = (row.get(subject_key) or "").strip() if subject_key else ""
        body = (row.get(body_key) or "").strip() if body_key else ""
        if not subject and not body:
            continue
        rows.append({"sender": sender, "subject": subject or f"{stem} row {index}", "body": body})
    if not rows:
        raise ValueError("CSV contained no rows with subject or body content.")
    return rows
