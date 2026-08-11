# <p align="center">🧰 Essential Hermes Skills — The Power Bundle</p>

<p align="center">
  <strong>Five production-tested skills that turn Hermes Agent into a serious workhorse.</strong><br>
  Run any complex project. Open up any program. Debug any codebase. Search the web. Read any page.<br>
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

- **Execute** complex multi-phase projects without losing the thread
- **Reverse** — open up any program, find out why it breaks, and check whether it's safe
- **Debug** unfamiliar codebases with discipline, not chaos
- **Search** the web with a tiered fallback chain that never dead-ends
- **Extract** content from any page — even JavaScript-heavy SPAs

Each skill is **self-contained**, **production-tested**, and documented with its own README. Drop any of them into any Hermes profile and it just works.

> **The philosophy:** skills should be enforced *systems*, not suggestions. Every skill here encodes hard rules, triggers, and fallbacks — so the agent does the right thing without being reminded.

---

## 📦 The Five Skills

### 1. 🏗️ `complex-project-workflow` — The Master Project Engine

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

### 2. 🕵️ `reverse-skill` — Open Up Any Program and See What's Inside

**What it is (plain English):** software is a black box — you see what it *shows* you, not what it *does*. When a program breaks, won't start, acts suspicious, or hides its logic, reverse-skill gives your agent the tools to open the box: read the code inside apps, find out why they crash, see what they send over the internet, and judge whether they're safe to trust. An 85-skill pack ported from the popular [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) project (23.9k⭐).

**Everyday examples of what this gets you:**
- **"This app won't open anymore."** A program (say, QuickBooks) crashes on launch and the error message says nothing useful. reverse-skill inspects the compiled code, finds the missing dependency or corrupted check, and tells you exactly what broke — instead of guessing.
- **"Is this downloaded file safe?"** You grabbed something from a sketchy site. The malware-analysis module dissects it safely — what it does, where it's trying to phone home — without running it on your machine.
- **"Why can't I log in to this website?"** A login form sends encrypted parameters you can't reproduce in your own test script. The JS reverse module figures out how the signing works, so you can test your integration properly.
- **"Why is my app calling home?"** Suspicious network traffic from a tool you use? reverse-skill traces what it sends, where, and why.

**Why coders and IT pros need this in their job:**
- **Troubleshooting closed-source software** — when vendor code breaks and the error message lies, reverse engineering is how you find the truth instead of uninstalling and hoping
- **Security audits** — before you trust a tool, a dependency, or an app in your environment, you can verify what it actually does
- **Working with legacy or unknown code** — no source code? No problem. Read the compiled version
- **CTF and security careers** — this is the exact skill set security jobs are built on

**Under the hood (for the technically curious):**
- **Router-first design** — a `reverse-skill-router` skill reads the task, picks the PRIMARY module, and enforces the authorization contract (authorized-use only)
- **Self-evolving** — each task writes lessons to `field-journal/`, so the next similar target skips trial-and-error
- **On-demand tool bootstrap** — missing jadx/frida/ghidra? The bootstrap manifest provisions it (commercial tools stay manual-license-only)
- **Cross-platform** — every helper ships as both PowerShell (`.ps1`) and POSIX shell (`.sh`) twins
- **85 skills, one install** — copy the whole pack, or cherry-pick individual modules (each has its own English trigger description)
- **Fully attributed** — a fork/port of the upstream project; deep reference content preserved verbatim (see the language note in `reverse-skill/README.md`)

**Trigger phrases:** *"this app won't open" · "is this file safe" · "analyze this APK" · "reverse this .NET binary" · "why is this app calling home"* — any troubleshooting / security-audit / RE task

---

### 3. 🔧 `app-debug-workflow` — Disciplined Codebase Auditing

**What it is:** A 90-minute timeboxed, multi-session workflow for auditing an unfamiliar full-stack codebase — security, performance, reliability, and dev-tooling bugs.

