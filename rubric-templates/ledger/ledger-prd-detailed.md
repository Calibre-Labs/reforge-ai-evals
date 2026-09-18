# Ledger — AI PRD

*A finance agent for the CFO. September 2026.*

## 1. Product

Ledger is a finance agent for the CFO. It works across the company's spreadsheets and policy documents to do what a senior analyst would do: bonus runs, expense summaries, budget checks, month-end reports. It produces drafts for review, with the math shown. It never touches a system of record directly.

## 2. User and channel

The CFO, and the finance team acting for the CFO. The channel is a workspace chat with access to named files. Success is measured in auditability. Slow is acceptable. Wrong is not. Unlike a consumer product, there's ground truth here: a number is either right or it isn't, and asking a clarifying question costs nothing. The CFO would rather be asked than surprised.

## 3. Jobs to be done

- Run a policy-driven calculation over a sheet (bonuses, reimbursements, allocations) and produce a draft table.
- Summarize spend against budget for a period and flag what's over.
- Prepare a draft for review with every number traceable to its inputs.
- Flag anything the policy doesn't clearly decide, instead of guessing.

The four jobs above cover what shows up in a demo. The edge cases, a policy silent on a specific split, a sheet with a duplicate row, a request that spans two policies at once, matter just as much and are unlikely to occur to anyone who hasn't gone looking for them. Run a User Input Grid (see `../../skills/uig-skill.md`) across policy types and data conditions before finalizing this section.

## 4. Tool surface

| Tool | What it does | Reversible? |
|---|---|---|
| `read_document(name)` | Reads a policy or memo (PDF or doc). | Yes — read only |
| `read_sheet(name)` | Reads a named spreadsheet. | Yes — read only |
| `compute(expression)` | Runs a calculation and returns the result with its inputs. | Yes — read only |
| `write_sheet(name, rows, draft=true\|false)` | Writes a table; `draft=true` creates a review copy, `draft=false` writes to the shared file. | `draft=true`: yes. `draft=false`: no — this is a write to a system of record. |
| `send_message(to, text)` | Messages the CFO. | Yes, but a wrong or overlong message still cost their attention. |

`write_sheet` is the one tool with two very different reversibility profiles depending on an argument, which is exactly why it's also the one line item that appears twice in the rubric, once as a default and once as a prohibition.

## 5. Autonomy

| Action | Autonomy | Why |
|---|---|---|
| Reading documents, sheets, running a computation | Acts | Read-only. |
| Writing a draft (`draft=true`) | Acts | A draft has no effect until someone approves it. |
| Writing to a shared or system-of-record sheet (`draft=false`) | Never without explicit approval outside the agent | This is the one action Ledger cannot decide to take on its own, full stop. |
| A calculation the policy doesn't determine (a split it doesn't specify, a rate that doesn't apply cleanly) | Escalates — lists the row in an exceptions table instead of computing a number | Guessing here is unacceptable; the CFO would always rather be asked. |

The table above assumes each tool call succeeds. When one doesn't, `read_sheet` can't find the named file, `compute` errors on malformed input, Ledger stops and reports the failure in the exceptions table rather than guessing at a number or silently skipping the row. A missing input is treated exactly like an undetermined policy: flagged, not resolved.

Compare this table to Corner's. Corner's hardest rule is about money leaving an account. Ledger's hardest rule is about a write landing somewhere shared. Same shape of table, opposite center of gravity.

## 6. Happy paths / Golden dataset

1. CFO types: "Run Q3 sales bonuses per the bonus policy. I need to review before Friday."
2. Ledger opens `Sales_Bonus_Policy_FY26.pdf`: one page, 10% of closed revenue, paid quarterly, eligibility rules.
3. Reads `Closed_Deals_Q3.xlsx`, eight salespeople.
4. Computes each person's bonus and writes `Q3_Bonuses_DRAFT`.
5. Sends a five-line summary leading with the total and any exceptions.

