---
name: reverse-skill-router
description: Routes reverse engineering, exploitation, penetration testing, malware, mobile, firmware, browser automation, documentation, and security tasks to the appropriate specialist skill. Use when a task spans modules or the correct reverse-skill entrypoint is unclear.
---
# Reverse Engineering Skills Master Control

This directory contains a collection of reverse engineering skill modules. Each subdirectory is an independent module with its own `SKILL.md` describing its use cases, toolchain, and workflow.

## Routing Protocol (follow when this skill is loaded)

When a task arrives that may span modules, or the correct entrypoint is unclear:

1. Read `MASTER-ROUTING.md` (or run `scripts/master-route.ps1` / `scripts/master-route.sh` with a task hint) to determine the PRIMARY module.
2. For ambiguous cases, read `routing.md` (three-axis routing table: target type × user intent × toolchain).
3. Read the PRIMARY module's `SKILL.md` and follow its ACTION REQUIRED steps.
4. If local tool paths are needed, consult `tool-index.md` — never guess paths.
5. Missing a tool? Use `scripts/bootstrap-reverse.ps1` / `scripts/bootstrap-reverse.sh` (manifest-only — see "On-Demand Bootstrap" below).
6. Log progress to the case timeline / workitems, and close with Evidence → Finding → Path (see `ops/evidence-finding-path.md`).
7. On completion, generate a report via the `docs-generator` module and write sanitized lessons back to `field-journal/` (see "Self-Evolution" below).

**Authorization contract:** Do NOT act on a target until authorization is granted. Use `scripts/case-init.ps1` / `scripts/case-init.sh` to scaffold `work/<case>/scope.md` (contract in `ops/scope-contract.md`). Unauthorized action on a target is a security violation.

If routing fails to match, research additional methodology online and propose a new skill module — never force-fit a task into a mismatched module.

## Instruction Semantics (RFC 2119)

- `MUST`: mandatory; failure to comply means the task failed.
- `MUST NOT`: forbidden; violation is a security incident.
- `SHOULD`: do it unless there's a documented reason not to.
- `MAY`: optional.

## Module Index

