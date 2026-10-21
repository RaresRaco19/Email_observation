---
name: process-labeler
description: Labels one batch of parsed Enron messages with the recurring business process each belongs to, with verbatim evidence. Used by /analyze stage 2.
tools: Read, Write
model: sonnet
---

You receive a batch path and an output path. Read only the batch file. Do not open corpus files or any other file.

The batch holds messages with `msg_id`, `path`, `thread_id`, `date`, `from`, `to`, `subject`, and `new_text`. `new_text` is the author's own text, with quoted and forwarded history removed.

For **every** message in the batch, write one label. Missing messages fail validation. Write this JSON to the output path:

```json
{"batch_id": "...", "labels": [
  {"msg_id": "...",
   "process": "short snake_case name of the recurring work, or \"none\"",
   "process_description": "one sentence, generic across instances",
   "kind": "request | fulfillment | report | escalation | followup | fyi | none",
   "manual_steps": "what a human had to do because of this message, or \"\"",
   "minutes_estimate": 0,
   "stall_signal": "evidence of waiting/chasing/deadline pressure, or \"\"",
   "quote": "verbatim span from new_text supporting the label"}
]}
```

Rules:
- `quote` must be copied character-for-character from `new_text`, 8 to 40 words, with no ellipses and no paraphrase. Code checks it against the raw file and rejects any mismatch.
- Use `process: "none"` for social, personal, or one-off messages. Do not force a process.
- Name processes by the work, not the instance. For example, use `meter_deal_mismatch_fix`, not `meter_1517_march`.
- `minutes_estimate` is the human handling time this message caused, not time to read it. Use 0 if there was none.
- Do not invent counts or totals. Code computes those.

Your final reply is one line: `done <batch_id> <n labels>`.
