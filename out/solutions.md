# Solution designs

One design per top opportunity: an automation, or the rollout of a quick win. Citations are message ids; quotes are verified verbatim.

## 1. Missing or expired deal tickets for metered flow

Volume management, settlements and accounting staff keep finding gas allocated at a meter where Sitara has no deal, or only an expired or short-dated one. Each case becomes a one-off email to the deal owner, usually Daren Farmer, and is often chased for days or months. A daily exception job would compare allocated meter flow against active Sitara deal terms, open one pre-filled case per gap and route it to the deal owner with a one-click decision (extend, new deal, or write-off/PPA). Gaps would be caught in the month they occur instead of at settlement or a year later, and the follow-up emails would stop. Modelled value is $205 per month ($2,460 per year).

**Effort:** M · **Success metric:** Number of meter-days with allocated flow but no valid Sitara deal still open at month-end close, plus the median age of gap cases from first flow to resolution

**How it works today**

1. Volume management or settlements finds allocated flow at a meter that has no matching Sitara deal: the deal has expired, it starts a day late, or it covers only part of the month. Sometimes this turns up through a Feedback Monitor error or a counterparty statement. (volume management / settlements analyst (e.g. Jackie Young, Heidi Withers, Rebecca Griffin)) [farmer-d/logistics/896, farmer-d/logistics/1055, farmer-d/logistics/2137, farmer-d/logistics/1356]
2. The analyst emails the deal owner and types the meter number, Sitara deal number, dates, contract and volume into free text. They ask for the deal to be rolled, extended or created so that accounting can set up an accounting arrangement. (volume management analyst to Texas desk deal owner (Daren Farmer)) [farmer-d/logistics/896, farmer-d/logistics/1999, farmer-d/logistics/1149]
3. If it is unclear who owns the deal, the request is passed between people and desks (George/Craig, Julie Meyers, then Daren) until someone accepts it. (logistics / trading desk contacts) [farmer-d/logistics/1055, farmer-d/logistics/117, farmer-d/logistics/130]
4. The requester follows up by email while the gap stays open, sometimes repeatedly in the same thread. (volume management, settlements, Aimee Lannou (logistics)) [farmer-d/logistics/1160, farmer-d/logistics/1485, farmer-d/logistics/1227, farmer-d/logistics/1149]
5. For old or large gaps, an approver asks for root cause and billing details before signing off on a deal, or proposes letting the volume hit an OBA as a PPA instead. (approver (Gary Lamphier), East Desk logistics (Victor Lamadrid)) [farmer-d/logistics/1356, farmer-d/logistics/1489, farmer-d/logistics/1972]
6. The deal owner creates or extends the Sitara ticket, or fixes the volume. The change then has to flow through to Unify and Volume Management before payment or invoicing can happen. (deal owner / scheduler (Daren Farmer, Mary Poorman)) [farmer-d/logistics/130, farmer-d/logistics/1299, farmer-d/logistics/1516]

**Where it stalls**

- Deal tickets are not rolled forward month to month. Flow continues on an expired deal, nobody notices for months, and then someone has to work out who should roll it.
  > There should be a deal ticket in Sitara for this sale to Engage, but 
it looks as though 12/99 was the last month a deal was entered
  [farmer-d/logistics/1055]
- A deal that covers only some of the flow days leaves the rest stranded. The same issue comes back and needs a second request for a new deal number.
  > Can you assist Anita and I w/a deal number to place the 1st 20 days on.
  [farmer-d/logistics/1149]
- A counterparty-reported volume with no deal sits unanswered for weeks after production month, and the requester has to chase.
  > Were you able to find anything out about this?
  [farmer-d/logistics/2137]
- Gaps found very late (a 1/99 meter found in 8/2000) get held up because the approver needs root cause and billing details first.
  > I am uncomfortable putting a deal out there without more details.
  [farmer-d/logistics/1356]
- Prior-period gaps can become impossible to process in the systems, which forces a workaround decision.
  > I don't think we can even process this request.
  [farmer-d/logistics/1489]
- Volumes are changed repeatedly between pipeline allocation, Unify paths and Sitara deals, so the same gap is reworked several times.
  > We go round and round at this point 
changing volumes two, three or more times.
  [farmer-d/logistics/1972]
- Volumes that are not actualized leave nothing in Volume Management, so a counterparty payment is stuck against a hard noon deadline.
  > The volumes have not be actualized so there is nothing in Volume Management.
  [farmer-d/logistics/130]

**Proposed automation**

A nightly reconciliation job reads allocated daily volumes by meter and contract from Volume Management, plus the active Sitara deals for the same meter, counterparty and dates. It flags every meter-day where there is flow but no deal covers it, which includes missing deals, expired deals, deals that start late and partial-month coverage. Each gap becomes one exception case pre-filled with the meter, contract, counterparty, flow days, volume, the last deal number seen at that meter and the suggested fix (for example, extend deal X through the end of the month). The case is routed to the deal owner of the last deal at that meter, with a fallback owner by desk. The owner picks extend, create a new deal, or write-off/PPA with a reason, so requesters no longer have to email and chase. Cases still open after a set age go to the desk lead, and month-end close gets a report of open gaps, so they are fixed in the production month rather than discovered months later.

- Trigger: Nightly schedule after the daily allocation load, plus an on-demand run before month-end close and settlement
- Inputs: allocated daily volumes by meter and contract (Volume Management); Sitara deal tickets: deal number, counterparty, meter, start and end dates, volume, evergreen flag, deal owner; Unify paths by meter and day; Feedback Monitor errors where available; meter-to-desk ownership table for routing
- Outputs: daily exception queue of meter-days with flow but no valid deal, one pre-filled case per gap, for the deal owner; a suggested action per case (extend deal / new deal / write-off or PPA), with the decision and reason recorded; a month-end report of open gaps by age and volume for volume management, settlements and the desk lead; a notification to the requester (volume management or settlements) when a case is resolved and the deal number is available
- Existing systems: Sitara, Unify, Volume Management, Feedback Monitor
- New components: nightly flow-versus-deal comparison job (meter, day, counterparty), exception case store with status, owner, age and decision, routing rules: last deal owner at the meter, then a desk fallback, pre-filled notification and decision form (extend / new deal / write-off or PPA, with reason), aging escalation rule and month-end open-gap report

**Implementation steps**

1. Agree the matching key and tolerance with volume management and the Texas desk: meter, contract, counterparty, day, and a minimum volume below which gaps are batched rather than raised individually.
2. Build read-only extracts of allocated volumes from Volume Management and of deal terms (dates, meter, evergreen flag, owner) from Sitara.
3. Write the comparison job and run it over recent production months in shadow mode. Check its exceptions against the gaps people actually emailed about, such as meters 98-6719, 98-9676 and 1520, to tune false positives.
4. Build the routing table (last deal owner per meter, plus a desk fallback) and the pre-filled case notification with its decision form.
5. Pilot with the Texas desk deal owner and the volume management analysts who raise most of these requests. Retire the free-text email requests for gaps the job already catches.
6. Add the aging escalation and the month-end open-gap report, and record decisions so recurring meters (repeated monthly rolls) can be moved to evergreen deals.
7. Extend to other desks once the false-positive rate is acceptable.

**Stays manual**

- Whether flow is legitimate and should get a deal, or should not be flowing at all, because it needs commercial judgement from the deal owner.
- Price and terms for a new or extended deal (for example, a premium rate or historical transport charge), because the trader sets them.
- Approving write-offs, PPA/OBA treatment or very old prior-period gaps, where an approver needs root cause, end-user billing and counterparty credit context.
- Disputes with pipelines or counterparties over allocated volumes, which need negotiation outside the systems.
- Same-day payment deadlines such as prompt counterparty payments, which still need someone to coordinate across accounting and logistics.

**Risks**

