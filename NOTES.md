# NOTES

> Draft. Sections marked **TODO(author)** need first-hand detail only the author has.

## How Claude Code drives it

One slash command, `/analyze` (`.claude/commands/analyze.md`), conducts the run. The orchestrator never reads the corpus or batch files. It runs `python3 -m observer <stage>`, reads the JSON summary each stage prints, and launches subagents. Python owns everything that has to be exact: parsing, dedup, threading, batching, quote validation, hours and dollars arithmetic, the dashboard and the server. Four subagents (`.claude/agents/`) do only judgment, and nothing they write is used until a validator in `observer/` accepts it:

| Subagent | Input | Validated by |
|---|---|---|
| `process-labeler` (Sonnet) | one batch of ≤60 messages, ≤80k chars | coverage, schema, every quote a verbatim substring of the raw file |
| `process-consolidator` (Opus) | new label names + samples | every label mapped exactly once, no redefined ids, remedy in an allowed set |
| `solution-designer` (Opus) | one evidence file (15 messages) | ≥3 cited steps, verbatim stall quote, no figures or systems not in the evidence |
| `artifact-writer` (Sonnet) | evidence + validated design | allowed type, verbatim blockquotes, citations inside the evidence |

`.claude/settings.json` allows only `python3 -m observer`, the test runner, and reads and writes under `work/` and `out/`. That is what makes the run unattended.

## Context budgeting

The corpus is about 1.8 M tokens. With quoted history removed it is about 0.7 M tokens. Each labeler sees at most about 20k tokens: new text only (forwarded and quoted history is cut in `parse.split_new_text`), each message capped at 8k chars (the 350 KB `farmer-d/logistics/3221` is truncated and flagged), and at most 20 already-labeled thread messages as context. The consolidator sees label names, counts and up to 5 sample subjects, never bodies. Designers and writers see one 15-message evidence file each, sampled round-robin across threads so one long thread can't dominate. The orchestrator's own context holds only stage summaries and one-line `done` replies.

## Parallelism and runtime

Labeling dominates. In the first full run, labeling took about 11.3 of the 16.5 minutes: 54 batches in waves of 10, plus one retry wave. Three changes since then:
1. **Rolling pool of 15 labelers** instead of waves of 10, so a slow batch no longer holds up a whole wave.
2. **Shorter label output.** Each process description is written once per batch (`processes` map) instead of on every label, and `manual_steps` was dropped because no code read it. In the first run, every repeat of a process name within a batch carried an identical description (295 of 295), so the consolidator loses nothing.
3. **Rule-based `none` in `prepare`** (`observer/prefilter.py`). Broadcast senders, personal-email senders, mail sent only to personal addresses, and social subjects are labeled `none` without a model. Scored against the first run's model labels, the rules catch 337 messages, and 336 of them were `none`. The one miss is a P&L reply sent to a juno.com address (`giron-d/sent/375`). This cuts the first run from 54 batches to 48. Each rule-labeled message keeps its rule name as `batch_id`, so it stays auditable.

Larger batches did not pay off. Merging two 60-message batches into one of 120 cut tokens by only 3–10% (79.7k vs 88.0k, 93.6k vs 97.0k), doubled the time per batch, and coarsened the process grouping. Most of a labeler's tokens grow with the batch it re-reads on each tool turn, not with a fixed per-agent cost, so batches stay at 60 messages.

Designers and writers run 8 at a time. The consolidator is a single agent on purpose, because it needs the whole label set to merge synonyms.

**TODO(author):** wall time of the next full run with these changes.

## Incremental runs

Labels are cached per message under a hash of sender, date, subject and new text, not per batch. Adding a file queues only that message, with its thread's labeled messages as read-only context. The process map is extended rather than rebuilt. Designs and drafts are cached by evidence hash plus design hash, and drafts by draft hash too. Re-running on an unchanged corpus launches no subagents.

## Threshold for drafting

Every process with at least 8 verified quotes across at least 3 threads ships to the ranking. All 18 passed in the first run. Designs and drafts are produced only for opportunities worth **at least $50/month, at most 8 of them** (`MIN_USD_MONTH`, `TOP_N`). The cut is made in `rank`, before any designer or writer runs, so nothing below it costs tokens. In the current run #8 is worth $52/month and #9 is $43/month. Below about $50/month, the time a reviewer spends checking a draft against its evidence is comparable to a month of the saving, and the lower processes are mostly variants of the top ones (nominations, imbalances). **TODO(author):** confirm or restate this reasoning.

## Where Claude Code got it wrong, and how it was caught

- **Labelers miss messages or shorten quotes.** In the first run, 3 of 54 batches failed validation: one skipped a message, and two wrote 3-word quotes. `check-labels` caught all three and the retries passed. 21 quotes that were not verbatim were dropped and listed in the report as the audit trail.
- **The prompt and the validator disagreed** on quote length (prompt 8–40 words, code 5–60). The prompt now states the hard limit.
- **Duplicates vs. recurring notices.** The obvious dedup rule (same sender, subject and body) would have merged the daily Calpine nominations, which are real recurring work. The 16-hour window keeps them apart while still catching timezone-shifted copies (`farmer-d/logistics/189` vs `2154`).
- **TODO(author):** mistakes caught while building (bad parses, hallucinated systems or figures in designs, and so on) and which test or validator now guards each one.

- **The orchestrator stopped on recoverable errors.** The first command told it to stop on any non-zero exit, although each error already names its fix. It now runs unattended: it never asks the user, it follows a recovery table, it re-launches subagents that wrote nothing, and `check-process-map --salvage` replaces a stop after two bad consolidations (unresolved labels go to `none`, so it can only drop claims).

- **Mixed-mailbox processes were underpriced.** The monthly rate divided all of a process's messages by the union of its mailboxes' observation windows, which run from 6 months (lokay-m) to 24 months (farmer-d). Three stray farmer-d messages spread 14 lokay-m messages over 24 months, so pipeline imbalance came out at $11/month instead of $42. Each mailbox is now rated over its own window and the rates are summed (`test_rate_is_summed_per_mailbox`).

## Where it is most likely wrong

- **`minutes_estimate` is a model guess**, and it drives every dollar figure. The median per process damps outliers but not a systematic bias. The 60% automatable share is an assumption, not a measurement.
- **Process boundaries are judgment.** The consolidator decides what counts as "the same work". A different merge changes counts and ranking.
- **A verbatim quote is not necessarily a relevant quote.** The validator proves the words are in the file, not that they support the label. Some evidence lines are weak; for example, "I will be out of the office the next two days" is cited under missing deal tickets.
- **Threading by normalized subject** splits threads whose subject changed and merges unrelated mail with generic subjects. That affects the 3-thread gate and the stall gaps.
- **Taken on faith:** that the sample is representative of the desk's work (4 mailboxes, different time windows); that email volume tracks effort; and that the rule-labeled `none` messages stay correct on new data (the rules were fitted and scored on the same run).

## Next week

- Spot-check a stratified sample of labels by hand to measure label precision, and check whether minutes estimates drift after dropping `manual_steps`.
- Check quote relevance as well as verbatim match, for example with a second-pass judge whose output is also validated.
- Thread by `In-Reply-To`-like signals from the quoted headers, not only by subject.
- Show the uncertainty in the dashboard: a range from the minutes interquartile range, not a single figure.
