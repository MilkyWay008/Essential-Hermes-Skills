# This Pack's Domain Coverage Map (depth-first)

> Versus the community's "hundreds of micro-skills": we cover the main battlefields with **a few deep skills + routing + ops**.  
> Date: 2026-07-18

## Domain -> Entry Point in This Pack

| Domain | PRIMARY / Module | Notes |
|----|----------------|------|
| Mobile Android | `apk-reverse/` `mobile-reverse/` | |
| Mobile iOS | `mobile-reverse/` | |
| Deep binary analysis | `ida-reverse/` `radare2/` `ghidra-reverse/` | Ghidra = primary open-source path |
| General RE / anti-debugging / OLLVM | `reverse-engineering/` | |
| .NET | `dotnet-reverse/` | |
| Frontend JS / signing | `js-reverse/` | |
| Browser extensions | `browser-extension-reverse/` | |
| DSL / risk-control VM | `reverse-engineering/dsl-vm-reverse/` | |
| Protocols / PCAP | `protocol-reverse/` | |
| Firmware IoT | `firmware-pentest/` | |
| Malware samples | `malware-analysis/` | |
| Digital forensics / IR | `digital-forensics/` | |
| Threat hunting / blue team | `threat-hunting/` | |
| Pentest tooling | `pentest-tools/` (+ src-hunter) | |
| Windows / AD | `windows-ad/` | |
| Cloud / containers / K8s | `cloud-k8s/` | |
| Code audit / SAST | `code-audit/` | |
| Wi-Fi / wireless | `wifi-wireless/` | |
| OT / ICS | `ot-ics/` | Passive-first; register writes forbidden by default |
| macOS | `macos-reverse/` | iOS still goes through mobile-reverse |
| Thick clients | `thick-client/` | |
| Go / Rust binaries | `go-rust-reverse/` | |
| Hardware debug ports | `hardware-security/` | Hands off to firmware-pentest |
| Databases | `database-security/` | |
| Email / phishing | `email-security/` | |
| Federated identity SSO | `identity-federation/` | Complements api-security JWT |
| RF / SDR | `radio-sdr/` | Receive-only by default; not Wi-Fi |
| Multi-stage attacks | `attack-chain/` | |
| Pwn | `pwn-chain/` | |
| N-day patches | `patch-diff-exploit/` | |
| EDR research | `edr-bypass-re/` | |
| API | `api-security/` | |
| Supply-chain SBOM | `supply-chain-security/` | |
| LLM/Agent | `llm-security/` | + `ops/skill-supply-chain.md` |
| Browser automation | `browser-automation/` | |
| Reports / diagrams | `docs-generator/` `diagram-generator/` | |
| Symbol migration | `binary-diff/` | |
| Operations contracts | `ops/` | **Differentiator** |
| CTF orchestration | `CTF-Sandbox-Orchestrator/` | |
| Crypto pattern recognition | `reverse-engineering` pattern docs | Shared with reversing tasks; no separate extension pack maintained |

## Domains Explicitly Not Merged Wholesale (policy when routing misses)

| Domain | Policy |
|----|------|
| Pure game-cheat development | Not a product direction; Unity samples can still go through `reverse-engineering` + seed-014 |
| Deep automotive/aviation certification-grade | Link out; this pack only has RF/OT entry-level |
| Pure GRC/compliance long-form | Doesn't replace professional GRC tools; can be referenced in report templates |
| 800+ ATT&CK micro-skills | Use this table + optional ATT&CK tags (Finding field) |

## Relation to MITRE ATT&CK (optional)

Finding templates allow `optional_attack: Txxxx` (see `ops/evidence-finding-path.md`); a full ATT&CK engine is **not required**.
