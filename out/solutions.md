# Solution designs

One design per top opportunity: an automation, or the rollout of a quick win. Citations are message ids; quotes are verified verbatim.

## 1. Meter flow with missing or expired deal resolution

Volume management and logistics keep finding gas allocated at a meter with no Sitara deal behind it: the deal has expired, covers the wrong days, or the volume is parked on Strangers Gas. They then email Daren Farmer, the deal owner, one request at a time to extend or create a ticket, and that request often waits a day or more. The fix is a daily exception job that compares allocated flow by meter and day with active Sitara deal terms and sends the owner a pre-filled extend/create/write-off request. Most of these items would then be caught the day after flow starts instead of months later, which removes the chasing emails worth about $184 a month ($2,208 a year).

**Effort:** M · **Success metric:** Number of meter-days with allocated flow but no covering Sitara deal at month-end close, and the median days from first flow to deal extension or creation

**How it works today**

1. A volume analyst or logistics scheduler sees flow or an allocation at a meter that no valid deal covers. The deal might have ended (286824 ends on 6/17), cover only some days (155118 is valid on 1/26 only), or not exist at all. Sometimes the item shows up in the allocation exception screen or as a Feedback Monitor error. (volume management analyst / logistics) [farmer-d/logistics/1224, farmer-d/logistics/782, farmer-d/logistics/899, farmer-d/logistics/1356]
2. While waiting for a deal number, the analyst parks the volume on Strangers Gas, or in Volume Management with 'no detail', so the meter clears temporarily. (volume management analyst) [farmer-d/logistics/899, farmer-d/logistics/130]
3. The analyst types up an email to the deal owner with the meter, deal number, dates and decatherms, and asks for an extension or a new ticket (e.g. extend 422516 for 10/6/2000, extend 465322 for 11/21/2000). (volume management analyst (Jackie Young, Aimee Lannou)) [farmer-d/logistics/1981, farmer-d/logistics/1999, farmer-d/logistics/1149]
4. If the owner is unclear or the request lands on the wrong desk, it gets forwarded between desks (the East desk to Daren, Julie to Daren, George/Craig asked to work out who should roll the deal). (traders / deal owners on HPL and East desks) [farmer-d/logistics/1055, farmer-d/logistics/1981, farmer-d/logistics/117]
5. Old or large items go to an approver, who asks why the gas was only found now before agreeing to a deal, a buy back or a write-off. (deal owner / approver) [farmer-d/logistics/1356, farmer-d/logistics/1489, farmer-d/logistics/2070]
6. The deal owner extends or creates the Sitara ticket. Someone inserts the path in Unify, and the analyst re-allocates, gets track ids and closes the item. Volumes are often changed several times before it is closed. (trader, scheduler, volume management) [farmer-d/logistics/1981, farmer-d/logistics/1514, farmer-d/logistics/1972]

**Where it stalls**

- Logistics cannot move until the deal owner answers, and nothing in the request tells him what is needed or by when.
  > Logistics is waiting to hear from Daren on this issue.
  [farmer-d/logistics/782]
- Flow starts before any Sitara deal exists, so the gap is found later during allocation instead of on day one.
  > It looks as though this meter is flowing starting 3/1/2000.
  [farmer-d/logistics/899]
- The same meter comes back because the deal covers only part of the month's flow days, so a second request is needed.
  > Can you assist Anita and I w/a deal number to place the 1st 20 days on.
  [farmer-d/logistics/1149]
- An item found after two years stalls at approval because nobody can say why the gas was missed.
  > I am uncomfortable putting a deal out there without more details.
  [farmer-d/logistics/1356]
- A very old request may not be processable at all because the period predates the current scheduling system.
  > I don't think we can even process this request.
  [farmer-d/logistics/1489]
- Volumes are re-allocated several times between parties, which repeats deal and path changes.
  > We go round and round at this point 
changing volumes two, three or more times.
  [farmer-d/logistics/1972]
- A missing actualization or deal blocks a counterparty payment that has a hard deadline.
  > Payment MUST be set up by noon 5/24/01 for prompt payment to Spinnaker.
  [farmer-d/logistics/130]
- The analyst only learns the deal term has ended when checking the ticket during allocation.
  > I checked the deal ticket (286824) and it ends on 6/17.
  [farmer-d/logistics/1224]

**Proposed automation**

A nightly job pulls allocated or measured volumes by meter and gas day from the volume and allocation data behind Volume Management and the allocation exception screen. It joins them to active Sitara deal tickets on meter and date. Each meter-day with flow is put into one bucket: covered; no deal; deal expired or outside its term (flow on days the deal does not cover); or parked on Strangers Gas. Next to each meter it shows the nearest existing deal number so the owner can see at a glance whether an extension will do. Exceptions are grouped per deal owner (the trader on the nearest deal, or a desk default when there is none) into one daily digest, rather than one email per meter. Each line carries the meter, the date range, the volume, the suggested deal to extend and three actions: extend, create new, or route to write-off/approval. Items stay open, with their age shown, until a covering Sitara deal appears or someone records a decision. Anything open past a set age, or tied to a payment deadline, is escalated to the desk lead.

- Trigger: Nightly schedule after the day's allocations post, plus an on-demand run during month-end close
- Inputs: allocated and measured volumes by meter and gas day (allocation / Volume Management data); active and recently expired Sitara deal tickets: deal number, meter, start/end dates, counterparty, trader; volumes currently placed on the Strangers Gas contract; Unify path records for the meter and date, to show whether a path exists; a maintained meter-to-desk/owner table for meters that have no deal history
- Outputs: a daily exception digest for each deal owner (e.g. Daren Farmer for HPL deals), listing meter, dates, volume, suggested deal to extend and action buttons; a shared open-exceptions list for volume management, with age, status and owner, replacing individual chase emails; an escalation notice to the desk lead for items older than the threshold or with a payment due date; a month-end summary: meter-days with flow but no deal, and volume parked on Strangers Gas
- Existing systems: Sitara, Unify, Volume Management, allocation exception screen, Feedback Monitor
- New components: nightly meter-versus-deal comparison job, exception classifier (no deal / outside term / strangers gas), owner-routing table (meter and deal to trader or desk), per-owner daily digest email with pre-filled extend/create/write-off requests, open-exceptions tracker with ageing and escalation rules, decision log capturing who approved a write-off or buy back and why

**Implementation steps**

1. With volume management, list the exception types they chase today (no deal, partial-term deal, expired deal, Strangers Gas) and agree how each is defined at the meter-day level.
2. Get read access to Sitara deal tickets (meter, term, trader) and to the daily allocation data behind Volume Management and the allocation exception screen.
3. Build the comparison job and run it in shadow mode for one month next to the current email process. Check that its exceptions match what analysts such as Jackie Young and Aimee Lannou actually raised.
4. Build the owner-routing table from deal history, and send meters with no history to a desk default. Have the HPL and East desk leads confirm it.
5. Turn on the daily digest for one desk (HPL, Daren Farmer) with pre-filled extend/create requests and a status the owner can update with a reply or a click.
6. Add ageing and escalation rules, including a flag for items tied to counterparty payment deadlines.
7. Add the Unify path check so that a deal extension without a path is still shown as open.
8. Extend to other desks, and retire ad-hoc chase emails for exceptions the job already covers.

**Stays manual**

- Deciding whether to extend a deal, create a new one or treat the flow as unauthorized. This is a commercial pricing decision for the trader.
- Approving write-offs to unaccounted-for gas, buy backs and old prior-period adjustments, which need judgment on whether the gas can be invoiced (as in the Adonis case).
- Deciding whether very old periods can be processed at all, e.g. periods before the move to Unify.
- Settling volume disputes with outside parties such as Enerfin or HL&P when their numbers differ from ours.

**Risks**

- The evidence does not show how allocation data is stored or exported, so the effort to join it to Sitara by meter could be higher than estimated. Confirm data access before committing.
- Meter numbers appear in several formats (98-9676, 0986725, 6387). If they are not normalized the job will produce false exceptions. Build a meter key mapping and test it in shadow mode.
- Prior-period re-allocations change volumes after the fact, so an item may reopen. Track by meter-day and show reopened items as such instead of creating duplicates.
- If owner routing is wrong, exceptions bounce between desks just as they do now. Have desk leads review the routing table, and give unassigned items a default owner.
- A large digest could be ignored. Group items per owner, rank by volume and age, and keep the daily list short.
- The evidence comes from a single mailbox (farmer-d), so how often this happens on other desks is uncertain.

