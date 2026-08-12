# 🕵️ reverse-skill — Open Up Any Program and See What's Inside

> **Hermes Agent port of [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill)** (MIT, 23.9k⭐). Upstream READMEs, routing docs, and bilingual (EN/ZH) content preserved in this folder — this port adapts the skill pack to Hermes Agent conventions so every module loads as a first-class Hermes skill.

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

| Part | What it is |
|------|-----------|
| `skills/` | The whole pack — the router, 43 specialist modules, and the nested CTF collection |
| `skills/SKILL.md` | The **router skill** (`reverse-skill-router`) — reads the task, picks the PRIMARY module, enforces the authorization contract |
| `skills/<module>/` | 43 specialist modules — each a self-contained Hermes skill (`SKILL.md` + `references/` + `scripts/`) |
| `skills/CTF-Sandbox-Orchestrator/` | 42 CTF competition sub-skills orchestrated by a master controller |
| `skills/config/routing.json` | 41 routing rules (R0–R40) — single source of truth for routing |
| `skills/field-journal/` | Self-evolving knowledge base — lessons written back after each task |
| `skills/scripts/` | Cross-platform helpers (`.ps1` + `.sh` twins): `master-route`, `case-init`, `bootstrap-reverse`, `smoke`, etc. |
| `kali/`, `burp-mcp-full/`, `docs/`, `examples/` | Auxiliary tooling and docs from upstream |

## Install into Hermes

### Option A — install the whole pack as one folder (recommended)

Copy the entire `skills/` folder into your Hermes skills directory as a **single folder named `reverse-skill`**:

```bash
# Hermes sees one clean entry: ~/.hermes/skills/reverse-skill/
# (includes the router, all 43 RE/security modules, and the 42 CTF sub-skills)
cp -r skills ~/.hermes/skills/reverse-skill/
```

That's it — one command. The folder contains the `SKILL.md` router (the pack's entry point), all 43 specialist modules, and the nested `CTF-Sandbox-Orchestrator/` (42 competition sub-skills + its own master orchestrator). Hermes groups everything under `reverse-skill/` — one tidy folder, not 44 folders scattered in your skills root. The router fires when a task spans modules or the entrypoint is unclear; individual modules also fire on their own triggers (e.g. *"analyze this APK"* → `apk-reverse`).

> **Why one command now?** The CTF collection lives *inside* `skills/` in this port, and every module references the pack's shared scaffolding (`scripts/`, `ops/`, `field-journal/`, `tool-index.md`) via relative paths — so the whole pack must stay together. Partial installs (copying a few modules) break those relative references; that's why cherry-picking is not offered. If you want fewer visible skills, use Option B instead.
>
> ⚠️ **Note:** Option A installs only `skills/`. The auxiliary dirs (`kali/`, `burp-mcp-full/`, `docs/`, `examples/`) are **not** copied — Kali auto-bootstrap scripts inside a few modules reference `kali/` and will need it present if you use Kali; copy it too with `cp -r skills kali burp-mcp-full docs ~/.hermes/skills/reverse-skill/` when needed.

### Option B — install the whole pack, then hide the long-tail

Same folder install as Option A, then disable the rarely-used modules so they don't clutter the Hermes skill index:

```bash
cp -r skills ~/.hermes/skills/reverse-skill/
```

Then in your Hermes `config.yaml`, add the modules you don't need day-to-day:

```yaml
skills:
  disabled:
    - radio-sdr
    - ot-ics
    - hardware-security
    - competition-web-runtime
    # ... add any module you rarely reach for
```

Disabled skills are hidden from the index and skill list, but their files stay on disk — a skill librarian (or `read_file` on the module's `SKILL.md` path) can still find them when a task actually needs them. Best of both worlds: a clean index, with the full pack one `read_file` away.

> **Hidden ≠ unreachable through the router.** The router dispatches by **file path**, not through the skill index — it reads `MASTER-ROUTING.md`, `routing.json`, and each module's `SKILL.md` directly from disk. So a module you disabled is still fully reachable whenever the router routes to it; disabling only removes it from the skill index, never from the pack's routing.

### Verify

After install, trigger any module by name — e.g. ask the agent to *"analyze this APK"* (apk-reverse), *"reverse this .NET binary"* (dotnet-reverse), *"help me understand this stripped Go binary"* (go-rust-reverse), or *"route this security task"* (reverse-skill-router). The skill's frontmatter description is the trigger.

### 🚀 Optional power-up — install the jshookmcp MCP server

Want the whole toolkit to hit its automation ceiling? Register **[jshookmcp](https://github.com/vmoranv/jshookmcp)** as an MCP server in Hermes. It adds 134+ tools spanning browser automation / CDP debugging, JS hooking & deobfuscation, Frida memory forensics, WASM reversing, and source-map reconstruction — and the agent can use them across every module that touches web/JS/mobile targets.

It **especially boosts the 7 src-hunter playbooks** that carry `mcp__jshook__*` tool tables (`api-rest`, `file-upload`, `mobile`, `oauth-saml-jwt`, `rce`, `ssrf-cache-host`, `xss`): with jshookmcp registered, those playbooks' automation sections go fully live instead of falling back to native `browser_*` / curl / Python.

```bash
# install per the project README, then register in Hermes config.yaml:
# mcp_servers:
#   jshook:
#     command: <path to jshookmcp>
```

**Not required** — every module works without it (the 7 playbooks note their fallback inline), so the pack stays self-sufficient on any machine. Install it when you want the full power; the agent will also mention this upgrade on its own when a task clearly benefits. Details: `skills/pentest-tools/src-hunter/references/tools/mcp-jshook.md` → *Install & Upgrade Path*.

## Packaging a release (zip/tar)

Always build distribution archives from **git-tracked files** — never `zip -r` the working tree. The working tree contains untracked junk that must never ship: `reports/` (un-desensitized pentest samples — anti-leak policy), `.trash/`, and `*.bak` backups. Use the bundled scripts:

```bash
bash skills/scripts/zip-dist.sh              # -> ../reverse-skill-dist.zip (or .tar.gz if zip missing)
powershell -File skills/scripts/zip-dist.ps1 # -> <repo>/reverse-skill-dist.zip
```

Both build from `git ls-files` only, so the junk is excluded by construction. The archive contains the pack as a `reverse-skill/` folder (same layout as the repo). If you deliberately want the sample CTF report in the archive, copy it in manually.

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
- **Mixed licensing:** the overall pack is MIT (upstream `LICENSE`), but the `CTF-Sandbox-Orchestrator/` subtree ships under **GNU GPL v3** (its own `LICENSE`, preserved from upstream) — respect GPLv3 terms when redistributing that subtree. Bootstrap-installed `pentestswarm` is AGPL-3.0 (CLI invocation only; no source vendored).