- Allocation data arrives late or is restated (prior-month re-allocations), which would cause false or flapping exceptions. Mitigate by re-running per production month and suppressing cases whose volumes keep changing until allocation settles.
- The evidence does not show the actual data structures or access paths for Sitara, Unify and Volume Management, so extract effort is uncertain. A technical discovery step is needed before committing to the M estimate.
- Deal ownership is often unclear in the emails, so routing by last deal owner may send cases to the wrong person. Mitigate with a desk fallback owner and a reassign action.
- Systems may not support very old periods (the emails note pre-Unify pathing for 1999), so the job should only cover current and recent production months.
- The modelled saving ($205 per month) is small, so the build should stay lightweight. The main benefit may be catching unbilled gas early, which the evidence suggests but does not quantify.
- Users may keep emailing in parallel. Mitigate by having the case notification carry all the request details and by measuring the drop in ad-hoc requests.

## 2. Real-time desk position and procedure instructions

The real-time desk lead writes a fresh free-form email to the shift traders almost every day. Each one gives that day's long or short position (hub, hours, MW, price, book) and often restates a standing rule about Enpower, CAPS, the service sheet, losses or lending, and some of these get resent or corrected. Two fixes would make the emails predictable and stop the repeats: a fixed position notice template and one standing real-time procedures checklist that the notices link to. Together they are worth about $114 a month ($1,368 a year) in the lead's handling time, and they lower the risk of deals being booked wrong.

**Effort:** S · **Success metric:** Count of separate reminder, correction or resend emails from the desk lead to the shift group per month (for example 'just a reminder', 'one more time', 'here it is again') after rollout compared with before, plus the share of position emails sent in the template format.

**How it works today**

1. Desk lead (Bill Williams) writes a free-form email to the shift group or shift.portland@enron.com giving the day's length or short: hub (NP-15/SP-15), hours (HE 7-22), MW, price, and the book (ST-WBOM, ST-CALI). The order and wording change from day to day. (real-time desk lead) [williams-w3/sent_items/512, williams-w3/sent_items/502, williams-w3/sent_items/496, williams-w3/sent_items/466]
2. Shift traders read the email and book the deals under the named book in Enpower. They check the position against CAPS and record ST-CALI sales or length in the service sheet beneath the desk's own activity. (real-time shift traders) [williams-w3/sent_items/466, williams-w3/sent_items/506, williams-w3/sent_items/496]
3. For one-off structures (APS losses, El Paso lending, PGE John Day to Malin transmission), the lead spells out the Enpower entries deal by deal: which deal number to reuse or price, which leg is priced at zero, and the annuity to ST-NW. Scheduling (Lisa) or deal entry (Kate) may already have made the tag or the Enpower deals. (real-time desk lead, scheduling, deal entry) [williams-w3/sent_items/463, williams-w3/sent_items/433, williams-w3/sent_items/434, williams-w3/sent_items/380]
4. Standing procedures go out as separate ad hoc emails mixed in with daily positions: hourly BPA checkout for Frontier and GCPUD with initials on the service sheet, CAISO price cap and wheeling fees, OASIS transmission paths, and using the Enpower swap function instead of annuities. (real-time desk lead) [williams-w3/sent_items/506, williams-w3/sent_items/449, williams-w3/sent_items/444, williams-w3/sent_items/432]
5. When instructions are missed or change, the lead sends follow-ups and resends: schedule changes must be called in, copy the lead on EES sheets and cut notes, updated APX buys. (real-time desk lead) [williams-w3/sent_items/487, williams-w3/sent_items/471, williams-w3/sent_items/403]

**Where it stalls**

- Standing rules sit inside individual emails, not in one place the shift can look up, so the lead has to re-send and remind.
  > These schedule changes must be called in.  Just a reminder.
  [williams-w3/sent_items/487]
- A procedure already circulated by another trader is resent in full because no shared reference exists.
  > Ryan sent this email out once already, here it is again.
  [williams-w3/sent_items/444]
- Distribution rules for EES sheets and cut notes are not followed, so the lead sends a correction.
  > I should be copied on the EES sheets, and any cut notes to volume managament, the services desk, or other traders.
  [williams-w3/sent_items/471]
- Position updates arrive in pieces in follow-up emails, so traders have to piece the current position together from several messages.
  > We have also bought HE 21 and HE 22 from the APX.
  [williams-w3/sent_items/403]
- Deal-entry rules that are explained only in passing lead to booking errors and long disputes afterward.
  > Swaps have caused disputes that have dragged on for months in the past, so call me with any questions.
  [williams-w3/sent_items/432]
- Where the service sheet should record things changes by email, and every trader has to remember the change.
  > Going forward, please put all the ST-CALI sales or length in the service sheet beneath our activity.
  [williams-w3/sent_items/506]

**Proposed quick win**

Two artifacts replace free-form writing. The first is a fixed position notice template that the desk lead fills in each afternoon for the next flow day. It has one row per position with fields for date, long/short, hub (NP-15/SP-15), hours (HE range), MW, price, book (ST-WBOM, ST-CALI, ST-Whourly) and the Enpower deal number(s) if already made. It also has a line saying where the entry goes (CAPS line, service sheet section) and a 'special handling' line that points to a numbered checklist item, not a re-explanation. The second is a standing Real-Time Shift Procedures checklist kept as a single document with numbered items. Items cover booking position deals under the named book in Enpower and matching CAPS, logging ST-CALI activity beneath desk activity on the service sheet, hourly BPA checkout for Frontier and GCPUD with initials, calling in schedule changes, copying the lead on EES sheets and cut notes, losses deals (buy from EPE, sale to APS at zero), PGE John Day to Malin on the standing deal, EPE lending, the Enpower swap function and CAISO wheeling fee components. When a rule changes, the lead edits the checklist item and the next notice carries a one-line 'Checklist updated: item N' instead of a full new email. Corrections go out as a reissued notice with a version marker ('v2 replaces v1'), not as a loose follow-up.

- Trigger: The desk lead's daily close of next-day positions (length or short in the BOM or ST-CALI books), plus any change to a standing real-time procedure.
- Inputs: next-day long/short positions by hub, hours, MW, price and book; Enpower deal numbers already created by deal entry or scheduling; CAPS position line; changes to standing procedures (BPA checkout, losses, lending, swaps, CAISO fees)
- Outputs: daily position notice in a fixed format for the real-time shift traders; a numbered Real-Time Shift Procedures checklist the shift uses on every shift; a short 'checklist updated: item N' line when a rule changes
- Existing systems: Enpower, CAPS, service sheet, preschedule sheet, shift.portland@enron.com
- New components: position notice email template (saved Outlook template or signature block) with fixed fields: date, long/short, hub, HE range, MW, price, book, Enpower deal #, CAPS line, special handling item #, version, Real-Time Shift Procedures checklist with numbered items and a change log, standing distribution list rule: notices go to shift.portland@enron.com with the lead and services desk copied

**Implementation steps**

1. Collect the standing rules already scattered across the lead's sent emails (BPA checkout, service sheet placement, ST-CALI logging, schedule-change call-ins, EES and cut note copies, losses to APS, PGE John Day to Malin, EPE lending, Enpower swap function, CAISO price cap and fee components, OASIS path notes) and write each as a numbered checklist item.
2. Have the shift traders review the draft checklist in the next real-time meeting, then publish it in one shared location next to the service sheet and preschedule sheet.
3. Build the position notice template with the fixed fields, with one row per position and a special-handling column that refers to checklist item numbers.
4. Starting on a set date, the desk lead sends every position notice from the template to shift.portland@enron.com, and sends corrections as reissued notices marked v2/v3.
5. Shift traders confirm each row against Enpower and CAPS and initial it on the service sheet, the same way they already initial the hourly BPA checkout.
6. Each time a rule changes, edit the checklist item, add a change-log line, and mention the item number in the next notice. After one month, check whether any separate reminder emails were still needed.

**Stays manual**

- Deciding the position itself (how much length to carry, price, which book) stays with the desk lead because it is a trading judgment.
- One-off structures not yet in the checklist (for example a new lending arrangement) still need a written explanation the first time. They become checklist items only once they recur.
- Professional conduct issues and meeting announcements are not procedure and stay as normal email.
- Traders still make the real-time calls (BPA checkout, EPE dispatchers, calling in schedule changes). The checklist reminds them but cannot make the call.

