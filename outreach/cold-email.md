# Outreach

Copy for selling the audit. Read the whole file before sending anything.

## Who to write to

Twenty to a hundred seats. Below twenty the stack is too small for the fee to make sense, and above a hundred it is a different sale with procurement in the way.

Companies that show at least three of these:

- Job posts naming the tools ("experience with Figma, Jira, Confluence").
- A public stack page, or a `builtwith`-style profile showing eight or more paid products.
- Recent funding or a hiring spike, because renewals get reviewed around then.

Best single signal: a finance or operations hire in the last ninety days. Someone new has just been handed the software bill and has no attachment to any of it.

## Before you send anything

These are not optional. Skipping them means the copy never gets read.

1. Send from a separate domain, not your main one. Warm it for three to four weeks first.
2. SPF, DKIM and DMARC set up. Verify the list immediately before upload and keep bounces under two percent.
3. Turn off open and click tracking. It damages deliverability and the numbers are unreliable.
4. Every email needs a plain-text opt-out line and a physical postal address at the bottom. That is law in the US and the UK, not a courtesy.
5. Ten to twenty sends per day per mailbox for the first two weeks.

## The one thing that makes this work

You have no clients, so you cannot claim results. What you do have is a public worked example with real list prices that anyone can check, and a directory of 101 projects with live GitHub data.

Lead with those. "Here is the arithmetic, verify it yourself" is a stronger opening than an invented case study, and it survives the obvious question: who else have you done this for.

## Email 1, day 0

Subject: `software renewals`

> Hi {first},
>
> Saw {company} is hiring a {role}. Teams at that stage usually end up with {tool} for docs, {tool} for issues and {tool} for design, and the total lands somewhere between eight and fifteen dollars per seat per tool per month once everyone with a login is counted.
>
> I put a public worked example together for a thirty person company. Seven subscriptions, four of them replaceable, roughly half the bill gone. Every figure is list price, so you can check the arithmetic before deciding whether I am worth talking to.
>
> https://mhaq6349-rgb.github.io/oss-alternatives/audit/example/
>
> If it is useful, send me three numbers: headcount, rough annual software spend, and the tool people complain about most. I will tell you whether an audit is worth $900 or a waste of your money.
>
> {name}

## Email 2, day 4

Different angle. Do not mention the first email.

Subject: `the ones to keep`

> Hi {first},
>
> Most advice about software spend assumes every subscription is waste. In the example I published, two of seven stayed, including the password manager. Security tooling is the last place to cut, and Slack is expensive to leave because the switching cost is mostly habit, not software.
>
> Knowing which is which is the actual work. If a supplier ever quotes you a percentage of savings, ask what happens when the honest answer is to change nothing. A flat fee makes that answer free to give.
>
> Same example if you want to check the reasoning: https://mhaq6349-rgb.github.io/oss-alternatives/audit/example/
>
> {name}

## Email 3, day 10

Give something away. No ask at all.

Subject: `replacement list`

> Hi {first},
>
> No pitch in this one. I maintain a directory of open source replacements, forty nine commercial products mapped to a hundred and one projects with stars, licences and activity pulled from GitHub. It is free and it stays free.
>
> https://mhaq6349-rgb.github.io/oss-alternatives/
>
> If you ever want the paid version, the audit is on the same site. If not, the directory should still save you an afternoon.
>
> {name}

## Email 4, day 18

The breakup. Send it and honour it.

Subject: `closing this out`

> Hi {first},
>
> I will stop here so I am not another unread sender in your inbox.
>
> If software renewals come up later, everything is public: the audit is at https://mhaq6349-rgb.github.io/oss-alternatives/audit/ and the directory is at https://mhaq6349-rgb.github.io/oss-alternatives/
>
> {name}

## LinkedIn

Connection note, under 300 characters:

> Hi {first}, I map paid software to open source replacements and publish the arithmetic. Thought it might be relevant to what {company} is building. Happy to connect either way.

Message after they accept, one only:

> Thanks for connecting. If a renewal ever needs a second opinion, I do a fixed fee audit and publish the method so you can judge it first. Either way, the directory is free: https://mhaq6349-rgb.github.io/oss-alternatives/

Do not follow up a second time on LinkedIn if they do not reply. One message, then leave it.

## Replies

**"Too expensive."**
> Fair. If your stack is under about $15,000 a year the maths does not work and I say so on the pricing page. If it is above that, the fee is covered by one replacement, and half comes back if I cannot find three times it.

**"We already use open source."**
> Then the audit is probably wasted money. The teams that get value are usually the ones paying for eight or ten tools where two or three have quietly become load bearing.

**"Send me some information."**
> Two links, no attachment: the worked example and the pricing page. If you send headcount, rough spend and the tool people complain about, I will tell you straight whether it is worth $900.

**"Can you just tell me what to replace?"**
> Not usefully without the invoices. The replacement for one line is sometimes the tool you already pay for on another, and that only shows up in the whole stack.

## What to fix first

The site currently sends requests to a public GitHub issue. That is a real channel but a bad one for a business conversation, and anyone can read the thread. Set `CONTACT_EMAIL` in `scripts/build_audit.py` to a real address, rebuild, and every button on the site switches to email.

Also worth doing before the first send: a domain that is not `github.io`. Cold email linking to a `github.io` subdomain reads as a hobby project, which undercuts a $900 fee.
