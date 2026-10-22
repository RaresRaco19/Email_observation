"""Stages 2-3 validators: labeler output, the per-message label store, candidates, and the process map.

Labels are cached per message, keyed by a hash of what the labeler saw (sender, date, subject, new text),
not per batch. Adding one file to the corpus then queues one message, instead of re-packing and
re-labeling every batch after it. The process map is likewise extended, never rebuilt: the consolidator
only maps label names it has not seen before.
"""
import json
from collections import Counter

from . import config
from .config import Paths
from .util import read_json, sha, write_json
from .validate import label_schema_errors, quote_error

MAX_LISTED_ERRORS = 30
EMPTY_MAP = {"processes": [], "map": {}}


def message_key(m: dict) -> str:
    """Content key for the label cache; independent of path, batch and position in the corpus."""
    return sha(m["from"], m["date"] or "", m["subject"], m["new_text"])[:16]


def load_store(p: Paths) -> dict:
    return read_json(p.work / "label_store.json", {"labels": {}, "ingested": {}})


def batch_label_errors(p: Paths, bid: str, payload: list[dict]):
    """Return (fatal_errors, accepted_labels) for one batch's label file.

    accepted_labels holds every label that passes the schema and belongs to the batch, whatever its quote;
    quotes are re-checked against the raw file whenever check-labels rebuilds the label status in messages.json.
    """
    data = read_json(p.labels / f"{bid}.json")
    if data is None:
        return ["label file missing"], []
    labels = data.get("labels") if isinstance(data, dict) else None
    if not isinstance(labels, list):
        return ["top-level 'labels' list missing"], []

    expected = {m["msg_id"] for m in payload}
    fatal, accepted, bad_quotes, seen = [], [], [], set()
    for lab in labels:
        errs = label_schema_errors(lab)
        mid = lab.get("msg_id") if isinstance(lab, dict) else None
        if mid in seen:
            errs.append(f"duplicate label for {mid}")
        if isinstance(mid, str) and mid not in expected:
            errs.append(f"{mid} is not in this batch")
        if errs:
            fatal.extend(f"{mid}: {e}" for e in errs)
            continue
        seen.add(mid)
        accepted.append(lab)
        if lab["process"] != "none" and (qerr := quote_error(lab["quote"], mid, p.corpus)):
            bad_quotes.append(f"{mid}: {qerr}")

    missing = sorted(expected - seen)
    if missing:
        fatal.append(f"{len(missing)} messages have no label: {', '.join(missing[:10])}")
    claimed = sum(1 for lab in accepted if lab["process"] != "none")
    if claimed and len(bad_quotes) / claimed > config.BAD_QUOTE_LIMIT:
        fatal.append(f"{len(bad_quotes)}/{claimed} quotes failed verbatim check: " + "; ".join(bad_quotes[:10]))
    return fatal[:MAX_LISTED_ERRORS], accepted


def absorb(p: Paths, store: dict, attempts: dict, bid: str, payload: list[dict]) -> list[str]:
    """Move a batch's final labels into the store; returns its fatal errors.

    Final means valid, or failed MAX_ATTEMPTS times. Messages a failed batch left unlabeled are marked
    failed so they are not re-queued forever. A batch still awaiting its retry is left out.
    """
    label_file = p.labels / f"{bid}.json"
    if not label_file.exists():
        return ["label file missing"]
    h = sha(label_file.read_text(encoding="utf-8"))
    fatal, accepted = batch_label_errors(p, bid, payload)
    failed = len(set(attempts.get(bid, [])) | ({h} if fatal else set())) >= config.MAX_ATTEMPTS
    if (not fatal or failed) and store["ingested"].get(bid) != h:
        keys = {m["msg_id"]: message_key(m) for m in payload}
        for lab in accepted:
            store["labels"][keys[lab["msg_id"]]] = {"label": lab, "batch_id": bid}
        if failed:
            for k in keys.values():
                store["labels"].setdefault(k, {"failed": True, "batch_id": bid})
        store["ingested"][bid] = h
    return fatal


