"""Fetch GitHub metadata for every repository referenced in data/tools.json.

Results are cached in data/repos.json so the build never depends on the network.
Run with --force to refresh.
"""

import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "repos.json"
TOKEN_FILE = pathlib.Path.home() / ".config" / "opencode" / "github-token.txt"

FIELDS = (
    "full_name", "description", "stargazers_count", "forks_count",
    "language", "archived", "html_url", "homepage", "pushed_at",
    "open_issues_count", "topics", "license",
)


def token():
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return os.environ.get("GITHUB_TOKEN", "")


def repos_in_use():
    spec = json.loads((DATA / "tools.json").read_text(encoding="utf-8"))
    seen = []
    for tool in spec["tools"]:
        for alt in tool["alternatives"]:
            if alt["repo"] not in seen:
                seen.append(alt["repo"])
    return seen


def fetch(repo, tok):
    req = urllib.request.Request(
        "https://api.github.com/repos/" + repo,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "openalt-build",
            **({"Authorization": "Bearer " + tok} if tok else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    force = "--force" in sys.argv
    cache = {}
    if CACHE.exists() and not force:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    tok = token()
    wanted = repos_in_use()
    fetched = 0
    failed = []

    for repo in wanted:
        if repo in cache and not force:
            continue
        try:
            raw = fetch(repo, tok)
        except urllib.error.HTTPError as exc:
            failed.append((repo, exc.code))
            continue
        except Exception as exc:  # noqa: BLE001
            failed.append((repo, str(exc)))
            continue
        cache[repo] = {k: raw.get(k) for k in FIELDS}
        fetched += 1
        time.sleep(0.2)

    DATA.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")

    stars = sum(v.get("stargazers_count") or 0 for v in cache.values())
    print(f"repos in spec: {len(wanted)}")
    print(f"cached now:    {len(cache)}")
    print(f"fetched:       {fetched}")
    print(f"total stars:   {stars:,}")
    if failed:
        print("failed:")
        for repo, why in failed:
            print(f"  {repo}: {why}")


if __name__ == "__main__":
    main()
