---
description: Run the full observation analysis over corpus/ (parse → label → validate → rank → draft → dashboard)
argument-hint: "[--force] [--no-serve]"
allowed-tools: Bash(python -m observer:*), Bash(python3 -m observer:*), Read, Agent
---

You are the orchestrator of a full analysis run. Arguments: `$ARGUMENTS`.

Ground rules for this run:
- Never read corpus files or batch files into your own context. Subagents read batches; Python reads the corpus. You only read the small JSON summaries that `python -m observer` prints.
- Never compute counts, hours, dollars, or verify quotes yourself. That is done by `python -m observer`, and its output is authoritative.
- Every stage is cached by content hash. Skip whatever the manifest marks `done`, unless `--force` is in the arguments.
- If any `python -m observer` step exits non-zero, stop and report its stderr. Do not work around it.

## Stage 1: Prepare (deterministic)

Run `python -m observer prepare $ARGUMENTS`. It parses every file, dedups, threads, splits new from quoted text, and writes `work/batches/<hash>.json` and `work/manifest.json`. It prints a JSON summary: file count (must be 3240), unique messages, threads, and a list of `pending_batches` (each with `id` and `path`).

## Stage 2: Label (parallel subagents)

For each pending batch, launch a `process-labeler` subagent. Pass it only the batch path and the output path `work/labels/<batch id>.json`. Launch up to 10 at a time in a single message, and wait for the whole wave to finish before launching the next one.

Then run `python -m observer check-labels`. It verifies coverage (every message in a batch has a label), the schema, and every quote against the raw file. Batches that fail come back in `retry_batches`. Re-run those once, passing the validator's error list to the subagent. A batch that fails twice is recorded as failed and the run continues.

## Stage 3: Consolidate processes (one subagent)

Run `python -m observer candidates`. It writes `work/candidates.json`, which lists the distinct process labels with counts and sample subjects (no bodies). Launch one `process-consolidator` subagent on it, writing `work/process_map.json`. Then run `python -m observer check-process-map`, which requires every candidate to be mapped exactly once.

## Stage 4: Rank (deterministic)

Run `python -m observer rank`. Code aggregates processes, frequency, participants, and stall times; computes hours/month and $/month at $85/h; drops any claim without validated evidence; and writes `out/report.json` and `out/report.md`. It prints the ranked opportunities and which of them clear the artifact threshold.

## Stage 5: Draft artifacts (parallel subagents)

For each opportunity in `artifact_targets` that is not already done, launch an `artifact-writer` subagent with the opportunity id and the paths it prints. Run all of them in parallel. Then run `python -m observer check-artifacts`, which validates citations inside the artifacts. Re-run a failing artifact once with the errors.

## Stage 6: Dashboard

Run `python -m observer build-dashboard`. Unless `--no-serve` is in the arguments, start `python -m observer serve` in the background and report its URL.

## Final report

Finish with a short summary: messages read, processes found, opportunities ranked, total $/month, artifacts drafted, rejected claims and failed batches (with reasons), wall-clock time per stage (from `work/run.log`), and the dashboard URL.
