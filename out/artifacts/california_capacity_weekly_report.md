---
opportunity: california_capacity_weekly_report
type: sop
citations: [lokay-m/sent_items/46, lokay-m/sent_items/67, lokay-m/sent_items/40, lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/55, lokay-m/sent_items/131, lokay-m/sent_items/146, lokay-m/sent_items/63, lokay-m/sent_items/110]
---

# SOP: Weekly California Capacity Report (automated draft, analyst approval)

**Owner:** Transwestern commercial analyst (today michelle.lokay)
**Distribution list:** steven.harris, kimberly.watson, lorraine.lindberg, tk.lohman, lindy.donoho [lokay-m/sent_items/18]
**Value:** about 1.3 hours a month, or $110 per month ($1,320 per year) at $85/hour

## Why this changed

The report was typed by hand every week. Delivery and utilization figures were keyed in, and each percentage was worked out by hand. The week label was also typed, and once a report went out with the wrong week, so the whole list got a correction email:

> Sorry, the effective date for this new report is 01/07-01/11.

[lokay-m/sent_items/46]

## What the job produces

A scheduled job runs on the last trading day of the week, after Gas Daily prices are posted. That is normally Friday, or Thursday in a short week (for example 12/26-12/28 [lokay-m/sent_items/63] or 02/19-02/22 [lokay-m/sent_items/110]). It produces:

1. **A draft email, not sent**, titled `California Capacity Report for Week of MM/DD-MM/DD`. The week comes from the trading-week calendar. The body uses the current layout:
   - Transwestern average deliveries to California with utilization, San Juan lateral throughput, and total East deliveries.
   - El Paso average deliveries to California, then PG&ETop, SoCalEhr and SoCalTop, each with capacity, deliveries and utilization.
   - Thursday's or Friday's posted Gas Daily prices, with the heading matched to the send day: SoCal gas large pkgs, PG&E large pkgs, San Juan (non-Bondad), and TW Permian, each with its day-over-day change [lokay-m/sent_items/131].
2. **A validation notice** to the analyst if a day of data is missing, a capacity value is older than the set age limit, or a percentage falls outside a plausible range.
3. **A history file** that records each week's figures.

An example of a line the job now calculates:

> Transwestern's average deliveries to California were 1059 MMBtu/d (97%), with San Juan lateral throughput at 839 MMBtu/d.

[lokay-m/sent_items/67]

## Weekly routine for the analyst (about 10 minutes)

1. **Open the draft and check the validation status** printed at the top. If it shows a hold, go to Exceptions below.
2. **Check the subject week** against the calendar. It must match the Monday-to-last-trading-day range.
3. **Check the figures for anything odd.** Compare them with last week's history line. If utilization changes sharply, for example PG&ETop at 33% [lokay-m/sent_items/40], add a short note on the cause.
4. **Check the price lines.** A point with no posting must read `n/a`, never last week's price [lokay-m/inbox/10].
5. **Add commentary** if needed, then **approve**. Only approval sends the email to the distribution list.

## Exceptions

| Situation | What to do |
|---|---|
| Missing day of delivery data | Hold the draft. Get the missing day from the source, then rerun. Do not send a partial average. |
| Capacity value past its age limit | Confirm the current capacity with the pipeline posting and update the capacity table with an effective date. Only the capacity owner makes this change. |
| Capacity changed in the source | Confirm it is a real capacity change and not a data glitch before updating the table. SoCalEhr moved from 1042 [lokay-m/inbox/10] to 1250 [lokay-m/sent_items/18]. |
| Gas Daily point not posted, or the point was renamed | Leave it as `n/a`. Update the point mapping if the name changed, as when TW San Juan became San Juan (non-Bondad) [lokay-m/sent_items/146]. |
| Percentage out of range | Recheck the capacity and deliveries inputs before approving. |
| Error found after sending | Send one correction email to the list, then fix the calendar, table or mapping so the error cannot repeat. |

A stale capacity value gives a utilization figure that looks right but is wrong. For example:

> PG&ETop, capacity of 1140 MMBtu/d, deliveries of 374 MMBtu/d (33%)

[lokay-m/sent_items/40]

## What stays manual

- Final review and approval of every report. The job never sends on its own.
- Commentary on unusual weeks.
- Capacity table updates.
- Adding or dropping report sections. For example, the Enron basis table first read `n/a` and was later dropped [lokay-m/sent_items/55].

## Rollout

The job runs alongside the manual report for three to four weeks, with the draft going only to the analyst. Each week, the analyst compares its figures with the report that was sent. After that, the job switches to the approve-and-send flow. Success measure: analyst minutes per report, and zero correction emails.
