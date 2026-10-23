"""Stage 4: aggregate validated labels into processes and price them. All arithmetic lives here."""
import statistics
from collections import Counter
from datetime import datetime

from . import config
from .config import Paths
from .labels import load_view, valid_labels
from .parse import parse_file, raw_path_for
from .util import read_json, sha, write_json

DAYS_PER_MONTH = 30.44
EVIDENCE_FOR_WRITER = 15
REMEDY_LABEL = {"automation": "Automation", "quick_win": "Quick win"}


def usd(x: float) -> str:
    return f"${x:,.0f}"


def _dt(iso):
    return datetime.fromisoformat(iso) if iso else None


def thread_gaps(thread_msgs: list[dict]) -> list[float]:
    """Hours between consecutive dated messages of a thread; gaps beyond STALL_GAP_MAX_DAYS are dropped."""
    dates = sorted(d for m in thread_msgs if (d := _dt(m["date"])))
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(dates, dates[1:])]
    return [g for g in gaps if 0 < g <= config.STALL_GAP_MAX_DAYS * 24]


def mailbox_windows(messages: list[dict]) -> dict[str, tuple[datetime, datetime]]:
    """First and last dated message of each mailbox: the period in which we could have seen its work."""
    win = {}
    for m in messages:
        if (d := _dt(m["date"])):
            lo, hi = win.get(m["mailbox"], (d, d))
            win[m["mailbox"]] = (min(lo, d), max(hi, d))
    return win


def mailbox_months(windows: dict, mailbox: str) -> float:
    """Length of one mailbox's observation window in months, at least one."""
    lo, hi = windows.get(mailbox, (None, None))
    days = (hi - lo).total_seconds() / 86400 if lo else 0.0
    return max(1.0, days / DAYS_PER_MONTH)


def price(by_mailbox: dict[str, int], windows: dict, minutes: list[float]) -> dict:
    """Each mailbox's messages are rated over that mailbox's own observation window and the rates are summed, so
    messages from a 6-month mailbox are not diluted by one stray message from a 24-month one. The window is the
    mailbox's, not the process's first-to-last span, so a six-week burst is still not priced as if it recurred."""
    terms = [{"mailbox": mb, "messages": n, "months": round(mailbox_months(windows, mb), 2),
              "per_month": round(n / mailbox_months(windows, mb), 2)} for mb, n in sorted(by_mailbox.items())]
    per_month = sum(n / mailbox_months(windows, mb) for mb, n in by_mailbox.items())
    median_min = statistics.median(minutes) if minutes else 0.0
    hours = per_month * median_min / 60 * config.AUTOMATABLE_SHARE
    dollars = hours * config.RATE_USD
    rate = " + ".join(f"{t['messages']} msgs / {t['months']:.2f} months observed ({t['mailbox']})" for t in terms)
    return {
        "rate_by_mailbox": terms,
        "messages_per_month": round(per_month, 2), "median_minutes": median_min,
        "hours_month": round(hours, 1), "usd_month": round(dollars), "usd_year": round(dollars) * 12,
        "formula": (f"{rate} = {per_month:.2f}/month; x {median_min:g} min median handling x {config.AUTOMATABLE_SHARE:.0%} "
                    f"automatable = {hours:.1f} h/month; x ${config.RATE_USD}/h = {usd(dollars)}/month"),
    }


