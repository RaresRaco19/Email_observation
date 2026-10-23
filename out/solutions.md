# Solution designs

One design per top opportunity: an automation, or the rollout of a quick win. Citations are message ids; quotes are verified verbatim.

## 1. Meter flow with missing or expired deal resolution

Gas regularly turns up at HPL meters with no Sitara deal, with a deal whose term has ended, or parked on Strangers Gas. Logistics, Volume Management and accounting then email Daren Farmer's desk one meter at a time to get a ticket extended or created, and the reply often takes a day or more. A daily exception job would compare allocated flow against active Sitara deal terms and send each gap to the deal owner as a pre-filled extend/create/write-off request. This removes the manual detective work and the status-chasing, worth about $184 a month ($2,208 a year) at $85/hour, and closes gaps before payment and invoicing deadlines.

**Effort:** M · **Success metric:** Number of meter/day exceptions with flow but no valid Sitara deal (or on Strangers Gas) still open at month-end close, and median days from first flow to deal extension or creation. Track the count of ad-hoc 'please extend deal' emails to the deal desk alongside these.

**How it works today**

1. An allocation or exception screen shows flow at a meter on days with no valid deal. Examples are a meter allocated since March with no volume scheduled, or flow on days outside a deal's term. (Volume Management / pipeline allocation analyst) [farmer-d/logistics/1055, farmer-d/logistics/899, farmer-d/logistics/1149]
2. The analyst looks up the Sitara deal ticket by hand, works out which days or months it does not cover, and decides who the trader or deal owner is. (Volume Management / logistics) [farmer-d/logistics/1224, farmer-d/logistics/1055, farmer-d/logistics/782]
3. To keep the volume from hanging in the exception screen, the analyst parks it on Strangers Gas or another temporary accounting arrangement. (Volume Management) [farmer-d/logistics/899]
4. The analyst emails the deal owner, usually Daren Farmer, asking for a specific deal to be extended (deal number, date and volume) or a new ticket to be created. (Volume Management / logistics / accounting) [farmer-d/logistics/1981, farmer-d/logistics/1999, farmer-d/logistics/1514, farmer-d/logistics/117]
5. If nothing comes back, requesters send status follow-ups, forward the thread to other people, or escalate. This happens most when a payment or invoice deadline is close. (logistics, accounting, settlements) [farmer-d/logistics/1485, farmer-d/logistics/130, farmer-d/logistics/782]
6. The deal owner or approver decides whether to extend the deal, create a new deal or a buy-back, or refuse/write the volume off (for example, very old or questionable volumes). Volumes are then reallocated, sometimes several times. (trader / deal owner, East desk, credit/approver) [farmer-d/logistics/1356, farmer-d/logistics/1489, farmer-d/logistics/2070, farmer-d/logistics/1972]

**Where it stalls**

- Logistics cannot finish until the deal owner answers, because the deal covers only one day of the flowing volume.
  > He will either need 
to extend the deal or maybe there should be another deal in place.
  [farmer-d/logistics/782]
- Volume waits on Strangers Gas, a temporary parking contract, until the trader replies. The requester's vacation then forces a handoff.
  > I'm going to place 98-9676 on Strangers Gas until you 
hear back from Daren or Julie.
  [farmer-d/logistics/899]
- The same meter and deal come back again because the deal term does not match the days that actually flowed.
  > There is gas out there for days 1-3 and 6-20 
but the deal is only good for 21-31.
  [farmer-d/logistics/1149]
- The analyst has to check the ticket end date by hand and find the uncovered days before asking for an extension.
  > I checked the deal ticket (286824) and it ends on 6/17.  There 
is still two more days that need to be reallocated.
  [farmer-d/logistics/1224]
- The gap was found months late, and no one was sure who should be rolling the deal.
  > it looks as though 12/99 was the last month a deal was entered 
(IF/HSC+1.00).
  [farmer-d/logistics/1055]
- The gap went undetected for so long that the approver will not create a deal without an investigation.
  > I am uncomfortable putting a deal out there without more details.
  [farmer-d/logistics/1356]
- Prior-period gaps become too old to fix in the scheduling system.
  > The East Desk was not up and 
running on Unify in June of 1999.
  [farmer-d/logistics/1489]
- Volumes are reallocated again and again between desks because deals and paths do not match actual flow.
  > We go round and round at this point 
changing volumes two, three or more times.
  [farmer-d/logistics/1972]
- A volume with no actualization blocks a supplier payment that has a hard deadline.
  > Payment MUST be set up by noon 5/24/01 for prompt payment to Spinnaker.
  [farmer-d/logistics/130]

**Proposed automation**

A daily job pulls allocated and metered volumes by meter and day, along with active Sitara deal tickets (deal number, counterparty, meter, start and end dates, trader). It finds three exception types: flow with no deal, flow on days outside a deal's term, and volume sitting on Strangers Gas. For each one it builds an exception record showing the meter, the uncovered dates and volumes, the closest existing deal (the likely deal to extend) and the deal owner on record. The record goes to that owner as one daily digest. The digest has one-click options to extend the named deal, create a new deal, or refer the volume for write-off or investigation. The requesting analyst sees the status on a shared exception list, so they don't need to send status emails. Exceptions that are still open close to month-end, or close to a payment deadline, are escalated to the desk lead. Old ones are flagged early, before they become prior-year cleanups.

- Trigger: Nightly schedule after the daily allocation load. An extra run happens on business days in the last week of the month and before settlement and payment cutoffs.
- Inputs: Daily allocated and metered volumes by meter and day (the data behind the allocation exception screen and Volume Management); Active and recently expired Sitara deal tickets: deal number, counterparty, meter, term dates, trader/deal owner; Volumes currently assigned to the Strangers Gas contract; Unify paths/nominations for the meter, to tell unscheduled flow apart from scheduled flow; Payment and settlement deadlines for counterparties with pending payments
- Outputs: Daily exception digest for each deal owner (e.g. the HPL trader desk): meter, dates, uncovered volume, suggested deal to extend; Shared exception list with status (open, extension requested, extended, new deal, referred for write-off) for Volume Management, logistics and accounting; Escalation notice to the desk lead for exceptions that are still open near month-end or a payment cutoff; Monthly aging report of exceptions older than one production month, so prior-period cleanup is visible early
- Existing systems: Sitara, Unify, Volume Management, Strangers Gas
- New components: nightly flow-vs-deal comparison job, exception record store with status tracking, meter-to-deal-owner lookup table (maintained by the desk), deal-owner daily digest email with extend / create / refer actions, shared exception list view for requesters, month-end and payment-deadline escalation rule, exception aging report

**Implementation steps**

1. Confirm read access to the allocation data behind Volume Management and to a Sitara deal extract (deal number, meter, term, trader). Use an export or report if there is no direct query.
2. Build the meter-to-deal-owner lookup from current Sitara traders. Have the desk confirm it, with a fallback owner for each pipeline or region.
3. Write the comparison job for the three exception types (no deal, outside term, Strangers Gas). Run it in report-only mode for one month against the emailed requests to check its precision.
4. Add the suggested-deal logic: the same meter and counterparty with a term that ends just before, or starts just after, the uncovered days.
5. Launch the deal-owner digest and the shared exception list. Ask Volume Management and logistics to point to the list instead of sending a new email for each meter.
6. Add escalation rules for exceptions still open near month-end close or near known payment cutoffs, plus the aging report.
7. After two production months, review the exceptions that were never resolved and tune the thresholds (for example, a minimum volume, and leaving out meters known to be measurement-only).

**Stays manual**

- Choosing between extending a deal, creating a new deal or buy-back, or refusing the volume. This is a commercial and pricing decision for the trader.
- Approving deals for old or suspicious volumes (e.g. a counterparty no longer in business, or volume found after nearly two years), which needs an investigation and approver sign-off.
- Write-offs to unaccounted-for gas, or using an OBA/PPA for small or unreliable volumes. These need a judgment on how good the data is and how much money is at stake.
- Entering or changing Unify paths for cross-desk (e.g. East desk) pieces, which need coordination between desks.
- Pricing on newly created or extended deals.

**Risks**