## 2. Deal price and invoice discrepancy resolution

Settlements and volume accountants find that a counterparty invoice, statement or payment disagrees with the deal booked in Sitara. Today they email the trader one deal at a time and wait, often right up to an invoice or payment deadline. A pre-invoice match job compares each counterparty line with the Sitara deal price and volume, sends the trader a queue of cases that already hold both figures, and writes the confirmed answer back so Unify can redraft. That removes most of the research and chasing, worth about $110 per month ($1,320 per year).

**Effort:** M · **Success metric:** Median hours from discrepancy detected to trader decision, and the share of invoices redrafted in Unify after being sent, measured per production month before and after rollout

**How it works today**

1. A counterparty statement, invoice or payment arrives, and a settlements or volume accountant compares it by hand with the deal ticket in Sitara, deal by deal. (settlements / volume accounting (e.g. Megan Parker, Katherine Herrera, Lauri Allen)) [farmer-d/logistics/837, farmer-d/logistics/133, farmer-d/logistics/922]
2. When a price, rate or volume differs, or the counterparty does not recognise the deal at all, the accountant writes a free-text email to the trader or logistics desk. The email holds the deal number, both figures and a question about which one is correct. (settlements accountant to trader / logistics desk (Daren Farmer)) [farmer-d/logistics/922, farmer-d/logistics/963, farmer-d/logistics/2083, farmer-d/logistics/124]
3. The trader looks back at the deal, sometimes having to ask the counterparty's trader or a third party for the deal terms, and confirms the price or agrees to dispute it. (trader / desk (Daren Farmer, Darron Giron)) [giron-d/sent/665, farmer-d/logistics/963, giron-d/sent/178]
4. If the trader is unavailable, the accountant escalates or asks someone else to change the deal so the invoice can still go out on time. (settlements accountant / deal entry (Elizabeth Hernandez)) [farmer-d/logistics/177, farmer-d/logistics/1488, farmer-d/logistics/951]
5. The desk corrects the Sitara deal, settlements redraft the invoice in Unify, and a corrected invoice goes to the counterparty. Commercial conditions may first have to be discussed before billing. (desk, then settlements) [giron-d/sent/636, farmer-d/logistics/124, lokay-m/sent_items/45]

**Where it stalls**

- The mismatch is found only after the counterparty's figures arrive. The accountant then has to ask the trader which price is right, under time pressure.
  > We have HSC -0.05 and Mitchell shows HSC - 0.04.
  [farmer-d/logistics/922]
- The counterparty does not have the deal booked at all, so payment stops until the trader goes back to the other side's trader. Invoices are due the same day.
  > Pat Dresner (accountant) at Midcon Texas says she does not show these deals
  [farmer-d/logistics/963]
- Every case depends on one trader. When he is out, the accountant has to route around him to get the invoice out.
  > I think Daren is out for the remainder of the day and I need to send out my invoice this afternoon.
  [farmer-d/logistics/177]
- Sitara was not updated with the month's price, so the Unify invoice had to be redrafted after the fact.
  > The Sitara was not updated for Aug.  I just corrected Sitara.
  [giron-d/sent/636]
- A per-day price differs between the counterparty and Sitara, and it is found only line by line during checkout.
  > For sale deal 707274, DEFS says the price on 4/4 should be 5.25 and we have 5.20 in Sitara.
  [farmer-d/logistics/133]
- The counterparty's deal terms are not available in a structured form, so the desk cannot reconcile its own book in Tagg without chasing a list.
  > Could you ask Steve for a list that has the terms of each deal?
  [giron-d/sent/665]
- The counterparty disputes what the deal covers, and nobody has the counterparty trader's name to hand.
  > Texas General Land office has called and is disputing that this sale is a
  [farmer-d/logistics/2083]

**Proposed automation**

Counterparty statements, invoices and payment remittances are loaded into a staging table as they arrive, one row per deal, day and point. A match job joins each row to the Sitara deal ticket by deal number, or by counterparty, point and production month when no number is given. It compares price or index formula, volume and transport rate, and flags differences above a tolerance, missing deals and zero-rate tickets. Each flagged row becomes a case in a shared discrepancy queue. A case holds the deal number, both figures, the invoice due date and the trader from the Sitara ticket, and is routed to that trader with a backup named for each desk. The trader picks 'Sitara correct', 'counterparty correct' or 'dispute'. Choosing 'counterparty correct' produces a prefilled Sitara change request, and after the change is made settlements are told to redraft in Unify. The same match also runs on the desk's own booked deals before invoices go out, so stale prices like the August Agave case are caught before the invoice rather than after it.

- Trigger: Arrival of a counterparty statement, invoice or payment in settlements, plus a scheduled pre-invoice run in the days before invoices are sent each production month
- Inputs: counterparty statements, invoices and payment remittances (deal number, production month, day, point, volume, price or rate); Sitara deal tickets (deal number, counterparty, trader, price or index formula, volume, term, transport rate); invoice drafts and due dates from Unify; desk booking positions in Tagg where a deal is valued there; desk-to-trader and backup roster
- Outputs: discrepancy cases for the responsible trader, holding both figures, the deal number and the due date; prefilled Sitara deal change requests when the counterparty figure is confirmed; a redraft notice to settlements when the Sitara change is made; a dispute record that settlements send to the counterparty when the Sitara figure is confirmed; a daily aging list of open cases sorted by invoice due date, for the settlements lead
- Existing systems: Sitara, Unify, Tagg
- New components: counterparty statement intake and staging table (manual upload at first, with a parser for recurring statement layouts), deal match and tolerance comparison job, discrepancy case queue with trader routing and backup escalation, decision form (Sitara correct / counterparty correct / dispute) that produces a prefilled deal change request, pre-invoice stale-price check and aging report

**Implementation steps**

1. Pull a sample of recent counterparty statements from settlements (Midcon, Mitchell Gas Services, DEFS, Hesco, Southern Union, Texas General Land Office) and list the fields each one carries.
2. Build the staging table and a manual upload template, with deal number, production month, day, point, volume and price, so accountants can load any statement on day one.
3. Write the match job against a read-only Sitara extract. Join by deal number first, then by counterparty, point and month, and agree price and volume tolerances with settlements.
4. Set up the case queue. Route each case by the trader on the Sitara ticket and assign a named backup per desk for when the trader is out.
5. Add the decision form. Have 'counterparty correct' produce a Sitara change request for deal entry, and send settlements a Unify redraft notice once Sitara is updated.
6. Add the scheduled pre-invoice run that flags zero-rate tickets and months with no price entered before invoices are drafted.
7. Run alongside the current email process for one production month, compare the cases with the emails actually sent, then switch settlements over to the queue.
8. Add parsers for the highest-volume counterparty statement layouts after the pilot.

**Stays manual**

- Deciding which price is correct: only the trader knows what was agreed, as the Mitchell and DEFS cases show.
- Approving and keying any change to a Sitara deal ticket, which stays under existing deal-entry controls.
- Contacting the counterparty's trader when they have no record of the deal or dispute what it covers (Midcon, Texas General Land Office).
- Commercial judgments such as holding billing until side conditions are discussed (the Transwestern capacity release case).
- Penalty or imbalance charges that the counterparty raises and that are not tied to a single deal line.

**Risks**

- Counterparty statements come in many layouts and some carry no deal number. Mitigate with a manual upload template first, and add parsers only for the high-volume layouts.
- Index-based prices (for example HSC minus a differential) need formula comparison rather than a single number. Compare the formula and the differential, and flag any case where the index cannot be resolved for a human to look at.
- Tolerances that are too tight flood traders with noise. Tune them during the parallel month and track how often traders mark cases 'Sitara correct'.
- The evidence does not show how Unify or Tagg export data or what access is available. Confirm extract access with IT before committing to the M estimate.
- Traders may keep answering by email. The settlements lead should send email requests back to the queue, and the aging report makes overdue cases visible.
- The value estimate rests on a sampled median handling time. Measure actual time per case during the pilot.

## 3. Real-time congestion and deal settlement reconciliation

Today the real-time desk finds settlement breaks by hand. Bill Williams compares Enpower deals, CAPS schedules, position manager, the inc sheet and CAISO congestion and reserve awards, then emails settlements (Jim Reyes, Virginia Thompson, Heather Dunton) one hour and one deal at a time. Some of these breaks, such as PMAs and price corrections, stay open for weeks. The fix is a daily job that matches Enpower against CAPS and CAISO results by hour, book and schedule ID, and sends both teams one variance list each morning. It catches breaks before the P&L is struck and replaces many one-off emails with a single tracked list.

