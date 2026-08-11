# 🕵️ reverse-skill — Hermes-Ready Cybersecurity Skills Router

> **Hermes Agent port of [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill)** (MIT, 23.9k⭐). Upstream READMEs, routing docs, and bilingual (EN/ZH) content preserved in this folder — this port adapts the skill pack to Hermes Agent conventions so every module loads as a first-class Hermes skill.

A collection of **85 security/RE skill modules** for reverse engineering, exploitation, penetration testing, malware analysis, mobile, firmware, browser automation, CTF, and security documentation — organized behind a routing skill that dispatches tasks to the right specialist module.

## What's inside

| Part | What it is |
|------|-----------|
| `skills/` | 43 specialist modules — each a self-contained Hermes skill (`SKILL.md` + `references/` + `scripts/`) |
| `CTF-Sandbox-Orchestrator/` | 42 CTF competition sub-skills orchestrated by a master controller |
| `skills/SKILL.md` | The **router skill** (`reverse-skill-router`) — reads the task, picks the PRIMARY module, enforces the authorization contract |
| `skills/config/routing.json` | 41 routing rules (R0–R40) — single source of truth for routing |
| `skills/field-journal/` | Self-evolving knowledge base — lessons written back after each task |
| `skills/scripts/` | Cross-platform helpers (`.ps1` + `.sh` twins): `master-route`, `case-init`, `bootstrap-reverse`, `smoke`, etc. |
| `kali/`, `burp-mcp-full/`, `docs/`, `examples/` | Auxiliary tooling and docs from upstream |

## Install into Hermes

### Option A — install individual modules (recommended)

Copy only the module folders you need into your Hermes profile's skills directory:

```bash
# generic — replace <profile> with your Hermes profile name
cp -r skills/apk-reverse ~/.hermes/skills/            # or your profile skills dir
cp -r skills/ida-reverse ~/.hermes/skills/
cp -r skills/malware-analysis ~/.hermes/skills/
```

Each module loads as a standalone skill with its own trigger description. No router required for single-module use.

### Option B — install the whole pack (router + all modules)

Copy the entire `skills/` content into your skills directory:

```bash
cp -r skills/* ~/.hermes/skills/
```

This installs the `reverse-skill-router` (which dispatches across modules) plus all 43 specialist skills. The router fires when a task spans modules or the entrypoint is unclear.

### Verify

After install, trigger any module by name — e.g. ask the agent to *"analyze this APK"* (apk-reverse), *"reverse this .NET binary"* (dotnet-reverse), *"help me understand this stripped Go binary"* (go-rust-reverse), or *"route this security task"* (reverse-skill-router). The skill's frontmatter description is the trigger.

## How it works

1. Task arrives → router (or the matching module's trigger) fires
2. Router reads `MASTER-ROUTING.md` / `routing.json` → picks PRIMARY module
3. Reads the PRIMARY module's `SKILL.md` → follows its workflow
4. Missing tools → `bootstrap-reverse` provisions from the manifest (JEB Pro stays manual-license-only)
5. After the task → lessons written to `field-journal/` → next similar task skips trial-and-error

## Requirements & safety

- **Authorized use only.** Every module enforces the authorization contract (scope file via `case-init`, no action on a target until auth is granted). The router's `RULES.md` gates are mandatory.
- **No mandatory API keys.** Most modules work with freely available tools (jadx, Ghidra, radare2, Frida, pwntools…). Optional MCP integrations (IDA MCP, Ghidra MCP, BurpSuite MCP, jshookmcp) are additive, never required.
- **Cross-platform.** Helpers ship as both PowerShell (`.ps1`) and POSIX shell (`.sh`) twins; docs cover Windows, Linux, and macOS.
- **Commercial tools** (IDA Pro, JEB Pro, BurpSuite) are referenced but never downloaded or license-circumvented by the bootstrap.

## 🌐 Language note — why some files are still in Chinese

The **skill surface is fully English**: every module's `SKILL.md` (the file Hermes indexes, triggers on, and loads), the router, and all frontmatter descriptions were translated as part of this port.

However, **the deep reference files remain in their original language** — many `references/` docs, the `src-hunter/payloader/` attack libraries, `field-journal/` case studies, and several top-level docs (`AGENTS.md`, `RULES.md`, `CONTRIBUTING.md`, `MASTER-ROUTING.md`, `routing.md`) contain Chinese.

> **That Chinese is NOT ours — it comes from the upstream project.** This folder is a fork/port of [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill), and we deliberately preserved the deep reference content **verbatim** to keep the knowledge base intact. We translated the Hermes-facing layer (skill triggers, descriptions, router, workflow headers) and left the deep content as upstream wrote it — both because the payloads/commands inside are language-neutral, and because wholesale translation would risk corrupting a battle-tested library.
>
> If you need the Chinese reference material translated, refer to the upstream project, or translate on-demand when a skill loads it.

## Attribution & license

- **Upstream project:** [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) by zhaoxuya520 — MIT license, kept in this folder (`LICENSE`).
- **This port:** adaptations made for Hermes Agent conventions (frontmatter descriptions in English, router rewritten for Hermes' load-on-demand model, machine-specific references removed). All upstream docs, routing matrices, RULES, and module content preserved verbatim where possible — including the original Chinese in deep reference files, per the note above.
- Ported 2026-08-11. Star count referenced from upstream at port time.
