# AI Evals

A plugin of skills for building an eval loop for an AI product, from the rubric in your PRD to judges you can trust. It is the working repo for the [Reforge AI Evals course](https://www.reforge.com) taught by [Calibre Labs](https://blog.calibrelabs.ai), and it works for any agent or AI feature.

Your coding agent can do most of the eval process if it has the right instructions. Two steps stay with you: reading traces and calibrating judges. The skills here cover the rest.

We add skills as the course moves through its sessions, so this repo grows over the five weeks.

---

## The skills

| Step | Who does it | Skill | Added in | Status |
|---|---|---|---|---|
| Not sure where to start | Claude | [`eval-guide`](skills/eval-guide/SKILL.md) | Week 1 | Available |
| Write the eval rubric into the PRD, v1 before traces and v2 after | Claude drafts, you decide | [`eval-rubric`](skills/eval-rubric/SKILL.md) | Week 1 | Available |
| Build a diverse set of test inputs | Claude | [`uig`](skills/uig/SKILL.md) | Week 1 | Available |
| Read and annotate traces | **You** | | Week 1 | |
| Cluster your notes into trace codes | Claude | [`trace-codes`](skills/trace-codes/SKILL.md) | Week 1 | Available |
| Write code-based evals | Claude | [`eval-code`](skills/eval-code/SKILL.md) | Week 2 | Available |
| Write LLM judges | Claude | [`eval-llm-judge`](skills/eval-llm-judge/SKILL.md) | Week 2 | Available |
| Run the agent and the scorers over a dataset | Claude | `eval-run` | Week 2 | Coming |
| Label a sample pass or fail | **You** | | Week 3 | |
| Measure each judge against your labels and fix it | Claude | [`llm-align`](skills/llm-align/SKILL.md) | Week 3 | Available |
| Turn tickets and bad traces into dataset rows | Claude | [`ticket-to-eval`](skills/ticket-to-eval/SKILL.md) | Week 3 | Available |
| Check tool calls and multi-step traces | Claude | `eval-trace` | Week 4 | Coming |
| Score production on a schedule and report drift | Claude | `eval-monitor` | Week 4 | Coming |

Start with `eval-guide` if you are not sure which one you need. It looks at your situation and loads the right skill.

---

## Install

**Claude Code, as a plugin (recommended):**

```bash
claude plugin marketplace add Calibre-Labs/reforge-ai-evals
claude plugin install ai-evals@calibre-labs
```

Skills then run as `/ai-evals:eval-rubric`, `/ai-evals:trace-codes` and so on, or just describe what you need and the right skill loads.

**For one session, from a clone:**

```bash
git clone https://github.com/Calibre-Labs/reforge-ai-evals
claude --plugin-dir ./reforge-ai-evals
```

**Claude desktop app:** run `bash scripts/build-plugin.sh` and install `dist/ai-evals.plugin`.

**Codex:** a `.codex-plugin/` manifest and per-skill `agents/openai.yaml` files are included. We have not tested them yet.

**As plain slash commands (no plugin):** `bash install-skills.sh` copies each skill into `~/.claude/commands/`.

The skills read and write plain files (markdown, CSV, JSON, HTML). You do not need an account with any eval platform. `llm-align` and `ticket-to-eval` can also read from a platform such as Braintrust or LangSmith if your data lives there.

---

## Worked examples

### `rubric-templates/`

Worked examples of the AI PRD's rubric section. Corner and Ledger were built live during the Eval Rubrics webinar: a consumer shopping agent and an enterprise finance agent, each taken from v1 rubric through a real trace to v2. Support Triage is a lighter-weight sample PRD for a support-ticket classification agent, useful as a quick reference alongside the full worked examples.

Mapper is the course project for the fall 2026 cohort of AI Evals: a market research agent with five tools. Its session was recorded from a real run on Oct 2, 2026, and its trace page tags every step with a layer (context, retrieval, harness, systems). Its v2 rubric gets written in Week 1 of the course.

| File | Description |
|------|-------------|
| `ai-prd-template.md` | The generic AI PRD template, release-thresholds section included, that both worked examples start from |
| `corner/corner-prd-detailed.md` | Corner's full PRD: a local shopping assistant that buys everyday purchases by text |
| `corner/corner-prd.html` | Rendered HTML version of Corner's PRD |
| `corner/corner-rubric-v1.html` | Corner's v1 rubric, written from the PRD in under an hour, before a single trace |
| `corner/corner-rubric-v2.html` | Corner's v2 rubric, sharpened after reading traces from a real session |
| `corner/corner-simulation.html` | A simulated Corner session: a text order end to end |
| `corner/corner-trace.html` | The raw trace behind that simulation, annotated against the v1 rubric |
| `ledger/ledger-prd-detailed.md` | Ledger's full PRD: a finance agent that runs bonus calculations and reports for a CFO |
| `ledger/ledger-prd.html` | Rendered HTML version of Ledger's PRD |
| `ledger/ledger-rubric-v1.html` | Ledger's v1 rubric, written from the PRD before a single trace |
| `ledger/ledger-rubric-v2.html` | Ledger's v2 rubric, sharpened after reading traces from a real session |
| `ledger/ledger-simulation.html` | A simulated Ledger session: a bonus run end to end |
| `ledger/ledger-trace.html` | The raw trace behind that simulation, annotated against the v1 rubric |
| `mapper/mapper-prd-detailed.md` | Mapper's full PRD: a market research agent that returns a ranked, sourced market map |
| `mapper/mapper-prd.html` | Rendered HTML version of Mapper's PRD |
| `mapper/mapper-rubric-v1.html` | Mapper's v1 rubric: nine lines, written from the PRD before a single trace |
| `mapper/mapper-simulation.html` | A recorded Mapper session, click through what the user saw |
| `mapper/mapper-trace.html` | The trace behind that session, tagged by layer, with a reviewer view (press R) |
| `mapper/traces/index.html` | Nine more recorded Mapper sessions to read and annotate in Week 1. Each trace page has a notes box, and the index exports the notes as a CSV for `trace-codes` |
| `mapper/traces/sessions.json` | The same nine sessions as data |
| `support-triage/support-triage-prd.md` | Sample PRD for a support-ticket triage agent that categorizes tickets by intent, sentiment, and urgency |

Corner and Ledger sit on opposite ends of the same framework: a consumer product where asking the user is expensive and mistakes are small and recoverable, and an enterprise product where asking is free and a mistake compounds. See the [webinar recording and slides](https://luma.com/ayok3w9i) for the full walkthrough.

---


---

## Spring 2026 example: the single-prompt Market Map agent

The first cohort used a simple Market Map agent: one prompt, no tools, top three companies for a market category. Its prompt, datasets and evaluators are still here as a complete small example of an eval loop.

**Prompt:** [`prompts/market-map-prompt.md`](prompts/market-map-prompt.md)

### `datasets/`

These datasets are specific to the Market Map agent and serve as examples of how to build and expand an eval dataset.

| File | Rows | Description |
|------|------|-------------|
| `week1-dataset.csv` | 10 | Original dataset from Session 1. Includes an `expected` column with gold-standard reference responses for use with the reference judge. |
| `week2-dataset-30.csv` | 30 | Subset chosen for maximum diversity across all 4 UIG dimensions. Recommended starting point for Sessions 2–3. |
| `week3-dataset-60.csv` | 54 | Full expanded dataset with all query types and edge cases. Each row is tagged with metadata: `query_type`, `domain`, `style`, `temporal`, `edge_case`. |
| `week3-geography.csv` | 20 | Regional queries: SE Asia, India, Europe, Africa, China. Tests whether geographic constraints are applied correctly. |
| `week3-historical.csv` | 20 | Historical snapshot queries across domains. Tests whether the agent uses period-accurate data instead of defaulting to 2025. |
| `week3-impossible.csv` | 15 | Logically self-contradicting queries. Tests whether the agent refuses gracefully rather than confidently hallucinating. |
| `week3-jargon.csv` | 20 | VC/tech jargon queries (PLG, bootstrapped, ai-native, etc.). Tests whether jargon terms are applied as real filters. |
| `week3-metric-ranking.csv` | 20 | Queries requesting non-standard ranking criteria (NPS, uptime, GitHub stars). Tests whether the agent applies the requested metric or defaults to revenue. |
| `week3-currency.csv` | 20 | Dedicated currency mismatch dataset. All rows have `edge_case: true` and `failure_mode: currency_mismatch`. Covers 8 currencies (EUR, GBP, JPY, KRW, CHF, DKK, SEK, INR) across all 5 domains and 4 query types. Derived from support ticket TKT-007. |
| `week3-gap-analysis.md` | n/a | Gap analysis doc: which UIG dimensions are still under-covered and recommended queries to fill them. |
| `support-tickets.csv` | 10 | Synthetic customer support tickets with PII. Source material for the `ticket-to-eval` skill. |
| `regression-dataset.csv` | 10 | PII-stripped queries derived from real support tickets. Tagged with `failure_mode` and `source_ticket` in addition to standard UIG tags. |

All datasets are CSV files. The column layout matches Braintrust's import format, and any tool that reads CSV can use them.

**Metadata tags** (in the `metadata` column as JSON):

```json
{
  "query_type": "direct_category | competitive_comps | acquisition_targets | historical_snapshot | future_speculative | segment_specific | validation | trend_evolution | edge_out_of_scope",
  "domain": "tech_saas | healthcare | financial | consumer_brand | industrial_other",
  "style": "well_specified | under_specified | multi_constraint | jargon_heavy | edge_out_of_scope",
  "temporal": "current | historical | future",
  "edge_case": true | false
}
```

### `evaluators/`

| File | Description |
|------|-------------|
| `evaluators.py` | All evaluator functions, ready to run locally or wire into an eval platform as scorer functions |

**What's inside:**

*Code-based evaluators (deterministic, no LLM call):*
- `company_count`: checks that exactly 3 ranked companies appear in the output
- `has_sources`: checks that 3–4 source citations are present
- `has_metrics`: checks that each company has at least 2 supporting data points
- `has_category`: checks that a market category is identified before ranking

*LLM judge evaluators (semantic, calls Claude):*
- `ranking_quality_judge`: are the 3 companies the right ones in the right order?
- `edge_case_handling_judge`: for vague or out-of-scope queries, did the agent handle ambiguity gracefully rather than hallucinating confidently?
- `reference_judge`: compares the output to a gold-standard expected response (requires the `expected` column to be populated)

Each judge prompt includes 3 few-shot examples (clear PASS, clear FAIL, BORDERLINE) and returns structured JSON with a critique before the score.

### `mcp/`

`braintrust_write.py` is an optional MCP server that lets Claude write dataset rows into Braintrust. `names.json` holds the short aliases it uses. The spring sessions ran their experiments in Braintrust. Nothing in the skills requires it.

**Running the evaluators locally:**

```python
from evaluators import company_count, has_sources, ranking_quality_judge

output = "your model output here"
input_query = "team chat"

print(company_count(output, input_query))          # 0.0, 0.5, or 1.0
print(ranking_quality_judge(output, input_query))  # {"score": 1.0, "metadata": {...}}
```

The LLM judge evaluators need an [Anthropic API key](https://console.anthropic.com) and `pip install anthropic`.

---

## The User Input Grid

The **User Input Grid (UIG)** is the framework we use to ensure an eval dataset covers the real diversity of inputs an agent will face in production. It applies to any AI product. The Market Map UIG below is one example.

See [`skills/uig/SKILL.md`](skills/uig/SKILL.md) for the general methodology, or [`docs/uig-market-map.md`](docs/uig-market-map.md) for the Market Map-specific analysis.

**Market Map UIG, 4 dimensions:**

| Dimension | Values |
|-----------|--------|
| Query Type | Direct Category · Competitive Comps · Acquisition Targets · Historical Snapshot · Future/Speculative · Segment-Specific · Validation · Trend/Evolution |
| Market Domain | Tech/SaaS · Healthcare · Consumer/Brand · Financial · Industrial/Other |
| Query Style | Well-Specified · Under-Specified · Multi-Constraint · Jargon-Heavy · Edge/Out-of-Scope |
| Temporal Frame | Current · Historical · Future |

The Week 1 dataset (10 rows) had **zero coverage** of the Financial domain and Segment-Specific query type. The Week 2 dataset was designed to fill those gaps deliberately.

---

## Key ideas from the course

**On evaluator design:**
- Code-based evaluators check *structure*. LLM judges check *semantics*. Use both.
- Write one criterion per judge. Compound judges are uninterpretable when they fail.
- The borderline few-shot example is more valuable than the pass example because it calibrates the gray zone.
- Validate judges with TPR/TNR against human labels before trusting them in production.

**On dataset design:**
- Most eval datasets are built from engineer intuition (overfits to what engineers know) or real user logs (overfits to easy common cases). A UIG forces deliberate coverage.
- 30–80 queries hitting each dimension value 3+ times outperforms 500 random queries.
- Tag every row with its dimension values. You need to slice by dimension to diagnose failures.

**On the eval loop:**
- Evals are only useful if they run on every prompt change. Wire them into your workflow, not just ad-hoc.
- A score going up is only meaningful if you know *what changed* and *which eval category improved*.

**On judge calibration (TPR/TNR):**
- Before trusting an LLM judge in production, validate it against human labels using TPR (does it catch true positives?) and TNR (does it reject true negatives?).
- False negatives (judge too strict) and false positives (judge too lenient) have different root causes and need different fixes. Investigate the scorer's reasoning for each disagreement before changing the prompt.
- Use the `llm-align` skill to automate this workflow for any set of judge scores and human labels.