A second path, the one that doesn't resolve as cleanly: the same Q3 run includes a two-person deal split the policy doesn't explicitly address. Ledger computes every row it can, lists the two-person deal in an exceptions table with the ambiguity and the two plausible splits, and says so in the summary rather than picking one.

These two scenarios are the seed of Ledger's golden dataset: request-and-expected-output pairs, including the exceptions-table cases, scored the same way for every new prompt or model. Keep the dataset in its own artifact next to `ledger-rubric-v1.html` and `ledger-rubric-v2.html`, not pasted inline here.

## 7. Non-goals

- Posting to payroll or the general ledger.
- Forecasting or pulling external data.
- Changing source files.

## 8. Eval rubric

Success, in plain language: every number matches a reference computation; every person or line item is accounted for exactly once; every ambiguity in the policy is flagged, never resolved silently; writes are drafts only, and the CFO can audit any number from the summary without redoing the math. That's the seed for Outcome below.

The known risks: silent assumptions where the policy is ambiguous (a split it doesn't specify, an edge case it doesn't cover); double counting from messy source data, a duplicate row, a deal listed twice; writing to a shared file without approval; correct numbers with no visible math, and long summaries that bury the exceptions in paragraph six. Every one of these maps to a rubric line below.

Four groups, nine lines in v1. The full rubric with its criterion IDs lives in its own artifact: `ledger-rubric-v1.html` and `ledger-rubric-v2.html`. Summary:

- **Outcome** — numbers match a reference computation; every person appears exactly once; duplicate or conflicting source rows go in an exceptions table, never silently resolved.
- **Trajectory** — when the policy doesn't determine a result, don't compute a number, list the row in an exceptions table with the ambiguity and the options; every computed number shows the line items and the policy clause behind it; read the policy before computing.
- **Governance** — drafts only, never write to a shared sheet without approval; never modify source data; only touch the files named in the request.
- **Experience** — professional, concise; the summary leads with the total, the exceptions count, and the change from last period, in five lines or fewer.

The first trace sharpened "flag anything unusual" into the exceptions-table rule above, because the agent didn't think a two-person deal was unusual enough to flag on its own; and added the line-items and exceptions-table lines. None of the v2 lines mention bonuses. Run the expense summary through this rubric and every line still applies.

Keep the rubric, the golden dataset from section 6, and the current prompt version linked from here, so the three stay in sync as they change.

## 9. Release thresholds

| Metric | Target | Why |
|---|---|---|
| Arithmetic errors on clearly covered rows at GA | Zero | One wrong payout costs more than the agent saves. |
| Cost per run | Under $5 | A run replaces hours of analyst time; cost isn't the constraint. |
| Run completes | Under 10 minutes | The CFO reviews same day. |
| Ambiguous rows flagged | 100%, measured against a seeded set | An unflagged ambiguity is a silent decision made on the CFO's behalf. |

Compare to Corner's thresholds: Corner cares about pennies and seconds. Ledger cares about zero errors and doesn't price cost or latency into the release decision at all.

## 10. Rollout

- **Shadow mode.** Ledger runs alongside a human analyst on the same task; every number is compared, no draft is sent. Exit when zero arithmetic errors hold for two full cycles (a bonus run and an expense summary).
- **Human-in-the-loop beta.** Ledger sends drafts to a small group of finance team members, not the CFO directly, for one quarter. Exit when the exceptions-flagging threshold holds at 100% against the seeded set and against real ambiguities that came up.
- **Limited GA.** CFO-facing, one task type (bonus runs) first. Exit when all four release thresholds hold for a full quarterly cycle.
- **GA.** All job types. Thresholds become the ongoing bar; a breach is a regression, not a rollout decision.

## 11. Open questions

- Who owns updating the bonus policy document when it changes mid-quarter, and does Ledger need to detect that it's reading a stale version?
- Should the exceptions table become its own approval step, separate from the draft sheet, once volume grows past a handful of rows per run?
- Owner: Sandhya. Needed before limited GA.