**Why it's useful:**
- **Timeboxed by design** — 90 minutes, no rabbit holes, no scope creep
- **Session discipline** — Session A (debug, *no code*) then Session B (fix, *no planning*): you never break what you're analyzing
- **Multi-verifier gates** — rubber-duck and subagent audits before anything gets fixed
- **Complete pipeline** — discover → duck-verify → plan → handoff → fix → validate
- **25 documented pitfalls** — MSYS2 path bugs, venv isolation, patch backslashes, taskkill git-bash traps — learned the hard way, so you don't have to

**Trigger phrases:** *"codebase audit" · "security review" · "bug hunt" · "audit this unfamiliar codebase for bugs"*

---

### 4. 🔎 `web_search` — Tiered Search That Never Fails

**What it is:** A tiered web-search chain — **DeepSeek → Tavily → TinyFish → DuckDuckGo** — that replaces the built-in web_search tool with a richer, key-managed chain.

**Why it's useful:**
- **Best answer first** — DeepSeek sits at tier 1 because **deepseek-v4-flash (0731 build) natively supports the Responses API protocol**, which includes **native server-side search**: the model searches the web itself and synthesizes an actual *answer* in one call — no separate search round-trip, no raw link list to post-process
- **Raw results when you need them** — Tavily/TinyFish/DuckDuckGo for links, citations, and sources (effectively free)
- **Fail-fast fallthrough** — auto mode tries tier 1 → 2 → 3 → 4 and stops at the first success
- **Zero-key safety net** — DuckDuckGo needs no key, so the chain always has a last resort
- **Standalone by design** — scripts only need Python 3 stdlib; drop the folder into any profile or publish to GitHub as-is
- **SOUL.md injection** — teach the agent to prefer this skill over the built-in tool, automatically

**Trigger phrases:** any web search / online lookup / fact-check / research — *"Search for X" · "Look up Y" · "Find information about Z"*

---

### 5. 🌐 `web_extract` — Read Any Page, No Matter What

**What it is:** A tiered web-content extraction skill — Jina Reader first (except X.com), trafilatura fallback (best for X.com), headless browser as last resort.

**Why it's useful:**
- **Never dead-ends** — three fallback tiers mean almost any URL is readable: articles, docs, JS-heavy SPAs, X.com posts
- **Cost-aware** — free tiers first, expensive browser automation last
- **Verbatim code** — every method ships with copy-paste commands (curl, execute_code, browser_navigate)
- **Known-limitations table** — YouTube 403s, login-gated pages, 429/451/403, the 50KB stdout cap — documented up front

**Trigger phrases:** user gives a URL and asks to *read, extract, fetch, summarize, or look up* its content

---

## 🧭 Which Skill Do I Use When?

| Situation | Skill |
|-----------|-------|
| "Run this complex project end-to-end" | 🏗️ `complex-project-workflow` |
| "This app won't open / is this file safe / why is it calling home" | 🕵️ `reverse-skill` |
| "Audit this unfamiliar codebase for bugs" | 🔧 `app-debug-workflow` |
| "Search for / look up / find out X" | 🔎 `web_search` |
| "Read / summarize this URL" | 🌐 `web_extract` |
| Research project needing both search + extraction | 🔎 `web_search` → 🌐 `web_extract` |
| Project with a research phase | 🏗️ `complex-project-workflow` (Recon phase) |
| A code project that also involves closed-source or suspicious binaries | 🏗️ `complex-project-workflow` → 🕵️ `reverse-skill` |

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
        └────────┬───────┘    └─────┬────────────┘
                 │                  │
        ┌────────▼────────┐   ┌─────▼─────────────┐
        │  web_extract    │   │  reverse-skill    │
        │  (read it fully)│   │ (open any program)│
        └─────────────────┘   └───────────────────┘
