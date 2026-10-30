"""Render the static site from data/tools.json + data/repos.json.

No framework, no runtime dependencies. Writes into site/.
"""

import html
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs"

SPEC = json.loads((DATA / "tools.json").read_text(encoding="utf-8"))
REPOS = json.loads((DATA / "repos.json").read_text(encoding="utf-8"))
SITE = SPEC["site"]


def esc(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def stars(n):
    n = n or 0
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def license_name(repo):
    lic = REPOS.get(repo, {}).get("license") or {}
    spdx = lic.get("spdx_id")
    if not spdx:
        return "unknown"
    if spdx == "NOASSERTION":
        return "custom licence"
    return spdx


def repo_url(name):
    return "projects/" + name + "/index.html"


def tool_url(slug):
    return "alternatives/" + slug + "/index.html"


def category_url(cat):
    return "category/" + slugify(cat) + "/index.html"


def up(depth):
    return "../" * depth


def page(title, description, body, depth, canonical):
    root = up(depth)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(SITE['base_url'] + '/' + canonical)}">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="bar">
  <a class="brand" href="{root}index.html">{esc(SITE['name'])}</a>
  <span class="tagline">{esc(SITE['tagline'])}</span>
</header>
<main>
{body}
</main>
<footer>
  <p>Data from the GitHub API, refreshed at build time. No affiliation with the products listed.</p>
</footer>
</body>
</html>
"""


def card(repo, why, depth):
    meta = REPOS.get(repo, {})
    name = repo.split("/")[1]
    facts = [f"{stars(meta.get('stargazers_count'))} stars", meta.get("language") or "—", license_name(repo)]
    return f"""<article class="card">
  <h3><a href="{up(depth)}{repo_url(repo)}">{esc(name)}</a></h3>
  <p class="why">{esc(why)}</p>
  <p class="facts">{" · ".join(esc(f) for f in facts)}</p>
  <p class="desc">{esc(meta.get("description") or "")}</p>
</article>"""


def table(rows):
    head = "<tr><th>Project</th><th>Stars</th><th>Language</th><th>License</th></tr>"
    body = []
    for repo, why in rows:
        meta = REPOS.get(repo, {})
        body.append(
            f'<tr><td><a href="{esc(repo_url(repo))}">{esc(repo)}</a></td>'
            f"<td>{stars(meta.get('stargazers_count'))}</td>"
            f"<td>{esc(meta.get('language') or '—')}</td>"
            f"<td>{esc(license_name(repo))}</td></tr>"
        )
    return f'<table class="cmp">{head}{"".join(body)}</table>'


def build_home(tools):
    cats = {}
    for t in tools:
        cats.setdefault(t["category"], []).append(t)

    blocks = []
    for cat, items in sorted(cats.items()):
        links = "".join(
            f'<li><a href="{tool_url(t["slug"])}">{esc(t["name"])}</a>'
            f'<span class="small">{len(t["alternatives"])} alternatives</span></li>'
            for t in sorted(items, key=lambda x: x["name"])
        )
        blocks.append(
            f'<section class="cat"><h2><a href="{category_url(cat)}">{esc(cat)}</a></h2>'
            f'<ul class="plain">{links}</ul></section>'
        )

    total_repos = len({a["repo"] for t in tools for a in t["alternatives"]})
    hero = f"""<section class="hero">
  <h1>Open source alternatives to the tools you already pay for</h1>
  <p>{len(tools)} products, {total_repos} open source projects, ranked by what actually fits.</p>
</section>"""
    return page(
        f"{SITE['name']} — open source alternatives",
        "Honest, data-backed open source alternatives to Notion, Linear, Slack, Figma and more.",
        hero + "".join(blocks),
        0,
        "index.html",
    )


def build_tool(tool):
    alts = sorted(tool["alternatives"], key=lambda a: -(REPOS.get(a["repo"], {}).get("stargazers_count") or 0))
    cards = "".join(card(a["repo"], a["why"], 2) for a in alts)
    body = f"""<nav class="crumbs"><a href="../../index.html">Home</a> / <a href="../../{category_url(tool['category'])}">{esc(tool['category'])}</a></nav>
