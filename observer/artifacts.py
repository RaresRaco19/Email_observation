"""Stage 5 validator: drafted artifacts may only cite evidence messages, quote verbatim, and use computed figures."""
import re

from . import caught
from .config import Paths
from .util import read_json, sha, write_json
from .validate import quote_error

CITE = re.compile(r"\[([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/\d+)\]")
DOLLARS = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")


def front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    head, sep, body = text[4:].partition("\n---")
    if not sep:
        return {}, text
    fm = {}
    for line in head.splitlines():
        key, _, val = line.partition(":")
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        fm[key.strip()] = val
    return fm, body


def blockquotes(body: str) -> list[str]:
    quotes, cur = [], []
    for line in body.splitlines() + [""]:
        if line.startswith(">"):
            cur.append(line.lstrip(">").strip())
        elif cur:
            q = CITE.sub("", " ".join(cur)).strip().strip("\"'“”").strip()
            q = re.sub(r"\s*[—-]+\s*$", "", q).strip().strip("\"'“”")
            if q:
                quotes.append(q)
            cur = []
    return quotes


def artifact_errors(p: Paths, opp_id: str) -> list[str]:
    ev = read_json(p.evidence / f"{opp_id}.json")
    if ev is None:
        return [f"no evidence file for {opp_id}"]
    path = p.artifacts / f"{opp_id}.md"
    if not path.exists():
        return ["artifact file missing"]
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    fm, body = front_matter(text)
    allowed_ids = {m["msg_id"] for m in ev["messages"]}
    errs = []
    if fm.get("opportunity") != opp_id:
        errs.append(f"front matter opportunity must be {opp_id!r}")
    if fm.get("type") not in ev["allowed_types"]:
        errs.append(f"front matter type must be one of {ev['allowed_types']} for a {ev['opportunity']['remedy']} opportunity")
    cites = fm.get("citations")
    if not isinstance(cites, list) or not cites:
        errs.append("front matter citations must be a non-empty list")
        cites = []
    for c in set(cites) | set(CITE.findall(body)):
        if c not in allowed_ids:
            errs.append(f"citation {c} is not in the evidence file")
    for q in blockquotes(body):
        if all(quote_error(q, mid, p.corpus) for mid in allowed_ids):
            errs.append(f"blockquote is not verbatim from any evidence message: {q[:80]!r}")
    return errs + figure_errors(body, ev["allowed_figures"])


def figure_errors(text: str, allowed: list[str]) -> list[str]:
    """Every dollar amount a model writes must be one of the figures code computed."""
    allowed_figs = {f.replace(",", "") for f in allowed}
    return [f"dollar figure {fig} is not one of {allowed}" for fig in DOLLARS.findall(text)
            if fig.replace(" ", "").replace(",", "") not in allowed_figs]


def _stamp(p: Paths, opp_id: str) -> str | None:
    """Hash of the evidence, validated design and draft, so a draft is redone when the design it builds on changes."""
    parts = (p.evidence / f"{opp_id}.json", p.out / "solutions" / f"{opp_id}.json", p.artifacts / f"{opp_id}.md")
    if not all(f.exists() for f in parts):
        return None
    return sha(*(f.read_text(encoding="utf-8") for f in parts))


def artifact_done(p: Paths, opp_id: str) -> bool:
    """True when the current draft passed validation against the current evidence and design."""
    stamp = _stamp(p, opp_id)
    return stamp is not None and read_json(p.work / "artifacts.ok", {}).get(opp_id) == stamp


def check(p: Paths) -> dict:
    report = read_json(p.out / "report.json")
    if report is None:
        raise SystemExit("out/report.json missing; run rank first")
    stamps, ok, retry = read_json(p.work / "artifacts.ok", {}), [], []
    for o in report["opportunities"]:
        if "artifact" not in o:
            continue
        errs = artifact_errors(p, o["id"])
        draft = p.out / o["artifact"]
        caught.record(p, "artifacts", o["id"], errs, version=draft.read_text(encoding="utf-8") if draft.exists() else "")
        if not errs and not (p.out / "solutions" / f"{o['id']}.json").exists():
            errs = ["its solution design has not been validated; run check-solutions first"]
        if errs:
            stamps.pop(o["id"], None)
            retry.append({"id": o["id"], "evidence_path": f"work/evidence/{o['id']}.json",
                          "solution_path": f"out/solutions/{o['id']}.json",
                          "output_path": f"out/{o['artifact']}", "errors": errs[:15]})
        else:
            stamps[o["id"]] = _stamp(p, o["id"])
            ok.append(o["id"])
    shown = {o["id"] for o in report["opportunities"]}
    for stale in p.artifacts.glob("*.md") if p.artifacts.exists() else []:
        if stale.stem not in shown:
            stale.unlink()
    write_json(p.work / "artifacts.ok", {k: v for k, v in stamps.items() if k in shown})
    return {"ok": ok, "retry": retry}
