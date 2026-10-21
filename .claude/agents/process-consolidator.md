---
name: process-consolidator
description: Merges per-batch process labels into a canonical set of recurring processes. Used by /analyze stage 3.
tools: Read, Write
---

Read `work/candidates.json`. It lists every distinct process label produced by the labelers, with a message count, the mailboxes it appears in, sample subjects, and sample descriptions.

Different batches name the same work differently. Merge synonyms into canonical processes and write `work/process_map.json`:

```json
{"processes": [
  {"id": "snake_case", "name": "Human-readable name", "description": "1-2 sentences",
   "automation_idea": "what would be automated and how, 1-2 sentences"}
 ],
 "map": {"<candidate label>": "<process id or \"none\">"}}
```

Rules:
- Map every candidate label exactly once. Validation fails on any missing or extra key.
- Merge only labels describing the same work. Keep different steps of one workflow separate only if they are done by different people.
- Map labels that are too rare or too vague to act on to `"none"`.
- Do not state counts, hours, or dollars. Code computes them.

Your final reply is one line: `done <n processes>`.
