"""Exact checks on model output. Nothing a subagent writes is used before passing through here."""
import re
from functools import lru_cache
from pathlib import Path

from .parse import raw_path_for, read_text

MIN_QUOTE_WORDS = 5
MAX_QUOTE_WORDS = 60
KINDS = {"request", "fulfillment", "report", "escalation", "followup", "fyi", "none"}
_WS = re.compile(r"\s+")


def norm(s: str) -> str:
    """Whitespace-insensitive form used on both sides of every quote check (bodies hard-wrap at ~76 cols)."""
    return _WS.sub(" ", s).strip()


@lru_cache(maxsize=4096)
def _norm_raw(path: str) -> str:
    return norm(read_text(Path(path)))


def quote_error(quote, msg_id: str, corpus: Path) -> str | None:
    """None when the quote is a verbatim (whitespace-normalized) substring of the message's raw file."""
    if not isinstance(quote, str) or not quote.strip():
        return "missing quote"
    n = len(quote.split())
    if not MIN_QUOTE_WORDS <= n <= MAX_QUOTE_WORDS:
        return f"quote has {n} words (need {MIN_QUOTE_WORDS}-{MAX_QUOTE_WORDS})"
    # no separate ellipsis rule: an elided quote fails the substring check, and some bodies contain "...." verbatim
    raw = raw_path_for(msg_id, corpus)
    if not raw.is_file():
        return f"no raw file for {msg_id}"
    if norm(quote) not in _norm_raw(str(raw)):
        return "quote not found verbatim in raw file"
    return None


def label_schema_errors(label) -> list[str]:
    if not isinstance(label, dict):
        return ["label is not an object"]
    errs = []
    if not isinstance(label.get("msg_id"), str):
        errs.append("msg_id missing")
    proc = label.get("process")
    if not isinstance(proc, str) or not proc.strip():
        errs.append("process missing")
        return errs
    if proc == "none":
        return errs
    if not re.fullmatch(r"[a-z0-9_]{3,60}", proc):
        errs.append(f"process {proc!r} is not snake_case")
    if label.get("kind") not in KINDS:
        errs.append(f"kind {label.get('kind')!r} invalid")
    m = label.get("minutes_estimate")
    if isinstance(m, bool) or not isinstance(m, (int, float)) or not 0 <= m <= 480:
        errs.append("minutes_estimate must be a number in 0-480")
    for f in ("process_description", "manual_steps", "stall_signal", "quote"):
        if not isinstance(label.get(f), str):
            errs.append(f"{f} must be a string")
    return errs