def build(p: Paths) -> dict:
    stamp = read_json(p.work / "process_map.ok")
    pm = read_json(p.work / "process_map.json")
    if not stamp or pm is None or stamp.get("map_hash") != sha((p.work / "process_map.json").read_text(encoding="utf-8")):
        raise SystemExit("process map not validated; run check-process-map first")
    view = load_view(p)
    labels = valid_labels(view)
    meta = {m["msg_id"]: m for m in view["messages"]}
    manifest = read_json(p.work / "manifest.json")
    label_summary = view["summary"]
    procs = {proc["id"]: proc for proc in pm["processes"]}
    if any(proc.get("remedy") not in config.REMEDIES for proc in procs.values()):
        raise SystemExit("process map predates remedies; run candidates with --reconsolidate")
    windows = mailbox_windows(view["messages"])
    by_thread = {}
    for m in meta.values():
        by_thread.setdefault(m["thread_id"], []).append(m)

    unmapped = sorted({lab["process"] for lab in labels if lab["process"] != "none"} - set(pm["map"]))
    if unmapped:
        raise SystemExit(f"{len(unmapped)} labels are not in the process map; run candidates and check-process-map first")
    grouped = {}
    for lab in labels:
        pid = pm["map"].get(lab["process"], "none")
        if pid != "none":
            grouped.setdefault(pid, {})[lab["msg_id"]] = lab  # one label per unique message

    ranked, rejected = [], []
    for pid, labs in grouped.items():
        msgs = [meta[mid] for mid in labs]
        threads = sorted({m["thread_id"] for m in msgs})
        reason = (f"only {len(labs)} validated quotes (need {config.MIN_EVIDENCE})" if len(labs) < config.MIN_EVIDENCE
                  else f"only {len(threads)} distinct threads (need {config.MIN_THREADS})" if len(threads) < config.MIN_THREADS
                  else None)
        if reason:
            rejected.append({"id": pid, "name": procs[pid]["name"], "evidence": len(labs), "threads": len(threads),
                             "reason": reason})
            continue
        dates = sorted(d for m in msgs if (d := _dt(m["date"])))
        mailboxes = sorted({m["mailbox"] for m in msgs})
        gaps = [g for t in threads for g in thread_gaps(by_thread[t])]
        touch = Counter()
        for m in msgs:
            touch.update([m["from"]] + m["to"] + m["cc"])
        touch.pop("", None)
        evidence = sorted(({
            "msg_id": mid, "date": meta[mid]["date"], "from": meta[mid]["from"], "subject": meta[mid]["subject"],
            "thread_id": meta[mid]["thread_id"], "quote": lab["quote"], "kind": lab["kind"],
            "minutes": lab["minutes_estimate"], "stall": bool(lab["stall_signal"].strip()),
            "dup_paths": meta[mid]["dup_paths"],
        } for mid, lab in labs.items()), key=lambda e: (e["date"] or "", e["msg_id"]))
        by_month = dict(sorted(Counter(d.strftime("%Y-%m") for d in dates).items()))
        flagged = sum(e["stall"] for e in evidence)
        ranked.append({
            "id": pid, "name": procs[pid]["name"], "description": procs[pid]["description"],
            "remedy": procs[pid]["remedy"], "action_idea": procs[pid]["action_idea"],
            "source_labels": sorted(k for k, v in pm["map"].items() if v == pid),
            "messages": len(msgs), "threads": len(threads), "mailboxes": mailboxes,
            "first_date": dates[0].isoformat() if dates else None, "last_date": dates[-1].isoformat() if dates else None,
            "participants": [{"address": a, "messages": c} for a, c in touch.most_common(8)],
            "kinds": dict(Counter(lab["kind"] for lab in labs.values()).most_common()),
            "by_month": by_month,
            "stall": {"median_gap_hours": round(statistics.median(gaps), 1) if gaps else None,
                      "max_gap_hours": round(max(gaps), 1) if gaps else None, "flagged_messages": flagged},
            # shown next to the figure, never used to order it
            "confidence": {"quotes": len(labs), "threads": len(threads), "mailboxes": len(mailboxes),
                           "active_months": len(by_month), "stall_share": round(flagged / len(labs), 2)},
            **price(Counter(m["mailbox"] for m in msgs), windows, [lab["minutes_estimate"] for lab in labs.values()]),
            "evidence": evidence,
        })
    ranked.sort(key=lambda o: (-o["usd_month"], -o["messages"], o["id"]))
    for i, o in enumerate(ranked, 1):
        o["rank"] = i

    from .artifacts import artifact_done
    from .solutions import design_done
    # only opportunities worth at least MIN_USD_MONTH, at most TOP_N of them, are shown, totalled and worked on: each gets
    # a design (an automation or a quick-win rollout) and then a draft built on it. Nothing below the cut gets an
    # evidence file, so no designer or writer is ever launched for it.
    shown = [o for o in ranked if o["usd_month"] >= config.MIN_USD_MONTH][:config.TOP_N]
    rest = ranked[len(shown):]
    designs, targets = [], []
    for o in shown:
        ev_path = p.evidence / f"{o['id']}.json"
        write_json(ev_path, evidence_packet(p, o))
        target = {"id": o["id"], "remedy": o["remedy"], "evidence_path": str(ev_path.relative_to(p.root))}
        o["design"] = f"solutions/{o['id']}.json"
        designs.append({**target, "output_path": str((p.work / "solutions" / f"{o['id']}.json").relative_to(p.root)),
                        "done": design_done(p, o["id"])})
        out = p.artifacts / f"{o['id']}.md"
        o["artifact"] = f"artifacts/{o['id']}.md"
        targets.append({**target, "solution_path": f"out/{o['design']}", "output_path": str(out.relative_to(p.root)),
                        "done": artifact_done(p, o["id"])})
    for stale in p.evidence.glob("*.json") if p.evidence.exists() else []:
        if stale.stem not in {o["id"] for o in shown}:
            stale.unlink()

    report = {
        "generated_from": {"files": manifest["files"], "unique_messages": manifest["unique_messages"],
                           "duplicates_removed": manifest["duplicates_removed"], "threads": manifest["threads"],
                           "files_by_folder": manifest["files_by_folder"],
                           "dates_out_of_range": manifest.get("dates_out_of_range", 0),
                           "messages_labeled": label_summary.get("messages_labeled"),
                           "quotes_rejected": label_summary.get("quotes_rejected"),
                           "rejected_quotes": label_summary.get("rejected_quotes", []),
                           "failed_batches": label_summary.get("failed_batches", [])},
        "assumptions": {"rate_usd": config.RATE_USD, "automatable_share": config.AUTOMATABLE_SHARE,
                        "min_evidence": config.MIN_EVIDENCE, "min_threads": config.MIN_THREADS,
                        "top_n": config.TOP_N, "min_usd_month": config.MIN_USD_MONTH},
        "total_usd_month": sum(o["usd_month"] for o in shown),
        "total_hours_month": round(sum(o["hours_month"] for o in shown), 1),
        "opportunities": shown, "rejected": rejected,
        "below_cutoff": [{k: o[k] for k in ("rank", "id", "name", "remedy", "messages", "hours_month", "usd_month")}
                         for o in rest],
    }
    report["total_usd_year"] = report["total_usd_month"] * 12
    write_json(p.out / "report.json", report)
    (p.out / "report.md").write_text(render_md(report), encoding="utf-8")
    return {
        "opportunities": [{"rank": o["rank"], "id": o["id"], "usd_month": o["usd_month"], "hours_month": o["hours_month"],
                           "messages": o["messages"]} for o in ranked],
        "rejected": len(rejected), "total_usd_month": report["total_usd_month"],
        "solution_targets": designs,
        "top_n": config.TOP_N, "min_usd_month": config.MIN_USD_MONTH, "artifact_targets": targets,
    }


