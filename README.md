# AI Evals Toolkit: LLM judges, eval datasets and rubrics

**An open-source plugin and toolkit for evaluating AI agents and LLM features.** It covers writing the eval rubric in your PRD, designing eval datasets (the User Input Grid), turning trace notes into failure codes, writing code-based evaluators and LLM-as-a-judge prompts, and checking judges against human labels (TPR/TNR). Each step is a skill for Claude Code (and Codex) that your coding agent can run.

It is the working repo for the [Reforge AI Evals course](https://www.reforge.com/courses/ai-evals), taught by Sandhya Hegde and Justin Bauer of [Calibre](https://calibrelabs.ai), and it works for any agent or AI feature, from a single-turn prompt to a multi-step agent. Two steps stay with you: reading traces and labeling outputs to calibrate judges. The skills cover the rest.

**Who it's for:** product managers, AI engineers and founders who want to go from "I have a prompt that works" to "I have an eval loop I trust", and then to monitoring the agent in production.

---

## Contents

- [Quick start](#quick-start)
- [The skills](#the-skills)
- [What's in this repo](#whats-in-this-repo)
- [The User Input Grid (UIG)](#the-user-input-grid-uig)
- [Key ideas](#key-ideas)
- [FAQ](#faq)
- [Example agents: Mapper and Market Map](#example-agents-mapper-and-market-map)
- [Course sessions](#course-sessions)
- [About](#about)
- [License](#license)

---

## Quick start

**Claude Code, as a plugin (recommended):**

```bash
claude plugin marketplace add Calibre-Labs/reforge-ai-evals
claude plugin install ai-evals@calibre-labs
```

Skills then run as `/ai-evals:eval-rubric`, `/ai-evals:trace-codes` and so on, or just describe what you need and the right skill loads. Start with `/ai-evals:eval-guide` if you are not sure which one you need.

**For one session, from a clone:**

```bash
git clone https://github.com/Calibre-Labs/reforge-ai-evals.git
claude --plugin-dir ./reforge-ai-evals
```

You can also run Claude Code from the repo root: `.claude/commands/` links to `skills/`, so the skills load as plain slash commands there.

**Other ways to install:**
- **Claude desktop app:** run `bash scripts/build-plugin.sh` and install `dist/ai-evals.plugin`.
- **Codex:** a `.codex-plugin/` manifest and per-skill `agents/openai.yaml` files are included (not yet tested).
- **Plain slash commands, no plugin:** `bash install-skills.sh` copies each skill into `~/.claude/commands/`.

The skills read and write plain files (markdown, CSV, JSON, HTML), so you don't need an account with any eval platform. `llm-align` and `ticket-to-eval` can also read from a platform such as Braintrust or LangSmith if your data lives there.

**Run the example evaluators locally** (the LLM judges need an [Anthropic API key](https://console.anthropic.com) and `pip install anthropic`):

```python
from evaluators import company_count, has_sources, ranking_quality_judge

output = "your model output here"
input_query = "team chat"

print(company_count(output, input_query))          # 0.0, 0.5, or 1.0
print(ranking_quality_judge(output, input_query))  # {"score": 1.0, "metadata": {...}}
```

**Optional: braintrust-write MCP server.** This lets Claude insert dataset rows directly into Braintrust (`ticket-to-eval` can use it). Run `pip install -r mcp/requirements.txt`; `install-skills.sh` prints the config snippet to add to `~/.claude/settings.json`. `names.json` holds the short aliases it uses.

---

## The skills

Skills are added as the course moves through its sessions, so this list grows over the five weeks.

| Step | Who does it | Skill | Course week | Status |
|---|---|---|---|---|
| Not sure where to start | Claude | [`eval-guide`](skills/eval-guide/SKILL.md) | Week 1 | Available |
| Write the eval rubric into the PRD, v1 before traces and v2 after | Claude drafts, you decide | [`eval-rubric`](skills/eval-rubric/SKILL.md) | Week 1 | Available |
| Build a diverse set of test inputs (User Input Grid) | Claude | [`uig`](skills/uig/SKILL.md) | Week 1 | Available |
| Read and annotate traces | **You** | | Week 1 | |
| Cluster your trace notes into failure codes | Claude | [`trace-codes`](skills/trace-codes/SKILL.md) | Week 1 | Available |
| Write code-based evaluators | Claude | [`eval-code`](skills/eval-code/SKILL.md) | Week 2 | Available |
| Write LLM-as-a-judge evaluators | Claude | [`eval-llm-judge`](skills/eval-llm-judge/SKILL.md) | Week 2 | Available |
| Run the agent and the scorers over a dataset | Claude | `eval-run` | Week 2 | Coming |
| Label a sample pass or fail | **You** | | Week 3 | |
| Measure each judge against your labels (TPR/TNR) and fix it | Claude | [`llm-align`](skills/llm-align/SKILL.md) | Week 3 | Available |
| Turn support tickets and bad traces into regression eval rows | Claude | [`ticket-to-eval`](skills/ticket-to-eval/SKILL.md) | Week 3 | Available |
| Check tool calls and multi-step traces | Claude | `eval-trace` | Week 4 | Coming |
| Score production on a schedule and report drift | Claude | `eval-monitor` | Week 4 | Coming |

---

## What's in this repo

| Folder | What it gives you | Reusable for any AI product? |
|--------|-------------------|------------------------------|
| [`skills/`](skills/) | The plugin's skills: eval rubrics, User Input Grid, trace codes, code evaluators, LLM judges, judge alignment, ticket-to-eval | Yes |
| [`rubric-templates/`](rubric-templates/) | AI PRD template plus worked PRDs, eval rubrics, simulated sessions and annotated traces for three agents (consumer, enterprise, market research) | Yes |
| [`evaluators/`](evaluators/) | 4 code-based evaluators and 7 LLM-as-a-judge evaluators for the Market Map agent | Patterns yes, criteria are Market Map–specific |
| [`datasets/`](datasets/) | Tagged eval datasets (10 to 54 rows) plus targeted edge-case sets for geography, history, jargon, currency and impossible queries | Example only |
| [`prompts/`](prompts/) | The Market Map system prompt (v2, with 3 few-shot examples) | Example only |
| [`docs/`](docs/) | A complete worked User Input Grid for the Market Map agent | Example only |
| [`mcp/`](mcp/) | A small MCP server for writing rows to Braintrust datasets | Yes |

### `rubric-templates/`: AI PRD and eval rubric examples

**Mapper** is the course project for the fall 2026 cohort: a market research agent with five tools. Its session was recorded from a real run on Oct 2, 2026, and its trace page tags every step with a layer (context, retrieval, harness, systems).

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
| [`mapper/mapper-prd-detailed.md`](rubric-templates/mapper/mapper-prd-detailed.md) | Full PRD for Mapper, a market research agent that returns a ranked, sourced market map ([HTML](rubric-templates/mapper/mapper-prd.html)) |
| [`mapper/mapper-rubric-v1.html`](rubric-templates/mapper/mapper-rubric-v1.html) | Mapper's v1 rubric: nine lines, written from the PRD before a single trace |
| [`mapper/mapper-simulation.html`](rubric-templates/mapper/mapper-simulation.html) | A recorded Mapper session: click through what the user saw |
| [`mapper/mapper-trace.html`](rubric-templates/mapper/mapper-trace.html) | The trace behind that session, tagged by layer, with a reviewer view (press R) |
| [`mapper/traces/index.html`](rubric-templates/mapper/traces/index.html) | Nine more recorded Mapper sessions to read and annotate. Each page has a notes box, and the index exports the notes as a CSV for `trace-codes` ([data](rubric-templates/mapper/traces/sessions.json)) |
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
| `support-tickets.csv` | 10 | Synthetic customer support tickets containing PII. Source material for the `ticket-to-eval` skill. |
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

- General method: [`skills/uig/SKILL.md`](skills/uig/SKILL.md) (or run the `uig` skill)
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
- The `llm-align` skill automates this for any set of judge scores and human labels.

---

## FAQ

### What is an AI eval?
An AI eval is a repeatable test that scores an AI feature's outputs against defined criteria, so you can tell whether a prompt, model or agent change made the product better or worse. A useful eval setup has three parts: a dataset of realistic inputs, evaluators that score each output, and a loop that reruns them on every change.

### What is LLM-as-a-judge?
LLM-as-a-judge means using a language model to grade another model's output against a written criterion. It's for semantic qualities code can't check, such as whether the ranking is correct or whether an ambiguous query was handled well. This repo's judges each test one criterion, give binary PASS/FAIL definitions, include 3 few-shot examples (PASS, FAIL, borderline) and return JSON with a critique before the score. See [`skills/eval-llm-judge/SKILL.md`](skills/eval-llm-judge/SKILL.md).

### When should I use a code-based evaluator instead of an LLM judge?
Use code for anything structural and deterministic: counts, required sections, citations, formats. It's fast, free and never drifts. Use an LLM judge for meaning: correctness, relevance, tone, edge-case handling. Most products need both. See [`skills/eval-code/SKILL.md`](skills/eval-code/SKILL.md).

### How do I know whether my LLM judge is trustworthy?
Label 20–40 outputs by hand (roughly half PASS, half FAIL), run the judge on the same outputs, and compute TPR (how often the judge agrees when a human said PASS) and TNR (how often it agrees when a human said FAIL). Aim for both above 90%, and treat 80% as the minimum. Track them separately, because a judge with high overall accuracy can still be too lenient. The `llm-align` skill automates this.

### How big should an eval dataset be?
Coverage matters more than size. 30–80 queries that hit every value of every UIG dimension at least 3 times will usually beat 500 random queries. Start small, tag every row, and add rows where the gap analysis or production failures show you're blind.

### What is a User Input Grid?
A method for designing eval datasets around the dimensions along which real user inputs vary, so you cover them deliberately instead of by accident. See [The User Input Grid](#the-user-input-grid-uig).

### What goes in an AI PRD and an eval rubric?
An AI PRD specifies the agent's *behavior*, not screens. It includes how much autonomy the agent has and the release thresholds that gate a launch. The eval rubric lists the criteria the agent is judged on, with the definition of success and known risks next to the criteria they justify. Write a v1 rubric from the PRD before you read any traces, then sharpen it into v2 after trace analysis. The `eval-rubric` skill drafts both; see [`rubric-templates/`](rubric-templates/) for worked examples.

### How do I turn production failures into regression tests?
Take the support ticket or trace, strip the PII, classify the failure mode, map it to your UIG dimensions, and add it to a regression dataset, plus a few generalized variants so you test the failure pattern rather than just the one query. The `ticket-to-eval` skill does this end to end ([example](datasets/regression-dataset.csv)).

### Do I need Braintrust or Claude to use this?
No. The skills read and write plain files, and the methods (UIG, judge design, TPR/TNR, rubrics) work with any eval platform and any model. The skills run in [Claude Code](https://claude.com/claude-code), with untested Codex support. The example datasets use [Braintrust](https://braintrust.dev)'s CSV layout, which any tool that reads CSV can use.

---

## Example agents: Mapper and Market Map

**Mapper (fall 2026 cohort)** is a market research agent with five tools that returns a ranked, sourced market map. Its PRD, v1 rubric, a recorded session and ten annotatable traces are in [`rubric-templates/mapper/`](rubric-templates/mapper/).

**Market Map (spring 2026 cohort)** is the simpler version: one prompt, no tools or retrieval, returning the top 3 players in a market with supporting metrics and citations. Its prompt, datasets and evaluators remain here as a complete small example of an eval loop.

- *"team chat"* → ranks Microsoft Teams, Slack, Google Chat
- *"what AI security startups could Okta acquire in 2026 with its cash?"* → a scoped acquisition-target analysis
- *"search in 2003"* → a period-accurate historical market map

Because all of Market Map's knowledge comes from the model's weights, its failure modes are predictable and its output format is fixed, which makes it a good first eval target. Prompt: [`prompts/market-map-prompt.md`](prompts/market-map-prompt.md).

---

## Course sessions

The spring 2026 cohort's sessions, built on the Market Map agent. For the fall cohort, see the course week for each skill in [The skills](#the-skills).

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
