#!/usr/bin/env python3
"""
TinyFish web search tier — raw ranked results with URLs.

Tier 3 of the web_search skill. Uses TinyFish's hosted search API
(https://agent.tinyfish.ai/v1/search) with X-API-Key auth.

Key: TINYFISH_API_KEY (from .env — never hardcode).
Usage:
    python tinyfish_search.py --query "..." [--max-results 5] [--json]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://agent.tinyfish.ai/v1/search"


def _load_key() -> str:
    key = os.environ.get("TINYFISH_API_KEY", "").strip()
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
                    if line.startswith("TINYFISH_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
    return ""


def search(query: str, max_results: int = 5, timeout: int = 30) -> dict:
    key = _load_key()
    if not key:
        return {"success": False, "error": "TINYFISH_API_KEY not found in env or .env"}

    params = urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(
        f"{ENDPOINT}?{params}",
        headers={"X-API-Key": key, "Accept": "application/json"},
        method="GET",
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
            "snippet": r.get("snippet", ""),
            "position": r.get("position"),
        })
    return {
        "success": True,
        "tier": "tinyfish",
        "query": query,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="TinyFish web search")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = search(args.query, max_results=args.max_results)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        for i, r in enumerate(result["results"][: args.max_results], 1):
            print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet'][:200]}")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
