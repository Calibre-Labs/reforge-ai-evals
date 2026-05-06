# Reforge AI Evals — Project Plan

A set of Claude Code slash command skills for building, auditing, and improving AI eval frameworks.
Designed to be client-distributable: each skill is a standalone `.md` file that installs in
`~/.claude/commands/` and works with zero external dependencies.

---

## Skills

| Skill file | Command | Purpose |
|-----------|---------|---------|
| `skills/uig-skill.md` | `/uig` | Build a User Input Grid, audit eval datasets, recommend new inputs |
| `skills/eval-code-skill.md` | `/eval-code` | Write deterministic code-based evaluators (format, count, structure) |
| `skills/eval-llm-judge-skill.md` | `/eval-llm-judge` | Write LLM-as-judge evaluator prompts for semantic properties |
| `skills/llm-align-skill.md` | `/llm-align` | Analyze LLM judge alignment with human labels (TPR/TNR, disagreements) |
| `skills/ticket-to-eval-skill.md` | `/ticket-to-eval` | Convert support tickets or traces into regression + generalized eval rows |

## Docs & Examples

| File | Description |
|------|-------------|
| `docs/uig-market-map.md` | Worked UIG example for a Market Map AI agent (output of `/uig`) |

---

## How to Install (for clients)

Copy the skill files you want into `~/.claude/commands/`:

```bash
cp skills/uig-skill.md ~/.claude/commands/uig.md
cp skills/eval-code-skill.md ~/.claude/commands/eval-code.md
cp skills/eval-llm-judge-skill.md ~/.claude/commands/eval-llm-judge.md
cp skills/llm-align-skill.md ~/.claude/commands/llm-align.md
cp skills/ticket-to-eval-skill.md ~/.claude/commands/ticket-to-eval.md
```

Then run `/uig`, `/eval-code`, etc. from any Claude Code session.

---

## Current Status

### Done
- [x] `/uig` — fully general-purpose; works for queries, instructions, structured records, agent inputs; no Braintrust dependency; no Market Map coupling
- [x] `docs/uig-market-map.md` — moved from `skills/` (it's an example, not a skill)

### To Do

#### Generalize existing skills (remove Braintrust + Market Map coupling)

- [ ] **`eval-code-skill.md`** — Remove "Sandhya" from description. Remove "For Braintrust" label from function signature. Replace Market Map–specific code examples (`company_count`, `has_category`, schema with `companies/sources` fields) with generic ones. See: [skill file](skills/eval-code-skill.md)

- [ ] **`eval-llm-judge-skill.md`** — Remove "Sandhya" from description. Remove "market map agent" reference in Step 3 guidance. Remove "market map evals" in working notes. Replace with generic examples. See: [skill file](skills/eval-llm-judge-skill.md)

- [ ] **`ticket-to-eval-skill.md`** — Major generalization needed. Phase 0 is Braintrust-primary (make it platform-agnostic). Phase 1 failure modes are Market Map–specific (generalize to common AI failure modes, keep Market Map ones as examples). Phase 3 dimension values are Market Map–specific (replace with generic UIG field references). Phase 5 dataset append instructions are Braintrust-specific. See: [skill file](skills/ticket-to-eval-skill.md)

- [ ] **`llm-align-skill.md`** — Largest change. All 5 phases use Braintrust SQL query syntax. Goal: keep the core methodology (confusion matrix, TPR/TNR, disagreement investigation, prompt fix suggestions, few-shot example selection) but replace Braintrust-specific queries with platform-agnostic pseudocode + notes on how to get the same data from other platforms (CSV, JSONL, custom eval runners). See: [skill file](skills/llm-align-skill.md)

#### New skills

- [ ] **`eval-trace-skill.md`** — New skill for evaluating multi-turn conversations with tool calls and complex traces. Single-turn eval skills can't handle: tool call correctness, multi-turn coherence, task completion rate, span-level scoring. Key dimensions to cover:
  - Tool selection correctness (right tool called?)
  - Tool parameter correctness (right arguments?)
  - Multi-turn coherence (context maintained across turns?)
  - Task completion (end-to-end goal achieved?)
  - Graceful handling of tool errors and ambiguous instructions
  - Trace structure: evaluating a span tree, not a single output string

  Target use case: Agentforce conversational agents with Salesforce action tool calls.

#### Docs / examples

- [ ] **`docs/examples/`** — Add worked UIG examples for 2–3 product archetypes beyond Market Map:
  - Conversational agent (e.g., Agentforce)
  - Internal search / knowledge retrieval (e.g., Glean-style)
  - Coding assistant

---

## Design Principles

1. **Standalone, no external dependencies** — each skill works with zero setup beyond copying the file
2. **Platform-agnostic** — no Braintrust-specific API calls, no hardcoded eval platform assumptions
3. **No product-specific tuning** — Market Map is an example, not the target; all examples should be clearly labeled as illustrative
4. **General-purpose input framing** — "inputs" not "queries"; covers instructions, records, actions, and text
5. **Embed, don't reference** — all methodology content lives in the skill file itself; no broken reference pointers
