---
opportunity: deal_price_invoice_discrepancy
type: sop
citations: [farmer-d/logistics/133, farmer-d/logistics/124, farmer-d/logistics/949, farmer-d/logistics/963, farmer-d/logistics/839, farmer-d/logistics/99, farmer-d/logistics/1488, giron-d/sent/178, giron-d/sent/636, farmer-d/logistics/965, farmer-d/logistics/2087, farmer-d/logistics/1438]
---

# SOP: Invoice-to-Sitara Discrepancy Queue

**Owner:** Gas Settlements (intake and close-out). Logistics deal owners resolve the items.
**Systems:** Sitara (deals), Unify (invoice redraft), SAP (netting and adjustments).
**Value:** about $63 per month ($756 per year) at $85 per hour. Most of the gain comes from fewer late payments and less chasing.

## Why this exists

Today a mismatch reaches logistics as an email with two numbers in it, and someone has to look both up by hand.

> For sale deal 707274, DEFS says the price on 4/4 should be 5.25 and we have 5.20 in Sitara.
[farmer-d/logistics/133]

Answers come late, so settlements has to chase them while the invoice stays open [farmer-d/logistics/99] [giron-d/sent/178]:

> I have not received a response from you regarding the pricing discrepancies on these deals.
[farmer-d/logistics/99]

## What the automation produces

1. **Matching run.** The run starts when settlements logs an invoice, payment or price statement, and it repeats every night against Sitara changes. For each line it finds the Sitara deal, compares price and volume within tolerance, and checks that every day in the range is covered by a valid deal. This is the gap check that is done by hand today [farmer-d/logistics/949].
2. **Queue item.** Each mismatch becomes one item, routed to the deal owner in Sitara. It shows the counterparty value next to the Sitara value, plus the invoice due date.
3. **Reminders and escalation.** Reminders are timed to the due date and go to the deal owner and their lead. They replace the "answer ASAP" escalation emails [farmer-d/logistics/1488].
4. **Monthly report.** Discrepancies are counted by counterparty and cause.

## Daily steps

**Gas Settlements analyst**
1. Log each counterparty line with these fields: counterparty, production month, point or meter, deal number (if given), day range, volume, price, and payment due date. Payment dates matter, for example "The 2/2000 production invoices are due to be paid 3/27" [farmer-d/logistics/963].
2. Check the line's match result. Lines that pass need nothing more.
3. Lines with **no deal found** or an **exchange-type deal** flag go into the queue. Do not bill those lines until the item is resolved. One exchange deal had to be netted in SAP after billing [farmer-d/logistics/2087].

**Logistics deal owner (mostly Daren Farmer's desk)**
4. Open the item and choose one of three options:
   - **Sitara is correct:** settlements disputes the invoice.
   - **Sitara needs correction:** fix or cut off the deal in Sitara [farmer-d/logistics/965], then resolve the item.
   - **Deal missing or another trader's deal:** name the trader. If needed, talk to the counterparty's trader [farmer-d/logistics/963].
5. Resolve before the due date. Agreeing on a rate stays the owner's call [farmer-d/logistics/839].

**Gas Settlements, on the resolution notice**
6. Redraft in Unify after the Sitara correction, as was done for the Agave price calculation [giron-d/sent/636]. Or net or adjust in SAP. Then send the corrected invoice to the counterparty [farmer-d/logistics/124].

## Exceptions (handled by a person, outside the auto-match)

- **Index-priced deals** (for example, IF plus a fee [farmer-d/logistics/124]) are flagged for review, not auto-matched.
- **Stale owner:** if the deal's trader has left, the item goes to the logistics desk lead. Old suspended payments are investigated by hand [farmer-d/logistics/1438].
- **Volume-only differences** caused by meter flow are kept in a separate list so they do not flood the price queue.
- **Counterparty does not recognize the deal:** the deal owner handles this by phone or relationship contact.

## What a person checks weekly

- Items still open as the payment due date nears.
- Items routed to the wrong owner. Fix the owner field in Sitara.
- Measures: median hours from logging to resolution, and the count of follow-up and escalation emails on price discrepancies.