def check_labels(p: Paths) -> dict:
    manifest = read_json(p.work / "manifest.json")
    if manifest is None:
        raise SystemExit("work/manifest.json missing; run prepare first")
    attempts = read_json(p.work / "attempts.json", {})
    store = load_store(p)
    ok, retry, failed, not_labeled = [], [], [], []
    for b in manifest["batches"]:
        payload = read_json(p.root / b["path"])["messages"]
        label_file = p.labels / f"{b['id']}.json"
        if not label_file.exists():
            not_labeled.append(b["id"])
            continue
        fatal = absorb(p, store, attempts, b["id"], payload)
        if not fatal:
            ok.append(b["id"])
            continue
        # one attempt per distinct failing file content, so re-running this check is idempotent
        fails = set(attempts.get(b["id"], [])) | {sha(label_file.read_text(encoding="utf-8"))}
        attempts[b["id"]] = sorted(fails)
        entry = {"id": b["id"], "path": b["path"], "output": b["output"], "errors": fatal}
        (failed if len(fails) >= config.MAX_ATTEMPTS else retry).append(entry)
    write_json(p.work / "attempts.json", attempts)
    write_json(p.work / "label_store.json", store)

    # every message's status is rebuilt from the store for the current corpus, so it covers every run so far
    view = read_json(p.work / "messages.json")
    if not isinstance(view, dict):
        raise SystemExit("work/messages.json missing or from an older version; run prepare first")
    rejected, counts = [], Counter()
    for m in view["messages"]:
        for k in ("label", "batch_id", "reject_reason"):
            m.pop(k, None)
        entry = store["labels"].get(m["key"])
        if entry is None:
            m["status"] = "unlabeled"
        elif entry.get("failed"):
            m.update(status="failed", batch_id=entry["batch_id"])
        else:
            lab = {k: v for k, v in entry["label"].items() if k != "msg_id"}
            qerr = lab["process"] != "none" and quote_error(lab["quote"], m["msg_id"], p.corpus)
            m.update(status="rejected" if qerr else "valid", label=lab, batch_id=entry["batch_id"])
            if qerr:
                m["reject_reason"] = qerr
                rejected.append({"msg_id": m["msg_id"], "process": lab["process"], "reason": qerr})
            elif lab["process"] != "none":
                counts["process"] += 1
        counts[m["status"]] += 1
    summary = {
        "batches": len(manifest["batches"]), "ok": len(ok), "retry_batches": retry,
        "failed_batches": [{"id": f["id"], "errors": f["errors"][:5]} for f in failed],
        "not_labeled": len(not_labeled), "messages_labeled": counts["valid"] + counts["rejected"],
        "messages_failed": counts["failed"], "messages_total": manifest["unique_messages"],
        "labels_valid": counts["valid"], "labels_process": counts["process"],
        "quotes_rejected": counts["rejected"],
    }
    write_json(p.work / "messages.json", {**view, "checked": True, "summary": {**summary, "rejected_quotes": rejected}})
    return summary


def load_view(p: Paths) -> dict:
    """messages.json after check-labels: every current message with its label status, plus the label summary."""
    view = read_json(p.work / "messages.json")
    manifest = p.work / "manifest.json"
    if (view is None or not view.get("checked") or not manifest.exists()
            or view["manifest_hash"] != sha(manifest.read_text(encoding="utf-8"))):
        raise SystemExit("work/messages.json has no label status for the current corpus; run check-labels first")
    return view


def valid_labels(view: dict) -> list[dict]:
    return [{**m["label"], "msg_id": m["msg_id"], "batch_id": m["batch_id"]}
            for m in view["messages"] if m["status"] == "valid"]