- The evidence does not show the actual data feeds or table structures for allocations or Sitara. Feasibility of the extract has to be confirmed before committing; plan a manual export fallback.
- Deal-owner records may be stale or ambiguous (requesters often ask who should be rolling a deal). If the lookup is not kept up to date, exceptions go to the wrong person. Mitigate with a fallback owner and a weekly 'unowned' list.
- Meter allocation data is revised after the fact, so the flags can be false or keep changing. Show the allocation date and suppress repeats until the volume changes.
- Too many small exceptions (single-day, tiny volumes) could make owners ignore the digest. Use a volume threshold and grouping by deal.
- The savings estimate (about $184/month) uses the median handling time across all messages. The real benefit depends on whether requesters actually stop sending ad-hoc emails.
- The evidence comes from one mailbox (farmer-d), so the volume handled by other desks is not visible.

## 2. Deal price and invoice discrepancy resolution

Settlements and accounting staff find by hand that a counterparty statement or invoice disagrees with the deal booked in Sitara. They then email the trader, often Daren Farmer, and wait, sometimes past the invoice deadline, for him to say which price or volume is right. The proposal is a matching job that compares incoming statement lines with Sitara deal price and volume and opens a discrepancy case for the trader of record with both figures and the due date attached. Detection becomes automatic, the trader answers in one step, and the corrected deal goes straight back to Unify for redraft. The modeled value is small, at $79 per month ($948 per year) at $85 per hour.

**Effort:** M · **Success metric:** Median hours from a discrepancy being raised to the trader's confirmation, and the share of mismatched invoice lines still unresolved on their invoice or payment due date.

**How it works today**

1. A counterparty statement, invoice or payment arrives, and a settlements or accounting analyst compares it line by line with the Sitara deal ticket, by hand. (settlements / volume accounting analyst) [farmer-d/logistics/837, farmer-d/logistics/133, farmer-d/logistics/922]
2. When the price or volume differs, or the counterparty does not recognise the deal, the analyst emails the trader who created the deal in Sitara and asks which figure is correct, often marked ASAP. (settlements analyst to trader (logistics desk)) [farmer-d/logistics/922, farmer-d/logistics/963, farmer-d/logistics/2083, farmer-d/logistics/124]
3. The trader researches the deal, or has to ask the counterparty's trader or a colleague, because the analyst cannot tell who agreed the terms. (trader) [farmer-d/logistics/837, farmer-d/logistics/963, giron-d/sent/665]
4. If the trader is unavailable or the answer is slow, the analyst chases again, escalates, or routes the change to another person so the invoice deadline is not missed. (settlements analyst) [farmer-d/logistics/1488, farmer-d/logistics/177, farmer-d/logistics/951]
5. The trader or deal desk corrects the price on the deal in Sitara, and settlements then redrafts the invoice in Unify and sends a corrected invoice. (trader / Sitara deal desk, then settlements) [giron-d/sent/636, farmer-d/logistics/124, farmer-d/logistics/177]
6. Where the disagreement involves contractual conditions or penalty charges, commercial staff hold the billing until the terms are discussed. (commercial / marketing lead) [lokay-m/sent_items/45, giron-d/sent/178]

**Where it stalls**

- The mismatch is found only after the counterparty's figures arrive, and the analyst must wait for the trader to say which price is right before paying or invoicing.
  > deal 156658.  We have HSC -0.05 and Mitchell shows HSC - 0.04.  Can you tell
  [farmer-d/logistics/922]
- The counterparty does not recognise deals that exist in Sitara, and the analyst does not know which counterparty trader to contact, so the case goes back to the trader while the payment due date approaches.
  > in her system and she can not pay on them.  You created the deals in Sitara
  [farmer-d/logistics/963]
- The deal ticket itself is incomplete (a zero rate), so research depends on someone remembering the deal.
  > a zero rate, however.  Elsa/Daren- do either of you remember this deal?
  [farmer-d/logistics/837]
- The single trader of record is out, so the analyst has to find someone else to change the price before the invoice goes out.
  > I think Daren is out for the remainder of the day and I need to send out my invoice this afternoon.
  [farmer-d/logistics/177]
- The price in Sitara was never updated for the month, so the invoice has to be redrafted downstream in Unify.
  > The Sitara was not updated for Aug.  I just corrected Sitara.  So you can
  [giron-d/sent/636]
- The counterparty pushes for an answer and the analyst can only forward the request with an ASAP flag.
  > Help .   Steve Mauch at Hesco is wanting an answer ASAP
  [farmer-d/logistics/1488]
- The counterparty disputes which deal a sale belongs to, and the trader on the other side is not known.
  > Do we have the name of the trader at Texas General Land Office that did this
  [farmer-d/logistics/2083]

**Proposed automation**

Settlements analysts drop each counterparty statement or invoice extract (deal number, production month, day range, volume, price) into a shared intake. A matching job joins each line to the Sitara deal by deal number, or by counterparty, point and month when no deal number is given. It compares price and volume within a tolerance and flags lines that differ, lines with no matching deal, and deals with a zero or missing price, such as the month-not-updated case. Each flagged line becomes a discrepancy case routed to the trader who created the deal in Sitara, with a named backup trader, and it shows both figures and the invoice or payment due date. The trader answers with one action: Sitara is correct, so dispute with the counterparty, or the counterparty is correct, so correct the deal. A deal correction notifies settlements that the line is ready to redraft in Unify, and open cases near their due date are escalated automatically to the backup.

- Trigger: Arrival of a counterparty statement, invoice or payment extract in the settlements intake, plus a daily sweep before invoice and payment due dates.
- Inputs: Counterparty statement or invoice lines: deal number, production month, days, point or meter, volume, price; Sitara deal tickets: deal number, counterparty, price or index formula, volume, trader who created the deal; Invoice and payment due dates entered by settlements; Desk roster of primary and backup trader per desk
- Outputs: Discrepancy case per mismatched line for the trader of record, with both figures and the due date; Ready-to-redraft notice to the settlements analyst once the deal is corrected or the price is confirmed; Daily open-case list with ageing for the logistics desk lead; Monthly count of discrepancies by counterparty and cause (price, volume, unknown deal, missing price)
- Existing systems: Sitara, Unify
- New components: statement intake template (spreadsheet layout settlements fill per counterparty statement), nightly and on-arrival matching job against Sitara deal price and volume, discrepancy case queue with confirm / correct / dispute actions, trader-of-record and backup routing table, due-date escalation rule, redraft-ready notification to settlements

**Implementation steps**

1. Pull a read-only extract of Sitara deal tickets (deal number, counterparty, price, volume, creating trader) and confirm the fields with the Sitara deal desk.
2. Agree with settlements (for example Megan Parker, Katherine Herrera, Tina Valadez) on a statement intake template and the price and volume tolerances that count as a mismatch.
3. Build the matching job: deal-number match first, then counterparty, point and month fallback, plus checks for zero or missing prices.
4. Build the case queue and routing table, mapping each deal's creating trader to a backup so absences do not block invoicing.
5. Add due-date escalation and the redraft-ready notice that tells settlements when to redraft in Unify.
6. Pilot for one production month on the logistics desk's top counterparties, running alongside the current email process, and compare flagged lines with the discrepancies raised by email.
7. Tune the tolerances and the fallback matching, then make the queue the standard channel and retire ad hoc price-confirm emails for covered counterparties.

**Stays manual**

- Deciding which price is contractually correct: only the trader knows what was agreed, sometimes by phone with the counterparty's trader.
- Changing a deal in Sitara and approving an invoice dispute: these remain trader or deal desk approvals.
- Disputes about whether a sale belongs to an exchange or term deal, and conditions attached to capacity releases or penalty charges, which need commercial discussion before billing.
- Contacting the counterparty's trader or accountant when they do not show the deal in their system.

**Risks**

- Counterparty statements arrive in inconsistent formats, and the evidence does not show their layout, so the intake template may need manual keying. Mitigate this by starting with the highest-volume counterparties.
- Index-based prices (for example HSC minus a differential, or IF plus an adder) need the index value to compare totals. Mitigate this by comparing the formula terms as booked rather than the computed totals.
- Sitara access, the field names, and whether the creating trader is stored on the deal are assumed and not confirmed by the emails. Verify them with the Sitara deal desk before building.
- Tolerances set too tight will flood traders with false cases. Start loose and tune during the pilot.
- The modeled value is low ($79 per month at $85 per hour), so build cost must stay small. Reuse existing extracts and spreadsheets rather than building a new application.
- Unify integration is limited to a notice. Automatic redraft is not proposed, because the evidence does not describe how redrafts are triggered.

