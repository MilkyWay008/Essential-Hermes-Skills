---
name: web_extract
description: "general web content extraction: Jina Reader first (except X.com), trafilatura fallback (best for X.com), headless browser last resort. Use when asked to read/extract/fetch a URL's content."
version: 2.1.0
author: Ringo/MilkyWay008
metadata:
  hermes:
    tags: [web, extract, jina, trafilatura, url, fetch, read]
    related_skills: [search-this, web-interaction]
---

# web_extract — Web Content Extraction

**TRIGGER:** User gives a URL and asks to read, extract, fetch, summarize, or look up its content. Also triggers when a task needs page content (e.g. research, verification, data gathering).

**HARD RULE — Extraction Priority (in this order, no exceptions):**

```
Step 1: Jina Reader (r.jina.ai)   ← ALWAYS try first — EXCEPT x.com URLs
Step 2: trafilatura (Python)      ← when Jina fails/blocked; ALSO always used for x.com
Step 3: Headless browser          ← final fallback when both above fail
```

---

## When to use which (the golden rule)

| Site / Situation | Best tool |
|------------------|-----------|
| **X.com / Twitter** | **trafilatura FIRST** (Jina is frequently DDoS-blocked on x.com; trafilatura gets the raw HTML with the post text) |
| **JS-heavy sites** (grok.com, SPA apps, forums, dashboards) | **Jina Reader** (renders JS; trafilatura's static parse only gets the `<title>`) |
| **Normal article / blog / docs page** | Jina Reader (fast, clean markdown) |
| **Jina returns error/blocked/empty** | trafilatura next |
| **trafilatura returns nothing / title-only** | browser last |
| **Login-gated content** | browser only (both Jina + trafilatura fail behind auth) |

**The complementarity rule:** Jina is best for JS-heavy pages; trafilatura is best for X.com and anything Jina can't open — and things trafilatura can't open, Jina usually can. They cover each other's blind spots. Only when BOTH fail do you go to the browser.

---

## Method 1 — Jina Reader (default first choice)

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

---

## Method 2 — Trafilatura

Trafilatura is installed in the Hermes venv (`pip install trafilatura`) — importable from both `terminal` and `execute_code`. No path resolution needed.

### Usage — Method A: execute_code (PRIORITY — preferred)

✅ **Cleanest way** — no shell quoting, no path resolution, output comes back as a clean tool result:

```python
# execute_code — trafilatura is importable directly
import trafilatura
d = trafilatura.fetch_url('TARGET_URL')
print(trafilatura.extract(d))
```

**Why it's priority:** no shell quoting, no path resolution, output comes back as clean tool result. The sandbox already uses the Hermes venv Python.

---

### Usage — Method B: terminal (fallback)

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

### Practical tips

- **X.com:** trafilatura works great — the post text is in the raw HTML. This is the FIRST choice for x.com.
- **JS-heavy pages:** trafilatura often returns only the `<title>` (e.g. grok.com gave 71 chars = title only while the page was 468K). If extracted text is suspiciously short or title-only → the page is JS-rendered → use Jina (Method 1) or browser (Method 3).
- **When Jina is blocked:** trafilatura is the immediate fallback.
- **`trafilatura.exe` CLI is a broken trampoline** — ALWAYS use the Python API above, never the .exe.

---

## Method 3 — Headless Browser (final fallback)

If both Jina and trafilatura fail (login-gated, captcha, exotic JS, empty):

```python
browser_navigate(url)   # then read the returned snapshot
browser_snapshot()      # full accessibility tree if needed
```

- Always works for rendered content (it executes JS)
- Captures the accessibility tree — good enough for reading post text, comments, etc.
- Slower than the other two; use only when they fail.

---

## Verify extraction quality

After extracting, sanity-check the result:

- If output is only a title / nav text / "No content" → the real content is JS-rendered → try the OTHER tool (complementarity rule).
- If output contains the substantive content (article body, post text, guide steps) → done.

---

## First-Time Run & Install

The skill is ready to use once its folder exists — no build step and **no API keys required**. Jina Reader is free and anonymous, trafilatura ships in the Hermes venv, and the headless browser is built in. Two optional setup items make the agent prefer this skill automatically.

### 1. Optional: make sure `trafilatura` is installed

Trafilatura is already installed in the Hermes venv. If it's ever missing from a fresh environment:

```bash
python -m pip install trafilatura
```

### 2. SOUL.md Injection — make the agent prefer this skill

For the agent to **automatically use this skill instead of the built-in `web_extract` tool**, add a few lines to the profile's `SOUL.md` (e.g. `<profile>/SOUL.md`) under a suitable section (e.g. `## General Agent System prompt` or a new `## Web Extract` section). Reference injection (live in the gf-helen profile):

```markdown
## Web Extract
When performing a web extract, use the `web_extract` skill `skill_view(name='web_extract')` instead of the built-in web_extract tool, unless the user explicitly requests the built-in tool. Native `web_extract` requires an API-key backend (firecrawl/tavily/exa/parallel) unless the web-native plugin is present. When uncertain, load the extraction skill and follow its 3-tier fallback:

1. **Jina Reader first** (except X.com): `curl -sL "https://r.jina.ai/https://<URL>"`
   - Best for JS-heavy pages (grok.com, SPA apps, forums).
2. **trafilatura** when Jina fails/blocked — and ALWAYS first for X.com:
   `python -c "import trafilatura; print(trafilatura.extract(trafilatura.fetch_url('<URL>')))"`
   - Best for X.com and raw-HTML pages; bundled in the internal venv, no install.
3. **Headless browser** as last resort: `browser_navigate("<URL>")` then read the snapshot.

**Complementarity rule:** Jina is best for JS-heavy; trafilatura is best for X.com and anything Jina can't open — and things trafilatura can't open, Jina usually can.
```

> 💡 On a fresh install, you can simply tell your agent: *"Set up the web_extract skill: add the SOUL.md rule for me."* The agent will handle the rest (backups included).

### 3. Verify

```bash
curl -sL "https://r.jina.ai/https://example.com"
```

Expect clean markdown back (`Title:` / `URL Source:` / `Markdown Content:`). Or give the agent a URL and ask it to *read / extract / summarize* the page — it should load the skill and follow the 3-tier fallback.

---

## Known limitations

| Limitation | Workaround |
|------------|-----------|
| YouTube always 403 on Jina | Browser (or youtube-content skill) |
| X.com Jina DDoS block (usually < 24h) | trafilatura (works!) |
| JS-only pages: trafilatura gets title only | Jina Reader (renders JS) |
| Login-gated pages | Browser only |
| Binary files (PDF, images) | Not supported by Jina/trafilatura; use pdf skill or download |

---

## Related

- Search: use `search-this` skill (Tavily → TinyFish → Composio tiered priority)
- Browser interaction: `web-interaction` skill (built-in browser best practices)
- If this skill is missing a dependency, install via `python -m pip install trafilatura`