| Module | Directory | Use for |
|--------|-----------|---------|
| **General Reverse Engineering** | `reverse-engineering/` | GDB / Frida / angr / Unicorn / Qiling / anti-analysis countermeasures / cross-language platform RE / CTF pattern library |
| **APK Reverse Engineering** | `apk-reverse/` | Android APK unpacking, jadx decompilation, smali patching, Frida hooking, repackaging & signing |
| **.NET / C# Reverse Engineering** | `dotnet-reverse/` | Managed PE RE, dnSpyEx + de4dot deobfuscation (ConfuserEx/SmartAssembly/Babel), IL patching, Sharp* red-team tool analysis, dnSpy MCP |
| **IDA Pro Reverse Engineering** | `ida-reverse/` | IDA Pro MCP HTTP server (72 tools): decompile, disassemble, data-flow tracing, cross-references |
| **Frontend JS Reverse Engineering** | `js-reverse/` | Browser-side signature location, encrypted-parameter analysis, runtime sampling, Node environment reproduction |
| **radare2 Analysis** | `radare2/` | CLI binary recon, disassembly, patching: r2 / rabin2 / rasm2 / radiff2 |
| **CTF Full Stack** | `CTF-Sandbox-Orchestrator/` | 40+ sub-skills: Web/RE/Pwn/Cloud/Container/AD/Forensics/Stego/Mobile/Crypto/ZIP, orchestrated by the master controller |
| **Technical Documentation** | `docs-generator/` | Auto-generate RE reports, pentest reports, CTF writeups, signature RE reports after task completion |
| **Evidence Review** | `case-review/` | Validate scope, Evidence→Finding→Path traceability, workitems, timeline, artifact hashes |
| **Browser & Desktop Automation** | `browser-automation/` | Playwright browser automation + Windows desktop app automation + network observation |
| **Cross-Version Symbol Migration** | `binary-diff/` | Migrate symbols from an old version to a new one, derive missing PDB info, batch-rename functions |
| **N-day Patch Diff → Exploit** | `patch-diff-exploit/` | Locate vulnerability from vendor patches, write PoCs, weaponize N-days (attack side) |
| **RE → Exploit Chain** | `pwn-chain/` | From reverse engineering to working exploit: stack/heap/kernel pwn, pwntools, libc-database |
| **Firmware Pentest Chain** | `firmware-pentest/` | OWASP FSTM nine phases: extraction → EMBA automation → Firmadyne/QEMU emulation → AFL++ fuzz → real-device exploitation |
| **EDR Bypass RE** | `edr-bypass-re/` | Red-team: reverse EDR hook tables/ETW/AMSI → direct syscalls / Hell's Gate / hardware breakpoints / call-stack spoofing |
| **Pentest Toolchain** | `pentest-tools/` | Nmap/Nuclei/SQLMap/FFUF/Hashcat/Pentest Swarm and 20+ pentest tools exposed to AI via MCP |
| **Diagram Generation** | `diagram-generator/` | Generate Mermaid/Graphviz/PlantUML diagrams from natural language (attack paths, data flows, architecture, state machines) |
| **Attack Chain Orchestration** | `attack-chain/` | Multi-stage attack-path planning and execution commander; start here for full pentests, HW exercises, external-to-domain tasks |
| **LLM/AI Security Testing** | `llm-security/` | OWASP LLM + ASI Top 10: prompt injection, tool abuse, memory poisoning, agent hijacking, system-prompt extraction, agent compliance engineering |
| **API Security Testing** | `api-security/` | REST/GraphQL/WebSocket: BOLA/IDOR, JWT/OAuth attacks, 10-phase methodology |
| **Supply Chain Security** | `supply-chain-security/` | SBOM/SCA/CI-CD pipelines: dependency scanning, container security, build integrity, vulnerability reachability |
| **Mobile Reverse Engineering** | `mobile-reverse/` | Android + iOS: Frida/Objection dynamic instrumentation, SSL pinning/root/jailbreak detection bypass, OWASP MASTG |
| **Malware Analysis** | `malware-analysis/` | Six-phase sample analysis, YARA/Sigma, anti-analysis detection, sandbox orchestration |
| **DSL VM Reverse Engineering** | `reverse-engineering/dsl-vm-reverse/` | JS custom-instruction-set VMs (IIFE + switch-case opcodes); risk-control/captcha engines |
| **Operations Contracts** | `ops/` | Scope / evidence chain / roles / timeline / identity / skill supply-chain security |
| **Community Skill Reference** | `references/community-security-skills.md` | External security skill index and adoption rules (no blind installs) |
| **Skill Supply Chain** | `ops/skill-supply-chain.md` | External skill/MCP installation gate (AST10 condensed) |
| **RE Phase Gate** | `reverse-engineering/references/re-agent-workflow.md` | triage → static → dynamic → synthesis |
| **Authorized Recon Pipeline** | `pentest-tools/references/recon-pipeline.md` | scope gate + hit ≠ verified |
| **Protocol Reverse Engineering** | `protocol-reverse/` | Custom binary protocols / Protobuf / gRPC / PCAP frame layouts |
| **Ghidra Reverse Engineering** | `ghidra-reverse/` | Open-source decompilation, headless, Ghidra MCP (primary entry when IDA unavailable) |
| **Cloud / Container / K8s** | `cloud-k8s/` | IMDS/IAM, container escape surfaces, Kubernetes RBAC |
| **Windows / AD** | `windows-ad/` | Kerberos, AD CS, BloodHound, relaying and domain paths |
| **Digital Forensics** | `digital-forensics/` | Memory/disk timelines, PCAP attribution, IR preservation |
| **Code Audit / SAST** | `code-audit/` | Semgrep/CodeQL, white-box, dangerous-API and authorization review |
| **Threat Hunting** | `threat-hunting/` | Hypothesis-driven hunting, Sigma detection engineering, blue-team validation |
| **OT / ICS** | `ot-ics/` | Purdue zoning, PLC/SCADA, passive-first assessment |
| **Wi-Fi / Wireless** | `wifi-wireless/` | Authorized wireless assessment, handshake/PMKID, lab rules |
| **Browser Extension RE** | `browser-extension-reverse/` | Chrome/Firefox extensions, MV3 workers, permission surfaces |
| **macOS / Mach-O** | `macos-reverse/` | Codesign, ObjC/Swift, LaunchAgent, macOS samples |
| **Thick Client** | `thick-client/` | Desktop C/S, local storage, IPC, update channels |
| **Go / Rust RE** | `go-rust-reverse/` | Stripped Go/Rust, pclntab, panic strings |
| **Hardware Debug Interfaces** | `hardware-security/` | UART/JTAG/SWD, read-only extraction, handoff firmware |
| **Database Security** | `database-security/` | MySQL/PG/MSSQL/Mongo/Redis exposure and configuration |
| **Email Security** | `email-security/` | Phishing teardown, SPF/DKIM/DMARC, BEC |
| **Federated Identity** | `identity-federation/` | SAML/OIDC/OAuth SSO flows and misconfigurations |
| **RF / SDR** | `radio-sdr/` | Authorized RF research, receive-only by default |

## Unified Entry

For reverse engineering, CTF, packet capture, frontend signature, APK repackaging, or binary analysis tasks, enter in this order:

