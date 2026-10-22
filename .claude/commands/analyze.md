---
description: Run the full observation analysis over corpus/ (parse → label → validate → rank → design → draft → dashboard)
argument-hint: "[--force] [--max-batches N] [--reconsolidate] [--no-serve]"
allowed-tools: Bash(python3 -m observer:*), Read, Agent
---

You are the orchestrator of a full analysis run. Arguments: `$ARGUMENTS`.

Ground rules for this run:
- Never read corpus files or batch files into your own context. Subagents read batches; Python reads the corpus. You only read the JSON summaries that `python3 -m observer` prints.
- Never compute counts, hours, dollars, or verify quotes yourself. That is done by `python3 -m observer`, and its output is authoritative.
- Every stage is cached by content hash. Labels are cached per message, so a re-run after adding files labels only the new messages, and the process map is extended rather than rebuilt. `--force` (passed to prepare) wipes the cache.
- If any `python3 -m observer` step exits non-zero, stop and report its stderr. Do not work around it.

## Stage 1: Prepare (deterministic)

Run `python3 -m observer prepare $ARGUMENTS`. It parses every file, dedups, threads, splits new from quoted text, and batches only the messages that have no cached label (`messages_to_label`; `messages_cached` were labeled in earlier runs). `files` is the number of corpus files parsed (3,240 for the shipped corpus). If `pending_batches` is empty, launch no labelers but still run `check-labels`, which writes each message's label status into `work/messages.json` for the downstream stages. Note `pending_batches`, a list of `{id, path, output}`. `--max-batches N` limits that list for smoke tests.

## Stage 2: Label (parallel subagents)

For each pending batch, launch a `process-labeler` subagent (`subagent_type: "process-labeler"`) with this prompt: `Batch: <path>\nOutput: <output>`. Launch up to 10 in a single message, then wait for that whole wave before launching the next.

Then run `python3 -m observer check-labels`.
- For each entry in `retry_batches`, re-launch a labeler with the same prompt plus `\nPrevious attempt failed validation:\n<errors, one per line>`. Run all retries in one wave, then run `check-labels` again.
- Batches in `failed_batches` have failed twice. Note them and continue; their individually valid labels are still used.
- `not_labeled` counts batches that have no label file. With `--max-batches` that is expected. Otherwise, treat any batch you launched and still see unlabeled as failed.

## Stage 3: Consolidate processes (one subagent)

Run this stage once, after every labeling wave and its retries have finished, so the consolidator sees the full set of labels. Run `python3 -m observer candidates` (add `--reconsolidate` if it is in the arguments, to rebuild the map from scratch). It lists only labels not yet in the process map. If `needs_consolidation` is true, launch one `process-consolidator` subagent with the prompt `Candidates: work/candidates.json\nOutput: work/process_map_delta.json`. Then run `python3 -m observer check-process-map`, which validates the delta and merges it into `work/process_map.json` (run it even when no consolidation was needed). If it returns `"ok": false`, re-launch the consolidator once with the errors appended. If it fails a second time, stop and report the errors.

## Stage 4: Rank (deterministic)

Run `python3 -m observer rank`. It ships every process that clears the evidence gates (enough verified quotes across enough threads) and lists the rest as rejected with the reason. Only the top 8 by $/month are shown, totalled and worked on, and each has a `remedy`: `automation` or `quick_win`. It prints every ranked opportunity, the total of the top 8, `solution_targets` (each top-8 opportunity, `{id, remedy, evidence_path, output_path, done}`), and `artifact_targets` (the same opportunities, each `{id, remedy, evidence_path, solution_path, output_path, done}`). If `rank` says the process map predates remedies, rerun Stage 3 with `--reconsolidate`.

## Stage 5: Design solutions (parallel subagents)

Every target gets a design: the automation, or the rollout of the quick win. For every solution target with `done: false`, launch a `solution-designer` subagent with the prompt `Opportunity: <id>\nEvidence: <evidence_path>\nOutput: <output_path>`. Launch up to 10 in a single message and wait for the wave before the next. Then run `python3 -m observer check-solutions`. Re-launch each entry in `retry` once with `\nPrevious attempt failed validation:\n<errors, one per line>` appended, then run `check-solutions` again. Designs that are still invalid are left off the dashboard.

## Stage 6: Draft artifacts (parallel subagents)

For every artifact target with `done: false`, launch an `artifact-writer` subagent with the prompt `Opportunity: <id>\nEvidence: <evidence_path>\nSolution: <solution_path>\nOutput: <output_path>`. Launch writers only for targets whose design `check-solutions` has validated, because they build on it. A draft is cached against its evidence and design, so a changed design gets a new draft. Launch all of them in one message. Then run `python3 -m observer check-artifacts`. Re-launch each entry in `retry` once with its errors appended, then check again. Artifacts that are still invalid are left off the dashboard automatically.

## Stage 7: Dashboard

Run `python3 -m observer build-dashboard`. Unless `--no-serve` is in the arguments, start `python3 -m observer serve` with `run_in_background: true` and report http://127.0.0.1:8765/. If the port is already in use, a previous server is still running and already serves the new build.

## Final report

Finish with a short summary taken only from the printed summaries and `work/run.log`: files read, unique messages, messages labeled, opportunities shipped (and how many were rejected), total $/month, solution designs validated, drafts written (by remedy), rejected quotes, failed batches (with reasons), seconds per stage, and the dashboard URL.
