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
2. `NOW`: Read `../tool-index.md` to verify tool availability and actual paths
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
# 1. 打开页面
agent-browser open <url>

# 2. 获取可交互元素（返回 @e1, @e2... 引用）
agent-browser snapshot -i

# 3. 用引用操作元素
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. 完成后关闭
agent-browser close
```

### Command Reference

```bash
# 导航
agent-browser open <url>
agent-browser close

# 页面快照
agent-browser snapshot        # 完整无障碍树
agent-browser snapshot -i     # 仅可交互元素（推荐）

# 交互操作
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser type @e2 "text"
agent-browser press Enter
agent-browser scroll down 500

# 获取信息
agent-browser get text @e1
agent-browser get title
agent-browser get url

# 等待
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
# 1. Clone 项目
git clone https://github.com/zhexulong/openreverse.git
cd openreverse

# 2. 安装依赖
npm install

# 3. Integrate with the agent host (Hermes Agent)
npm run init:agents -- --target=all /path/to/project

# 4. 安装 CUA runtime（如果需要视觉驱动模式）
npm run install:cua-runtime
npm run doctor:cua-runtime

# 5. 安装网络观察依赖（如果需要抓包）
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
场景：自动化操作 IDA Pro 进行批量分析

1. 用 OpenReverse CUA 模式打开 IDA Pro
2. 自动加载目标二进制
3. 等待分析完成
4. 通过 UI 操作导出函数列表
5. 同时用 network lane 观察 IDA 的网络行为（如 Lumina 请求）
```

```text
场景：自动化操作 x64dbg 调试

1. 用 OpenReverse UIA 模式启动 x64dbg
2. 加载目标程序
3. 设置断点
4. 运行并观察寄存器/内存变化
5. 截图保存证据
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

### Bootstrap Triggers

- Browser operations missing Playwright → auto bootstrap
- Desktop operations need OpenReverse → guide the user through manual install (give complete steps)

### OpenReverse Manual Install Guide

If the AI detects that desktop automation is needed but OpenReverse isn't installed:

```markdown
⚠️ **需要 OpenReverse 进行桌面应用自动化**

**安装步骤**：
1. `git clone https://github.com/zhexulong/openreverse.git`
2. `cd openreverse && npm install`
3. `npm run init:agents -- --target=all <你的项目路径>`
4. 如需视觉模式：`npm run install:cua-runtime`
5. 如需网络观察：`npm run install:mitmproxy`

**验证**：`npm run doctor:cua-runtime` 和 `npm run doctor:network`
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
