# Email observation agent

This tool reads every message in an email archive (here, 3,240 Enron emails in `corpus/`) and finds the recurring work in it. It ranks the automation opportunities by dollars per month at $85/hour, and drafts an SOP, email, checklist or template for each of the top ones. A local dashboard shows the result, with every figure linked to the source email it came from.

Claude Code runs the whole pipeline. Python handles everything that has to be exact: parsing, deduplication, the arithmetic, and checking that each quote appears verbatim in its source file. Subagents handle only the judgment calls, and code validates their output before it is used. See `NOTES.md` for the design and its trade-offs.

## Requirements

- Python 3.10 or later. It uses only the standard library.
- [Claude Code](https://claude.com/claude-code), which needs a subscription but no API key.

## Run

Open Claude Code in the repo folder and run:

```
/analyze
```

A full run takes about 10 minutes. It ends by serving the dashboard at http://127.0.0.1:8765/. Running it again on an unchanged corpus reuses the cached results.

| Option | Effect |
|---|---|
| `--max-batches 2` | quick end-to-end test |
| `--no-serve` | build the dashboard without starting the server |
| `--reconsolidate` | rebuild the process map from scratch |
| `--force` | wipe the caches in `work/` and `out/` and start over |

To view the results of an earlier run without running it again:

```
python3 -m observer serve
```

## Tests

The tests run without a model.

```
python3 -m unittest discover -s tests -t .
```

## Output

- **`out/report.md`, `out/report.json`:** the ranked opportunities, with their arithmetic and the quotes that back them.
- **`out/solutions/`, `out/artifacts/`:** the design and the drafted artifact for each opportunity shown.
- **`out/dashboard/index.html`:** the dashboard.
- **`work/run.log`:** how long each stage took. `work/caught.json` lists the agent mistakes that validation rejected.
