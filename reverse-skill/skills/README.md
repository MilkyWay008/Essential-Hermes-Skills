# 🕵️ reverse-skill — Open Up Any Program and See What's Inside

> **Hermes Agent port of [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill)** (MIT, 24.4k⭐). Upstream READMEs, routing docs, and bilingual (EN/ZH) content preserved in this folder — this port adapts the skill pack to Hermes Agent conventions so every module loads as a first-class Hermes skill.

**In plain English:** software is a black box — you see what it *shows* you, not what it *does*. When a program breaks, won't start, acts suspicious, or hides its logic, reverse-skill gives your agent the tools to open the box: read the code inside apps, find out why they crash, see what they send over the internet, and judge whether they're safe to trust.

**Everyday examples of what this gets you:**

- **"This app won't open anymore."** A program (say, QuickBooks) crashes on launch and the error message says nothing useful. reverse-skill inspects the compiled code, finds the missing dependency or the corrupted check, and tells you exactly what broke — instead of guessing.
- **"Is this downloaded file safe?"** You grabbed something from a sketchy site. The malware-analysis module dissects it safely — what it does, where it's trying to phone home — without running it on your machine.
- **"Why can't I log in to this website?"** A login form sends encrypted parameters you can't reproduce in your own test script. The JS reverse module figures out how the signing works, so you can test your integration properly.
- **"Why is my app calling home?"** Suspicious network traffic from a tool you use? reverse-skill traces what it sends, where, and why.

**Why coders and IT pros need this in their job:**

- **Troubleshooting closed-source software** — when vendor code breaks and the error message lies, reverse engineering is how you find the truth instead of uninstalling and hoping
- **Security audits** — before you trust a tool, a dependency, or an app in your environment, you can verify what it actually does
- **Working with legacy or unknown code** — no source code? No problem. Read the compiled version
- **CTF and security careers** — this is the exact skill set security jobs are built on

## What's inside (the technical tour)

> **You are reading this from inside the installed pack.** Everything below is relative to this folder (`reverse-skill/` in your Hermes skills directory).

| Part | What it is |
|------|-----------|
| `SKILL.md` | The **router skill** (`reverse-skill-router`) — reads the task, picks the PRIMARY module, enforces the authorization contract |
| `<module>/` | 40 specialist modules — each a self-contained Hermes skill (`SKILL.md` + `references/` + `scripts/`) |
| `CTF-Sandbox-Orchestrator/` | 41 CTF competition sub-skills + a master orchestrator (42 skill files) |
| `config/routing.json` | 42 routing rules (R0–R41) — single source of truth for routing |
| `field-journal/` | Self-evolving knowledge base — lessons written back after each task |
| `scripts/` | Cross-platform helpers (`.ps1` + `.sh` twins): `master-route`, `case-init`, `bootstrap-reverse`, `smoke`, etc. |
| `ops/` | Operations contracts: scope, evidence chain, roles, identity, skill supply-chain |
| `tests/` | Routing benchmark (163 cases) and test scripts |
| `references/` | Shared cross-module references (e.g. community skills, domain coverage map) |

> **Note:** the pack repo also carries auxiliary dirs (`kali/`, `burp-mcp-full/`, `docs/`) that are **not** part of this installed folder — a few Kali-bootstrap scripts reference `kali/` and need it present if you use Kali (copy it from the repo into this folder).

## How it works

1. Task arrives → router (or the matching module's trigger) fires
2. Router reads `MASTER-ROUTING.md` / `config/routing.json` → picks PRIMARY module
3. Reads the PRIMARY module's `SKILL.md` → follows its workflow
4. Missing tools → `scripts/bootstrap-reverse` provisions from the manifest (JEB Pro stays manual-license-only)
5. After the task → lessons written to `field-journal/` → next similar task skips trial-and-error

## Requirements & safety

- **Authorized use only.** Every module enforces the authorization contract (scope file via `scripts/case-init`, no action on a target until auth is granted). The `RULES.md` gates are mandatory.
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

- **Upstream project:** [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) by zhaoxuya520 — MIT license (the upstream `LICENSE` lives at the repo root `reverse-skill/LICENSE`; subtree licenses that do ship inside this installed folder are listed below).
- **This port:** adaptations made for Hermes Agent conventions (frontmatter descriptions in English, router rewritten for Hermes' load-on-demand model, machine-specific references removed). All upstream docs, routing matrices, RULES, and module content preserved verbatim where possible — including the original Chinese in deep reference files, per the note above.
- Ported 2026-08-11. Star count referenced from upstream at port time.
- **Mixed licensing:** the overall pack is MIT (upstream `LICENSE`), but the `CTF-Sandbox-Orchestrator/` subtree ships under **GNU GPL v3** (its own `LICENSE`, preserved) and the `pentestswarm` CLI ships under **AGPL-3.0** (CLI-only).
