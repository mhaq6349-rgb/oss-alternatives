"""Generate the OpenAlt Audits site into docs/audit.

Run after scripts/build.py, which creates docs/.
"""

import html
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "audit"
SRC = ROOT / "audit"

BASE = "https://mhaq6349-rgb.github.io/oss-alternatives/audit"
SITE_NAME = "OpenAlt Audits"

NAV = [
    ("", "Home"),
    ("method", "Method"),
    ("example", "Example"),
    ("pricing", "Pricing"),
    ("faq", "Questions"),
    ("about", "About"),
    ("contact", "Contact"),
]

# vendor, replacement or None, today, after, save, why
LINES = [
    ("Figma Professional", "Penpot", 4320, 1080, 3240,
     "Twenty-four editors at $15. Penpot covers design and prototype handoff, and the files stay on your server."),
    ("Jira Standard", "Plane", 2934, 900, 2034,
     "Thirty users at $8.15. Plane's cycles and modules map onto how the team already works."),
    ("Confluence Standard", "Outline", 2304, 900, 1404,
     "Thirty users at $6.40. Outline is faster and the search actually finds things."),
    ("Slack Pro", None, 3150, 3150, 0,
     "Kept. Every replacement here costs more in lost habits than it saves, and the network effect is real."),
    ("Auth0", "Keycloak", 1800, 600, 1200,
     "Five thousand monthly active users. Keycloak is dull software, which is what you want under login."),
    ("Mixpanel Growth", "PostHog", 3600, 1200, 2400,
     "Event volume is the cost driver. PostHog self-hosted also brings replays, which were being paid for separately."),
    ("1Password Business", None, 2876, 2876, 0,
     "Kept. Security tooling is the last place to optimise on price, and the migration risk is not worth $2,876."),
]

TOTAL_TODAY = sum(l[2] for l in LINES)
TOTAL_AFTER = sum(l[3] for l in LINES)
TOTAL_SAVE = sum(l[4] for l in LINES)


def esc(value):
    return html.escape(str(value), quote=True)


def money(n):
    return f"${n:,.0f}"


def nav_html(root, active):
    out = []
    for slug, label in NAV:
        href = root + (slug + "/" if slug else "") + "index.html"
        current = ' aria-current="page"' if slug == active else ""
        out.append(f'<a href="{href}"{current}>{esc(label)}</a>')
    return "\n      ".join(out)


def layout(slug, title, description, body, depth=1):
    root = "../" * depth
    site_root = "../" * (depth + 1)
    canonical = f"{BASE}/{slug + '/' if slug else ''}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23101a15'/%3E%3Ctext x='16' y='23' font-family='monospace' font-size='20' font-weight='700' fill='%23e9eee3' text-anchor='middle'%3E%24%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,500;12..96,700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>
<script>document.documentElement.classList.add("js");</script>
<a class="skip" href="#main">Skip to content</a>
<div class="grain" aria-hidden="true"></div>

<div class="shell">

  <header class="top">
    <a class="mark" href="{root}index.html">OpenAlt <span>Audits</span></a>
    <nav class="nav" aria-label="Primary">
      {nav_html(root, slug)}
    </nav>
  </header>

  <main id="main">
{body}
  </main>

  <footer>
    <div class="foot-grid">
      <div>
        <h4>{esc(SITE_NAME)}</h4>
        <p style="margin:0">A fixed-fee audit of software spend. Built on the same data as the <a href="{site_root}index.html">open source alternatives directory</a>.</p>
      </div>
      <div>
        <h4>Pages</h4>
        <ul>
          <li><a href="{root}method/index.html">Method</a></li>
          <li><a href="{root}example/index.html">Worked example</a></li>
          <li><a href="{root}pricing/index.html">Pricing</a></li>
          <li><a href="{root}faq/index.html">Questions</a></li>
        </ul>
      </div>
      <div>
        <h4>Elsewhere</h4>
        <ul>
          <li><a href="{root}contact/index.html">Request an audit</a></li>
          <li><a href="https://github.com/mhaq6349-rgb/oss-alternatives">Source on GitHub</a></li>
          <li><a href="{site_root}index.html">Alternatives directory</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <span>&copy; {SITE_NAME}</span>
      <span>Figures are annual and in USD.</span>
    </div>
  </footer>

