# NOTES

**Shipped run:** 3,240 files read, giving 3,201 unique messages and 2,535 threads. That produced 19 processes. The 8 shown opportunities total **$712/month**. The full unattended run took 8.8 minutes. A re-run on the unchanged corpus takes about 20 seconds and launches no subagents.

## How Claude Code drives it

One slash command, `/analyze`, conducts the run. The orchestrator never reads the corpus. It runs `python3 -m observer <stage>`, reads the JSON summary each stage prints, and launches subagents.

**The split:** Python does everything that must be exact (next chapter). Four subagents do only judgment, and code validates their output before anything uses it:

| Subagent | Sees | Rejected by code if |
|---|---|---|
| `process-labeler` (Sonnet, 48 batches, pool of 15) | one batch of up to 60 messages | a message is skipped, the schema is wrong, or a quote is not verbatim in the raw file |
| `process-consolidator` (Opus, 1) | label names, counts and sample subjects, no bodies | a label is unmapped, an id is redefined, or the remedy is not allowed |
| `solution-designer` (Opus, 8) | one evidence file (15 messages) | it cites fewer than 3 steps, a stall quote is not verbatim, or a figure or system is not in the evidence |
| `artifact-writer` (Sonnet, 8) | the evidence file and its validated design | the artifact type is not allowed, a blockquote is not verbatim, or a citation is outside the evidence |

**Why this shape:** the corpus is about 30 context windows. Fanning out is the only way to read all of it, and code checks are the only way to trust what comes back.

**Unattended:** `settings.json` pre-approves only `python3 -m observer` and file access under `work/` and `out/`. `analyze.md` forbids asking the user, maps each error to the stage that fixes it, and relaunches once any subagent that wrote nothing.

## Why the deterministic work is a Python module

`observer/` (standard library only, run as `python3 -m observer <stage>`) does every step whose answer has exactly one correct value. That covers parsing, dedup, threading, batching, the prefilter, quote checks, the arithmetic, the evidence files, the dashboard and the server.
- **Cost:** these steps touch the whole corpus on every run. Parsing and dedup with a model would mean pushing all 1.8M tokens through agents just to get the same answer every time. Python does it in about 2 seconds, and all deterministic stages together take under 3 seconds, at zero tokens.
- **Checking is cheap enough to do completely.** Every quote, about 1,300 per run, is matched against its raw file. Having a model check them would cost about as much as labeling again, and the checker would then need checking.
- **Exact and testable.** The same input gives the same dollars every run, and 50 tests cover it without a model, as the brief requires.
- **It keeps the orchestrator small.** It reads one JSON summary per stage, never message text.

## Why labelers run in parallel

- **No single agent can read it all.** Even with quoted history cut, the corpus is about 0.7M tokens, far beyond one context. It is split into 48 batches of up to 60 messages, about 20k tokens each.
- **Batches are independent.** A message's label depends only on its own text and its thread's context, which goes along with the batch. Labelers don't need to talk to each other, so they can all run at once.
- **Time:** at about a minute per batch, labeling one batch after another would take close to an hour, against a 30-minute budget. A rolling pool of 15 finishes in about 4–5 minutes.
- **Small, isolated failures.** A small batch keeps each agent's context short, and a batch that fails validation is retried on its own.
- **Trade-off:** each labeler names processes without seeing the other batches, so the same work gets different names. A single consolidator then merges these names. It runs alone on purpose, because it needs the full set of names.

## Decisions and their trade-offs

- **Labelers see new text only.** That shrinks the corpus from about 1.8M to about 0.7M tokens. *Trade-off:* context that exists only in the quoted part is lost; thread context partly makes up for it.
- **Labeling cost was cut where it didn't cost accuracy.** It went from 11.3 to 4.6 minutes:
  - a rolling pool of 15;
  - each process description written once per batch;
  - a rule-based `none` label for 337 obvious non-work messages (336 matched the model).
  - Bigger batches (120 messages) saved only 3–10% of tokens and doubled the time per batch. *Trade-off:* the rules were scored on the same data they were written from.
- **Everything is cached by content hash,** so a re-run redoes nothing. *Trade-off:* the process map is only extended; regrouping needs `--reconsolidate`.
- **Pricing uses the median minutes and each mailbox's own window.** *Trade-off:* the median likely runs low.
- **Threshold: at least $50/month, at most 8.** Below that, reviewing a draft costs about a month of the saving. The cut happens before the designers run, so nothing below it costs tokens.

## Where Claude Code got it wrong, and how it was caught

- **In the run, validators rejected agent output before it shipped.** Each rejection is recorded in `work/caught.json`.
- **Labeler quotes:** 44 were dropped (35 too short, 9 not verbatim) and 1 batch was retried. The design and draft validators never fired.
- **Mistakes caught while building:**
  - The monthly rate diluted processes that span several mailboxes (pipeline imbalance showed $11/month instead of $42).
  - Dedup would have merged the daily recurring notices.
  - Tests now cover both.

## Where it is most likely wrong, and what was taken on faith

- **Minutes per message are model guesses,** and the 60% automatable share is an assumption. Together they drive every dollar figure.
- **A verbatim quote is not necessarily a relevant one.** Code proves the words are in the file, not that they support the label.

## Next steps

1. **A hook that validates on write.** A `PostToolUse` hook on `Write` (label, design and draft paths) runs a new `observer check-file <path>`. On failure it exits with code 2, so the agent gets the errors and fixes them in the same turn. That removes most retries and recovers dropped quotes.
2. **A new `evidence-judge` agent** (Haiku, one per shown opportunity) marks each quote as `supports` or `weak`. A `check-evidence` validator enforces one verdict per message, and `rank` stops counting `weak` quotes towards the evidence gate. Verdicts are cached by evidence hash.
3. **Threading by reply headers, in code.** `parse.QUOTE_MARKERS` already finds the embedded reply headers. Match their sender and date to a parsed message, link each reply to its parent with union-find, and keep the subject as the fallback.
4. **Mutation tests for the design and draft validators.** Fixtures with an invented figure, an unnamed system, a paraphrased quote and an outside citation must each be rejected with the right category. Real runs have never exercised these validators.
