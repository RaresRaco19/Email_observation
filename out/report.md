# Automation opportunities

Read 3,240 files (3,201 unique messages after removing 39 duplicates, 2,535 threads). Labeled 3,201 messages; 21 quotes failed verification and were dropped.

**Total: $810/month ($9,720/year), 9.5 hours/month** at $85/h, assuming 60% of handling time is automatable.

Ships every process with at least 8 verified quotes in at least 3 threads; 0 had too little evidence. Monthly rates use the period the involved mailboxes were observed. The top 8 by $/month are shown and totalled, and each gets a solution design plus a draft built on it (an automation, or the rollout of a quick win). Solution designs are in `solutions.md`.

| # | Process | Remedy | Msgs | /month | Median min | Hours/mo | $/mo | Draft |
|---|---|---|---|---|---|---|---|---|
| 1 | Missing or expired deal tickets for metered flow | Automation | 311 | 12.04 | 20 | 2.4 | $205 | artifacts/meter_flow_missing_deal_resolution.md |
| 2 | Real-time desk position and procedure instructions | Quick win | 81 | 8.95 | 15 | 1.3 | $114 | artifacts/realtime_desk_instructions.md |
| 3 | Weekly California Capacity Report | Automation | 17 | 2.87 | 45 | 1.3 | $110 | artifacts/california_capacity_weekly_report.md |
| 4 | Real-time deal entry and position variance reconciliation | Automation | 53 | 5.86 | 20 | 1.2 | $100 | artifacts/realtime_deal_variance_reconciliation.md |
| 5 | Meter volume and allocation variance resolution | Automation | 111 | 4.29 | 25 | 1.1 | $91 | artifacts/meter_volume_allocation_variance.md |
| 6 | Deal book transfers and booking corrections | Quick win | 96 | 4.8 | 20 | 1.0 | $82 | artifacts/deal_book_transfer_correction.md |
| 7 | Deal price and invoice discrepancy resolution | Automation | 101 | 3.69 | 20 | 0.7 | $63 | artifacts/deal_price_invoice_discrepancy.md |
| 8 | Trading book, curve and system access setup | Quick win | 71 | 3.55 | 15 | 0.5 | $45 | artifacts/trading_book_setup_access.md |

## 1. Missing or expired deal tickets for metered flow

Volume management, settlements or schedulers find gas flowing at a meter with no valid Sitara deal (missing, expired, wrong counterparty) and ask the deal owner to create, extend or correct the ticket, or approve a write-off to unaccounted-for gas.

*Automation:* A daily job compares allocated meter volumes against active Sitara deal tickets and flags each meter with flow but no matching or unexpired deal, pre-filling the counterparty, meter, month and volume into a request to the deal owner. The deal owner still decides whether to extend, create a new deal, or sign off a write-off to unaccounted-for gas.

*Arithmetic:* 311 messages / 25.84 months observed (farmer-d, giron-d) = 12.04/month; x 20 min median handling x 60% automatable = 2.4 h/month; x $85/h = $205/month

Evidence:
- `farmer-d/logistics/590` (1999-12-15, howard.camp@enron.com): "Sitara Deal 92943 for meter 1431 has expired on Oct 31, 1999 .  Settlements 
is unable to draft an invoice for this deal."
- `farmer-d/logistics/591` (1999-12-15, aimee.lannou@enron.com): "Could you please resolve this issue for Howard?  I will be out of the office 
the next two days."
- `farmer-d/logistics/596` (1999-12-16, stella.morris@enron.com): "deal 96731 is not in CPR for 6/98 or OSS.  Please enter deal for 
sale on contract 078-15631-102 for 17,462 MMBTU."
- `farmer-d/logistics/606` (1999-12-21, jackie.young@enron.com): "has flow for every day this month but no K."
- `farmer-d/logistics/623` (1999-12-28, david.baumbach@enron.com): "This deal will be the second part of Sitara deal #143974."

## 2. Real-time desk position and procedure instructions

The real-time desk lead emails shift traders the hourly long and short positions to cover and standing rules for entering deals, cuts, lending and schedules in Enpower and CAPS.

*Quick win:* A standing procedures checklist for the real-time shift (deal entry in Enpower and CAPS, cuts, lending, tags) and a fixed position notice template (hub, hours, MW, price, book, deal number) are used by the desk lead, so each email follows the same structure and rules are not re-explained.

*Arithmetic:* 81 messages / 9.05 months observed (williams-w3) = 8.95/month; x 15 min median handling x 60% automatable = 1.3 h/month; x $85/h = $114/month