</div>
<script src="{root}assets/site.js" defer></script>
</body>
</html>
"""


def ledger(expanded=False):
    rows = []
    for vendor, repl, today, after, save, _why in LINES:
        cls = "replace" if save else "keep"
        cost = f"{money(today)} \u2192 {money(after)}" if save else money(today)
        rows.append(
            f'<tr class="{cls}" data-save="{save}">'
            f'<td class="vendor">{esc(vendor)}</td>'
            f'<td class="alt">{esc(repl + ", self-hosted") if repl else "Keep it"}</td>'
            f'<td class="alt">{cost}</td>'
            f'<td class="num">{money(save) if save else "\u2014"}</td>'
            f"</tr>"
        )

    caption = (
        "Worked example: a 30-person company, seven subscriptions, list prices. Annual, USD."
        if not expanded else
        "The full seven lines. Every replacement is priced with the server and maintenance it needs."
    )

    return f"""<table class="lines">
        <caption>{esc(caption)}</caption>
        <thead>
          <tr>
            <th scope="col">Subscription</th>
            <th scope="col">Replace with</th>
            <th scope="col">Annual cost</th>
            <th scope="col" class="num">Saves</th>
          </tr>
        </thead>
        <tbody>
          {"".join(rows)}
        </tbody>
        <tfoot>
          <tr>
            <td>{money(TOTAL_TODAY)} today</td>
            <td>{money(TOTAL_AFTER)} after</td>
            <td>4 of 7 replaced</td>
            <td class="num">{money(TOTAL_SAVE)}</td>
          </tr>
        </tfoot>
      </table>"""


def home():
    body = f"""
    <aside class="rail" aria-label="Running total of savings found">
      <p>Recoverable in the worked example</p>
      <span class="total" id="railTotal">$0</span>
      <p class="note">Counted line by line as you read. Every figure is annual, and every replacement is priced with the server you'll have to run.</p>
    </aside>

    <section class="hero" style="margin-top:0">
      <h1>{money(TOTAL_TODAY)} a year. <em>{money(TOTAL_SAVE)}</em> of it is optional.</h1>
      <p class="lede">That is a 30-person company's stack worked line by line, from real list prices. We read your invoices, price the open source replacement including the server it needs, and tell you which subscriptions to keep paying for.</p>
      <p class="meta">Fixed fee. One week. The spreadsheet is yours either way.</p>
    </section>

    <section class="ledger">
      {ledger()}
      <p class="footnote">The "after" column includes a $900/year hosting and maintenance allowance per replacement, because self-hosting is not free — someone has to patch it. Two subscriptions stayed. That is normal: the honest answer is usually a third of what you pay for is worth keeping.</p>
    </section>

    <section>
      <h2>How the week runs</h2>
      <p class="sub">No discovery workshops. You send a file, you get a document.</p>
      <ol class="steps">
        <li>
          <span class="n">01</span>
          <div>
            <h3>Send the invoice export</h3>
            <p>A CSV or PDF of software charges for the last twelve months. Redact card numbers. We sign an NDA if you need one.</p>
          </div>
        </li>
        <li>
          <span class="n">02</span>
          <div>
            <h3>We price both paths</h3>
            <p>Every line gets a replacement shortlist and a real annual cost: licence, hosting, the hours to migrate, and who maintains it after.</p>
          </div>
        </li>
        <li>
          <span class="n">03</span>
          <div>
            <h3>You get the order of operations</h3>
            <p>Which two to move first, which to leave alone, and the ones that will cost more to run than they save.</p>
          </div>
        </li>
      </ol>
      <p class="meta" style="margin-top:18px"><a href="method/index.html">What each day actually looks like</a></p>
    </section>

    <section>
      <h2>Rough check before you email</h2>
      <p class="sub">Three numbers, approximate is fine. This is the same arithmetic the audit starts with.</p>

      <div class="calc">
        <div class="fields">
          <div class="field">
            <label for="seats">People with a paid seat <output id="seatsOut" for="seats">30</output></label>
            <input type="range" id="seats" min="3" max="500" value="30" step="1">
          </div>
          <div class="field">
            <label for="price">Average cost per seat, per tool, per month <output id="priceOut" for="price">$8</output></label>
            <input type="range" id="price" min="3" max="80" value="8" step="1">
          </div>
          <div class="field">
            <label for="vendors">Separate subscriptions <output id="vendorsOut" for="vendors">7</output></label>
            <input type="range" id="vendors" min="1" max="30" value="7" step="1">
          </div>
        </div>

        <div class="result">
          <div>
            <p class="k">You spend, roughly</p>
            <p class="v" id="spend">$0</p>
          </div>
          <div>
            <p class="k">Usually recoverable</p>
            <p class="v save" id="recover">$0</p>
            <p class="rng" id="rangeText">&nbsp;</p>
          </div>
          <div>
            <p class="k">Against a $900 fee</p>
            <p class="v" id="breakeven">&mdash;</p>
          </div>
        </div>

        <p class="calc-note">These percentages are a rule of thumb, not a benchmark from hundreds of clients: 18% at one to three subscriptions, 28% at four to six, 34% above that, give or take six points. The worked example recovered {round(TOTAL_SAVE / TOTAL_TODAY * 100)}%, which is high. Your real number needs your invoices.</p>
      </div>
    </section>

    <section>
      <h2>What lands in your inbox</h2>
      <p class="sub">Two files and one call. Nothing recurring, nothing to log in to.</p>
      <dl class="deliver">
        <div>
          <dt>Spreadsheet</dt>
          <dd>Every line you pay for, the annual figure, the replacement options, the real post-migration cost, and the net difference.</dd>
        </div>
        <div>
          <dt>Migration order</dt>
          <dd>A two-page PDF sequencing the moves by risk, with the ones we advise against called out plainly.</dd>
        </div>
        <div>
          <dt>One call</dt>
          <dd>Thirty minutes to argue with our numbers. If we got your context wrong, we say so and revise the document.</dd>
        </div>
      </dl>
    </section>

    <section>
      <h2>One audit, fixed fee</h2>
      <div class="offer">
        <div>
          <p class="price">$900<small>Flat. Half refunded if the audit doesn't find three times the fee.</small></p>
        </div>
        <a class="cta" href="contact/index.html">Request an audit</a>
      </div>
    </section>