**Risks**

- The evidence comes from one mailbox (williams-w3), so how shift traders actually use CAPS and the service sheet is only seen through the lead's emails. Validate the checklist with the traders before rollout.
- A stale checklist could mislead traders on price caps or deal numbers. Mitigate with a dated change log and by quoting the item number in each notice.
- The savings are small (about $114 a month), so the case rests as much on fewer booking errors and swap disputes as on time saved. That benefit is not quantified in the evidence.
- Traders may keep working from old emails. Mitigate by announcing that only template notices and the current checklist are authoritative.

## 3. Weekly California Capacity Report

Every week Michelle Lokay hand-builds the California Capacity Report: Transwestern and El Paso deliveries to California, utilization percentages by El Paso delivery point, posted Gas Daily prices and Enron basis. She types the numbers and percentages into an email by hand, and at least once had to send a follow-up to correct the report's week. A scheduled job that fills in the existing format, checks the dates and arithmetic, and holds the draft for her approval would remove most of the compilation work, worth about $110 per month ($1,320 per year), and stop corrections like that one.

**Effort:** M · **Success metric:** Analyst minutes per weekly California Capacity Report, plus the number of correction emails sent after a report (target zero)

**How it works today**

1. At the end of each trading week (usually Friday, Thursday when the week is short), the analyst gathers Transwestern's average deliveries to California and its utilization, San Juan lateral throughput and total East deliveries, and types them into the opening sentence of a new email. (Transwestern commercial analyst (michelle.lokay)) [lokay-m/sent_items/18, lokay-m/sent_items/63, lokay-m/sent_items/110]
2. The analyst collects El Paso's average deliveries to California and, for each delivery point (PG&ETop, SoCalEhr, SoCalTop), the capacity and deliveries, then works out each utilization percentage by hand. Capacity figures change over time and must be kept current by hand (SoCalEhr was listed at 1042 in October and at 1250 from December). (Transwestern commercial analyst (michelle.lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/146]
3. The analyst copies the latest posted Gas Daily prices (SoCal gas, PG&E, TW San Juan, later 'San Juan (non-Bondad)', and TW Permian) with their day-over-day changes. Points with no posting are entered as 'n/a', and the heading is retyped as Thursday's or Friday's prices to match the send day. (Transwestern commercial analyst (michelle.lokay)) [lokay-m/sent_items/67, lokay-m/sent_items/131, lokay-m/sent_items/97]
4. The analyst adds an Enron Online basis table (Perm-CA, SJ-CA, SJ-Waha, Perm-Waha). It shrinks to a single month, then reads 'n/a', and from February it is dropped altogether. (Transwestern commercial analyst (michelle.lokay)) [lokay-m/inbox/10, lokay-m/sent_items/18, lokay-m/sent_items/55, lokay-m/sent_items/79]
5. The analyst types a subject of the form 'California Capacity Report for Week of MM/DD-MM/DD' and emails the report to the same fixed distribution list (steven.harris, kimberly.watson, lorraine.lindberg, tk.lohman, lindy.donoho). (Transwestern commercial analyst (michelle.lokay)) [lokay-m/sent_items/40, lokay-m/sent_items/86, lokay-m/sent_items/117]
6. When a report goes out with a mistake, the analyst sends a correction email to the whole list. (Transwestern commercial analyst (michelle.lokay)) [lokay-m/sent_items/46]

**Where it stalls**

- The week and dates are typed by hand, so at least one report went out labelled with the wrong week and needed a correction email to the whole distribution list.
  > Sorry, the effective date for this new report is 01/07-01/11.
  [lokay-m/sent_items/46]
- Every week the analyst keys in delivery and utilization figures by hand from source data, and these are the numbers the recipients read first. This is the main recurring handling time, about 45 minutes per report.
  > Transwestern's average deliveries to California were 945 MMBtu/d (87%), with San Juan lateral throughput at 865 MMBtu/d.
  [lokay-m/inbox/10]
- Capacity at each delivery point is a reference value the analyst maintains by hand. SoCalEhr capacity changed between reports, and each percentage is worked out by hand, so a stale capacity or a slip in the division would go unnoticed.
  > - SoCalEhr, capacity 1250 MMBtu/d, deliveries of 910 MMBtu/d (73%)
  [lokay-m/sent_items/67]
- The report is rebuilt from scratch every week, even when a section has gone stale (the Enron Online basis table first became 'n/a' and was later dropped). This shows the format is maintained by hand rather than generated.
  > Transwestern's average deliveries to California were 1011 MMBtu/d (93%), with San Juan lateral throughput at 872 MMBtu/d.
  [lokay-m/sent_items/86]

**Proposed automation**

On the last trading day of each week, a scheduled job averages the week's daily Transwestern deliveries to California, San Juan lateral throughput and East deliveries. It does the same for El Paso deliveries to California and each delivery point (PG&ETop, SoCalEhr, SoCalTop). It works out utilization against a maintained capacity table. It reads the latest posted Gas Daily prices for SoCal gas, PG&E, San Juan and TW Permian and calculates the day-over-day changes. It then fills in the existing report text exactly as recipients see it today, with a subject built from the trading-week calendar (for example 'California Capacity Report for Week of 03/11-03/15'), so the week can no longer be mistyped. Validation checks stop the draft and flag it to the analyst if a day of data is missing, a capacity value is older than a set age, or a percentage falls outside a plausible range. The analyst gets the draft as an unsent email, can add commentary or mark a price 'n/a', and approves it to go to the standard list.

- Trigger: Weekly schedule on the last trading day of the week (normally Friday, Thursday when Friday is a holiday or non-posting day), after Gas Daily prices are posted
- Inputs: Daily Transwestern deliveries to California, San Juan lateral throughput and East deliveries for the week; Daily El Paso deliveries to California by delivery point (PG&ETop, SoCalEhr, SoCalTop); Capacity reference table per El Paso delivery point (for example SoCalEhr 1250, PG&ETop 1140, SoCalTop 540), with an effective date; Posted Gas Daily prices for SoCal gas large pkgs, PG&E large pkgs, San Juan (non-Bondad) / TW San Juan and TW Permian, current and previous posting; Trading-week calendar to set the report week and choose the Thursday or Friday price heading; Distribution list: steven.harris, kimberly.watson, lorraine.lindberg, tk.lohman, lindy.donoho
- Outputs: Draft 'California Capacity Report for Week of MM/DD-MM/DD' email in the current format, held for the analyst's approval; Validation notice to the analyst listing missing days, stale capacity values or out-of-range percentages; Weekly history file of the reported figures, so trends can be read without searching past emails
- Existing systems: Gas Daily, Transwestern, El Paso
- New components: Weekly scheduled report job, Delivery and throughput extract with weekly averaging, Gas Daily price loader with day-over-day change calculation, Maintained capacity reference table with effective dates, Report text template that reproduces the current email layout, Week-label generator built on a trading-week calendar, Validation rules (completeness, capacity age, percentage range), Draft-and-approve email step to the fixed distribution list, Weekly figures history file

**Implementation steps**

1. Confirm with the analyst where each figure comes from today: the Transwestern and El Paso delivery data, how the capacity values are set, and how Gas Daily prices are obtained. The emails do not name these sources.
2. Build the report text template from a recent report (for example the week of 03/11-03/15) and get the analyst to sign off that it matches the current layout line for line.
3. Build the capacity reference table with effective dates, loaded with the values in the latest reports, and name an owner for updates.
4. Build the delivery extract and weekly averaging, then backfill several past weeks and check the output against the reports already sent (for example weeks 12/10-12/14 through 03/11-03/15).
5. Build the Gas Daily price loader and the change calculation, with a defined 'n/a' rule when a point has no posting.
6. Add the trading-week calendar and subject generator, including short weeks such as 12/26-12/28 and 02/19-02/22.
7. Add the validation rules and the draft-and-approve email step, sending only to the analyst at first.
8. Run in parallel with the manual report for three to four weeks, comparing figures, then switch the list to the approved automated draft.

**Stays manual**

