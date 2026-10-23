---
opportunity: deal_price_invoice_discrepancy
type: sop
citations: [farmer-d/logistics/922, farmer-d/logistics/963, farmer-d/logistics/177, giron-d/sent/636, farmer-d/logistics/2083]
---

# SOP: Deal price and invoice discrepancy queue

**Owner:** settlements lead. **Users:** settlements and volume accountants, traders and the logistics desk, deal entry.
**Value:** about $110 per month ($1,320 per year) at $85 per hour, based on a sampled 20-minute median handling time. Measure the real time during the pilot.

## What the automation produces

Counterparty statements, invoices and payments are loaded into a staging table, one row per deal, day and point. A match job compares each row with the Sitara deal ticket (price or index formula, volume, transport rate). Each difference, missing deal or zero-rate ticket becomes a case holding the deal number, both figures, the invoice due date and the trader named on the Sitara ticket. Today this arrives as a free-text email, for example:

> We have HSC -0.05 and Mitchell shows HSC - 0.04.
[farmer-d/logistics/922]

## Daily routine

1. **Load.** Accountants upload each new statement, invoice or remittance with the upload template. Required fields are deal number, production month, day, point, volume and price. If the statement has no deal number, the job matches on counterparty, point and month.
2. **Pre-invoice run.** In the days before invoices go out each production month, the scheduled run flags zero-rate tickets and months with no price entered, so stale prices are fixed before the invoice rather than after. In the Agave case Sitara was not updated and the Unify invoice was redrafted afterward:
> The Sitara was not updated for Aug. I just corrected Sitara. So you can redraft in Unify.
[giron-d/sent/636]
3. **Review the queue.** The settlements lead opens the daily aging list, sorted by invoice due date. Work the cases due soonest first.
4. **Trader decision.** The trader picks one of three answers:
   - Sitara correct: settlements send the dispute record to the counterparty.
   - Counterparty correct: the form produces a prefilled Sitara change request for deal entry. After deal entry makes the change, settlements get a redraft notice and redraft in Unify.
   - Dispute: the trader takes it to the counterparty.
5. **Backup.** Each desk has a named backup. If the trader is out, the case goes to the backup at once. The accountant should not have to write what one did here:
> I think Daren is out for the remainder of the day and I need to send out my invoice this afternoon.
[farmer-d/logistics/177]
6. **Close.** The case closes when the corrected invoice is sent or the dispute is recorded.

## What a person checks

- Each flagged case before it goes out. Tolerances are agreed with settlements. If traders mark many cases "Sitara correct", the tolerance is too tight and the lead adjusts it.
- Index prices such as HSC minus a differential. The job compares the formula and the differential. If it cannot resolve the index, it flags the case for a person.
- Any email that still arrives from a trader or accountant. The settlements lead sends it back to the queue.

## Exceptions that stay manual

- **Which price is right.** Only the trader knows what was agreed.
- **Sitara changes.** Deal entry approves and keys them under existing controls.
- **Counterparty has no record of the deal.** The trader contacts the other side's trader, as in the Midcon case:
> Pat Dresner (accountant) at Midcon Texas says she does not show these deals
[farmer-d/logistics/963]
- **Disputes over what a deal covers.** Example, Texas General Land Office:
> Texas General Land office has called and is disputing that this sale is a part of the month exchange deal for transport.
[farmer-d/logistics/2083]
- **Commercial holds and penalty or imbalance charges** not tied to a single deal line.

## Measures

Median hours from discrepancy detected to trader decision, and the share of invoices redrafted in Unify after being sent, per production month before and after rollout. Run alongside the email process for one production month before switching over.