"""
    return layout("", f"{SITE_NAME} — find the software you don't need to pay for",
                  "A fixed-fee audit of your software spend. We price the open source replacement honestly and tell you which subscriptions to keep.",
                  body, depth=0)


def method():
    body = """
    <section class="hero" style="margin-top:0">
      <h1 class="small">Seven days, and four of them are reading.</h1>
      <p class="lede">An audit is mostly boring work done carefully. Here is the actual schedule, so you can judge whether the fee is fair.</p>
    </section>

    <section class="tight">
      <table class="data">
        <thead>
          <tr><th scope="col">Day</th><th scope="col">What happens</th><th scope="col">What you get</th></tr>
        </thead>
        <tbody>
          <tr><td>0</td><td>You send the export and a sentence about what annoys you. We confirm scope or decline.</td><td>A yes or a no within one business day.</td></tr>
          <tr><td>1</td><td>Normalise the file: deduplicate, catch the tools paid annually, find the ones hiding in a card statement rather than an invoice.</td><td>A cost inventory you probably do not have.</td></tr>
          <tr><td>2</td><td>For each line, find the two or three realistic replacements. Reject the ones that fail on licences, data residency, or missing features.</td><td>A shortlist per line, with rejects written down.</td></tr>
          <tr><td>3</td><td>Price the shortlist properly: hosting, backup, monitoring, and the hours to migrate. Not the licence fee alone.</td><td>The real annual cost of each path.</td></tr>
          <tr><td>4</td><td>Sequencing. Which migration blocks another, which ones break mid-quarter, which need a freeze window.</td><td>An order of operations.</td></tr>
          <tr><td>5</td><td>Write the document. Every recommendation has a number attached and a reason it is safe.</td><td>Spreadsheet and PDF.</td></tr>
          <tr><td>6</td><td>The call. You push back, we revise or defend.</td><td>A document you can act on.</td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>What we need from you</h2>
      <div class="prose">
        <ul>
          <li>A CSV or PDF export of software charges covering twelve months.</li>
          <li>Headcount, and roughly how many people use each tool.</li>
          <li>Anything you know is contractual: annual prepay, minimum terms, procurement rules.</li>
          <li>One person who can answer questions in a few hours, not days.</li>
        </ul>
        <p>That is it. No infrastructure access, no repository, no admin credentials. An audit of spend does not require access to your systems, and asking for it would be a warning sign.</p>
      </div>
    </section>

    <section>
      <h2>What we will not do</h2>
      <div class="prose">
        <p>Worth being explicit, because scope creep in both directions is how these engagements go wrong.</p>
        <ul>
          <li><strong>We do not perform the migration.</strong> The document tells you what to move and in what order. Doing it is a separate project, and often better done by whoever already knows your systems.</li>
          <li><strong>We do not negotiate with vendors.</strong> This is not procurement consultancy and we hold no leverage with your suppliers.</li>
          <li><strong>We do not manage anything afterwards.</strong> There is no retainer, no monitoring, no monthly fee.</li>
          <li><strong>We do not guarantee savings.</strong> If the honest answer is that you are already lean, that is what the document will say, and the guarantee on the pricing page exists because of it.</li>
        </ul>
      </div>
    </section>

    <section>
      <h2>Why self-hosting gets a line item</h2>
      <div class="prose">
        <p>Every "free" replacement in this industry is free the way a puppy is free. Someone patches it, someone restarts it when it falls over, someone gets paged at 2am.</p>
        <p>We put a flat $900 a year per replacement against hosting and upkeep. For a small tool that is generous. For a database it is optimistic. The point is that the number appears in the same column as the subscription it replaces, so the comparison is honest rather than flattering.</p>
        <p>When a replacement cannot beat its subscription once that line is included, it gets marked "keep" and we move on. Roughly a third of what most companies pay for survives that test.</p>
      </div>
    </section>
