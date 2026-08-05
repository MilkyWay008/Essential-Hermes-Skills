#!/usr/bin/env python3
"""
DuckDuckGo web search tier — raw ranked results with URLs.

Tier 4 (last resort) of the web_search skill. No API key required.

STANDALONE: works with OR without the `duckduckgo-search` (ddgs) package.
  - If `ddgs` (or legacy `duckduckgo_search`) is importable → use the package
    (better parsing, handles rate limiting).
  - Otherwise → fall back to a pure-stdlib HTML scrape of DuckDuckGo's
    html.duckduckgo.com endpoint (no third-party deps).

Usage:
    python ddgs_search.py --query "..." [--max-results 5] [--json]
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import warnings

# Suppress the legacy-package rename warning (duckduckgo_search → ddgs) which
# otherwise pollutes --json stdout. Real errors still surface.
warnings.filterwarnings("ignore", message=".*renamed to `ddgs`.*")
warnings.filterwarnings("ignore", message=".*duckduckgo_search.*")

HTML_ENDPOINT = "https://html.duckduckgo.com/html/"


def _search_package(query: str, max_results: int) -> list:
    """Use the ddgs / duckduckgo_search package if installed."""
    try:
        from ddgs import DDGS  # new package name
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # legacy package name
        except ImportError:
            return []  # not installed — caller falls back to stdlib

    out = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                out.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("url", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                })
    except Exception:  # noqa: BLE001 — package may fail (rate limit, network)
        return []
    return out


def _search_stdlib(query: str, max_results: int, timeout: int = 30) -> list:
    """Pure-stdlib fallback: scrape DuckDuckGo's HTML endpoint."""
    params = urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(
        f"{HTML_ENDPOINT}?{params}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return []

    results = []
    # DuckDuckGo html endpoint: each result is a <div class="result"> block
    blocks = re.split(r'<div class="result[^"]*"', html)[1:]
    for block in blocks:
        if len(results) >= max_results:
            break
        title_m = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.S)
        url_m = re.search(r'class="result__a"[^>]*href="([^"]+)"', block)
        snip_m = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', block, re.S)
        if not title_m or not url_m:
            continue
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
        url = urllib.parse.unquote(url_m.group(1))
        snippet = ""
        if snip_m:
            snippet = re.sub(r"<[^>]+>", "", snip_m.group(1)).strip()
        if title and url:
            results.append({"title": title, "url": url, "snippet": snippet})
    return results


def search(query: str, max_results: int = 5, timeout: int = 30) -> dict:
    """DuckDuckGo search — package first, stdlib fallback. No key needed."""
    results = _search_package(query, max_results)
    source = "ddgs-package"
    if not results:
        results = _search_stdlib(query, max_results, timeout=timeout)
        source = "ddgs-stdlib"
    if not results:
        return {"success": False, "error": "DuckDuckGo returned no results (rate-limited or blocked?)"}
    return {
        "success": True,
        "tier": "ddgs",
        "query": query,
        "results": results,
        "source": source,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DuckDuckGo web search (no key)")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = search(args.query, max_results=args.max_results)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        print(f"(via {result.get('source', 'ddgs')})")
        for i, r in enumerate(result["results"][: args.max_results], 1):
            print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet'][:200]}")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
