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

Compare this table to Corner's. Corner's hardest rule is about money leaving an account. Ledger's hardest rule is about a write landing somewhere shared. Same shape of table, opposite center of gravity.

## 6. Happy path

1. CFO types: "Run Q3 sales bonuses per the bonus policy. I need to review before Friday."
2. Ledger opens `Sales_Bonus_Policy_FY26.pdf`: one page, 10% of closed revenue, paid quarterly, eligibility rules.
3. Reads `Closed_Deals_Q3.xlsx`, eight salespeople.
4. Computes each person's bonus and writes `Q3_Bonuses_DRAFT`.
5. Sends a five-line summary leading with the total and any exceptions.

## 7. Non-goals

- Posting to payroll or the general ledger.
- Forecasting or pulling external data.
- Changing source files.

## 8. Known risks

- Silent assumptions where the policy is ambiguous (a split it doesn't specify, an edge case it doesn't cover).
- Double counting from messy source data: a duplicate row, a deal listed twice.
- Writing to a shared file without approval.
- Correct numbers with no visible math, and long summaries that bury the exceptions in paragraph six.

## 9. Definition of success

- Every number matches a reference computation.
- Every person or line item is accounted for exactly once.
- Every ambiguity in the policy is flagged, never resolved silently.
- Writes are drafts only, and the CFO can audit any number from the summary without redoing the math.

## 10. Eval rubric

Four groups, nine lines in v1. The full rubric with its criterion IDs lives in its own artifact: `ledger-rubric-v1.html` and `ledger-rubric-v2.html`. Summary:

- **Outcome** — numbers match a reference computation; every person appears exactly once; duplicate or conflicting source rows go in an exceptions table, never silently resolved.
- **Trajectory** — when the policy doesn't determine a result, don't compute a number, list the row in an exceptions table with the ambiguity and the options; every computed number shows the line items and the policy clause behind it; read the policy before computing.
- **Governance** — drafts only, never write to a shared sheet without approval; never modify source data; only touch the files named in the request.
- **Experience** — professional, concise; the summary leads with the total, the exceptions count, and the change from last period, in five lines or fewer.

The first trace sharpened "flag anything unusual" into the exceptions-table rule above, because the agent didn't think a two-person deal was unusual enough to flag on its own; and added the line-items and exceptions-table lines. None of the v2 lines mention bonuses. Run the expense summary through this rubric and every line still applies.

## 11. Release thresholds

| Metric | Target | Why |
|---|---|---|
| Arithmetic errors on clearly covered rows at GA | Zero | One wrong payout costs more than the agent saves. |
| Cost per run | Under $5 | A run replaces hours of analyst time; cost isn't the constraint. |
| Run completes | Under 10 minutes | The CFO reviews same day. |
| Ambiguous rows flagged | 100%, measured against a seeded set | An unflagged ambiguity is a silent decision made on the CFO's behalf. |

Compare to Corner's thresholds: Corner cares about pennies and seconds. Ledger cares about zero errors and doesn't price cost or latency into the release decision at all.

## 12. Rollout

- **Shadow mode.** Ledger runs alongside a human analyst on the same task; every number is compared, no draft is sent. Exit when zero arithmetic errors hold for two full cycles (a bonus run and an expense summary).
- **Human-in-the-loop beta.** Ledger sends drafts to a small group of finance team members, not the CFO directly, for one quarter. Exit when the exceptions-flagging threshold holds at 100% against the seeded set and against real ambiguities that came up.
- **Limited GA.** CFO-facing, one task type (bonus runs) first. Exit when all four release thresholds hold for a full quarterly cycle.
- **GA.** All job types. Thresholds become the ongoing bar; a breach is a regression, not a rollout decision.

## 13. Open questions

- Who owns updating the bonus policy document when it changes mid-quarter, and does Ledger need to detect that it's reading a stale version?
- Should the exceptions table become its own approval step, separate from the draft sheet, once volume grows past a handful of rows per run?
- Owner: Sandhya. Needed before limited GA.
