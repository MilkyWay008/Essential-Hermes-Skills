---
name: browser-automation
description: >-
  Unified automation entrypoint. Covers browser automation (Playwright) and Windows desktop app automation
  (OpenReverse). Browser scenarios: open pages, click, fill forms, scrape, network observation. Desktop
  scenarios: UIA/CUA-driven app control.
---

# Automation Operations (Desktop & Browser Automation)

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Confirm whether the current task falls within this skill's scope
2. `NOW`: Read `../tool-index.md` to verify tool availability and actual paths (if missing at cold start, run `scripts/refresh-tool-index.ps1` on Windows or `bash scripts/refresh-tool-index.sh` on Linux/macOS first)
3. `NEXT`: Call bootstrap when tools are missing; don't guess paths
4. `ACT`: Proceed to the first step of the "Workflow" and execute it; don't stop at the confirmation stage

## Scope

Use this skill when the task falls into the following scenarios:

### Browser Scenarios (Playwright / agent-browser)
- Open web pages and manipulate page elements (click, fill forms, submit)
- Scrape page content or take screenshots
- Automate login flows
- Interact with web pages during penetration testing (submit payloads, trigger XSS)
- Automated handling of CAPTCHA pages
- Batch form submission

### Desktop Application Scenarios (OpenReverse)
- Drive Windows desktop applications (IDA Pro, x64dbg, Wireshark, etc.)
- Need vision-driven interaction (CUA mode)
- Need structured UI operations (UIA mode)
- Network traffic observation for desktop apps (built-in mitmproxy)
- Automate GUI operations of reverse-engineering tools
- Black-box test desktop software

### Division of Labor with Other Tools

| Scenario | What to use |
|------|--------|
| Operate web pages (inside the browser) | **Playwright / agent-browser** |
| Operate desktop apps (Windows GUI) | **OpenReverse** |
| Packet capture analysis, HTTP request capture | anything-analyzer or OpenReverse network lane |
| JS breakpoints, hooks, CDP debugging | jshookmcp |
| Locate signing algorithms, environment-completion reproduction | js-reverse |

Quick decision:
- Target is a web page → Playwright
- Target is a Windows desktop app → OpenReverse
- Both are needed → combine them

---

## Part 1: Browser Automation (Playwright / agent-browser)

### Core Workflow

```bash
# 1. Open a page
agent-browser open <url>

# 2. Get interactive elements (returns @e1, @e2... references)
agent-browser snapshot -i

# 3. Operate elements using references
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. Close when finished
agent-browser close
```

### Command Reference

```bash
# Navigation
agent-browser open <url>
agent-browser close

# Page snapshot
agent-browser snapshot        # full accessibility tree
agent-browser snapshot -i     # interactive elements only (recommended)

# Interactions
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser type @e2 "text"
agent-browser press Enter
agent-browser scroll down 500

# Get information
agent-browser get text @e1
agent-browser get title
agent-browser get url

# Waiting
agent-browser wait @e1
agent-browser wait 2000
agent-browser wait --load networkidle
```

### Notes
- MUST run `agent-browser close`, otherwise the process leaks
- snapshot before acting; don't guess element references
- After submitting a form, use `wait --load networkidle` to let the page settle

---

## Part 2: Desktop Application Automation (OpenReverse)

### Overview

[OpenReverse](https://github.com/zhexulong/openreverse) is a desktop interaction and evidence-collection framework for AI agents. It supports:
- **UIA mode**: Windows UI Automation, structured desktop control operations
- **CUA mode**: vision-driven interaction (Computer Use Agent), suited to complex GUIs
- **Network observation**: built-in mitmproxy proxy + local capture

### Interaction Mode Selection

| Mode | Suitable for | Underlying |
|------|---------|------|
| UIA | Target app has standard Windows controls (buttons, text boxes, lists) | Windows UI Automation API |
| CUA | Target app UI is complex or uses non-standard controls (IDA's disassembly view, custom-rendered interfaces) | vision recognition + mouse/keyboard |

### Network Observation Modes

| Mode | Suitable for |
|------|---------|
| Proxy Lane | Target app can be configured with a proxy (recommended) |
| Local Lane | Target app cannot use a proxy; needs local capture |

### Installation & Configuration

```bash
# 1. Clone the project
git clone https://github.com/zhexulong/openreverse.git
cd openreverse

# 2. Install dependencies
npm install

# 3. Integrate with the agent host (Hermes Agent)
npm run init:agents -- --target=all /path/to/project

# 4. Install the CUA runtime (only if you need vision-driven mode)
npm run install:cua-runtime
npm run doctor:cua-runtime

# 5. Install network observation dependencies (only if you need packet capture)
npm run install:mitmproxy
npm run doctor:network
```

### Common Combinations

| Need | Configuration |
|------|------|
| Operate desktop apps only | UIA or CUA, no network lane |
| Operate desktop apps + packet capture | UIA/CUA + proxy lane |
| Operate desktop apps + local capture | UIA/CUA + local lane |

### Reverse-Engineering Scenario Examples

```text
Scenario: automate IDA Pro for batch analysis

1. Open IDA Pro with OpenReverse in CUA mode
2. Automatically load the target binary
3. Wait for analysis to complete
4. Export the function list through UI operations
5. Simultaneously observe IDA's network behavior with the network lane (e.g. Lumina requests)
```

```text
Scenario: automate x64dbg debugging

1. Launch x64dbg with OpenReverse in UIA mode
2. Load the target program
3. Set breakpoints
4. Run and observe register/memory changes
5. Take screenshots to preserve evidence
```

---

## On-Demand Bootstrap

### Automation Capability Boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| Playwright | ✓ | npm + npx playwright install | browser automation engine |
| agent-browser CLI | ✓ | npm install -g agent-browser | browser operations CLI |
| Node.js | ✓ | winget | prerequisite dependency |
| OpenReverse | ✗ | manual clone + npm install | experimental stage, heavy dependencies |
| mitmproxy | ✗ | manual install | OpenReverse network-observation dependency |

> **Hermes-native alternative**: Hermes agents have built-in browser tools (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`) that speak the same `@eN` ref model — you can complete browser scenarios with zero npm installs. Use agent-browser only when the native tools are unavailable.

### Bootstrap Triggers

- Browser operations missing Playwright → auto bootstrap
- Desktop operations need OpenReverse → guide the user through manual install (give complete steps)

### OpenReverse Manual Install Guide

If the AI detects that desktop automation is needed but OpenReverse isn't installed:

```markdown
⚠️ **OpenReverse required for desktop application automation**

**Installation steps**:
1. `git clone https://github.com/zhexulong/openreverse.git`
2. `cd openreverse && npm install`
3. `npm run init:agents -- --target=all <your project path>`
4. If you need vision mode: `npm run install:cua-runtime`
5. If you need network observation: `npm run install:mitmproxy`

**Verification**: `npm run doctor:cua-runtime` and `npm run doctor:network`
```

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Applicable to**: any task needing automated browser or desktop-app operations
**Downstream exits**:
- Captured requests need analysis → `anything-analyzer` or `js-reverse`
- Need JS debugging/hooking → `jshookmcp`
- Need to recover signing algorithms → `js-reverse`
- Desktop app is a reverse-engineering tool → `ida-reverse/`

**Peer modules**: `js-reverse` (may need to analyze JS after browser operations), `ida-reverse` (OpenReverse can automate IDA GUI operations)


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