"""
    return layout("method", "Method — how the audit week runs",
                  "The day-by-day schedule of an OpenAlt audit, what we need from you, and what we refuse to do.",
                  body)


def example():
    reasons = "".join(
        f"""<div>
          <dt>{esc(vendor)}</dt>
          <dd>{esc(why)}</dd>
        </div>"""
        for vendor, repl, _t, _a, _s, why in LINES
    )
    body = f"""
    <aside class="rail" aria-label="Running total of savings found">
      <p>Recoverable across these seven lines</p>
      <span class="total" id="railTotal">$0</span>
      <p class="note">This is the same arithmetic as the home page, expanded. Scroll and the total builds line by line.</p>
    </aside>

    <section class="hero" style="margin-top:0">
      <h1 class="small">One stack, all seven lines, and the reasoning.</h1>
      <p class="lede">A 30-person software company. Not a client — a constructed example using current list prices, so you can check our arithmetic before paying us anything.</p>
      <p class="meta">{money(TOTAL_TODAY)} today, {money(TOTAL_AFTER)} after four replacements, {money(TOTAL_SAVE)} a year.</p>
    </section>

    <section class="ledger">
      {ledger(expanded=True)}
    </section>

    <section>
      <h2>Line by line</h2>
      <p class="sub">The part a spreadsheet alone will not tell you.</p>
      <dl class="deliver">
        {reasons}
      </dl>
    </section>

    <section>
      <h2>What we would do first</h2>
      <div class="prose">
        <p><strong>Confluence first.</strong> Lowest risk of the four: nobody's workflow depends on the wiki's specific software, and Outline imports the content. A week of an intern's time.</p>
        <p><strong>Auth0 second.</strong> Keycloak is the least pleasant migration here, but it sits under everything, so leaving it until later means doing the work twice.</p>
        <p><strong>Figma and Jira last.</strong> Both are habit-heavy. Designers and engineers will resist, and resistance is expensive. Run them in parallel with the team's own champions, not as an IT project.</p>
        <p><strong>Mixpanel whenever the contract renews.</strong> It is the biggest single saving and the least urgent, because event volume only grows.</p>
      </div>
    </section>

    <section>
      <h2>The caveat on all of this</h2>
      <div class="callout">
        <p>This is a modelled example built from list prices, not a rescued client. It shows the method and the arithmetic. Your numbers will differ in both directions, and the audit exists to replace this with your actual invoices.</p>
      </div>
      <div class="prose">
        <p>Two things move the totals most: seat count, and whether you already pay annually. A team of twelve with three tools has very little to recover, and we will say so before taking the fee.</p>
      </div>
    </section>

    <section>
      <h2>Check the prices yourself</h2>
      <div class="prose">
        <p>Every figure above is public list pricing at the time of writing. If you think a number is wrong, check it — and tell us, because a wrong price in a public example is worse for us than for you.</p>
        <p class="meta" style="margin-top:20px"><a href="../index.html">Browse the replacement projects</a> before you decide.</p>
      </div>
    </section>
