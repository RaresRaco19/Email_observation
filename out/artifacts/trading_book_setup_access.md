---
opportunity: trading_book_setup_access
type: template
citations: [giron-d/sent/769, giron-d/sent/777, giron-d/sent/650, giron-d/inbox/161, giron-d/sent/412, giron-d/inbox/132, giron-d/inbox/155, giron-d/sent/520, giron-d/sent/18, giron-d/sent/526, giron-d/sent/525, giron-d/sent/470]
---

# Book and Access Request Template

**For:** desk leads and regional leads asking for a new Tagg book, a mapping change or user access.
**Send to:** the book administrators (Susan Trevino, Burton McIntyre) [giron-d/sent/525], cc your risk lead. Do not route by word of mouth:

> We need to add a new book in Tagg.  Kam suggested I send the request to you.

[giron-d/sent/769]

**Subject line:** `Book Request - [desk] - [book name]`
**Where it lives:** the shared Netco controls folder, next to the existing Trader-Book template [giron-d/inbox/132].

## Section A: The book (required)

| Field | Your entry | Example from past requests |
|---|---|---|
| Book name(s) | [book name] | FT-ENOVATE, INTRA-ENOVATE [giron-d/sent/650] |
| Counterparty / legal entity the book falls under | [entity] | Enovate, LLC or Enron MW, LLC [giron-d/sent/650] |
| Region and desk | [desk] | West desk [giron-d/sent/525] |
| Risk types | [P / B / I / GD] | P, B, I & GD [giron-d/sent/650] |
| Requested book and portfolio codes | [codes] | [giron-d/sent/470] |
| Fallback if codes are taken | [call me / pick any / alternative] | [giron-d/inbox/161] |
| Code consistency rule across regions | [rule] | see below [giron-d/inbox/161] |
| Date deals must move to the book | [date] | "by the end of next week" [giron-d/sent/650] |
| Approver | [name] | |

> We need all price, basis, index, and gas daily US books to be the same, all Canadian books to be the same and all physical books to have the same codes please.

[giron-d/inbox/161]

## Section B: Mappings (required for a new business unit or desk)

| Field | Your entry |
|---|---|
| Pipes to map to the business unit (or "all pipes from [existing unit]") | [pipes] [giron-d/sent/777] |
| Sitara curve mappings to change (from CurveMappings.xls) | [location, old curve, new curve] [giron-d/inbox/155] |
| EOL products assigned to this book | [products] [giron-d/inbox/132] |

If these fields are missing, the admins have to come back and ask:

> Darron, do you know which pipes these two new business units will be

[giron-d/sent/777]

## Section C: Traders and risk-type routing (required)

| Trader | Price book | Basis book | Index book | Gas daily book |
|---|---|---|---|---|
| [trader] | [book] | [book] | [book] | [book] |

State whether index goes to the trader's own book or to one person who manages index separately [giron-d/inbox/132]. This table is the trader matrix that Tagg IT asks for [giron-d/sent/412].

## Section D: User access (optional, keep short)

| User | Tagg user name | Book Admin list | Calc post ids | Print | Other (PEP reporting line) |
|---|---|---|---|---|---|
| [name] | [user id] | [Y/N] [giron-d/sent/18] | [Y/N] | [Y/N] [giron-d/sent/520] | [change] |

> I can calc postids for FT-NW but cannot print.  Please help.

[giron-d/sent/520]

## Before you send

1. Every book has an entity, a desk and its risk types.
2. Pipes and Sitara curve mappings are listed, or marked "no change".
3. Every risk type is routed to a trader book in Section C.
4. Codes follow the regional consistency rule, and a fallback is stated.
5. Every user who needs the book has calc and print access listed.
6. The required-by date and the approver are filled in.

## For the admins: request log and reply

Log each request with its request number, the codes assigned and the confirmation date. Send the confirmation back to the requester to keep for audit [giron-d/sent/526]. If a request arrives as free text, send this reply:

```
Thanks for the request for [book name]. To set it up without delay,
please resend it on the Book and Access Request template in the Netco
controls folder. Still missing: [fields].
Subject: Book Request - [desk] - [book name]
```

Measure success by the share of requests that are set up with no clarifying email. The value is small (about $45 a month, $540 a year), so this should stay a template and not become a system build.
