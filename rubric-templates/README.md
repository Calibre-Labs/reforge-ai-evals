# AI PRD and eval rubric templates

An AI PRD template plus worked examples showing how to write an eval rubric for an AI agent: write v1 from the PRD before reading any traces, then sharpen it into v2 after trace analysis.

Corner and Ledger were built live during the [Eval Rubrics that Drive AI Product Strategy](https://luma.com/ayok3w9i) webinar for the [Reforge AI Evals course](https://www.reforge.com/courses/ai-evals). They sit at opposite ends of the same framework. **Corner** is a consumer shopping agent, where asking the user is expensive and mistakes are small and recoverable. **Ledger** is an enterprise finance agent, where asking is free and a mistake compounds.

| | PRD | Rubric v1 | Rubric v2 | Simulated session | Annotated trace |
|-|-----|-----------|-----------|-------------------|-----------------|
| **Corner** (consumer) | [md](corner/corner-prd-detailed.md) · [html](corner/corner-prd.html) | [html](corner/corner-rubric-v1.html) | [html](corner/corner-rubric-v2.html) | [html](corner/corner-simulation.html) | [html](corner/corner-trace.html) |
| **Ledger** (enterprise) | [md](ledger/ledger-prd-detailed.md) · [html](ledger/ledger-prd.html) | [html](ledger/ledger-rubric-v1.html) | [html](ledger/ledger-rubric-v2.html) | [html](ledger/ledger-simulation.html) | [html](ledger/ledger-trace.html) |

- [`ai-prd-template.md`](ai-prd-template.md): the generic AI PRD template both examples start from, with sections for autonomy, the eval rubric and release thresholds
- [`support-triage/support-triage-prd.md`](support-triage/support-triage-prd.md): a lighter sample PRD for a support-ticket triage agent
