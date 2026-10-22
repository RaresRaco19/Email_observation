"""Parse one raw Enron export file. Only the top-level header block is used for metadata."""
import re
from email.parser import HeaderParser
from email.utils import getaddresses, parsedate_to_datetime
from datetime import timezone
from pathlib import Path

from . import config

# Start of quoted/forwarded history inside a body. Everything from the earliest match on is "quoted".
QUOTE_MARKERS = [
    re.compile(r"^[ \t]*-{3,}\s*Original Message\s*-{3,}", re.M | re.I),
    re.compile(r"^[ \t]*-{5,}\s*Forwarded by", re.M),
    # Lotus Notes reply header: a name line, then "MM/DD/YYYY HH:MM AM", then "To:"
    re.compile(r"^[^\n]*\S[^\n]*\n[ \t]*\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [AP]M[ \t]*\n[ \t]*To:", re.M),
    re.compile(r"^[ \t]*From:[^\n]*\n[ \t]*(Sent|Date):", re.M),
]
SUBJECT_PREFIX = re.compile(r"^\s*((re|fw|fwd)\s*:\s*)+", re.I)
MIN_NEW_TEXT = 20


def msg_id_for(path: Path, corpus: Path) -> str:
    rel = path.relative_to(corpus).as_posix()
    return rel[:-1] if rel.endswith(".") else rel


def raw_path_for(msg_id: str, corpus: Path) -> Path:
    return corpus / (msg_id + ".")


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def normalize_subject(subject: str) -> str:
    return " ".join(SUBJECT_PREFIX.sub("", subject or "").lower().split())


def split_new_text(body: str) -> tuple[str, str]:
    """Return (new_text, source). source is 'new' or 'body' (pure forwards fall back to the whole body)."""
    cut = min((m.start() for rx in QUOTE_MARKERS if (m := rx.search(body))), default=len(body))
    new = body[:cut].strip()
    if len(new) < MIN_NEW_TEXT:
        return body.strip(), "body"
    return new, "new"


def _addrs(value: str | None) -> list[str]:
    return [a.lower() for _, a in getaddresses([value or ""]) if a]


def parse_file(path: Path, corpus: Path) -> dict:
    text = read_text(path)
    head, sep, body = text.partition("\n\n")
    if not sep:
        head, body = text, ""
    h = HeaderParser().parsestr(head + "\n")
    date = None
    if h.get("Date"):
        try:
            date = parsedate_to_datetime(h["Date"]).astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError):
            date = None
    out_of_range = bool(date) and not config.DATE_RANGE[0] <= date[:10] <= config.DATE_RANGE[1]
    if out_of_range:
        date = None
    new_text, source = split_new_text(body)
    truncated = len(new_text) > config.MSG_MAX_CHARS
    mid = msg_id_for(path, corpus)
    return {
        "msg_id": mid,
        "mailbox": mid.split("/")[0],
        "folder": "/".join(mid.split("/")[:2]),
        "message_id_header": (h.get("Message-ID") or "").strip(),
        "date": date,
        "date_out_of_range": out_of_range,
        "from": (_addrs(h.get("From")) or [""])[0],
        "from_name": (h.get("X-From") or "").split("<")[0].strip(),
        "to": _addrs(h.get("To")),
        "cc": _addrs(h.get("Cc")),
        "subject": " ".join((h.get("Subject") or "").split()),
        "body": body,
        "new_text": new_text[: config.MSG_MAX_CHARS],
        "new_text_source": source,
        "truncated": truncated,
    }