<h1>Open source alternatives to {esc(tool['name'])}</h1>
<p class="lede">{esc(tool['summary'])} If the subscription is the problem, these do the same job and you keep the data.</p>
<section class="cards">{cards}</section>
<h2>At a glance</h2>
{table([(a["repo"], a["why"]) for a in alts])}
<p class="note">Star counts come from GitHub and move daily. A high count means attention, not fitness — read the notes above before picking. Licences marked "custom licence" use modified terms GitHub cannot identify; check the repository before assuming standard AGPL or MIT rights.</p>"""
    return page(
        f"Open source alternatives to {tool['name']}",
        f"{len(alts)} open source alternatives to {tool['name']}, with stars, licenses and what each one is actually good at.",
        body,
        2,
        f"alternatives/{tool['slug']}/index.html",
    )


def build_project(repo, tool_names):
    meta = REPOS.get(repo, {})
    replaces = ", ".join(
        f'<a href="../../../{tool_url(slug)}">{esc(name)}</a>' for slug, name in tool_names
    )
    body = f"""<nav class="crumbs"><a href="../../../index.html">Home</a> / Project</nav>
<h1>{esc(repo.split('/')[1])}</h1>
<p class="lede">{esc(meta.get('description') or '')}</p>
<ul class="meta">
  <li><strong>Repository</strong> <a href="{esc(meta.get('html_url') or '#')}">{esc(repo)}</a></li>
  <li><strong>Stars</strong> {stars(meta.get('stargazers_count'))}</li>
  <li><strong>Language</strong> {esc(meta.get('language') or '—')}</li>
  <li><strong>License</strong> {esc(license_name(repo))}</li>
  <li><strong>Open issues</strong> {meta.get('open_issues_count') or 0}</li>
  <li><strong>Replaces</strong> {replaces}</li>
</ul>
<p class="note">Metadata last read from the GitHub API at build time.</p>"""
    return page(
        f"{repo} — open source alternative",
        (meta.get("description") or repo) + ". Stars, license and activity.",
        body,
        3,
        f"projects/{repo}/index.html",
    )


def build_category(cat, tools):
    links = "".join(
        f'<li><a href="../../{tool_url(t["slug"])}">{esc(t["name"])}</a>'
        f'<span class="small">{len(t["alternatives"])} alternatives</span></li>'
        for t in sorted(tools, key=lambda x: x["name"])
    )
    body = f"""<nav class="crumbs"><a href="../../index.html">Home</a> / {esc(cat)}</nav>
<h1>{esc(cat)}</h1>
<p class="lede">Open source alternatives in this category.</p>
<ul class="plain">{links}</ul>"""
    return page(f"{cat} — open source alternatives", f"Open source alternatives for {cat}.", body, 2, f"category/{slugify(cat)}/index.html")


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    tools = SPEC["tools"]
    for t in tools:
        t.setdefault("alternatives", [])

    # reverse index: repo -> [(slug, name)]
    replaces = {}
    for t in tools:
        for a in t["alternatives"]:
            replaces.setdefault(a["repo"], []).append((t["slug"], t["name"]))

    write("index.html", build_home(tools))

    for t in tools:
        write(f"alternatives/{t['slug']}/index.html", build_tool(t))

    cats = {}
    for t in tools:
        cats.setdefault(t["category"], []).append(t)
    for cat, items in cats.items():
        write(f"category/{slugify(cat)}/index.html", build_category(cat, items))

    for repo, names in replaces.items():
        write(f"projects/{repo}/index.html", build_project(repo, names))

    # assets
    shutil.copyfile(ROOT / "assets" / "style.css", write("assets/style.css", ""))
    shutil.copyfile(ROOT / "assets" / "favicon.svg", write("favicon.svg", ""))

    urls = ["", "index.html"]
    urls += [f"alternatives/{t['slug']}/" for t in tools]
    urls += [f"category/{slugify(c)}/" for c in cats]
    urls += [f"projects/{r}/" for r in replaces]
    sitemap = "".join(
        f"<url><loc>{SITE['base_url']}/{u}</loc></url>" for u in dict.fromkeys(urls)
    )
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['base_url']}/sitemap.xml\n")

    pages = 1 + len(tools) + len(cats) + len(replaces)
    print(f"pages:      {pages}")
    print(f"tools:      {len(tools)}")
    print(f"projects:   {len(replaces)}")
    print(f"categories: {len(cats)}")
    print(f"output:     {OUT}")


if __name__ == "__main__":
    main()
