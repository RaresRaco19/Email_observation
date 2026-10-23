---
opportunity: deal_price_invoice_discrepancy
type: email
citations: [farmer-d/logistics/922, farmer-d/logistics/177, farmer-d/logistics/963, giron-d/sent/636]
---

**To:** Logistics desk lead; Sitara deal desk
**Subject:** Proposal: flag deal price and invoice mismatches automatically, with a case for the trader

Hello,

**The problem.** Settlements and accounting find mismatches by hand, then email the trader and wait. A typical request:

> We have HSC -0.05 and Mitchell shows HSC - 0.04.
[farmer-d/logistics/922]

When the trader of record is away, the invoice still has to go out:

> I think Daren is out for the remainder of the day and I need to send out my invoice this afternoon.
[farmer-d/logistics/177]

Sometimes the counterparty does not show the deal at all:

> Pat Dresner (accountant) at Midcon Texas says she does not show these deals
[farmer-d/logistics/963]

Sometimes the price in Sitara was never updated for the month:

> The Sitara was not updated for Aug.  I just corrected Sitara.  So you can
[giron-d/sent/636]

Across the four mailboxes we see 127 messages in 96 threads, about 4.64 a month. 53 of them are flagged as stalls.

**The fix.** Settlements drops each counterparty statement or invoice extract into a shared intake template (deal number, production month, days, point, volume, price). A matching job compares each line with the Sitara deal price and volume. It flags lines that differ, lines with no matching deal, and deals with a zero or missing price. Each flag becomes a case for the creating trader, with a named backup, showing both figures and the due date. The trader answers once: Sitara is correct (dispute), or the counterparty is correct (correct the deal). A correction sends settlements a ready-to-redraft notice for Unify. Open cases near their due date escalate to the backup.

**The value.** The model gives 0.9 hours a month saved, which is $79 a month ($948 a year) at $85 an hour. This is small, so build cost must stay low: reuse existing extracts and spreadsheets, not a new application. The larger benefit is fewer invoices stuck waiting on one trader.

**What stays manual.** Deciding which price is contractually correct, approving Sitara changes and invoice disputes, exchange-versus-term deal disputes, penalty or capacity conditions, and contacting the counterparty's trader or accountant.

**What I need from you.**
1. A read-only extract of Sitara deal tickets (deal number, counterparty, price, volume, creating trader). Please confirm these fields exist, since the emails do not.
2. Agreement from settlements on the intake template and the tolerances that count as a mismatch. Start loose.
3. A primary and backup trader roster per desk.

**Plan.** Pilot for one production month on the top counterparties, alongside the current email process. Compare flagged lines with the discrepancies raised by email, then tune the tolerances. Success measure: median hours from a case being raised to trader confirmation, and the share of mismatched lines still open on their due date.

Please reply if you will sponsor the pilot.

Thank you
