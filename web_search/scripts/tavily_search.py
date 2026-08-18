#!/usr/bin/env python3
"""
Tavily web search tier — raw ranked results with URLs.

Tier 2 of the web_search skill. Returns structured results (title/url/snippet).

Key: TAVILY_API_KEY (from .env — never hardcode).
Usage:
    python tavily_search.py --query "..." [--max-results 5] [--json]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.tavily.com/search"


def _load_key() -> str:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if key:
        return key
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
                    if line.startswith("TAVILY_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
    return ""


def search(query: str, max_results: int = 5, timeout: int = 30) -> dict:
    key = _load_key()
    if not key:
        return {"success": False, "error": "TAVILY_API_KEY not found in env or .env"}

    body = {"api_key": key, "query": query, "max_results": max_results}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
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
            "score": r.get("score"),
        })
    return {
        "success": True,
        "tier": "tavily",
        "query": query,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tavily web search")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = search(args.query, max_results=args.max_results)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        for i, r in enumerate(result["results"], 1):
            print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet'][:200]}")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
