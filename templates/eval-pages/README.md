# Eval page templates

Three one-file HTML pages for showing evals to the people who decide on them: a **results page** for every scorer run by run, a **code check page** and an **LLM judge page** that show one scorer word for word with its results. Each page has buttons for agreeing or disagreeing with the scorer's calls, so reading results turns into labeling for the next round of alignment.

Each template is static HTML with one slot for your data. Your coding agent writes the JSON from your own runs, and `build_page.py` fills in the template. There's no server and no build step, and the only thing the page loads from outside is Google Fonts.

```bash
python3 build_page.py results examples/mapper-results.json --out results.html
python3 build_page.py code-check examples/mapper-code-check.json --out check.html
python3 build_page.py judge examples/mapper-judge.json --out judge.html
```

| Template | Shows | Example (Mapper, fall 2026 Week 3) |
|---|---|---|
| [`results.html`](results.html) | Every scorer's pass rate per run, against its release threshold, in two groups: fixes to keep fixed, and codes still to hill-climb. Which sessions changed with each fix, and every session as a row of pass or fail dots that opens into what the user saw. | [page](examples/mapper-results.html) · [data](examples/mapper-results.json) |
| [`code-check.html`](code-check.html) | The prompt that wrote the check, the check's code with its key parts marked, the dataset, pass rates per run, and five sessions to agree or disagree with. | [page](examples/mapper-code-check.html) · [data](examples/mapper-code-check.json) |
| [`judge.html`](judge.html) | The prompt that wrote the judge, the judge prompt split into the seven parts of a good judge (with a weak judge to compare), up to ten verdicts to call yourself with agreement counted, and the whole file. | [page](examples/mapper-judge.html) · [data](examples/mapper-judge.json) |

The examples come from Mapper, the course's market research agent: a 10-row sample of its 30-row course dataset scored on v1 and v1.1, its half-empty columns check (TC-8, rubric line X2) and its metric scope judge (TC-4, rubric line O3).

To have your agent make these, point it here once you have scored runs: "Build the results page from templates/eval-pages for runs A and B, and a judge page for my metric scope judge." The [`eval-code`](../../skills/eval-code/SKILL.md) and [`eval-llm-judge`](../../skills/eval-llm-judge/SKILL.md) skills write the scorers; these pages show them.

## The data

Every field is plain JSON. Optional fields can be left out, and the page drops that part.

### Shared: a row

A row is one session in one run, as the user saw it.

```json
{
  "id": "n05", "group": "metric scope", "expected": "answer", "input": "streaming services by subscribers",
  "scores": { "x2": { "score": 0, "reason": "Half-empty column(s): \"Content Budget\" (4 of 6 empty)." } },
  "cards": [{ "tool": "generate_market_map", "title": "Global Video Streaming Services",
              "cols": ["Subscribers", "Content Budget"], "rows": [["Netflix", "~325M (2025/2026)", "~$18B (2026 est.)"]],
              "body": null,
              "flags": [{ "scorer": "x2", "cols": [1], "cells": [[1, 1]], "note": "half empty", "colNotes": { "1": "4 of 6 empty" } }] }],
  "said": [{ "user": "streaming services by subscribers", "text": "I'll map the top streaming services by subscribers. Sound good?" }]
}
```

