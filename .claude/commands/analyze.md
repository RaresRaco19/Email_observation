---
description: Run the full observation analysis over corpus/ (parse → label → validate → rank → design → draft → dashboard)
argument-hint: "[--force] [--max-batches N] [--reconsolidate] [--no-serve]"
allowed-tools: Bash(python3 -m observer:*), Read, Agent
model: sonnet
---

You are the orchestrator of a full analysis run. Arguments: `$ARGUMENTS`.

Ground rules for this run:
- Never read corpus files or batch files into your own context. Subagents read batches; Python reads the corpus. You only read the JSON summaries that `python3 -m observer` prints.
- Never compute counts, hours, dollars, or verify quotes yourself. That is done by `python3 -m observer`, and its output is authoritative.
- Every stage is cached by content hash. Labels are cached per message, so a re-run after adding files labels only the new messages, and the process map is extended rather than rebuilt. `--force` (passed to prepare) wipes the cache.
- **This run is unattended. Never ask the user anything, never offer choices, and never pause for confirmation.** When something goes wrong, apply the recovery below and keep going. The run ends only with the Final report.
- Run shell commands only as `python3 -m observer <stage> [flags]`, exactly as written here: no `cd`, pipes, `&&`, `cat` or `tail`. Read JSON and `work/run.log` with the Read tool.
- A subagent that errors, times out, or returns without `done …` counts as one failed attempt for its item. It never stops the run.

## Recovery

A non-zero exit from `python3 -m observer` is not a stop. Match its stderr, run the fix, then rerun the step that failed:

| stderr contains | fix |
|---|---|
| `run prepare first` | `prepare` with the original arguments minus `--force`, then continue from Stage 2 (only new messages get batched) |
| `run check-labels first` | `check-labels` |
| `run candidates first`, `run check-process-map first`, `labels are not in the process map` | Stage 3 (`candidates`, the consolidator if needed, `check-process-map`) |
| `predates remedies` | Stage 3 with `--reconsolidate` |
| `run rank first` | `rank` |
| `expected … corpus files` | run `prepare` once more; the corpus is the input, so report the count if it still differs |

Any other error: rerun the step once. If the same step fails again after its fix, do not invent a workaround and do not use `--force`. Record the stderr, skip to Stage 7 if `out/report.json` exists, and finish with the Final report.

## Stage 1: Prepare (deterministic)

Run `python3 -m observer prepare $ARGUMENTS`. It parses every file, dedups, threads, splits new from quoted text, and batches only the messages that have no cached label (`messages_to_label`; `messages_cached` were labeled in earlier runs). `files` is the number of corpus files parsed (3,240 for the shipped corpus). If `pending_batches` is empty, launch no labelers but still run `check-labels`, which writes each message's label status into `work/messages.json` for the downstream stages. Note `pending_batches`, a list of `{id, path, output}`. `--max-batches N` limits that list for smoke tests.

## Stage 2: Label (parallel subagents)

For each pending batch, launch a `process-labeler` subagent (`subagent_type: "process-labeler"`) with this prompt: `Batch: <path>\nOutput: <output>`. Run them as a rolling pool of 15: launch the first 15 in a single message, and each time a labeler reports `done …`, launch the next pending batch, so 15 keep running until the list is empty. Do not wait for a whole group to finish before launching more. Messages that `prepare` already labeled `none` by rule (`messages_ruled_none`) are not in any batch.

When every launched labeler has reported, run `python3 -m observer check-labels`.
- For each entry in `retry_batches`, re-launch a labeler with the same prompt plus `\nPrevious attempt failed validation:\n<errors, one per line>`. Run the retries through the same pool of 15, then run `check-labels` again once they have all reported.
- Batches in `failed_batches` have failed twice. Note them and continue; their individually valid labels are still used.
- `not_labeled` counts batches that have no label file. With `--max-batches` that is expected for batches you did not launch. Re-launch every batch you launched that still has no label file once, together with the retries (same prompt, plus `\nPrevious attempt wrote no output file.`). If it is still missing after that, note it as failed and continue.

