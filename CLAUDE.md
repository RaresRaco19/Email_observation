# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Greenfield. The repo currently holds only `README.md` (the assignment brief, which is the source of truth for requirements) and `corpus/`. No code, build, lint, or test commands exist yet. Add them here once they do. The directory is not a git repo yet. The final deliverable gets pushed to the user's own remote, and `.claude/` must be committed as it was actually used.

## Entry point: `/analyze`

`.claude/commands/analyze.md` runs the whole pipeline. The main session only conducts the run. It calls `python -m observer <stage>` for deterministic work and fans out judgment to the subagents in `.claude/agents/`: `process-labeler` (one per batch, in parallel), `process-consolidator` (one), and `artifact-writer` (one per opportunity above the threshold). Each subagent writes JSON or markdown to `work/` or `out/`, and a `check-*` stage validates it in code before anything uses it. The stage names and file contracts are defined in those files. Keep the Python CLI in sync with them. The `observer` package itself is not built yet.

## What is being built

An "observation agent" driven by Claude Code. One command must do all of the following over an Enron email subset:
1. Read **every** message (no sampling).
2. Identify the recurring processes: who touches them, how often, and where they stall.
3. Rank the automation opportunities, with hours per month and dollars per month at a **blended $85/hour**.
4. Cite every process and opportunity back to specific message files, each with a **verbatim quote**. Claims without valid evidence must not ship. The reviewer spot-checks quotes against the raw files.
5. Draft usable artifacts (an SOP, an email, a checklist, or a template) for opportunities above a chosen threshold, and justify that threshold in `NOTES.md`.
6. Serve a localhost dashboard with ranked opportunities, a running dollar total, and click-through from every number to its source message. It should be client-presentable.

## Hard constraints (from README)

- **No paid API calls.** Model work runs through Claude Code itself (subagents, skills, slash commands, hooks), not through an SDK with an API key.
- A full unattended run finishes in **under 30 minutes**.
- **Incremental runs.** Re-running on an unchanged corpus must not redo finished work, so cache by content hash.
- **Deterministic code (Python or TypeScript) owns everything that must be exact:** parsing, dedup, hours and dollars arithmetic, citation/quote validation, and the server. Models only judge and summarize, and their output is validated by code.
- **Tests must pass without invoking a model.**
- Everything runs locally.
- Deliverables: the repo, the `.claude/` dir as used, `NOTES.md` (two pages max, covering how Claude Code was driven, subagent/context budgeting, parallelism, caught mistakes, failure modes, and what was taken on faith), and the outputs of one real run (report, dashboard, logs, artifacts).

## Corpus facts

- 3,240 files, about 15 MB. That is roughly 30 times one context window, so work must be chunked and fanned out to subagents. Never read the whole corpus into one context.
- Layout: `corpus/<mailbox>/<folder>/<N>.`. Filenames end in a trailing dot and have no extension. Folders and file counts: `farmer-d/logistics` (1194), `giron-d/sent` (789), `giron-d/inbox` (380), `williams-w3/sent_items` (520), `williams-w3/inbox` (139), `lokay-m/sent_items` (161), `lokay-m/inbox` (57). A test should assert that the parsed total is 3,240, which proves every file was read.
- Format is raw RFC-822-ish Enron/Lotus export: `Message-ID`, `Date`, `From`, `To`, `Subject`, `X-From`/`X-To`/`X-cc`/`X-bcc`, `X-Folder`, `X-Origin`, `X-FileName`, then the body. Line endings are mixed CRLF and LF.
- Known messiness:
  - `corpus/giron-d/sent/795.` has no `Date:` header.
  - Two files have an empty `Message-ID:` (`giron-d/sent/501.` and `giron-d/sent/670.`), so Message-ID alone cannot be the dedup key.
  - Message-IDs and file contents are duplicated across files. Dedup on normalized content and Message-ID, not on path.
  - `corpus/farmer-d/logistics/3221.` is about 350 KB, versus a typical size of 50 KB or less. It needs chunking and truncation handling.
  - Forwarded and quoted blocks embed their own `Date:`/`From:` lines in many formats (`03/14/2001 09:36 AM`, `Saturday, September 30, 2000 8:41 AM`, and others). Parse only the top-level header block for message metadata.
- Quotes used as citations must be checked as exact substrings of the raw file. Normalize whitespace and line endings consistently on both sides, because bodies hard-wrap at about 76 columns.
