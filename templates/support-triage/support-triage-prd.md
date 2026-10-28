# Sample AI PRD: Support Ticket Triage (v1.0)

**Owner:** [Name]  | **Status:** Prototyping  | **Default Model:** Gemini 3 Flash Preview

## 1. Problem & Business Value

Support leads spend about 4 hours per day manually tagging tickets. This creates a lag before specialists can see high-priority issues.

**Proposed solution:** A background agent that autonomously classifies tickets in real time by Intent, Sentiment and Urgency

## 2. Prompt Logic & Dataset

### System Instructions

> You are a support analyst. Categorize incoming tickets into one of three buckets: Technical, Billing, or Feature Request. Assign a Volatility score from 1-10 based on user frustration.

### Golden Dataset

- Attached: 50 historical tickets with "Gold" labels for few-shot prompting.

### Graceful Failure

- If sentiment is **Angry**, immediately flag for **human override**, regardless of category.

## 3. Tool Specification

The agent should have access to the following APIs before making a triage decision:

| Tool Name | Action | Input Param | Purpose |
| --- | --- | --- | --- |
| `User_Lookup` | Query internal database | `user_email` | Check whether the user is a VIP or Enterprise customer to escalate priority. |
| `Subscription_Check` | Stripe/Billing API | `customer_id` | Confirm active paid plan before routing to Priority Tech Support. |
| `Jira_Search` | Jira API | `keyword_string` | Check for an existing Active Incident or Known Bug matching the complaint. |
| `CRM_Write` | Salesforce/HubSpot API | `ticket_id`, `tag` | Write final classification and sentiment score to the CRM record. |

## 4. Evaluation Criteria

| Metric | Target | Why It Matters |
| --- | --- | --- |
| Categorization Accuracy | > 92% | Avoid routing Billing issues to Dev teams. |
| Sentiment Precision | > 85% | Avoid false alarms on frustrated users. |
| Latency | < 2s | Must be faster than manual triage. |
| Hallucination Rate | 0% | Model should never invent ticket IDs or usernames. |

Note: standard out-of-the-box evals like LLM tone/helpfulness are not primary success metrics for this workflow.

## 5. Edge Cases Handling

- **Low-confidence fallback:** If model confidence is `< 0.7`, do not auto-tag. Move ticket to **Needs Human Review**.
- **Drift monitoring:** Run a weekly manual audit on 5% of AI-tagged tickets.
- **User feedback loop:** Add a support-side prompt: `Is this tag correct? [Yes/No]`.

## 6. Prototype & Early Findings

**Internal Demo:** [Link]

**Early findings:**
- Very short inputs (for example, "Help!") cause category hallucinations. Add a clarification-needed mode.
- About 20% of tickets contain two issues (for example, "I can't log in and I need to update my billing info"). The current model picks only the first issue, so we need multi-label classification instructions.
- The model struggled with sarcasm. We added 5 sarcastic complaint examples to the Golden dataset for few-shot learning via the system prompt.

## 7. Technical Constraints

- **Data privacy:** Scrub all PII (email addresses, phone numbers) with a regex preprocessor before sending to the LLM API.
- **Cost per ticket:** Keep categorization cost below `$0.01` to maintain ROI.