def spread_sample(evidence: list[dict], n: int) -> list[dict]:
    """Up to n messages taken round-robin across threads (stalled messages first within each thread), so a writer
    sees many conversations rather than one long one. Busiest threads go first."""
    by_thread = {}
    for e in sorted(evidence, key=lambda e: (not e["stall"], e["date"] or "", e["msg_id"])):
        by_thread.setdefault(e["thread_id"], []).append(e)
    queues = sorted(by_thread.values(), key=lambda q: (-len(q), q[0]["date"] or "", q[0]["msg_id"]))
    out = []
    while len(out) < n and any(queues):
        for q in queues:
            if q and len(out) < n:
                out.append(q.pop(0))
    return sorted(out, key=lambda e: (e["date"] or "", e["msg_id"]))


def evidence_packet(p: Paths, o: dict) -> dict:
    sample = spread_sample(o["evidence"], EVIDENCE_FOR_WRITER)
    msgs = []
    for e in sample:
        parsed = parse_file(raw_path_for(e["msg_id"], p.corpus), p.corpus)
        msgs.append({**{k: e[k] for k in ("msg_id", "date", "from", "subject", "thread_id", "quote", "kind", "stall")},
                     "to": parsed["to"][:5], "new_text": parsed["new_text"][:3000]})
    figures = [usd(o["usd_month"]), usd(o["usd_year"]), f"${config.RATE_USD}"]
    return {
        "opportunity": {k: o[k] for k in ("id", "name", "description", "remedy", "action_idea", "messages", "threads",
                                           "mailboxes", "participants", "stall", "confidence", "kinds", "hours_month", "usd_month",
                                           "usd_year", "messages_per_month", "median_minutes", "formula")},
        "allowed_figures": figures, "allowed_types": config.ARTIFACT_TYPES[o["remedy"]], "messages": msgs,
    }


