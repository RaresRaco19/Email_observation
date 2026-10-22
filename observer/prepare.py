"""Stage 1: parse every file, dedup, thread, and pack the messages that still need a label into batches.

Only messages whose content key is missing from work/label_store.json are batched, so a re-run after
adding files labels just the new messages. Earlier labeled messages of the same thread ride along as
read-only context.
"""
import json
import shutil
from datetime import datetime

from . import config
from .config import Paths
from .labels import absorb, load_store, message_key
from .parse import normalize_subject, parse_file
from .util import read_json, sha, write_json


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def corpus_files(p: Paths):
    return sorted(f for f in p.corpus.rglob("*") if f.is_file())


DUP_WINDOW_HOURS = 16


def _hours(iso):
    return datetime.fromisoformat(iso).timestamp() / 3600 if iso else None


def dedup(msgs: list[dict]) -> list[dict]:
    """Merge copies of one message; the lowest path is canonical, the rest go in dup_paths.

    Two files are copies if they share a non-empty Message-ID, or have identical sender, subject and
    whitespace-normalized body with timestamps under DUP_WINDOW_HOURS apart. The window matters both
    ways: the export stores some copies with a timezone-shifted Date (farmer-d/logistics/189 vs 2154,
    10 h apart), while recurring notices such as the daily Calpine nomination repeat sender, subject
    and body verbatim ~24 h apart and must stay separate occurrences.
    """
    msgs = sorted(msgs, key=lambda m: m["msg_id"])
    uf, by_mid, by_content = UnionFind(len(msgs)), {}, {}
    for i, m in enumerate(msgs):
        if m["message_id_header"]:
            if m["message_id_header"] in by_mid:
                uf.union(by_mid[m["message_id_header"]], i)
            else:
                by_mid[m["message_id_header"]] = i
        key = sha(m["from"], normalize_subject(m["subject"]), " ".join(m["body"].split()))
        by_content.setdefault(key, []).append(i)
    for idxs in by_content.values():
        for x in range(len(idxs)):
            for y in range(x + 1, len(idxs)):
                ha, hb = _hours(msgs[idxs[x]]["date"]), _hours(msgs[idxs[y]]["date"])
                if ha is None or hb is None or abs(ha - hb) < DUP_WINDOW_HOURS:
                    uf.union(idxs[x], idxs[y])
    groups = {}
    for i, m in enumerate(msgs):
        groups.setdefault(uf.find(i), []).append(m)
    unique = []
    for members in groups.values():
        canon = dict(members[0])
        canon["dup_paths"] = [m["msg_id"] for m in members[1:]]
        unique.append(canon)
    return sorted(unique, key=lambda m: m["msg_id"])


def assign_threads(msgs: list[dict]) -> None:
    for m in msgs:
        subj = normalize_subject(m["subject"])
        m["thread_id"] = "t" + sha(subj if subj else "solo:" + m["msg_id"])[:10]


def pack_batches(msgs: list[dict]) -> list[list[dict]]:
    order = sorted(msgs, key=lambda m: (m["mailbox"], m["thread_id"], m["date"] or "", m["msg_id"]))
    batches, cur, size = [], [], 0
    for m in order:
        n = len(m["new_text"]) + len(m["subject"]) + 200
        if cur and (size + n > config.BATCH_MAX_CHARS or len(cur) >= config.BATCH_MAX_MSGS):
            batches.append(cur)
            cur, size = [], 0
        cur.append(m)
        size += n
    if cur:
        batches.append(cur)
    return batches


CONTEXT_PER_THREAD = 3
CONTEXT_PER_BATCH = 20
CONTEXT_CHARS = 600


def batch_payload(batch: list[dict]) -> list[dict]:
    return [{
        "msg_id": m["msg_id"], "thread_id": m["thread_id"], "date": m["date"], "from": m["from"],
        "to": m["to"][:5], "subject": m["subject"], "new_text": m["new_text"],
        "new_text_source": m["new_text_source"], "truncated": m["truncated"],
    } for m in batch]