Evidence:
- `williams-w3/sent_items/512` (2001-06-12, bill.williams@enron.com): "We are long 25 mws in NP-15 at $54 for HE 7-22.  This is under the ST-WBOM line in CAPS."
- `williams-w3/sent_items/506` (2001-06-13, bill.williams@enron.com): "We must check out with BPA each hour for Frontier and GCPUD."
- `williams-w3/sent_items/502` (2001-06-14, bill.williams@enron.com): "We have 25 mws of length in the BOM book at $56 again for 06/14/01 on peak."
- `williams-w3/sent_items/496` (2001-06-15, bill.williams@enron.com): "We are long 25 mws 7-22 on Monday in SP-15 at $65. Deals should be under ST-WBOM."
- `williams-w3/sent_items/487` (2001-06-19, bill.williams@enron.com): "These schedule changes must be called in.  Just a reminder."

## 3. Weekly California Capacity Report

Commercial staff compile and email a weekly report of Transwestern and El Paso California deliveries, utilization and posted Gas Daily prices.

*Automation:* A weekly scheduled job pulls the delivery, utilization and Gas Daily price figures and generates the California Capacity Report in the existing format for distribution. An analyst only reviews the draft and adds commentary before it is sent.

*Arithmetic:* 17 messages / 5.92 months observed (lokay-m) = 2.87/month; x 45 min median handling x 60% automatable = 1.3 h/month; x $85/h = $110/month

