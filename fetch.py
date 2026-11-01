"""Fetch public GitHub metrics for the libraries listed in repos.txt."""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
CACHE_DIR = Path("cache")
DATA_DIR = Path("data")
REPOS_FILE = Path("repos.txt")
OUT_FILE = DATA_DIR / "metrics.csv"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
FIELDS = [
    "repo", "stars", "open_issues", "days_since_push", "archived",
    "days_since_release", "contributors", "fetched_on",
]


def get_json(path, retries=3):
    """Call the GitHub API. Returns None for 404 and raises on other failures."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "supplier-risk",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {TOKEN}",
    }
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(API + path, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            if err.code in (403, 429):
                reset = err.headers.get("X-RateLimit-Reset")
                wait = int(reset) - int(time.time()) if reset else 60
                if wait > 300:
                    raise RuntimeError(
                        f"rate limit reached, resets in {wait // 60} minutes")
                wait = max(wait, 1)
                print(f"  rate limited, waiting {wait} seconds")
                time.sleep(wait)
                continue
            if err.code >= 500 and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GitHub returned HTTP {err.code} for {path}")
        except urllib.error.URLError as err:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"network error: {err.reason}")
    raise RuntimeError(f"gave up after {retries} attempts: {path}")


def cached_get(owner_repo, kind, path):
    """Return API data, reading from the cache folder when a copy exists."""
    CACHE_DIR.mkdir(exist_ok=True)
    name = owner_repo.replace("/", "__")
    cache_file = CACHE_DIR / f"{name}__{kind}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))["data"]
    data = get_json(path)
    cache_file.write_text(json.dumps({"data": data}), encoding="utf-8")
    time.sleep(0.3)
    return data


def days_since(timestamp):
    """Days between a GitHub timestamp like 2026-10-01T12:00:00Z and today."""
    if not timestamp:
        return ""
    when = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    when = when.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - when).days


def fetch_repo(owner_repo):
    repo = cached_get(owner_repo, "repo", f"/repos/{owner_repo}")
    if repo is None:
        return None
    release = cached_get(owner_repo, "release",
                         f"/repos/{owner_repo}/releases/latest")
    contributors = cached_get(owner_repo, "contributors",
                              f"/repos/{owner_repo}/contributors?per_page=100")
    return {
        "repo": owner_repo,
        "stars": repo.get("stargazers_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "days_since_push": days_since(repo.get("pushed_at")),
        "archived": bool(repo.get("archived", False)),
        "days_since_release": days_since((release or {}).get("published_at")),
        "contributors": len(contributors or []),
        "fetched_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def read_repo_list():
    repos = []
    for line in REPOS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            repos.append(line)
    return repos


def main():
    if not TOKEN:
        print("GITHUB_TOKEN is not set. Complete the token steps in the guide.")
        sys.exit(1)
    if not REPOS_FILE.exists():
        print("repos.txt not found in this folder.")
        sys.exit(1)

    DATA_DIR.mkdir(exist_ok=True)
    rows, failed = [], []
    for name in read_repo_list():
        if name.count("/") != 1:
            print(f"Skipping '{name}': use owner/name format")
            failed.append(name)
            continue
        print(f"Fetching {name} ...")
        try:
            row = fetch_repo(name)
        except RuntimeError as err:
            print(f"  ERROR: {err}")
            failed.append(name)
            continue
        if row is None:
            print("  Not found. Check the spelling on GitHub.")
            failed.append(name)
            continue
        rows.append(row)
        print(f"  stars={row['stars']} issues={row['open_issues']} "
              f"contributors={row['contributors']}")

    if rows:
        with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSaved {len(rows)} rows to {OUT_FILE}")
    print(f"Failed: {failed if failed else 'none'}")


if __name__ == "__main__":
    main()
