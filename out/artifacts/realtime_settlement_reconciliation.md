---
opportunity: realtime_settlement_reconciliation
type: sop
citations: [williams-w3/sent_items/453, williams-w3/sent_items/442, williams-w3/sent_items/291, williams-w3/sent_items/510, williams-w3/sent_items/90]
---

# SOP: Daily real-time settlement reconciliation

**Owner:** real-time desk (Bill Williams). **Closing owners:** settlements (Virginia Thompson, Heather Dunton, Jim Reyes).
**Value:** about 0.9 hours a month of handling, $77 a month, $924 a year at $85/h. The case rests mainly on catching breaks earlier, so keep the build light.

## What the job produces
Each morning, after the DPR is published, the job matches the prior day's Enpower deals (by book, such as ECTRT, ST-WBOM, ST-CALI) against CAPS final schedules by schedule ID and hour ending. It emails one variance list to the desk and settlements. It also:
- Flags duplicate deals, deals missing from CAPS, CAPS schedules missing from Enpower, and award hours with no revenue line.
- Calculates expected congestion and replacement-reserve revenue from awarded MW and price, replacing the hand calculation.
- Updates a break log with owner, status and age.
- At month end, checks each PMA line against Enpower deal history and the inc sheet.

## Daily routine (real-time desk)
1. Open the morning variance list. Check the CAISO award file was loaded. If the feed is missing, upload the desk's award file by hand.
2. For each variance, decide: real break, or position manager display fault. Position manager is only a cross-check, since it has reported variances that vanish in the detail view [williams-w3/sent_items/291].
3. Duplicate deals: confirm, zero out in Enpower, and note it in the break log. This is the case the job exists to catch earlier:

> We had some double deal-entry last night under the ST-WBOM book.

[williams-w3/sent_items/453]

4. Schedule mismatches (firm vs n-firm, wrong ID such as ECTRT vs ECTSTSW): assign to scheduling and ask the CISO for a fix. Example of the pattern:

> For HE 11 and HE12, Danielle at the CISO misentered our schedule.

[williams-w3/sent_items/510]

5. Expected-revenue lines: send to settlements to check against the CAISO statement. Hours with no CAISO data show as "unconfirmed", not zero. A verbal confirmation on a recorded line is noted in the log [williams-w3/sent_items/90].

## Settlements routine
1. Take ownership of each assigned break in the log. Set the status and close it only once the entry posts.
2. Review open prior-month items (unposted PMAs, price corrections) every week. The log replaces email threads such as:

> The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753).

[williams-w3/sent_items/442]

## Month-end PMA check
When the PMA file arrives, run the checker. Review every line it flags as unsupported by Enpower or the inc sheet before accepting it. If the file layout needs a manual import at first, the desk does that step.

## Exceptions and what stays manual
- Choosing the correcting entry, zero-out or PMA amount: settlements and the desk.
- Annuities between books: the desk head approves; settlements books.
- Disputes with the CISO/CAISO or counterparties, and tape pulls (Chip Cox) for undocumented trades.
- A break unresolved after its agreed age limit goes to Virginia Thompson for a meeting with the desk.
- Noisy matches (inconsistent books or schedule IDs): add to the mapping table, don't suppress.

## Rollout notes
Run alongside the current DPR and BOM SAR check for two to four weeks. Retire free-text adjustment emails only for break types the job reliably catches. Confirm Enpower and CAPS extract access first, since the evidence doesn't show it.

**Measures:** median age of open breaks, and the share of breaks first found by the morning job rather than by email.
