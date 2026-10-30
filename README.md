# OpenAlt

A programmatic SEO site: open source alternatives to the tools people already pay for.

**Status:** vertical slice. 4 products, 15 projects, 24 pages. Not deployed.

## Why this niche

The search demand is real and specific — people type "open source alternative to Notion", not "open source productivity tools". Every page targets one of those queries exactly, so there is no keyword guessing.

The data is free and reliable: the GitHub API returns stars, license, language and last activity for every project. Nothing is scraped, nothing is invented, and every claim on a page is either editorial (the one-line "why") or fetched.

## Structure

```
data/tools.json      curated list: commercial tool -> open source alternatives
data/repos.json      GitHub metadata cache, refreshed by fetch_github.py
scripts/fetch_github.py  pulls /repos/{owner}/{repo} for every cited project
scripts/build.py     renders the whole site into site/
assets/style.css     one stylesheet, no framework
site/                generated output (gitignored)
```

## Build

```bash
python scripts/fetch_github.py     # cache GitHub metadata
python scripts/build.py            # render site/
python -m http.server 8123 --directory site
```

`fetch_github.py` uses the token at `~/.config/opencode/github-token.txt` (5,000 req/hr). Without it you get 60/hr, which is enough for this dataset but not for a large one.

## Page types

| Page | URL | Count |
|---|---|---|
| Home | `/` | 1 |
| Commercial tool | `/alternatives/{tool}/` | 4 |
| Category | `/category/{category}/` | 4 |
| Project | `/projects/{owner}/{repo}/` | 15 |

Each tool page carries editorial notes, a star-sorted card grid, and a comparison table. Each project page links back to every tool it replaces, which builds the internal link graph both ways.

Generated alongside the HTML: `sitemap.xml` and `robots.txt`.

## What was verified

- 24 pages build from 15 live GitHub records, 713,925 combined stars.
- Every page loads with zero console errors.
- Stylesheet resolves correctly at all three depths (`/`, `/alternatives/x/`, `/projects/o/r/`).

Two bugs were found and fixed during the slice:

1. **Link depth was off by one.** Subpages requested `/alternatives/assets/style.css` and rendered unstyled. Caught by reading the access log, not by eye.
2. **`NOASSERTION` leaked into the UI.** AFFiNE has no SPDX license, so the card printed the API's placeholder. Now renders as "see repo".

## Next

1. **Scale the dataset.** 4 tools → ~45. At 4–6 alternatives each that is roughly 200 project pages plus 45 tool pages, ~255 total.
2. **Deploy.** GitHub Pages, repository `oss-alternatives`, served from `/docs` or `gh-pages`.
3. **Then measure.** Search Console, which queries actually land, which pages get impressions but no clicks.

## Known gaps

- No search, no filtering. Fine at 4 tools, needed past ~20.
- No per-project "last commit" freshness signal on cards, though the data is cached.
- Descriptions are the upstream ones, including non-English text. Should be normalised.