"""
    return layout("example", "Worked example — seven lines, fully costed",
                  "A complete sample audit for a 30-person company: what to replace, what to keep, and why.",
                  body)


def pricing():
    body = """
    <section class="hero" style="margin-top:0">
      <h1 class="small">$900, and half of it back if we waste your time.</h1>
      <p class="lede">One price for companies up to about 100 seats. No retainer, no percentage, no upsell into a migration project.</p>
    </section>

    <section class="tight">
      <div class="offer">
        <div>
          <p class="price">$900<small>Half refunded if the audit doesn't identify savings of at least $2,700 a year.</small></p>
        </div>
        <a class="cta" href="contact/index.html">Request an audit</a>
      </div>
    </section>

    <section>
      <h2>What the fee covers</h2>
      <dl class="deliver">
        <div><dt>Included</dt><dd>The full cost inventory, replacement shortlists, real post-migration pricing, migration sequence, the document, and the call.</dd></div>
        <div><dt>Not included</dt><dd>Doing the migration, negotiating with vendors, buying licences on your behalf, or managing anything after delivery.</dd></div>
        <div><dt>Turnaround</dt><dd>Seven days from receiving a usable export. If your data arrives messy, we tell you before starting the clock.</dd></div>
        <div><dt>Larger companies</dt><dd>Above roughly 100 seats or 40 subscriptions, the work is materially bigger and we quote separately. Usually $1,800–2,400.</dd></div>
      </dl>
    </section>

    <section>
      <h2>Why not a percentage of savings</h2>
      <div class="prose">
        <p>Because it pays us to recommend bad migrations. A consultant on 20% of savings has a reason to push the riskiest move that shows the biggest number, and no reason to tell you that a replacement will cost more to run than it saves.</p>
        <p>A flat fee makes "keep this one" a neutral sentence. It also means our incentive is to finish quickly rather than to keep the engagement open.</p>
      </div>
    </section>

    <section>
      <h2>The guarantee, honestly</h2>
      <div class="prose">
        <p>If the document does not identify at least $2,700 of annual savings — three times the fee — we refund half. You keep the document either way, including the analysis of why there was nothing to find.</p>
        <p>It is not a full refund because the work was done. Reading twelve months of invoices and pricing replacements takes days whether or not the answer is flattering. A full refund would mean we only get paid when the answer is convenient, which is the incentive we just argued against.</p>
      </div>
      <div class="callout">
        <p>If your stack is under about $15,000 a year, this is probably not worth buying. The maths does not support it and we would rather say so now than take the fee and produce a thin document.</p>
      </div>
    </section>

    <section>
      <h2>Payment and paperwork</h2>
      <div class="prose">
        <p>Invoice on acceptance, payable before delivery. Bank transfer or card. We can sign an NDA and your procurement paperwork, but we are a small operation and cannot complete enterprise vendor-security questionnaires that assume a compliance department.</p>
      </div>
    </section>
