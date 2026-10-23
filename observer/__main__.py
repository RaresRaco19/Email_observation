"""CLI: python3 -m observer <stage>. Each stage prints one JSON summary and logs its timing to work/run.log."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone

from . import artifacts, dashboard, labels, prepare, rank, server, solutions
from .config import default_paths

STAGES = {
    "prepare": lambda p, a: prepare.run(p, force=a.force, max_batches=a.max_batches),
    "check-labels": lambda p, a: labels.check_labels(p),
    "candidates": lambda p, a: labels.candidates(p, reset=a.reconsolidate),
    "check-process-map": lambda p, a: labels.check_process_map(p, salvage=a.salvage),
    "rank": lambda p, a: rank.build(p),
    "check-solutions": lambda p, a: solutions.check(p),
    "check-artifacts": lambda p, a: artifacts.check(p),
    "build-dashboard": lambda p, a: dashboard.build(p),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m observer")
    ap.add_argument("stage", choices=[*STAGES, "serve"])
    ap.add_argument("--force", action="store_true", help="prepare: wipe work/ and out/ first")
    ap.add_argument("--max-batches", type=int, default=None, help="prepare: list at most N pending batches (smoke tests)")
    ap.add_argument("--reconsolidate", action="store_true", help="candidates: rebuild the process map from scratch")
    ap.add_argument("--salvage", action="store_true",
                    help="check-process-map: merge the valid part of a failing delta and map the rest to none")
    ap.add_argument("--port", type=int, default=None)
    args, _unknown = ap.parse_known_args(argv)  # tolerate the rest of /analyze's $ARGUMENTS, e.g. --no-serve
    p = default_paths()
    if args.stage == "serve":
        server.serve(p, **({"port": args.port} if args.port else {}))
        return 0
    started = time.time()
    summary = STAGES[args.stage](p, args)
    p.work.mkdir(parents=True, exist_ok=True)
    with open(p.work / "run.log", "a", encoding="utf-8") as log:
        log.write(json.dumps({"stage": args.stage, "started": datetime.fromtimestamp(started, timezone.utc).isoformat(),
                              "seconds": round(time.time() - started, 2),
                              "summary": {k: v for k, v in summary.items() if not isinstance(v, list) or len(v) <= 50}}) + "\n")
    json.dump(summary, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
