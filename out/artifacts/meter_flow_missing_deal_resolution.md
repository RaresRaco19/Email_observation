---
opportunity: meter_flow_missing_deal_resolution
type: sop
citations: [farmer-d/logistics/782, farmer-d/logistics/130, farmer-d/logistics/1356, farmer-d/logistics/899, farmer-d/logistics/1224, farmer-d/logistics/1981]
---

# SOP: Daily meter-versus-deal exception digest

**Purpose.** Replace one-off chase emails to the deal owner with a nightly exception list. Today the work is about 10.81 requests a month, worth about $184 a month ($2,208 a year) at $85/hour. The stall looks like this:

> Logistics is waiting to hear from Daren on this issue.

[farmer-d/logistics/782]

## What the automation produces
A nightly job runs after the day's allocations post. It compares allocated and measured volumes by meter and gas day with active Sitara deal tickets. Each meter-day lands in one bucket: covered, no deal, outside the deal term, or parked on Strangers Gas. It produces:
- A daily digest per deal owner (for example Daren Farmer for HPL). Each line has the meter, date range, volume, the nearest deal number to extend, and three actions: extend, create new, or route to write-off/approval.
- A shared open-exceptions list for volume management, showing age, status and owner.
- An escalation notice to the desk lead for old items or items with a payment deadline.
- A month-end summary of meter-days with flow but no deal, and volume on Strangers Gas.

## Daily steps for the desk
1. **Volume management (Jackie Young, Aimee Lannou):** open the shared list each morning. Do not email the owner for anything already on the digest. Check that new lines match what the allocation exception screen or Feedback Monitor shows.
2. **Deal owner:** work your digest. Extend the deal, create a new one, or send the item to approval. Record the decision in the log with a reason. A typical case is a deal that ends before the flow does:

> I checked the deal ticket (286824) and it ends on 6/17.

[farmer-d/logistics/1224]

3. **Volume management:** once a covering Sitara deal appears, confirm the Unify path exists. An extension without a path stays open. Then re-allocate and close. Reopened prior-period items show as reopened, not as new.
4. **Desk lead:** act on escalations the same day. Items tied to a payment deadline come first:

> Payment MUST be set up by noon 5/24/01 for prompt payment to Spinnaker.

[farmer-d/logistics/130]

## What a person checks
- Weekly: unassigned items, which go to the desk default owner, and wrong routing between the HPL and East desks.
- Meter number formats (such as 98-9676 or 0986725). Fix mismatches in the meter key table [farmer-d/logistics/899].
- Month end: compare the success measure (meter-days with flow but no covering deal, and median days from first flow to a deal) with last month.

## Exceptions that stay manual
- The decision to extend, create, or treat the flow as unauthorized. This is the trader's pricing call. The 1981 thread shows the typical ask the digest pre-fills [farmer-d/logistics/1981].
- Write-offs to unaccounted-for gas, buy backs and old prior-period adjustments. The approver needs the facts before agreeing:

> I am uncomfortable putting a deal out there without more details.

[farmer-d/logistics/1356]

- Periods that may be too old to process (before the move to Unify), and volume disputes with outside parties such as Enerfin or HL&P.
- Meters with no deal history: the job sends them to the desk default, and a person assigns an owner.

## Rollout note
Run in shadow mode for one month beside the email process, then switch on the HPL desk first. The evidence comes from one mailbox (farmer-d), so check volumes on other desks before extending.
