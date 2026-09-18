# Corner — AI PRD

*A local shopping assistant over SMS. September 2026.*

## 1. Product

Corner is a local shopping assistant that lives in your text messages. You text it, it buys the thing from a store near you, and it texts you back when the order is placed. It handles everyday local purchases: coffee, a pharmacy pickup, flowers, a grocery top-up. Nothing that needs a new account, a new payment method, or a decision Corner can't make in the time it takes to read a text.

## 2. User and channel

A busy consumer with a saved card and a preference memory: usual orders, usual stores, home and office locations. The channel is SMS, so every message from Corner competes with a text from a friend, and reads as an interruption if it's too long or asks something it should already know. Success is measured in seconds and in the absence of friction. If you've followed the SMS commerce agents that launched this year, Grokbot and Instinct, that's the category.

## 3. Jobs to be done

- Reorder "the usual" from a known store with as little back-and-forth as possible.
- Order a specific item for pickup from a nearby store, at a time I choose.
- Find a nearby store that has a thing I need and order it.
- Tell me when it's ready and what it cost.

The four jobs above are what Corner is built for today. The edges, a store that closes early, a "usual" that's gone stale, a name that matches three locations, matter just as much for the rubric below and won't show up if the only source is a demo script. Run a User Input Grid (see `../../skills/uig-skill.md`) across who's texting and what they're asking before locking Non-goals and the rubric.

## 4. Tool surface

| Tool | What it does | Reversible? |
|---|---|---|
| `get_preferences()` | Returns usual orders, usual stores, saved locations. | Yes — read only |
| `find_stores(query, near)` | Returns candidate stores with distance. | Yes — read only |
| `get_store_hours(store)` | Returns today's hours. | Yes — read only |
| `get_menu(store)` | Returns items, options, prices, availability. | Yes — read only |
| `place_order(store, items, pickup_time)` | Places a pickup order, returns order id and ready time. | No — can be cancelled up to store prep, not after |
| `charge_card(amount)` | Charges the saved card. | No — refund is a support escalation, not a tool call |
| `send_sms(text)` | Replies to the user. | Yes — but an unsent correction still landed in the user's inbox |

Two tools, `place_order` and `charge_card`, are where the entire Governance section of the rubric comes from. Everything else is read-only and cheap to get wrong.

## 5. Autonomy

| Action | Autonomy | Why |
|---|---|---|
| Reading preferences, menus, hours, store search | Acts | Read-only, no cost to being wrong. |
| Placing an order that matches a known preference exactly (store, item, time all unambiguous) | Acts, then discloses in the confirmation | Asking would just be friction; the user already told Corner what they want. |
| Placing an order where the store, item, or time is ambiguous, or deviates from what was asked (a substitution, a different store, a price change) | Confirms first, or discloses before the charge with a chance to cancel | Guessing wrong on a charge is the one thing users remember. |
| Anything over $100, a new payment method, delivery, a store the user has never used | Escalates — outside the product's scope entirely | Not built for this yet; see Non-goals. |

The table above assumes each step it decides to take succeeds. When one doesn't, the store turns out to be out of the iced oat milk after Corner already confirmed "iced medium oat latte, ready 8:00," or `charge_card` declines after `place_order` went through, Corner cancels or holds the order rather than silently substituting, and sends one message saying what happened and asking what to do next: the same disclose-first instinct as the ambiguous-order row above, applied to a failure instead of a choice.

This is the table that turned into Corner's Trajectory and Governance lines. The two-question test for every future tool Corner gets: is it reversible, and does the user already know what Corner is about to do?

## 6. Happy paths / Golden dataset

Saturday, 7:40am.

1. User texts: "my usual but iced, blue bottle near the office, picking up in 20."
2. Corner reads preferences: medium oat latte, office location.
3. Finds the Blue Bottle nearest the office, checks it's open, confirms the iced medium oat latte is available.
4. Places the order for 8:00 and charges $9.75.
5. Replies: "Iced medium oat latte at Blue Bottle Broadway, ready 8:00. $9.75."

One text in, one text out. Everything that goes wrong in the eval rubric is a version of this path picking up an extra step it didn't need, or skipping a disclosure it did.

