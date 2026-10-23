---
opportunity: realtime_shift_position_handoff
type: template
citations: [williams-w3/sent_items/466, williams-w3/sent_items/433, williams-w3/sent_items/395, williams-w3/sent_items/403, williams-w3/sent_items/506]
---

# Real-time shift handoff template (Service Sheet tab)

Use: the desk lead fills it each evening for the next trading day, pastes the filled table into the email to DL-Portland Real Time Shift, and the operator going off fills the Return section at shift end. The aim is that nobody has to write "one more time" or ask what a line meant. The modelled value is small (about $52 a month, $624 a year), so the gain is fewer missed entries and correction re-sends.

## Why these fields

Today each position goes out as free text, for example:

> We are long 25 mws on peak for 06/27/01 in SP-15.  This should be in CAPS under ST-WBOM, deals should be under ST-WBOM in Enpower as well.

[williams-w3/sent_items/466]

Enpower entry is split across people, so the open items must be named:

> Please put the price in for deal #672781 (buy from EPE).

[williams-w3/sent_items/433]

Corrections go out as separate emails, which forces the shift to merge messages [williams-w3/sent_items/403]. Other desks' positions sit in their own sheet [williams-w3/sent_items/506].

## Section 1: Positions (one row per position)

| Date | HE from-to | Hub (NP-15 / SP-15) | MW | Long / Short | Price | Book (ST-WBOM / ST-CALI / St-SW) | In CAPS? | Enpower deal #s already entered | Still to key or price | Revised? |
|---|---|---|---|---|---|---|---|---|---|---|
| [date] | [HE 7-22] | [hub] | [25] | [long] | [price] | [book] | [Y/N] | [#] | [e.g. price on EPE buy] | [no] |

A correction is a new row marked "revised", not a new email.

## Section 2: Other desks' positions

- ST-CALI / St-SW length or shorts: [link to ST-CALI sheet, time of last update]. Do not retype.

## Section 3: Special duties this shift

- [APS losses: MW, HE, tag made by, Enpower deals]
- [BPA hourly check-out: call after the EPE dispatcher call; initial each hour]
- [NEVP transmission notice: lead time]
- [Ancillary dispatch to track and record on the EES sheet]

## Section 4: Standing instructions changed

- [Instruction, who confirmed it, date. Example: unit ramp order]

## Section 5: Return (operator fills at shift end)

- Missed or changed schedules: [HE, reason]
- Transmission requests withdrawn or removed by dispatchers: [hour, MW, who removed]
- Enpower items still open: [deal #]
- Problems for the lead: [text]

The dispatcher-removal line exists because the lead asked for exactly this report:

> Send me an email each time the dispatchers remove requests on our behalf

[williams-w3/sent_items/395]

## Stays manual

Positions, prices and book choice stay with the desk lead. Real-time trades and dispatcher calls stay with the operators. Contesting charges stays manual; the Return section only provides the trail.