- Final review and approval before sending: recipients rely on the figures for commercial decisions, and someone has to answer for them.
- Commentary or context on unusual weeks (for example a sharp utilization drop at PG&ETop), which needs market knowledge.
- Updating capacity values when a pipeline posts new capacity: the change has to be confirmed as an actual capacity change and not a data glitch.
- Deciding to add or drop report sections (as when the Enron Online basis table was dropped).

**Risks**

- The evidence never names the system that holds daily Transwestern and El Paso delivery volumes, or how Gas Daily prices are obtained. If those figures come from manual lookups or a source that can't be fed into the job, the build grows. Mitigation: confirm the sources first (step 1) and re-scope before funding.
- The savings are small, about $110 per month ($1,320 per year), and all the volume comes from one mailbox (lokay-m) over a few months. Mitigation: keep the build to a script plus template and drop it if the sources need integration work.
- A stale capacity value would produce wrong utilization percentages that look plausible. Mitigation: effective-dated capacity table, age check, and an analyst prompt when the value is older than the set limit.
- Gas Daily postings are sometimes missing for a point (reports show 'n/a' for TW San Juan), and a point's label changed to 'San Juan (non-Bondad)'. Mitigation: map points explicitly and print 'n/a' rather than carrying a stale price.
- If recipients come to trust an automated draft, they may assume figures were reviewed when they were not. Mitigation: the job never sends without approval and prints the validation status in the draft.

## 4. Real-time deal entry and position variance reconciliation

Real-time traders on the West desk find mismatches between Enpower deals, CAPS schedules, position manager and the EPE schedules by hand, often a day or a month later. Deal control and settlements then trade emails to fix prices, counterparties, duplicate entries and PMAs. An automated end-of-shift variance report flags every hour and book that is not flat, every scheduled hour with no deal, and every duplicate or price mismatch. Staff can then fix these during the shift instead of after the DPR or a PMA shows them. Code puts the handling time it removes at about 1.2 hours a month, worth $100/month ($1,200/year) at $85/hour.

**Effort:** M · **Success metric:** Number of hours per month where a book was not flat or a deal was missing and the variance was first found after the shift (by the DPR, BOM SAR or a PMA), plus the share of shifts with a completed EPE Reconciliation sheet entry

**How it works today**

1. The day-ahead trader enters the deals in Enpower and the schedules in CAPS under a book such as ST-WBOM. Real-time staff get emailed instructions to make matching imbalance purchases and sales during real time. (day-ahead / real-time trader (Bill Williams)) [williams-w3/sent_items/392]
2. During the shift, real-time staff handle cuts, declined bids and generator shortfalls. They enter imbalance purchases in Enpower and email the schedulers to say how each deviation should be allocated. (real-time desk) [williams-w3/sent_items/425, williams-w3/sent_items/514]
3. Schedulers and traders check CAPS against what was actually agreed and send manual-entry corrections when the CISO or a counterparty entered a schedule wrongly. (real-time desk and CAPS schedulers) [williams-w3/sent_items/510, williams-w3/inbox/126]
4. The night shift is expected to run the CARP and fill in the EPE Reconciliation sheet. Errors in the Excel EPE schedules are found later and emailed to the lead. (night real-time traders, EPE schedulers) [williams-w3/sent_items/417, williams-w3/inbox/79]
5. The next morning, the lead reads the DPR and runs a BOM SAR. He finds double entries and missing deals in position manager, then zeroes deals or asks deal control to add them. (real-time lead, deal control) [williams-w3/sent_items/453, williams-w3/sent_items/373]
6. Price, counterparty and volume corrections reach settlements as prior-month adjustments (PMAs) and annuities. Each one gets questions and meeting requests before the revenue is trued up. (real-time lead, settlements (Virginia Thompson), risk (Heather Dunton)) [williams-w3/sent_items/442, williams-w3/sent_items/441, williams-w3/sent_items/501, williams-w3/sent_items/481, williams-w3/sent_items/387]

**Where it stalls**

- A price correction made in Enpower never reached revenue. It surfaced only a month later during the PMA review, and the lead had to ask settlements how to fix it.
  > The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753).
  [williams-w3/sent_items/442]
- A January volume change in the settlement notes was never reflected in Enpower or the inc sheet. The resulting PMA charge was disputed months later.
  > Enpower and the inc sheet do not reflect this change.
  [williams-w3/sent_items/441]
- The shift-end reconciliation depends on traders filling in a sheet by hand. When they skip it, Houston cannot tell whether the CARP was run at all.
  > Even if there are no variances, please complete the July EPE Reconciliation sheet going forward.
  [williams-w3/sent_items/417]
- Wrong values in the Excel EPE schedules went unnoticed for two days until a scheduler spotted them and escalated.
  > Please note the following due to the past two days schedules have been wrong in the EPE Schedules in Excel:
  [williams-w3/inbox/79]
- A missing deal left position manager short, and this was found after the flow date. Deal control had to be asked to investigate.
  > Pacificorp deal #694155 is not in for those hours.
  [williams-w3/sent_items/373]
- Duplicate deal entry was caught only the next morning, from the DPR and a BOM SAR, and had to be zeroed out after the fact.
  > We had some double deal-entry last night under the ST-WBOM book.
  [williams-w3/sent_items/453]

**Proposed automation**

A scheduled comparison job runs at the end of each real-time shift and again before the morning DPR. For each flow date, book and hour ending, it lines up the Enpower deals against the CAPS schedules (by schedule ID), the position manager net position and the EPE schedules sheet. It produces one exception list covering hours where a book is not flat, CAPS schedules with no matching Enpower deal and the reverse, deals that look duplicated (same book, counterparty, hours and volume entered twice), and price or volume differences between Enpower and the schedule sheets. The list is emailed to the shift and saved as that night's EPE Reconciliation sheet entry, including a dated 'no variances' line, so Houston can see that the check ran. Each corrected deal is logged with its deal number and hours, so later PMA questions can be answered from the log instead of by email. Traders still decide and enter every correction.

- Trigger: End of each real-time shift, plus a pre-DPR run early the next morning for the previous flow date
- Inputs: Enpower deal extract by book (deal number, counterparty, hours, MW, price); CAPS schedules and schedule IDs for the flow date; position manager net position by hour and zone; EPE schedules in Excel; list of books in scope (e.g. ST-WBOM, ECTRT)
- Outputs: Per-shift exception list emailed to the real-time desk: unflat hours, missing deals, possible duplicates, price or volume mismatches; Auto-filled EPE Reconciliation sheet row for each shift, including 'no variances' when the check finds nothing; Correction log (deal number, field, old and new value, who corrected it) for deal control and settlements to use when reviewing PMAs
- Existing systems: Enpower, CAPS, position manager, EPE Reconciliation sheet, DPR
- New components: extract scripts for Enpower deals and CAPS schedules by flow date and book, hour-by-hour matching and flatness rules engine, duplicate-deal detector, exception email and reconciliation sheet writer, correction log shared with settlements

**Implementation steps**

1. Confirm with the real-time desk and IT which export options exist for Enpower, CAPS and position manager (files, reports or database views). Agree the key that links a deal to a schedule, such as the schedule ID or the deal number.
2. Choose a pilot book (ST-WBOM) and write the extracts for one flow date. Compare the results by hand with a past DPR and BOM SAR to calibrate.
3. Write the matching rules: net position by hour and book, schedule without deal, deal without schedule, duplicates, and price or volume differences above a tolerance agreed with the desk.
4. Add the EPE schedules sheet as an input and write each shift's result to the EPE Reconciliation sheet, including a 'no variances' row.
5. Schedule the job at shift end and before the DPR. Send the exception list to the real-time desk distribution.
6. Run it in parallel with the manual CARP and reconciliation for a month and track false positives. Tighten the tolerances before extending it to other books.
7. Share the correction log with deal control and settlements, and use it as the first reference when PMA questions come in.

**Stays manual**