Evidence:
- `lokay-m/inbox/10` (2001-10-26, michelle.lokay@enron.com): "Friday's posted Gas Daily prices:"
- `lokay-m/sent_items/18` (2001-12-14, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 1122 MMBtu/d (103%), with San Juan lateral throughput at 844 MMBtu/d."
- `lokay-m/sent_items/67` (2001-12-21, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 1059 MMBtu/d (97%), with San Juan lateral throughput at 839 MMBtu/d."
- `lokay-m/sent_items/63` (2001-12-28, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 959 MMBtu/d (88%), with San Juan lateral throughput at 827 MMBtu/d."
- `lokay-m/sent_items/55` (2002-01-04, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 840 MMBtu/d (77%), with San Juan lateral throughput at 829 MMBtu/d."

## 4. Real-time deal entry and position variance reconciliation

Real-time staff find mismatches between Enpower, CAPS, position manager, schedule sheets and EPE schedules, then correct deals, annuities and prior month adjustments with deal control and settlements.

*Automation:* An end-of-shift comparison of Enpower deals against CAPS schedules and position manager lists every hour and book that is not flat or has a missing deal. The shift trader still decides the correction and enters it.

*Arithmetic:* 53 messages / 9.05 months observed (williams-w3) = 5.86/month; x 20 min median handling x 60% automatable = 1.2 h/month; x $85/h = $100/month

Evidence:
- `williams-w3/sent_items/514` (2001-06-11, bill.williams@enron.com): "Harbor and Martel were declined with the CISO for 06/08/01 HE 1 and HE 2."
- `williams-w3/sent_items/510` (2001-06-12, bill.williams@enron.com): "There should be a 25 mw n-firm export for HE 7-10 and HE 13-22."
- `williams-w3/sent_items/501` (2001-06-14, bill.williams@enron.com): "It should be $295 for HE 15-17 and $290 for HE 18-19.  I have checked Enpower and the sheet to make sure that they reflect these changes."
- `williams-w3/sent_items/499` (2001-06-14, bill.williams@enron.com): "The CP "New" represents a counterparty as yet to be determined."
- `williams-w3/sent_items/481` (2001-06-20, bill.williams@enron.com): "I spoke with Chris and he is on board with the annuity of $18750 from ST-CALI to ST-WHOURLY."

## 5. Meter volume and allocation variance resolution

Logistics and volume management reconcile differences between nominated, metered, allocated and counterparty-reported volumes at meters, and reallocate or correct volumes before the month is finalized.

*Automation:* When meter statements, actuals notices or allocation data arrive, a comparison against nominations and POPS/Sitara allocations produces a variance list by meter and day, above a tolerance. Logistics staff still investigate the flagged meters and decide on reallocation, overrides or paybacks.

*Arithmetic:* 111 messages / 25.86 months observed (farmer-d, williams-w3) = 4.29/month; x 25 min median handling x 60% automatable = 1.1 h/month; x $85/h = $91/month

Evidence:
- `williams-w3/inbox/142` (undated, clem.cernosek@enron.com): "Volumes tie to the
scheduled quantity except for the 14th, which I am still working through with
the operator."
- `farmer-d/logistics/581` (1999-12-14, lauri.allen@enron.com): "Please make sure these volumes are moved off the Reliant contract prior to November close."
- `farmer-d/logistics/582` (1999-12-14, anita.luong@enron.com): "We need to resolve this as soon as possible so Settlement can send out payments."
- `farmer-d/logistics/583` (1999-12-14, howard.camp@enron.com): "These were buybacks that were incorrectly nominated to transport contracts"
- `farmer-d/logistics/595` (1999-12-16, stella.morris@enron.com): "There wasn't any deal in 
OSS for the above reference meter, nor could I find anything in CPR."

## 6. Deal book transfers and booking corrections

Credit, risk, settlements and other offices ask the book administrator to move deals between trading books (including bankruptcy and Canadian books) or fix counterparty, price or book on booked deals, then confirm completion.

*Quick win:* A structured request template (deal numbers, current book, target book or field change, reason, deadline, requester) is used by credit, risk and settlements staff whenever they ask for a book move or booking correction. The book administrator works from one consistent list and replies with a standard completion confirmation.

*Arithmetic:* 96 messages / 19.99 months observed (giron-d) = 4.80/month; x 20 min median handling x 60% automatable = 1.0 h/month; x $85/h = $82/month

Evidence:
- `giron-d/sent/763` (2000-06-19, darron.giron@enron.com): "you recognized 3.975 (thousand) of orig, and I did not see that coming out of any book. Could you let me know who granted that."
- `giron-d/sent/762` (2000-06-19, darron.giron@enron.com): "Can you update for transport? Sitara #131389 (North Shore) and #131405 (Peoples). Thanks."
- `giron-d/sent/724` (2000-07-28, darron.giron@enron.com): "Could you please make sure that this deal was really done with Dynegy Eenrgy 
Resources, Limited in EOL."
- `giron-d/sent/721` (2000-07-31, darron.giron@enron.com): "The new exchange deals for the EMW Park & Loan are 350499 and 350511."
- `giron-d/sent/710` (2000-08-10, darron.giron@enron.com): "Manually rebook every EOL deal that fails - If you have trouble doing this, 
just let me know and I'll follow up."

## 7. Deal price and invoice discrepancy resolution

Settlements and counterparties raise price, volume or fee mismatches between invoices or payments and Sitara deal tickets; logistics verifies the deal, disputes the invoice or corrects the deal.

*Automation:* When a counterparty invoice or payment is received, its price and volume lines are matched against the Sitara deal ticket for that month and mismatches are routed to the deal owner with both values side by side. The deal owner still decides whether the deal or the invoice is wrong and confirms the correction.

*Arithmetic:* 101 messages / 27.38 months observed (farmer-d, giron-d, lokay-m, williams-w3) = 3.69/month; x 20 min median handling x 60% automatable = 0.7 h/month; x $85/h = $63/month

Evidence:
- `farmer-d/logistics/601` (1999-12-21, kenneth.seaman@enron.com): "BMC bought 20,000 from us and intended no swing and no buyback."
- `farmer-d/logistics/604` (1999-12-21, julie.meyers@enron.com): "I wanted to update you on those Phillips deals that the counterparty is"
- `farmer-d/logistics/621` (1999-12-28, stella.morris@enron.com): "Daren is there a deal in CPR which may not have fed over to OSS?"
- `farmer-d/logistics/622` (1999-12-28, stella.morris@enron.com): "Daren is there a deal in CPR which may not have fed over to OSS?"
- `farmer-d/logistics/629` (1999-12-29, charlotte.hawkins@enron.com): "I have an error for Transco Bammel for that 20.0/day on days 23 through 27"

## 8. Trading book, curve and system access setup

Requests to create trading books, curves, portfolio and product mappings, and user access in Tagg, Sitara, TDS and EOL for traders and desks, relayed to system administrators.

*Quick win:* A single book and access request template captures book name, region, trader, curve and pipe mappings, systems needed (Tagg, Sitara, TDS, EOL) and approver. Desk staff fill it in before contacting the book administrators, so requests stop bouncing back for missing details.

*Arithmetic:* 71 messages / 19.99 months observed (giron-d) = 3.55/month; x 15 min median handling x 60% automatable = 0.5 h/month; x $85/h = $45/month

Evidence:
- `giron-d/sent/786` (2000-06-08, darron.giron@enron.com): "Tagg
IM-CENT-MID
INTRA-CNT-GULF
INTRA-NGPL-STRG
INTRA-CNT-MKT
INTRA-CNT-MKT2
INTRA-PARKLOAN
INTRA-GD-TRANS"
- `giron-d/sent/784` (2000-06-08, darron.giron@enron.com): "IM-CENT-MID INTRA-CNT-GULF INTRA-NGPL-STRG INTRA-CNT-MKT INTRA-CNT-MKT2 INTRA-CNT-TRANS INTRA-PARKLOAN INTRA-GD-TRANS"
- `giron-d/sent/778` (2000-06-13, darron.giron@enron.com): "We need to break out our Midcon region into two separate books starting with July production."
- `giron-d/sent/777` (2000-06-13, darron.giron@enron.com): "I need to make sure that all necessary pipes are mapped to these business units in order for traders to be able to book deals on them."
- `giron-d/sent/776` (2000-06-13, darron.giron@enron.com): "it might be easier to allow the two books to have deals on any Central pipe."

## Below the top 8 (not totalled)

| # | Process | Remedy | Msgs | Hours/mo | $/mo |
|---|---|---|---|---|---|
| 9 | Daily P&L, position report and book close | Quick win | 42 | 0.4 | $36 |
| 10 | Gas nomination intake and change processing | Automation | 103 | 0.4 | $34 |
| 11 | Audit, valuation and curve validation data requests | Quick win | 30 | 0.3 | $26 |
| 12 | Monthly activity and hours surveys | Quick win | 23 | 0.3 | $24 |
| 13 | CAISO congestion revenue reconciliation | Automation | 17 | 0.3 | $24 |
| 14 | Pipeline and OBA imbalance reconciliation | Automation | 21 | 0.2 | $20 |
| 15 | Credit report rebook processing | Automation | 59 | 0.1 | $13 |
| 16 | CAISO market notice relay to the real-time desk | Automation | 22 | 0.1 | $10 |
| 17 | Pipeline outage and shut-in notice handling | Quick win | 18 | 0.1 | $6 |
| 18 | Transport contract amendment requests | Quick win | 18 | 0.1 | $6 |

## Quotes that failed verification

These labels were dropped because their quote is not a verbatim substring of the raw file.

- `farmer-d/logistics/161` (pipeline_imbalance_resolution): quote not found verbatim in raw file
- `farmer-d/logistics/199` (deal_volume_without_deal_resolution): quote has 4 words (need 5-60)
- `farmer-d/logistics/1998` (deal_inquiry_followup_chase): quote has 4 words (need 5-60)
- `farmer-d/logistics/2025` (nomination_flow_change_coordination): quote has 4 words (need 5-60)
- `farmer-d/logistics/2027` (missing_deal_creation_request): quote not found verbatim in raw file
- `farmer-d/logistics/2111` (deal_ticket_setup_request): quote has 2 words (need 5-60)
- `farmer-d/logistics/615` (daily_nomination_file_receipt): quote has 4 words (need 5-60)
- `farmer-d/logistics/627` (pipeline_nomination_notice_processing): quote has 4 words (need 5-60)
- `farmer-d/logistics/628` (nomination_flow_change_coordination): quote has 4 words (need 5-60)
- `farmer-d/logistics/688` (daily_nomination_file_receipt): quote has 4 words (need 5-60)
- `farmer-d/logistics/716` (counterparty_nomination_actuals_notice): quote has 4 words (need 5-60)
- `farmer-d/logistics/764` (nomination_change_relay): quote has 4 words (need 5-60)
- `farmer-d/logistics/96` (deal_price_discrepancy_resolution): quote not found verbatim in raw file
- `giron-d/inbox/37` (deal_book_reassignment_request): quote not found verbatim in raw file
- `giron-d/inbox/62` (eol_product_trader_book_mapping): quote has 4 words (need 5-60)
- `giron-d/sent/15` (trading_book_setup_and_access_admin): quote has 3 words (need 5-60)
- `giron-d/sent/362` (deal_book_reassignment_fix): quote has 4 words (need 5-60)
- `giron-d/sent/392` (schedule_c_release_notification): quote has 4 words (need 5-60)
- `giron-d/sent/399` (schedule_c_release_notification): quote has 4 words (need 5-60)
- `giron-d/sent/569` (pricing_curve_setup_request): quote has 4 words (need 5-60)
- `williams-w3/sent_items/406` (realtime_desk_deal_entry_instructions): quote has 4 words (need 5-60)