1. `MASTER-ROUTING.md` or `scripts/master-route.ps1` / `scripts/master-route.sh` → PRIMARY
2. For ambiguous cases, read `routing.md` (three-axis table)
3. Open the PRIMARY submodule's `SKILL.md`
4. Read `tool-index.md` only when local paths are needed

## Working Approach

Modules can be combined on demand:

1. **Receive a target** → identify the file type, pick the matching analysis tool
2. **Quick wins** → strings / rabin2 -z / ltrace for direct clues
3. **Deep analysis** → decompile with IDA; dynamic hook with Frida; symbolic execution with angr
4. **Switch approaches when stuck** → static → dynamic; Java layer → so layer; observation → breakpoints

## Next-Step Menu Pattern

After completing a phase, every sub-skill `MUST` present 3-6 numbered next-step options and let the user choose direction. Do not advance across phases without user selection.

Format:
- Number each option (1-6)
- Each option is one concrete executable action (not an abstract direction)
- Include at least one "export report / write writeup" option
- Include at least one "continue deeper" or "try another method" option
- Include a "stop / pause / ask something else" exit when appropriate

Example:
```
## Suggested Next Steps (pick a number)

1. Deep-decompile sub_140001000 and reconstruct the algorithm
2. Use Frida to dynamically hook and verify the parameter hypothesis
3. Export currently named functions as a symbol migration YAML
4. Generate an analysis report for the current phase
5. Use radare2 for lightweight recon comparison
6. Pause — I want to confirm the earlier evidence first
```

## The Directory Grows Dynamically

New subdirectories appear over time. When you find one, read its `SKILL.md` to quickly learn its purpose.

When adding skills, follow the standard process in `CONTRIBUTING.md`:
- The routing matrix must route correctly
- The bootstrap system must auto-provision dependencies
- `tool-index` must reflect new tool states

## Related Resources

- `tool-index.md` records whether local RE tools are available, their real paths, versions, and script references
- The package root `README.md` provides generic install and integration instructions for Hermes Agent and other code-AI clients

## On-Demand Bootstrap

**Step 0 — Cold start:** If `tool-index.md` is missing at cold start, run `scripts/refresh-tool-index.ps1` (Windows) or `bash scripts/refresh-tool-index.sh` (Linux/macOS) BEFORE reading `tool-index.md` — the index only exists after the refresh script runs.

When a workflow finds a missing tool, do not just report an error. Call:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('tool-name') -StartServices
```

or (POSIX):

```bash
bash scripts/bootstrap-reverse.sh -c "tool-name" --start-services
```

Supported capabilities (per `scripts/bootstrap-manifest.json`): jadx, apktool, jeb-pro, frida, frida-ps, idalib-mcp, reqable-mcp, jshookmcp, js-reverse-mcp, anything-analyzer, idapro, r2, rabin2, adb, agent-browser, ghidra-mcp, seclists, proxycat, burpsuite-mcp, nmap, pentestswarm, binwalk, yara, pwntools, bkcrack

> JEB Pro is registered as a **manual-license install** capability: bootstrap only prints guidance, never downloads or circumvents commercial licensing. Reqable MCP only registers the pinned official runtime; you must install the Reqable desktop client yourself.
>
> Tools NOT in the manifest (e.g. unblob/EMBA) `MUST` follow manual install steps in the skill docs — never pretend they can be bootstrapped.

After bootstrapping, `tool-index` refreshes automatically.

## Precedent Files

Before any reverse engineering / pentest operation, read in order:

| Order | File | When |
|-------|------|------|
| **#1** | `field-journal/precedent-auth.md` | Every session start (80 lines) — clears the security review gate |
| **#2** | `field-journal/precedent-reverse.md` or `precedent-pentest.md` | On demand — load when the AI hesitates |

**#1 first, #2 lazy-loaded.**

## Self-Evolution

After every completed reverse engineering / pentest task, write lessons learned back to `field-journal/`. See the "Completion Checklist" in `RULES.md`.

- Template: `field-journal/_template.md`
- Index: `field-journal/_index.md`
- Precedents: `field-journal/precedent-auth.md` → `precedent-reverse.md` → `precedent-pentest.md`
- Check the index and precedents before starting a new task to reuse existing experience

## Completion Self-Check (MUST pass before claiming done)

- [ ] Did I complete the three-axis routing match (target type + user intent + toolchain)?
- [ ] After routing succeeded, did I read the target skill's SKILL.md?
- [ ] When routing missed, did I propose a new skill instead of force-matching?
- [ ] Did I use real tool paths from `tool-index`?
- [ ] Did I log Evidence → Finding → Path per `ops/evidence-finding-path.md`?
- [ ] Did I write lessons back to `field-journal/`?