"""
    return layout("pricing", "Pricing — $900 flat, half refunded if we find nothing",
                  "One fixed fee for a software spend audit, what it includes, and the refund terms.",
                  body)


def faq():
    qa = [
        ("Who actually does the work?",
         "<p>A small operation. The same person who built the alternatives directory behind this site reads your invoices and writes the document. There is no account manager and no offshore team.</p>"
         "<p>That is a limitation as well as a selling point: we take a handful of audits at a time, and we will tell you when the next slot is rather than pretend otherwise.</p>"),
        ("Do you take a cut of the savings?",
         "<p>No. The fee is flat. A percentage would pay us to recommend the riskiest migration with the biggest headline number, and to stay quiet when a replacement costs more to run than it saves.</p>"),
        ("What if you find nothing worth changing?",
         "<p>You get a document saying so, with the analysis. Half the fee is refunded under the guarantee because we did not clear the three-times threshold. A thin stack is a good problem to have.</p>"),
        ("Is my financial data safe?",
         "<p>You send invoices, not credentials. We ask for card numbers to be redacted, we do not need access to any system, and the working files are deleted after delivery unless you ask us to keep them.</p>"
         "<p>If your policy requires an NDA before sharing anything, say so in the first message and we will send one back.</p>"),
        ("Do you do the migration?",
         "<p>No. The document tells you what to move and in what order. Most migrations are better done by the people who already know the systems, and we would be learning your infrastructure at your expense.</p>"),
        ("What about licences like AGPL?",
         "<p>They matter, and they are part of the shortlist. Some projects carry modified licences — several of the tools in our directory are marked \"custom licence\" because GitHub cannot identify them. If a licence creates an obligation your business cannot accept, the option is rejected and we say why.</p>"),
        ("Why do you count hosting as a cost?",
         "<p>Because someone has to run it. A flat $900 a year per replacement covers a server, backups and the hours to patch it. For a database that number is optimistic, and the document says when it is.</p>"),
        ("Can you audit just one tool?",
         "<p>No, and it would not be worth $900. The value is in seeing the whole stack at once: the replacement for one line is sometimes the tool you already pay for on another.</p>"),
        ("We are on annual contracts. Does that matter?",
         "<p>It changes the sequencing, not the analysis. You get a plan keyed to your renewal dates so you can give notice in time, rather than discovering the deadline after it passed.</p>"),
        ("How do I start?",
         "<p>Send a short message with your headcount, approximate annual software spend, and what you suspect is wasteful. If it looks like a fit we send a scope question and an invoice. If it does not, we say so.</p>"),
    ]

    items = "".join(
        f"""<details>
          <summary>{esc(q)}</summary>
          <div class="answer">{a}</div>
        </details>"""
        for q, a in qa
    )

    body = f"""
    <section class="hero" style="margin-top:0">
      <h1 class="small">The questions worth asking before you pay anyone.</h1>
      <p class="lede">Including the ones that make us look worse.</p>
    </section>

    <section class="tight">
      {items}
    </section>

    <section>
      <h2>Still deciding?</h2>
      <p class="sub">Read the worked example first. It shows exactly what the deliverable looks like, with real arithmetic you can check.</p>
      <p class="meta"><a href="example/index.html">See the full worked example</a></p>
    </section>
"""
    return layout("faq", "Questions — OpenAlt Audits",
                  "Who runs the audit, what happens when there is nothing to save, how your data is handled, and why the fee is flat.",
                  body)


def about():
    body = """
    <section class="hero" style="margin-top:0">
      <h1 class="small">A small operation with a public dataset.</h1>
      <p class="lede">No team page, no stock photography, no claimed client logos. Here is what actually exists behind this site.</p>
    </section>

    <section class="tight">
      <div class="prose">
        <p>This audit service grew out of an <a href="../index.html">open source alternatives directory</a>: 49 commercial products mapped to 101 open source projects, with stars, licences and languages pulled from the GitHub API at build time.</p>
        <p>The directory answers "what could replace this". The audit answers the harder question: "what should we replace, in what order, and what does it actually cost once someone has to run it".</p>
        <p>The second question needs your invoices, which is why it is a paid engagement and not a website.</p>
      </div>
    </section>

    <section>
      <h2>What we are good at</h2>
      <div class="prose">
        <ul>
          <li>Reading a software bill and spotting the lines nobody has questioned in three years.</li>
          <li>Knowing which open source projects are actually maintained, and which are abandoned repositories with a nice README.</li>
          <li>Pricing the unglamorous parts: hosting, backups, patching, and the hours to migrate.</li>
          <li>Saying "keep that one" when it is the right answer.</li>
        </ul>
      </div>
    </section>

    <section>
      <h2>What we are not</h2>
      <div class="prose">
        <ul>
          <li><strong>Not a migration shop.</strong> We do not implement.</li>
          <li><strong>Not procurement.</strong> No vendor relationships, no negotiating leverage.</li>
          <li><strong>Not a compliance vendor.</strong> If you need SOC 2 paperwork and a security questionnaire, this is the wrong supplier.</li>
          <li><strong>Not a research firm.</strong> The percentages on the calculator are a rule of thumb, not a benchmark from hundreds of clients. We would rather say that than invent a sample size.</li>
        </ul>
      </div>
    </section>

    <section>
      <h2>Why the site looks like a ledger</h2>
      <div class="prose">
        <p>Because the deliverable is a ledger. The page you are reading is the same document structure you get: lines, annual figures, a replacement, and a subtraction. Designing it as anything else would be dishonest about what the work is.</p>
        <p>The green bar behind the text is the paper accounting software replaced. It seemed more appropriate than another dark-mode dashboard.</p>
      </div>
    </section>
