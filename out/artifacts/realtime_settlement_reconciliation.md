---
opportunity: realtime_settlement_reconciliation
type: sop
citations: [williams-w3/sent_items/442, williams-w3/sent_items/453, williams-w3/sent_items/291, williams-w3/sent_items/90, williams-w3/sent_items/510, williams-w3/sent_items/441]
---

# SOP: Daily real-time settlement reconciliation

Owner: the real-time trader, with settlements (Jim Reyes, Heather Dunton, Virginia Thompson) and the CAPS scheduling group as readers. Value: about $77 a month ($924 a year) at $85/hour. It is a small gain in handling time. The main benefit is catching missed revenue earlier.

## What the job produces

Each morning, once the DPR for the prior flow day is available, the job compares Enpower deals (by book: ST-WBOM, ST-CALI, ST-WHOURLY, ECTRT, ECTSTSW) with CAPS final schedules, position manager, and CAISO congestion and replacement-reserve awards. It matches on hour ending, schedule ID and counterparty. It produces:

1. A daily variance report by hour and book, sent as a morning digest to the real-time desk, the CAPS group and settlements. It replaces the ad hoc variance emails.
2. Exception queue rows, each with an owner, age, expected revenue (MW x price per HE) and the source of each side.
3. A PMA validation report when a monthly PMA file arrives, flagging lines with no matching change in Enpower or the inc sheet.
4. A weekly aging summary of open corrections, reviewed before the P&L flash.

## What a person checks

- **Trader, each morning:** open the digest and review each exception. Typical types are a duplicate deal, a CISO misentry, an award with no booked revenue, or a counterparty or price change with no revenue effect. Example of a duplicate:
> We had some double deal-entry last night under the ST-WBOM book. Consequently I zeroed the following deals out this morning after receiving the DPR and running a BOM SAR.

  [williams-w3/sent_items/453]
- **Settlements:** for an award with no booked revenue, confirm the expected amount and book the true-up. Example of the gap the queue should surface at once instead of a month later:
> The appropriate price is in Enpower, but the revenue has never appeared (Deal #590753).

  [williams-w3/sent_items/442]
- **PMA review (Virginia Thompson):** check each flagged line, such as a charge for a reduction in a purchase. Example of the mismatch the validator should flag:
> Enpower and the inc sheet do not reflect this change.

  [williams-w3/sent_items/441]
- **CAPS group:** fix CAPS entries when the CISO misenters a schedule.
> For HE 11 and HE12, Danielle at the CISO misentered our schedule.

  [williams-w3/sent_items/510]

## Exceptions

- **Position manager noise.** Position manager sometimes reports variances that vanish in the detail view [williams-w3/sent_items/291]. The job compares at detail level and drops variances that disappear there. Anything it still cannot explain goes to the trader.
- **Missing CAISO data.** When the CAISO site has no data for an hour, as when its server went down [williams-w3/sent_items/90], mark the hour "no source data". Do not treat it as zero revenue or as a variance. The trader confirms the amount with the CAISO and records it in the row.
- **Aging.** Any exception still open at the weekly review is escalated to its owner before the P&L flash.
- **Job failure or missing feed.** The trader falls back to the manual DPR and BOM SAR check for that day.

## Stays manual

- Choosing the correcting entry: zero a deal, enter an imbalance purchase, or book an annuity between books.
- Taking a charge for a counterparty and deciding how to allocate deviation.
- Disputes with the CISO/CAISO, which need calls and recorded-line evidence.
- Approving and booking PMAs and true-ups (settlements).
- Tape pulls to confirm what was traded when no system record exists.

## Success measure

The share of variances and PMA questions that first appear in the daily queue rather than in an ad hoc email, and the median days an exception stays open before its correcting entry or PMA is booked. Run the job alongside the manual process for two weeks on ST-WBOM before retiring the ad hoc emails.
