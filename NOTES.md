# NOTES

**Shipped run:** 3,240 files read, giving 3,201 unique messages and 2,535 threads. That produced 19 processes. The 8 shown opportunities total **$712/month**. The full unattended run took 8.8 minutes. A re-run on the unchanged corpus takes about 20 seconds and launches no subagents.

## How Claude Code drives it

One slash command, `/analyze`, conducts the run. The orchestrator never reads the corpus. It runs `python3 -m observer <stage>`, reads the JSON summary each stage prints, and launches subagents.

**The split:** Python does everything that must be exact. That covers parsing, dedup, threading, batching, quote checks, the arithmetic, the dashboard and the server. Four subagents do only judgment, and code validates their output before anything uses it:

| Subagent | Sees | Rejected by code if |
|---|---|---|
| `process-labeler` (Sonnet, 48 batches, pool of 15) | one batch of up to 60 messages | a message is skipped, the schema is wrong, or a quote is not verbatim in the raw file |
| `process-consolidator` (Opus, 1) | label names, counts and sample subjects, no bodies | a label is unmapped, an id is redefined, or the remedy is not allowed |
| `solution-designer` (Opus, 8) | one evidence file (15 messages) | it cites fewer than 3 steps, a stall quote is not verbatim, or a figure or system is not in the evidence |
| `artifact-writer` (Sonnet, 8) | the evidence file and its validated design | the artifact type is not allowed, a blockquote is not verbatim, or a citation is outside the evidence |

**Why this shape:** the corpus is about 30 context windows. Fanning out is the only way to read all of it, and code checks are the only way to trust what comes back.

**Unattended:** `settings.json` pre-approves only `python3 -m observer` and file access under `work/` and `out/`. `analyze.md` forbids asking the user, maps each error to the stage that fixes it, and relaunches once any subagent that wrote nothing.

## Decisions and their trade-offs

- **Labelers see new text only.** Cutting quoted and forwarded history takes the corpus from about 1.8M to about 0.7M tokens; each message is capped at 8k characters. *Trade-off:* context that only appears in the quoted part is lost. Up to 20 labeled messages from the same thread go along as read-only context.
- **Fewer tokens and less time in labeling:**
  - Labeling went from 11.3 of 16.4 minutes in the first version to about 4.6 minutes, retry included.
  - **A rolling pool of 15** replaced waves of 10, so one slow batch no longer holds up a wave.
  - **Shorter output:** each process description is written once per batch, not on every label (all 295 repeats in the first run were identical).
  - **A rule-based `none` label** (`prefilter.py`) covers broadcast senders, personal addresses and social subjects. It handles 337 messages without a model, cutting 54 batches to 48. 336 of the 337 matched the first run's model labels (the miss is `giron-d/sent/375`). *Trade-off:* the rules were written and scored on the same data.
  - **Bigger batches were rejected.** Going from 60 to 120 messages saved 3–10% of tokens (79.7k vs 88.0k) but doubled the time per batch and coarsened the grouping.
- **Cached by content hash.** Labels are cached per message; designs and drafts by the hashes of their evidence and design. A new file labels only that message. *Trade-off:* the process map is only extended, so a better regrouping needs a manual `--reconsolidate`.
- **Evidence gates instead of a cap on the number of processes.** A process ships only with at least 8 verified quotes across at least 3 threads.
- **Pricing:** `Σ(messages / months observed, per mailbox) × median minutes × 60% × $85`.
  - Each mailbox's own observation window is used, not the process's own span, so a burst is not priced as recurring.
  - The median damps outlier estimates. *Trade-off:* it likely runs low, since total time is count × mean.
- **Threshold: at least $50/month, at most 8.** Below about $50/month, reviewing a draft against its evidence costs about a month of the saving, and most processes below the cut are variants of ones above it. The cut is made in `rank`, before any designer or writer runs, so nothing below it costs tokens. Here #8 is $59 and #9 is $52.

## Where Claude Code got it wrong, and how it was caught

Every rejection is recorded in `work/caught.json` and counted on the dashboard's Method page. In the shipped run:
- **44 labeler quotes were dropped:** 35 too short and 9 not verbatim. They don't count as evidence and are listed in `report.md`.
- **1 batch was rejected** (7 of 28 quotes too short); its retry passed. The first version showed the same pattern: 3 of 54 batches failed (one skipped message, two with 3-word quotes) and all passed on retry.
- **The design and draft validators have never fired in a logged run,** so only unit tests back them.

Caught while building:
- **The prompt and the code disagreed** on quote length (8–40 words vs 5–60). The prompt now states the code's limit.
- **Dedup would have merged real recurring work,** such as the daily Calpine nominations. A 16-hour window keeps them apart and still catches timezone-shifted copies (`test_daily_repeats_stay_separate`).
- **Mixed-mailbox processes were underpriced** by dividing by the union of 6- to 24-month windows. Pipeline imbalance showed $11/month instead of $42 (`test_rate_is_summed_per_mailbox`).
- **The orchestrator stopped on errors it could fix.** It now follows a recovery table, checked with a fault-injection run, and `check-process-map --salvage` replaces stopping after two bad consolidations (unresolved labels go to `none`, which only drops claims).

## Where it is most likely wrong, and what was taken on faith

- **Minutes per message are model guesses,** and they drive every dollar figure. The 60% automatable share is an assumption.
- **Process boundaries are judgment.** A different consolidation changes the counts and the ranking.
- **A verbatim quote is not necessarily a relevant one.** Code proves the words are in the file, not that they support the label.
- **Threading by subject** splits renamed threads and merges unrelated mail with generic subjects, which affects the 3-thread gate and stall measurement.
- **One mailbox's view.** farmer-d contributes only its `logistics` folder; the figures are lower bounds.
- **Taken on faith:**
  - that 4 mailboxes are representative of the desk;
  - that email volume tracks effort;
  - that the prefilter rules hold on new data.

## Next steps

1. **Measure label quality:** hand-check a stratified sample of labels and minute estimates, and calibrate the minutes against it.
2. **Check that quotes are relevant,** not just verbatim, with a second-pass judge whose output is also validated.
3. **Price with a mean (trimmed) and show a range** on the dashboard instead of a single figure.
4. **Thread by the reply headers** embedded in the quoted text, not only by subject.
5. **Test the design and draft validators against deliberately broken agent output,** since real runs haven't exercised them yet.
