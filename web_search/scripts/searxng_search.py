#!/usr/bin/env python3
"""
SearXNG web search tier — meta-search aggregating 70+ engines (optional).

Tier 5 (optional) of the web_search skill. Adds breadth our single-engine
tiers lack: multi-engine meta-search, category filters (news/science/...),
time_range filtering (day/week/month/year), and explicit engine selection.

Requires SEARXNG_URL (a public or self-hosted SearXNG instance). If it is not
set or unreachable, this tier reports failure and the dispatcher falls through.

Usage:
    python searxng_search.py --query "..." [--max-results 5] [--json]
        [--categories news] [--time-range week] [--engines google,bing] [--safesearch 0]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _load_url() -> str:
    """Read SEARXNG_URL from env or .env (never hardcoded)."""
    url = os.environ.get("SEARXNG_URL", "").strip().rstrip("/")
    if url:
        return url
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.environ.get("HERMES_HOME", ""), ".env"),
        os.path.expanduser("~/.hermes/.env"),
    ]
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("SEARXNG_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/")
        except OSError:
            continue
    return ""


def search(
    query: str,
    max_results: int = 5,
    timeout: int = 30,
    categories: str = "",
    time_range: str = "",
    engines: str = "",
    safesearch: int = 0,
) -> dict:
    base_url = _load_url()
    if not base_url:
        return {"success": False, "error": "SEARXNG_URL not set in env or .env (needs a SearXNG instance)"}

    params = {"q": query, "format": "json", "limit": max_results}
    if categories:
        params["categories"] = categories
    if time_range:
        params["time_range"] = time_range
    if engines:
        params["engines"] = engines
    if safesearch:
        params["safesearch"] = str(safesearch)

    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        return {"success": False, "error": f"HTTP {e.code}: {detail}"}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": str(e)}

    results = []
    for r in data.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "engine": r.get("engine"),
            "published_date": r.get("published_date"),
        })
    return {
        "success": True,
        "tier": "searxng",
        "query": query,
        "results": results,
        "meta": {
            "instance": base_url,
            "categories": categories or None,
            "time_range": time_range or None,
            "engines": engines or "aggregated (instance config)",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SearXNG meta-search (optional tier)")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--categories", default="", help="filter by category: general, news, science, images, ...")
    parser.add_argument("--time-range", default="", help="filter by recency: day, week, month, year")
    parser.add_argument("--engines", default="", help="comma-separated engine names, e.g. google,bing")
    parser.add_argument("--safesearch", type=int, default=0, help="0=none, 1=moderate, 2=strict")
    args = parser.parse_args()

    result = search(
        args.query,
        max_results=args.max_results,
        categories=args.categories,
        time_range=args.time_range,
        engines=args.engines,
        safesearch=args.safesearch,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        print(f"[searxng via {result['meta']['instance']}]")
        for i, r in enumerate(result["results"], 1):
            print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet'][:200]}")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
