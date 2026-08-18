<p align="center">🔎 <strong>web_search</strong> — Tiered Web Search Skill for Hermes Agents</p>

**Zero-install, zero-key-out-of-the-box tiered web search for Hermes Agent. DeepSeek Responses API "smart layer" search first — with automatic fallback to Tavily, TinyFish, and DuckDuckGo (plus an optional SearXNG breadth tier) so search always works, even with no API key at all.**

<p align="center">
  <img alt="Platform: Windows / Linux / macOS" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
  <img alt="Zero Install" src="https://img.shields.io/badge/zero%20install-stdlib%20only-orange?style=for-the-badge">
  <img alt="5 Tiers" src="https://img.shields.io/badge/tiers-5-brightgreen?style=for-the-badge">
  <img alt="DeepSeek Native Search" src="https://img.shields.io/badge/deepseek%20responses%20api-native%20search-purple?style=for-the-badge">
  <img alt="Standalone" src="https://img.shields.io/badge/standalone-github%20ready-yellow?style=for-the-badge">
</p>

<p align="center"><em>By Ringo — for Hermes Agent profiles · v1.1.0</em></p>

---

## 📑 Table of Contents

- [💡 Why This Skill Exists](#-why-this-skill-exists)
- [✨ Key Features](#-key-features)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Quick Start](#-quick-start)
- [🗂️ Tier Reference](#️-tier-reference)
- [📁 Directory Structure](#-directory-structure)
- [🧪 Troubleshooting](#-troubleshooting)
- [🛣️ Roadmap](#️-roadmap)
- [📦 Dependencies](#-dependencies)
- [🔍 Search Keywords](#-search-keywords)
- [📝 Credits & License](#-credits--license)

---

## 💡 Why This Skill Exists

**DeepSeek's Responses API now supports a native, server-side "smart layer" web search** — you send the query with a `web_search` tool, and DeepSeek's model searches the live web *itself*, reads the results, and synthesizes an answer. No search-engine key. No client-side scraping. Just one API call. *(See [this thread](https://twitter-thread.com/t/2084871704103493708) for the announcement walkthrough.)*

**The problem:** most agentic systems (including Hermes Agent's built-in `web_search` tool) have **not been updated to support this new protocol yet**. Patching agent source code is fragile — the next update overwrites it.

**The solution:** a **skill-layer tiered search** that lives *outside* the agent binary:

1. **DeepSeek native search** — the new smart layer, Q&A-grade answers
2. **Tavily** — raw ranked results
3. **TinyFish** — raw ranked results (hosted search API)
4. **DuckDuckGo (ddgs)** — no key required, pure-stdlib fallback
5. **SearXNG (optional)** — self-hosted meta-search breadth; **inactive by default** until you run a SearXNG server and point `SEARXNG_URL` at it

If a tier fails or has no key, the next tier automatically takes over — so **search always works, out of the box, even with zero API keys configured**.

---

## ✨ Key Features

- **🔎 DeepSeek smart-layer search first** — server-side `web_search` builtin; the model searches + synthesizes (no search-engine key needed)
- **🔄 Automatic tier fallback** — `auto` tries deepseek → tavily → tinyfish → ddgs, stops at first success, reports the winning tier
- **🔑 Keys from `.env`, never hardcoded** — scripts read `DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `TINYFISH_API_KEY` from the environment
- **🦆 DuckDuckGo works with zero keys** — package-first, pure-Python-stdlib fallback
- **📦 Standalone & GitHub-ready** — only Python 3 stdlib required; optional `ddgs` package enhances tier 4
- **🧩 Drop-in for any Hermes profile** — folder-based skill, no agent code changes
- **🛡️ Update-proof** — survives Hermes upgrades; SOUL.md injection makes agents prefer it over the built-in tool

### Feature Matrix

| Tier | Engine | Returns | Key Required | Cost |
|------|--------|---------|--------------|------|
| 1 | DeepSeek `/responses` native search | Synthesized **answer** | `DEEPSEEK_API_KEY` | ~1元/M in · 2元/M out |
| 2 | Tavily API | Raw results (title/url/snippet) | `TAVILY_API_KEY` | free tier |
| 3 | TinyFish API | Raw results (title/url/snippet) | `TINYFISH_API_KEY` | free tier |
| 4 | DuckDuckGo | Raw results (title/url/snippet) | **none** | free |
| 5 (opt) | SearXNG | Raw results (title/url/snippet) — 70+ engines | `SEARXNG_URL` (your own instance) | free (self-hosted) |

---

## ⚙️ How It Works

```
                    ┌─────────────────────────────┐
                    │   search.py (dispatcher)    │
                    │  --query "..." --tier auto  │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────┬───────────┼───────────┬──────────────┐
        ▼              ▼           ▼           ▼
   ┌─────────┐   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ deepseek│   │ tavily  │  │ tinyfish │  │   ddgs   │
   │  tier 1 │   │ tier 2  │  │  tier 3  │  │  tier 4  │
   │ smart   │   │ raw     │  │ raw      │  │ raw      │
   │ answer  │   │ results │  │ results  │  │ results  │
   └─────────┘   └─────────┘  └──────────┘  └──────────┘
       │              │             │             │
       └──────────────┴─────────────┴─────────────┘
                  first success wins
```

An optional **5th tier — SearXNG** joins the chain — but only when you set `SEARXNG_URL`. It is **inactive by default**: while no URL is configured, the dispatcher skips it entirely and the chain simply runs tiers 1–4.

**What it is:** [SearXNG](https://docs.searxng.org/) is a privacy-respecting, **self-hosted meta-search engine**. It aggregates 70+ upstream engines (Google, Bing, Brave, Wikipedia, …) from *your own server* — no search-API key needed, and queries leave from *your* IP, not a third-party's.

**How it becomes functional:** tier 5 requires you to run a SearXNG instance yourself and point the skill at it:

1. **Run a SearXNG server on your machine** — easiest via Docker:

   ```bash
   docker run -d -p 32768:8080 -e "SEARXNG_BASE_URL=http://localhost:32768" --name searxng searxng/searxng
   ```

   (or install it natively: `pip install searxng`, or your distro's package; any SearXNG instance — local or one you trust — works.)

2. **Point the skill at it** — add to your profile's `.env`:

   ```
   SEARXNG_URL=http://localhost:32768
   ```

3. **Verify** — from then on the dispatcher includes SearXNG in `--tier auto` (or force it with `--tier searxng`). No `SEARXNG_URL`, no tier 5 — simple as that.

Each tier is an independent script invoked as a subprocess by the dispatcher — so a failure in one never affects the others, and each script can also be run standalone.

---

## 🚀 Quick Start

```bash
# 1. (Optional) Install the ddgs package to enhance tier 4:
python -m pip install ddgs
#    or: uv pip install --python <path-to-python> ddgs

# 2. (Optional) Add API keys to your profile's .env for tiers 1–3:
#    DEEPSEEK_API_KEY=sk-...
#    TAVILY_API_KEY=tvly-...
#    TINYFISH_API_KEY=sk-tinyfish-...

# 2b. (Optional) Activate tier 5 (SearXNG) — ONLY if you run your own instance:
#     docker run -d -p 32768:8080 -e "SEARXNG_BASE_URL=http://localhost:32768" searxng/searxng
#     SEARXNG_URL=http://localhost:32768   # <-- your own server, queried from your IP

# 3. Search!
python "<skills>/web/web_search/scripts/search.py" --query "your query here"
python "<skills>/web/web_search/scripts/search.py" --query "..." --tier tavily
python "<skills>/web/web_search/scripts/search.py" --query "..." --json
```

**No keys configured?** Tier 4 (DuckDuckGo) still works — search just falls through to it automatically.

### Agent Integration (SOUL.md Injection)

Add these lines to your profile's `SOUL.md` so agents prefer this skill over the built-in tool:

```markdown
## Web Search
When performing a web search, use the `web_search` skill
(tiered: deepseek → tavily → tinyfish → ddgs) instead of the built-in
web_search tool, unless the user explicitly requests the built-in tool.
```

Then just tell your agent: *"Set up the web_search skill for me."* It will handle keys, backups, and the SOUL.md rule.

---

## 🗂️ Tier Reference

| Tier | Command | Output |
|------|---------|--------|
| 1 · DeepSeek | `deepseek_search.py --query "..."` | Synthesized answer |
| 2 · Tavily | `tavily_search.py --query "..."` | Raw ranked results |
| 3 · TinyFish | `tinyfish_search.py --query "..."` | Raw ranked results |
| 4 · DuckDuckGo | `ddgs_search.py --query "..."` | Raw ranked results |
| 5 · SearXNG (opt) | `searxng_search.py --query "..."` | Raw ranked results — 70+ engines (requires your own SearXNG instance) |

All scripts accept `--json` for machine-readable output. The dispatcher accepts `--tier auto|deepseek|tavily|tinyfish|ddgs|searxng`, `--max-results`, and `--timeout`.

---

## 📁 Directory Structure

```
web_search/
├── SKILL.md                       # skill definition + full docs
├── README.md                      # this file
└── scripts/
    ├── search.py                  # dispatcher (auto tier chain)
    ├── deepseek_search.py         # tier 1: DeepSeek /responses native web_search
    ├── tavily_search.py           # tier 2: Tavily API
    ├── tinyfish_search.py         # tier 3: TinyFish API (X-API-Key)
    ├── ddgs_search.py             # tier 4: DuckDuckGo (package + stdlib fallback)
    └── searxng_search.py          # tier 5 (optional): SearXNG meta-search
```

---

## 🧪 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `DEEPSEEK_API_KEY not found` | Add key to `.env`; or let auto fall through to tavily |
| `All search tiers failed` | Check network; ddgs needs no key so it should always be the safety net |
| ddgs returns nothing | DuckDuckGo rate-limits aggressively — wait a minute or use `--tier tavily` |
| DeepSeek tier costs tokens | It's an LLM call; use tavily/tinyfish/ddgs for link-hunting, deepseek for Q&A |

---

## 🛣️ Roadmap

| Status | Item |
|--------|------|
| ✅ Done | 4-tier chain, `.env` key handling, standalone ddgs fallback |
| 🔜 Next | Optional caching layer, per-tier timeouts config, more engines (SearXNG, Exa) |

---

## 📦 Dependencies

| Dependency | Required? | Used For |
|------------|-----------|----------|
| Python 3 (stdlib only) | ✅ required | All tiers (urllib, json, argparse) |
| `ddgs` / `duckduckgo_search` | ⭕ optional | Tier 4 enhanced parsing & rate-limit handling |
| SearXNG instance (`SEARXNG_URL`) | ⭕ optional | Tier 5 — only needed if you self-host one |

---

## 🔍 Search Keywords

web search skill, tiered web search, DeepSeek Responses API, DeepSeek native search, smart layer search, DeepSeek web_search builtin, Tavily search, TinyFish search, DuckDuckGo search, ddgs, Hermes Agent skill, zero install web search, no API key web search, agentic search skill, LLM search fallback, SearXNG meta-search, 联网搜索, 分层搜索, 网页搜索技能, DeepSeek 搜索, 无需 API key 搜索

---

## 📝 Credits & License

Built by **Ringo** for the Hermes Agent ecosystem — inspired by DeepSeek's 2026-07-31 V4-Flash update adding native Responses API web search.

Distributed under the **MIT License**. Use it, fork it, ship it.

---

<p align="center"><em>🔎 Search smarter. Fall back gracefully. Ship it anywhere.</em></p>
