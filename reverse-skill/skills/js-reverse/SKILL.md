---
name: js-reverse
description: >-
  Use for frontend JavaScript reverse engineering via js-reverse-mcp: signature-chain localization, page
  observation forensics, runtime sampling, local environment reconstruction, and evidence-based output.
  Prefers js-reverse_* tools in the current environment; pairs with jshookmcp when a stronger
  browser/CDP/hook surface is needed.
---

# MCP Frontend JS Reverse Engineering Workflow Guide

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm the operations in this skill are authorized routine operations
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Move into the first step of the workflow and execute; do not stop at confirmation

## Scope

Use this skill first when the task falls into the following scenarios:

- Locating API signatures, encrypted parameters, and risk-control fields
- Observing page request chains and script origins
- Capturing function arguments and return values at runtime
- Tracing the trigger points of a specific XHR/Fetch/WebSocket
- Bringing page evidence back to Node for local reproduction and environment patching

If the target is a binary, APK, PE, ELF, DLL, or SO, use `ida-reverse`, `radare2`, or `reverse-engineering` instead.

## Default Tool Mapping in the Current Environment

This skill does not assume bare tool names exist; it defaults to binding the `js-reverse_*` tools available in the current client environment.

If the current task explicitly mentions `jshookmcp`, `JS hook`, `CDP`, browser breakpoints, network interception, SourceMap, or AST deobfuscation, still use this skill; just switch the underlying MCP surface to `jshookmcp` instead of treating it as a new master entry.

Prerequisite: `jshookmcp` is not a bare local command-line tool; it is an MCP server that must first be downloaded/registered/enabled. The related tool surface is only truly callable after it is connected and enabled in the Claude MCP configuration.

Common mappings:

- `list_scripts` -> `js-reverse_list_scripts`
- `get_script_source` -> `js-reverse_get_script_source`
- `search_in_sources` -> `js-reverse_search_in_sources`
- `break_on_xhr` -> `js-reverse_break_on_xhr`
- `evaluate_script` -> `js-reverse_evaluate_script`
- `get_paused_info` -> `js-reverse_get_paused_info`
- `set_breakpoint_on_text` -> `js-reverse_set_breakpoint_on_text`
- `list_network_requests` -> `js-reverse_list_network_requests`
- `get_request_initiator` -> `js-reverse_get_request_initiator`
- `get_websocket_messages` -> `js-reverse_get_websocket_messages`
- `take_screenshot` -> `js-reverse_take_screenshot`
- `new_page` -> `js-reverse_new_page`
- `navigate_page` -> `js-reverse_navigate_page`
- `select_page` -> `js-reverse_select_page`
- `select_frame` -> `js-reverse_select_frame`
- `pause/resume` -> `js-reverse_pause_or_resume`

If the tool name prefixes change in the future, update this section first; don't guess ad hoc during execution.

### jshookmcp's Role

- Role: an enhanced execution surface for `js-reverse`, not a standalone master controller
- Best for: browser automation, CDP debugging, JS hooking, network interception, SourceMap reconstruction, AST-assisted understanding
- Call prerequisite: download `@jshookmcp/jshook` and register it in the MCP client configuration first, then make sure the server is enabled
- Recommended entry: still follow `Observe → Capture → Rebuild`, only preferring jshookmcp's browser and hook capabilities during the `Observe/Capture` phases
- Relationship with anything-analyzer: both can do browser/network-side forensics; anything-analyzer leans toward packet capture and HTTP analysis, while jshookmcp leans toward the JS runtime, CDP, hooking, and source understanding

## Core Principles

- `Observe-first`
- `Hook-preferred`
- `Breakpoint-last`
- `Rebuild-oriented`
- `Evidence-first`

Observe the page first, then sample minimally, then patch the local environment — don't skip forensics and guess the environment directly.

## Five-Phase Workflow

### 1. Observe

Goal: confirm the target request, related scripts, and candidate functions first — no environment guessing.

Default actions:

- Open the target page with `js-reverse_new_page` or `js-reverse_navigate_page`
- Find the target request with `js-reverse_list_network_requests`
- Trace the call origin with `js-reverse_get_request_initiator`
- Narrow down the script set with `js-reverse_list_scripts` and `js-reverse_search_in_sources`

