<p align="center">🌐 <b>web_extract</b> — Extract Any Web Page's Content, No Matter How Stubborn</p>

**The tiered web-content extraction skill for Hermes Agent: Jina Reader first (except X.com), trafilatura fallback (best for X.com), headless browser as the last resort — so every URL — article, blog, docs, JS-heavy SPA, forum, dashboard, or X.com post — gets read, extracted, fetched, summarized, or looked up successfully.**

![Type](https://img.shields.io/badge/Type-Skill-8A2BE2?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Terminal%20%2B%20Browser-4B0082?style=for-the-badge)
![Agent](https://img.shields.io/badge/Agent-Hermes-00ADD8?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.1.0-2ea44f?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Author:** Ringo/MilkyWay008 · **Version:** 2.1.0 · **Tags:** `web`, `extract`, `jina`, `trafilatura`, `url`, `fetch`, `read` · **Related skills:** [`search-this`](#), [`web-interaction`](#)

---

## 📑 Table of Contents

- [💡 What This Skill Does](#what-this-skill-does)
- [✨ Key Features](#key-features)
- [⚙️ How It Works — The 3-Tier Extraction Pipeline](#how-it-works--the-3-tier-extraction-pipeline)
- [🚀 Quick Start / How to Trigger](#quick-start--how-to-trigger)
- [📁 Files / Structure](#files--structure)
- [⚠️ Pitfalls & Gotchas](#pitfalls--gotchas)
- [🔍 Search Keywords](#search-keywords)
- [📝 Credits & License](#credits--license)

---

## 💡 What This Skill Does

`web_extract` is the general-purpose **web content extraction** skill for Hermes Agent. Whenever a URL needs to be turned into readable content — for reading, summarizing, research, verification, or data gathering — this skill picks the right extraction tool automatically, in a strict priority order, so you never stare at an empty page.

It chains **three extraction methods** with complementary blind spots:

| Priority | Tool | Best for |
|----------|------|----------|
| **1st** | **Jina Reader** (`r.jina.ai`) | JS-heavy sites, normal articles, blogs, docs — fast, clean markdown |
| **2nd** | **trafilatura** (Python) | **X.com / Twitter** (first choice there), and anything Jina can't open |
| **3rd** | **Headless browser** | Login-gated content, captchas, exotic JS, final fallback |

**The complementarity rule:** Jina is best for JS-heavy pages; trafilatura is best for X.com and anything Jina can't open — and things trafilatura can't open, Jina usually can. They cover each other's blind spots. Only when **BOTH** fail do you go to the browser.

---

## ✨ Key Features

- **⚡ Three-tier fallback pipeline** — Jina Reader → trafilatura → headless browser, with a hard, no-exceptions priority rule.
- **🐦 X.com/Twitter specialist** — trafilatura extracts post text straight from raw HTML; Jina is frequently DDoS-blocked on x.com, so trafilatura goes **first** there.
- **🖥️ JS-heavy site support** — Jina Reader renders JavaScript (grok.com, SPAs, forums, dashboards); trafilatura's static parse would only get the `<title>`.
- **🔑 Zero API keys** — Jina Reader is free and anonymous; trafilatura is pre-installed in the Hermes venv (`pip install trafilatura`), importable from both `terminal` and `execute_code`, with **no path resolution needed**.
- **🛡️ Prompt-injection resistant** — Jina strips prompt-injection from scraped content.
- **📝 Clean markdown output** — Jina returns `Title:`, `URL Source:`, `Markdown Content:`; trafilatura via `execute_code` returns a clean tool result with no shell-quoting headaches.
- **✅ Built-in quality verification** — sanity-check the extracted output and fall through to the *other* tool when only a title/nav text comes back.
- **🎯 Hardened with real-world quirks** — knows YouTube always 403s Jina, `trafilatura.exe` is a broken trampoline, and login-gated pages need the browser.

---

## ⚙️ How It Works — The 3-Tier Extraction Pipeline

**HARD RULE — Extraction Priority (in this order, no exceptions):**

```
Step 1: Jina Reader (r.jina.ai)   ← ALWAYS try first — EXCEPT x.com URLs
Step 2: trafilatura (Python)      ← when Jina fails/blocked; ALSO always used for x.com
Step 3: Headless browser          ← final fallback when both above fail
```

### When to use which (the golden rule)

| Site / Situation | Best tool |
|------------------|-----------|
| **X.com / Twitter** | **trafilatura FIRST** (Jina is frequently DDoS-blocked on x.com; trafilatura gets the raw HTML with the post text) |
| **JS-heavy sites** (grok.com, SPA apps, forums, dashboards) | **Jina Reader** (renders JS; trafilatura's static parse only gets the `<title>`) |
| **Normal article / blog / docs page** | Jina Reader (fast, clean markdown) |
| **Jina returns error/blocked/empty** | trafilatura next |
| **trafilatura returns nothing / title-only** | browser last |
| **Login-gated content** | browser only (both Jina + trafilatura fail behind auth) |

### Verify extraction quality

After extracting, sanity-check the result:

- If output is only a title / nav text / "No content" → the real content is JS-rendered → try the **OTHER** tool (complementarity rule).
- If output contains the substantive content (article body, post text, guide steps) → **done**.

---

## 🚀 Quick Start / How to Trigger

> **TRIGGER:** User gives a URL and asks to **read, extract, fetch, summarize, or look up** its content. Also triggers when a task needs page content (e.g. research, verification, data gathering).

### Method 1 — Jina Reader (default first choice)

```bash
curl -sL "https://r.jina.ai/https://TARGET_URL"
```

Run via `terminal`. Replace `TARGET_URL` with the full URL.

- Output is clean markdown: `Title:`, `URL Source:`, `Markdown Content:`
- **Free, no API key** (anonymous)
- Strips prompt-injection from scraped content
- **Do NOT retry Jina on YouTube** — always 403 (bot detection). Go straight to browser.
- **X.com** — skip Jina entirely (see Method 2). Jina's x.com block is usually temporary (< 24h on first access), but don't wait for it.
- Rate limits: if 429/451/403, wait a few seconds OR fall through to trafilatura immediately.

**Detecting failure:** Jina returns a JSON error like `{"code":403,"name":"AbuseAlleviationError",...}` or an HTTP error, or an empty/garbage body. If so → go to Method 2.

### Method 2 — Trafilatura

Trafilatura is installed in the Hermes venv (`pip install trafilatura`) — importable from both `terminal` and `execute_code`. No path resolution needed.

#### Usage — Method A: `execute_code` (PRIORITY — preferred)

✅ **Cleanest way** — no shell quoting, no path resolution, output comes back as a clean tool result:

```python
# execute_code — trafilatura is importable directly
import trafilatura
d = trafilatura.fetch_url('TARGET_URL')
print(trafilatura.extract(d))
```

**Why it's priority:** no shell quoting, no path resolution, output comes back as clean tool result. The sandbox already uses the Hermes venv Python.

#### Usage — Method B: `terminal` (fallback)

Use when `execute_code` is unavailable or the extraction is very long (avoid 50KB stdout cap in execute_code).

```bash
python -c "
import trafilatura
url = 'TARGET_URL'
downloaded = trafilatura.fetch_url(url)
print('Downloaded:', len(downloaded) if downloaded else 0, 'chars')
if downloaded:
    text = trafilatura.extract(downloaded)
    print(text)
"
```

**One-liner form (works from any cwd):**

```bash
python -c "import trafilatura; print(trafilatura.extract(trafilatura.fetch_url('TARGET_URL')))"
```

### Method 3 — Headless Browser (final fallback)

If both Jina and trafilatura fail (login-gated, captcha, exotic JS, empty):

```python
browser_navigate(url)   # then read the returned snapshot
browser_snapshot()      # full accessibility tree if needed
```

- Always works for rendered content (it executes JS)
- Captures the accessibility tree — good enough for reading post text, comments, etc.
- Slower than the other two; use only when they fail.

---

## 📁 Files / Structure

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill definition — extraction priority hard rule, golden-rule table, all three methods with verbatim commands, verification steps, known limitations, related skills |
| `README.md` | This human-friendly overview of the skill (you are here) |

> ℹ️ The skill is fully self-contained in `SKILL.md` — no scripts or references are shipped. If a dependency is missing, install it with:

```bash
python -m pip install trafilatura
```

---

## ⚠️ Pitfalls & Gotchas

- **YouTube → Jina is always 403** (bot detection). Do NOT retry — go straight to the browser.
- **X.com → skip Jina entirely.** Its x.com block is usually temporary (< 24h on first access), but don't wait for it — trafilatura works.
- **JS-only pages → trafilatura returns title only.** Example: grok.com gave 71 chars (= title only) while the page was 468K. If extracted text is suspiciously short or title-only → the page is JS-rendered → use Jina or the browser.
- **`trafilatura.exe` CLI is a broken trampoline** — ALWAYS use the Python API above, never the .exe.
- **Login-gated content** — both Jina and trafilatura fail behind auth; browser only.
- **Jina rate limits** — on 429/451/403, wait a few seconds or fall through to trafilatura immediately.
- **50KB stdout cap** — very long extractions via `execute_code` can hit it; use the `terminal` fallback instead.
- **Binary files (PDF, images)** — not supported by Jina/trafilatura; use the pdf skill or download the file.

### Known limitations

| Limitation | Workaround |
|------------|-----------|
| YouTube always 403 on Jina | Browser (or youtube-content skill) |
| X.com Jina DDoS block (usually < 24h) | trafilatura (works!) |
| JS-only pages: trafilatura gets title only | Jina Reader (renders JS) |
| Login-gated pages | Browser only |
| Binary files (PDF, images) | Not supported by Jina/trafilatura; use pdf skill or download |

---

## 🔍 Search Keywords

`web_extract`, `web extraction`, `extract URL`, `read URL`, `fetch URL`, `look up URL`, `summarize page`, `Jina Reader`, `r.jina.ai`, `trafilatura`, `headless browser`, `X.com extraction`, `Twitter extraction`, `JS-heavy sites`, `SPA scraping`, `login-gated content`, `curl extract`, `markdown from webpage`, `prompt injection stripping`, `youtube-content skill`, `search-this`, `web-interaction`, `Tavily`, `TinyFish`, `Composio`

---

## 📝 Credits & License

- **Author:** Ringo/MilkyWay008 · **Version:** 2.1.0
- **Tools used:** [Jina Reader](https://r.jina.ai) (free, keyless), [trafilatura](https://github.com/adbar/trafilatura) (Python, `pip install trafilatura`), Hermes built-in headless browser (`browser_navigate` / `browser_snapshot`)
- **Related skills:** `search-this` (Tavily → TinyFish → Composio tiered search priority) · `web-interaction` (built-in browser best practices)

Released under the **MIT License**. This skill is provided as-is — verify extracted content before relying on it.

---

<p align="center">🌐 <b>Jina first, trafilatura for X, browser as the last resort — every URL, every time.</b></p>
