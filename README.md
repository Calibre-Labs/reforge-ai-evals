# Reforge AI Evaluation Course — Market Map Agent

This repository contains everything built during the live demo sessions of the [Reforge AI Evaluation course](https://www.reforge.com). We use a **Market Map agent** as a shared project across all four sessions — a single-turn AI that takes a market research query and returns a ranked list of the top 3 players in that market, with supporting metrics and citations.

The goal is to go from "I have a prompt that works" to "I have a repeatable, measurable eval loop" — and eventually to online monitoring of the agent in production.

---

## The Agent

The Market Map agent takes queries like:

- *"team chat"* → ranks Microsoft Teams, Slack, Google Chat
- *"what AI security startups could Okta acquire in 2026 with its cash?"* → scoped acquisition target analysis
- *"search in 2003"* → period-accurate historical market map

It is a single-turn prompt with no tools or retrieval — all knowledge is in the model's weights, which makes it a great target for evals: the failure modes are predictable and the output format is fixed.

**Prompt:** [`prompts/market-map-prompt.md`](prompts/market-map-prompt.md)

---

## What's in This Repo

### `prompts/`

| File | Description |
|------|-------------|
| `market-map-prompt.md` | System prompt v2 — includes 3 few-shot examples covering a standard query, a historical query, and an under-specified query |

### `datasets/`

| File | Rows | Description |
|------|------|-------------|
| `week1-dataset.csv` | 10 | Original dataset from Session 1. Now includes an `expected` column with gold-standard reference responses for use with the reference judge. |
| `week2-dataset-curated-30.csv` | 30 | Curated subset chosen for maximum diversity across all 4 UIG dimensions. Recommended starting point for Sessions 2–3. |
| `week2-dataset.csv` | 53 | Full expanded dataset with all query types and edge cases. Each row is tagged with metadata: `query_type`, `domain`, `style`, `temporal`, `edge_case`. |

All datasets are in [Braintrust](https://braintrust.dev) CSV format and can be imported directly.

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
| `evaluators.py` | All evaluator functions, ready to wire into Braintrust as scorer functions |

**What's inside:**

*Code-based evaluators (deterministic, no LLM call):*
- `company_count` — checks that exactly 3 ranked companies appear in the output
- `has_sources` — checks that 3–4 source citations are present
- `has_metrics` — checks that each company has at least 2 supporting data points
- `has_category` — checks that a market category is identified before ranking

*LLM judge evaluators (semantic, calls Claude):*
- `ranking_quality_judge` — are the 3 companies the right ones in the right order?
- `edge_case_handling_judge` — for vague or out-of-scope queries, did the agent handle ambiguity gracefully rather than hallucinating confidently?
- `reference_judge` — compares the output to a gold-standard expected response (requires the `expected` column to be populated)

Each judge prompt includes 3 few-shot examples (clear PASS, clear FAIL, BORDERLINE) and returns structured JSON with a critique before the score.

### `skills/`

Reference documents and reusable frameworks — not course exercises, but the methodology behind the work.

| File | Description |
|------|-------------|
| `uig-market-map.md` | The User Input Grid for this specific agent: 4 dimensions, coverage audit of Week 1 dataset, gap analysis, and recommended queries to fill each gap |
| `uig-skill.md` | How to build a UIG for any AI product — the general methodology |
| `eval-code-skill.md` | How to write code-based evaluators: when to use them, how to find their failure modes, common patterns |
| `eval-llm-judge-skill.md` | How to write LLM judge evaluators: the 4 required components, how to write few-shot examples, how to validate with TPR/TNR |

---

## Session Overview

| Session | Topic | Key Files |
|---------|-------|-----------|
| 1 | Traces in Braintrust playground | `week1-dataset.csv`, `market-map-prompt.md` |
| 2 | Code-based and LLM judge evaluators | `evaluators.py`, `week2-dataset-curated-30.csv` |
| 3 | Dataset management and prompt iteration | `week2-dataset.csv`, `uig-market-map.md` |
| 4 | Online monitoring and custom trace analysis viewer | TBD |

---

## Getting Started

**Prerequisites:**
- A [Braintrust](https://braintrust.dev) account
- An [Anthropic API key](https://console.anthropic.com) (for the LLM judge evaluators)
- Python 3.10+ with `anthropic` installed: `pip install anthropic`

**Session 2 setup:**

1. Import `week2-dataset-curated-30.csv` into Braintrust as a new dataset
2. Copy `market-map-prompt.md` into the Braintrust playground as your system prompt
3. Run an experiment against the dataset
4. Add `evaluators.py` as scorer functions in your experiment config

**Running evaluators locally:**

```python
from evaluators import company_count, has_sources, ranking_quality_judge

output = "your model output here"
input_query = "team chat"

print(company_count(output, input_query))       # 0.0, 0.5, or 1.0
print(ranking_quality_judge(output, input_query))  # {"score": 1.0, "metadata": {...}}
```

---

## The User Input Grid

The **User Input Grid (UIG)** is the framework we use to ensure our eval dataset covers the real diversity of queries the agent will face in production. See [`skills/uig-market-map.md`](skills/uig-market-map.md) for the full analysis.

**4 dimensions, 5 values each on average:**

| Dimension | Values |
|-----------|--------|
| Query Type | Direct Category · Competitive Comps · Acquisition Targets · Historical Snapshot · Future/Speculative · Segment-Specific · Validation · Trend/Evolution |
| Market Domain | Tech/SaaS · Healthcare · Consumer/Brand · Financial · Industrial/Other |
| Query Style | Well-Specified · Under-Specified · Multi-Constraint · Jargon-Heavy · Edge/Out-of-Scope |
| Temporal Frame | Current · Historical · Future |

The Week 1 dataset (10 rows) had **zero coverage** of the Financial domain and Segment-Specific query type. The Week 2 dataset was designed to fill those gaps deliberately.

---

## Key Ideas from the Course

**On evaluator design:**
- Code-based evaluators check *structure*. LLM judges check *semantics*. Use both.
- Write one criterion per judge. Compound judges are uninterpretable when they fail.
- The borderline few-shot example is more valuable than the pass example — it calibrates the gray zone.
- Validate judges with TPR/TNR against human labels before trusting them in production.

**On dataset design:**
- Most eval datasets are built from engineer intuition (overfits to what engineers know) or real user logs (overfits to easy common cases). A UIG forces deliberate coverage.
- 30–80 queries hitting each dimension value 3+ times outperforms 500 random queries.
- Tag every row with its dimension values. You need to slice by dimension to diagnose failures.

**On the eval loop:**
- Evals are only useful if they run on every prompt change. Wire them into your workflow, not just ad-hoc.
- A score going up is only meaningful if you know *what changed* and *which eval category improved*.
