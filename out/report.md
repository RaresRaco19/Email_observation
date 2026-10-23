# Automation opportunities

Read 3,240 files (3,201 unique messages after removing 39 duplicates, 2,535 threads). Labeled 3,201 messages; 44 quotes failed verification and were dropped.

**Total: $661/month ($7,932/year), 7.8 hours/month** at $85/h, assuming 60% of handling time is automatable.

Ships every process with at least 8 verified quotes in at least 3 threads; 0 had too little evidence. Monthly rates use the period the involved mailboxes were observed. The top 8 by $/month are shown and totalled, and each gets a solution design plus a draft built on it (an automation, or the rollout of a quick win). Solution designs are in `solutions.md`.

| # | Process | Remedy | Msgs | /month | Median min | Hours/mo | $/mo | Draft |
|---|---|---|---|---|---|---|---|---|
| 1 | Meter flow with missing or expired deal resolution | Automation | 260 | 10.81 | 20 | 2.2 | $184 | artifacts/meter_flow_missing_deal_resolution.md |
| 2 | Deal price and invoice discrepancy resolution | Automation | 127 | 4.64 | 20 | 0.9 | $79 | artifacts/deal_price_invoice_discrepancy.md |
| 3 | Real-time congestion and deal settlement reconciliation | Automation | 55 | 6.08 | 15 | 0.9 | $77 | artifacts/realtime_settlement_reconciliation.md |
| 4 | Real-time desk standing procedures | Quick win | 54 | 5.97 | 15 | 0.9 | $76 | artifacts/realtime_desk_instructions.md |
| 5 | Weekly California capacity report | Automation | 17 | 2.87 | 30 | 0.9 | $73 | artifacts/california_capacity_weekly_report.md |
| 6 | Meter volume and allocation variance resolution | Automation | 94 | 3.64 | 20 | 0.7 | $62 | artifacts/meter_volume_allocation_variance.md |
| 7 | Sitara deal ticket entry and correction requests | Quick win | 117 | 4.53 | 15 | 0.7 | $58 | artifacts/sitara_deal_ticket_change_request.md |
| 8 | Real-time position and shift handoff | Quick win | 37 | 4.09 | 15 | 0.6 | $52 | artifacts/realtime_shift_position_handoff.md |

## 1. Meter flow with missing or expired deal resolution

Logistics and volume management find gas flowing at a meter with no deal, an expired deal or volumes on the strangers gas contract, and chase the deal owner to create or extend a Sitara ticket or approve a write-off to unaccounted-for gas.

*Automation:* A daily job compares metered and allocated volumes by meter against active Sitara deal tickets and flags flow with no deal, an expired term or a strangers gas assignment. It routes each exception to the deal owner on record with the meter, dates and volumes already filled in. The deal owner still decides whether to extend, create a deal or sign off a write-off to unaccounted-for gas.

*Arithmetic:* 260 messages / 24.06 months observed (farmer-d) = 10.81/month; x 20 min median handling x 60% automatable = 2.2 h/month; x $85/h = $184/month

Evidence:
- `farmer-d/logistics/585` (1999-12-14, mandy.mackinnon@enron.com): "We need a method to accomodate the volume flow on HPL at meter 415 and 9643."
- `farmer-d/logistics/590` (1999-12-15, howard.camp@enron.com): "Settlements is unable to draft an invoice for this deal. This deal either needs to be extended or a new deal needs to be set up."
- `farmer-d/logistics/591` (1999-12-15, aimee.lannou@enron.com): "Could you please resolve this issue for Howard? I will be out of the office the next two days."
- `farmer-d/logistics/596` (1999-12-16, stella.morris@enron.com): "deal 96731 is not in CPR for 6/98 or OSS.  Please enter deal for sale on contract 078-15631-102 for 17,462 MMBTU."
- `farmer-d/logistics/606` (1999-12-21, jackie.young@enron.com): "has flow for every day this month but no K."

## 2. Deal price and invoice discrepancy resolution

