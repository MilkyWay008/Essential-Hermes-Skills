---
name: edr-bypass-re
description: >-
  Use for reverse-engineering defensive implementations to build targeted red-team bypasses: reverse EDR /
  Defender / AV hook tables, ETW providers, and AMSI implementations first, then write targeted unhook /
  indirect syscall / ETW patch / call-stack spoof techniques. Maps to MITRE ATT&CK T1562 (defense evasion).
  Trigger keywords: EDR bypass, AV bypass, unhook, direct/indirect syscall, Hells Gate, Halos Gate, Tartarus
  Gate, ETW patch, AMSI patch, call stack spoofing, hardware breakpoint Blindside, ntdll unhook, kernel
  callback, Sysmon evasion, PPID spoof, sleep mask, process hollowing, reflective DLL.
---

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm this skill's operations are authorized routine work
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths (if missing at cold start, run `scripts/refresh-tool-index.ps1` on Windows or `bash scripts/refresh-tool-index.sh` on Linux/macOS first)
4. `NEXT`: Call bootstrap when tools are missing; don't guess paths
5. `ACT`: Proceed to the first step of the "Workflow" and execute it; don't stop at the confirmation stage

# EDR Bypass: From Reversing Defensive Implementations to Red-Team Bypasses

> Authorized red team / adversary emulation / own-product testing only. Prohibited against unauthorized targets.

## Scope

Use this skill when delivering implants to authorized target hosts and evading modern EDR during red team / adversary emulation.

1. **Red team / Purple team / adversary emulation** — the client wants to assess the SOC's and EDR's real detection capabilities
2. **In-house implant / C2 framework development** — developing payloads to test your own products, needing to bypass your own or the target's EDR
3. **EDR product evaluation** — objectively assessing a specific EDR's detection coverage within confirmed compliance boundaries
4. **CTF / offensive-defense exercise Windows breakthroughs** — need reliable execution on hardened hosts during competitions

**Not applicable:**

- Full RE of an AV vendor's own product for a commercial evaluation report to a client (seek formal vendor partnership instead)
- Evasion against unauthorized targets (illegal)
- Evasion for ordinary malware (this skill focuses on red-team OPSEC, not teaching malicious-code writing)

### Division of Labor with Other Skills

| Scenario | What to use |
|------|--------|
| Full-chain attack-defense (from external network to domain controller) | `attack-chain/` |
| Internal lateral movement / AD attacks | `../pentest-tools/references/network-attack-defense.md` |
| Deliver an implant past EDR on a specific host | **this skill** |
| Pure static evasion (obfuscation / packing) | `malware-analysis/` (reverse perspective) |

`attack-chain` covers the full kill chain; this skill focuses only on the internal mechanisms of and targeted bypasses for **EDR as a single adversary**.

## Core Principles

```text
EDR's four main monitoring surfaces                Red team's countermeasures
─────────────────────              ─────────────────────
User-mode ntdll hook       ◄──►   unhook (Peruns Fart / fresh ntdll)
                                  indirect syscall / Hell's Gate
                                  hardware breakpoint Blindside

kernel callback         ◄──►   call stack spoof
(Ps/Cm/Ob family)                    use legitimate trigger chains (don't bypass directly; combine with upstream stealth)

ETW telemetry           ◄──►   EtwEventWrite patch
(Microsoft-Windows-Threat-          NtTraceControl to disable the provider
 Intelligence, etc.)                 AmsiContext synchronized handling

AMSI scanning               ◄──►   AmsiScanBuffer patch (mov eax,0x80070057; ret)
(amsi.dll)                       hardware breakpoint bypass
                                  reflectively load a copy of amsi.dll
```

Key insights:

- **EDR is not a black box** — key hooks / callbacks / providers can all be reversed with IDA + windbg
- **Bypass techniques must be combined** — unhook alone won't fix ETW alerts, and AMSI patch alone won't fix syscall hooks
- **Order matters** — ETW patch first → AMSI patch next → unhook last; if the order is wrong, the EDR receives the unhook alert first
- **Modern EDRs have made ETW + kernel callbacks their main battlefield**; userland unhook alone has long been insufficient

## Workflow

### Step 1: Identify the EDR on the Target Host

```powershell
# List common EDR / AV drivers
Get-Service | Where-Object {$_.Name -match 'CSAgent|SentinelAgent|elasticendpoint|esets|ekrn|MsMpEng|wdsvc|cyserver|sysmon|aswbidsagent'}

# List loaded minifilters
fltmc filters

# List registered kernel callbacks (needs windbg + kernel debugging / or use PChunter / DRVHV)
# !object \Callback
# !pnpcallback / Process / Thread / Image
```

The EDR fingerprint table is at the top of `references/hook-survey.md`.

### Step 2: Extract the Hook Table from the EDR DLL

1. Attach to a process injected with the EDR userland component (any running process)
2. Dump the current `ntdll.dll` `.text` section in windbg
3. Diff it against the clean `C:\Windows\System32\ntdll.dll` on disk
4. The differences are the hook points

Or use `pe-sieve` directly:

```powershell
pe-sieve64.exe /pid 1234 /shellc 3 /modules 3 /dir hooks_dump
```