- Deciding how to correct a variance (adding, zeroing or repricing a deal, or reallocating a deviation such as Harbor's to load deviation), because that is a commercial judgment and depends on calls with the CISO or the counterparty.
- Getting the CISO or counterparties to fix schedules they entered wrongly, because that requires a phone call or email with an outside party.
- Agreeing PMAs and annuities with settlements and risk. These involve negotiated amounts and sign-off, for example by Chris on an annuity.
- Filling in placeholder deals such as counterparty 'New' until the trader confirms the real counterparty.

**Risks**

- The evidence does not show whether Enpower, CAPS or position manager can be exported automatically. If they can't, the job needs screen exports, which raises the effort. The first step therefore confirms access.
- Schedule IDs and books do not always line up (one email says all schedules should be under ECTSTSW not ECTRT). A mapping table is needed, or the report will be full of false mismatches.
- Load shifts between NP and SP can produce variances even when both CAPS and Enpower are flat. Tolerances and zone grouping must be tuned during the parallel run.
- The monthly saving is small ($100/month in code's estimate, from one mailbox only). The main value is catching revenue errors earlier, and the evidence does not quantify that. The effort should stay small to match.
- If traders come to trust the report and stop checking, a gap in an extract (a missing book, for example) could hide variances. The report should list which sources and books it loaded.

## 5. Meter volume and allocation variance resolution

Volume variances at meters (nominated vs metered vs allocated vs counterparty-reported) are found late, by hand: in the UA4 report, in month-end imbalance reviews, or when a counterparty calls asking to be paid. Each one is then worked through email chains to Daren Farmer that sit for days. A daily variance job would compare actuals against nominations, POPS allocations and Sitara deals, then send each flagged meter to its owner with the deal and contract history already attached. That replaces the research-and-chase emails, and the estimated value is $91 per month ($1,092 per year) at $85 per hour.

**Effort:** M · **Success metric:** Number of meter-days with flow but no deal or zero POPS volume still open at month-end UA4, and median days from variance to resolution

**How it works today**

1. A scheduler or volume analyst spots a variance at a meter: a counterparty short on nomination, a meter receiving under nom, or an interconnect not pulling gas. They email the volumes by day and ask the logistics desk how to handle it. (volume management / scheduler) [farmer-d/logistics/682, farmer-d/logistics/743, farmer-d/logistics/902]
2. Accounting or storage desks compare counterparty or confirmed volumes against what was booked, attach spreadsheets, and ask for the best way to correct the difference. (central desk scheduler / accounting) [farmer-d/logistics/924]
3. Unallocated volume shows up on the UA4 report. The analyst searches OSS and CPR for a deal, then reconstructs the meter's contract history month by month to work out which contract should take the volume. (volume management analyst) [farmer-d/logistics/617, farmer-d/logistics/1191]
4. When POPS feeds zero or stale volumes to Sitara, someone spots the imbalance later and asks for a manual override of POPS daily volumes using flow data from Gas Control, so the P&L is right. (risk / imbalance reviewer and volume management) [farmer-d/logistics/925, farmer-d/logistics/1013]
5. The issue goes to the logistics lead (Daren Farmer) or a trader for a decision on deal setup, buyback, reallocation or wellhead purchase. Requesters follow up with status emails while it waits. (logistics lead / trader) [farmer-d/logistics/626, farmer-d/logistics/861, farmer-d/logistics/1038, farmer-d/logistics/1357, farmer-d/logistics/102]
6. Items that are still open are gathered into periodic outstanding-issue lists with deadlines, for example for the intercompany cleanup before SAP implementation. Unresolved ones show up as payment disputes from counterparties. (volume management lead) [farmer-d/logistics/1185, farmer-d/logistics/2089]

**Where it stalls**

- Unallocated volume reaches UA4 with no deal anywhere, so the analyst has to dig up the contract history by hand before anyone can decide.
  > There wasn't any deal in 
OSS for the above reference meter, nor could I find anything in CPR.
  [farmer-d/logistics/617]
- POPS feeds zero volumes to Sitara and nobody notices until an imbalance review, so purchase costs sit in UA4 instead of the P&L.
  > This means that these purchase volumes (expenses) have 
not been picked up in Tom's P&L and are, instead, sitting in UA4.
  [farmer-d/logistics/925]
- Zero volumes in POPS have to be overridden by hand from Gas Control data, and the request has to be repeated because the first note did not get it done.
  > Please override POP'S  daily volume{ presently zero}  to reflect  daily 
activity you can obtain from Gas Control.
  [farmer-d/logistics/1013]
- Two desks use different measurement sources for the same meter, which creates a desk-to-desk variance that stays open for months.
  > ENA is using Tetco's  volume and HPLC is using the HPL Measurement volume, 
causing a desk to desk variance.
  [farmer-d/logistics/1185]
- Counterparty volumes differ from booked volumes by a large amount, and the desk has no standard correction path, so it asks by email.
  > Cilco withdrew 200,000 mmbtu's more than we booked @ bammel.  
Please let me know the best way to correct the problem.
  [farmer-d/logistics/924]
- Volume management cannot act until a trader decides the direction, and the item waits in someone's inbox.
  > I'm now awaiting on an e-mail from Gary as to the direction that he is going 
to take.  I will follow suit according to his instructions.
  [farmer-d/logistics/1357]
- Unresolved allocation turns into counterparty payment demands handled by phone, because nobody caught the gap before settlement.
  > I am getting several phone calls from Alpine Resources demanding to be paid 
for meter 5892 and there is nothing there to be paid.
  [farmer-d/logistics/2089]

**Proposed automation**

A daily variance job reads meter actuals (Gas Control and HPL Measurement daily flow) and compares them, by meter and day, with confirmed nominations and POPS allocated volumes and with the volumes on the Sitara deals tied to each meter. It flags four cases: (a) flow with no deal or no allocatable contract, which would otherwise land in UA4; (b) POPS volume of zero or missing while the meter shows flow, which is the stuck-feed case; (c) a gap between actual and nomination above a set tolerance, for example short or under-nom days; and (d) two desks using different measurement sources at one meter. For every flagged meter it builds a case sheet showing the meter's contract and deal history by month, so the analyst no longer has to reconstruct it from OSS and CPR. Each case goes to the meter's assigned volume analyst, and anything needing a commercial call goes to the logistics lead in a single daily digest instead of separate emails. Open cases age on a shared list that replaces the hand-built outstanding-issues email, so follow-up nudges are automatic.

- Trigger: Daily schedule after Gas Control / measurement actuals are loaded, plus a month-end run before the UA4 report is finalized
- Inputs: Daily meter actuals from Gas Control / HPL Measurement; Confirmed nominations by meter and day; POPS allocated daily volumes and meter allocation settings; Sitara deal numbers and volumes per meter; Deal and contract history in OSS and CPR per meter; UA4 report lines; Meter-to-analyst assignment list; Tolerance thresholds per meter or counterparty
- Outputs: Daily variance list by meter and day with variance type, for volume management analysts; Case sheet per flagged meter with contract and deal history, so no manual research is needed; Daily decision digest for the logistics lead (Daren Farmer) listing meters needing a buyback, deal setup or reallocation call; Shared open-issues list with age and owner, replacing the periodic outstanding-issues email; Month-end UA4 pre-check showing volumes still lacking a contract before close
- Existing systems: POPS, Sitara, OSS, CPR, UA4, Gas Control, HPL Measurement
- New components: Daily meter variance comparison job with configurable tolerances, Zero/missing POPS feed detector, Meter contract-history lookup that builds the case sheet, Routing table mapping meters to responsible analysts, Daily decision digest email for the logistics lead, Shared open-variance tracker with owner, age and resolution code, Month-end UA4 pre-close check

**Implementation steps**

1. Confirm with volume management and Gas Control which extracts exist for daily actuals, confirmed nominations, POPS allocations and Sitara deal volumes, and agree on one meter-day key.
2. Build read-only extracts and a variance comparison script covering the four flag types (no deal, zero POPS feed, nomination gap, source mismatch).
3. Set tolerances with the logistics lead, starting wide to avoid noise, and keep the meter-to-analyst assignment list.
4. Add the contract-history lookup from OSS and CPR so each flagged meter gets a month-by-month case sheet.
5. Run in shadow mode for one month next to the current process and compare the flags with the variance emails that actually came in, then tune the tolerances.
6. Turn on routing, the daily decision digest and the shared open-issues tracker; retire the hand-built outstanding-issues list.
7. Add the month-end UA4 pre-close run, and review open-case age weekly with the volume management lead.

**Stays manual**

- Deciding whether to set up a deal, arrange a buyback, reallocate, or treat gas as a wellhead purchase. These are commercial calls for the trader or logistics lead.
- Entering POPS overrides and reallocations. A person confirms the Gas Control figures before changing allocation that feeds the P&L.
- Settling disputes with counterparties and interstate pipelines (for example over who has custody transfer or which measurement is authoritative), which needs negotiation and sometimes Legal.
- Researching historical meters whose assignment changed and where records are incomplete. The case sheet helps, but someone still has to judge which contract should have been used.

**Risks**

- The evidence does not show what form the actuals, nomination and POPS data come in or whether automated extracts exist. If they don't, the effort could grow from M to L, so confirm data access first.
- Tolerances set too tight will flood analysts with noise and the alerts will get ignored. Mitigate with shadow mode and per-meter thresholds.
- Different measurement sources (for example pipeline volume vs HPL Measurement) can produce false variances. Record which source is authoritative for each meter and flag disagreements as their own case type.
- Preliminary flow data can change after it is first reported. Re-run on revised actuals and mark cases as provisional until measurement is final.
- The dollar value is modest ($91 per month) because it covers only email handling time. Avoided P&L hits from volumes sitting in UA4 are real but not quantified here.

## 6. Deal book transfers and booking corrections

Settlements, credit, risk and accounting staff ask the book administrator (Darron Giron) to move deals between books or fix price, counterparty or book through free-form emails. These are often forwarded two or three times, missing deal terms or IDs, and tied to same-day invoicing or book-calc deadlines. A standard book-move and booking-correction request template, with a standard completion confirmation, removes the clarifying round-trips and the forwarding hops. It is worth about $82 a month ($984 a year) in handling time and also cuts deadline risk on invoicing.

**Effort:** S · **Success metric:** Share of book-move or correction requests that are completed with no clarifying question or forwarding hop, and the median hours from request to completion confirmation.

**How it works today**

1. Settlements staff find deals in the wrong book (for example ECC deals or EnronOnline deals auto-booked into MGMT-WEST or G-DAILY-EST). They email whoever they think owns the book, and that person forwards the email to the book administrator. (settlements (Calgary) / Houston book owners) [giron-d/sent/550, giron-d/sent/405, giron-d/sent/539]
2. Settlements and accounting staff send one-off correction requests to change a price, rate or counterparty on a Sitara deal, each by its own email. (settlements / volume management) [giron-d/sent/469, giron-d/sent/117, giron-d/sent/83]
3. During the bankruptcy period, credit and risk staff send lists of counterparties or auto-terminating deals to move into the bankruptcy books, often in several batches of 'stragglers'. (credit / risk (Stacey Richardson, Cyndie Balfour-Flanagan, P. Love)) [giron-d/inbox/117, giron-d/inbox/91, giron-d/inbox/84, giron-d/inbox/57]
4. The person carrying out the move (IT/Estate database staff or the book administrator) writes back with clarifying questions: book IDs, commodity code, cutoff date for active deals, counterparty ID. (Estate database / IT (Cecilia Cheung)) [giron-d/inbox/67]
5. The deal lists are reconciled against Sitara or TAGG numbers and the price book, and someone confirms completion by email. (book administrator / risk) [giron-d/inbox/103, giron-d/inbox/94, giron-d/sent/665, giron-d/sent/469]
6. Unexplained GL differences come back later as possible write-offs and need research into which deals they relate to. (accounting (Richard Tomaski) / book administrator) [giron-d/inbox/138]

**Where it stalls**

- Requests go to the wrong person first and are forwarded on, which uses up hours on a same-day invoicing deadline.
  > Here are some more deals that need to be flipped out of the G-DAILY-EST book,
  [giron-d/sent/405]
- Wrong-book deals block invoicing for two entities until they are fixed and confirmed.
  > Invoicing for November should start today, and both ECC and ENA are held back from invoicing until these deals are fixed
  [giron-d/sent/539]
- The request has no book IDs, commodity code or cutoff date, so the executor has to send a list of questions before the move can start.
  > If I can have all the answers soon then I think the deals move can be completed around 3:00p.m.
  [giron-d/inbox/67]
- Requests carry a hard book-calc deadline and need a completion confirmation, but there is no standard confirmation format.
  > Please let me know when this is complete.  We need to have it done by the time we calc our books today - no exceptions.
  [giron-d/inbox/84]
- Deal lists arrive without Sitara numbers, so they have to be reconciled before anyone can act on them.
  > Please note that there are still several deals that I am trying to reconcile back to Sitara numbers.
  [giron-d/inbox/103]
- Verification waits for a book calc, so cross-checking is pushed to the next day.
  > Because of the translation to the bankruptcy book, we can not calc the bankruptcy book for a while, so we will cross reference those in the morning.
  [giron-d/inbox/94]
- Corrections without a recorded reason come back as unexplained GL differences that have to be researched.
  > Can you guys help try to resolve these differences?  We may have to write them off anyways, but we need to know what they relate to.
  [giron-d/inbox/138]

**Proposed quick win**

Publish one 'Book move / booking correction request' email template, plus a short completion-confirmation reply, both owned by the book administrator. The request template has one row per deal. Each row holds: deal number (Sitara or EnronOnline/TAGG ID), TAGG short name of the counterparty, current book, target book or field to change (price, rate, counterparty, book) with the new value, production month, physical or financial, reason (for example ECC counterparty, bankruptcy termination, invoice mismatch), required-by deadline (invoicing or book calc), and requester. For bulk moves such as bankruptcy transfers, the template also asks up front for the items the Estate database executor had to ask about: source and target book IDs, commodity code, active-deal cutoff date, and counterparty ID. The administrator sends a published book-owner list to settlements and credit, so requests go straight to the right person instead of being forwarded. Every completed request gets the standard confirmation, which repeats the deal list, the action taken, and the time done, so settlements can release invoicing and accounting has a record that explains later GL differences.

- Trigger: Settlements, credit, risk or accounting staff find a deal in the wrong book or with a wrong price or counterparty, usually ahead of an invoicing start or a book calc deadline.
- Inputs: deal numbers (Sitara / EnronOnline / TAGG); TAGG counterparty short names; current and target book names; field to change and new value; production month; physical or financial flag; reason for the change; deadline (invoicing or book calc); for bulk moves: book IDs, commodity code, active-deal cutoff date, counterparty ID
- Outputs: a complete request the book administrator can act on without follow-up questions; a standard completion confirmation to the requester (and accounting when invoicing is held); a book-owner contact list so requests are routed directly; a running log of corrections with reasons, for GL reconciliation
- Existing systems: Sitara, TAGG, EnronOnline, Estate database
- New components: book move / booking correction request template (email body with one row per deal), bulk-move addendum listing book IDs, commodity code, cutoff date and counterparty ID, standard completion-confirmation reply, book-owner routing list (book name to responsible controller), shared correction log (spreadsheet) recording deal, change, reason and date

**Implementation steps**

1. Draft the request template fields from the questions that recur in the evidence: deal IDs, books, field and new value, physical or financial, reason, deadline, and the bulk-move IDs and cutoff date.
2. Draft the completion-confirmation reply that repeats the deal list, the action taken, and the time completed.
3. Build the book-owner routing list (for example MGMT-WEST, G-DAILY-EST, NG-PRICE, the bankruptcy books) with the responsible person for each book, and confirm it with Jeffrey Gossett.
4. Save the template and confirmation as stationery or a saved Notes/Outlook draft for the book administrator, and send the template and routing list to the settlements, credit, risk and accounting contacts who send these requests most often.
5. When a free-form request arrives, reply once with the template, and accept it as-is only if it is a deadline-critical same-day request.
6. Start the shared correction log and record each completed request.
7. After one month, review which fields were still missing and which requests still arrived by forwarding, then adjust the template and routing list.

**Stays manual**

- Deciding whether a deal really belongs in another book (ECC versus ENA counterparty, bankruptcy eligibility), because it needs credit and legal context.
- Executing the move or change in Sitara, TAGG or the Estate database and checking the result after the book calc.
- Researching GL differences that turn up as potential write-offs.
- Prioritising same-day requests that compete for the same calc or invoicing deadline.

**Risks**

- Requesters keep sending free-form emails under deadline pressure. Mitigation: reply with the template every time, and get managers (for example Jeffrey Gossett) to endorse it.
- The routing list goes stale as book ownership changes, which was common during the bankruptcy period. Mitigation: date the list and review it monthly.
- The evidence covers only one mailbox (giron-d), so the volume and mix of requests from other desks are uncertain. The template may need more fields for cases not seen here.
- Bulk bankruptcy moves have attachments and executor-specific needs (Estate database CP IDs), and the evidence shows only one example of those questions. Validate the addendum with the IT executor before rollout.
- The savings are small ($82 a month by the formula), so the main value is fewer invoicing delays. That benefit is not priced and should not be presented as extra savings.

## 7. Deal price and invoice discrepancy resolution

Settlements staff and counterparties find price, volume or deal-coverage mismatches between invoices or payments and the Sitara deal tickets. Each one is emailed to the logistics deal owner, who often answers late, so payments and invoices due dates are put at risk. A matching job that compares each invoice or payment line with the Sitara deal for that month, and sends the deal owner one queue item showing both values, cuts the manual lookups and the reminder emails. It is worth about $63 per month ($756 per year) at $85 per hour.

**Effort:** M · **Success metric:** median hours from a discrepancy being logged to the deal owner's resolution, and the count of follow-up or escalation emails per month on price or invoice discrepancies

**How it works today**

1. A counterparty invoice, payment or price statement arrives in Gas Settlements. The analyst compares it by hand with the Sitara deal ticket and finds that the price, volume or deal coverage does not match. (Gas Settlements analyst) [farmer-d/logistics/133, farmer-d/logistics/124, farmer-d/logistics/949]
2. The analyst emails the logistics deal owner (mostly Daren Farmer), names the deal number, the counterparty's value and the Sitara value, and asks which one is correct. If no deal can be found, the analyst asks whether one is missing or who the trader is. (Gas Settlements analyst to logistics deal owner) [farmer-d/logistics/133, farmer-d/logistics/949, farmer-d/logistics/963, farmer-d/logistics/1438]
3. The deal owner checks the deal and the trader's intent, and sometimes has to bring in the trader or the counterparty's trader. This happens when the counterparty's accountant does not show the deals in their system. (logistics deal owner / trader) [farmer-d/logistics/963, farmer-d/logistics/839]
4. If no answer comes, settlements sends follow-ups and escalations, often because a counterparty is pressing or an invoice payment date is close. (Gas Settlements analyst) [farmer-d/logistics/99, farmer-d/logistics/1488, giron-d/sent/178]
5. The deal owner corrects the deal in Sitara or cuts it off going forward. Settlements then redrafts the invoice in Unify or nets or adjusts the balance in SAP, and sends a corrected invoice to the counterparty. (logistics deal owner, then Gas Settlements) [giron-d/sent/636, farmer-d/logistics/965, farmer-d/logistics/2087, farmer-d/logistics/124]

**Where it stalls**

- Settlements waits on the deal owner to say which price is correct and has to chase for an answer, so the invoice stays open in the meantime.
  > I have not received a response from you regarding the pricing discrepancies on these deals.
  [farmer-d/logistics/99]
- The mismatch is found only after the counterparty disputes the price. It is then passed on by email as two numbers that someone has to look up by hand.
  > For sale deal 707274, DEFS says the price on 4/4 should be 5.25 and we have 5.20 in Sitara.
  [farmer-d/logistics/133]
- Sitara was not updated for the month, so the invoice had to be redrafted in Unify after the fact.
  > The Sitara was not updated for Aug.  I just corrected Sitara.  So you can
  [giron-d/sent/636]
- The counterparty does not recognize deals entered in Sitara, and settlements cannot tell who the responsible trader is. This blocks payment close to the due date.
  > I don't have another trader's name.  Could you please talk to your KN
  [farmer-d/logistics/963]
- Deal coverage gaps (days with no valid deal) are only found when the invoice is worked.
  > There are only two deals on PGEV pipeline: Deal #156071- valid 02/01/00 -
  [farmer-d/logistics/949]
- The counterparty presses for an answer and settlements escalates to logistics with no context added.
  > Help .   Steve Mauch at Hesco is wanting an answer ASAP
  [farmer-d/logistics/1488]
- Settlements bills without knowing the deal structure (an exchange deal), and the balance has to be netted in SAP afterwards.
  > I did not know that this was part of a Natural Gas / Crude Oil exchange deal
  [farmer-d/logistics/2087]

**Proposed automation**

The settlements analyst enters or uploads each counterparty invoice, payment or price statement as line items (counterparty, production month, point or meter, deal number if given, day range, volume, price). A matching job looks up the Sitara deals for that counterparty, point and month. It checks that the price matches, that the volume is within tolerance, and that every day of the range is covered by a valid deal. It also flags lines with no deal at all and deals that have a deal-type flag such as an exchange. Each mismatch becomes one queue item routed to the deal's owner in Sitara (the trader or logistics contact). The item shows the counterparty value and the Sitara value side by side, along with the invoice due date, and lets the owner choose: Sitara is correct (dispute the invoice), Sitara needs correction, or the deal is missing or belongs to another trader. Open items are reminded automatically and escalated as the payment due date nears, which replaces the ad-hoc chasing emails. When the owner resolves an item, settlements is told it can redraft in Unify or adjust in SAP.

- Trigger: A counterparty invoice, payment or price statement is logged by Gas Settlements. A nightly re-run checks open items against Sitara changes.
- Inputs: counterparty invoice, payment or price lines (counterparty, production month, point, deal number, day range, volume, price); Sitara deal tickets for the counterparty and month (deal number, price or index terms, valid dates, volume, trader or owner); invoice drafts in Unify for the same month; invoice payment due dates entered by settlements
- Outputs: a mismatch queue item for the deal owner, showing the counterparty and Sitara values side by side and the due date; an automatic reminder and escalation on open items, sent to the deal owner and their lead; a resolution notice to the settlements analyst (dispute the invoice, or redraft in Unify after the Sitara correction); a monthly report of discrepancies by counterparty and cause for settlements and logistics management
- Existing systems: Sitara, Unify, SAP
- New components: structured invoice and payment line intake form or upload template, invoice-to-deal matching job with price and volume tolerances and a day-coverage check, discrepancy queue with owner routing and three resolution choices, due-date-driven reminder and escalation rules, monthly discrepancy report

**Implementation steps**

1. Agree with Gas Settlements and logistics on the fields an invoice line must carry, and on price and volume tolerances, taking examples from recent disputes (DEFS, Duke, Midcon, Hesco).
2. Build a read-only extract of Sitara deals by counterparty, point and month, including valid date ranges and the deal owner or trader.
3. Build the intake form or upload template that settlements uses to log counterparty invoice and payment lines with a due date.
4. Write the matching job: find the deal by number or by counterparty, point and month, then compare price and volume and check that each day is covered by a valid deal.
5. Stand up the discrepancy queue with routing to the Sitara deal owner, the side-by-side view and the three resolution choices.
6. Add reminder and escalation rules keyed to the invoice due date, and a notice back to settlements on resolution.
7. Pilot for one production month with the settlements analysts who raise the most disputes against Daren Farmer's deals, and compare against the email threads for the same month.
8. Roll out to all desks, then retire the email route for price-confirmation requests.

**Stays manual**

- Deciding whether the deal or the invoice is wrong needs the trader's knowledge of what was agreed with the counterparty.
- Correcting the deal in Sitara or cutting off a deal going forward stays a logistics or trader action.
- Talking to the counterparty's trader or accountant when they do not recognize a deal is a relationship call.
- Netting exchange-deal balances in SAP and redrafting invoices in Unify remain with Gas Settlements.
- Investigating old suspended payments where the original owner has left needs human judgment.

**Risks**

- The evidence does not show how counterparty invoices reach settlements (paper, fax or email). If lines must be keyed in by hand, intake effort could eat into the savings. Mitigate by starting with an upload template and measuring keying time.
- Index-priced deals (for example IF plus a fee) need the published index to compute an expected price, and the evidence does not show where that index is held. Mitigate by flagging index deals for review rather than auto-matching them.
- Sitara owner or trader fields may be stale when traders leave, which would misroute items. Mitigate with a fallback to the logistics desk lead.
- Volume differences driven by meter flow rather than deal entry could flood the queue. Mitigate with tolerances and by separating volume-only items.
- The volume is modest, at about $63 per month, so the build must stay small. The main value is fewer late payments and less chasing, not handling hours.

## 8. Trading book, curve and system access setup

Requests to set up Tagg books, portfolio and book codes, pipe and curve mappings, and user access reach the book administrators as free-form emails, so admins write back for missing details and requesters chase them. The fix is one book and access request template, kept in a shared folder and filled in by the desk before anything goes to the administrators, plus a short reply admins send to redirect free-form requests to it. The main benefit is fewer clarification round trips and faster book creation. Code values the handling time at about $45 a month ($540 a year).

**Effort:** S · **Success metric:** share of book and access requests that are set up without any clarifying email from the admins, tracked in the request log

**How it works today**

1. A new business unit or desk is created, and the system administrator asks the desk which pipes must be mapped so traders can book deals on it. (Tagg/Sitara system administrator (Imelda Frayre)) [giron-d/sent/777]
2. The desk lead emails a book request in free text to whichever admin he has been told handles it, listing book names, the counterparty the books fall under, and the risk types (P, B, I and GD), often marked as urgent. (desk lead / book requester (Darron Giron, Kam Keiser)) [giron-d/sent/769, giron-d/sent/650, giron-d/inbox/161]
3. The book administrators set up the book and email back a confirmation, which the requester later forwards as audit evidence. (book administrators (Susan Trevino, Burton McIntyre)) [giron-d/sent/526, giron-d/sent/525]
4. Portfolio and book codes, post ids and file names are then relayed by separate emails to the people who need them downstream. (desk lead and risk staff) [giron-d/sent/470, giron-d/inbox/403, giron-d/sent/157]
5. Trader-to-book assignments for price, basis and index, EOL products and Sitara curve mappings are gathered by spreadsheet and email from each region before the Tagg IT meeting. (risk managers and regional leads (Dawn Kenne, Kam Keiser, regional leads)) [giron-d/sent/412, giron-d/inbox/132, giron-d/inbox/155]
6. User access and reporting-line changes (Book Admin list, PEP reviewer, print access for books) are requested one by one by email. (desk lead to the relevant admin) [giron-d/sent/18, giron-d/sent/523, giron-d/sent/520]

**Where it stalls**

- The requester does not know who handles new Tagg books, so the request is routed by word of mouth and can reach the wrong person first.
  > We need to add a new book in Tagg.  Kam suggested I send the request to you.
  [giron-d/sent/769]
- The admin has to come back to ask which pipes the new business units will trade before traders can book deals, because the original request did not list them.
  > Darron, do you know which pipes these two new business units will be
  [giron-d/sent/777]
- Coding conventions for book and portfolio codes are written into the email body every time, and the admin must phone back when the codes requested are not available.
  > We need all price, basis, index, and gas daily US books to be the same, all Canadian books to be the same and all physical books to have the same codes please.
  [giron-d/inbox/161]
- The trader-to-book matrix is requested at short notice because it is needed for a Tagg IT meeting, which puts the desk under pressure to turn it around the same morning.
  > We have a meeting set up with Tagg IT and need this
  [giron-d/sent/412]
- Routing of risk types to trader books is decided late, after the books exist, and has to be confirmed in a separate round of emails.
  > Also, when physical deals are done, will all risk types go to the same desk or will one person be managing the index separately.
  [giron-d/inbox/132]
- Access is not set up fully with the book, so the requester finds a gap later and has to ask for help.
  > I can calc postids for FT-NW but cannot print.  Please help.
  [giron-d/sent/520]

**Proposed quick win**

Create one Book and Access Request template (a single spreadsheet tab plus an email subject convention, 'Book Request - <desk> - <book name>') with required fields for everything the admins asked for later in the threads: book names, the counterparty or legal entity they fall under, region and desk, risk types (price, basis, index, gas daily), requested book and portfolio codes and the fallback if they are taken, pipes to map, Sitara curve mappings, EOL products, traders assigned per risk type, users who need Book Admin, calc or print access, the date by which deals must move, and the approver. Store it in the shared Netco controls folder next to the existing Trader-Book template, and put a routing line at the top that names the book administrators as the single destination. The desk lead fills it in and sends it to the book administrators, cc the risk lead. The admins keep a short prepared reply that returns any free-form request with the template attached and lists the missing fields. A one-page checklist at the bottom ('before you send') covers the items that caused follow-ups: pipes mapped, risk types routed to trader books, codes consistent across regions, and print and calc access for every user.

- Trigger: A desk, business unit, counterparty entity or trader needs a new trading book, mapping change or user access in Tagg, Sitara or EOL.
- Inputs: book names, counterparty entity and region or desk; risk types per book (price, basis, index, gas daily); requested book and portfolio codes; pipes to map to the business unit; Sitara curve mappings (from CurveMappings.xls); EOL products and trader-to-book assignments; users needing Book Admin, calc or print access; required-by date and approver
- Outputs: a complete book request the book administrators can action without a clarifying email; the admins' confirmation reply with the assigned book and portfolio codes, sent back to the requester and kept for audit; a filled-in record of trader and risk-type routing that serves as the trader matrix for Tagg IT
- Existing systems: Tagg, Sitara, EOL, PEP
- New components: Book and Access Request template (spreadsheet tab with required fields and a routing header), 'before you send' checklist covering pipes, risk-type routing, code consistency and access, prepared admin reply that returns free-form requests with the template and the missing fields, email subject convention 'Book Request - <desk> - <book name>', request log tab where admins record the request number, the codes assigned and the confirmation date

**Implementation steps**

1. Collect the fields admins have asked for after the fact in past book threads (pipes, counterparty entity, risk types, codes, trader assignment, access) and agree the required field list with the book administrators.
2. Build the template and checklist as one spreadsheet in the shared Netco controls folder, reusing the columns of the existing Trader-Book template so the trader matrix and the book request are the same document.
3. Add the routing header naming the book administrators as the one destination, and the subject convention.
4. Write the prepared reply the admins send back for any free-form request, with the template linked and a list of missing fields to fill in.
5. Announce the template to desk leads and regional leads, and have Kam Keiser and Darron Giron use it for the next batch of book requests as the pilot.
6. After one month, review the request log for requests that still needed a clarifying email and add the missing fields to the template.

**Stays manual**

- Choosing book names and which trader or desk owns each risk type is a desk decision that needs the traders' input.
- Admins still decide whether a requested book or portfolio code is available and pick the alternative.
- Approving access and reporting-line changes in PEP stays with HR and the supervisor.
- Urgent setups for reorganizations (for example the Netco books for all regions) still need direct calls between the desk and the admins.

**Risks**

- Requesters may keep sending free-form emails out of habit; mitigate by having the admins consistently send the prepared reply rather than piecing details together.
- The evidence comes from a single mailbox (giron-d), so the admins' own intake steps and their real field requirements are inferred; validate the field list with the book administrators before rollout.
- TDS is named in the process description but never appears in the sampled messages; confirm whether TDS access belongs on the form before adding it.
- A template that is too long may slow down simple access requests; keep the access-only section short and optional fields clearly marked.
- Low value at about $45 a month means this should stay a low-cost template, not a system build.
