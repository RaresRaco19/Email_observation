# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Python 3.10, standard library only. Use `python3`, because this machine has no `python` command.

- Full run: `/analyze` (add `--max-batches 2` for a quick end-to-end test, `--reconsolidate` to rebuild the process map, or `--force` to wipe the `work/` and `out/` caches). Re-running after adding corpus files labels only the new messages.
- One stage by hand: `python3 -m observer <prepare|check-labels|candidates|check-process-map|rank|check-solutions|check-artifacts|build-dashboard|serve>`.
- Tests: `python3 -m unittest discover -s tests -t .`
- One test: `python3 -m unittest tests.test_pipeline.PipelineTest.test_rank_arithmetic`

The directory is not a git repo yet. The deliverable gets pushed to the user's own remote, with `.claude/`, `work/`, and `out/` committed as used in the real run.

## Architecture

`.claude/commands/analyze.md` conducts the run. Python does every exact step, and four subagents in `.claude/agents/` do judgment. Their output only enters the pipeline through a code validator:

1. `prepare` (`observer/prepare.py`, `parse.py`) parses the top header block of each file and splits the author's new text from quoted or forwarded history. It dedups and threads by normalized subject. Messages that `prefilter.py` rules mark as obvious non-work mail (broadcast senders, personal-email senders or recipients, social subjects) go straight into the store as `none` with `batch_id: rule:v<PREFILTER_VERSION>:<rule>`; bump the version when a rule changes. Then it batches only messages with no entry in `work/label_store.json`, which caches labels per message, keyed by a hash of sender, date, subject and new text. Adding a file therefore queues just that message, with already-labeled messages of its thread attached as read-only `context`. A first run rules 337 messages `none` and packs about 48 batches. It also writes `work/messages.json`, the metadata of every unique message (no bodies), with `checked: false`.
2. `process-labeler` subagents (a rolling pool of 15) label every message in a batch, each with a verbatim quote, and describe each process name once in a top-level `processes` map that `check-labels` copies onto the stored labels. `check-labels` (`labels.py`, `validate.py`) enforces coverage and the schema, and drops quotes that are not whitespace-normalized substrings of the raw file. A batch that fails is retried once, then marked failed. Accepted labels go into the store. It then writes each message's `status` (`valid`, `rejected`, `failed`, `unlabeled`), its `label`, and a `summary` that includes `rejected_quotes` back into `messages.json`, and sets `checked: true`. `candidates` and `rank` read only that file, and refuse it unless it was checked after the latest `prepare`.
3. `candidates` lists only label names not yet in `work/process_map.json`, plus the existing processes. `process-consolidator` maps them onto existing ids or new processes in `work/process_map_delta.json`. `check-process-map` requires every new label to be mapped exactly once and forbids redefining existing ids, then merges the delta. The labeler and consolidator prompts both describe a good process (a recurring, workflow-level unit of automatable work) and send non-work traffic (out-of-office, IT broadcasts, one-off projects) to `none`. There is no numeric cap; the evidence gates in `rank` are the quality bar. Each new process also gets a `remedy` (`automation`, or `quick_win` when a prepared reply, deadline checklist or request template would help more than a system) and an `action_idea`; `check-process-map` rejects any other remedy. Process ids stay stable across runs; `--reconsolidate` rebuilds the map from scratch. If the consolidator fails validation twice, `check-process-map --salvage` merges the valid part of the delta and maps every remaining label to `none`.
4. `rank` (`rank.py`) does all of the arithmetic: `Σ(msgs_mailbox / months_mailbox) × median minutes ÷ 60 × AUTOMATABLE_SHARE × $85`. Each mailbox's messages are rated over that mailbox's own observation window (first to last dated message, at least 1 month) and the rates are summed. A short-window mailbox is then not diluted by a long one, and bursts are still not priced as recurring because the window is the mailbox's, not the process's own span. It drops processes with fewer than `MIN_EVIDENCE` (8) valid quotes or `MIN_THREADS` (3) threads, ranks every process that passes by $/month, and keeps only those worth at least `MIN_USD_MONTH` ($50), at most `TOP_N` (8), in `opportunities` and the total; the rest go to `below_cutoff`. Each shown opportunity gets subagent work: a design (the automation, or the rollout of a quick win) and then a draft built on it. It refuses a process map without remedies. It writes `out/report.{json,md}` (including the rejected quotes, as the reviewer's audit trail) plus `work/evidence/<id>.json` only for those targets (15 messages sampled round-robin across threads, plus `allowed_types`). All constants live in `observer/config.py`.
5. `solution-designer` subagents write a structured design per target (automation or quick win) to `work/solutions/<id>.json`. `check-solutions` (`solutions.py`) requires at least 3 cited workflow steps and a verbatim stall quote, rejects citations outside the evidence, dollar figures not in `allowed_figures`, and `systems` not named in the evidence. It copies valid designs to `out/solutions/` and renders `out/solutions.md`; `work/solutions.ok` caches them by evidence and design hash.
6. `artifact-writer` subagents draft one artifact per target, built on its validated design: `reply`, `checklist` or `template` for a quick win, `sop` or proposal `email` for automation. `check-artifacts` (`artifacts.py`) rejects a type outside the evidence file's `allowed_types`, citations outside the evidence, blockquotes that are not verbatim, dollar figures that are not in `allowed_figures`, and drafts whose design is not validated. `work/artifacts.ok` caches each draft by evidence, design and draft hash, so a redesign triggers a redraft.
7. `build-dashboard` (`dashboard.py`) embeds the report and validated designs in one HTML file. `serve` (`server.py`) serves it on 127.0.0.1:8765 together with `/raw/<msg_id>` for drill-through.

The run is unattended: `analyze.md` forbids asking the user and holds a recovery table that maps each `SystemExit` message ("run prepare first", "predates remedies", and so on) to the stage that fixes it. Subagents that write no output are re-launched once.

Every `check-*` stage records what it rejected in `work/caught.json` (`observer/caught.py`), keyed by stage, item, content hash and error, so a re-check adds nothing. `build-dashboard` prints and shows the counts per category.

A message id is its corpus path without the trailing dot, for example `farmer-d/logistics/880`. Every stage appends its timing to `work/run.log`.

## What is being built

An "observation agent" driven by Claude Code. One command must do all of the following over an Enron email subset:
1. Read **every** message (no sampling).
2. Identify the recurring processes: who touches them, how often, and where they stall.
3. Rank the automation opportunities, with hours per month and dollars per month at a **blended $85/hour**.
4. Cite every process and opportunity back to specific message files, each with a **verbatim quote**. Claims without valid evidence must not ship. The reviewer spot-checks quotes against the raw files.
5. Draft usable artifacts (an SOP, an email, a checklist, or a template) for opportunities above a chosen threshold, and justify that threshold in `NOTES.md`.
6. Serve a localhost dashboard with ranked opportunities, a running dollar total, and click-through from every number to its source message. It should be client-presentable.

## Hard constraints (from the assignment brief)

- **No paid API calls.** Model work runs through Claude Code itself (subagents, skills, slash commands, hooks), not through an SDK with an API key.
- A full unattended run finishes in **under 30 minutes**.
- **Incremental runs.** Re-running on an unchanged corpus must not redo finished work, so cache by content hash.
- **Deterministic code (Python or TypeScript) owns everything that must be exact:** parsing, dedup, hours and dollars arithmetic, citation/quote validation, and the server. Models only judge and summarize, and their output is validated by code.
- **Tests must pass without invoking a model.**
- Everything runs locally.
- Deliverables: the repo, the `.claude/` dir as used, `NOTES.md` (two pages max, covering how Claude Code was driven, subagent/context budgeting, parallelism, caught mistakes, failure modes, and what was taken on faith), and the outputs of one real run (report, dashboard, logs, artifacts).

## Corpus facts

- 3,240 files, about 6.8 MB of text (`du` reports 15 MB because of block overhead), roughly 1.7–1.9 M tokens. Removing quoted history leaves about 2.6 M chars (~0.7 M tokens). That is far more than one context window, so work must be chunked and fanned out to subagents. Never read the whole corpus into one context.
- Layout: `corpus/<mailbox>/<folder>/<N>.`. Filenames end in a trailing dot and have no extension. Folders and file counts: `farmer-d/logistics` (1194), `giron-d/sent` (789), `giron-d/inbox` (380), `williams-w3/sent_items` (520), `williams-w3/inbox` (139), `lokay-m/sent_items` (161), `lokay-m/inbox` (57). A test should assert that the parsed total is 3,240, which proves every file was read.
- Format is raw RFC-822-ish Enron/Lotus export: `Message-ID`, `Date`, `From`, `To`, `Subject`, `X-From`/`X-To`/`X-cc`/`X-bcc`, `X-Folder`, `X-Origin`, `X-FileName`, then the body. Line endings are mixed CRLF and LF.
- Known messiness:
  - `corpus/giron-d/sent/795.` has no `Date:` header.
  - `corpus/lokay-m/inbox/74.` is dated 2031. Dates outside `DATE_RANGE` (1997–2002) are treated as missing and counted as `dates_out_of_range` in the manifest.
  - No file has an empty top-level `Message-ID`, but `giron-d/sent/501.` and `670.` contain an empty one inside an embedded message.
  - Copies exist across folders and mailboxes, sometimes re-wrapped and with a timezone-shifted `Date` (`farmer-d/logistics/189.` vs `2154.`, 10 h apart). Recurring notices such as the daily Calpine nomination repeat sender, subject, and body verbatim about 24 h apart. They are real occurrences and must not be merged, which is why `dedup` uses a 16-hour window. The result is 39 copies removed and 3,201 unique messages.
  - `corpus/farmer-d/logistics/3221.` is about 350 KB, versus a typical size of 50 KB or less. It needs chunking and truncation handling.
  - Forwarded and quoted blocks embed their own `Date:`/`From:` lines in many formats (`03/14/2001 09:36 AM`, `Saturday, September 30, 2000 8:41 AM`, and others). Parse only the top-level header block for message metadata.
- Quotes used as citations must be checked as exact substrings of the raw file. Normalize whitespace and line endings consistently on both sides, because bodies hard-wrap at about 76 columns.
