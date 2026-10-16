# AI Evals Toolkit: LLM judges, eval datasets and rubrics

**An open-source, practical toolkit for evaluating AI agents and LLM features.** It covers LLM-as-a-judge prompt templates, code-based evaluators, a method for designing eval datasets (the User Input Grid), AI PRD and eval rubric templates, judge alignment (TPR/TNR) and Claude Code skills that automate each step.

It was built live for the [Reforge AI Evals course](https://www.reforge.com/courses/ai-evals), taught by Sandhya Hegde and Justin Bauer of [Calibre](https://calibrelabs.ai). The methods apply to any AI product, from a single-turn prompt to a multi-step agent. Market Map, the example agent used throughout, is only the demo.

**Who it's for:** product managers, AI engineers and founders who want to go from "I have a prompt that works" to "I have an eval loop I trust", and then to monitoring the agent in production.

---

## Contents

- [Quick start](#quick-start)
- [What's in this repo](#whats-in-this-repo)
- [The User Input Grid (UIG)](#the-user-input-grid-uig)
- [Key ideas](#key-ideas)
- [FAQ](#faq)
- [The example agent: Market Map](#the-example-agent-market-map)
- [Course sessions](#course-sessions)
- [About](#about)
- [License](#license)

---

## Quick start

**Prerequisites:** a [Braintrust](https://braintrust.dev) account, an [Anthropic API key](https://console.anthropic.com) for the LLM judges, and Python 3.10+.

```bash
git clone https://github.com/Calibre-Labs/reforge-ai-evals.git
cd reforge-ai-evals
pip install anthropic
bash install-skills.sh   # installs /uig, /eval-code, /eval-llm-judge, /llm-align, /ticket-to-eval
```

Then open Claude Code in your own project and run `/uig` to design an eval dataset, or `/eval-llm-judge` to write your first judge.

**Run the evaluators locally:**

```python
from evaluators import company_count, has_sources, ranking_quality_judge

output = "your model output here"
input_query = "team chat"

print(company_count(output, input_query))          # 0.0, 0.5, or 1.0
print(ranking_quality_judge(output, input_query))  # {"score": 1.0, "metadata": {...}}
```

**Run the Market Map demo in Braintrust:**

1. Import `datasets/week2-dataset-30.csv` into Braintrust as a new dataset
2. Paste `prompts/market-map-prompt.md` into the Braintrust playground as the system prompt
3. Run an experiment against the dataset
4. Add the scorers in `evaluators/` to the experiment

**Optional: braintrust-write MCP server.** This lets Claude insert dataset rows directly into Braintrust (`/ticket-to-eval` uses it). Run `pip install -r mcp/requirements.txt`; `install-skills.sh` prints the config snippet to add to `~/.claude/settings.json`.

---

## What's in this repo

| Folder | What it gives you | Reusable for any AI product? |
|--------|-------------------|------------------------------|
| [`skills/`](skills/) | Claude Code skills for building a UIG, writing code evaluators, writing LLM judges, aligning judges with human labels, and turning support tickets into eval rows | Yes |
| [`rubric-templates/`](rubric-templates/) | AI PRD template plus two fully worked eval rubrics (consumer and enterprise agents), each taken from v1 through a real trace to v2 | Yes |
| [`evaluators/`](evaluators/) | 4 code-based evaluators and 7 LLM-as-a-judge evaluators, ready for Braintrust | Patterns yes, criteria are Market Map–specific |
| [`datasets/`](datasets/) | Tagged eval datasets (10 to 54 rows) plus targeted edge-case sets for geography, history, jargon, currency and impossible queries | Example only |
| [`prompts/`](prompts/) | The Market Map system prompt (v2, with 3 few-shot examples) | Example only |
| [`docs/`](docs/) | A complete worked User Input Grid for the Market Map agent | Example only |
| [`mcp/`](mcp/) | A small MCP server for writing rows to Braintrust datasets | Yes |

### `skills/`: Claude Code skills for AI evals

Install them with `bash install-skills.sh`, which copies each one to `~/.claude/commands/`.

| Skill | Command | What it does |
|-------|---------|--------------|
| [`uig-skill.md`](skills/uig-skill.md) | `/uig` | Builds a User Input Grid for any AI product, audits your eval dataset's coverage against it, and proposes queries to fill the gaps |
| [`eval-code-skill.md`](skills/eval-code-skill.md) | `/eval-code` | Writes deterministic, code-based evaluators: when to use them, their failure modes, common patterns |
| [`eval-llm-judge-skill.md`](skills/eval-llm-judge-skill.md) | `/eval-llm-judge` | Writes LLM-as-a-judge prompts: one criterion, binary PASS/FAIL, 3 few-shot examples, structured output, TPR/TNR validation |
| [`llm-align-skill.md`](skills/llm-align-skill.md) | `/llm-align` | Measures how well an LLM judge agrees with human labels (TPR/TNR), investigates disagreements, and suggests fixes to the judge prompt |
| [`ticket-to-eval-skill.md`](skills/ticket-to-eval-skill.md) | `/ticket-to-eval` | Turns a support ticket or production trace into eval rows: strips PII, classifies the failure mode, maps it to the UIG, and appends it to your regression dataset |

### `rubric-templates/`: AI PRD and eval rubric examples

Corner and Ledger were built live during the [Eval Rubrics that Drive AI Product Strategy](https://luma.com/ayok3w9i) webinar. They sit at opposite ends of the same framework. Corner is a consumer product where asking the user is expensive and mistakes are small and recoverable. Ledger is an enterprise product where asking is free and a mistake compounds.

| File | Description |
|------|-------------|
| [`ai-prd-template.md`](rubric-templates/ai-prd-template.md) | Generic AI PRD template with autonomy, eval rubric and release-threshold sections |
| [`corner/corner-prd-detailed.md`](rubric-templates/corner/corner-prd-detailed.md) | Full PRD for Corner, a local shopping assistant that buys everyday purchases by text ([HTML](rubric-templates/corner/corner-prd.html)) |
| [`corner/corner-rubric-v1.html`](rubric-templates/corner/corner-rubric-v1.html) | Corner's v1 rubric, written from the PRD in under an hour, before reading a single trace |
| [`corner/corner-rubric-v2.html`](rubric-templates/corner/corner-rubric-v2.html) | Corner's v2 rubric, sharpened after reading traces from a real session |
| [`corner/corner-simulation.html`](rubric-templates/corner/corner-simulation.html) | A simulated Corner session: a text order end to end |
| [`corner/corner-trace.html`](rubric-templates/corner/corner-trace.html) | The raw trace behind that simulation, annotated against the v1 rubric |
| [`ledger/ledger-prd-detailed.md`](rubric-templates/ledger/ledger-prd-detailed.md) | Full PRD for Ledger, a finance agent that runs bonus calculations and reports for a CFO ([HTML](rubric-templates/ledger/ledger-prd.html)) |
| [`ledger/ledger-rubric-v1.html`](rubric-templates/ledger/ledger-rubric-v1.html) | Ledger's v1 rubric, written from the PRD before reading a single trace |
| [`ledger/ledger-rubric-v2.html`](rubric-templates/ledger/ledger-rubric-v2.html) | Ledger's v2 rubric, sharpened after reading traces from a real session |
| [`ledger/ledger-simulation.html`](rubric-templates/ledger/ledger-simulation.html) | A simulated Ledger session: a bonus run end to end |
| [`ledger/ledger-trace.html`](rubric-templates/ledger/ledger-trace.html) | The raw trace behind that simulation, annotated against the v1 rubric |
| [`support-triage/support-triage-prd.md`](rubric-templates/support-triage/support-triage-prd.md) | A lighter sample PRD for a support-ticket triage agent that categorizes tickets by intent, sentiment and urgency |

### `evaluators/`: code-based evaluators and LLM judges

[`evaluators.py`](evaluators/evaluators.py) contains every evaluator as a plain Python function, for local runs or as Braintrust scorer functions. The other files contain one evaluator each, written as a Braintrust custom scorer (`handler` function).

*Code-based evaluators (deterministic, no LLM call):*

| Evaluator | File | Checks |
|-----------|------|--------|
| `company_count` | [`code-company-count.py`](evaluators/code-company-count.py) | Exactly 3 ranked companies appear in the output |
| `has_sources` | [`code-has-sources.py`](evaluators/code-has-sources.py) | 3–4 source citations are present |
| `has_metrics` | [`code-has-metrics.py`](evaluators/code-has-metrics.py) | Each company has at least 2 supporting data points |
| `has_category` | [`code-has-category.py`](evaluators/code-has-category.py) | A market category is identified before the ranking |

*LLM-as-a-judge evaluators (semantic):*

| Evaluator | File | Checks |
|-----------|------|--------|
| `ranking_quality_judge` | [`llm-judge-ranking-quality.py`](evaluators/llm-judge-ranking-quality.py) | The 3 companies are the right ones, in the right order |
| `edge_case_handling_judge` | [`llm-judge-edge-case-handling.py`](evaluators/llm-judge-edge-case-handling.py) | Vague or out-of-scope queries are handled gracefully instead of answered with confident hallucination |
| `reference_judge` | [`llm-judge-reference.py`](evaluators/llm-judge-reference.py) | The output matches a gold-standard reference answer (needs the `expected` column) |
| `company_match_judge` | [`llm-judge-company-match.py`](evaluators/llm-judge-company-match.py) | The top 3 companies match the reference, in the same order (company and rank only) |
| `metric_coverage_judge` | [`llm-judge-metric-coverage.py`](evaluators/llm-judge-metric-coverage.py) | At least 2 of the 3 companies have 2+ quantitative metrics each |
| `metric_scope_judge` | [`llm-judge-metric-scope.py`](evaluators/llm-judge-metric-scope.py) | Metrics are scoped to the relevant product, not the parent company (for example, not Microsoft's total revenue for a Teams query) |

Each judge prompt has 3 few-shot examples (a clear PASS, a clear FAIL and a BORDERLINE case) and returns structured JSON with a critique before the score.

### `datasets/`: example eval datasets

All datasets are Braintrust-format CSVs and can be imported directly.

| File | Rows | Description |
|------|------|-------------|
| `week1-dataset.csv` | 10 | The original Session 1 dataset. Includes an `expected` column with gold-standard reference responses for the reference judge. |
| `week2-dataset-30.csv` | 30 | A subset chosen for maximum diversity across all 4 UIG dimensions. The recommended starting point. |
| `week3-dataset-60.csv` | 54 | The full expanded dataset with every query type and edge case, each row tagged with UIG metadata. |
| `week3-geography.csv` | 20 | Regional queries (SE Asia, India, Europe, Africa, China). Tests whether geographic constraints are applied. |
| `week3-historical.csv` | 20 | Historical snapshot queries. Tests whether the agent uses period-accurate data instead of defaulting to the present. |
| `week3-impossible.csv` | 15 | Self-contradicting queries. Tests whether the agent refuses gracefully instead of hallucinating confidently. |
| `week3-jargon.csv` | 20 | VC and tech jargon (PLG, bootstrapped, AI-native). Tests whether jargon is applied as a real filter. |
| `week3-metric-ranking.csv` | 20 | Non-standard ranking criteria (NPS, uptime, GitHub stars). Tests whether the requested metric is used instead of revenue. |
| `week3-currency.csv` | 20 | Currency mismatch cases across 8 currencies (EUR, GBP, JPY, KRW, CHF, DKK, SEK, INR), all 5 domains and 4 query types. Derived from support ticket TKT-007. |
| `week3-gap-analysis.md` | — | Which UIG dimensions are still under-covered, with recommended queries to fill them. |
| `support-tickets.csv` | 10 | Synthetic customer support tickets containing PII. Source material for `/ticket-to-eval`. |
| `regression-dataset.csv` | 10 | PII-stripped regression queries derived from the support tickets, tagged with `failure_mode` and `source_ticket`. |

**Metadata tags** (JSON in the `metadata` column):

```json
{
  "query_type": "direct_category | competitive_comps | acquisition_targets | historical_snapshot | future_speculative | segment_specific | validation | trend_evolution | edge_out_of_scope",
  "domain": "tech_saas | healthcare | financial | consumer_brand | industrial_other",
  "style": "well_specified | under_specified | multi_constraint | jargon_heavy | edge_out_of_scope",
  "temporal": "current | historical | future",
  "edge_case": true | false
}
```

---

## The User Input Grid (UIG)

**The User Input Grid (UIG) is a method for designing AI eval datasets that cover the real diversity of inputs an agent will face in production.** You list the dimensions along which user inputs vary (such as query type, domain, phrasing style and time frame), list the values each dimension can take, and then check that your dataset hits every value several times. It replaces datasets built from engineer intuition, which overfit to what engineers know, or from raw user logs, which overfit to easy, common cases.

- General method: [`skills/uig-skill.md`](skills/uig-skill.md) (or run `/uig`)
- Worked example: [`docs/uig-market-map.md`](docs/uig-market-map.md)

**Market Map UIG: 4 dimensions**

| Dimension | Values |
|-----------|--------|
| Query Type | Direct Category · Competitive Comps · Acquisition Targets · Historical Snapshot · Future/Speculative · Segment-Specific · Validation · Trend/Evolution |
| Market Domain | Tech/SaaS · Healthcare · Consumer/Brand · Financial · Industrial/Other |
| Query Style | Well-Specified · Under-Specified · Multi-Constraint · Jargon-Heavy · Edge/Out-of-Scope |
| Temporal Frame | Current · Historical · Future |

The Week 1 dataset (10 rows) had **zero coverage** of the Financial domain and the Segment-Specific query type. The Week 2 dataset was designed to fill those gaps deliberately.

---

## Key ideas

**Evaluator design**
- Code-based evaluators check *structure*. LLM judges check *semantics*. Use both.
- Write one criterion per judge. A compound judge is uninterpretable when it fails.
- The borderline few-shot example is worth more than the pass example: it calibrates the gray zone.
- Validate judges against human labels (TPR/TNR) before trusting them in production.

**Dataset design**
- 30–80 queries that hit each dimension value 3+ times outperform 500 random queries.
- Tag every row with its dimension values. You need to slice by dimension to diagnose failures.

**The eval loop**
- Evals are only useful if they run on every prompt change. Wire them into your workflow.
- A score going up only means something if you know *what changed* and *which eval category improved*.

**Judge calibration**
- False negatives (judge too strict) and false positives (judge too lenient) have different root causes and need different fixes. Read the judge's reasoning for each disagreement before changing the prompt.
- `/llm-align` automates this for any Braintrust experiment.

---

## FAQ

### What is an AI eval?
An AI eval is a repeatable test that scores an AI feature's outputs against defined criteria, so you can tell whether a prompt, model or agent change made the product better or worse. A useful eval setup has three parts: a dataset of realistic inputs, evaluators that score each output, and a loop that reruns them on every change.

### What is LLM-as-a-judge?
LLM-as-a-judge means using a language model to grade another model's output against a written criterion. It's for semantic qualities code can't check, such as whether the ranking is correct or whether an ambiguous query was handled well. This repo's judges each test one criterion, give binary PASS/FAIL definitions, include 3 few-shot examples (PASS, FAIL, borderline) and return JSON with a critique before the score. See [`skills/eval-llm-judge-skill.md`](skills/eval-llm-judge-skill.md).

### When should I use a code-based evaluator instead of an LLM judge?
Use code for anything structural and deterministic: counts, required sections, citations, formats. It's fast, free and never drifts. Use an LLM judge for meaning: correctness, relevance, tone, edge-case handling. Most products need both. See [`skills/eval-code-skill.md`](skills/eval-code-skill.md).

### How do I know whether my LLM judge is trustworthy?
Label 20–40 outputs by hand (roughly half PASS, half FAIL), run the judge on the same outputs, and compute TPR (how often the judge agrees when a human said PASS) and TNR (how often it agrees when a human said FAIL). Aim for both above 90%, and treat 80% as the minimum. Track them separately, because a judge with high overall accuracy can still be too lenient. `/llm-align` automates this.

### How big should an eval dataset be?
Coverage matters more than size. 30–80 queries that hit every value of every UIG dimension at least 3 times will usually beat 500 random queries. Start small, tag every row, and add rows where the gap analysis or production failures show you're blind.

### What is a User Input Grid?
A method for designing eval datasets around the dimensions along which real user inputs vary, so you cover them deliberately instead of by accident. See [The User Input Grid](#the-user-input-grid-uig).

### What goes in an AI PRD and an eval rubric?
An AI PRD specifies the agent's *behavior*, not screens. It includes how much autonomy the agent has and the release thresholds that gate a launch. The eval rubric lists the criteria the agent is judged on, with the definition of success and known risks next to the criteria they justify. Write a v1 rubric from the PRD before you read any traces, then sharpen it into v2 after trace analysis. See [`rubric-templates/`](rubric-templates/).

### How do I turn production failures into regression tests?
Take the support ticket or trace, strip the PII, classify the failure mode, map it to your UIG dimensions, and add it to a regression dataset, plus a few generalized variants so you test the failure pattern rather than just the one query. `/ticket-to-eval` does this end to end ([example](datasets/regression-dataset.csv)).

### Do I need Braintrust or Claude to use this?
No. The methods (UIG, judge design, TPR/TNR, rubrics) work with any eval platform and any model. The datasets and scorers are formatted for [Braintrust](https://braintrust.dev), and the skills run in [Claude Code](https://claude.com/claude-code).

---

## The example agent: Market Map

The Market Map agent takes a market research query and returns a ranked list of the top 3 players in that market, with supporting metrics and citations.

- *"team chat"* → ranks Microsoft Teams, Slack, Google Chat
- *"what AI security startups could Okta acquire in 2026 with its cash?"* → a scoped acquisition-target analysis
- *"search in 2003"* → a period-accurate historical market map

It is a single-turn prompt with no tools or retrieval, so all its knowledge comes from the model's weights. That makes it a good eval target: the failure modes are predictable and the output format is fixed. Prompt: [`prompts/market-map-prompt.md`](prompts/market-map-prompt.md).

---

## Course sessions

| Session | Topic | Key files |
|---------|-------|-----------|
| 1 | Traces in the Braintrust playground | `week1-dataset.csv`, `market-map-prompt.md` |
| 2 | Code-based and LLM judge evaluators | `evaluators/`, `week2-dataset-30.csv` |
| 3 | Dataset management and prompt iteration | `week3-dataset-60.csv`, `docs/uig-market-map.md` |
| 4 | Online monitoring and turning production failures into evals | `support-tickets.csv`, `regression-dataset.csv`, `/ticket-to-eval`, `/llm-align` |
| Webinar | [Eval Rubrics that Drive AI Product Strategy](https://luma.com/ayok3w9i) | `rubric-templates/` |

---

## About

Built by **Sandhya Hegde** and **Justin Bauer**, co-founders of [Calibre](https://calibrelabs.ai), an applied AI research and consulting firm. They teach the [AI Evals course on Reforge](https://www.reforge.com/courses/ai-evals), and Calibre writes about AI product quality at [blog.calibrelabs.ai](https://blog.calibrelabs.ai).

## License

Code (`evaluators/`, `mcp/`, `install-skills.sh`) is released under the [MIT License](LICENSE). Everything else, including the skills, rubric templates, PRDs, datasets, prompts and docs, is released under [Creative Commons Attribution 4.0 (CC BY 4.0)](LICENSE-CONTENT): reuse and adapt it freely, with credit to Calibre.

If you use this toolkit, cite it with GitHub's **"Cite this repository"** button (see [`CITATION.cff`](CITATION.cff)).
