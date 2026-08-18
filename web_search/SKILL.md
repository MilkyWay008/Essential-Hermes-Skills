---
name: web_search
description: "Tiered web search (deepseek → tavily → tinyfish → ddgs → searxng-optional). Q&A via DeepSeek native server-side search, raw results via Tavily/TinyFish/DuckDuckGo, + optional SearXNG meta-search breadth tier. Replaces the built-in web_search tool with a richer, key-managed chain."
version: 1.1.0
author: Ringo
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [web, search, tiered, deepseek, tavily, tinyfish, ddgs, standalone]
    homepage: https://github.com/MilkyWay008/Essential-Hermes-Skills
---

# web_search — Tiered Search Skill

Performs web searches using a **tiered chain**: try the best source first, fall
through on failure, and always report which tier served the result. Designed to
be **standalone** (scripts only need Python 3 stdlib; optional `ddgs` package
enhances the last tier) so the skill folder can be dropped into any Hermes
profile or published to GitHub as-is.

## Tier Order

| Priority | Tier | What it returns | Key needed |
|----------|------|-----------------|------------|
| 1 | **deepseek** | A synthesized **answer** (DeepSeek `/responses` native `web_search` — server executes the search, model answers) | `DEEPSEEK_API_KEY` |
| 2 | **tavily** | Raw ranked results (title / url / snippet) | `TAVILY_API_KEY` |
| 3 | **tinyfish** | Raw ranked results via agent.tinyfish.ai | `TINYFISH_API_KEY` |
| 4 | **ddgs** | Raw results via DuckDuckGo (package first, stdlib fallback) | none |
| 5 (opt) | **searxng** | Raw results via **SearXNG meta-search (70+ engines)** — breadth, news/science categories, time-range, engine selection | `SEARXNG_URL` (optional; activates only when set) |

`auto` mode tries 1 → 2 → 3 → 4 → (5 if `SEARXNG_URL` set) and stops at the first success. If the top tier
has no key configured, it fails fast and the next tier takes over. SearXNG
is an **optional breadth tier** — it only joins the chain when `SEARXNG_URL`
points to a reachable public or self-hosted instance, so its absence never
blocks the base tiers.

> **SearXNG adds breadth, not depth replacement.** It aggregates 70+ engines
> in one query (vs our single-engine tiers), supports `--categories`
> (news, science, general…), `--time-range` (day/week/month/year), and
> `--engines` selection. Use it explicitly when you want multi-engine /
> news / recently-updated results. It still returns snippets only — pair with
> `web_extract` for full pages.

## When to Use

- **Q&A / "what's the latest on X"** → deepseek tier gives the best answer (model
  reads search results itself, may cost DeepSeek tokens: ~1元/M input, 2元/M output).
- **Need links / citations / raw sources** → tavily, tinyfish, or ddgs (effectively free).
- **Need multi-engine breadth, news/science categories, or time-filtered results** → searxng
  (optional; requires a `SEARXNG_URL` instance). Try `python scripts/search.py --query "..." --tier searxng --categories news --time-range week`.
- **Built-in Hermes `web_search` tool vs this skill** → use this skill unless the
  user explicitly asks for the built-in tool. See "SOUL.md Injection" below.

## Usage (agent-facing)

The agent runs the dispatcher via terminal:

```bash
python "<skills>/web/web_search/scripts/search.py" --query "your query here"
python "<skills>/web/web_search/scripts/search.py" --query "..." --tier tavily
python "<skills>/web/web_search/scripts/search.py" --query "..." --json
```

Replace `<skills>` with the profile's skills directory, e.g.
`~/.hermes/skills`.

Per-tier scripts can also be invoked directly:

```bash
python deepseek_search.py --query "..."      # answer-style
python tavily_search.py --query "..."        # raw results
python tinyfish_search.py --query "..."      # raw results
python ddgs_search.py --query "..."          # raw results, no key
```

