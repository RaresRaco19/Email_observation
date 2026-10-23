---
opportunity: deal_book_transfer_correction
type: email
citations: [giron-d/inbox/84, giron-d/inbox/67, giron-d/inbox/103, giron-d/sent/539, giron-d/sent/246, giron-d/sent/405]
---

**To:** Darron Giron, book controller
**Cc:** Jeffrey Gossett; Cecilia Cheung (Estate database); book administrators
**Subject:** Proposal: a structured book-move request and lookup for deal and counterparty transfers

Darron,

I propose we replace the emailed lists of deals to flip or move between books with one structured request and a lookup job. It would start small.

**The problem.** Invoicing, credit and middle office send deal lists, terminated-counterparty lists and spreadsheets to move deals between books, including the bankruptcy books. We saw 70 messages across 57 threads. Half of the 35 flagged messages stalled, and the median gap was 9.5 hours. Three things cause the delays:

- Deadlines leave no slack. Credit wrote:

> We need to have it done by the time we calc our books today - no exceptions.

[giron-d/inbox/84]

- The operator has to ask for details the request never contained (CP IDs, commodity code, cutoff date):

> If I can have all the answers soon then I think the deals move can be completed around 3:00p.m.

[giron-d/inbox/67]

- Lists do not match live deal numbers:

> Please note that there are still several deals that I am trying to reconcile back to Sitara numbers.

[giron-d/inbox/103]

Requests also reach the wrong person first. Stacey Vallejo's invoicing requests had to be forwarded to whoever owns the book [giron-d/sent/405]. Invoicing was held back until the ECC deals were flipped [giron-d/sent/539], and customers waited on confirmation [giron-d/sent/246].

**The fix.**
1. A request form with required fields: deal numbers or counterparty short names/CP IDs, source and target book, financial or physical, active-deal cutoff date, deadline.
2. A lookup job that finds the live deals in Sitara and TAGG. It applies the saved rules (ECC deals with counterparties other than RISKMANTRA go to FT-US/CAND-ERMS; terminated counterparties go to the bankruptcy books). It produces a proposed move file and an exceptions list.
3. A book ownership table that routes each request to its controller, so nothing is forwarded by hand.
4. A before-and-after confirmation email to the requester after the move, and a scheduled sweep of US books for ECC deals before monthly invoicing starts.

**What stays manual.** Credit and legal still decide which counterparties are terminated. The book administrator reviews the move file and runs the move in Sitara or the Estate database. You resolve the exceptions. New books, subregion and curve mapping changes stay as controller requests.

**Value, stated plainly.** At 3.49 messages a month, 20 minutes of median handling and 60% automatable, this saves about 0.7 hours a month. That is $59 a month ($708 a year) at $85/h. Volume comes in bursts, such as the January 2002 bankruptcy moves, so a full integration may not pay back. I suggest phase one only: the form, the ownership table and a read-only lookup. Then measure median time from request to confirmed move and the number of clarifying emails per request.

**Open check.** The emails do not show whether Sitara, TAGG and the Estate database can be queried or exported. Please confirm access with IT before we build.

Can you approve a one-month pilot on a single region's books?

Thanks,
[Name]
