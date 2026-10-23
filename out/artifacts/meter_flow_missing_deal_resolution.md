---
opportunity: meter_flow_missing_deal_resolution
type: sop
citations: [farmer-d/logistics/130, farmer-d/logistics/1356, farmer-d/logistics/1149, farmer-d/logistics/1981, farmer-d/logistics/899]
---

# SOP: Daily meter-flow exception run (flow with no valid deal)

**Scope.** Gas flowing at a meter with no Sitara deal, an expired deal term, or volume parked on Strangers Gas. Today Volume Management, logistics and accounting email the deal owner (mostly Daren Farmer's desk) one meter at a time. The evidence shows 260 messages over about 24 months, roughly 11 a month, worth about $184 a month ($2,208 a year) at $85/hour.

## What the automation produces each day
After the nightly allocation load, a job compares allocated and metered volumes by meter and day against active Sitara deal tickets. It writes one exception record per gap with:
- meter, uncovered dates and volumes;
- the closest existing deal (same meter and counterparty, term ending just before or starting just after), so the request names a deal to extend, as in this typical ask:

> Daren can you please extend Deal #422516 to cover flow of 9 dec. for 10/6/2000
[farmer-d/logistics/1981]

- the deal owner on record, from the desk-maintained meter-to-owner lookup.

Outputs: a daily digest to each deal owner (extend / create / refer actions), a shared exception list with status, escalation notices, and a monthly aging report.

## Who does what
| Role | Daily task |
|---|---|
| Deal owner (trader) | Open the digest. For each item choose extend, create new deal or buy-back, or refer for write-off. |
| Volume Management / logistics analyst | Check the shared exception list instead of emailing. Add notes only where the record is wrong. |
| Accounting / settlements | Watch items tied to a payment cutoff; confirm status before the deadline. |
| Desk lead | Receives escalations and the aging report. Maintains the owner lookup and fallback owners. |

## What a person checks
1. Digest items carry a plausible suggested deal. Reject or correct it if the term or counterparty is wrong.
2. Parked volume is visible. An analyst who parks volume on Strangers Gas, as here, leaves it on the list until a deal is chosen:

> I'm going to place 98-9676 on Strangers Gas until you hear back from Daren or Julie.
[farmer-d/logistics/899]

3. Repeat gaps on the same meter (partial-month coverage) are grouped by deal, not listed day by day:

> Can you assist Anita and I w/a deal number to place the 1st 20 days on.
[farmer-d/logistics/1149]

## Exceptions
- **Near month-end or a payment cutoff:** items still open escalate to the desk lead. Example of the pressure this relieves:

> Payment MUST be set up by noon 5/24/01 for prompt payment to Spinnaker.
[farmer-d/logistics/130]

- **Old or questionable volume** (found long after the fact, counterparty gone): not auto-resolved. It goes to the approver with an investigation request, since the approver will not sign off blind:

> I am uncomfortable putting a deal out there without more details.
[farmer-d/logistics/1356]

- **Cross-desk pieces** (for example East desk Unify paths): the deal owner coordinates by hand.
- **Unowned meter:** goes to the fallback owner and appears on a weekly unowned list.
- **Small or single-day volumes** below the threshold are held back from the digest and shown only on the aging report.

## Stays manual
Choosing extend vs. new deal vs. buy-back, pricing on new or extended deals, write-offs to unaccounted-for gas or OBA/PPA treatment, approval of old volumes, and Unify path changes across desks.

## Run cadence and review
Nightly after the allocation load, plus extra runs in the last week of the month and before settlement cutoffs. Roll out in report-only mode for one month, then review unresolved items after two production months. Track: exceptions open at month-end close, median days from first flow to a deal being extended or created, and the count of ad-hoc "please extend deal" emails.

Caveat: evidence comes from one mailbox (farmer-d), and the allocation and Sitara data feeds must be confirmed before build; keep a manual export as fallback.