**Effort:** M · **Success metric:** median age of open settlement breaks (PMAs, price corrections, schedule mismatches) in the break log, and the share of breaks first found by the morning job rather than by email from the desk or settlements

**How it works today**

1. After each operating day the real-time trader looks over what happened: CISO declines, incs and decs, cuts, misentered schedules. Each item is written up as a free-text email to settlements or the scheduling group, listing hour ending, schedule ID and book. (real-time trader (Bill Williams)) [williams-w3/sent_items/514, williams-w3/sent_items/510, williams-w3/sent_items/425]
2. The trader works out the expected revenue for congestion relief and replacement reserve capacity by hand and emails the figure so settlements can check it against the CAISO statement. (real-time trader) [williams-w3/sent_items/322, williams-w3/sent_items/431, williams-w3/sent_items/90]
3. The next morning the trader gets the DPR, runs a BOM SAR, spots double or wrong deal entries, zeroes them out in Enpower and emails settlements to explain the revenue impact. (real-time trader / settlements (Heather Dunton)) [williams-w3/sent_items/453]
4. Annuities between books (for example ST-CALI to ST-WHOURLY) are agreed with the desk head and passed to settlements by email to book. (real-time trader / settlements) [williams-w3/sent_items/481, williams-w3/sent_items/387]
5. When the monthly PMA arrives, the trader checks each adjustment against Enpower and the inc sheet. Where they disagree he escalates to settlements and asks for a meeting to true it up. (real-time trader / settlements (Virginia Thompson)) [williams-w3/sent_items/442, williams-w3/sent_items/441, williams-w3/sent_items/426]
6. Position manager variances, from schedule errors or counterparties such as Enron Canada, are reported by email. Schedule corrections arrive from other desks with instructions to change load zones until the position is flat. (real-time trader / scheduling) [williams-w3/sent_items/291, williams-w3/inbox/126]
7. Disputed trades with nothing written down are settled by having a recorded-line tape pulled. (real-time trader / tape custodian (Chip Cox)) [williams-w3/sent_items/428, williams-w3/sent_items/426]

**Where it stalls**

- A price correction sits in Enpower but the revenue never flows through. The break carries over from one month to the next and needs an escalation to get trued up.
  > The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753).
  [williams-w3/sent_items/442]
- A PMA from January is challenged months later because settlement notes disagree with Enpower and the inc sheet. Nothing compared the two sources when the change was made.
  > On TransAlta deal #509285, your notes indicate that mw volumes for HE 23 and HE 24 were reduced by 95 mws each hour.
  [williams-w3/sent_items/441]
- The PMA tool appears to charge again when a counterparty is changed, so the desk has to check every counterparty correction by hand.
  > Are we being charged for each counterparty again (like EES and ST-Cali last month), if so, we need to fix this flawed tool.
  [williams-w3/sent_items/442]
- Nothing was recorded for a disputed deal, so working it out means pulling tapes or tracking down the trader, and the BOM PMA is still open.
  > We could pull tapes?  Ask the person who did the deal?  There is nothing in notebooks.
  [williams-w3/sent_items/426]
- Position manager reports variances that disappear in the detail view, so the desk can't rely on it and checks positions by hand.
  > Position manager is also not working properly, it is reporting a variance at Pacificorp system border ? and at Palo Verde.
  [williams-w3/sent_items/291]
- Congestion revenue can't be confirmed from CAISO data because the CAISO site went down. The desk relies on a verbal confirmation on a recorded line.
  > HE18-although it shows nothing from the CAISO on their site (their server went down) is the same as HE17-the CAISO specifically relayed this to me on a recorded line.
  [williams-w3/sent_items/90]
- Double deal entry is caught only the next morning, after the DPR and a BOM SAR, and then has to be reversed by hand.
  > We had some double deal-entry last night under the ST-WBOM book.
  [williams-w3/sent_items/453]
- The counterparty enters a schedule wrong, so CAPS and the actual energy flow disagree until the desk finds it and asks for a manual fix.
  > For HE 11 and HE12, Danielle at the CISO misentered our schedule.
  [williams-w3/sent_items/510]

**Proposed automation**

Each morning, after the DPR is produced, a reconciliation job pulls the previous day's Enpower deals by book (ECTRT, ST-WBOM, ST-CALI, ST-WHOURLY and others) and the CAPS final schedules by schedule ID and hour ending. It also loads whatever CAISO congestion and replacement reserve award data the desk can export. It matches records on schedule ID, hour ending and counterparty, then flags volume or direction mismatches (for example firm import against n-firm export), duplicate deals with the same terms, deals not in CAPS, CAPS schedules not in Enpower, and award hours with no matching revenue line. The job estimates expected congestion and capacity revenue from awarded MW and clearing price, which replaces the trader's hand calculation. Every variance goes into a running break log with an owner, a status and age. The log stays open until settlements closes it, so prior-month items such as unposted PMAs and price corrections stay visible instead of getting lost in email threads. In month-end mode, PMA lines are checked against the Enpower deal history and the inc sheet, and any adjustment those sources don't support is flagged before it is accepted.

- Trigger: Daily schedule, after the DPR is published each morning. A month-end run starts when the PMA file is received.
- Inputs: Enpower deal records for the prior day by book, deal number, counterparty, price, volume and hour ending; CAPS final schedules and position manager positions by schedule ID and hour ending; DPR and BOM SAR output; CAISO congestion and replacement reserve awards and prices, where an export is available; inc sheet entries for incs, decs and declines; monthly PMA lines from settlements; agreed annuities between books
- Outputs: a morning variance list by hour, book and schedule ID, emailed to the real-time desk and settlements; an expected-revenue line for each congestion or reserve award hour, for settlements to check against the CAISO statement; a running break log with owner, status and age, including open prior-month PMAs; a month-end PMA check that flags adjustments not supported by Enpower or the inc sheet
- Existing systems: Enpower, CAPS, position manager, inc sheet, DPR, BOM SAR
- New components: daily Enpower-to-CAPS matching job keyed on schedule ID, hour ending and book, duplicate-deal detector (same book, counterparty, hour and volume entered more than once), CAISO award loader and expected-revenue calculator for congestion and replacement reserves, break log (shared table) with owner, status, age and links to the deals involved, month-end PMA checker that compares PMA lines with the Enpower deal history and the inc sheet, morning variance email or report

**Implementation steps**

1. Collect last year's reconciliation emails from the real-time desk and list the break types: schedule direction or firmness errors, double entry, unposted price changes, congestion and reserve revenue, annuities and PMA disputes. Agree with settlements which ones the job must catch.
2. Get read access to Enpower deal extracts and to CAPS final schedules. Confirm the shared keys (schedule ID, hour ending, book, counterparty) and how ECTRT and ECTSTSW schedules map to Enpower books.
3. Build the matching job and the duplicate-deal detector. Run them alongside the existing DPR and BOM SAR check for two to four weeks and compare their output with the breaks the desk actually reports.
4. Add the CAISO award loader and expected-revenue calculation. Where no data feed exists, allow a manual upload of the desk's award file.
5. Set up the break log with settlements (Virginia Thompson, Heather Dunton, Jim Reyes) as owners of closing items. Load the currently open PMA and price-correction items.
6. Add the month-end PMA checker and run it on the next PMA before the desk reviews it.
7. Switch the morning email on for the real-time desk and settlements. Retire the free-text adjustment emails for any break type the job reliably catches.

**Stays manual**

- Deciding the correcting entry, zero-out or PMA amount. Settlements and the desk own the P&L effect and may need to talk to the counterparty.
- Agreeing annuities between books, which needs the desk head's approval.
- Disputes with the CISO/CAISO or counterparties over declined bids, cuts or misentered schedules, which need calls on recorded lines.
- Pulling tapes to settle disputed deals with nothing written down.
- Telling a real variance apart from a position manager display fault.

**Risks**

- The evidence doesn't show whether Enpower or CAPS can export data automatically or in what format. Confirm extract access before committing, or start from scheduled report exports.
- Position manager itself showed false variances. The job should compare source records, not position manager totals, and treat position manager only as a cross-check.
- CAISO data can be missing (their server went down). The job must mark those hours unconfirmed, not zero, so it doesn't report false breaks.
- Schedule IDs and books are entered inconsistently, for example ECTRT against ECTSTSW. Matching rules need a maintained mapping table or the job will generate noise.
- All evidence comes from one mailbox (williams-w3), and the calculated handling value is small (about $77 a month, $924 a year at $85/h). The case rests on catching breaks earlier rather than on hours saved. Scope it as a lightweight script first.
- The evidence doesn't describe the PMA file layout. The month-end checker may need a manual import step at first.

