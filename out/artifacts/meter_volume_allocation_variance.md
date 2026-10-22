---
opportunity: meter_volume_allocation_variance
type: sop
citations: [farmer-d/logistics/617, farmer-d/logistics/925, farmer-d/logistics/1013, farmer-d/logistics/924, farmer-d/logistics/682, farmer-d/logistics/743, farmer-d/logistics/902, farmer-d/logistics/1185, farmer-d/logistics/1357, farmer-d/logistics/2089, farmer-d/logistics/861]
---

# SOP: Daily meter variance review (Logistics / Volume Management)

**Purpose.** Catch differences between nominated, metered, allocated and counterparty-reported volumes at each meter on the day they happen. Today they surface late, on the UA4 report, in imbalance reviews, or when a counterparty calls.

> There wasn't any deal in OSS for the above reference meter, nor could I find anything in CPR.

[farmer-d/logistics/617]

> Someone needs to be overriding the 0 volumes so that Sitara is receiving correct information and the P&L is kept as accurate as possible.

[farmer-d/logistics/925]

## What the automation produces

Once Gas Control / HPL Measurement actuals are loaded each day, a variance job compares every meter-day with confirmed nominations, POPS allocated volumes and the Sitara deals tied to the meter. It produces:

1. **Daily variance list** by meter and day, sent to the meter's assigned volume analyst. Each line carries one of four flags:
   - (a) **No deal / no contract**: flow with no allocatable contract, which would otherwise land in UA4 [farmer-d/logistics/617].
   - (b) **Zero POPS feed**: POPS shows zero or missing volume while the meter is flowing [farmer-d/logistics/925], [farmer-d/logistics/1013].
   - (c) **Nomination gap**: actual vs nomination is outside tolerance, such as short days, receiving under nom, or a counterparty not pulling gas [farmer-d/logistics/682], [farmer-d/logistics/743], [farmer-d/logistics/902].
   - (d) **Source mismatch**: two desks use different measurement at the same meter, or counterparty volumes differ from booked volumes [farmer-d/logistics/1185], [farmer-d/logistics/924].
2. **Case sheet** for each flagged meter, showing month-by-month contract and deal history from OSS and CPR, so analysts no longer have to rebuild it by hand.
3. **Daily decision digest** for the logistics lead (Daren Farmer), listing the meters that need a buyback, deal setup or reallocation call.
4. **Shared open-variance tracker** with owner, age and resolution code. It replaces the hand-built outstanding-issues email [farmer-d/logistics/1185].
5. **Month-end UA4 pre-check**: volumes still without a contract, run before the UA4 report is finalized.

## Daily routine

| When | Who | Action |
|---|---|---|
| After actuals load | Volume analyst | Open your variance list. For each flag, check the case sheet and confirm the Gas Control figure before you act. |
| Same morning | Volume analyst | Flags (b) and (c) with a clear fix: enter the POPS override or reallocation, then close the case with a resolution code. |
| Same morning | Volume analyst | Anything that needs a commercial call (deal setup, buyback, wellhead purchase): set it to "decision needed" so it appears in the digest. Do not email it separately. |
| Midday | Logistics lead / trader | Work through the digest and record the decision on each case in the tracker [farmer-d/logistics/1357]. |
| Weekly | Volume management lead | Review open cases by age. Escalate anything waiting on a counterparty, a pipeline or Legal. |
| Month-end | Volume management | Run the UA4 pre-check and clear or assign every meter-day that still has no contract. |

## What a person still checks (stays manual)

- **Commercial calls** on deal setup, buyback, reallocation or wellhead treatment. These belong to the trader or logistics lead.
- **POPS overrides and reallocations.** The analyst confirms the Gas Control numbers before changing allocation that feeds the P&L.
- **Disputes** with counterparties and pipelines over custody transfer or which measurement is authoritative, which may involve Legal.
- **Historical meters** whose records are incomplete. The case sheet helps, but someone still decides which contract applies.

## Exceptions

- **Preliminary flow data**: mark the case *provisional* and re-run once measurement is final.
- **Source disagreement** (type d): record which source is authoritative for that meter. Keep the case open as its own type until both desks agree [farmer-d/logistics/1185].
- **Too many flags**: tell the logistics lead so the per-meter tolerances can be widened. The first month runs in shadow mode next to the current emails to tune them.
- **Counterparty payment demand** on a meter with no allocation: open a type (a) case at once and attach the caller's volumes.

> I am getting several phone calls from Alpine Resources demanding to be paid for meter 5892 and there is nothing there to be paid.

[farmer-d/logistics/2089]

## Measure of success

Track the meter-days with flow but no deal, or zero POPS volume, that are still open at the month-end UA4, plus the median days from variance to resolution. The goal is to stop "status?" follow-ups like [farmer-d/logistics/861]. Value of the email handling time saved: $91 per month ($1,092 per year) at $85/hour.