All scripts accept `--json` for machine-readable output.

## First-Time Run & Install

The skill is ready to use once its folder exists — no build step. But two setup
items are required for tiers 1–3 (keys) and one optional (ddgs package).

### 1. API Keys — all go in the profile's `.env` (never in this file)

Open `<profile>/.env` (e.g. `~/.hermes/profiles/<profile>/.env` (or `~/.hermes/.env` for the default profile))
and make sure these exist:

```bash
DEEPSEEK_API_KEY=sk-...            # tier 1 — DeepSeek platform key
TAVILY_API_KEY=tvly-...            # tier 2 — app.tavily.com key
TINYFISH_API_KEY=sk-tinyfish-...   # tier 3 — from the tinyfish MCP config (X-API-Key)
```

The scripts read keys from the environment first, then fall back to scanning
common `.env` locations (cwd, `~/.hermes/.env`,
and the active profile path). No keys are hardcoded anywhere.

### 2. Optional: install the `duckduckgo-search` package (tier 4 enhancement)

The ddgs tier works standalone via stdlib HTML scraping, but installing the
package gives better parsing and rate-limit handling:

```bash
# Windows (git-bash / PowerShell):
python -m pip install duckduckgo-search
# or if pip is missing:
uv pip install --python <path-to-python> duckduckgo-search
```

### 3. SOUL.md Injection — make the agent prefer this skill

For the agent to **automatically use this skill instead of the built-in
`web_search` tool**, add a few lines to the profile's `SOUL.md` (e.g.
`<profile>/SOUL.md`) under a suitable section (e.g. `## General Agent System
prompt` or a new `## Web Search` section):

```markdown
## Web Search
When performing a web search, use the `web_search` skill
(tiered: deepseek → tavily → tinyfish → ddgs) instead of the built-in
web_search tool, unless the user explicitly requests the built-in tool.
```

On a fresh install, you can simply tell your agent: *"Set up the web_search
skill: copy the API keys to .env and add the SOUL.md rule for me."* The agent
will handle the rest (backups included).

### 4. Verify

```bash
python "<skills>/web/web_search/scripts/search.py" --query "hello world" --tier tavily --json
```

Expect `"success": true` and a `tier` field naming the serving tier.

## Troubleshooting

- **`DEEPSEEK_API_KEY not found`** → key missing in `.env`; tier 1 fails fast, auto falls to tavily.
- **`All search tiers failed`** → check network + that at least one key exists; ddgs needs no key so it should always be the last-resort safety net.
- **ddgs returns nothing** → DuckDuckGo rate-limits aggressively; wait a minute or use `--tier tavily`.
- **DeepSeek tier costs tokens** → it is an LLM call; prefer tavily/tinyfish/ddgs for link-hunting, deepseek for Q&A.

## Files

- `SKILL.md` — this file
- `scripts/search.py` — dispatcher (auto tier chain)
- `scripts/deepseek_search.py` — tier 1: DeepSeek `/responses` native web_search
- `scripts/tavily_search.py` — tier 2: Tavily API
- `scripts/tinyfish_search.py` — tier 3: TinyFish API (X-API-Key)
- `scripts/ddgs_search.py` — tier 4: DuckDuckGo (package + stdlib fallback)
- `scripts/searxng_search.py` — tier 5 (optional): SearXNG meta-search (needs `SEARXNG_URL`)

## SearXNG optional setup (breadth tier)

The searxng tier is dormant unless `SEARXNG_URL` is set. To enable it, add to
the profile's `.env` (or export in the shell):

```bash
SEARXNG_URL=https://searxng.example.com   # public instance, or self-hosted
```

Self-host with Docker: `docker run -d -p 8888:8080 searxng/searxng` then
`SEARXNG_URL=http://localhost:8888`. Public instances are listed at
https://searxng.org/. If unset, the tier is skipped silently — the base
chain (tiers 1-4) always works.
