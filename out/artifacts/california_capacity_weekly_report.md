---
opportunity: california_capacity_weekly_report
type: sop
citations: [lokay-m/inbox/10, lokay-m/sent_items/46, lokay-m/sent_items/131, lokay-m/sent_items/18]
---

# SOP: Weekly California Capacity Report (generated draft)

**Owner:** Transwestern marketing analyst (Michelle Lokay). **Audience:** the fixed Transwestern commercial list (Steven Harris, Kimberly Watson, Lorraine Lindberg, TK Lohman, Lindy Donoho).

**Why it exists:** the report is retyped by hand every week, about 2.87 a month, at roughly 30 minutes each. At $85/hour the automatable share is worth $73 a month ($876 a year). The value is small, so the tool stays a simple script, not an integration.

## What the automation produces

Each Friday morning (the last business day in a short week, when Thursday's posted Gas Daily prices are used), a script reads the weekly input sheet and produces:

1. An unsent draft titled "California Capacity Report for Week of MM/DD-MM/DD", with the week range built from the calendar, addressed to the existing list.
2. The report in today's layout, for example:

> Transwestern's average deliveries to California were 945 MMBtu/d (87%), with San Juan lateral throughput at 865 MMBtu/d.

[lokay-m/inbox/10]

   Followed by the El Paso breakdown (PG&ETop, SoCalEhr, SoCalTop), the Gas Daily price table with day-over-day changes ("n/a" for missing points), and the basis section only if included that week.
3. A check list above the draft: out-of-range values and missing inputs.
4. A weekly CSV of the computed figures.

## What the analyst checks (before every send)

- Every figure against the input sheet; the percent-of-capacity numbers especially.
- The check list. Utilization over 100% is not automatically wrong: one week legitimately showed 103% [lokay-m/sent_items/18]. Confirm it, then add a line of context.
- The week label and the distribution list.
- Price points: confirm which are shown (for example "San Juan (non-Bondad)" replaced "TW San Juan" in March [lokay-m/sent_items/131]) and whether a basis section goes in.
- Add commentary on unusual weeks, then send.

## Exceptions

| Situation | Action |
|---|---|
| Missing delivery or price input | Draft shows "n/a"; analyst fills the input or sends with "n/a" |
| Utilization over 100%, or large week-over-week jump | Flagged; analyst confirms with the source before sending |
| Capacity changed (SoCalEhr moved from 1042 to 1250 MMBtu/d between October and December) | Analyst updates the capacity table with a new effective date; any figure not reviewed recently is flagged |
| Wrong week label sent | Past failure: the analyst had to send a correction. |

> Sorry, the effective date for this new report is 01/07-01/11.

[lokay-m/sent_items/46]

   With the calendar-built subject this should not recur. If it does, send a correction and log it.
| Gas Daily cannot be pulled automatically (licensed publication) | Analyst pastes prices into the input sheet |

## Stays manual

Final review and sending; commentary on unusual weeks; confirming capacity changes; deciding which price points and basis sections appear.

## Rollout and measure

Before go-live, record where each number comes from (the emails do not name the sources), then run the script alongside the manual report for three to four weeks and compare figure by figure. Success is the share of reports sent from the draft with no correction email, plus analyst minutes per report before and after.