def candidates(p: Paths, reset: bool = False) -> dict:
    """List label names the process map does not cover yet (all of them with reset=True)."""
    view = load_view(p)
    labels = valid_labels(view)
    meta = {m["msg_id"]: m for m in view["messages"]}
    pm = EMPTY_MAP if reset else read_json(p.work / "process_map.json", EMPTY_MAP)
    cands, known = {}, set()
    for lab in labels:
        if lab["process"] == "none":
            continue
        if lab["process"] in pm["map"]:
            known.add(lab["process"])
            continue
        c = cands.setdefault(lab["process"], {"count": 0, "mailboxes": set(), "sample_subjects": [], "sample_descriptions": []})
        c["count"] += 1
        c["mailboxes"].add(meta[lab["msg_id"]]["mailbox"])
        subj = meta[lab["msg_id"]]["subject"]
        if subj and subj not in c["sample_subjects"] and len(c["sample_subjects"]) < 5:
            c["sample_subjects"].append(subj)
        d = lab["process_description"]
        if d and d not in c["sample_descriptions"] and len(c["sample_descriptions"]) < 3:
            c["sample_descriptions"].append(d)
    for c in cands.values():
        c["mailboxes"] = sorted(c["mailboxes"])
    existing = [{k: proc[k] for k in ("id", "name", "description")} for proc in pm["processes"]]
    write_json(p.work / "candidates.json", {"reset": reset, "existing_processes": existing, "candidates": cands})
    return {"candidates": len(cands), "already_mapped": len(known), "existing_processes": len(existing),
            "candidates_path": "work/candidates.json", "output": "work/process_map_delta.json",
            "needs_consolidation": bool(cands)}


def delta_errors(cands: dict, existing_ids: set, delta) -> list[str]:
    if not isinstance(delta, dict) or not isinstance(delta.get("new_processes"), list) or not isinstance(delta.get("map"), dict):
        return ["process_map_delta.json needs 'new_processes' (list) and 'map' (object)"]
    errs, ids = [], set()
    for proc in delta["new_processes"]:
        if not isinstance(proc, dict) or not isinstance(proc.get("id"), str):
            errs.append(f"process entry without id: {proc!r:.80}")
            continue
        if proc["id"] in ids or proc["id"] in existing_ids or proc["id"] == "none":
            errs.append(f"new process id {proc['id']!r} duplicates an existing id or is reserved")
        ids.add(proc["id"])
        for f in ("name", "description", "action_idea"):
            if not isinstance(proc.get(f), str) or not proc[f].strip():
                errs.append(f"process {proc['id']}: {f} missing")
        if proc.get("remedy") not in config.REMEDIES:
            errs.append(f"process {proc['id']}: remedy must be one of {sorted(config.REMEDIES)}")
    missing = sorted(set(cands) - set(delta["map"]))
    extra = sorted(set(delta["map"]) - set(cands))
    if missing:
        errs.append(f"{len(missing)} candidate labels unmapped: {', '.join(missing[:15])}")
    if extra:
        errs.append(f"{len(extra)} map keys are not candidates: {', '.join(extra[:15])}")
    bad = sorted({v for v in delta["map"].values() if v != "none" and v not in ids | existing_ids})
    if bad:
        errs.append(f"map values that are not existing or new process ids: {', '.join(map(str, bad[:15]))}")
    return errs[:MAX_LISTED_ERRORS]


def check_process_map(p: Paths) -> dict:
    """Validate the consolidator's delta and merge it into process_map.json, which only this code writes."""
    cdata = read_json(p.work / "candidates.json")
    if cdata is None:
        raise SystemExit("work/candidates.json missing; run candidates first")
    pm = EMPTY_MAP if cdata["reset"] else read_json(p.work / "process_map.json", EMPTY_MAP)
    delta_path = p.work / "process_map_delta.json"
    if cdata["candidates"]:
        try:
            delta = read_json(delta_path)
        except ValueError as e:
            return {"ok": False, "errors": [f"invalid JSON: {e}"]}
        errs = (["process_map_delta.json missing"] if delta is None
                else delta_errors(cdata["candidates"], {proc["id"] for proc in pm["processes"]}, delta))
        if errs:
            return {"ok": False, "errors": errs}
        pm = {"processes": pm["processes"] + delta["new_processes"], "map": {**pm["map"], **delta["map"]}}
    write_json(p.work / "process_map.json", pm)
    delta_path.unlink(missing_ok=True)
    write_json(p.work / "process_map.ok", {"map_hash": sha((p.work / "process_map.json").read_text(encoding="utf-8"))})
    added = len(cdata["candidates"])
    return {"ok": True, "labels_added": added, "processes": len(pm["processes"]),
            "processes_added": len(delta["new_processes"]) if added else 0,
            "labels_mapped_to_none": sum(1 for v in pm["map"].values() if v == "none")}
