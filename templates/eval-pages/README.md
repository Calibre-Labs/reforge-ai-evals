# Eval page templates

Two one-file HTML pages for showing eval results to the people who decide on them:

- a **results page**, with every scorer run by run
- a **scorer page**, with one code check or LLM judge word for word, its results, and the sessions it scored

Both pages are built from your own scored runs. On the scorer page, reviewers agree or disagree with each call, and each call is saved as their own pass or fail label, ready for [`llm-align`](../../skills/llm-align/SKILL.md).

Each template is static HTML with one slot for your data. Your coding agent writes the data as JSON, and `build_page.py` fills it in. There's no server and no build step, and the page loads nothing from outside except Google Fonts.

```bash
python3 build_page.py results examples/mapper-results.json --out results.html
python3 build_page.py scorer examples/mapper-x2-check.json --out x2.html
python3 build_page.py scorer examples/mapper-o3-judge.json --out o3.html
```

| Template | Shows | Examples (Mapper, fall 2026 Week 3) |
|---|---|---|
| [`results.html`](results.html) | <ul><li>Each scorer's pass rate per run, against its release threshold</li><li>Two groups: fixes to keep fixed, and codes still to hill-climb</li><li>Which sessions changed with each fix</li><li>Every session as a row of pass or fail dots, which opens to what the user saw</li></ul> | [page](examples/mapper-results.html) · [data](examples/mapper-results.json) |
| [`scorer.html`](scorer.html) | One layout for code checks and LLM judges: <ul><li>Pass rates per run, with the failing sessions</li><li>The scorer word for word, with its parts marked: a code check's file, or a judge's prompt</li><li>Every session from the latest run, with the scorer's call and reason, to label with Agree or Disagree</li></ul> | Code check: [page](examples/mapper-x2-check.html) · [data](examples/mapper-x2-check.json)<br>Judge: [page](examples/mapper-o3-judge.html) · [data](examples/mapper-o3-judge.json) |

The examples come from Mapper, the course's market research agent:

- **Results page:** a 10-row sample of Mapper's 30-row Mapper Dev Dataset, scored on v1 and v1.1.
- **Code check example:** the half-empty columns check (TC-8, rubric line X2).
- **Judge example:** the metric scope judge (TC-4, rubric line O3).

Once you have scored runs, point your agent here, for example: "Build the results page from templates/eval-pages for runs A and B, and a scorer page for my metric scope judge." The [`eval-code`](../../skills/eval-code/SKILL.md) and [`eval-llm-judge`](../../skills/eval-llm-judge/SKILL.md) skills write the scorers, and these pages show them.

## The data

Every field is plain JSON. If you leave out an optional field, the page drops that part.

### A row

A row is one session in one run, as the user saw it.

```json
{
  "id": "n05", "group": "metric scope", "expected": "answer", "input": "streaming services by subscribers",
  "scores": { "x2": { "score": 0, "reason": "Half-empty column(s): \"Content Budget\" (5 of 6 empty)." } },
  "cards": [{ "tool": "generate_market_map", "title": "Global Video Streaming Services",
              "cols": ["Subscribers", "Content Budget"], "rows": [["Netflix", "~325M (2025/2026)", "~$18B (2026 est.)"]],
              "body": null,
              "flags": [{ "scorer": "x2", "cols": [1], "cells": [[1, 1]], "note": "half empty", "colNotes": { "1": "5 of 6 empty" } }] }],
  "said": [{ "user": "streaming services by subscribers", "text": "I'll map the top streaming services by subscribers. Sound good?" }]
}
```

- **`cards`** hold the output, as either a table or a `body` of text. In a table, `cols` lists the columns, and each entry in `rows` starts with the row's name. Flatten whatever your product returns into this shape.
- **`flags`** (optional) mark what a scorer counted against a card:
  - `cols`: whole columns, by index
  - `cells`: single cells, as `[row, column]`
  - `colNotes`: a note per column

  The pages highlight flags on rows that scorer failed.
- **`said`** is the conversation: what the user typed each turn, and the agent's text.
- **`scores`** has one entry per scorer id, each with a `score` (1 or 0) and a one-sentence `reason`. On the scorer page, a row has its one scorer's `score` and `reason` at the top level instead.

### `results.html`

```json
{
  "title": "Mapper scorer runs", "eyebrow": "Mapper · course scorers", "headline": "How each version scores, run by run",
  "standfirst": "Every scorer on the 30-row Mapper Dev Dataset…", "foot": "…",
  "runs": [{ "key": "w3-v1", "label": "v1", "note": "Week3 v1 production baseline", "scored_at": "2026-11-04T06:11:36Z", "rows": [] }],
  "scorers": [{ "id": "g2", "rubric": "G2", "code": "TC-1", "name": "Links retrieved, and they open", "kind": "Code",
                "group": "fixed", "threshold": 100, "fix": "Harness: resolve redirects, cite from a numbered list" },
              { "id": "o3", "rubric": "O3", "code": "TC-4", "name": "Metric scope", "kind": "Judge",
                "group": "climb", "threshold": 90, "live": true, "target": true }],
  "next": { "label": "v1.5", "when": "Nov 11", "what": "One fix each for O3, X2, O2 and T1" }
}
```