def render_md(r: dict) -> str:
    g = r["generated_from"]
    lines = [
        "# Automation opportunities", "",
        f"Read {g['files']:,} files ({g['unique_messages']:,} unique messages after removing {g['duplicates_removed']} duplicates, "
        f"{g['threads']:,} threads). Labeled {g['messages_labeled'] or 0:,} messages; {g['quotes_rejected'] or 0} quotes failed verification and were dropped.", "",
        f"**Total: {usd(r['total_usd_month'])}/month ({usd(r['total_usd_year'])}/year), {r['total_hours_month']} hours/month** "
        f"at ${r['assumptions']['rate_usd']}/h, assuming {r['assumptions']['automatable_share']:.0%} of handling time is automatable.", "",
        f"Ships every process with at least {r['assumptions']['min_evidence']} verified quotes in at least "
        f"{r['assumptions']['min_threads']} threads; {len(r['rejected'])} had too little evidence. "
        "Monthly rates add up each mailbox's messages over the period that mailbox was observed. "
        f"Opportunities worth at least {usd(r['assumptions']['min_usd_month'])}/month are shown and totalled (at most "
        f"{r['assumptions']['top_n']}, by $/month), and each gets a solution design plus a draft built on it (an automation, or the rollout of a quick win). Solution designs are in `solutions.md`.", "",
        "| # | Process | Remedy | Msgs | /month | Median min | Hours/mo | $/mo | Draft |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for o in r["opportunities"]:
        lines.append(f"| {o['rank']} | {o['name']} | {REMEDY_LABEL[o['remedy']]} | {o['messages']} | {o['messages_per_month']} | {o['median_minutes']:g} | "
                     f"{o['hours_month']} | {usd(o['usd_month'])} | {o.get('artifact', '')} |")
    for o in r["opportunities"]:
        lines += ["", f"## {o['rank']}. {o['name']}", "", o["description"], "", f"*{REMEDY_LABEL[o['remedy']]}:* {o['action_idea']}", "",
                  f"*Arithmetic:* {o['formula']}", "", "Evidence:"]
        lines += [f"- `{e['msg_id']}` ({(e['date'] or 'undated')[:10]}, {e['from']}): \"{e['quote']}\"" for e in o["evidence"][:5]]
    if r["below_cutoff"]:
        lines += ["", f"## Below the cutoff: under {usd(r['assumptions']['min_usd_month'])}/month or outside the top {r['assumptions']['top_n']} (not totalled)", "",
                  "| # | Process | Remedy | Msgs | Hours/mo | $/mo |", "|---|---|---|---|---|---|"]
        lines += [f"| {o['rank']} | {o['name']} | {REMEDY_LABEL[o['remedy']]} | {o['messages']} | {o['hours_month']} | "
                  f"{usd(o['usd_month'])} |" for o in r["below_cutoff"]]
    if r["rejected"]:
        lines += ["", "## Not shipped (insufficient evidence)", ""]
        lines += [f"- {x['name']}: {x['reason']}" for x in r["rejected"]]
    if g["rejected_quotes"]:
        lines += ["", "## Quotes that failed verification", "",
                  "These labels were dropped because their quote is not a verbatim substring of the raw file.", ""]
        lines += [f"- `{x['msg_id']}` ({x['process']}): {x['reason']}" for x in g["rejected_quotes"]]
    return "\n".join(lines) + "\n"
