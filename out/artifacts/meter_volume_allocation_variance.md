---
opportunity: meter_volume_allocation_variance
type: sop
citations: [farmer-d/logistics/595, farmer-d/logistics/622, farmer-d/logistics/739, farmer-d/logistics/925, farmer-d/logistics/1185, farmer-d/logistics/1351, farmer-d/logistics/1483, farmer-d/logistics/2089]
---

# SOP: Daily and month-end meter exception review

**Owner:** volume management. **Users:** logistics desk, settlements/UA4 analysts, accounting managers.

## What the automation produces

After each POPS allocation run, and again before month-end UA4 close, a read-only job compares MIPs measurement volumes, POPS confirmed and allocated volumes, and Sitara, OSS and CPR deals by meter and gas day. Each rule hit becomes one row in a shared exception queue. A row shows the meter, period, the volume from each source, the prior month, a suggested owner, status and age. Rules:

- flow with no deal
- deal with no flow
- zero or missing POPS-to-Sitara feed
- delivery nom at a receipt meter
- confirmation on a day the deal does not cover
- nomination not pulled
- allocated vs measured difference beyond tolerance

Outputs: a daily exception list, a month-end UA4 summary, an aging report that replaces the manual interdesk/interconnect list, and an evidence pack per exception.

## Daily routine

1. Volume management opens the daily list after the allocation run and confirms the owner on each new row (routing table: meter and rule type to owner).
2. The owner checks the row's evidence pack before emailing anyone. The pack already answers the questions analysts used to ask by hand:
   > Daren is there a deal in CPR which may not have fed over to OSS?

   [farmer-d/logistics/622]
3. Flow with no deal [farmer-d/logistics/595] goes to the logistics desk. A zero feed to Sitara [farmer-d/logistics/925] goes to volume management the same day, so volumes are overridden before P&L is affected.
4. The owner records a resolution note on the row and sets the status. Nobody sends a "status?" email; they read the queue instead of asking:
   > What is the status on this meter?

   [farmer-d/logistics/739]

## What a person checks

- **Confirmations outside the deal dates.** A confirmation on a day the deal does not cover causes wrong prorating, as in [farmer-d/logistics/1351]. A person decides whether to move the volume or add the date to the deal.
- **Desk-to-desk variances.** Different volume sources on each side [farmer-d/logistics/1185] are flagged. Logistics and the counterparty decide which number is custody.
- **Unallocated flow awaiting a deal.** The owner confirms flow occurred and has a deal extended [farmer-d/logistics/1483].
- **Counterparty payment calls.** Accounting checks the queue before forwarding a call such as [farmer-d/logistics/2089].

## Exceptions and escalation

- A row open past the age limit set by volume management escalates to the named manager on the routing table.
- A row with no owner is assigned by volume management that day.
- A tolerance that produces noise is logged and adjusted by volume management, not silenced by individual analysts.
- If a source extract fails or is late, the job marks the run incomplete and the desk works from the prior day's list.

## Stays manual

- Deciding which volume is correct when sources disagree.
- Creating, extending or moving deals in Sitara, and reallocating in POPS.
- Legal or commercial calls, such as the book a sale belongs in.
- Talking to counterparties and pipelines.

## Measure

Meters with measured flow but no matching Sitara/OSS deal still open at month-end UA4 close, and the median age of open exceptions. Handling time saved is small, about $62/month ($744/year) at $85/hour. The real value is catching large feed failures the day they appear.