## 3. Real-time congestion and deal settlement reconciliation

The real-time desk works out by hand, hour by hour, how Enpower deals, CISO schedules, congestion awards and PMAs differ from CAPS, the inc sheet and the DPR. It then sends one-off emails to settlements and chases the answers for days. A daily variance job would compare these sources by hour and book and open a tracked exception for each mismatch. That turns free-form chasing into a short review queue, which recovers about $77 a month ($924 a year) at $85/hour and leaves an audit trail for every PMA.

**Effort:** M · **Success metric:** Share of real-time variances and PMA questions that first appear in the daily exception queue rather than in an ad hoc email, and the median days an exception stays open before its correcting entry or PMA is booked.

**How it works today**

1. During the operating day the real-time trader deals with cuts, declines and bought-back schedules (CISO declines, El Paso Electric cuts, Harbor not running). The trader enters fixing trades such as imbalance purchases in Enpower and checks that the position is flat in CAPS position manager. (real-time trader (Bill Williams)) [williams-w3/sent_items/514, williams-w3/sent_items/425, williams-w3/sent_items/291]
2. When the CISO misenters a schedule or an import ID is wrong, the desk emails the CAPS group and its schedulers so they can fix the CAPS entry manually or change load zones. (real-time trader and CAPS scheduling group (Kit Blair, Caroline Emmert, Eugene Lee, Kourtney Nelson)) [williams-w3/sent_items/510, williams-w3/inbox/126]
3. The next morning the trader reads the DPR, runs a BOM SAR, and zeroes or corrects bad deals such as double deal-entry in ST-WBOM. The trader then emails settlements with the deal numbers and the revenue effect. (real-time trader to settlements (Heather Dunton)) [williams-w3/sent_items/453, williams-w3/sent_items/481]
4. The trader works out the expected congestion and replacement-reserve revenue by hand (MW times price per HE) and emails it to Jim Reyes and the CAPS group so the revenue gets booked. This includes hours where the CAISO site has no data. (real-time trader to real-time settlements (Jim Reyes)) [williams-w3/sent_items/322, williams-w3/sent_items/431, williams-w3/sent_items/90]
5. When a monthly PMA arrives, the trader checks it against Enpower and the inc sheet, emails the questions to Virginia Thompson, and follows up until the true-up is booked. Sometimes this needs a tape pull to settle what was traded. (real-time trader and PMA/settlements analyst (Virginia Thompson), tape room (Chip Cox)) [williams-w3/sent_items/442, williams-w3/sent_items/441, williams-w3/sent_items/426, williams-w3/sent_items/428, williams-w3/sent_items/387]

**Where it stalls**

- A price correction already sits in Enpower, but the matching revenue never reaches the book. No one catches it until the trader goes over the next month's PMA, so the true-up waits more than a month.
  > The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753).
  [williams-w3/sent_items/442]
- A PMA from January shows a volume change that the deal system and the inc sheet never recorded. The trader only finds the gap months later and has to ask for a meeting to go through it.
  > On TransAlta deal #509285, your notes indicate that mw volumes for HE 23 and HE 24 were reduced by 95 mws each hour.
  [williams-w3/sent_items/441]
- Nothing records the deal, so finding out what was traded means pulling tapes or asking traders. Meanwhile an earlier PMA question is still open.
  > We could pull tapes?  Ask the person who did the deal?  There is nothing in notebooks.  Any word on the BOM PMA?
  [williams-w3/sent_items/426]
- Double deal-entry only comes to light after the DPR and a manual BOM SAR the next morning. It is then fixed by zeroing deals and explaining excess revenue to settlements.
  > We had some double deal-entry last night under the ST-WBOM book.  Consequently I zeroed the following deals out this morning after receiving the DPR and running a BOM SAR.
  [williams-w3/sent_items/453]
- Position manager raises false variances that disappear in the detail view, so the trader has to check variances by hand and report them.
  > Position manager is also not working properly, it is reporting a variance at Pacificorp system border ? and at Palo Verde.
  [williams-w3/sent_items/291]
- Congestion revenue for an hour has no CAISO data because the CAISO server went down. The amount rests on a verbal statement over a recorded line, so it has to be chased by hand.
  > HE18-although it shows nothing from the CAISO on their site (their server went down) is the same as HE17-the CAISO specifically relayed this to me on a recorded line.
  [williams-w3/sent_items/90]
- The CISO misenters schedules, so CAPS and the actual energy flow disagree and someone has to fix CAPS by hand.
  > For HE 11 and HE12, Danielle at the CISO misentered our schedule.  CAPS shows a final of 25 mws as a firm import.
  [williams-w3/sent_items/510]

**Proposed automation**

Each morning after the DPR is published, a reconciliation job pulls the previous day's real-time deals from Enpower by book (ST-WBOM, ST-CALI, ST-WHOURLY, ECTRT, ECTSTSW). It also pulls the final schedules from CAPS and its position manager, and the CAISO congestion and replacement-reserve awards. It matches them by hour ending, schedule ID and counterparty. Every mismatch becomes an exception row with the expected value and the source of each side: a volume or direction difference, a duplicate deal, an award with no booked revenue, or a counterparty or price change that has no revenue effect. Exceptions go into a shared queue that the real-time trader and settlements (Jim Reyes, Heather Dunton, Virginia Thompson) all see, replacing the ad hoc emails. When a PMA arrives, the same job compares each PMA line with the current Enpower deal and the inc sheet, and flags lines that have no supporting change or whose sign does not match the trade. Each exception stays open, with its age and owner showing, until someone records a correcting entry or PMA, so stalled items show up on their own.

- Trigger: Daily, once the DPR for the prior flow day is available; also run on demand when a monthly PMA file is received.
- Inputs: Enpower deal records by book, hour ending, counterparty, price and volume; CAPS final schedules and position manager positions by schedule ID and hour; CAISO congestion, replacement-reserve and imbalance award data; DPR and BOM SAR output for the prior day; inc sheet entries; monthly PMA lines from settlements; annuity entries between books
- Outputs: daily variance report by hour and book for the real-time desk and the CAPS group; exception queue entries assigned to settlements, each with the expected revenue and its calculation; PMA validation report for Virginia Thompson that flags PMA lines with no matching change in Enpower or the inc sheet; aging summary of open corrections before the P&L flash
- Existing systems: Enpower, CAPS, position manager, DPR, BOM SAR, inc sheet, CAISO
- New components: daily hourly reconciliation job (Enpower vs CAPS vs CAISO awards), duplicate-deal detector by book, counterparty and hour, expected-revenue calculator for congestion and replacement reserves (MW x price per HE), PMA line validator against Enpower and the inc sheet, shared exception queue with owner, age and resolution fields, morning variance email digest that replaces the ad hoc reports

**Implementation steps**

1. Sit with the real-time trader and settlements to list the variance types seen in the emails: duplicate entries, CISO misentries, cuts, unbooked congestion or reserve revenue, unexplained PMAs, and counterparty changes. Agree on the matching keys for each (book, HE, schedule ID, deal number).
2. Get read access to Enpower deal extracts and CAPS final schedules and position manager data, and find where CAISO award data and the DPR can be pulled each day.
3. Build the daily matching script for one book (ST-WBOM) and run it alongside the current manual process for two weeks, comparing its exceptions with what the trader reports by email.
4. Add the expected-revenue calculator for congestion and replacement reserves, plus the duplicate-deal detector, and extend coverage to the other real-time books.
5. Set up the shared exception queue with owner and status, and send the morning digest to the real-time desk, the CAPS group and settlements.
6. Add the PMA validator: load each month's PMA lines and check each one against the Enpower deal history and the inc sheet before settlements books it.
7. Retire the ad hoc variance emails once the queue covers them, and review aging exceptions each week before the P&L flash.

**Stays manual**

