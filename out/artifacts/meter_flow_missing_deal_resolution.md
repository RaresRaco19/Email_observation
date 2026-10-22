---
opportunity: meter_flow_missing_deal_resolution
type: sop
citations: [farmer-d/logistics/896, farmer-d/logistics/1055, farmer-d/logistics/1149, farmer-d/logistics/1160, farmer-d/logistics/1485, farmer-d/logistics/1356, farmer-d/logistics/1489, farmer-d/logistics/1972, farmer-d/logistics/1999, farmer-d/logistics/2137, farmer-d/logistics/130, farmer-d/logistics/117]
---

# SOP: Resolving metered flow with no valid Sitara deal (exception queue)

**Owner:** Texas desk deal owner (currently Daren Farmer), with volume management and settlements as requesters.
**Applies to:** current and recent production months only. Older periods stay on the manual approval path (step 5).

## Why this exists

Today volume management types the meter, deal number, dates and volume into a free-text email for every gap [farmer-d/logistics/896], then follows up until someone answers [farmer-d/logistics/1160] [farmer-d/logistics/1485]. Expired deals can go unnoticed for months:

> There should be a deal ticket in Sitara for this sale to Engage, but it looks as though 12/99 was the last month a deal was entered
[farmer-d/logistics/1055]

The process runs at about 2.4 hours a month, modelled at $205 per month ($2,460 per year) at $85/hour.

## What the automation produces

A nightly job runs after the daily allocation load, and can also be run on demand before month-end close. It compares allocated daily volumes by meter and contract in Volume Management with active Sitara deals. It uses Unify paths and Feedback Monitor errors where they are available. For each meter-day with flow but no covering deal, it opens **one pre-filled case** with these fields:

- meter, contract, counterparty, flow days and volume
- the last Sitara deal number seen at that meter, and its evergreen flag
- the suggested fix, such as extending a deal or creating a new one for days that are not covered (the partial-month case in [farmer-d/logistics/1149])

The case goes to the owner of the last deal at that meter. If that owner is unknown, it goes to the desk fallback owner.

## Daily routine

1. **Deal owner opens the queue each morning.** For each case, choose **Extend**, **New deal** or **Write-off/PPA**, and enter a reason. Commercial judgement stays with you: decide whether the gas should be flowing at all, and set the price and terms.
2. **Extend / New deal:** make the change in Sitara, then enter the deal number on the case. The requester is notified automatically. This replaces one-off emails like [farmer-d/logistics/1999].
3. **Wrong owner:** reassign the case to the right desk. Do not forward it by email. This avoids the hand-offs seen in [farmer-d/logistics/117].
4. **Volume management / settlements:** check the queue before emailing. Raise a manual case only for gaps the job did not catch, such as a counterparty statement volume like the one in [farmer-d/logistics/2137], and fill in the same fields.
5. **Exceptions that need an approver:** for old or large gaps, attach root cause and end-user billing details before you ask for sign-off [farmer-d/logistics/1356]. Very old periods may not be processable in the systems, so record a PPA/OBA decision on the case [farmer-d/logistics/1489].

## Aging, deadlines and month-end

- Cases still open after the agreed age escalate to the desk lead.
- A month-end report lists open gaps by age and volume for volume management, settlements and the desk lead. The target is zero open meter-days at close.
- Same-day payment deadlines are handled manually. Phone the deal owner and logistics directly:

> Payment MUST be set up by noon 5/24/01 for prompt payment to Spinnaker.
[farmer-d/logistics/130]

## Things a person still checks

- **Volumes that keep changing.** Cases on restated allocations are held until the allocation settles, so nobody reworks the same gap:

> We go round and round at this point changing volumes two, three or more times.
[farmer-d/logistics/1972]

- **Volume disputes with pipelines or counterparties.** These are negotiated outside the systems. Record the outcome on the case.
- **Meters rolled every month.** Once a month, review meters that need a monthly roll and consider moving them to evergreen deals.
