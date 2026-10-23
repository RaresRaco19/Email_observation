---
opportunity: california_capacity_weekly_report
type: sop
citations: [lokay-m/sent_items/46, lokay-m/sent_items/86, lokay-m/inbox/10, lokay-m/sent_items/18]
---

# SOP: Weekly California Capacity Report (draft-and-review)

**Owner:** Transwestern marketing analyst (Michelle Lokay). **Recipients:** Steven Harris, Kimberly Watson, Lorraine Lindberg, TK Lohman, Lindy Donoho. **Value:** about 0.9 h/month, $73/month ($876/year) at $85/h. This is small, so keep the build light and confirm data sources first.

## What the automation produces
A scheduled job runs on the last business day of the week (Friday, or Thursday on short weeks). It saves a draft email, not a sent one, containing:
- The subject "California Capacity Report for Week of MM/DD-MM/DD", built from the business calendar.
- The existing body layout: Transwestern deliveries, San Juan lateral and East deliveries, El Paso deliveries by point (PG&ETop, SoCalEhr, SoCalTop) with utilization percentages, posted Gas Daily prices, and the Enron Online basis block only when quotes exist.
- Exception notes at the top for the analyst.
- A weekly figures archive row.

Example of the sentence the job reproduces:

> Transwestern's average deliveries to California were 1011 MMBtu/d (93%), with San Juan lateral throughput at 872 MMBtu/d.

[lokay-m/sent_items/86]

## What the analyst checks before sending
1. Read the exception notes: missing source days, a price not posted (shown as "n/a"), a capacity value changed since last week, a week-over-week swing, or any percentage above 100% (Transwestern reached 103%).
2. Confirm the week range in the subject matches the calendar week. A hand-typed label caused this correction to all five recipients:

> Sorry, the effective date for this new report is 01/07-01/11.

[lokay-m/sent_items/46]

3. Sanity-check the volumes against the prior week's report.
4. Add market commentary for unusual weeks, then send.

## Capacity table
Utilization depends on delivery-point capacities, which change. SoCalEhr was 1042 in October and 1250 from December:

> SoCalEhr, capacity 1042 MMBtu/d, deliveries of 707 MMBtu/d (68%)

[lokay-m/inbox/10]

The analyst owns the effective-dated capacity table and updates it whenever El Paso or Transwestern announces a change. The job never changes it on its own.

## Exceptions
| Situation | Action |
|---|---|
| Source volume missing for a day | Job flags it; analyst obtains the data or notes the gap in the email |
| Gas Daily price not posted or location renamed (for example TW San Juan to San Juan (non-Bondad)) | Job writes "n/a", never a carried-forward price; analyst confirms |
| Enron basis quotes unavailable | Section omitted; analyst decides whether to explain |
| Wrong week or error found after sending | Send one correction to the full list, and log it for the success metric |
| Job fails to produce a draft | Build the report by hand as before |

## Rollout and measure
Run in parallel for three or four weeks (job draft alongside the hand-built report) and reconcile differences. Then switch to draft-and-review. Track, over the first 8 weeks, the share of reports sent without a correction and the analyst's minutes per report (about 30 today; target is review only).

## Open items
The evidence does not show where Transwestern and El Paso volumes come from. Confirm the sources, and any Gas Daily licensing limits, before funding the build. Without them, a spreadsheet that calculates percentages and the subject line is the fallback.
