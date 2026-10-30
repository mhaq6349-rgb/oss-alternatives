"""Build a prospect list from public job boards.

Finds companies hiring for roles that name the tools in our directory, then
pulls their live job board to confirm the mention and get the role title.

Sources are ATS APIs that are designed to be public: Greenhouse, Lever, Ashby.
No scraping of LinkedIn, no login, no ToS problem.

    python outreach/prospects.py

Writes outreach/prospects.csv
"""

import csv
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAVILY_KEY = pathlib.Path.home() / ".config" / "opencode" / "keys" / "tavily.txt"
OUT = ROOT / "outreach" / "prospects.csv"

TOOLS = ["Figma", "Jira", "Confluence", "Notion", "Slack", "Linear", "Asana", "Miro"]

# The vendors themselves are not prospects, and aggregators produce noise.
EXCLUDE = {
    "figma", "notion", "slack", "linear", "asana", "miro", "atlassian",
    "jobgether", "greenhouse", "lever", "ashby",
}

MIN_TOOLS = 3
MAX_PER_COMPANY = 2
MAX_AGE_DAYS = 400

QUERIES = [
    'site:job-boards.greenhouse.io "Figma" "Jira"',
    'site:boards.greenhouse.io "Figma" "Confluence"',
    'site:jobs.lever.co "Figma" "Jira"',
    'site:jobs.ashbyhq.com "Figma" "Notion"',
    'site:job-boards.greenhouse.io "Jira" "Confluence" "Slack"',
    'site:jobs.lever.co "Notion" "Figma"',
    'site:jobs.ashbyhq.com "Jira" "Confluence"',
    'site:job-boards.greenhouse.io "Linear" "Notion"',
]

ATS_PATTERNS = [
    ("greenhouse", re.compile(r"(?:job-)?boards\.greenhouse\.io/([A-Za-z0-9_-]+)")),
    ("lever", re.compile(r"jobs\.lever\.co/([A-Za-z0-9_-]+)")),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([A-Za-z0-9_-]+)")),
]

UA = {"User-Agent": "openalt-prospects/1.0"}


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def tavily(query):
    if not TAVILY_KEY.exists():
        raise SystemExit(f"missing Tavily key at {TAVILY_KEY}")
    key = TAVILY_KEY.read_text(encoding="utf-8").strip()
    payload = json.dumps({
        "api_key": key,
        "query": query,
        "max_results": 10,
        "search_depth": "basic",
    }).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={**UA, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8")).get("results", [])


def discover():
    """Return {(ats, token): source_query} from search results."""
    found = {}
    for q in QUERIES:
        try:
            results = tavily(q)
        except Exception as exc:  # noqa: BLE001
            print(f"  search failed: {q} ({exc})")
            continue
        for r in results:
            url = r.get("url", "")
            for ats, pat in ATS_PATTERNS:
                m = pat.search(url)
                if m:
                    found.setdefault((ats, m.group(1).lower()), q)
                    break
        time.sleep(0.4)
    return found


def greenhouse_jobs(token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = http_json(url)
    out = []
    for j in data.get("jobs", []):
        body = (j.get("content") or "") + " " + (j.get("title") or "")
        out.append({
            "role": j.get("title", ""),
            "url": j.get("absolute_url", ""),
            "text": body,
            "updated": j.get("updated_at", ""),
        })
    return out


def lever_jobs(token):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = http_json(url)
    out = []
    for j in data if isinstance(data, list) else []:
        body = (j.get("descriptionPlain") or "") + " " + (j.get("text") or "")
        cats = j.get("categories") or {}
        out.append({
            "role": j.get("text", ""),
            "url": j.get("hostedUrl", ""),
            "text": body,
            "updated": cats.get("createdAt", "") or "",
        })
    return out


def ashby_jobs(token):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    data = http_json(url)
    out = []
    for j in data.get("jobs", []):
        body = (j.get("descriptionHtml") or "") + " " + (j.get("title") or "")
        out.append({
            "role": j.get("title", ""),
            "url": j.get("jobUrl", ""),
            "text": body,
            "updated": j.get("publishedAt", "") or "",
        })
    return out


FETCHERS = {"greenhouse": greenhouse_jobs, "lever": lever_jobs, "ashby": ashby_jobs}


def matched_tools(text):
    low = text.lower()
    return [t for t in TOOLS if t.lower() in low]


def main():
    from collections import Counter
    from datetime import date, datetime

    today = date.today()

    def stale(posted):
        try:
            when = datetime.fromisoformat(posted[:10]).date()
        except ValueError:
            return False
        return (today - when).days > MAX_AGE_DAYS

    print("searching for job boards...")
    boards = discover()
    print(f"boards found: {len(boards)}")

    rows = []
    for (ats, token), query in sorted(boards.items()):
        if token in EXCLUDE:
            continue
        try:
            jobs = FETCHERS[ats](token)
        except Exception as exc:  # noqa: BLE001
            print(f"  {ats}/{token}: {exc}")
            continue

        hits = []
        for job in jobs:
            tools = matched_tools(job["text"])
            if len(tools) < MIN_TOOLS:
                continue
            if stale(job["updated"]):
                continue
            hits.append({
                "company": token,
                "ats": ats,
                "role": job["role"],
                "tools": ", ".join(tools),
                "url": job["url"],
                "posted": job["updated"][:10],
                "board_jobs": len(jobs),
                "source": query,
            })
        hits.sort(key=lambda r: -len(r["tools"].split(",")))
        rows.extend(hits[:MAX_PER_COMPANY])
        print(f"  {ats}/{token}: {len(jobs)} jobs, {len(hits)} qualify")

    seen_company = Counter()
    seen_role = set()
    unique = []
    for r in rows:
        key = (r["company"], r["role"])
        if key in seen_role:
            continue
        if seen_company[r["company"]] >= MAX_PER_COMPANY:
            continue
        seen_role.add(key)
        seen_company[r["company"]] += 1
        unique.append(r)

    unique.sort(key=lambda r: (-len(r["tools"].split(",")), r["board_jobs"], r["company"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["company", "ats", "role", "tools", "url", "posted", "board_jobs", "source"])
        writer.writeheader()
        writer.writerows(unique)

    companies = sorted({r["company"] for r in unique})
    print()
    print(f"rows:      {len(unique)}")
    print(f"companies: {len(companies)}")
    print(f"output:    {OUT}")
    print()
    for c in companies:
        print("  " + c)


if __name__ == "__main__":
    main()