## 4. Real-time desk standing procedures

The real-time desk lead (Bill Williams) runs the Portland real-time desk's standing procedures as a stream of one-off emails to the shift group. These cover Enpower deal entry, swaps, cut handling, hourly generator checkouts, customer finals in CAPS or FSP, and transmission scheduling, and some have to be re-sent because traders do not follow them. The fix is a single maintained Real-Time Desk Procedures checklist, organised by topic and reviewed at the start of every shift, plus a short change-notice template, so the lead edits one document instead of re-sending instructions. The main benefit is fewer repeated reminders and fewer missed steps that cause penalties, disputes or complaints from counterparties.

**Effort:** S · **Success metric:** Number of reminder or re-sent instruction emails from the desk lead to the shift group per month, plus the number of counterparty escalations about missed hourly checkouts or outage calls, compared before and after rollout.

**How it works today**

1. A rule or procedure change comes from outside the desk (a CAISO/FERC change, a request from volume management, a CAPS outage, a forwarded idea), and the desk lead forwards it to the shift group with his own instructions on top. (real-time desk lead) [williams-w3/sent_items/449, williams-w3/sent_items/413, williams-w3/sent_items/473, williams-w3/sent_items/444]
2. The desk lead emails step-by-step Enpower procedures for particular situations, such as swaps through the swap function, deal #146517 for PGE transmission, and Colstrip cuts with index buys, a BPA wheel, linked deals and a flat check in real time position manager. (real-time desk lead) [williams-w3/sent_items/432, williams-w3/sent_items/434, williams-w3/sent_items/338]
3. Positions and dispatch instructions that only apply for a while (EPE lending shorts by book, Sundance 3 and 4 dispatch for Enron Canada with phone numbers and the dispatch log) go out as separate emails for certain dates. (real-time desk lead / Kate Symes (deal details)) [williams-w3/sent_items/380, williams-w3/sent_items/365, williams-w3/sent_items/386]
4. Shift traders carry out the instructions during their shift: they call CAISO for outages, call Grays Harbor and Frontier every hour and report actuals to BPA, sign off the hour in the services book, and handle cuts using the attached cut sheet. (shift traders (shift.portland group)) [williams-w3/sent_items/408, williams-w3/sent_items/357, williams-w3/sent_items/369]
5. When a step is missed or forgotten, the lead re-sends a reminder or escalates after a counterparty complains (BPA service complaint, schedule changes not called in, cut notes not copied to him). (real-time desk lead) [williams-w3/sent_items/487, williams-w3/sent_items/471, williams-w3/sent_items/357]

**Where it stalls**

- Instructions get lost in inboxes, so the same content is re-sent instead of being looked up in one place.
  > Ryan sent this email out once already, here it is again.
  [williams-w3/sent_items/444]
- Standing rules are not followed between reminders, so the lead has to email the shift group again about the same rule.
  > These schedule changes must be called in.  Just a reminder.
  [williams-w3/sent_items/487]
- The distribution rules for EES sheets and cut notes are not consistently applied, so the lead misses information and has to send a correction.
  > I should be copied on the EES sheets, and any cut notes to volume managament, the services desk, or other traders.
  [williams-w3/sent_items/471]
- An hourly checkout procedure was not done consistently, and the desk found out from a counterparty escalation that threatened the services business.
  > Warren explained to me the necessity and importance of calling in and reporting the actual amount of energy generated by Grays Harbor and Frontier EVERY hour.
  [williams-w3/sent_items/357]
- Deal entry done the wrong way in Enpower (annuities instead of swaps) has caused downstream disputes that dragged on for months.
  > Swaps have caused disputes that have dragged on for months in the past, so call me with any questions.
  [williams-w3/sent_items/432]
- A nightly deadline set by volume management is passed on only as a forwarded email, with nothing in a shift routine to make sure it gets done.
  > Volume management needs us to create customer finals by 3AM each night in CAPS or FSP.
  [williams-w3/sent_items/413]

**Proposed quick win**

Gather the standing instructions now spread across the lead's emails into one Real-Time Desk Procedures checklist, kept as a single shared document that the shift.portland group can reach. It has fixed sections: Start-of-shift checks, Hourly duties (generator checkouts and services book sign-off), Enpower deal entry (swaps, transmission deals, specific deal numbers), Cuts (the existing cut sheet plus the Colstrip steps), CAISO rules (price cap, outage calls, wheeling fee components), Nightly deadlines (customer finals by 3AM in CAPS or FSP), Distribution list rules, and a Temporary instructions page with start and end dates (EPE lending, Sundance dispatch, CAPS outages). Every trader goes through the Start-of-shift section and the Temporary instructions page at the start of each shift. When something changes, the lead edits the matching section and sends a short change-notice email from a fixed template that names the section and the change, instead of rewriting the whole procedure. Questions keep going to the lead by phone, as they do today, and any answer that becomes a rule is added to the checklist.

- Trigger: The start of each shift, when the incoming trader reviews the checklist, and any new rule or procedure change that reaches the desk lead (a CAISO/FERC change, a volume management request, a system outage, a new trade arrangement), which prompts an edit to the checklist and a change notice.
- Inputs: standing instruction emails from the desk lead (Enpower procedures, CAISO rules, cut handling, checkouts); the existing cut procedures sheet attached to the CUTS email; deadlines from volume management (customer finals by 3AM); temporary arrangements with dates (EPE lending books and deal numbers from Kate, Sundance dispatch window)
- Outputs: the Real-Time Desk Procedures checklist for shift traders; a start-of-shift checklist section with the hourly and nightly duties; a dated Temporary instructions page; short change-notice emails to the shift group naming the section that changed
- Existing systems: Enpower, CAPS, FSP, services book, dispatch log, lotus notes
- New components: Real-Time Desk Procedures checklist document (sectioned by topic), start-of-shift checklist section, Temporary instructions page with start and end dates, change-notice email template (section, what changed, effective date, owner), shift sign-off line confirming the checklist was reviewed

**Implementation steps**

1. Go through the lead's past instruction emails to the shift group and pull every standing rule into a draft, grouped into the fixed sections (Start-of-shift, Hourly duties, Enpower deal entry, Cuts, CAISO rules, Nightly deadlines, Distribution rules, Temporary instructions).
2. Put the existing cut procedures sheet and the Colstrip cut steps under Cuts, and write the swap, PGE transmission deal and EPE lending entry rules as numbered Enpower steps.
3. Write the start-of-shift checklist with the time-bound duties: hourly Grays Harbor and Frontier checkouts reported to BPA and signed off in the services book, CAISO outage calls, customer finals by 3AM in CAPS or FSP, and who gets copied on EES sheets and cut notes.
4. Save the document where every shift trader can reach it, and link to it from the shift.portland group's standing materials.
5. Write the change-notice email template, and agree that the lead updates the document first and then sends the notice, instead of a free-form procedure email.
6. Go through the checklist with the group at the next real-time meeting and have each trader confirm in the shift sign-off that they reviewed it.
7. Review the Temporary instructions page weekly and remove entries whose end date has passed.

**Stays manual**

- Deciding trading strategy and when a rule applies (buying over the price cap for reliability, dec bids or buy-backs with generators), because these are market judgments the lead makes.
- The phone calls themselves (to CAISO, BPA, the generators and the power pool), because the evidence says they must be called in until the generators are automatically metered.
- Handling unusual cuts or outages that the checklist does not cover, which still go to the lead or Les by phone.
- Workplace conduct issues such as after-hours behavior, which the lead handles directly and which do not belong in a procedures checklist.

**Risks**

- The checklist goes stale if the lead keeps sending free-form emails. Mitigate by making the change-notice template the only route and checking at the weekly meeting that the document matches recent notices.
- Traders may skip reading it. Mitigate with the shift sign-off line and by keeping the start-of-shift section to one page.
- The evidence comes from one mailbox (williams-w3) and does not show where shared desk documents are kept or whether a shared drive exists. Confirm the location with the desk before rollout.
- Phone numbers, passwords and deal numbers in the instructions change, and some (for example the power pool login) should not go in a widely shared document. Keep credentials out and put a review date on contact details.
- At the computed value of $76 a month ($912 a year), the case rests on fewer penalties, disputes and counterparty complaints rather than on email time saved. Those avoided costs are not quantified in the evidence.