Settlements, accounting or counterparties report a price or volume mismatch between an invoice, a payment and the booked deal, and the desk verifies, disputes or corrects the deal so the invoice can be finaled.

*Automation:* When invoices or counterparty statements arrive, a match against the Sitara deal price and volume flags each line that differs and opens a case with the deal number, both figures and the trader. The trader still confirms which price is correct and approves any deal change or invoice dispute.

*Arithmetic:* 127 messages / 27.38 months observed (farmer-d, giron-d, lokay-m, williams-w3) = 4.64/month; x 20 min median handling x 60% automatable = 0.9 h/month; x $85/h = $79/month

Evidence:
- `farmer-d/logistics/582` (1999-12-14, anita.luong@enron.com): "We need to resolve this as soon as possible so Settlement can send out payments."
- `farmer-d/logistics/629` (1999-12-29, charlotte.hawkins@enron.com): "I have an error for Transco Bammel for that 20.0/day on days 23 through 27"
- `farmer-d/logistics/677` (2000-01-12, aimee.lannou@enron.com): "Meter 1517, Sweeny Phillips, has been reallocated for 12/99."
- `farmer-d/logistics/681` (2000-01-12, kristen.hanson@enron.com): "I spoke with Ricky Archer at Calpine about some penalty charges I billed him for undertakes on Dec 20, 21, 31."
- `farmer-d/logistics/753` (2000-02-04, lauri.allen@enron.com): "I cannot for the life of me remember why this sale deal is in there."

## 3. Real-time congestion and deal settlement reconciliation

The real-time desk reconciles Enpower deals, congestion revenue, annuities and prior-month adjustments against CAPS, inc sheets and settlement flashes, and chases corrections before the P&L flash.

*Automation:* A daily comparison of Enpower deals and congestion awards against CAPS and settlement data lists variances by hour and book. Settlements and the real-time desk still decide on the correcting entry or PMA.

*Arithmetic:* 55 messages / 9.05 months observed (williams-w3) = 6.08/month; x 15 min median handling x 60% automatable = 0.9 h/month; x $85/h = $77/month

Evidence:
- `williams-w3/sent_items/514` (2001-06-11, bill.williams@enron.com): "Harbor and Martel were declined with the CISO for 06/08/01 HE 1 and HE 2."
- `williams-w3/sent_items/510` (2001-06-12, bill.williams@enron.com): "For HE 11 and HE12, Danielle at the CISO misentered our schedule."
- `williams-w3/sent_items/481` (2001-06-20, bill.williams@enron.com): "I spoke with Chris and he is on board with the annuity of $18750 from ST-CALI to ST-WHOURLY."
- `williams-w3/sent_items/453` (2001-06-29, bill.williams@enron.com): "We had some double deal-entry last night under the ST-WBOM book. Consequently I zeroed the following deals out this morning after receiving the DPR and running a BOM SAR."
- `williams-w3/sent_items/442` (2001-07-03, bill.williams@enron.com): "The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753). Remember, this deal was originally input as a buy at $320 and a sell at $30"

## 4. Real-time desk standing procedures

The real-time desk lead repeatedly emails procedures and rules on deal entry in Enpower, tags, cuts, checkouts and scheduling that shift traders must follow.

*Quick win:* A maintained real-time desk procedures checklist covering Enpower deal entry, cut handling, tags and time changes, used by shift traders at the start of each shift. The desk lead updates one document instead of re-sending instructions.

*Arithmetic:* 54 messages / 9.05 months observed (williams-w3) = 5.97/month; x 15 min median handling x 60% automatable = 0.9 h/month; x $85/h = $76/month

