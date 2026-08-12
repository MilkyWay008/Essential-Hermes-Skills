# reverse-skill PRIMARY Fast Path

> Kept in sync with `scripts/master-route.ps1`.

## Execution Contract

```text
1. Route first, act second
2. Output the PRIMARY path + a one-line rationale
3. case-init / scope.md (ops/scope-contract) — no ACT on the target unless auth is granted
4. Assign lead + specialist roles (ops/role-map)
5. Open the PRIMARY SKILL.md immediately → ACTION REQUIRED
6. Trust only tool-index for tool paths; if missing, bootstrap (manifest capabilities only)
7. Append to timeline / workitems as you go; conclusions flow Evidence→Finding→Path
8. No match → read the full routing.md table or propose a new skill
```

```powershell
powershell -File scripts\master-route.ps1 -Hint "<user-task>"
# By default writes to the current project's work/master-route-<ts>/route-scope.md; when calling from another directory, explicitly pass the project root
powershell -File scripts\master-route.ps1 -Hint "<user-task>" -ProjectRoot "C:\path\to\analysis-project"
powershell -File scripts\case-init.ps1 -Hint "<user-task>" -CaseName "my-case"
# case defaults to the current project's work/<case>/; -PackageRoot kept for compatibility, -ProjectRoot takes precedence
powershell -File scripts\case-init.ps1 -Hint "<user-task>" -CaseName "my-case" -ProjectRoot "C:\path\to\analysis-project"
# One-shot, ready to ACT (auth + target + network profile):
powershell -File scripts\case-init.ps1 -Hint "<task>" -CaseName "my-case" -AuthGranted -TargetUrl "https://target/" -NetworkProfile authorized_target_only
# Smoke test: verify + script parsing + routing matrix (incl. Chinese Hint)
powershell -File scripts\smoke.ps1
# Lightweight scope gate before ACT (exit 2 if not ready; -Force only warns)
powershell -File scripts\case-guard.ps1 -CaseRoot work\my-case
# Evidence append
powershell -File scripts\append-evidence.ps1 -CaseRoot work\my-case -Id E-001 -Title "..." -ReproCommand "..."
python3 skills/case-review/scripts/review_case.py work/<case> --verify-hashes --strict
```

## Ops Contract

| Doc | Purpose |
|------|------|
| `ops/IDENTITY.md` | We are a routing package, not a Z3r0 platform |
| `ops/scope-contract.md` | Startup gate |
| `ops/evidence-finding-path.md` | Evidence chain |
| `case-review/SKILL.md` | Evidence graph review and report handoff |
| `ops/role-map.md` | role → skill |
| `ops/timeline-workitem.md` | Timeline and coverage |
| `ops/sandbox-profile.md` | Tool comparison |
| `ops/skill-supply-chain.md` | Safety latch for installing external skills/MCPs |
| `references/community-security-skills.md` | Community skill ecosystem (borrow, don't merge) |
| `reverse-engineering/references/re-agent-workflow.md` | RE: triage→static→dynamic→synthesis |
| `pentest-tools/references/recon-pipeline.md` | Authorized recon pipeline + evidence gate |

## Priority (high → low)

| ID | Condition | PRIMARY |
|----|------|---------|
| **R4** | DSL VM / fireye / custom opcode VM | `reverse-engineering/dsl-vm-reverse/` |
| **R1** | APK / smali / jadx / apktool | `apk-reverse/` |
| **R2** | IPA / iOS / Objection / MobSF / mobile | `mobile-reverse/` |
| **R3** | JS signing / front-end crypto / jshook / CDP | `js-reverse/` |
| **R30** | Browser extension reverse engineering | `browser-extension-reverse/` |
| **R31** | macOS / Mach-O | `macos-reverse/` |
| **R33** | Go / Rust binaries | `go-rust-reverse/` |
| **R5** | .NET / dnSpy / de4dot / ConfuserEx | `dotnet-reverse/` |
| **R9** | Malicious samples / YARA / sandbox | `malware-analysis/` |
| **R21** | Protocols / Protobuf / PCAP protocol | `protocol-reverse/` |
| **R22** | Ghidra / open-source decompilation | `ghidra-reverse/` |
| **R6** | IDA / decompilation / deep disassembly | `ida-reverse/` |
| **R7** | radare2 / r2 | `radare2/` |
| **R8** | Firmware / binwalk / IoT / EMBA | `firmware-pentest/` |
| **R34** | Hardware debug ports / UART/JTAG | `hardware-security/` |
| **R28** | OT / ICS / industrial control | `ot-ics/` |
| **R17** | pwn / ROP / stack exploitation | `pwn-chain/` |
| **R16** | N-day / patch diffing | `patch-diff-exploit/` |
| **R18** | EDR / AV evasion / syscall | `edr-bypass-re/` |
| **R24** | Windows / AD / Kerberos / AD CS | `windows-ad/` |
| **R37** | Federated identity SAML/OIDC | `identity-federation/` |
| **R23** | Cloud / containers / K8s | `cloud-k8s/` |
| **R35** | Database security | `database-security/` |
| **R25** | Forensics / memory dumps / timelines | `digital-forensics/` |
| **R36** | Email / phishing analysis | `email-security/` |
| **R29** | Wi-Fi / wireless pentest | `wifi-wireless/` |
| **R38** | RF / SDR research | `radio-sdr/` |
| **R32** | Thick client security | `thick-client/` |
| **R26** | Code audit / SAST / Semgrep | `code-audit/` |
| **R27** | Threat hunting / detection engineering / blue team | `threat-hunting/` |
| **R10** | Attack chain / red team / lateral / full pentest | `attack-chain/` |
| **R11** | Nmap / Nuclei / SQLMap / SRC / pentest tools | `pentest-tools/` |
| **R12** | API / GraphQL / BOLA / JWT attacks | `api-security/` |
| **R13** | SBOM / Trivy / supply chain | `supply-chain-security/` |
| **R14** | LLM / prompt injection / agent security | `llm-security/` |
| **R15** | bindiff / symbol migration / PDB | `binary-diff/` |
| **R19** | Browser/desktop automation | `browser-automation/` |
| **R40** | Case / Evidence graph review | `case-review/` |
| **R20** | Reports / writeups | `docs-generator/` |
| **R39** | Diagrams / Mermaid / Graphviz / PlantUML / architecture diagrams | `diagram-generator/` |
| **R41** | Pure multi-type CTF orchestration | `CTF-Sandbox-Orchestrator/` |
| **R0** | General RE / anti-debug / OLLVM / unknown binaries | `reverse-engineering/` |
## Boundaries

| Task | Handling |
|------|------|
| Pure multi-type CTF orchestration | `CTF-Sandbox-Orchestrator/` |

## Reading Order

```text
RULES.md → MASTER-ROUTING.md → PRIMARY SKILL.md
  → (optional) routing.md three axes / field-journal
  → tool-index.md → bootstrap → ACT
```