"""
    return layout("about", "About — OpenAlt Audits",
                  "Who runs this, what we are good at, what we refuse to do, and why the site looks like an accounting ledger.",
                  body)


def contact():
    body = """
    <section class="hero" style="margin-top:0">
      <h1 class="small">Tell us three things and we will tell you if this is worth $900.</h1>
      <p class="lede">No form, no calendar widget. One message, one honest reply within a business day.</p>
    </section>

    <section class="tight">
      <div class="offer">
        <div>
          <p class="price">$900<small>Fixed. Half refunded if we cannot find three times the fee.</small></p>
        </div>
        <a class="cta" href="https://github.com/mhaq6349-rgb/oss-alternatives/issues/new?title=Audit%20request&body=Headcount%3A%0AApproximate%20annual%20software%20spend%3A%0AWhat%20you%20suspect%20is%20wasteful%3A%0AAnything%20contractual%20we%20should%20know%3A">Open a request</a>
      </div>
      <p class="fineprint">Requests open an issue on the public repository, which is an odd place for a commercial conversation but works without a mail server or a form backend. Do not put financial details in it — that is what the reply is for.</p>
    </section>

    <section>
      <h2>What to include</h2>
      <div class="prose">
        <ol>
          <li><strong>Headcount</strong> and roughly how many people have a paid seat per tool.</li>
          <li><strong>Approximate annual software spend</strong>, a rounded number is fine.</li>
          <li><strong>What you suspect is wasteful</strong> — the tool everyone complains about, the one nobody remembers buying.</li>
          <li><strong>Anything contractual</strong>: annual prepay, renewal dates, procurement rules.</li>
        </ol>
        <p>Four lines is enough. If it looks like a fit we reply with one scope question and an invoice. If it does not, we say so and tell you why.</p>
      </div>
    </section>

    <section>
      <h2>What not to send</h2>
      <div class="prose">
        <ul>
          <li>Card numbers, bank details, or anything that would make a breach your problem.</li>
          <li>System access of any kind. We never need it, and a supplier who asks is worth declining.</li>
          <li>Your full invoice export before an agreement. Three numbers is enough to start.</li>
        </ul>
      </div>
    </section>

    <section>
      <h2>Response times</h2>
      <div class="prose">
        <p>One business day for a first reply. Seven days from a usable export to a delivered document. If the queue is longer than that we say so before you pay, not after.</p>
        <p class="meta" style="margin-top:22px">Prefer to read more first? The <a href="example/index.html">worked example</a> shows the whole deliverable, and <a href="faq/index.html">the questions page</a> covers the awkward parts.</p>
      </div>
    </section>
"""
    return layout("contact", "Contact — request an audit",
                  "What to send to request a software spend audit, what not to send, and how quickly we reply.",
                  body)


PAGES = [
    ("", home),
    ("method", method),
    ("example", example),
    ("pricing", pricing),
    ("faq", faq),
    ("about", about),
    ("contact", contact),
]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for slug, builder in PAGES:
        path = OUT / slug / "index.html" if slug else OUT / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(builder(), encoding="utf-8")

    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copyfile(SRC / "assets" / name, assets / name)

    print(f"audit pages: {len(PAGES)}")
    print(f"output:      {OUT}")


if __name__ == "__main__":
    main()