def thread_context(batch: list[dict], labeled_by_thread: dict) -> list[dict]:
    """The latest already-labeled messages of each thread in the batch, so a new reply is read in context."""
    ctx = []
    for tid in dict.fromkeys(m["thread_id"] for m in batch):
        for m, process in labeled_by_thread.get(tid, [])[-CONTEXT_PER_THREAD:]:
            ctx.append({"msg_id": m["msg_id"], "thread_id": tid, "date": m["date"], "from": m["from"],
                        "subject": m["subject"], "new_text": m["new_text"][:CONTEXT_CHARS], "process": process})
    return ctx[:CONTEXT_PER_BATCH]


def ingest_label_files(p: Paths, store: dict) -> None:
    """Absorb label files no check-labels run has absorbed yet (e.g. after an interrupted run)."""
    attempts = read_json(p.work / "attempts.json", {})
    for lf in sorted(p.labels.glob("*.json")) if p.labels.exists() else []:
        batch = read_json(p.batches / lf.name)
        if batch is not None and store["ingested"].get(lf.stem) != sha(lf.read_text(encoding="utf-8")):
            absorb(p, store, attempts, lf.stem, batch["messages"])


def run(p: Paths, force: bool = False, max_batches: int | None = None,
        expected_files: int | None = None) -> dict:
    if force:
        shutil.rmtree(p.work, ignore_errors=True)
        shutil.rmtree(p.out, ignore_errors=True)
    files = corpus_files(p)
    if expected_files is not None and len(files) != expected_files:
        raise SystemExit(f"expected {expected_files} corpus files, found {len(files)}")
    parsed = [parse_file(f, p.corpus) for f in files]
    unique = dedup(parsed)
    assign_threads(unique)
    for m in unique:
        m["key"] = message_key(m)

    store = load_store(p)
    ingest_label_files(p, store)
    write_json(p.work / "label_store.json", store)
    labeled_by_thread = {}
    for m in sorted(unique, key=lambda m: (m["date"] or "", m["msg_id"])):
        entry = store["labels"].get(m["key"])
        if entry and not entry.get("failed"):
            labeled_by_thread.setdefault(m["thread_id"], []).append((m, entry["label"]["process"]))
    todo = [m for m in unique if m["key"] not in store["labels"]]

    batches = []
    for b in pack_batches(todo):
        payload = batch_payload(b)
        ctx = thread_context(b, labeled_by_thread)
        bid = sha(json.dumps({"messages": payload, "context": ctx}, sort_keys=True))[:12]
        path = p.batches / f"{bid}.json"
        if not path.exists():
            write_json(path, {"batch_id": bid, "messages": payload, "context": ctx})
        batches.append({"id": bid, "path": str(path.relative_to(p.root)),
                        "output": str((p.labels / f"{bid}.json").relative_to(p.root)), "n": len(payload),
                        "context": len(ctx)})

    meta = [{**{k: v for k, v in m.items() if k not in ("body", "new_text")}, "status": "unlabeled"} for m in unique]
    by_folder = {}
    for m in parsed:
        by_folder[m["folder"]] = by_folder.get(m["folder"], 0) + 1
    manifest = {
        "files": len(files), "files_by_folder": by_folder, "unique_messages": len(unique),
        "duplicates_removed": len(files) - len(unique), "threads": len({m["thread_id"] for m in unique}),
        "undated": sum(1 for m in unique if not m["date"]),
        "dates_out_of_range": sum(1 for m in unique if m["date_out_of_range"]), "truncated": sum(1 for m in unique if m["truncated"]),
        "messages_cached": len(unique) - len(todo), "messages_to_label": len(todo),
        "batches": batches,
    }
    write_json(p.work / "manifest.json", manifest)
    # check-labels fills in each message's label status and sets checked; rank refuses a view from an older prepare
    write_json(p.work / "messages.json", {"manifest_hash": sha((p.work / "manifest.json").read_text(encoding="utf-8")),
                                          "checked": False, "messages": meta})

    pending = [{"id": b["id"], "path": b["path"], "output": b["output"]} for b in batches]
    summary = {k: v for k, v in manifest.items() if k != "batches"}
    summary.update(total_batches=len(batches), pending_batches=pending[:max_batches] if max_batches else pending)
    if max_batches:
        summary["pending_not_listed"] = max(0, len(pending) - max_batches)
    return summary
