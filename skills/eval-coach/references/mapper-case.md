# Mapper: the course's worked example

Mapper (mapper.calibrelabs.ai) is a single-agent market research product: you name a technology
category and it returns a ranked market map with sources. Every week of the course used it. Use
these facts when a learner wants a concrete example. The repo has the real files:
`templates/mapper/` (PRD, rubric v1, a recorded session, ten annotatable traces) and
`docs/uig-market-map.md` (the full user input grid).

## The parts (Week 1)

| Part | Mapper |
|---|---|
| Goal | Map one tech category |
| Context | The system prompt, the chat so far and the user's saved preferences |
| Retrieval | `web_search` and `read_page` bring in snippets and page text |
| Harness | One agent, no helpers. Loop v1 asks one scoping question before any search |
| Systems | Gemini models, five tools (`get_preferences`, `web_search`, `read_page`, `build_market_map`, `publish_share_link`), stored preferences, logs |

Steps in v1.5: check scope (turn 1, no tools) → research (one search pass; links resolved and
numbered) → pick the output (rules in code pick one of five: map, matrix, timeline, SWOT, news) →
build it → refine (user asks for changes; a new version is saved). After the session goes idle for
five minutes, the scorers run and scores go to Amplitude (one event per session) and Braintrust
(on the trace).

## Rubric v1 (Week 2): nine lines

| Line | Says |
|---|---|
| O1 | Every figure names its time period. |
| O2 | Every figure has a source that supports it. |
| T1 | Confirms scope, then delivers what was confirmed. |
| T2 | Searches before stating a figure that's new to the session. |
| G1 | Marks estimates. Never shows one as a reported figure. |
| G2 | Cites only sources it retrieved. No invented links. |
| G3 | Declines investment advice and requests outside tech. |
| X1 | Leads with the output. Two sentences around it, at most. |
| X2 | Says how it read the request. Names figures it couldn't find. |

## Trace codes (Week 2) and what happened to each (Weeks 3 to 5)

From notes on ten traces. Counts are out of the reviewed traces, not live traffic.

| Code | Pattern | Count | Rubric | Decision |
|---|---|---|---|---|
| TC-1 | Cites links that don't open | 10 of 10 | G2 | Harness fix (missing capability): the writing step never saw the real links. Code check keeps it fixed |
| TC-2 | Figures with no source behind them | 5 of 10 | O2 | LLM judge: read the source against the claim |
| TC-3 | Drops part of what was agreed | 5 of 10 | T1 | LLM judge: compare the promise to the build |
| TC-4 | Mixes metrics in one column | 5 of 10 | O3 (new in v2) | LLM judge (metric scope), aligned in Week 4 |
| TC-5 | Asks the wrong scoping question | 5 of 10 | T1 | Harness change: loop v2 asks only when unclear |
| TC-6 | Picks companies that don't fit | 4 of 10 | none | Not checked yet; read in monitoring |
| TC-7 | Uses stale figures as current | 3 of 10 | none | Not checked yet; read in monitoring |
| TC-8 | Half-empty columns | 3 of 10 | X2 | Code check: count the empty cells |
| TC-9 | Mishandles past or future years | 2 of 10 | T3 (new in v2) | Prompt fix (spec gap): never told other years count |
| TC-10 | Writes an essay instead of a map | 2 of 10 | X1 | Code check possible (is there an output card); didn't recur |
| TC-11 | Gives investment advice | 1 of 10 | G3 | Prompt fix (spec gap): never told it was off limits |

Example of a well-formed code, TC-4: *Yes if one column mixes different measures or periods, or
doesn't say which it shows.* Evidence: NVIDIA's fiscal year next to others' single quarters; Teams
users from Q1 2024 next to Discord and Slack in 2026; one "Valuation/Rev" column, unclear which.

## Rubric v2: eleven lines

New: **O3** each column uses one metric, for the company or business unit named, over one kind of
period (from TC-4). **T3** answers for the year the user named, past or future, and marks
projections (from TC-9). Sharpened: **T1** asks a scoping question only when the request is
ambiguous, then delivers what was confirmed (TC-5); **G3** declines buy, sell or hold calls; past
and future tech markets are in scope (TC-11); **X2** names figures it couldn't find and shows no
column that's mostly empty (TC-8).

## Fixes and their effect (Week 3, 30 recorded sessions per version)

- TC-11, prompt line added ("Don't give investment advice: no buy, sell or hold calls ... offer a
  market map instead"): declined 1 of 5 → 5 of 5.
- TC-9, prompt line added (past and future markets are in scope; keep the year the user named):
  2 of 4 → 4 of 4.
- TC-1, harness change: redirect links resolved to real pages, given to the writing step as a
  numbered list, anything not on the list dropped: 28 dead links → 0; links that open 3 of 30 → 30
  of 30. No prompt change.

The two written live: TC-8 half-empty columns as a code check (fail if any column is more than half
empty; "empty" means blank, N/A, "Not disclosed", "Unknown" or a dash) and TC-4 metric scope as an
LLM judge (example fail: Oracle Health shown with all of Oracle's $67.4B revenue).

Scores on v1.1: metric scope 33 to 37% (bar 90%, misses), half-empty 83% (bar 95%, misses), source
behind each figure 50%, delivers what was agreed 53%. Release thresholds from the PRD: under $0.10
per session, median time to first map under 30s, zero sessions failing any governance line.

## Judge alignment (Week 4)

Metric-scope judge against human labels: v1 TPR 69%, TNR 81% → v3 TPR 91%, TNR 93%. Changes:
clearer rules and new examples (ranking column first; fiscal years, gaps and labeled columns
pass), checks as ordered steps that stop at the first fail, and a stronger model (Flash instead of
Flash-Lite). With the aligned judge, v1.1 scored 40%.

## Versions

| Version | What changed | Codes | Effect |
|---|---|---|---|
| v1 | As recorded Oct 2 | | Weeks 1 and 2 |
| v1.1 | Links resolved and checked; past and future years; investment advice declined | TC-1, 9, 11 | G2 links 10% → 100%, T3 93% → 100%, G3 87% → 100% |
| v1.5 | One metric per column, for the right company or unit, over one kind of period (prompt) | TC-4 | O3 40% → 47%; X2 83% → 97%; O2 51% → 27% (not aligned, worth reading) |
| v2 | New loop: asks only when unclear; the model picks the output; research is a tool | TC-5 | Scoping question asked 30 of 30 → 4 of 30; T1 60% → 97% (new judge, not yet aligned); O2 27% → 40%; O3 47% → ~67% |

The catch the course called out: a score from an unaligned judge (T1's new judge in v2) isn't
believable until you align it.

## Agent success rate

Mapper has no single success event, so the course built one: a session succeeds when every
must-pass line passes (O2, O3, G2, G3), with user evidence (shared or published the map, kept
refining, came back) counted where it exists, and cost and latency kept as separate guardrails.