Evidence:
- `williams-w3/sent_items/487` (2001-06-19, bill.williams@enron.com): "These schedule changes must be called in.  Just a reminder."
- `williams-w3/sent_items/473` (2001-06-23, bill.williams@enron.com): "CAPS will be down from HE 20 through HE 1 on Saturday morning.  We will have to use workspace and run Enpower to CAPS after HE 1."
- `williams-w3/sent_items/471` (2001-06-25, bill.williams@enron.com): "I should be copied on the EES sheets, and any cut notes to volume managament, the services desk, or other traders."
- `williams-w3/sent_items/449` (2001-07-02, bill.williams@enron.com): "Remember to include CAISO export fees, Tie Meter Multipliers/import fees and grid management fees in your CAISO calculations of wheeling charges."
- `williams-w3/sent_items/444` (2001-07-02, bill.williams@enron.com): "When scheduling from BOBR to FC3 on PAC (t) be sure to just put in the POR/POD and do NOT schedule each wheel seperately."

## 5. Weekly California capacity report

Each week California deliveries, capacity utilization and Gas Daily prices are compiled and emailed to the Transwestern commercial team.

*Automation:* A scheduled job each week pulls delivery and capacity data and posted Gas Daily prices and generates the report email in the existing format. The analyst only reviews the numbers and adds commentary before sending.

*Arithmetic:* 17 messages / 5.92 months observed (lokay-m) = 2.87/month; x 30 min median handling x 60% automatable = 0.9 h/month; x $85/h = $73/month

