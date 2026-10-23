---
opportunity: meter_volume_allocation_variance
type: email
citations: [farmer-d/logistics/622, farmer-d/logistics/925, farmer-d/logistics/2089, farmer-d/logistics/1185]
---

**To:** Volume Management Lead (process owner)
**Cc:** Logistics desk, Settlements
**Subject:** Proposal: one daily meter variance list instead of meter-by-meter emails

Hello,

I am proposing a daily meter variance check, to replace the email threads we use today to find and chase allocation exceptions.

**The problem.** Analysts find meter exceptions one at a time, then email the logistics desk to ask whether a deal exists. Stella Morris wrote:

> Daren is there a deal in CPR which may not have fed over to OSS?

[farmer-d/logistics/622]

Feed failures go unseen until someone reviews imbalances:

> POPS has fed 0 volumes back to Sitara on some of the HPLC deals.

[farmer-d/logistics/925]

Sometimes an outside party finds the gap first:

> I am getting several phone calls from Alpine Resources demanding to be paid for meter 5892 and there is nothing there to be paid.

[farmer-d/logistics/2089]

Open items also build into standing lists, such as the interdesk/interconnect report [farmer-d/logistics/1185]. In the sampled threads, 52 messages were flagged as stalled. The median gap was 18.0 hours and the longest was 588.7 hours.

**The fix.** After the POPS allocation run and the POPS-to-Sitara feed, a daily job compares three sources for each meter and gas day: MIPs measurement, POPS confirmed noms and allocations, and Sitara deals (with OSS and CPR for older months). It flags:
- flow with no valid deal
- a confirmation outside the deal's term
- zero POPS-to-Sitara volumes
- delivery noms on receipt meters
- confirmed volume that does not match allocated actuals
- a growing UA4 balance

Each exception goes on one shared list with the meter, month, volumes from each source, the prior month and the rule that fired. It is routed to the logistics desk (missing or invalid deals), the scheduler (nomination issues) or volume management (feed and allocation problems). Owners record a disposition on the item instead of starting a thread. An aging digest flags items left open, which replaces follow-up emails. A same-day alert covers zero-volume feeds.

**What stays with people.** Deciding which volume is correct, creating or changing deals, buybacks, reallocations and POPS changes, counterparty disputes, and setting tolerances.

**Computed value.** The count is 3.98 messages a month. At 20 minutes median handling and 60% automatable, that is 0.8 hours a month. At $85 per hour, that is $68 a month, or $816 a year. This is a small saving. The larger case is the P&L exposure when feed failures sit undetected in UA4, and the evidence does not price that. I suggest we validate it separately.

**Risks.** We have not confirmed that POPS, Sitara, OSS, CPR or MIPs can be read daily. Measurement is often restated late, so early items would be marked provisional. Tolerances set too tight would swamp analysts with noise.

**Ask.** Please approve a first step: confirm read-only access to the five systems and agree the first three rules (no valid deal, out-of-term confirmation, zero feed). Then we run one month in shadow beside the current interdesk/interconnect and feedback error reports before going live.

We would measure success by the median days from a variance first appearing to its disposition, the monthly count of research emails to the logistics desk, and the zero-feed days caught within 24 hours.

Thank you,
[Sender name]
