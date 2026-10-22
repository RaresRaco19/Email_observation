---
opportunity: realtime_deal_variance_reconciliation
type: sop
citations: [williams-w3/sent_items/392, williams-w3/sent_items/425, williams-w3/sent_items/510, williams-w3/inbox/126, williams-w3/sent_items/417, williams-w3/inbox/79, williams-w3/sent_items/453, williams-w3/sent_items/373, williams-w3/sent_items/442, williams-w3/sent_items/441, williams-w3/sent_items/499]
---

# SOP: End-of-shift real-time variance report

**Owner:** Real-time lead (West desk). **Users:** real-time shift traders, CAPS schedulers, deal control, settlements.
**Runs:** At the end of each real-time shift, and again early the next morning before the DPR, for the previous flow date.

## Why this exists

Mismatches between Enpower, CAPS, position manager and the EPE schedules are currently found the next morning or a month later. Examples: a duplicate entry caught from the DPR and a BOM SAR [williams-w3/sent_items/453], a missing deal that left position manager short [williams-w3/sent_items/373], and EPE schedules that stayed wrong for two days [williams-w3/inbox/79]. The manual reconciliation sheet also gets skipped:

> Even if there are no variances, please complete the July EPE Reconciliation sheet going forward.
[williams-w3/sent_items/417]

Code's estimate puts the handling time this removes at 1.2 hours a month, worth $100/month ($1,200/year) at $85/hour. The main value is catching revenue errors during the shift instead of at PMA time [williams-w3/sent_items/442].

## What the job produces

1. **Exception list**, emailed to the real-time desk distribution. For each flow date, book (for example ST-WBOM, ECTRT) and hour ending, it lists:
   - hours where the book is not flat in position manager;
   - CAPS schedules with no matching Enpower deal, and Enpower deals with no schedule (matched on schedule ID or deal number);
   - possible duplicate deals (same book, counterparty, hours and MW entered twice);
   - price or MW differences between Enpower, CAPS and the EPE schedules sheet.
2. **EPE Reconciliation sheet row** for the shift, filled in automatically and including a dated "no variances" line when nothing is found, so Houston can see the check ran.
3. **Correction log** with deal number, field, old value, new value and who corrected it, shared with deal control and settlements.

The report header lists which sources and books it loaded. If a source or book is missing, treat the whole report as incomplete.

## What the shift trader does

1. **Open the exception list before you hand off the shift.** Check the header: Enpower, CAPS, position manager and the EPE schedules must all be loaded.
2. **Work each exception and decide the fix yourself.** The report flags problems but never changes a deal. Typical fixes:
   - Missing imbalance purchase or sale: enter it in Enpower under the right book [williams-w3/sent_items/392].
   - Generation deviation the desk is taking on: enter the purchase and email the schedulers with the allocation [williams-w3/sent_items/425].
   - Duplicate entry: zero out the extra deal [williams-w3/sent_items/453].
   - Schedule entered wrongly by the CISO or a counterparty: send the CAPS manual-entry correction and call the outside party [williams-w3/sent_items/510], [williams-w3/inbox/126].
3. **Mark each exception as fixed or explained** so it goes into the correction log. Expected noise, such as an NP/SP load shift while both systems are flat, gets "explained":

> Finally there is a variance for HE 17 and HE 18 possibly because of load shift from NP to SP.
[williams-w3/sent_items/425]

4. **Hand off anything still open** to the real-time lead by name in the shift email.

## What the lead does the next morning

1. Read the pre-DPR run for the previous flow date. Any exception that is still open goes to deal control. For example:

> Pacificorp deal #694155 is not in for those hours.
[williams-w3/sent_items/373]

2. Confirm that every shift has an EPE Reconciliation sheet row.
3. When settlements raises a PMA or annuity question, check the correction log first and send the logged deal number, hours and values before asking for a meeting [williams-w3/sent_items/441].

## Exceptions and what stays manual

- **Placeholder deals** (counterparty "New") are flagged but not treated as errors until the trader confirms the counterparty [williams-w3/sent_items/499].
- **Book mapping mismatches** (for example schedules that belong under ECTSTSW rather than ECTRT [williams-w3/sent_items/510]) go to the lead so the mapping table can be updated. Do not "fix" the deal.
- **PMAs and annuities** are still agreed with settlements and risk, with the usual sign-off.
- **Report did not arrive or a source is missing:** run the manual CARP and fill in the EPE Reconciliation sheet by hand, as before, and tell the lead.

## Rollout

The pilot covers ST-WBOM only. For the first month the report runs alongside the manual CARP and reconciliation sheet, and the desk tracks false positives. Tolerances are tightened before more books are added.