```

- **`complex-project-workflow`** is the **orchestrator** — it knows *when* each phase runs
- **`web_search` + `web_extract`** power the **research** phases (find → read)
- **`app-debug-workflow`** powers the **execute** phase when the project is a code audit/fix
- **`reverse-skill`** is the **"what is this thing really doing?" specialist** — when the project hits a closed-source binary, a suspicious file, a crashing app, or a security audit, it opens the black box; it also feeds findings back into `complex-project-workflow`'s research phase
- All five share one principle: **hard rules, enforced systems, no drift**

---

## 🚀 Quick Start

### Install

Each skill is a self-contained folder. Copy the skill folder you want into your Hermes profile's skills directory (`~/.hermes/skills/` or your profile's skills dir):

```bash
# generic — works for any Hermes profile
cp -r complex-project-workflow ~/.hermes/skills/software-development/
cp -r reverse-skill/skills ~/.hermes/skills/security/            # whole pack (85 skills + router)
cp -r app-debug-workflow ~/.hermes/skills/software-development/
cp -r web_search ~/.hermes/skills/web/
cp -r web_extract ~/.hermes/skills/web/
```

### Configure

| Skill | Setup required |
|-------|----------------|
| `complex-project-workflow` | None — works out of the box |
| `reverse-skill` | None — works out of the box (tools auto-bootstrap on demand; optional MCP integrations are additive) |
| `app-debug-workflow` | None — works out of the box |
| `web_search` | API keys in profile `.env` (`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `TINYFISH_API_KEY`) + optional `pip install duckduckgo-search` |
| `web_extract` | `pip install trafilatura` (optional but recommended) |

### Verify

Trigger each skill with its phrase — e.g. ask the agent to *"run this as a master workflow"* (complex-project-workflow), *"this app won't open"* (reverse-skill), *"audit this codebase"* (app-debug-workflow), *"search for X"* (web_search), or *"read this URL"* (web_extract).

---

## 📁 Repository Structure

```
essential-hermes-skills/
├── README.md                    ← this file (bundle overview)
├── LICENSE                      ← MIT
├── complex-project-workflow/    ← 7-phase master project engine
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── reverse-skill/               ← 85-skill "open up any program" pack (Hermes port)
│   ├── README.md                ← Hermes guide (front page) + language note
│   ├── README-hermes.md         ← Hermes guide (duplicate, kept for visibility)
│   ├── README-orignal.md        ← upstream README (preserved)
│   ├── LICENSE                  ← upstream MIT (zhaoxuya520)
│   ├── skills/                  ← 43 specialist modules + router + scripts
│   ├── CTF-Sandbox-Orchestrator/← 42 CTF competition sub-skills
│   └── kali/                    ← Kali Linux edition docs
├── app-debug-workflow/          ← 90-min disciplined codebase auditing
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── web_search/                  ← tiered search (deepseek → tavily → tinyfish → ddgs)
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│       ├── search.py            ← dispatcher (auto tier chain)
│       ├── deepseek_search.py   ← tier 1: DeepSeek /responses web_search
│       ├── tavily_search.py     ← tier 2: Tavily API
│       ├── tinyfish_search.py   ← tier 3: TinyFish API
│       └── ddgs_search.py       ← tier 4: DuckDuckGo (no key)
└── web_extract/                 ← tiered web-content extraction
    ├── SKILL.md
    └── README.md
```

---

## 🔍 Search Keywords

`Essential Hermes Skills` · `Hermes skills bundle` · `Hermes Agent skills` · `complex project workflow` · `master workflow agent` · `reverse-skill Hermes` · `reverse engineering skills` · `APK reverse Hermes` · `malware analysis skill` · `security skills Hermes` · `pentest skills agent` · `codebase audit skill` · `debug workflow agent` · `web search skill` · `tiered web search` · `web extraction skill` · `read any URL agent` · `Hermes agent skills pack` · `AI agent workflows` · `agentic debugging` · `production Hermes skills` · `Hermes skill collection` · `multi-phase project agent` · `duck-council audit`

---

## 📝 License

**MIT** — free to use, modify, and distribute. See [`LICENSE`](LICENSE).

---

<p align="center">
  <strong>Essential Hermes Skills — run it, open it, debug it, search it, read it. Every day.</strong><br>
  <sub>Hard rules. Enforced systems. No drift. 🧰</sub>
</p>
