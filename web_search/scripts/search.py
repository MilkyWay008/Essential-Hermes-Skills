#!/usr/bin/env python3
"""
web_search dispatcher — tiered search: deepseek → tavily → tinyfish → ddgs → (searxng, optional).

Tries tiers in order; falls through on failure; reports which tier succeeded.
Keys are read from .env at runtime (never hardcoded). Works standalone — each
tier script lives in this folder and is invoked as a subprocess. SearXNG is an
optional breadth tier that joins the chain only when SEARXNG_URL is set.

Usage:
    python search.py --query "what is the weather in vegas nv"
    python search.py --query "..." --tier tavily        # force one tier
    python search.py --query "..." --tier auto --json   # machine-readable
    python search.py --query "..." --max-results 5
"""
import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TIERS = {
    "deepseek": "deepseek_search.py",
    "tavily": "tavily_search.py",
    "tinyfish": "tinyfish_search.py",
    "ddgs": "ddgs_search.py",
    "searxng": "searxng_search.py",  # optional: activates only when SEARXNG_URL is set
}

ORDER_BASE = ["deepseek", "tavily", "tinyfish", "ddgs"]


def _searxng_available() -> bool:
    """SearXNG is available only if SEARXNG_URL is set (env or .env)."""
    if os.environ.get("SEARXNG_URL", "").strip():
        return True
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.environ.get("HERMES_HOME", ""), ".env"),
        os.path.expanduser("~/.hermes/.env"),
    ]
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                if any(line.strip().startswith("SEARXNG_URL=") for line in fh):
                    return True
        except OSError:
            continue
    return False


def _effective_order() -> list:
    """Base order, plus searxng between ddgs and the end when configured."""
    base = list(ORDER_BASE)
    if _searxng_available():
        base.append("searxng")
    return base


def run_tier(tier: str, query: str, max_results: int, timeout: int = 120) -> dict:
    """Run one tier script and parse its JSON output."""
    script = os.path.join(SCRIPT_DIR, TIERS[tier])
    # deepseek uses --max-tokens; the raw-result tiers use --max-results
    if tier == "deepseek":
        limit_args = ["--max-tokens", str(400)]
    else:
        limit_args = ["--max-results", str(max_results)]
    cmd = [sys.executable, script, "--query", query, *limit_args, "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"success": False, "tier": tier, "error": "timeout"}
    if proc.returncode != 0:
        return {"success": False, "tier": tier, "error": proc.stderr.strip()[:300]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"success": False, "tier": tier, "error": "bad JSON output"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiered web search")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument(
        "--tier",
        choices=["auto"] + list(TIERS.keys()),
        default="auto",
        help="force a specific tier, or auto (default: try in order)",
    )
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=int, default=120, help="per-tier timeout")
    args = parser.parse_args()

    if args.tier != "auto":
        tiers = [args.tier]
    else:
        tiers = _effective_order()

    last_error = None
    for tier in tiers:
        result = run_tier(tier, args.query, args.max_results, timeout=args.timeout)
        if result.get("success"):
            if args.json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(f"--- tier: {result.get('tier')} ---")
                if "answer" in result and result["answer"]:
                    print(result["answer"])
                else:
                    for i, r in enumerate(result.get("results", [])[: args.max_results], 1):
                        print(f"{i}. {r.get('title', '')}")
                        print(f"   {r.get('url', '')}")
                        print(f"   {(r.get('snippet') or '')[:200]}")
            return 0
        last_error = result.get("error", "unknown error")

    # All tiers failed
    if args.json:
        print(json.dumps({"success": False, "error": f"All tiers failed: {last_error}"}, ensure_ascii=False))
    else:
        print(f"All search tiers failed. Last error: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