- **`runs`** go in order. The first run is the "before" for the `fixed` group. The `climb` group shows every run after the first.
- **`group`** is `fixed` for a scorer that keeps a shipped fix fixed, or `climb` for a code still to move.
- **`kind`** is `Code` or `Judge`.
- **`threshold`** is the release bar as a pass-rate percent. Use `null` if none is set yet.
- **`live: true`** labels a scorer that has no scores yet as "written live".
- **`target: true`** marks a scorer the `next` version is meant to fix. It's listed even before it has scores.
- **`next`** is optional.

### `scorer.html`

```json
{
  "title": "X2 Half-Empty Columns Check", "eyebrow": "Mapper · course scorer · still to hill-climb",
  "headline": "TC-8, half-empty columns", "lede": "X2: … A code check: it reads each market map's cells, with no model…",
  "chips": ["TC-8", "Rubric line X2", "Code check · no model", "Pass or fail", "Threshold 95%"],
  "scorer": { "id": "x2", "threshold": 95, "code": "TC-8" },
  "resultsNote": "5 of 30 sessions fail on v1.1. The release threshold is 95%.",
  "runs": [{ "key": "w3-v1.1", "label": "v1.1", "rows": [] }],
  "doc": { "heading": "The check", "lang": "code", "lines": ["/**", " * X2 …"], "source": "scorers/course/x2.ts, 56 lines",
           "parts": [{ "id": "empty", "label": "What counts as empty", "note": "A cell is empty if it is any of these:",
                       "bullets": ["Blank, or a dash", "Starts with N/A or Not disclosed"], "lines": [18, 19] }] },
  "files": [{ "file": "_pages.ts", "note": "fetches each cited page", "lines": ["…"] }],
  "sessions": ["04", "g3", "n06", "n11", "n18", "01", "…"], "sessionsHeading": "All 30 sessions on v1.1", "sessionsNote": "Failures first.", "reasonLabel": "Check Reasoning",
  "footLeft": "…", "footRight": "…"
}
```

- **`doc`** is the scorer itself, word for word, one string per line.
  - For a code check, set `lang` to `"code"` and use the file's lines.
  - For an LLM judge, set `lang` to `"prompt"` and use the prompt's lines.
- **`parts`** name the pieces of the doc, in order, with the line numbers each one covers, starting from 1.
  - A code check usually has three parts: what it reads, what it counts, and the rule.
  - A judge prompt has seven: context, one question, what passes, what fails, examples, critique then verdict, and input.
- **`files`** (optional) are extra files shown collapsed under the doc, such as the judge's whole file or a helper it imports.
- **`parts`** can include `bullets`, a list shown under the part's note.
- **`sessions`** are the row ids to show from the latest run, in order, usually all of them with failures first. Each one is a collapsible row, with its `reason` under a collapsible `reasonLabel` ("Judge Reasoning", say) and the conversation under "Session Input". The summary above the rows counts pass and fail, and how many the reader has reviewed, agreed and disagreed with, split by the scorer's fails and passes.

### Labels on the scorer page

Each session row has Agree and Disagree buttons. A call is saved as the reviewer's own label, `PASS` or `FAIL`, so it keeps its meaning after you change the scorer and rescore: Agree and Disagree are worked out again against the new call. A label can carry a short "why" note, which is what `llm-align` reads to group disagreements. Filters show all sessions, the ones nobody has labeled yet, or the disagreements.

Where the labels are kept depends on where the page runs:

- **Published as a Claude artifact with the `db` and `user` capabilities** (`{"db": {}, "user": {"scopes": ["profile"]}}`): labels are shared, one per session, and show who made each call, so two people can split the sessions. Reviewers need Contributor access or above to label. Your agent reads them back from the artifact's `labels` collection.
- **Anywhere else** (a local file, a static host): labels stay in the reviewer's browser, under `storageKey` if you set one. If that page is later published with the shared store, a button copies those labels into it.

Each shared label is one document, with id `<scorer id>.<session id>`:

```json
{ "scorer": "o3", "session": "n05", "human": "FAIL", "judge": "PASS", "run": "v1.1",
  "by": "u_…", "at": "2026-11-05T01:23:23Z", "note": "Revenue column mixes FY24 and Q3" }
```

`judge` is the scorer's call when the label was made. Compare `human` with the latest scores, not with `judge`, to measure the scorer you have now.
