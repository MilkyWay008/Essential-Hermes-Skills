#!/usr/bin/env python3
"""
DeepSeek Responses API web search tier — server-side search via /responses.

Tier 1 of the web_search skill. Uses DeepSeek's native Responses API web_search
builtin: the *server* executes the search and the model synthesizes an answer.
Returns an ANSWER, not raw links.

Key: DEEPSEEK_API_KEY (from .env — never hardcode).
Usage:
    python deepseek_search.py --query "what is the weather in vegas nv" [--max-tokens 400] [--json]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"


def _load_key() -> str:
    """Read DEEPSEEK_API_KEY from environment or .env files (no hardcoding)."""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    # Fallback: scan common .env locations
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
                    if line.startswith("DEEPSEEK_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
    return ""


def search(query: str, max_tokens: int = 400, timeout: int = 60) -> dict:
    """Run DeepSeek server-side web search. Returns a result dict."""
    key = _load_key()
    if not key:
        return {"success": False, "error": "DEEPSEEK_API_KEY not found in env or .env"}

    body = {
        "model": MODEL,
        "input": query,
        "tools": [{"type": "web_search"}],
        "max_output_tokens": max_tokens,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
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

    if data.get("status") == "failed" or data.get("error"):
        return {
            "success": False,
            "error": json.dumps(data.get("error") or data, ensure_ascii=False)[:500],
        }

    # Extract final answer text from message items
    answer_parts = []
    searched = False
    for item in data.get("output", []):
        if item.get("type") == "web_search_call":
            searched = True
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    answer_parts.append(content.get("text", ""))
    answer = "\n".join(p for p in answer_parts if p).strip()

    return {
        "success": True,
        "tier": "deepseek",
        "query": query,
        "answer": answer or "(no answer text returned)",
        "searched": searched,
        "model": MODEL,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek Responses web search")
    parser.add_argument("--query", required=True, help="search query")
    parser.add_argument("--max-tokens", type=int, default=400)
    parser.add_argument("--json", action="store_true", help="output raw JSON")
    args = parser.parse_args()

    result = search(args.query, max_tokens=args.max_tokens)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        print(result["answer"])
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