- Choosing the correcting entry: whether to zero a deal, enter an imbalance purchase, or book an annuity between books. This is a trading and accounting judgment.
- Taking a charge for a counterparty (for example, buying back Harbor's schedule) and deciding how to allocate deviation. These are commercial decisions.
- Disputes with the CISO/CAISO over misentered schedules or declined bids, which need calls and recorded-line evidence.
- Approving and booking PMAs and true-ups, which settlements (Virginia Thompson) still owns.
- Tape pulls to confirm what was traded when no system record exists.

**Risks**

- The evidence comes from one mailbox (williams-w3) and does not show how Enpower, CAPS or CAISO data can be extracted. Feeds may need manual exports at first, so confirm access before committing.
- Position manager already reports false variances. Using it as an input could flood the queue with noise, so compare at the detail level and suppress variances that disappear in the detail view.
- CAISO data can be missing (server outages). The job should mark those hours as 'no source data' rather than as a variance or zero revenue.
- PMA formats and the inc sheet layout do not appear in the emails. The PMA validator may need a manual mapping step until the formats are confirmed.
- The value is small (about $77 a month, $924 a year at $85/hour), so build it as a lightweight script on existing extracts. A larger integration would not pay back on handling time alone; the main case is catching missed revenue earlier.

## 4. Real-time desk standing procedures

The real-time desk lead re-teaches standing procedures by group email: Enpower swap entry, Colstrip cut clean-up, PGE transmission deal use, customer finals in CAPS or FSP, hourly generator checkouts for BPA, CAISO outage calls. Some of these emails are resent after they are missed. The fix is one maintained Real-Time Desk Procedures checklist, plus a short start-of-shift checklist and a fixed 'procedure change' email template that points to it. Traders then have one current reference, and the lead edits a section instead of re-sending or re-explaining the rule, worth about $76 per month ($912 per year) at $85/hour.

**Effort:** S · **Success metric:** Number of reminder or re-sent procedure emails from the desk lead to the shift group per month (target: near zero), and the share of shifts with a completed start-of-shift checklist

**How it works today**

1. A rule change or a new deal structure comes up (a FERC/CAISO ruling, a new transmission path, EPE lending, Sundance dispatch). The desk lead writes a free-form 'Group,' email to the shift traders that explains the procedure step by step. (real-time desk lead (Bill Williams)) [williams-w3/sent_items/449, williams-w3/sent_items/444, williams-w3/sent_items/386, williams-w3/sent_items/365]
2. Instructions that go with Enpower deal entry are sent one email at a time: use the swap function rather than annuities, use deal #146517 at zero price for PGE John Day to Malin, and a 7-step Enpower clean-up for Colstrip cuts. (real-time desk lead) [williams-w3/sent_items/432, williams-w3/sent_items/434, williams-w3/sent_items/338]
3. Deadlines and hand-offs to other desks are added by email as they arise: customer finals in CAPS or FSP by 3AM for volume management, copies of EES sheets and cut notes to the lead, a CAPS outage workaround through workspace. (real-time desk lead, volume management, shift traders) [williams-w3/sent_items/413, williams-w3/sent_items/471, williams-w3/sent_items/473]
4. Shift traders carry out the procedures on shift: they call in schedule changes, call the CAISO for every outage, call Grays Harbor and Frontier every hour, report actuals to BPA and sign off the hour in the services book. (shift traders (Portland shift desk)) [williams-w3/sent_items/487, williams-w3/sent_items/408, williams-w3/sent_items/357]
5. When a procedure is missed or forgotten, the lead re-sends the earlier instruction as a reminder or escalation. Sometimes he drafts it for someone else to send. (real-time desk lead, Kate Symes) [williams-w3/sent_items/487, williams-w3/sent_items/444, williams-w3/sent_items/357, williams-w3/sent_items/380]

**Where it stalls**

- Instructions already sent are lost in inboxes and have to be sent again. Nothing points to a single current version.
  > Ryan sent this email out once already, here it is again.
  [williams-w3/sent_items/444]
- The lead has to remind the shift desk of a standing rule because it is not written down where traders look during a shift.
  > These schedule changes must be called in.  Just a reminder.
  [williams-w3/sent_items/487]
- Who to copy on hand-offs is not standardised, so the lead goes uncopied and has to re-send the distribution rule.
  > I should be copied on the EES sheets, and any cut notes to volume managament, the services desk, or other traders.
  [williams-w3/sent_items/471]
- Inconsistent hourly generator checkouts led to a customer escalation from BPA, which then needed a full procedure email to fix.
  > Warren explained to me the necessity and importance of calling in and reporting the actual amount of energy generated by Grays Harbor and Frontier EVERY hour.
  [williams-w3/sent_items/357]
- Swaps entered the wrong way in Enpower cause long downstream disputes, and the fix arrives only as one email.
  > Swaps have caused disputes that have dragged on for months in the past, so call me with any questions.
  [williams-w3/sent_items/432]
- A nightly deadline from volume management reaches the desk as a forwarded email, not as a fixed shift task.
  > Volume management needs us to create customer finals by 3AM each night in CAPS or FSP.
  [williams-w3/sent_items/413]

**Proposed quick win**

Gather the standing instructions from the lead's 'Group,' emails into one Real-Time Desk Procedures checklist with fixed sections. Enpower deal entry covers swaps, the PGE John Day to Malin deal and book assignment for lending. Cuts covers the general cut sheet and the Colstrip steps. Then come CAISO rules (price cap practice, outage calls, wheeling fee items), hourly checkouts (Grays Harbor and Frontier, BPA, services book sign-off), nightly deadlines (customer finals in CAPS or FSP by 3AM) and distribution (who is copied on EES sheets and cut notes). Each section has an owner and a 'last changed' date. A short start-of-shift checklist taken from it is ticked by the incoming trader. When a rule changes, the lead edits the section and sends a fixed 'Procedure change' email: what changed, the section, the effective date, and 'acknowledge by reply'. The free-form explanation is no longer written each time. Reminders become 'see section X', and the weekly real-time meeting reviews only the change log.

- Trigger: A new or changed desk rule (market ruling, new deal structure, new customer service, missed procedure or outside escalation), plus the start of every shift for the start-of-shift checklist
- Inputs: the lead's existing procedure emails to the real-time group; the attached cut procedure sheet; deadlines set by volume management and the services desk; CAISO and BPA requirements relayed by the lead
- Outputs: one maintained Real-Time Desk Procedures checklist for shift traders; a start-of-shift checklist ticked by the incoming trader; short 'Procedure change' notices pointing to the changed section, with trader acknowledgements; a change log reviewed at the real-time meeting
- Existing systems: Enpower, CAPS, FSP, services book, dispatch log
- New components: Real-Time Desk Procedures checklist with sectioned, dated entries and an owner per section, start-of-shift checklist (hourly checkouts, 3AM customer finals, outage calls, copy list), 'Procedure change' email template with section reference and acknowledgement line, change log of procedure edits

**Implementation steps**

1. Collect the lead's past 'Group,' instruction emails and the attached cut sheet, and sort each rule into the sections Enpower deal entry, Cuts, CAISO, Hourly checkouts, Nightly deadlines, Distribution and Special dispatch.
2. Write each rule as a numbered checklist item in imperative form, keeping exact deal numbers, books and step order from the source email (for example the 7 Colstrip steps and deal #146517), with a source-email date.
3. Have the lead review the draft and remove rules that no longer apply, such as short-dated lending or Sundance coverage, marking time-limited items with an expiry date.
4. Put the checklist in one shared location the shift desk opens at the start of every shift, and print the one-page start-of-shift checklist for the desk.
5. Set up the 'Procedure change' email template and send the first one to the shift group, announcing the checklist and asking each trader to acknowledge it.
6. From then on, when a trader asks about a covered rule or misses a step, reply 'see section X' and update the section when the answer changes.
7. Review the change log and any repeated misses at the weekly real-time meeting, and retire or clarify items as needed.

**Stays manual**

- Judging trading strategy (dec bids, buy-backs, buying over the cap for reliability) stays with the lead and traders, because it depends on live market conditions.
- Handling escalations from counterparties such as BPA, and conduct issues, needs the lead's direct involvement.
- Deciding books and deal numbers for new one-off structures (lending with EPE, new transmission paths) is a trading decision. The checklist only records the result.
- The phone calls themselves (to CAISO, generators, BPA, the power pool) are still made by the shift trader. The checklist tells them when and what to record.

**Risks**

- The checklist goes stale if the lead keeps emailing rules without editing it. Mitigation: every change email must name a section, and the meeting reviews the change log.
- Traders may not open it during busy hours. Mitigation: keep the start-of-shift page to one sheet and ask for acknowledgements on changes.
- The evidence covers only one mailbox (williams-w3) and shows instructions sent, not how often traders actually look them up or miss them. The saving rests on the lead's handling time (about $76 per month) and may be understated if the reminders avoid penalties or disputes.
- The emails do not say where shared documents live for the desk, so the hosting location has to be agreed with the team. Choosing a place traders do not use would defeat the fix.
- Some instructions are time-limited (lending for specific dates, Sundance dispatch for July 19-22). Mixing them with standing rules could mislead. Mitigation: expiry dates on such items.

## 5. Weekly California capacity report

Every Thursday or Friday, Michelle Lokay builds the California Capacity Report by hand and sends it to the Transwestern commercial team. It covers Transwestern and El Paso deliveries to California, capacity utilization percentages, posted Gas Daily prices and Enron basis. A scheduled job would collect the week's figures, do the averages and percentages, fill in the week dates in the subject, and leave a ready-to-send draft in the existing layout. That saves roughly 0.9 h/month ($73/month, $876/year) and removes errors from retyping and copying last week's email, such as the wrong-week correction seen in January.

**Effort:** M · **Success metric:** Share of weekly reports sent without a follow-up correction, together with the analyst's minutes per report (target: review only), tracked over the first 8 weeks after switching to draft-and-review.

**How it works today**

1. At the end of each week (Thursday before a holiday or short week, otherwise Friday), the analyst collects Transwestern's average deliveries to California, San Juan lateral throughput and total East deliveries for the week. (Transwestern marketing analyst (michelle.lokay)) [lokay-m/inbox/10, lokay-m/sent_items/63, lokay-m/sent_items/30]
2. The analyst collects El Paso's average deliveries to California for the PG&ETop, SoCalEhr and SoCalTop delivery points, looks up each point's capacity (SoCalEhr changed from 1042 to 1250 and SoCalTop from 512 to 540 between October and December), and works out each utilization percentage by hand. (Transwestern marketing analyst (michelle.lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/40]
3. The analyst copies the day's posted Gas Daily prices and day-over-day changes for SoCal gas, PG&E, TW San Juan (later 'San Juan (non-Bondad)') and TW Permian, entering 'n/a' when a price is not posted. (Transwestern marketing analyst (michelle.lokay)) [lokay-m/sent_items/67, lokay-m/sent_items/131, lokay-m/sent_items/146]
4. The analyst adds Enron Online / Enron basis spreads (Perm-CA, SJ-CA, SJ-Waha, Perm-Waha) while they are available. From late December they read 'n/a', and from February the section is dropped. (Transwestern marketing analyst (michelle.lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/55, lokay-m/sent_items/79]
5. The analyst types the subject line 'California Capacity Report for Week of MM/DD-MM/DD' and emails the report to the same fixed list (Steven Harris, Kimberly Watson, Lorraine Lindberg, TK Lohman, Lindy Donoho). (Transwestern marketing analyst (michelle.lokay)) [lokay-m/sent_items/86, lokay-m/sent_items/97, lokay-m/sent_items/110]
6. When the week label on a sent report is wrong, the analyst sends a correction to the whole distribution list. (Transwestern marketing analyst (michelle.lokay)) [lokay-m/sent_items/46]

**Where it stalls**

- The report's week label is typed by hand, likely by reusing the previous week's email. A wrong effective date went out and needed a follow-up correction to all five recipients.
  > Sorry, the effective date for this new report is 01/07-01/11.
  [lokay-m/sent_items/46]
- The analyst keeps delivery-point capacities in her head or in last week's email. This October figure for SoCalEhr (1042) differs from the 1250 used from December, so each utilization percentage depends on a manually maintained capacity value and a hand calculation.
  > SoCalEhr, capacity 1042 MMBtu/d, deliveries of 707 MMBtu/d (68%)
  [lokay-m/inbox/10]
- El Paso volumes come from a third-party pipeline and are re-averaged and re-typed every week, together with the overall California utilization percentage.
  > El Paso's average deliveries to California were 2198 MMBtu/d (75%):
  [lokay-m/sent_items/18]
- Transwestern delivery, San Juan lateral and East figures are re-keyed into the same sentence every week. This is the repetitive core of the roughly 30 minutes of handling per report.
  > Transwestern's average deliveries to California were 1011 MMBtu/d (93%), with San Juan lateral throughput at 872 MMBtu/d.  Total East deliveries averaged 337 MMBtu/d.
  [lokay-m/sent_items/86]

**Proposed automation**

A weekly scheduled job runs on the report day. It reads the week's daily Transwestern deliveries to California, San Juan lateral throughput and East deliveries, plus El Paso's daily deliveries at PG&ETop, SoCalEhr and SoCalTop, and averages them over the business days of the reporting week. It divides each average by capacity from a small maintained table of delivery-point capacities, keeps Transwestern's percentage basis, and computes the percentages. It pulls the latest posted Gas Daily prices and the change from the prior posting for the four quoted locations, writing 'n/a' when no price is posted, and adds the Enron Online basis block only when quotes are available. It fills the existing email layout, builds the subject 'California Capacity Report for Week of MM/DD-MM/DD' from the calendar, and saves a draft addressed to the standing distribution list. The analyst checks the numbers, adds any commentary and sends it.

- Trigger: Weekly schedule on the last business day of the week (Friday, or Thursday when the week is short), early enough for the draft to be ready before the usual mid-morning send.
- Inputs: Daily Transwestern deliveries to California, San Juan lateral throughput and total East deliveries for the reporting week; Daily El Paso deliveries at PG&ETop, SoCalEhr and SoCalTop for the reporting week; Delivery-point capacity table (PG&ETop, SoCalEhr, SoCalTop, and the Transwestern California capacity used for its percentage); Posted Gas Daily prices and day-over-day changes for SoCal gas large pkgs, PG&E large pkgs, San Juan (non-Bondad) / TW San Juan, and TW Permian; Enron Online basis quotes for Perm-CA, SJ-CA, SJ-Waha and Perm-Waha, when available; Business-day calendar, used to work out the week range and report day; Standing distribution list
- Outputs: Draft email to the analyst in the existing layout, with a calendar-generated subject, ready to review and send; Exception notes at the top of the draft for the analyst: missing source days, a price not posted, a capacity value changed since last week, or a week-over-week swing beyond a threshold; Archived weekly figures (one row per week) so the commercial team can see trends without searching old emails
- Existing systems: Gas Daily, Enron Online
- New components: Weekly scheduled report job, Data extract for Transwestern and El Paso daily delivery volumes (source to be confirmed with the analyst), Maintained delivery-point capacity table with an effective date for each value, Gas Daily price loader with 'n/a' handling for unposted locations, Email template renderer that reproduces the current report layout and builds the week-range subject, Exception and sanity-check rules (missing days, capacity change, large swings), Weekly figures archive

**Implementation steps**

1. Sit with the analyst for one report cycle to confirm where each figure comes from: Transwestern volumes, El Paso volumes, capacities, Gas Daily prices and the Enron Online basis. Also confirm whether each percentage is computed over business days or calendar days.
2. Build the capacity table from the most recent reports (PG&ETop 1140, SoCalEhr 1250, SoCalTop 540) with effective dates, and assign an owner to update it.
3. Write the template renderer to reproduce the current email body and subject exactly, then check it by re-rendering several past weeks from their published figures.
4. Build the extracts and the Gas Daily loader, and calculate averages and percentages in code.
5. Run in parallel for three or four weeks: the job produces a draft while the analyst still builds the report by hand, and any differences are reconciled.
6. Switch to draft-and-review: the job saves the draft, and the analyst reviews, adds commentary and sends.
7. Add the weekly archive and the exception rules, and review the thresholds with the recipients after one month.

**Stays manual**

- Final review and send: recipients use these numbers for commercial decisions, so a person confirms they are plausible before they go out.
- Market commentary or explanation of unusual weeks, which needs judgment.
- Updating delivery-point capacities when El Paso or Transwestern capacity changes, because the change is announced outside the data feed.
- Deciding whether to include or drop a section (for example, the Enron basis block that went to 'n/a' and was later removed) when the data source is unavailable.

**Risks**

- The evidence never names where Transwestern and El Paso volumes come from. If El Paso data is only available from a manual website lookup, automation may need screen-scraping or may stay partly manual. Confirm sources before funding the build.
- The value is small, $73/month ($876/year), from a single mailbox over about five active months. A full integration may not pay back. A lighter version (a spreadsheet that calculates percentages and generates the subject from the calendar) captures most of the error reduction for less effort.
- Capacity values change: SoCalEhr went from 1042 to 1250 and SoCalTop from 512 to 540. A stale capacity table would silently misstate utilization. Mitigate with effective-dated capacities and a flag whenever a percentage is above 100% (Transwestern reached 103%) or moves sharply.
- Gas Daily prices are sometimes not posted for a location ('n/a'), and location names change (TW San Juan to San Juan (non-Bondad)). The loader must handle gaps and renames without carrying forward a stale price.
- Report-day changes (Thursday on short weeks) and holiday weeks (12/26-12/28, 02/19-02/22) must come from a business calendar, or the week label will repeat the error behind the January correction.
- Gas Daily content licensing may restrict automated extraction. Confirm before building the loader.

## 6. Meter volume and allocation variance resolution

Meter allocation problems (flow with no deal in OSS or CPR, POPS feeding zero volumes to Sitara, desk-to-desk variances, counterparties chasing payment) are found one meter at a time. Each one becomes its own email to Daren Farmer or volume management and can sit unanswered for days or weeks. A read-only exception report, run after each allocation, would compare measured flow, POPS confirmed and allocated volumes and Sitara/OSS deals, and give each meter a structured ticket with the evidence already attached. It saves about $62/month ($744/year) of handling, but most of its value is that big UA4 and P&L problems get caught the day they appear.

**Effort:** M · **Success metric:** Number of meters with measured flow but no matching Sitara/OSS deal still open at month-end UA4 close, and median age of open allocation exceptions

**How it works today**

1. A settlements or accounting analyst working a UA4 or allocation exception finds a meter with flow but no matching deal. They check OSS, CPR and MIPs measurement statements by hand. (settlements / UA4 analyst) [farmer-d/logistics/595, farmer-d/logistics/622, farmer-d/logistics/1483]
2. The analyst emails the logistics desk (usually Daren Farmer) to ask whether a deal exists, whether a CPR deal failed to feed OSS, or how a short or under-pulled nomination should be handled. (settlements analyst to logistics desk) [farmer-d/logistics/595, farmer-d/logistics/622, farmer-d/logistics/682, farmer-d/logistics/902]
3. Volume management or scheduling spots wrong data in POPS by chance while reviewing imbalances: missing BAV feeds, zero volumes fed back to Sitara, delivery noms at receipt meters, confirmations on days the deal does not cover. They then escalate by email. (volume management / scheduling) [farmer-d/logistics/925, farmer-d/logistics/754, farmer-d/logistics/1351]
4. Open items pile up and are chased with follow-ups, kept on a hand-maintained outstanding-issues list, or forwarded between managers until someone checks the allocation. (logistics and accounting managers) [farmer-d/logistics/739, farmer-d/logistics/1185, farmer-d/logistics/1191, farmer-d/logistics/1241]
5. The fix is coordinated by hand across several people: zero confirmed noms, change the allocation method, reallocate, verify BAV adjustments with Settlements, update facilities, or have a deal extended or set up. (measurement / volume management / Global Facilities Dept) [farmer-d/logistics/1439, farmer-d/logistics/1185, farmer-d/logistics/1483]
6. Counterparties chase payment for volumes Enron has nothing allocated for. Their calls reach accounting, which forwards them to logistics. (accounting / counterparty contact) [farmer-d/logistics/2089, farmer-d/logistics/1038]

**Where it stalls**

- An analyst cannot find a deal for measured flow in either system and has to wait for logistics to research it.
  > Daren - I need your help in resolving this issue.  There wasn't any deal in
  [farmer-d/logistics/595]
- A CPR deal may not have fed over to OSS. Nobody can see this until someone asks.
  > Daren is there a deal in CPR which may not have fed over to OSS?
  [farmer-d/logistics/622]
- Missing POPS feeds and zero volumes to Sitara went undetected for days, with UA4 and P&L impact.
  > problem of this magnitude needs to be addressed as soon as it's discovered.
  [farmer-d/logistics/925]
- Desk-to-desk variances come from the two sides using different volume sources. They sit on a manually tracked outstanding list.
  > ENA is using Tetco's  volume and HPLC is using the HPL Measurement volume,
  [farmer-d/logistics/1185]
- A receivable stays open while accounting waits on one logistics person.
  > receivable balance, then we are waiting on a response from Daren.
  [farmer-d/logistics/1241]
- POPS confirmations on days the deal does not cover cause wrong prorating and feedback errors.
  > When Karen allocates the actual 10,000 it is prorating 5,000 for each day
  [farmer-d/logistics/1351]
- Flow cannot be allocated until someone confirms it and gets a deal extended.
  > I need to verify that flow occured so that I can have a deal(s)
  [farmer-d/logistics/1483]
- Counterparties find unallocated volumes before Enron does.
  > I am getting several phone calls from Alpine Resources demanding to be paid
  [farmer-d/logistics/2089]

**Proposed automation**

A read-only reconciliation job runs after each POPS allocation and again at month-end. For every meter and day it pulls measured volume (MIPs measurement statements), POPS confirmed noms and allocated volumes, and the Sitara/OSS deals and their valid dates. It applies a fixed set of rules: flow with no deal, deal with no flow, zero or missing feed from POPS to Sitara, a delivery nom at a receipt meter, a confirmation outside the deal's date range, a nomination not pulled, and allocated vs measured differences beyond a tolerance. Each rule hit becomes an exception row. The row carries the meter, period, volumes from each source, the prior month for context, and a suggested owner (logistics desk, volume management, settlements). Exceptions go to one shared queue with status and age, replacing ad hoc emails and the hand-kept outstanding-issues list. Owners still decide the fix, and their resolution note is saved with the row.

- Trigger: Completion of the daily POPS allocation run, plus a scheduled month-end run before UA4 close
- Inputs: MIPs measurement statement volumes by meter and day; POPS confirmed nominations, allocation method and allocated volumes; Sitara deal tickets (meter, counterparty, valid dates, volume); OSS and CPR deal records for the same meters and periods; meter attributes (receipt vs delivery, allocatable flag); prior-month exception history
- Outputs: daily exception list by meter for volume management and the logistics desk; month-end UA4 exception summary for settlements and accounting managers; aging report of open exceptions, replacing the manual interdesk/interconnect outstanding list; per-exception evidence pack the analyst can forward to the counterparty or pipeline
- Existing systems: POPS, Sitara, OSS, CPR, MIPs
- New components: extracts from POPS, Sitara, OSS, CPR and MIPs into a staging table, rule-based variance engine with per-rule tolerances, exception queue with owner, status, age and resolution note, routing table mapping meters and rule types to owners, daily and month-end exception reports

**Implementation steps**

1. Inventory the past year of exception emails and agree the rule list and tolerances with volume management, logistics and settlements.
2. Arrange read-only extracts from POPS, Sitara, OSS, CPR and MIPs, keyed by meter number and gas day.
3. Build the staging table and the meter and deal matching logic. Handle CPR-to-OSS feed lag by comparing both.
4. Implement the rules one at a time, starting with flow-with-no-deal and zero POPS-to-Sitara feed, and test them against known historical cases (e.g. meters 1441, 986782, 984132).
5. Build the exception queue and routing table, with owners named by volume management.
6. Run in parallel with the current email process for one month-end, and tune tolerances to remove noise.
7. Switch the month-end UA4 review and the outstanding-issues list over to the queue, and ask analysts to file new exceptions there rather than by email.

**Stays manual**

- Deciding which volume is correct when sources disagree (e.g. pipeline vs HPL Measurement custody questions), because it depends on contracts and custody transfer.
- Creating, extending or moving deals in Sitara and reallocating meters in POPS, because these change P&L and are owned by logistics and volume management.
- Legal or commercial calls such as whether gas is bought as wellhead, or which book a sale belongs in.
- Talking to counterparties and pipelines (Transco, Exxon, Pennzoil and others) to settle imbalances.

**Risks**

- The evidence does not say what extracts or interfaces POPS, OSS, CPR and MIPs offer. If no extract exists, effort could grow from M to L, so confirm data access first.
- Meter numbers appear in different formats across messages (e.g. 98-9699, 986892, 0980439), and meters get replaced. A meter cross-reference must be maintained or matches will be missed.
- Loose tolerances will flood analysts with noise, and tight ones will miss material UA4 items. Tune them during the parallel run.
- Measured savings are small ($62/month at $85/hour), so the funding case rests on catching large feed failures early, like the 500,000 MMBtu POPS imbalance. That benefit is not priced in these figures.
- Exceptions without a clear owner will still stall. The routing table needs a named owner and an escalation path for each rule.

## 7. Sitara deal ticket entry and correction requests

Traders, producer services, storage and accounting staff ask the logistics desk (mostly Daren Farmer) in free-form email to create, change, zero out or cut off Sitara deal tickets. These requests often leave out the deal number, meter, effective date or reason, and are then chased with follow-ups for days. The fix is a standard Sitara deal request template that requesters fill in, plus a matching confirmation reply that sends back the deal number. This removes the clarification and 'have you had a chance' rounds. The process is valued at $58 per month ($696 per year) at $85 per hour, so this is a low-cost hygiene fix, not a system build.

**Effort:** S · **Success metric:** Share of Sitara deal request threads that need a follow-up or clarification email before the desk confirms a deal number, measured monthly against the pre-rollout baseline

**How it works today**

1. A requester emails the desk asking for a new deal ticket, often with the counterparty, meter, volume and price typed as loose text and sometimes with only a one-line ask (producer services / traders / volume management) [farmer-d/logistics/765, farmer-d/logistics/789, farmer-d/logistics/679, farmer-d/logistics/1082]
2. Other requests ask to change an existing deal: bring expected volume to zero, cut a deal off going forward, change pricing, or zero a deal out instead of killing it so Unify paths are not broken (volume management / storage / accounting) [farmer-d/logistics/748, farmer-d/logistics/965, farmer-d/logistics/1200, farmer-d/logistics/5]
3. The desk enters or changes the ticket in Sitara and, when asked, replies with the Sitara number. Coordinated entries such as a purchase plus a matching sale to the Storage Book have to land on the same day (logistics desk (Daren Farmer, Tom Acton)) [farmer-d/logistics/789, farmer-d/logistics/1082]
4. Monthly transport usage tickets are rolled forward with refreshed rates and zeroed volumes, and schedulers are told to check that volumes show correctly in Position Manager (transport rates / schedulers) [farmer-d/logistics/1144]
5. At month start or at close, unpathed or unassigned deals are found and the desk is asked who owns them and whether the deal has been entered (volume management / scheduler / accounting) [farmer-d/logistics/673, farmer-d/logistics/102, farmer-d/logistics/12]
6. When the request was incomplete, a change was made without telling anyone, or nothing was confirmed, requesters send follow-ups and supervisors escalate (requesters / logistics supervisor (Pat Clynes)) [farmer-d/logistics/59, farmer-d/logistics/1299, farmer-d/logistics/1200]

**Where it stalls**

- Zero-out requests are sent as a list in an earlier email with no confirmation per deal, so the requester has to chase the deals still open
  > Wanted to let you know that there are still two sitara deals that need to
  [farmer-d/logistics/748]
- A pricing change waits on the desk while the counterparty keeps calling and the requester has no status to give them
  > Duke has called me several times they want to get our March deals finalized.
  [farmer-d/logistics/1200]
- Deal entry for a storage sale is still not confirmed as close approaches, so accounting has to ask who did it
  > Have the two of you been able to get the deal in for the sale of the Centana storage to AEP?
  [farmer-d/logistics/12]
- Deals are killed instead of zeroed, which breaks paths downstream and leads to a corrective request and a question about the reason
  > If a deal is killed it poses a problem for us in Unify if there are any paths associated with the deal; therefore, we request the deals be zeroed out.
  [farmer-d/logistics/5]
- An EOL deal volume was changed after hours and the change was never sent to the desk, so the supervisor had to escalate
  > I got a call on Friday evening about this
  [farmer-d/logistics/1299]
- At the month rollover, deals are left unpathed and unassigned, and someone else has to path them from prior-month activity and ask who owns them
  > All Deals with the exception of the long term Transport Expense were left
  [farmer-d/logistics/673]
- Months-old deals are found still unpathed long after the fact
  > It doesn't look like it's been pathed for HPL and CHAN.
  [farmer-d/logistics/102]
- A cut-off request arrives as a forward with the reason buried in someone else's message, so no effective date or reason is stated
  > Can you cut off deal 47472 going forward? I am forwarding the message from
  [farmer-d/logistics/965]

**Proposed quick win**

Publish one 'Sitara deal request' email template that every requester must use for new tickets, changes, zero-outs, cut-offs and price changes. It has fixed fields: request type, existing Sitara deal number (for changes), counterparty, meter, start and end date, volume, price or pricing formula, book (for example Storage Book), linked entries that must go in the same day, and the reason. The template states the desk rule that deals are zeroed out, not killed, when paths exist in Unify. The desk keeps a matching confirmation reply that returns the new or changed Sitara deal number, the effective date and what was changed, and copies volume management when volumes or paths are affected. Requests missing required fields get a one-line canned reply pointing back to the template, not an ad-hoc question thread. A short month-start checklist covers rolling transport usage tickets, assigning unpathed pipes and checking volumes in Position Manager.

- Trigger: An incoming email asking the logistics desk to create, change, zero out, cut off or reprice a Sitara deal, and the first business day of each month for the rollover checklist
- Inputs: requester's completed template fields (request type, deal number, counterparty, meter, dates, volume, price, book, reason); the existing deal in Sitara for change requests; the list of pipes and deals not yet pathed at month start
- Outputs: Sitara deal request template for traders, producer services, storage and accounting; a confirmation reply to the requester with the Sitara deal number and the change made, copying volume management; a canned 'incomplete request' reply; a month-start deal rollover checklist for the desk and schedulers
- Existing systems: Sitara, Unify, Position Manager, EOL
- New components: Sitara deal request email template (Outlook/Lotus stationery or a shared document), desk confirmation reply text returning the Sitara deal number, canned incomplete-request reply, month-start rollover checklist (transport usage tickets, unpathed pipes, Position Manager volume check), shared folder or mailbox rule that files template-subject requests together

**Implementation steps**

1. Collect the fields that requests in the evidence actually carry (counterparty, meter, volume, price formula, deal number, book, same-day linked entries, reason) and draft the template with request-type checkboxes: new, change volume, change price, zero out, cut off.
2. Add the 'zero out, do not kill, when Unify paths exist' rule and a required reason line to the template.
3. Write the confirmation reply, which returns the Sitara deal number, the effective date and what changed, copies volume management for volume or path changes, and asks requesters to send EOL deal changes to the desk the same day.
4. Write the one-line incomplete-request reply that links to the template.
5. Draft the month-start checklist: roll transport usage tickets, list unpathed pipes and give each one an owner, and have schedulers check volumes in Position Manager.
6. Review the drafts with the logistics supervisor and the main requesting groups (producer services, storage, volume management, settlements), then store them in a shared location the desk can reach.
7. Announce the template by email to frequent requesters. For two weeks the desk answers free-form requests with the template attached, then moves to the incomplete-request reply.
8. After one month, count follow-up and 'have you had a chance' emails on deal requests and compare with the baseline.

**Stays manual**

- Entering and changing the ticket in Sitara itself. That is the desk's judgment on deal structure, rates and paths.
- Deciding whether an unclear or old deal (for example suspended payments on a former trader's deals) should be changed at all. This needs research and judgment.
- Assigning ownership of unpathed or unassigned pipes at the month rollover. That is a staffing decision for the supervisor.
- Handling rate questions where no contract covers the transaction. Legal and commercial judgment is needed.

**Risks**

- Requesters may ignore the template and keep sending one-line asks. Mitigation: the desk replies consistently with the template, and the supervisor backs the rule.
- The evidence does not show which email client or shared drive the desk uses, so where the template lives must be confirmed with the desk before rollout.
- The value is small ($58 per month), so rollout effort must stay at a few days. A heavier tool is not justified by this evidence.
- Some stalls come from capacity or ownership gaps (unassigned pipes, people out of the office), not missing fields. A template will not fix those, so the checklist only makes them visible.
- EOL deal changes start outside the email request flow. The template can ask for notification but cannot enforce it.

## 8. Real-time position and shift handoff

The Portland real-time desk lead emails the shift every evening, in free text, with the next day's length and shorts, the book to use (ST-WBOM, ST-CALI, St-SW), deals already keyed in Enpower, and one-off duties. Those emails get re-sent with corrections, and problems such as dispatcher-removed transmission requests come back only by ad hoc email. A fixed handoff template, kept as a tab on the Service Sheet and sent to DL-Portland Real Time Shift, puts every position and every return item in the same fields each time. The modelled value is small, about $52 a month ($624 a year) at $85/h. The bigger gain is fewer missed entries and fewer correction re-sends.

**Effort:** S · **Success metric:** Number of correction or follow-up emails per handoff to DL-Portland Real Time Shift ('one more time' re-sends), and the share of dispatcher-removed transmission requests recorded in the Return section on the same day

**How it works today**

1. In the evening, the desk lead writes a free-text email to the shift operators with the next day's long or short position: MW, hours ending, hub (NP-15 or SP-15), price, and the book the deals go under (ST-WBOM). (real-time desk lead (Bill Williams)) [williams-w3/sent_items/512, williams-w3/sent_items/502, williams-w3/sent_items/466, williams-w3/sent_items/414]
2. The same email covers other desks' positions (ST-CALI, St-SW), which have to be copied into the service sheet or looked up on Phil Platters sheet and in CAPS. (desk lead and shift operators) [williams-w3/sent_items/506, williams-w3/sent_items/496, williams-w3/sent_items/414]
3. The lead, or Kate Symes, says which Enpower deals are already entered (by deal number) and which ones the shift still has to key or price in real time. Examples are purchases from the Calimbalance or the price on an EPE buy. (desk lead, deal entry (Kate Symes), shift operators) [williams-w3/sent_items/392, williams-w3/sent_items/433, williams-w3/sent_items/370, williams-w3/sent_items/463]
4. One-off duties go into the same email: APS losses, the hourly BPA check-out, NEVP transmission notice, unit ramp order and EES ancillary dispatch tracking in the Service Sheet. (desk lead) [williams-w3/sent_items/506, williams-w3/sent_items/362, williams-w3/sent_items/360, williams-w3/sent_items/330]
5. When positions change after the first email, the lead sends a follow-up or forwarded correction, or corrects a standing instruction. (desk lead) [williams-w3/sent_items/403, williams-w3/sent_items/360]
6. Shift operators report problems back by individual email. One example is dispatchers removing transmission requests that should have been withdrawn through the Pacificorp Oasis system. (shift operators to desk lead) [williams-w3/sent_items/395]

**Where it stalls**

- Positions are corrected after the handoff email has gone out, so the shift has to merge several emails to know the real position.
  > We have also bought HE 21 and HE 22 from the APX.
  [williams-w3/sent_items/403]
- Other desks' positions sit in separate sheets, and the shift has to copy them across by hand. This invites missed or doubled entries.
  > ST-CALI is providing us with a sheet detailing their positions for RT, we will now be providing them with a sheet each morning detailing their sales from the previous day.
  [williams-w3/sent_items/506]
- Problems from the shift come back with no fixed place to record them, so mistakes surface as charges weeks later.
  > Send me an email each time the dispatchers remove requests on our behalf, or if We/PAC are/is unable to take the request out of their computer system.
  [williams-w3/sent_items/395]
- Enpower entry is split between the lead, deal entry and the shift. Open items wait until someone arrives or a price is filled in.
  > Kate has made the enpower for this deal (#672781, and #672785).  Please put the price in for deal #672781 (buy from EPE).
  [williams-w3/sent_items/433]
- Deal entry is pushed to the next morning, so the shift handles the schedule before the deals exist in Enpower.
  > I will do enpower for these deals when I arrive in the morning.
  [williams-w3/sent_items/362]
- Standing operating instructions are corrected by broadcast email. Nothing records which version is current.
  > After discussion with Roger, the Four Corners Units 4 and 5 are NOT take or pay.
  [williams-w3/sent_items/360]

**Proposed quick win**

Replace the free-text evening email with a fixed shift handoff template, kept as a tab on the Service Sheet. A copy is pasted into the email to DL-Portland Real Time Shift. The desk lead fills one row per position: date, hours ending, hub, MW, long or short, price, book (ST-WBOM, ST-CALI, St-SW), the CAPS line, Enpower deal numbers already entered, and what the shift must still key or price. The other sections are fixed. 'Other desks' positions' links to the ST-CALI sheet rather than retyping it. 'Special duties this shift' covers losses, BPA check-out, NEVP notice and ancillary dispatch. 'Standing instructions changed' covers items like unit ramp order. Operators fill a 'Return' section at shift end: missed or changed schedules, transmission requests withdrawn or removed by dispatchers, and Enpower items still open. That gives the lead one place to read problems back. A correction is a new row marked 'revised' in the same tab, not a separate 'one more time' email.

- Trigger: The evening handoff before each trading day, plus each shift change, when the operator going off fills the Return section.
- Inputs: next-day length and shorts by hour ending, hub and price; book assignments (ST-WBOM, ST-CALI, St-SW); Enpower deal numbers already entered; tags and preschedule entries made by preschedule staff; special duties and standing-instruction changes; operator-reported problems and dispatcher removals
- Outputs: filled handoff tab on the Service Sheet for the shift operators; handoff email to DL-Portland Real Time Shift in the fixed layout; shift-end Return section for the desk lead listing missed schedules, open Enpower items and transmission removals
- Existing systems: Service Sheet, CAPS, Enpower, DL-Portland Real Time Shift, Pacificorp Oasis system
- New components: shift handoff template tab (position table plus fixed sections), shift-end Return checklist (missed schedules, Oasis withdrawals, dispatcher removals, open Enpower items), 'revised' row convention that replaces correction emails, standing-instructions log section (ramp order, BPA check-out, NEVP notice lead time)

**Implementation steps**

1. Draft the template from the recurring fields in the lead's last month of 'Length for' emails: hours ending, hub, MW, price, book, CAPS line, Enpower deal numbers, and deals still to key.
2. Add the template as a tab on the Service Sheet, next to the existing initials column for hourly BPA check-out calls.
3. Add the shift-end Return checklist and the standing-instructions log section to the same tab.
4. Agree with Kate Symes (deal entry) and the preschedule staff that they put Enpower deal numbers and tag status into the tab rather than in a separate email.
5. Run the template alongside the email for two weeks. The lead pastes the filled table into the DL-Portland Real Time Shift email so operators see the same layout.
6. Switch over: corrections become 'revised' rows, and operator problem reports, including dispatcher removals of Pacificorp Oasis requests, go only into the Return section.
7. After a month, review the Return sections with the lead and add any recurring item that still arrives by email.

**Stays manual**

- Deciding positions, prices and which book carries them stays with the desk lead. That is a trading judgement.
- Real-time purchases and sales during the shift, and calls to dispatchers (EPE, BPA, NEVP, LADWP), stay with the operators.
- Contesting charges such as take-or-pay transmission bills stays manual. The Return log only gives the evidence trail.
- Changing operating rules (unit ramp order, take-or-pay status) needs a person to confirm them with the plant or counterparty before they go into the log.

**Risks**

- The evidence comes from one mailbox (williams-w3), and nearly all of it is the lead's sent mail. How operators actually report back is thinly evidenced, so check the Return section against the operators' practice before rollout.
- If the lead goes back to free-text email under time pressure, the template drifts out of date. Mitigate by making the template the only place deal numbers and corrections are recorded.
- The ST-CALI desk's own sheet may disagree with the handoff tab. Link to it rather than copying, and note the time of the last update.
- The dollar value is small (about $52 a month). The case rests on fewer missed entries and contested charges, which this evidence does not quantify.
