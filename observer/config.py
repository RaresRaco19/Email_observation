"""Tunable constants and filesystem layout. Every number the pipeline reports derives from these."""
import os
from dataclasses import dataclass
from pathlib import Path

RATE_USD = 85                 # blended $/hour (assignment brief)
AUTOMATABLE_SHARE = 0.6       # fraction of handling time automation is assumed to remove
BATCH_MAX_CHARS = 80_000      # ~20k tokens of message text per labeler subagent
BATCH_MAX_MSGS = 60           # caps labeler output size per batch
MSG_MAX_CHARS = 8_000         # per-message truncation (farmer-d/logistics/3221 is ~350 KB)
MIN_EVIDENCE = 8              # validated quotes a process needs to ship
MIN_THREADS = 3               # distinct threads it needs: one long conversation is not a recurring process
TOP_N = 8                     # opportunities shown and totalled; each gets a design and a draft built on it
REMEDIES = {"automation", "quick_win"}
# artifact types a writer may choose, by remedy
ARTIFACT_TYPES = {"automation": ["sop", "email"], "quick_win": ["reply", "checklist", "template"]}
BAD_QUOTE_LIMIT = 0.2         # batch fails if more than this share of its quotes are invalid
MAX_ATTEMPTS = 2
DATE_RANGE = ("1997-01-01", "2002-12-31")  # dates outside the corpus period (lokay-m/inbox/74 says 2031) count as undated
STALL_GAP_MAX_DAYS = 30       # thread gaps longer than this are treated as unrelated, not stalls
PORT = 8765


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def corpus(self): return self.root / "corpus"
    @property
    def work(self): return self.root / "work"
    @property
    def out(self): return self.root / "out"
    @property
    def batches(self): return self.work / "batches"
    @property
    def labels(self): return self.work / "labels"
    @property
    def evidence(self): return self.work / "evidence"
    @property
    def artifacts(self): return self.out / "artifacts"
    @property
    def dashboard(self): return self.out / "dashboard"


def default_paths() -> Paths:
    return Paths(Path(os.environ.get("OBSERVER_ROOT", Path(__file__).resolve().parent.parent)))
