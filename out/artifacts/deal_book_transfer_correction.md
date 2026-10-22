---
opportunity: deal_book_transfer_correction
type: template
citations: [giron-d/sent/405, giron-d/sent/539, giron-d/sent/550, giron-d/sent/665, giron-d/sent/117, giron-d/sent/83, giron-d/inbox/67, giron-d/inbox/84, giron-d/inbox/103, giron-d/inbox/138, giron-d/inbox/57]
---

# Book Move / Booking Correction Request

**Who uses it:** settlements, credit, risk and accounting staff who need a deal moved to another book, or a price, rate, counterparty or book fixed on a booked deal. **Send to:** the controller listed for the book on the book-owner routing list, not a general contact. Requests that go to the wrong person get forwarded, and that costs time before a same-day deadline [giron-d/sent/550] [giron-d/sent/405].

Why this form exists:

> Invoicing for November should start today, and both ECC and ENA are held back from invoicing until these deals are fixed
[giron-d/sent/539]

> If I can have all the answers soon then I think the deals move can be completed around 3:00p.m.
[giron-d/inbox/67]

## Part A: Request (copy into the email body)

**Subject:** Book move / correction – [book name] – needed by [date, time]

- **Requester and extension:** [name, x-number]
- **Required by:** [date and time], because of [invoicing start / book calc / Nymex close] [giron-d/inbox/84]
- **Reason:** [ECC counterparty in US book / bankruptcy termination / invoice price mismatch / wrong counterparty]

| Deal # (Sitara, EnronOnline or TAGG ID) | TAGG short name | Current book | Action: move to book, or field (price / rate / counterparty / book) and new value | Production month | Physical or financial |
|---|---|---|---|---|---|
| [Q24809.1] | [SHORTNAME] | [MGMT-WEST] | [Move to FT-US/CAND-ERMS] | [n/a] | [Financial] |
| [27253] | [SHORTNAME] | [book] | [Price → new price] | [03/01] | [Physical] |

Use the Sitara number whenever you have it. Lists without Sitara numbers have to be reconciled before anyone can work on them [giron-d/inbox/103]. When you change a price, say which document shows the correct one (for example the customer invoice) [giron-d/sent/83]. When you change a counterparty, give the full legal name and the short name [giron-d/sent/117]. For valuations, attach the deal terms and not just the deal list [giron-d/sent/665].

## Part B: Bulk-move addendum (bankruptcy or whole-book moves)

Fill this in up front. These are the questions the Estate database executor had to send back [giron-d/inbox/67]:

- **Source book name and CP ID:** [NG-PRICE, 11360]
- **Target book name and CP ID:** [bankruptcy book, ID]
- **Commodity code:** [NG / NGGJ]
- **Active-deal cutoff date:** [e.g. instr_end_dt > 1-jan-2002]
- **Other-side counterparty ID:** [ENA CP ID 1305?]
- **Deal types:** [financial only / physical and financial]
- **Is this a late batch of an earlier list?** [yes: give the date of the original list] [giron-d/inbox/57]

## Part C: Completion confirmation (book administrator replies)

```
Subject: DONE – [original subject]
Completed [date, time]. Action taken: [moved to / changed field to] for the
deals below. [Paste the deal table.] Exceptions: [none / deals not found].
Settlements can release invoicing. Logged in the correction log.
```

Record every completed request in the shared correction log with the deal, change, reason and date. GL differences that come back later as possible write-offs can then be traced to the change that caused them [giron-d/inbox/138].

## Handling rules for the book administrator

1. If a free-form request arrives, reply once with this template. Act on it as-is only when it has a same-day invoicing or calc deadline.
2. Deciding whether a deal belongs in another book (ECC vs ENA, bankruptcy eligibility), making the change in Sitara, TAGG or the Estate database, and checking the result after the book calc are still done by hand.
3. Review the template and the routing list after one month.

Estimated value: about $82 a month ($984 a year) in handling time, plus fewer invoicing holds, which are not priced here.
