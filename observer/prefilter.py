"""Rule-based "none" labels for obvious non-work mail, applied by prepare before batching.

Only high-precision rules on headers live here; everything a person has to read to judge goes to a labeler.
Against the first full run's labels these rules catch 337 messages, 336 of them labeled none by the model;
the miss is a P&L reply sent to a juno.com address (giron-d/sent/375).
"""
import re

from . import config

_BROADCAST = re.compile(config.BROADCAST_SENDER)
_SOCIAL = re.compile(config.SOCIAL_SUBJECT, re.I)


def _domain(addr: str) -> str:
    return addr.rsplit("@", 1)[-1].lower()


def _personal(addr: str) -> bool:
    d = _domain(addr)
    return any(d == p or d.endswith("." + p) for p in config.PERSONAL_DOMAINS)


def none_reason(m: dict) -> str | None:
    """Why message m is non-work mail, or None when a labeler has to judge it."""
    if _BROADCAST.search(m["from"]):
        return "broadcast_sender"
    if _personal(m["from"]):
        return "personal_sender"
    recips = m["to"] + m["cc"]
    if recips and all(_personal(a) or _domain(a).endswith(".net") for a in recips):
        return "personal_recipients"
    if _SOCIAL.search(m["subject"]):
        return "social_subject"
    return None


def rule_batch_id(reason: str) -> str:
    return f"rule:v{config.PREFILTER_VERSION}:{reason}"