## Stage 3: Consolidate processes (one subagent)

Run this stage once, after every labeling wave and its retries have finished, so the consolidator sees the full set of labels. Run `python3 -m observer candidates` (add `--reconsolidate` if it is in the arguments, to rebuild the map from scratch). It lists only labels not yet in the process map. If `needs_consolidation` is true, launch one `process-consolidator` subagent with the prompt `Candidates: work/candidates.json\nOutput: work/process_map_delta.json`. Then run `python3 -m observer check-process-map`, which validates the delta and merges it into `work/process_map.json` (run it even when no consolidation was needed). If it returns `"ok": false`, re-launch the consolidator once with the errors appended. If it fails a second time, run `python3 -m observer check-process-map --salvage`: code merges the valid part of the delta and maps every remaining label to `none` (this can only drop claims, never add them). Note `processes_dropped` and `labels_forced_none` and continue.

## Stage 4: Rank (deterministic)

Run `python3 -m observer rank`. It ships every process that clears the evidence gates (enough verified quotes across enough threads) and lists the rest as rejected with the reason. Only opportunities worth at least $50/month (`MIN_USD_MONTH`), at most 8 (`TOP_N`), are shown, totalled and worked on; nothing below that cut gets a target, so no designer or writer is launched for it. Each shown opportunity has a `remedy`: `automation` or `quick_win`. It prints every ranked opportunity, the total of the shown ones, `solution_targets` (each shown opportunity, `{id, remedy, evidence_path, output_path, done}`), and `artifact_targets` (the same opportunities, each `{id, remedy, evidence_path, solution_path, output_path, done}`). If `rank` says the process map predates remedies, rerun Stage 3 with `--reconsolidate`.

## Stage 5: Design solutions (parallel subagents)

Every target gets a design: the automation, or the rollout of the quick win. For every solution target with `done: false`, launch a `solution-designer` subagent with the prompt `Opportunity: <id>\nEvidence: <evidence_path>\nOutput: <output_path>`. Launch up to 10 in a single message and wait for the wave before the next. Then run `python3 -m observer check-solutions`. Re-launch each entry in `retry` once with `\nPrevious attempt failed validation:\n<errors, one per line>` appended, and each entry in `missing` (no design file was written) once with the original prompt, then run `check-solutions` again. Designs that are still invalid are left off the dashboard.

## Stage 6: Draft artifacts (parallel subagents)

For every artifact target with `done: false`, launch an `artifact-writer` subagent with the prompt `Opportunity: <id>\nEvidence: <evidence_path>\nSolution: <solution_path>\nOutput: <output_path>`. Launch writers only for targets whose design `check-solutions` has validated, because they build on it. A draft is cached against its evidence and design, so a changed design gets a new draft. Launch all of them in one message. Then run `python3 -m observer check-artifacts`. Re-launch each entry in `retry` once with its errors appended (a writer that wrote nothing shows up as `artifact file missing`), then check again. Artifacts that are still invalid are left off the dashboard automatically.

## Stage 7: Dashboard

Run `python3 -m observer build-dashboard`. Unless `--no-serve` is in the arguments, start `python3 -m observer serve` with `run_in_background: true` and report http://127.0.0.1:8765/. If the port is already in use, a previous server is still running and already serves the new build; that is not an error.

## Final report

Finish with a short summary taken only from the printed summaries and `work/run.log`: files read, unique messages, messages labeled, opportunities shipped (and how many were rejected), total $/month, solution designs validated, drafts written (by remedy), rejected quotes, mistakes caught by validators (the `caught` counts that `build-dashboard` prints), failed batches (with reasons), every recovery applied (retries, re-launches, `--salvage`, errors that ended the run early), seconds per stage, and the dashboard URL.