Must produce:

- The target request URL or its fingerprint
- Initiator leads
- Suspicious script URLs
- The initial task record

### 2. Capture

Goal: minimally invasive sampling of the target request to obtain parameter samples, call order, and runtime evidence.

Rules:

- Prefer `js-reverse_break_on_xhr`
- Prefer `js-reverse_evaluate_script` for lightweight runtime observation
- After a hit, first check `js-reverse_get_paused_info`
- Only use `js-reverse_set_breakpoint_on_text` when necessary

### 3. Rebuild

Goal: organize page evidence into locally iterable Node reproduction materials.

Rules:

- Local environment patching MUST be based on observed page evidence
- Do not patch `window/document/navigator/crypto/storage` out of thin air
- Record only one minimal causal patch decision at a time

### 4. Patch

Goal: drive environment patching by errors and the first divergence until the local script reliably produces the target parameters.

Rules:

- See what's missing first, then patch it
- One minimal patch decision at a time
- Retest immediately after each patch
- Record every patch in the task log

### 5. DeepDive

Goal: after the local run works, do deobfuscation, control-flow recovery, and business-logic distillation.

Rules:

- If the current task only needs the signature, this phase can be downgraded
- If the algorithm chain will be reused long-term, this phase MUST be done

## Execution Requirements

- All important steps MUST be written to a local task artifact
- If you can't explain why you're calling a tool, don't call it
- Prefer the ready-made MCP capabilities of `js-reverse_*` or jshookmcp for direct forensics; don't write scripts to reinvent capabilities first
- On failure, fall back per `references/fallbacks.md`
- Output follows `references/output-contract.md`

## Required Reading References

- Automation entry: `references/automation-entry.md`
- Parameter defaults: `references/tool-defaults.md`
- Task input template: `references/task-input-template.md`
- MCP-specific task orchestration: `references/mcp-task-template.md`
- Task artifacts: `references/task-artifacts.md`
- Local reproduction: `references/local-rebuild.md`
- Environment patching: `references/env-patching.md`
- Node reproduction: `references/node-env-rebuild.md`
- Instrumentation: `references/instrumentation.md`
- AST deobfuscation: `references/ast-deobfuscation.md`
- Fallbacks: `references/fallbacks.md`
- Output contract: `references/output-contract.md`

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternatives**:
- anything-analyzer MCP (port 23816) browser tools can serve as an alternative or supplement
- jshookmcp can serve as a stronger browser/CDP/Hook/Network/SourceMap/AST execution surface
- `reverse-engineering/SKILL.md` (if the target is not frontend JS)

**Downstream exits**:
- Environment patching needed → `references/env-patching.md`
- Local reproduction needed → `references/local-rebuild.md` / `references/node-env-rebuild.md`
- Deobfuscation needed → `references/ast-deobfuscation.md`
- Fall back when stuck → `references/fallbacks.md`

**Peer modules**: anything-analyzer MCP (browser automation and HTTP capture capabilities complement each other)

---

## On-Demand Bootstrap

The MCP capabilities this skill depends on can be auto-registered through the unified bootstrap system.

### Automation Capability Boundaries

| Capability | Auto-registrable | Method | Notes |
|------|-----------|------|------|
| jshookmcp | ✓ | npm-mcp (npx launch) | Automatically writes to the Claude MCP configuration |
| anything-analyzer | ✓ | local-http-mcp | Auto-registers + can auto-start the service |
| Node.js | ✓ | winget install | Runtime dependency |

### Bootstrap Method

```powershell
# 注册 jshookmcp 到 MCP 配置
powershell -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('jshookmcp')

# 注册并启动 anything-analyzer
powershell -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('anything-analyzer') -StartServices
```

### Notes

- After registering `jshookmcp`, you still need to **enable** that MCP server in the AI client before it can be called
- `anything-analyzer` needs pnpm and the project source; bootstrap auto-clones and installs dependencies
- If Node.js is not installed, bootstrap installs Node.js 22 via winget first

<br><br>## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than only reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
