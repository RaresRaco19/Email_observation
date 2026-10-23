---
opportunity: sitara_deal_ticket_change_request
type: template
citations: [farmer-d/logistics/789, farmer-d/logistics/5, farmer-d/logistics/965, farmer-d/logistics/59, farmer-d/logistics/765, farmer-d/logistics/1082, farmer-d/logistics/1299]
---

# Sitara Deal Request Template

Use this for every request to the logistics desk to create, change, zero out, cut off or reprice a Sitara deal. Send one deal per email. Subject line: `SITARA REQUEST - [type] - [counterparty] - [deal number or "new"]`.

## Why
Requests arrive as loose text or a one-line ask, and the desk then has to ask back or get chased. Requesters want the number back:

> Please supply the sitara number once entered.

[farmer-d/logistics/789]

Others end up chasing with:

> Have you had a chance to look at this yet?

[farmer-d/logistics/59]

Filling in every field below lets the desk enter the deal and confirm it in one pass. Value is small ($58 per month, $696 per year), so keep this a simple email form.

## Request form (copy into a new email to the logistics desk)

1. Request type (pick one): New deal / Change volume / Change price / Zero out / Cut off going forward
2. Existing Sitara deal number (required for every type except New): [deal number]
3. Counterparty: [counterparty]
4. Meter: [meter number]
5. Start date and end date (effective date of the change): [start] to [end]
6. Volume: [volume, for example MMBtu/d] and term (for example one-month baseload firm)
7. Price or pricing formula: [fixed price or formula, for example Gas Daily less an adjustment]
8. Book: [for example Storage Book]
9. Linked entries that must go in the same day: [for example matching purchase and sale, and who enters the other side] (see [farmer-d/logistics/1082])
10. Reason for the change: [one line; required for zero out and cut off]
11. Requester name and extension: [name, ext.]
12. Anyone to copy on the confirmation (volume management for volume or path changes): [names]

Example of a complete new-deal ask, as sent by producer services:

> Please create a one month baseload firm deal ticket for the remaining days of the month based on the following information:

[farmer-d/logistics/765]

## Rule to follow when ending a deal
Do not ask for a deal to be killed if paths exist. Ask for a zero out, and put the reason in field 10:

> If a deal is killed it poses a problem for us in Unify if there are any paths associated with the deal; therefore, we request the deals be zeroed out.

[farmer-d/logistics/5]

For a cut-off, state the deal number, effective date and reason yourself instead of forwarding someone else's note, as in:

> Can you cut off deal 47472 going forward?

[farmer-d/logistics/965]

## EOL deals
If you change an EOL deal (for example volume), email the desk the same day with the deal number. A change made after hours that never reached the desk led to an escalation. [farmer-d/logistics/1299]

## Desk replies

Confirmation (use when the form is complete):
"[Requester], done. Sitara deal [new or changed deal number], [counterparty], meter [meter], [start] to [end], [volume] at [price]. Change made: [what changed]. Effective [date]. Copying volume management: [names, or none]."

Incomplete request (one line, no back-and-forth):
"Please resend using the Sitara deal request form; missing: [field names]. I will enter it once I have them."

## What stays manual
The desk still enters and changes the ticket in Sitara and decides whether an old or unclear deal should be changed at all. Ownership of unpathed pipes at month start is the supervisor's call.
