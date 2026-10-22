"""Stage 5 validator: a solution design may only cite evidence messages, quote verbatim, use computed figures,
and name existing systems that the evidence mentions.

Validated designs are copied to out/solutions/<id>.json. work/solutions.ok records the evidence and design hashes
each one passed with, so an unchanged opportunity is not redesigned on the next run.
"""
import json

from .artifacts import figure_errors
from .config import Paths
from .util import read_json, sha, write_json
from .validate import quote_error

EFFORTS = {"S", "M", "L"}
TEXT_FIELDS = ("summary", "success_metric")
LIST_FIELDS = ("implementation_steps", "stays_manual", "risks")
SOLUTION_TEXT = ("approach", "trigger")
SOLUTION_LISTS = ("components", "inputs", "outputs", "systems")
MIN_STEPS = 3


def _paths(p: Paths, opp_id: str):
    return p.evidence / f"{opp_id}.json", p.work / "solutions" / f"{opp_id}.json", p.out / "solutions" / f"{opp_id}.json"


def _strs(x) -> bool:
    return isinstance(x, list) and bool(x) and all(isinstance(v, str) and v.strip() for v in x)


def design_errors(p: Paths, opp_id: str) -> list[str]:
    ev_path, path, _ = _paths(p, opp_id)
    ev = read_json(ev_path)
    if ev is None:
        return [f"no evidence file for {opp_id}"]
    try:
        d = read_json(path)
    except ValueError as e:
        return [f"invalid JSON: {e}"]
    if d is None:
        return ["design file missing"]
    if not isinstance(d, dict):
        return ["design must be a JSON object"]
    allowed_ids = {m["msg_id"] for m in ev["messages"]}
    errs = []
    if d.get("opportunity") != opp_id:
        errs.append(f"opportunity must be {opp_id!r}")
    if d.get("effort") not in EFFORTS:
        errs.append(f"effort must be one of {sorted(EFFORTS)}")
    errs += [f"{f} must be a non-empty string" for f in TEXT_FIELDS if not isinstance(d.get(f), str) or not d[f].strip()]
    errs += [f"{f} must be a non-empty list of strings" for f in LIST_FIELDS if not _strs(d.get(f))]

    steps = d.get("current_workflow")
    if not isinstance(steps, list) or len(steps) < MIN_STEPS:
        errs.append(f"current_workflow needs at least {MIN_STEPS} steps")
        steps = []
    for i, s in enumerate(steps):
        if not isinstance(s, dict) or not all(isinstance(s.get(k), str) and s[k].strip() for k in ("step", "who")):
            errs.append(f"current_workflow[{i}] needs 'step' and 'who'")
        elif not _strs(s.get("citations")):
            errs.append(f"current_workflow[{i}] needs at least one citation")
        else:
            errs += [f"current_workflow[{i}] cites {c}, which is not in the evidence file"
                     for c in s["citations"] if c not in allowed_ids]

    stalls = d.get("stall_points")
    if not isinstance(stalls, list) or not stalls:
        errs.append("stall_points needs at least one entry")
        stalls = []
    for i, s in enumerate(stalls):
        if not isinstance(s, dict) or not all(isinstance(s.get(k), str) and s[k].strip() for k in ("description", "quote", "citation")):
            errs.append(f"stall_points[{i}] needs 'description', 'quote' and 'citation'")
        elif s["citation"] not in allowed_ids:
            errs.append(f"stall_points[{i}] cites {s['citation']}, which is not in the evidence file")
        elif (qerr := quote_error(s["quote"], s["citation"], p.corpus)):
            errs.append(f"stall_points[{i}] quote: {qerr}")

    sol = d.get("solution")
    if not isinstance(sol, dict):
        errs.append("solution must be an object")
        sol = {}
    errs += [f"solution.{f} must be a non-empty string" for f in SOLUTION_TEXT if not isinstance(sol.get(f), str) or not sol[f].strip()]
    errs += [f"solution.{f} must be a non-empty list of strings" for f in SOLUTION_LISTS if not _strs(sol.get(f))]
    if _strs(sol.get("systems")):
        # existing systems must come from the emails; anything new belongs in solution.components
        corpus_text = json.dumps(ev, ensure_ascii=False).lower()
        errs += [f"system {s!r} is not mentioned in the evidence; put new tools in solution.components"
                 for s in sol["systems"] if s.strip().lower() not in corpus_text]
    return errs + figure_errors(json.dumps(d, ensure_ascii=False), ev["allowed_figures"])