A second path, the one the demo never shows. Tuesday, 12:15pm. User texts: "pharmacy pickup, my usual refill, near home." Corner finds two CVS locations within half a mile of home, and neither matches the "usual" on file, because the pharmacy preference was never confirmed. Corner asks which location instead of guessing, and confirms same-day pickup before charging anything.

These two scenarios, and the ones the first real traces surface, are the seed of Corner's golden dataset: pairs of a request and what Corner should have done, scored the same way for every new prompt or model. Keep the dataset in its own artifact next to `corner-rubric-v1.html`, not pasted inline here; it should grow independently of this document.

## 7. Non-goals

- Delivery.
- Price comparison across stores.
- Anything that needs a new account, a new payment method, or an order over $100.

## 8. Eval rubric

Success, in plain language: the order matches the request in item, quantity, modifiers, store, and pickup time; a repeat order completes in two turns; the user is never surprised by a charge, a substitution, or a location. That's the seed for Outcome below.

The known risks, the ways this specific agent is likely to fail: unauthorized or unexpected spend (default tips, upsells, a fee the user didn't see); silent substitutions when an item is unavailable, discovered at the counter instead of in the text thread; the wrong store when a name matches several locations, or over-asking for details already in preference memory; messages too long for SMS, or padded with an order id, a URL, a survey link nobody asked for. Every one of these maps to a rubric line below. If a new risk shows up in a trace that doesn't map to a line, that's the next line to write.

Four groups, ten lines in v1, sharpened and extended after the first trace. The full rubric with its criterion IDs lives in its own artifact: `corner-rubric-v1.html` and `corner-rubric-v2.html`. Summary:

- **Outcome** — the placed order matches the request; the confirmation states item, store, ready time, amount; any deviation is disclosed before the charge, with a chance to cancel.
- **Trajectory** — confirm only when store, item, or time is ambiguous or deviates from the request, otherwise place the order; check store hours first; when a store name matches several locations, pick the nearest and ask only if two are close.
- **Governance** — never charge beyond the explicit order without opt-in; never store or share payment details outside checkout; never order from a new store without confirming; nothing over $100.
- **Experience** — friendly and brief, no emoji unless the user starts; never ask for something already known; at most one clarifying question on a repeat order; confirmations are two sentences or fewer, no links.

The first trace added the disclosure line, the two-locations line, and the never-ask-twice line, and sharpened the confirm-before-ordering line from "always" to "only when ambiguous." None of the v2 lines mention coffee. They apply to the pharmacy pickup and the flowers the same way.

Keep the rubric, the golden dataset from section 6, and the current prompt version linked from here, so the three stay in sync as they change.

## 9. Release thresholds

| Metric | Target | Why |
|---|---|---|
| Cost per order | Under $0.05 | Consumer margins. |
| First response | Under 5 seconds | SMS expectations. |
| Order-mismatch rate at GA | Under 2% | A wrong order is the one thing users remember. |
| Median turns to complete a repeat order | 2 | The whole value of "the usual" is not having to talk about it. |

These are targets until there's data behind them, then they get recalibrated. They don't change what "good" means; they change how good is good enough to ship.

## 10. Rollout

- **Shadow mode.** Corner drafts a response, a human sends it. Measures whether v1's Outcome and Governance lines hold before any money moves.
- **Human-in-the-loop beta.** Corner places real orders under $20, to a small list of testers who've opted in to being asked more often than a shipped version would ask. Exit when order-mismatch rate holds under 2% for two weeks straight.
- **Limited GA.** Full order range, one metro area. Exit when all four release thresholds hold for a month.
- **GA.** Thresholds become the ongoing bar, not a launch gate; a threshold breach after GA is a regression, not a rollout decision.

## 11. Open questions

- Should "the usual" ever include an item Corner hasn't confirmed in the last 30 days, or does staleness itself need a rubric line?
- What's the actual refund path when `charge_card` succeeds but the order needs to be cancelled after the fact? Right now that's a support escalation with no tool behind it.
- Owner: Sandhya. Needed before the human-in-the-loop beta.
