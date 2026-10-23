---
opportunity: sitara_deal_ticket_change_request
type: template
citations: [farmer-d/logistics/5, farmer-d/logistics/789, farmer-d/logistics/59, farmer-d/logistics/765, farmer-d/logistics/1082, farmer-d/logistics/1299]
---

# Sitara Deal Request (send to the logistics desk)

Use this for every request to create or change a Sitara deal ticket. Requests in this form can be entered without a clarification round. The desk answers each one with the confirmation below. Value is modest (about $65 per month, $780 per year at $85 per hour), so this is an email template only, with no system build.

**Subject line:** `SITARA REQ: <action> <counterparty>`

## Fields to fill in

| Field | Your entry |
|---|---|
| Action (create / change price / change volume / zero out / cut off / path) | [action] |
| Existing Sitara deal number(s), if any | [deal numbers] |
| Counterparty | [counterparty] |
| Meter and pipe | [meter] / [pipe] |
| Start and end dates | [start] to [end] |
| Daily volume | [volume, MMBtu/d] |
| Price or index formula | [price or formula] |
| Book | [book] |
| Contract in place (Y/N) | [Y/N] |
| Close month needed by | [date] |
| Reason for the change | [reason] |
| Your name and phone extension | [name, ext.] |

Requests that already follow this pattern, such as the Doehrman #1 ticket (counterparty, meter, volume, price) [farmer-d/logistics/765], only need the book, contract status and deadline added.

## Guidance for requesters

1. **Zero out, do not kill, when paths exist.** Unify support has asked for this:

> If a deal is killed it poses a problem for us in Unify if there are any paths associated with the deal; therefore, we request the deals be zeroed out.

[farmer-d/logistics/5]

2. **Phoned-in or EOL changes must be confirmed by email in this template.** An after-hours EOL volume change was never passed to the desk [farmer-d/logistics/1299].
3. **Multi-party deals** (for example a storage purchase) need one template per desk, and each desk enters on the same day [farmer-d/logistics/1082].
4. State the close month. Without it the desk cannot tell what must be in before close.

## Desk confirmation reply (use when the request is complete)

```
Subject: RE: SITARA REQ: [action] [counterparty]
Sitara deal number(s) [created / changed]: [deal numbers]
Entered as: [fields as entered]
Date entered: [date]
Position Manager checked: [Y/N]   Pathing checked: [Y/N]
Reason on file: [reason]
```

Requesters have asked for exactly this:

> Please supply the sitara number once entered.

[farmer-d/logistics/789]

## Desk reply when fields are missing

```
Thanks. I cannot enter this yet. Please resend using the Sitara Deal
Request template with these fields: [missing fields]. I will enter it
as soon as it arrives, for the [close month] close.
```

## Month-start checklist (logistics desk, Pat Clynes reviews)

1. List unpathed deals by pipe.
2. Confirm which scheduler owns each pipe, and assign any pipe with no owner.
3. List open template requests that have a close-month deadline.
4. Send a confirmation reply for anything entered, so requesters do not have to chase with notes like this one:

> Have you had a chance to look at this yet?

[farmer-d/logistics/59]

## Stays manual

The desk still keys and edits tickets in Sitara and judges pricing and contract coverage. A scheduler decides whether a deal is zeroed or killed when Unify paths exist.