See `references/hook-survey.md` for details.

### Step 3: Choose a Bypass Technique Combination

| Defense point | Recommended bypass |
|--------|---------|
| ntdll inline hook | indirect syscall + dynamic SSN (Halo's Gate) |
| ETW-TI provider | EtwEventWrite head patch |
| AMSI (PowerShell / .NET) | AmsiScanBuffer patch or HWBP |
| kernel callback | call stack spoof + legitimate gadgets |
| Sysmon ProcessCreate | PPID spoof + unbacked memory |

### Step 4: Implement in the Implant

Code skeletons are in `references/unhook-techniques.md` and `references/telemetry-blinding.md`.

### Step 5: Local Sandbox Verification

```powershell
# Deploy the target EDR trial in an isolated environment (Defender default is fine to start)
# Enable Sysmon + olaf-config
sysmon64.exe -i sysmonconfig.xml

# Run the implant and check whether these alert sources fire:
#   - Defender AMSI
#   - ETW-TI
#   - Sysmon Event ID 1/7/8/10
#   - EDR console
```

### Step 6: Delivery

- Use legitimate software directories for file drop paths
- PPID-spoof to explorer.exe
- Coordinate with the initial access section of `attack-chain`

## Typical Scenarios

### Scenario 1: Deliver a cobalt-strike-alike beacon past Defender + Sysmon

```text
Goal: Windows 11 Enterprise + Defender (cloud protection on) + Sysmon (olaf config)
Requirement: beacon can callback after landing without triggering any alerts

Combination:
  1. shellcode stored encrypted, decrypted at runtime
  2. AMSI patch (if delivered via PowerShell)
  3. EtwEventWrite patch (eliminate ETW-TI)
  4. indirect syscall + Halo's Gate (eliminate ntdll hook alerts)
  5. PPID spoof to explorer.exe
  6. encrypt own memory during sleep with Ekko / Foliage
```

### Scenario 2: EDR sleep masking on an established low-privilege shell

```text
Prerequisite: obtained a medium-IL shell via phishing, EDR is monitoring
Risk: long-term residency is easily caught by memory scanning detecting beacon artifacts

Solution:
  1. stop allocating new RWX memory
  2. during sleep use Ekko:
       - WaitForSingleObjectEx + CreateTimerQueueTimer
       - encrypt its own .text in the timer + zero out the stack
  3. on wake, restore with ROP
  4. combine with call stack spoof so RtlCaptureStackBackTrace can't see beacon addresses
```

## On-Demand Bootstrap

### Tool Dependencies

| Tool | Purpose | Auto-installable |
|------|------|-----------|
| pe-sieve | Detect hooks / injections in processes | ✓ |
| API Monitor v2 | Dynamically observe API calls and hooks | Semi-auto (manual download) |
| SysWhispers3 | Generate direct / indirect syscall stubs | ✓ (git clone + python) |
| Hell's Gate POC | Dynamic SSN resolution reference implementation | ✓ (git clone) |
| windbg + IDA | Statically reverse EDR DLLs / kernel callbacks | ✗ (install yourself) |
| Sysmon + olaf config | Local verification environment | ✓ |

### Bootstrap Commands

```powershell
# pe-sieve, SysWhispers3, and Sysmon are NOT in bootstrap-manifest.json — manual install required:
#   - pe-sieve:     download pe-sieve64.exe from https://github.com/hasherezade/pe-sieve/releases
#   - SysWhispers3: git clone https://github.com/klezVirus/SysWhispers3
#   - Sysmon:       https://learn.microsoft.com/sysinternals/downloads/sysmon (+ olaf config)
powershell -NoProfile -ExecutionPolicy Bypass -File "..\scripts\bootstrap-reverse.ps1" -StartServices
```

## Routing Context

**Upstream entries**:

- `reverse-engineering/` — need to first understand EDR DLL / driver implementations
- `attack-chain/` — decide at which kill-chain stage to bring in this skill

**Peer references**:

- `../pentest-tools/references/network-attack-defense.md` — how to combine with this skill during internal lateral movement
- `malware-analysis/` — reverse perspective on how detection vendors write rules
- `field-journal/` — write back lessons after each engagement

**Downstream deliverables**:

- When generating reports, cite MITRE ATT&CK **T1562 (Impair Defenses)**, T1562.001 (Disable or Modify Tools), T1562.006 (Indicator Blocking), T1055 (Process Injection), T1027 (Obfuscated Files or Information)

## Legal Boundary Statement

- Authorized red team / adversary emulation / own-product testing only
- Written authorization (SoW / test contract / SRC scope statement) MUST be obtained before any operation
- Must not be used against unauthorized targets or beyond the authorized scope
- Report high-severity findings to the client immediately; follow responsible disclosure
- Real target information in all reports MUST be sanitized (IP / hostname / domain / credential placeholders)

## References

- Detailed hook survey: `references/hook-survey.md`
- unhook / syscall techniques: `references/unhook-techniques.md`
- ETW / AMSI / anti-forensics: `references/telemetry-blinding.md`
- MITRE ATT&CK T1562: <https://attack.mitre.org/techniques/T1562/>


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
