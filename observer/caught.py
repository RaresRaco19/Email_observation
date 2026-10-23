"""Ledger of subagent mistakes the validators caught before they reached the output (work/caught.json).

Every check-* stage records the errors it rejected. An entry is keyed by stage, item, the content hash of the
file that was checked, and the error text, so re-running a check on the same file does not count it twice,
while a retry that makes the same mistake again does count. Nothing here decides anything; it only counts.
"""
import re
from collections import Counter
from datetime import datetime, timezone

from .config import Paths
from .util import read_json, sha, write_json

# first match wins; the order puts specific patterns before generic ones
CATEGORIES = [
    (r"quotes failed verbatim check", "batch over the bad-quote limit"),
    (r"words \(need", "quote too short or too long"),
    (r"not found verbatim|blockquote is not verbatim", "quote not verbatim"),
    (r"messages have no label", "message skipped"),
    (r"is not in this batch", "label for a message not in the batch"),
    (r"duplicate label", "duplicate label"),
    (r"unmapped", "label left unmapped"),
    (r"map keys are not candidates|not existing or new process ids|duplicates an existing id", "process map inconsistent"),
    (r"remedy must be", "remedy outside the allowed set"),
    (r"not in the evidence file", "citation outside the evidence"),
    (r"is not mentioned in the evidence", "system not named in the evidence"),
    (r"dollar figure", "dollar figure not computed by code"),
    (r"front matter type must be", "artifact type not allowed"),
    (r"file missing|label file missing", "no output written"),
    (r"invalid JSON", "invalid JSON"),
]


def category(error: str) -> str:
    return next((name for pat, name in CATEGORIES if re.search(pat, error)), "schema or format")


def record(p: Paths, stage: str, item: str, errors: list[str], version: str = "") -> None:
    if not errors:
        return
    path = p.work / "caught.json"
    ledger = read_json(path, {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for e in errors:
        ledger.setdefault(sha(stage, item, version, e)[:16], {"stage": stage, "item": item, "error": e[:300],
                                                             "category": category(e), "seen": now})
    write_json(path, ledger)


def summary(p: Paths) -> dict:
    """Counts per stage and category, for the dashboard and the run log."""
    entries = read_json(p.work / "caught.json", {}).values()
    by_stage = {}
    for (stage, cat), n in sorted(Counter((e["stage"], e["category"]) for e in entries).items()):
        by_stage.setdefault(stage, {})[cat] = n
    return {"total": len(entries), "by_stage": by_stage}