- `cards` hold the output: a table (`cols`, and `rows` that start with the row's name) or a `body` of text. Use whatever your product returns, flattened this way.
- `flags` (optional) mark what a scorer counted against a card: whole columns (`cols`, by index), cells (`cells`, as `[row, column]`), and a note per column (`colNotes`). The results page highlights them when that scorer fails the row.
- `said` is the conversation: what the user typed each turn and the agent's text.
- `scores` has one entry per scorer id, with `score` set to 1 or 0 and a one-sentence `reason`. On the code check page a row carries its one scorer's `score` and `reason` directly.

### `results.html`

```json
{
  "title": "Mapper scorer runs", "eyebrow": "Mapper · course scorers", "headline": "How each version scores, run by run",
  "standfirst": "Every scorer on the 30-row course dataset…", "foot": "…",
  "runs": [{ "key": "w3-v1", "label": "v1", "note": "Week3 v1 production baseline", "scored_at": "2026-11-04T06:11:36Z", "rows": [] }],
  "scorers": [{ "id": "g2", "rubric": "G2", "code": "TC-1", "name": "Links retrieved, and they open", "kind": "Code",
                "group": "fixed", "threshold": 100, "fix": "Harness: resolve redirects, cite from a numbered list" },
              { "id": "o3", "rubric": "O3", "code": "TC-4", "name": "Metric scope", "kind": "Judge",
                "group": "climb", "threshold": 90, "live": true, "target": true }],
  "next": { "label": "v2", "when": "Nov 11", "what": "The metric scope fix" }
}
```

- List `runs` in order. The first run is the "before" for the `fixed` group, and the `climb` group shows every run after the first.
- `group` is `fixed` for a scorer that keeps a shipped fix fixed, or `climb` for a code still to move. `kind` is `Code` or `Judge`.
- `threshold` is the release bar as a pass-rate percent, or `null` if none is set. `live: true` labels a scorer with no scores yet as "written live". `target: true` marks the scorer the `next` version is meant to fix. `next` is optional.

### `code-check.html`

```json
{
  "title": "TC-8 Code Check Demo", "eyebrow": "…", "headline": "TC-8, half-empty columns", "lede": "…",
  "prompt": { "text": "Use the eval-code skill to write a code check for TC-8…", "note": "Typed into Claude…" },
  "prep": "cp -R runs/w3-v1 runs/w3-v1-x2\nnpm run score -- runs/w3-v1-x2 --local --scorers _x2",
  "file": "scorers/course/_x2.ts", "fileUrl": "https://github.com/…", "code": ["/**", " * X2 …"],
  "keys": [{ "key": "rule", "label": "The rule", "note": "A column fails when more than half its cells are empty." }],
  "marks": { "rule": [43] },
  "helpers": [{ "file": "_pages.ts", "note": "fetches each cited page", "code": ["…"] }],
  "dataset": { "blurb": "…", "stats": [{ "n": 30, "label": "sessions per run" }],
               "link": { "before": "Every row: ", "href": "…", "text": "the dataset page" } },
  "scorer": { "id": "x2", "threshold": 95, "code": "TC-8" },
  "resultsNote": "…", "runs": [{ "key": "w3-v1", "label": "v1", "rows": [] }],
  "seed": ["n11", "g3", "n06", "04", "n09"], "bridge": "…", "footLeft": "…", "footRight": "…"
}
```

- `code` is the file, one string per line, word for word. `keys` (up to three) name the parts that decide every call, and `marks` gives each key's line numbers, starting from 1.
- `seed` lists the five sessions shown first. "Draw five more" samples from the latest run.
- `prompt`, `prep`, `helpers`, `dataset` and `bridge` are optional.

### `judge.html`

```json
{
  "title": "Metric scope judge", "eyebrow": "…", "headline": "Metric scope", "stand": "…",
  "question": "Does every column use one metric, for the company or business unit named, over one kind of period?",
  "chips": ["TC-4", "Rubric v2 · O3", "Binary · pass or fail"],
  "prompt": { "text": "Use the eval-llm-judge skill to write a judge for TC-4…", "note": "…" }, "prep": "…",
  "parts": [{ "id": "context", "name": "Context", "why": "What the product is…", "text": "You are evaluating Mapper…" }],
  "examples": [{ "n": 1, "verdict": "PASS", "text": "Session: …" }],
  "weak": { "segments": [["You are an expert analyst.", 1], [" Rate the ", 0]], "flags": [["No product context", "…"]] },
  "rows": [], "verdicts": { "n01": { "score": 0, "critique": "The Revenue / Scale column mixes…" } },
  "verdictsHeading": "10 verdicts on v1.1", "file": "scorers/course/_o3.ts", "code": ["…"], "foot": "…"
}
```

- `parts` is the judge prompt cut into its parts, in order. A good judge has seven: context, one question, what counts as a pass, what counts as a fail, examples, reason then verdict, and only what it needs. Use the part id `examples` to show the `examples` as cards. Text wrapped in `**` shows in bold.
- `weak` is a bad judge for the same question. Its `segments` are pieces of text, each with a flag number (0 for no flag), and `flags` explains each numbered problem. Leave `weak` out to hide the toggle.
- `rows` are the sessions to call, and `verdicts` holds the judge's score and critique for each row id. The page counts how often the reader agrees with the judge.

The reader's calls on both scorer pages are saved in their own browser (under `storageKey`, if you set one). They're for discussion, not a labeling store. For labels that feed alignment, export from your trace review app, or ask your agent to add an export button.