## 5. Weekly California capacity report

Every week Michelle Lokay builds the California Capacity Report by hand: Transwestern and El Paso deliveries to California, capacity utilization by delivery point, Gas Daily prices with day-over-day changes, and Enron basis. She types it into an email to the same Transwestern commercial distribution list, and she has had to send a correction when the week label was wrong. A small weekly script would compute the averages and percentages, fill in the fixed email layout with the right week dates, and leave a draft for her to check and send. That removes the retyping and the arithmetic that cause errors, but the work is only worth $73 a month ($876 a year), so the build should stay small.

**Effort:** S · **Success metric:** Share of weekly California Capacity Reports sent from the generated draft without a follow-up correction email, and the analyst's minutes per report measured before and after the switch.

**How it works today**

1. The analyst gathers the week's average Transwestern deliveries to California, San Juan lateral throughput and total East deliveries, and works out percent of capacity by hand. (Transwestern marketing analyst (Michelle Lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/131]
2. The analyst collects El Paso's average deliveries to California, broken out by PG&ETop, SoCalEhr and SoCalTop, each with its capacity, deliveries and utilization percent. Capacity figures are kept up to date by hand; SoCalEhr changed from 1042 to 1250 MMBtu/d between October and December. (Transwestern marketing analyst (Michelle Lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/55]
3. The analyst copies the latest posted Gas Daily prices (SoCal gas, PG&E, TW San Juan or San Juan non-Bondad, TW Permian) with their daily changes, using Thursday's prices when the report goes out on a Thursday and marking any missing points as n/a. (Transwestern marketing analyst (Michelle Lokay)) [lokay-m/sent_items/30, lokay-m/sent_items/67, lokay-m/sent_items/131]
4. The analyst adds Enron Online bases (Perm-CA, SJ-CA, SJ-Waha, Perm-Waha). In late 2001 this became a one-month 'Enron basis', then 'n/a', and by February 2002 the section was dropped. (Transwestern marketing analyst (Michelle Lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/63, lokay-m/sent_items/79]
5. The analyst types the subject 'California Capacity Report for Week of MM/DD-MM/DD' and sends the email to the fixed Transwestern commercial distribution (Steven Harris, Kimberly Watson, Lorraine Lindberg, TK Lohman, Lindy Donoho), usually on Friday. When the week label is wrong, she sends a follow-up correction. (Transwestern marketing analyst (Michelle Lokay)) [lokay-m/sent_items/40, lokay-m/sent_items/46, lokay-m/sent_items/146]

**Where it stalls**

- Every figure and percentage is retyped into the email each week. The process is flagged as stalled because the whole report waits on one person compiling it once a week (median gap of about 165.8 hours between sends), and nothing checks the numbers.
  > Transwestern's average deliveries to California were 945 MMBtu/d (87%), with San Juan lateral throughput at 865 MMBtu/d.
  [lokay-m/inbox/10]
- The week date range in the subject is typed by hand. A wrong range went out to the whole distribution and needed a second correction email.
  > Sorry, the effective date for this new report is 01/07-01/11.
  [lokay-m/sent_items/46]
- Capacity numbers used to work out utilization are kept by hand and changed between reports (SoCalEhr 1042 in October, 1250 from December). A stale capacity number quietly skews every percentage.
  > SoCalEhr, capacity 1042 MMBtu/d, deliveries of 707 MMBtu/d (68%)
  [lokay-m/inbox/10]
- This week's report was flagged as stalled. The delivery and throughput figures are typed in again from scratch rather than taken from a data feed, so each send repeats the same manual compile.
  > Transwestern's average deliveries to California were 1011 MMBtu/d (93%), with San Juan lateral throughput at 872 MMBtu/d.  Total East deliveries averaged 337 MMBtu/d.
  [lokay-m/sent_items/86]

**Proposed automation**

A weekly script runs Friday morning (or Thursday in a short week). It takes the week's daily delivery figures for Transwestern and El Paso, a small capacity table kept under version control, and the latest posted Gas Daily prices. From these it works out the weekly averages, utilization percentages and price changes. It fills in the exact layout used in the emails today: the Transwestern paragraph, the El Paso breakdown by delivery point, the Gas Daily price table with 'n/a' for missing points, and an optional basis section. It builds the subject 'California Capacity Report for Week of MM/DD-MM/DD' from the calendar, so the week label cannot be mistyped. The output is an unsent draft addressed to the existing distribution list. The analyst checks it, adds any commentary and sends it. Sanity checks highlight values outside normal ranges, such as utilization over 100% (one week legitimately showed 103%) or a week-over-week jump, so they get a second look before sending.

- Trigger: Weekly schedule: Friday morning, or the last business day of a short week (the evidence shows Thursday sends that use Thursday's posted Gas Daily prices).
- Inputs: Daily Transwestern deliveries to California, San Juan lateral throughput and East deliveries for the report week; Daily El Paso deliveries to California at PG&ETop, SoCalEhr and SoCalTop; Capacity reference table per delivery point (e.g. PG&ETop 1140, SoCalEhr 1250, SoCalTop 540 MMBtu/d), with an effective date; Posted Gas Daily prices for SoCal gas large pkgs, PG&E large pkgs, TW San Juan / San Juan (non-Bondad) and TW Permian, current and prior day; Optional Enron Online basis quotes (Perm-CA, SJ-CA, SJ-Waha, Perm-Waha); Distribution list: steven.harris, kimberly.watson, lorraine.lindberg, tk.lohman, lindy.donoho
- Outputs: Draft 'California Capacity Report for Week of MM/DD-MM/DD' email in the current format, for the analyst to check and send to the Transwestern commercial team; A short list of out-of-range values and missing inputs (e.g. a price that is n/a, utilization over 100%) shown above the draft for the analyst; A weekly CSV of the computed numbers, so trends no longer have to be pieced together from old emails
- Existing systems: Gas Daily, Enron Online, Transwestern, El Paso
- New components: Weekly scheduled report script (averages, utilization percentages, price changes), Capacity reference table with effective dates, under version control, Email template that reproduces the current report layout, with the subject's week range built from the calendar, Input loader: a simple drop-in spreadsheet or CSV per week at first, replaced by direct feeds if they turn out to be available, Range checks and a missing-data list shown with the draft, Weekly CSV history of the report figures

**Implementation steps**

1. Sit with the analyst for one report cycle to record where each number actually comes from (pipeline flow data, Gas Daily, basis quotes). The emails do not name the source systems.
2. Write down the current report layout as a template, using a recent email (e.g. the week of 03/11-03/15) as the reference version.
3. Build the capacity reference table with effective dates, seeded from the figures in recent reports, and give one owner responsibility for updating it.
4. Write the script so it reads one weekly input sheet (daily volumes plus Gas Daily prices), computes averages, percentages and day-over-day price changes, and renders the draft email with a subject built from the calendar.
5. Add range checks (utilization over 100%, week-over-week jumps, missing price points shown as n/a) and display the results with the draft.
6. Run the script alongside the manual report for three to four weeks and compare it figure by figure with what the analyst sends.
7. Switch over: the script produces the draft, and the analyst checks it and sends it to the existing distribution list.
8. Only if it is cheap, replace the manual input sheet with direct pulls from the flow and price sources identified in step 1.

**Stays manual**

- Final review and sending, because the analyst owns the numbers that go to the commercial team and is the one who spots operational anomalies.
- Commentary or context on unusual weeks, such as deliveries above 100% of capacity or sharp price moves, because that takes market judgement.
- Updating the capacity table when a pipeline's posted capacity changes, because that is a business fact a person has to confirm.
- Deciding which price points and basis sections to include, because the evidence shows the format changing (basis dropped, 'San Juan (non-Bondad)' replacing 'TW San Juan').

**Risks**

- The emails do not say where the delivery and capacity data come from. If no machine-readable source exists, the script will run on a manually filled input sheet and save less time. Confirm the sources in step 1 before building any feed.
- Gas Daily is a licensed publication. Pulling prices automatically may be restricted, so if needed the price table stays a manual paste into the input sheet.
- A stale capacity table would quietly skew every utilization percentage. To guard against this, store an effective date for each capacity figure and flag any value not reviewed recently.
- Totals made by the script could differ from the analyst's own method (for example, how she handles a short holiday week like 12/26-12/28). The parallel run catches these differences before switching over.
- The value is small ($73 a month, $876 a year) and the evidence comes from one mailbox over about five active months. Spending more than a few days on this would not pay back, so keep it a script and avoid building an integration.
- The report format kept changing during the period observed (the Enron basis section went away). The template has to be easy to edit, or it will go out of date.

## 6. Meter volume and allocation variance resolution

Settlements, volume management and logistics staff find meter allocation exceptions one at a time: a meter with flow but no deal, POPS feeding zero volumes to Sitara, or a desk-to-desk volume variance. Each one becomes its own email thread to Daren Farmer's logistics desk and can wait days or weeks. A daily variance job would compare measured flow, POPS confirmed noms and allocations, and Sitara deals per meter, then route each exception with its supporting data to the right owner. Analysts would work one ranked exception list instead of researching and chasing each meter by email.

**Effort:** M · **Success metric:** Median days from a meter variance first appearing (flow, POPS or Sitara mismatch) to its disposition, together with the monthly count of variance-research emails to the logistics desk and the number of POPS-to-Sitara zero-feed days caught within 24 hours.

**How it works today**

1. A settlements or volume analyst finds an unexplained volume at a meter (UA4 balance, measured flow with no deal, or a short delivery), often months after the gas flowed. (settlements / volume management analyst) [farmer-d/logistics/595, farmer-d/logistics/622, farmer-d/logistics/682]
2. The analyst researches by hand across OSS, CPR and MIPs measurement statements to see whether a deal or measurement exists for the meter and month. (settlements analyst) [farmer-d/logistics/595, farmer-d/logistics/622, farmer-d/logistics/1483]
3. The analyst emails the logistics desk (mostly Daren Farmer) or the scheduler to ask whether a deal is missing, what a nomination was for, or how a short day should be handled. (analyst to logistics desk / scheduler) [farmer-d/logistics/622, farmer-d/logistics/754, farmer-d/logistics/902]
4. Feed failures between POPS and Sitara come to light only when someone reviews imbalance numbers. The zero volumes then have to be overridden by hand so the P&L is right. (volume management / imbalance reviewer) [farmer-d/logistics/925]
5. Open variances pile up in periodic lists (the interdesk/interconnect report, the feedback error report), each with a named owner working it through emails and calls. (volume management lead / accounting) [farmer-d/logistics/1185, farmer-d/logistics/1351]
6. Once a cause is agreed, staff zero confirmed noms, change the allocation method, reallocate the meter in POPS, and extend or create deals in Sitara. These steps are done by hand and handed off by phone. (volume management, scheduler, Global Facilities) [farmer-d/logistics/1439, farmer-d/logistics/1185, farmer-d/logistics/1483]
7. People who opened an item but got no answer send follow-ups, or escalate when a counterparty calls asking to be paid. (requester / accounting) [farmer-d/logistics/739, farmer-d/logistics/1241, farmer-d/logistics/2089]

**Where it stalls**

- Analysts cannot tell from their own systems whether a deal exists upstream in CPR, so each meter needs a question to the logistics desk.
  > Daren is there a deal in CPR which may not have fed over to OSS?
  [farmer-d/logistics/622]
- A broken POPS-to-Sitara feed goes unnoticed for days. Purchase volumes sit in UA4 instead of the P&L until someone reviewing imbalances spots it.
  > is that POPS has fed 0 volumes back to Sitara on some
  [farmer-d/logistics/925]
- Resolution waits on a reply from one person (Daren), and the receivable balance stays open in the meantime.
  > receivable balance, then we are waiting on a response from Daren.
  [farmer-d/logistics/1241]
- Variances pile up as a standing list of open items with a cleanup deadline, rather than being resolved as they occur.
  > Below is a list of the major items that are still outstanding on the
  [farmer-d/logistics/1185]
- A confirmation on a date the deal does not cover makes the allocation prorate wrongly, and nobody catches it until the feedback error report is worked.
  > When Karen allocates the actual 10,000 it is prorating 5,000 for each day
  [farmer-d/logistics/1351]
- Flow with no matching deal is surfaced only by an external party demanding payment, not by an internal check.
  > I am getting several phone calls from Alpine Resources demanding to be paid
  [farmer-d/logistics/2089]
- A meter allocating incorrectly is found only after it has already added to the current month's UA4 problem.
  > Please verify CP&L back to the first of June.
  [farmer-d/logistics/1191]
- Allocation exceptions are cleared one by one, by hand, each needing someone to verify the flow.
  > This is the last allocation exception I have to clear.
  [farmer-d/logistics/1483]

**Proposed automation**

A daily variance job pulls, for every meter and gas day, the measured volume (MIPs measurement), the confirmed noms and allocations in POPS, and the deals and volumes in Sitara (with OSS/CPR for older production months). It applies a fixed set of rules: flow with no valid deal on that day, a confirmation on a date outside the deal's term, zero volumes fed from POPS back to Sitara where flow exists, delivery noms on receipt meters, confirmed volume not matching allocated actuals beyond a tolerance, and a UA4 balance growing at a meter. Each exception goes on one shared list with the meter, month, volumes on each side, the prior month for context and the rule that fired. It is routed by rule to an owner: logistics desk for missing or invalid deals, scheduler for nomination issues, volume management for allocation and feed problems. Owners record a disposition on the item instead of starting an email thread. Items left open past an age threshold are flagged on a daily digest, so follow-ups and escalations are no longer needed.

- Trigger: Daily schedule after the POPS allocation run and the POPS-to-Sitara volume feed. A month-end run also covers the full production month.
- Inputs: Measured meter volumes by gas day (MIPs measurement statements); POPS confirmed nominations, allocation method and allocated volumes per meter and contract; Sitara deal tickets: term dates, meter, volumes fed back from POPS; OSS and CPR deal records for prior production months; UA4 balances by meter; Meter-to-owner routing table (desk, scheduler, analyst)
- Outputs: Daily exception list per meter and month, with volumes from each source, the prior month, and the rule that fired, for volume management and settlements analysts; Routed exception items for the logistics desk (missing or invalid deal), schedulers (nomination on wrong meter type, short delivery) and volume management (feed failure, allocation mismatch); Same-day alert when POPS feeds zero volumes to Sitara for deals with measured flow; Aging digest of open exceptions, with disposition history, for the volume management lead
- Existing systems: POPS, Sitara, OSS, CPR, MIPs
- New components: Daily meter variance comparison job (measurement vs POPS vs Sitara), Rule set with tolerances (no-deal flow, out-of-term confirmation, zero feed, delivery nom on receipt meter, confirmed vs actual mismatch, UA4 growth), Exception list with owner routing and a disposition field (fix deal, reallocate, accept variance, counterparty dispute), Feed-health check that alerts on zero POPS-to-Sitara volumes, Aging digest replacing manual follow-up emails

**Implementation steps**

1. Inventory the extract points: which POPS, Sitara and measurement tables or reports can be read daily, and how OSS/CPR history can be reached. Confirm read-only access with each system owner.
2. Build the meter/day join keyed on meter number, contract and deal (Sitara ticket and track id), and test it against the known cases in the evidence (meters 1441, 986782, 984132, Valero Texoma #71).
3. Write the first three rules (flow with no valid deal, out-of-term confirmation, zero POPS-to-Sitara feed). Set tolerances with volume management, then backtest on one closed month.
4. Build the meter-to-owner routing table with the logistics desk, schedulers and volume management. Add the disposition field and exception list.
5. Run in shadow mode for one month next to the existing interdesk/interconnect report and feedback error report. Compare what each catches and tune false positives.
6. Add the remaining rules (delivery noms on receipt meters, confirmed vs actual mismatch, UA4 growth) and the aging digest.
7. Go live: analysts log new variance questions as dispositions on exception items instead of emailing the desk. Review open-item aging weekly.

**Stays manual**

- Deciding which volume is correct when sources disagree (e.g. pipeline vs HPL Measurement custody transfer) is a commercial and contractual judgment for volume management.
- Deciding whether to create, extend or change a deal, or arrange a buyback, stays with the logistics desk and traders.
- Reallocations, zeroing confirmed noms and facility changes in POPS stay human-executed, because they ripple into Gas Control and settlements (the evidence shows a multi-party, phone-coordinated sequence).
- Disputes and payment claims from counterparties, and questions needing Legal input, stay with people.
- Choosing tolerances and approving which rules route to whom.

**Risks**

- The evidence does not show whether POPS, Sitara, OSS, CPR or MIPs offer usable extracts or interfaces. Integration could be harder than estimated, so confirm access before committing.
- Measurement is often restated or arrives late (outside-measured meters, prior-period adjustments). The job should re-run prior months and label items as provisional until measurement is final.
- Tolerances set too tight would flood analysts with noise and they would go back to email. Start with high-value rules, backtest, and tune during shadow mode.
- Meter numbering and facility changes (e.g. meter 986892 replaced by 980439) can break the join. Maintain a meter-change mapping fed by the facility change process.
- The measured benefit is small ($68/month, $816/year at $85/hour), because only about 4 messages a month are counted. The P&L exposure from undetected UA4 and feed failures is not priced here and is the stronger case, so it should be validated separately.
- If owners keep resolving items by phone and email, dispositions go unrecorded and the aging digest misleads. Make the disposition entry part of closing an item.

## 7. Sitara deal ticket entry and correction requests

Traders, field-services staff, storage and accounting email the logistics desk (mainly Daren Farmer) free-form requests to create, zero out, cut off, re-price or path Sitara deals. These requests often lack key fields, have no stated close deadline and never get a deal-number confirmation back, so requesters chase them for days. The fix is a standard Sitara deal request template, a matching confirmation reply that returns the Sitara number, and a short pre-close checklist. Together they remove the clarification and follow-up rounds (estimated at $65 per month, $780 per year, at $85 per hour).

**Effort:** S · **Success metric:** Share of Sitara deal requests to the logistics desk that receive a follow-up or 'have you had a chance' email before confirmation, plus the count of deals found unpathed at month start, compared before and after rollout.

**How it works today**

1. A requester emails the desk a free-form request for a new deal ticket. Counterparty, meter, volume and pricing appear in whatever layout the sender chooses, and sometimes there is only a one-line ask with no details. (producer services / field origination (e.g. Vance Taylor, Susan Smith), Volume Management) [farmer-d/logistics/765, farmer-d/logistics/789, farmer-d/logistics/679]
2. For multi-party transactions such as storage purchases, one email asks several desks to enter matching Sitara deals on the same day, and asks treasury to wire payment. (storage book / commercial lead) [farmer-d/logistics/1082]
3. Change requests (zero out expected volume, cut off a deal going forward, change pricing, kill rather than zero) reach the desk by email or phone. Each one cites deal numbers from an earlier list or thread. (Volume Management, storage, accounting, Unify support) [farmer-d/logistics/748, farmer-d/logistics/965, farmer-d/logistics/1200, farmer-d/logistics/5]
4. The desk scheduler enters or edits the ticket in Sitara. Transport usage tickets are refreshed in bulk, and schedulers are then asked to check that volumes show correctly in Position Manager. (logistics desk / scheduler) [farmer-d/logistics/1144, farmer-d/logistics/1299]
5. No standard confirmation goes back, so requesters follow up to find out whether the deal is in, priced or pathed. Around month start, unpathed and unassigned deals get escalated to supervisors. (requester, logistics supervisor (Pat Clynes)) [farmer-d/logistics/59, farmer-d/logistics/12, farmer-d/logistics/102, farmer-d/logistics/673]
6. Months later, accounting asks why historic deals were changed or suspended. The reason was never recorded with the request, so the trail has to be rebuilt by asking around. (accounting / settlements) [farmer-d/logistics/1438]

**Where it stalls**

- Zero-out requests sent as a list get done only in part. The requester has to send reminders because no confirmation per deal number comes back.
  > Wanted to let you know that there are still two sitara deals that need to
  [farmer-d/logistics/748]
- A pricing change waits in the desk queue while the counterparty keeps calling the requester, who has no status to give.
  > Duke has called me several times they want to get our March deals finalized.
  [farmer-d/logistics/1200]
- A request to enter a deal before close gets no acknowledgement, so accounting has to ask whether it was done.
  > Have the two of you been able to get the deal in for the sale of the Centana storage to AEP?
  [farmer-d/logistics/12]
- Requesters kill deals when they should zero them out. Killed deals break paths in Unify, which means rework and a request for reasons that should have come with the original ask.
  > If a deal is killed it poses a problem for us in Unify if there are any paths associated with the deal; therefore, we request the deals be zeroed out.
  [farmer-d/logistics/5]
- An EOL deal volume change was phoned in after hours and never written down or passed to the desk.
  > It is a deal with Aquila and the volume was changed.
  [farmer-d/logistics/1299]
- Deals are left unpathed at month start because nobody owns them. The scheduler has to guess at nominations and escalate.
  > I brokered and nominated the obvious but we seem to have 10,000 with
  [farmer-d/logistics/673]
- Historic months stay unpathed until someone notices long afterwards. Requests carry no close-month deadline.
  > It doesn't look like it's been pathed for HPL and CHAN.
  [farmer-d/logistics/102]

**Proposed quick win**

Publish one 'Sitara Deal Request' email template. Every requester copies it into new requests to the logistics desk. Its fixed fields are: action (create / change price / change volume / zero out / cut off / path), existing Sitara deal number(s) if any, counterparty, meter, pipe, start and end dates, daily volume, price or index formula, book, contract in place (Y/N), close month needed by, and reason for the change. A short guidance block in the template tells requesters to zero out deals instead of killing them when paths exist, because killed deals break Unify paths. It also tells them that phoned-in or EOL changes must be confirmed by email using the template. The desk answers each request with a prepared confirmation reply: Sitara number(s) created or changed, the fields as entered, the date entered, and whether Position Manager and pathing were checked. This reply closes the loop and gives accounting a written reason for later audits. A one-page month-start checklist covers the cases that currently escalate: unpathed deals by pipe, owner for each pipe, and open template requests with a close-month deadline.

- Trigger: An incoming email asking the logistics desk to create or change a Sitara deal, plus the month-start/close deadline for the checklist.
- Inputs: requester's filled-in Sitara Deal Request template; existing Sitara deal numbers and tickets; pipe-to-scheduler assignment list for the month
- Outputs: confirmation reply to the requester with the Sitara number(s) and fields as entered; written reason for each change kept in the email thread for accounting; month-start checklist of unpathed deals and owners for the logistics supervisor
- Existing systems: Sitara, Unify, Position Manager, EOL, Pops
- New components: Sitara Deal Request email template (fixed fields plus zero-out-not-kill guidance), prepared confirmation reply for the desk returning the Sitara number, short 'incomplete request' reply that lists the missing fields, month-start unpathed-deal and pipe-ownership checklist, shared mailbox folder or rule that files template requests by subject tag

**Implementation steps**

1. Collect a sample of past requests (field origination, storage, Volume Management, accounting) and confirm which fields the desk had to chase. Finalize the template field list with Daren Farmer and Pat Clynes.
2. Write the template with a fixed subject tag (for example 'SITARA REQ: <action> <counterparty>') and the guidance on zeroing out instead of killing deals, reviewed with Unify support (Tammy Jaquet) and Volume Management (Rita Wynne).
3. Write the prepared confirmation reply and the incomplete-request reply. Save both as stationery/saved replies in the desk schedulers' mail clients.
4. Write the month-start checklist: list unpathed deals per pipe, confirm the scheduler assigned to each pipe, and list open template requests due for the coming close.
5. Send the template to the regular requesters (field origination, storage book, Volume Management, accounting) with a short note. From then on, the desk replies to any free-form request with the template attached and asks for it to be resent.
6. Run the checklist at the next month start. Pat Clynes reviews it and assigns any pipe without an owner.
7. After one close, count requests that needed a follow-up or clarification round and adjust the fields.

**Stays manual**

- Actual entry and editing of deals in Sitara. The desk still keys tickets and judges pricing and contract coverage.
- Deciding whether a deal should be killed or zeroed out when Unify paths exist, which needs the scheduler's view of the paths.
- Assigning pipe ownership when schedulers change, which is a supervisor decision.
- Research on historic or suspended deals for accounting. The template only helps for requests made after rollout.

**Risks**

- Requesters keep sending free-form emails or phoning changes in. To counter this, the desk consistently replies with the template, and supervisors back the rule for EOL and after-hours changes.
- The evidence does not show how many requests are actually incomplete compared with simply waiting in a queue. If most delay is desk capacity, the template removes fewer rounds than expected, so measure follow-ups before and after.
- The field list rests on a 15-message sample. Some request types (transport usage tickets, multi-party storage deals) may need extra fields, so review the template after the first close.
- Confirmation replies add a small amount of desk work per request. Keep the reply short and prefilled so it costs less than the follow-up emails it replaces.
- The value is small (about $65 per month), so the rollout should stay low-cost and avoid any system build.

## 8. Deal and counterparty book transfers

Lists of deals or terminated counterparties that must be moved or flipped between trading books (ECC deals to FT-US/CAND-ERMS, ENA deals to the bankruptcy books) arrive as forwarded emails and spreadsheets. Book controllers then hunt for the live deals by hand, ask clarifying questions, and confirm back under invoicing or book-calc deadlines. A move-list service would take the incoming list, look up every live deal in Sitara or TAGG, apply standard move rules, and produce a reviewed move file and a before-and-after report. That cuts the lookup, the question rounds and the confirmations, worth about $59 a month ($708 a year) at $85/h.

**Effort:** M · **Success metric:** Median time from move request to confirmed move, and the number of clarifying emails per move request, both measured before and after rollout; plus the count of ECC deals found in US books after invoicing starts.

**How it works today**

1. A requester (Calgary invoicing, credit, risk or middle office) emails a list of deal numbers, counterparties or a spreadsheet of deals that sit in the wrong book or must go to the bankruptcy books, often with a same-day deadline. (invoicing / credit / middle office requester) [giron-d/sent/550, giron-d/sent/246, giron-d/inbox/117, giron-d/inbox/46]
2. The request is forwarded until it reaches the controller who owns the book, sometimes via a manager, because the requester does not know who handles the book. (book controller (e.g. Darron Giron) via manager (Jeffrey Gossett)) [giron-d/sent/550, giron-d/sent/539, giron-d/sent/405]
3. The controller passes the list to the book administrators and asks them to scan all their books for similar deals (e.g. ECC deals with counterparties other than RISKMANTRA) and to flip them. (book controller and book administrators) [giron-d/sent/539, giron-d/sent/405, giron-d/sent/246]
4. For counterparty-level moves, credit/legal supply terminated contracts and counterparty lists, and someone reconciles them to live deal numbers in TAGG and Sitara. (credit / bankruptcy team (Cyndie Balfour-Flanagan, Patrick Mulvany)) [giron-d/inbox/108, giron-d/inbox/103, giron-d/inbox/91]
5. The person running the move in the Estate database asks the controller to confirm source books, CP IDs, commodity code, cutoff date for active deals and the offsetting ENA counterparty before moving. (Estate database operator (Cecilia Cheung)) [giron-d/inbox/67, giron-d/inbox/84]
6. The move is done and confirmed by email so that invoicing can start or books can be calculated. Supplemental lists keep arriving afterwards. (book administrators / requester) [giron-d/inbox/84, giron-d/inbox/46, giron-d/sent/246]
7. Related structural changes (new internal books, subregion and curve mapping changes, conversions with evergreen flags) are also requested and remembered by email. (book controller and Sitara / risk support) [giron-d/sent/759, giron-d/sent/775, farmer-d/logistics/1371]

**Where it stalls**

- Invoicing waits on deals booked under the wrong Enron counterparty, and the book owners have to hunt for them across all their books by hand.
  > Invoicing for November should 
start today, and both ECC and ENA are held back from invoicing until these 
deals are fixed
  [giron-d/sent/539]
- Requests reach the wrong person first and are forwarded on, so time is lost before the book owner even sees them.
  > Please call me if you 
aren't the person who handles this book, and please forward this message on 
to the person who does.
  [giron-d/sent/405]
- The requester has to chase confirmation under a deadline of a few hours before customers can be invoiced.
  > Please let me know when these are 
finished as I need to get an invoice to the customers within the next couple 
of hours.
  [giron-d/sent/246]
- The move operator waits on answers about CP IDs, commodity code and cutoff date before running the move, because the request does not include them.
  > If I can have all the answers soon then I think the deals move can be completed around 3:00p.m.
  [giron-d/inbox/67]
- Counterparty and contract lists do not map cleanly to Sitara deal numbers, so reconciliation spills into the next day and supplemental lists follow.
  > Please note that there are still several deals that I am trying to reconcile back to Sitara numbers.
  [giron-d/inbox/103]
- Moves are tied to the daily book calculation, which leaves no slack for back-and-forth.
  > Please move only financial deals.  Please let me know when this is complete.  We need to have it done by the time we calc our books today - no exceptions.
  [giron-d/inbox/84]

**Proposed automation**

Requesters submit a structured move request instead of a free-form email: deal numbers or counterparty short names/CP IDs, source book(s), target book, deal type (financial or physical), cutoff date for active deals, and a deadline. A lookup job queries Sitara and TAGG for every live deal that matches. It applies saved rules for recurring cases, for example 'ECC deals with a counterparty other than RISKMANTRA belong in FT-US/CAND-ERMS' and 'auto-terminating deals for terminated counterparties go to the bankruptcy books'. It writes a proposed move file plus an exceptions list: unknown books, counterparties that resolve to no deal, contract-level items that do not reconcile to Sitara numbers. The request is routed to the controller who owns each source book, so nothing has to be forwarded. After the administrator runs the move, the job re-queries the books and emails a before-and-after confirmation to the requester. A scheduled sweep also checks US books for ECC-counterparty deals ahead of the invoicing start, so they are caught before invoicing instead of after.

- Trigger: A submitted move request (deal list, counterparty termination list or spreadsheet), plus a scheduled sweep of the books before monthly invoicing and before the daily book calc.
- Inputs: deal numbers or counterparty short names / CP IDs from the request; source and target book names; deal type filter (financial or physical) and active-deal cutoff date; live deal data from Sitara and TAGG; book-to-controller ownership table; saved move rules (ECC to FT-US/CAND-ERMS, terminated counterparties to bankruptcy books)
- Outputs: proposed move file per target book for the book administrator; exceptions list for the controller (unresolved counterparties, unknown books, unreconciled deals); before-and-after confirmation email to the requester (invoicing, credit, risk); pre-invoicing sweep report of ECC deals sitting in US books
- Existing systems: Sitara, TAGG, EnronOnline, Estate database
- New components: structured book-move request form, deal lookup job against Sitara and TAGG, move rule table, book ownership routing table, proposed move file and exceptions generator, post-move verification and confirmation email, scheduled pre-invoicing ECC sweep

**Implementation steps**

1. Collect the past move requests (ECC flips, bankruptcy book moves, MGMT-WEST and G-DAILY-EST cleanups) and list the fields every request ended up needing: CP ID, source book, deal type, cutoff date, offsetting counterparty, commodity code.
2. Build the book ownership table that maps each book (e.g. MGMT-WEST, G-DAILY-EST, NG-PRICE, NG-PR-OPT) to its controller and administrators.
3. Publish the structured request form with those fields required, and tell invoicing, credit and middle office to use it instead of emailing lists.
4. Write the lookup job: read the request, query Sitara and TAGG for live deals that match, and produce the proposed move file and exceptions list.
5. Encode the recurring rules (ECC counterparty deals to FT-US/CAND-ERMS, terminated counterparties to bankruptcy books, financial vs physical filter) in the rule table, reviewed by the controller.
6. Add post-move verification that re-queries the books and emails the requester a confirmation listing each deal and its new book.
7. Schedule the pre-invoicing sweep for ECC deals in US books, including EnronOnline deals that were booked automatically.
8. Pilot on one region's books for a month and compare against manual moves, then extend to all books.

**Stays manual**

- Credit and legal decide which counterparties and contracts are terminated (e.g. under the Master Netting Agreement); the tool only acts on their list.
- The book administrator reviews the proposed move file and runs the move in Sitara or the Estate database; nothing is moved automatically.
- The controller resolves exceptions: contract-level items that do not reconcile to Sitara numbers, books missing from the Estate database, ambiguous commodity codes.
- Structural changes such as new internal books, subregion or curve mapping changes and evergreen flag removal stay as controller requests to Sitara support.

**Risks**

- Volume is low (about 0.7 h a month at the measured rate) and concentrated in bursts such as the January 2002 bankruptcy moves, so a full integration may not pay back. Mitigation: start with the request form and a read-only lookup script (effort could fall to S) before building verification.
- The emails do not show how Sitara, TAGG and the Estate database can be queried or exported. Deal lookup may depend on access that has to be confirmed with IT first.
- Counterparty identifiers differ between sources (TAGG short names, CP IDs, contract numbers), so the lookup can miss deals or match the wrong ones. Mitigation: show unresolved items as exceptions and never drop them silently.
- Stale move rules could flip deals that should stay, e.g. ECC deals with RISKMANTRA. Mitigation: the controller owns the rule table and every move file is reviewed by a person.
- Requesters may keep emailing lists, which bypasses the form. Mitigation: book admins reply with the form link and the confirmation only comes from the tool.
