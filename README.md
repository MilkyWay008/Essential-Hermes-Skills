# <p align="center">🧰 Essential Hermes Skills — The Power Bundle</p>

<p align="center">
  <strong>Five production-tested skills that turn Hermes Agent into a serious workhorse.</strong><br>
  Debug any unfamiliar codebase. Run any complex project. Search the web. Read any page. Reverse anything.<br>
  <em>Built from real debugging sessions. Battle-tested in production.</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Skills-5_Production_Ready-2EA043?style=for-the-badge" alt="5 Production Skills"></a>
  <a href="#"><img src="https://img.shields.io/badge/Agent-Hermes_Agent-FFD700?style=for-the-badge" alt="Hermes Agent"></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows_%7C_Linux_%7C_macOS-0078D6?style=for-the-badge" alt="Cross-Platform"></a>
  <a href="#"><img src="https://img.shields.io/badge/Type-Essential_Workflows-8A2BE2?style=for-the-badge" alt="Essential Workflows"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License MIT"></a>
</p>

<p align="center">
  <strong>by Ringo / MilkyWay008</strong> · MIT License
</p>

---

## 📑 Table of Contents

- [💡 What This Bundle Is](#-what-this-bundle-is)
- [📦 The Five Skills](#-the-five-skills)
- [🧭 Which Skill Do I Use When?](#-which-skill-do-i-use-when)
- [⚙️ How They Work Together](#️-how-they-work-together)
- [🚀 Quick Start](#-quick-start)
- [📁 Repository Structure](#-repository-structure)
- [🔍 Search Keywords](#-search-keywords)
- [📝 License](#-license)

---

## 💡 What This Bundle Is

A curated collection of **five essential Hermes Agent skills** — the kind of tools you reach for every single day:

- **Debug** unfamiliar codebases with discipline, not chaos
- **Execute** complex multi-phase projects without losing the thread
- **Search** the web with a tiered fallback chain that never dead-ends
- **Extract** content from any page — even JavaScript-heavy SPAs
- **Reverse** binaries, apps, and protocols with an 85-skill security pack

Each skill is **self-contained**, **production-tested**, and documented with its own README. Drop any of them into any Hermes profile and it just works.

> **The philosophy:** skills should be enforced *systems*, not suggestions. Every skill here encodes hard rules, triggers, and fallbacks — so the agent does the right thing without being reminded.

---

## 📦 The Five Skills

### 1. 🔧 `app-debug-workflow` — Disciplined Codebase Auditing

**What it is:** A 90-minute timeboxed, multi-session workflow for auditing an unfamiliar full-stack codebase — security, performance, reliability, and dev-tooling bugs.

**Why it's useful:**
- **Timeboxed by design** — 90 minutes, no rabbit holes, no scope creep
- **Session discipline** — Session A (debug, *no code*) then Session B (fix, *no planning*): you never break what you're analyzing
- **Multi-verifier gates** — rubber-duck and subagent audits before anything gets fixed
- **Complete pipeline** — discover → duck-verify → plan → handoff → fix → validate
- **25 documented pitfalls** — MSYS2 path bugs, venv isolation, patch backslashes, taskkill git-bash traps — learned the hard way, so you don't have to

**Trigger phrases:** *"codebase audit" · "security review" · "bug hunt" · "audit this unfamiliar codebase for bugs"*

---

### 2. 🏗️ `complex-project-workflow` — The Master Project Engine

**What it is:** A universal 7-phase master workflow — Charter → Recon → Blueprint → Review → Execute → Assemble → Retrospect — for **any** complex project: code builds, consulting, content, research, or multi-phase delivery.

**Why it's useful:**
- **One workflow for everything** — builds, consulting, content creation, business ops, research
- **Hard gates between phases** — you can't execute before the blueprint is reviewed
- **Duck-council audits** — multiple LLM perspectives before critical decisions
- **Orchestrator discipline** — the agent never implements directly; it plans, delegates, and verifies
- **Context-health first** — subagents absorb the heavy lifting so the main thread stays sharp
- **Expanded Mode** for client/non-code work, time-boxed event prep built in

**Trigger phrases:** *"MASTER WORKFLOW — use for ANY project" · 2+ phases · 3+ components · external stakeholders*

---

### 3. 🌐 `web_extract` — Read Any Page, No Matter What

**What it is:** A tiered web-content extraction skill — Jina Reader first (except X.com), trafilatura fallback (best for X.com), headless browser as last resort.

**Why it's useful:**
- **Never dead-ends** — three fallback tiers mean almost any URL is readable: articles, docs, JS-heavy SPAs, X.com posts
- **Cost-aware** — free tiers first, expensive browser automation last
- **Verbatim code** — every method ships with copy-paste commands (curl, execute_code, browser_navigate)
- **Known-limitations table** — YouTube 403s, login-gated pages, 429/451/403, the 50KB stdout cap — documented up front

**Trigger phrases:** user gives a URL and asks to *read, extract, fetch, summarize, or look up* its content

---

### 4. 🔎 `web_search` — Tiered Search That Never Fails

**What it is:** A tiered web-search chain — **DeepSeek → Tavily → TinyFish → DuckDuckGo** — that replaces the built-in web_search tool with a richer, key-managed chain.

**Why it's useful:**
- **Best answer first** — DeepSeek tier synthesizes an actual *answer* (server-side search + model reasoning)
- **Raw results when you need them** — Tavily/TinyFish/DuckDuckGo for links, citations, and sources (effectively free)
- **Fail-fast fallthrough** — auto mode tries tier 1 → 2 → 3 → 4 and stops at the first success
- **Zero-key safety net** — DuckDuckGo needs no key, so the chain always has a last resort
- **Standalone by design** — scripts only need Python 3 stdlib; drop the folder into any profile or publish to GitHub as-is
- **SOUL.md injection** — teach the agent to prefer this skill over the built-in tool, automatically

**Trigger phrases:** any web search / online lookup / fact-check / research — *"Search for X" · "Look up Y" · "Find information about Z"*

---

### 5. 🕵️ `reverse-skill` — The 85-Skill Security & Reverse Engineering Pack

**What it is:** A Hermes-ready port of the popular [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) project (MIT, 23.9k⭐) — **85 security/RE skill modules** behind a routing skill that dispatches tasks to the right specialist: APK/.NET/JS/Go/IDA/radare2 reverse engineering, malware analysis, firmware pentest, EDR bypass, CTF, mobile, pentest toolchain, LLM/API security, and more.

**Why it's useful:**
- **Router-first design** — a `reverse-skill-router` skill reads the task, picks the PRIMARY module, and enforces the authorization contract (authorized-use only)
- **Self-evolving** — each task writes lessons to `field-journal/`, so the next similar target skips trial-and-error
- **On-demand tool bootstrap** — missing jadx/frida/ghidra? The bootstrap manifest provisions it (commercial tools stay manual-license-only)
- **Cross-platform** — every helper ships as both PowerShell (`.ps1`) and POSIX shell (`.sh`) twins
- **85 skills, one install** — copy the whole pack, or cherry-pick individual modules (each has its own English trigger description)
- **Fully attributed** — a fork/port of the upstream project; deep reference content preserved verbatim (see the language note in `reverse-skill/README.md`)

**Trigger phrases:** *"analyze this APK" · "reverse this .NET binary" · "understand this stripped Go binary" · "route this security task"* — any RE/malware/pentest task

---

## 🧭 Which Skill Do I Use When?

| Situation | Skill |
|-----------|-------|
| "Audit this unfamiliar codebase for bugs" | 🔧 `app-debug-workflow` |
| "Run this complex project end-to-end" | 🏗️ `complex-project-workflow` |
| "Read / summarize this URL" | 🌐 `web_extract` |
| "Search for / look up / find out X" | 🔎 `web_search` |
| Research project needing both search + extraction | 🔎 `web_search` → 🌐 `web_extract` |
| Project with a research phase | 🏗️ `complex-project-workflow` (Recon phase) |
| "Reverse / analyze this binary / APK / malware" | 🕵️ `reverse-skill` (router → specialist module) |

---

## ⚙️ How They Work Together

```
              ┌─────────────────────────────────┐
              │  complex-project-workflow       │
              │  (the master engine)            │
              │  Charter → Recon → Blueprint →  │
              │  Review → Execute → Assemble →  │
              │  Retrospect                     │
              └──────┬──────────────┬───────────┘
                     │              │
        Recon/Research phase   Execute phase
                     │              │
        ┌────────────▼───┐    ┌─────▼────────────┐
        │  web_search    │    │ app-debug-workflow│
        │  (find info)   │    │ (fix the code)    │
        └────────┬───────┘    └──────────────────┘
                 │
        ┌────────▼────────┐
        │  web_extract    │
        │  (read it fully)│
        └─────────────────┘
```

- **`complex-project-workflow`** is the **orchestrator** — it knows *when* each phase runs
- **`web_search` + `web_extract`** power the **research** phases (find → read)
- **`app-debug-workflow`** powers the **execute** phase when the project is a code audit/fix
- **`reverse-skill`** is the **security/RE specialist** — drop in any binary, APK, malware, or pentest target and let the router pick the right module
- All five share one principle: **hard rules, enforced systems, no drift**

---

## 🚀 Quick Start

### Install

Each skill is a self-contained folder. Copy the skill folder you want into your Hermes profile's skills directory:

```bash
# e.g. for the gf-helen profile on Windows:
cp -r app-debug-workflow ~/AppData/Local/hermes/profiles/gf-helen/skills/software-development/
cp -r complex-project-workflow ~/AppData/Local/hermes/profiles/gf-helen/skills/software-development/
cp -r web_extract ~/AppData/Local/hermes/profiles/gf-helen/skills/web/
cp -r web_search ~/AppData/Local/hermes/profiles/gf-helen/skills/web/
cp -r reverse-skill/skills ~/AppData/Local/hermes/profiles/gf-helen/skills/security/   # whole pack (85 skills + router)
```

### Configure

| Skill | Setup required |
|-------|----------------|
| `app-debug-workflow` | None — works out of the box |
| `complex-project-workflow` | None — works out of the box |
| `web_extract` | `pip install trafilatura` (optional but recommended) |
| `web_search` | API keys in profile `.env` (`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `TINYFISH_API_KEY`) + optional `pip install duckduckgo-search` |
| `reverse-skill` | None — works out of the box (tools auto-bootstrap on demand; optional MCP integrations are additive) |

### Verify

Trigger each skill with its phrase — e.g. ask the agent to *"search for X"* (web_search), *"read this URL"* (web_extract), *"audit this codebase"* (app-debug-workflow), *"run this as a master workflow"* (complex-project-workflow), or *"analyze this APK / reverse this binary"* (reverse-skill).

---

## 📁 Repository Structure

```
2026-0805-git Skill- Essential Hermes Skills/
├── README.md                    ← this file (bundle overview)
├── LICENSE                      ← MIT
├── app-debug-workflow/          ← 90-min disciplined codebase auditing
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── complex-project-workflow/    ← 7-phase master project engine
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── web_extract/                 ← tiered web-content extraction
│   ├── SKILL.md
│   └── README.md
├── web_search/                  ← tiered search (deepseek → tavily → tinyfish → ddgs)
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│       ├── search.py            ← dispatcher (auto tier chain)
│       ├── deepseek_search.py   ← tier 1: DeepSeek /responses web_search
│       ├── tavily_search.py     ← tier 2: Tavily API
│       ├── tinyfish_search.py   ← tier 3: TinyFish API
│       └── ddgs_search.py       ← tier 4: DuckDuckGo (no key)
└── reverse-skill/               ← 85-skill security & RE pack (Hermes port)
    ├── README.md                ← Hermes guide (front page) + language note
    ├── README-hermes.md         ← Hermes guide (duplicate, kept for visibility)
    ├── README-orignal.md        ← upstream README (preserved)
    ├── LICENSE                  ← upstream MIT (zhaoxuya520)
    ├── skills/                  ← 43 specialist modules + router + scripts
    ├── CTF-Sandbox-Orchestrator/← 42 CTF competition sub-skills
    └── kali/                    ← Kali Linux edition docs
```

---

## 🔍 Search Keywords

`Essential Hermes Skills` · `Hermes skills bundle` · `Hermes Agent skills` · `codebase audit skill` · `debug workflow agent` · `complex project workflow` · `master workflow agent` · `web search skill` · `tiered web search` · `web extraction skill` · `read any URL agent` · `Hermes agent skills pack` · `AI agent workflows` · `agentic debugging` · `production Hermes skills` · `Hermes skill collection` · `multi-phase project agent` · `duck-council audit` · `reverse-skill Hermes` · `reverse engineering skills` · `APK reverse Hermes` · `malware analysis skill` · `security skills Hermes` · `pentest skills agent`

---

## 📝 License

**MIT** — free to use, modify, and distribute. See [`LICENSE`](LICENSE).

---

<p align="center">
  <strong>Essential Hermes Skills — debug it, build it, search it, read it, reverse it. Every day.</strong><br>
  <sub>Hard rules. Enforced systems. No drift. 🧰</sub>
</p>