Evidence:
- `lokay-m/inbox/10` (2001-10-26, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 945 MMBtu/d (87%), with San Juan lateral throughput at 865 MMBtu/d.  Total East deliveries averaged 525 MMBtu/d."
- `lokay-m/sent_items/18` (2001-12-14, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 1122 MMBtu/d (103%), with San Juan lateral throughput at 844 MMBtu/d."
- `lokay-m/sent_items/67` (2001-12-21, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 1059 MMBtu/d (97%), with San Juan lateral throughput at 839 MMBtu/d."
- `lokay-m/sent_items/63` (2001-12-28, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 959 MMBtu/d (88%), with San Juan lateral throughput at 827 MMBtu/d."
- `lokay-m/sent_items/55` (2002-01-04, michelle.lokay@enron.com): "Transwestern's average deliveries to California were 840 MMBtu/d (77%), with San Juan lateral throughput at 829 MMBtu/d."

## 6. Meter volume and allocation variance resolution

Staff research meter allocation exceptions, UA4 and unaccounted-for differences, bad feeds and volume mismatches between pipeline, counterparty and internal systems, then move volumes or correct allocations.

*Automation:* After each allocation run, a comparison of POPS/MOPS meter volumes, UA4 results, pipeline statements and counterparty actuals lists every meter whose numbers disagree beyond a tolerance, with the prior month for context. Analysts receive one exception list instead of piecemeal emails. Volume management still decides which number is right and whether to reallocate.

*Arithmetic:* 94 messages / 25.86 months observed (farmer-d, williams-w3) = 3.64/month; x 20 min median handling x 60% automatable = 0.7 h/month; x $85/h = $62/month

Evidence:
- `williams-w3/inbox/142` (undated, clem.cernosek@enron.com): "Volumes tie to the
scheduled quantity except for the 14th, which I am still working through with
the operator."
- `farmer-d/logistics/581` (1999-12-14, lauri.allen@enron.com): "Please make sure these volumes are moved off the Reliant contract prior to November close."
- `farmer-d/logistics/583` (1999-12-14, howard.camp@enron.com): "Zero out 012-27049-02-001 Receipt  Package Id 2666"
- `farmer-d/logistics/595` (1999-12-16, stella.morris@enron.com): "I need your help in resolving this issue.  There wasn't any deal in 
OSS for the above reference meter, nor could I find anything in CPR."
- `farmer-d/logistics/601` (1999-12-21, kenneth.seaman@enron.com): "BMC bought 20,000 from us and 
intended no swing and no buyback."

## 7. Sitara deal ticket entry and correction requests

Traders, schedulers and accounting ask the desk to create, amend, rate-change, path, split or clean up Sitara and Tagg deal tickets and confirm the deal number back.

*Quick win:* A structured request template for requesters covering deal number, counterparty, meter, dates, volume, price, book and reason for the change. The desk uses a matching confirmation reply that returns the new or changed deal number, so requests do not need clarification rounds.

*Arithmetic:* 117 messages / 25.84 months observed (farmer-d, giron-d) = 4.53/month; x 15 min median handling x 60% automatable = 0.7 h/month; x $85/h = $58/month

Evidence:
- `farmer-d/logistics/604` (1999-12-21, julie.meyers@enron.com): "we might not be getting an answer until next week on these deals."
- `farmer-d/logistics/623` (1999-12-28, david.baumbach@enron.com): "Details for the deal to be entered on Jan. 1, 2000:"
- `farmer-d/logistics/638` (1999-12-30, donald.reinhardt@enron.com): "Please establish a spot ticket for United Oil & Minerals, Inc. at meter 5053 for January."
- `farmer-d/logistics/673` (2000-01-11, mandy.mackinnon@enron.com): "There were deals left unpathed for Jan 1 (and Dec?). I brokered and nominated the obvious but we seem to have 10,000 with transport contract to move this gas on and no sale"
- `farmer-d/logistics/675` (2000-01-12, pat.clynes@enron.com): "Please take the initiative to get these things done. I am counting on you and the others (Seniors in the group) to get these things done."

## 8. Real-time position and shift handoff

The desk lead tells the shift the day's long and short positions, deals to enter and books to use, and shift operators report missed schedules and problems back.

*Quick win:* A fixed handoff template listing position by hour and hub, book, deals to key, open issues and problems from the last shift, used by the desk lead and shift operators at each handover.

*Arithmetic:* 37 messages / 9.05 months observed (williams-w3) = 4.09/month; x 15 min median handling x 60% automatable = 0.6 h/month; x $85/h = $52/month

Evidence:
- `williams-w3/sent_items/512` (2001-06-12, bill.williams@enron.com): "We are long 25 mws in NP-15 at $54 for HE 7-22.  This is under the ST-WBOM line in CAPS."
- `williams-w3/sent_items/506` (2001-06-13, bill.williams@enron.com): "We must check out with BPA each hour for Frontier and GCPUD. Please make the call right after you call EPE dispatchers"
- `williams-w3/sent_items/502` (2001-06-14, bill.williams@enron.com): "We have 25 mws of length in the BOM book at $56 again for 06/14/01 on peak.  This energy is in NP-15.  Please make deals under ST-WBOM."
- `williams-w3/sent_items/496` (2001-06-15, bill.williams@enron.com): "We are long 25 mws 7-22 on Monday in SP-15 at $65. Deals should be under ST-WBOM."
- `williams-w3/sent_items/466` (2001-06-27, bill.williams@enron.com): "We are long 25 mws on peak for 06/27/01 in SP-15.  This should be in CAPS under ST-WBOM, deals should be under ST-WBOM in Enpower as well."

## Below the top 8 (not totalled)

| # | Process | Remedy | Msgs | Hours/mo | $/mo |
|---|---|---|---|---|---|
| 9 | Deal and counterparty book transfers | Automation | 70 | 0.5 | $46 |
| 10 | Trading book setup and system access requests | Quick win | 85 | 0.4 | $36 |
| 11 | Counterparty nomination intake and changes | Automation | 82 | 0.3 | $29 |
| 12 | Cost center surveys and allocation requests | Quick win | 22 | 0.3 | $27 |
| 13 | Transportation contract amendment approvals | Quick win | 18 | 0.3 | $26 |
| 14 | Daily P&L, position and post ID sign-off | Quick win | 40 | 0.2 | $17 |
| 15 | Pipeline operations, shut-in and outage notice relay | Automation | 42 | 0.2 | $15 |
| 16 | Deal data and audit support requests | Quick win | 31 | 0.2 | $15 |
| 17 | Pipeline and OBA imbalance reconciliation | Automation | 17 | 0.1 | $11 |
| 18 | CAISO market notice relay | Automation | 15 | 0.1 | $7 |
| 19 | Credit report distribution and rebooking | Automation | 49 | 0.1 | $6 |

## Quotes that failed verification

These labels were dropped because their quote is not a verbatim substring of the raw file.

- `farmer-d/logistics/1107` (deal_price_discrepancy_resolution): quote has 3 words (need 5-60)
- `farmer-d/logistics/1160` (sitara_deal_ticket_correction): quote has 4 words (need 5-60)
- `farmer-d/logistics/1369` (daily_flow_and_nomination_monitoring): quote not found verbatim in raw file
- `farmer-d/logistics/1409` (cost_center_allocation_reporting): quote not found verbatim in raw file
- `farmer-d/logistics/1423` (nomination_change_processing): quote has 4 words (need 5-60)
- `farmer-d/logistics/161` (pipeline_imbalance_reconciliation): quote not found verbatim in raw file
- `farmer-d/logistics/1998` (stale_request_followup): quote has 4 words (need 5-60)
- `farmer-d/logistics/2025` (customer_nomination_intake): quote has 4 words (need 5-60)
- `farmer-d/logistics/2033` (meter_volume_missing_deal_resolution): quote has 2 words (need 5-60)
- `farmer-d/logistics/2081` (sitara_deal_ticket_correction): quote has 3 words (need 5-60)
- `farmer-d/logistics/2111` (deal_ticket_setup_request): quote has 2 words (need 5-60)
- `farmer-d/logistics/615` (daily_flow_and_nomination_monitoring): quote has 4 words (need 5-60)
- `farmer-d/logistics/627` (daily_operations_notice_handling): quote has 4 words (need 5-60)
- `farmer-d/logistics/628` (customer_nomination_intake): quote has 4 words (need 5-60)
- `farmer-d/logistics/685` (nomination_intake_and_confirmation): quote has 4 words (need 5-60)
- `farmer-d/logistics/688` (daily_flow_and_nomination_monitoring): quote has 4 words (need 5-60)
- `farmer-d/logistics/716` (daily_nomination_actuals_distribution): quote has 4 words (need 5-60)
- `farmer-d/logistics/764` (nomination_change_processing): quote has 4 words (need 5-60)
- `farmer-d/logistics/767` (nomination_intake_and_confirmation): quote has 3 words (need 5-60)
- `farmer-d/logistics/90` (deal_price_invoice_discrepancy): quote not found verbatim in raw file
- `farmer-d/logistics/955` (counterparty_nomination_processing): quote has 4 words (need 5-60)
- `farmer-d/logistics/96` (deal_price_invoice_discrepancy): quote not found verbatim in raw file
- `giron-d/inbox/55` (deal_book_correction_and_transfer): quote has 2 words (need 5-60)
- `giron-d/inbox/62` (eol_product_trader_book_mapping): quote has 4 words (need 5-60)
- `giron-d/sent/11` (credit_report_counterparty_action_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/129` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `giron-d/sent/165` (daily_credit_report_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/171` (daily_credit_report_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/218` (credit_report_counterparty_action_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/253` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `giron-d/sent/258` (month_end_last_day_file): quote has 3 words (need 5-60)
- `giron-d/sent/260` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `giron-d/sent/28` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `giron-d/sent/41` (credit_report_counterparty_action_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/67` (credit_report_counterparty_action_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/76` (daily_credit_report_forwarding): quote has 3 words (need 5-60)
- `giron-d/sent/86` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `giron-d/sent/94` (credit_report_counterparty_rebooking): quote has 3 words (need 5-60)
- `williams-w3/inbox/136` (market_data_report_spreadsheet_maintenance): quote has 4 words (need 5-60)
- `williams-w3/sent_items/138` (realtime_desk_position_instructions): quote not found verbatim in raw file
- `williams-w3/sent_items/209` (realtime_desk_procedure_instructions): quote not found verbatim in raw file
- `williams-w3/sent_items/289` (realtime_desk_procedure_instructions): quote not found verbatim in raw file
- `williams-w3/sent_items/406` (realtime_desk_instructions): quote has 4 words (need 5-60)
- `williams-w3/sent_items/488` (desk_position_and_schedule_briefing): quote not found verbatim in raw file