def _stamp(p: Paths, opp_id: str) -> str | None:
    ev_path, path, _ = _paths(p, opp_id)
    if not ev_path.exists() or not path.exists():
        return None
    return sha(ev_path.read_text(encoding="utf-8"), path.read_text(encoding="utf-8"))


def design_done(p: Paths, opp_id: str) -> bool:
    """True when the current design passed validation against the current evidence."""
    stamp = _stamp(p, opp_id)
    ok = read_json(p.work / "solutions.ok", {})
    return stamp is not None and ok.get(opp_id) == stamp and _paths(p, opp_id)[2].exists()


def check(p: Paths) -> dict:
    report = read_json(p.out / "report.json")
    if report is None:
        raise SystemExit("out/report.json missing; run rank first")
    stamps, ok, retry, missing, designs = read_json(p.work / "solutions.ok", {}), [], [], [], {}
    targets = [o for o in report["opportunities"] if o.get("design")]
    shortlist = {o["id"] for o in targets}
    for o in targets:
        ev_path, path, out = _paths(p, o["id"])
        if not path.exists():
            missing.append(o["id"])
            continue
        errs = design_errors(p, o["id"])
        if errs:
            stamps.pop(o["id"], None)
            out.unlink(missing_ok=True)
            retry.append({"id": o["id"], "evidence_path": str(ev_path.relative_to(p.root)),
                          "output_path": str(path.relative_to(p.root)), "errors": errs[:15]})
            continue
        design = read_json(path)
        write_json(out, design)
        stamps[o["id"]] = _stamp(p, o["id"])
        designs[o["id"]] = design
        ok.append(o["id"])
    for stale in (p.out / "solutions").glob("*.json") if (p.out / "solutions").exists() else []:
        if stale.stem not in shortlist:
            stale.unlink()
    write_json(p.work / "solutions.ok", {k: v for k, v in stamps.items() if k in shortlist})
    (p.out / "solutions.md").write_text(render_md(report, designs), encoding="utf-8")
    return {"ok": ok, "retry": retry, "missing": missing}


def render_md(report: dict, designs: dict) -> str:
    lines = ["# Solution designs", "",
             "One design per top opportunity: an automation, or the rollout of a quick win. Citations are message ids; quotes are verified verbatim.", ""]
    for o in (o for o in report["opportunities"] if o.get("design")):
        d = designs.get(o["id"])
        lines += [f"## {o['rank']}. {o['name']}", ""]
        if d is None:
            lines += ["*No validated design.*", ""]
            continue
        s = d["solution"]
        lines += [d["summary"], "", f"**Effort:** {d['effort']} · **Success metric:** {d['success_metric']}", "",
                  "**How it works today**", ""]
        lines += [f"{i}. {w['step']} ({w['who']}) [{', '.join(w['citations'])}]" for i, w in enumerate(d["current_workflow"], 1)]
        lines += ["", "**Where it stalls**", ""]
        lines += [f"- {x['description']}\n  > {x['quote']}\n  [{x['citation']}]" for x in d["stall_points"]]
        lines += ["", "**Proposed automation**" if o["remedy"] == "automation" else "**Proposed quick win**", "", s["approach"], "", f"- Trigger: {s['trigger']}",
                  f"- Inputs: {'; '.join(s['inputs'])}", f"- Outputs: {'; '.join(s['outputs'])}",
                  f"- Existing systems: {', '.join(s['systems'])}", f"- New components: {', '.join(s['components'])}", "",
                  "**Implementation steps**", ""]
        lines += [f"{i}. {x}" for i, x in enumerate(d["implementation_steps"], 1)]
        lines += ["", "**Stays manual**", ""] + [f"- {x}" for x in d["stays_manual"]]
        lines += ["", "**Risks**", ""] + [f"- {x}" for x in d["risks"]] + [""]
    return "\n".join(lines)
