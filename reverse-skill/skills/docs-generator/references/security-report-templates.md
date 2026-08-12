# Security / Reverse / Pentest Technical Document Templates

This file provides document templates for security projects such as reverse engineering, penetration testing, and vulnerability analysis. After a task completes, the AI should create a document in the user's project directory and output per the matching template.

---

## 0. Evidence Chain (MUST be included in every security report)

> Full contract: `skills/ops/evidence-finding-path.md`  
> Case directory: `work/<case>/` (`case-init.ps1`)

The report body **MUST** contain the following sections (may be merged into "Core Findings", but the fields must not be omitted):

### 0.1 Scope Summary
- Link to `scope.md`: `auth` / `in_scope` / `network_profile`
- No scope → may not claim task completion

### 0.2 Evidence
At least 1 entry, fields: `E-id` / `source_ref` / `repro_command` / `content_hash|n/a`

### 0.3 Findings
Each: `F-id` / `severity|n/a_re` / `evidence_ids` / `confidence` / `location` / `status`

### 0.4 Path
At least 1 `P-id`: `path_type=attack|callflow|solve`, steps may attach E/F

### 0.5 Timeline Summary
Link to `timeline.md` or embed 3–10 key appended records

---

---

## 0.6 Vendor Structure Overlay (professional vendor report structure)

> Full rules: `vendor-report-rules.md` (Issue #65)  
> **MUST** read and select when generating formal security reports; **extract structure only, never copy vendor original text/IOC instances**.

| Flavor | Scenario | Skeleton in one line |
|--------|------|------------|
| `malware` | clearly malicious samples / ordinary trojans / white-plus-black | Huorong-style: overview→flow→sample analysis→incident response→IOC |
| `apt` | APT / campaigns / multi-stage chains | Kaspersky-style: summary→infection chain→investigation→interesting findings→technical analysis→detection & mitigation→IOC |
| `flavor = null` | ordinary reverse / pentest / CTF / JS signing | this section's task template + applicable generic Base elements |

**Generic elements (G1–G7) summary**: G1 Executive summary MUST · G2 Scope MUST · G3 E/F/P MUST · G4 IOC MUST only for `malware`/`apt` · G5 Recommendations MUST only for `malware`/`apt` · G6 Appendix SHOULD · G7 ATT&CK MUST for `apt`

Selection and section order per `vendor-report-rules.md`; where conflicts with §0.1–0.5 arise, **the Evidence contract wins**.

## 1. Reverse Engineering Report Template

```markdown
# [Target Name] Reverse Analysis Report

> Analysis date: YYYY-MM-DD
> Analyst: [AI / human]
> Toolchain: [jadx / IDA / radare2 / Frida / ...]

## 1. Target Overview

| Property | Value |
|------|---|
| Filename | |
| File type | APK / ELF / PE / Mach-O / ... |
| Size | |
| MD5 | |
| SHA256 | |
| Package/entry | |

## 2. Analysis Goals

<!-- the core questions this reversing must answer -->

## 3. Static Analysis

### 3.1 Basic Information
<!-- architecture, compiler, protection mechanisms, string features -->

### 3.1.1 Import Table / Dependencies (MUST for binaries)
<!-- write the E-imports / E-triage-imports summary; failures must also be recorded as Evidence; no skipping -->

### 3.2 Key Functions/Classes
<!-- list the located key logic, with code snippets -->

### 3.3 Crypto/Signing Algorithms
<!-- if crypto is involved, explain the algorithm, key source, parameter construction -->

## 4. Dynamic Analysis

### 4.1 Hook Records
<!-- Frida / xposed / other hook targets and results -->

### 4.2 Runtime Behavior
<!-- network requests, file operations, process behavior -->

## 5. Core Findings

<!-- numbered key conclusions -->

1. ...
2. ...
3. ...

## 6. Reproduction Steps

<!-- let others reproduce your analysis results -->

```bash
# key commands
```

## 7. Open Issues

<!-- points not fully resolved -->

## 8. Attachments

<!-- hook scripts, decryption code, screenshots, etc. -->
```

---

---

## 1b. Malware / APT Reports (vendor flavor)

When the task is malware analysis, virus reporting, or APT/campaign analysis, **do not** just deliver the "reverse engineering" skeleton above; ordinary reverse tasks keep their original template and do NOT auto-select a vendor flavor:

1. Read `vendor-report-rules.md` and select `malware` or `apt`
2. Output per the corresponding section order
3. Still **MUST** include the §0 Evidence chain; `malware` / `apt` flavors additionally **MUST** include an IOC table
4. Static analysis of binary samples **MUST** include import-table Evidence (consistent with the radare2/ida/malware hard gates)

## 2. Penetration Test Report Template

```markdown
# [Target] Penetration Test Report

> Test date: YYYY-MM-DD
> Test scope: [URL / IP / app name]
> Authorization status: [authorized / CTF / lab environment]

## 1. Executive Summary

<!-- one paragraph: what was tested, what was found, risk level -->

## 2. Test Scope

| Item | Details |
|------|------|
| Target | |
| Test type | black box / gray box / white box |
| Test window | |
| Tools | |

## 3. Findings Summary

| # | Vulnerability | Risk level | Status |
|---|---------|---------|------|
| 1 | | high/medium/low/info | verified/pending |

## 4. Vulnerability Details

### 4.1 [Vulnerability Name]

**Risk level**: high / medium / low

**Description**:

**Impact**:

**Reproduction steps**:

1. ...
2. ...
3. ...

**Evidence**:

```
<!-- request/response/screenshot/payload -->
```

**Remediation**:

## 5. Attack Path

<!-- if there is a full attack chain, draw the path -->

```
entry → recon → exploit → privilege escalation → goal achieved
```

## 6. Tools and Environment

| Tool | Version | Purpose |
|------|------|------|
| | | |

## 7. Remediation Summary

| Priority | Recommendation |
|--------|------|
| P0 | |
| P1 | |
| P2 | |

## 8. Appendix

<!-- full payloads, scripts, config files, etc. -->
```

---

## 3. CTF Writeup Template

```markdown
# [Competition] - [Challenge] Writeup

> Category: Web / Reverse / Pwn / Crypto / Misc / Forensics
> Difficulty: Easy / Medium / Hard
> Points: N pts
> Time to solve:

## Challenge Description

<!-- original description -->

## Solution Approach

### Step 1: Information Gathering
<!-- what was observed -->

### Step 2: Vulnerability / Breakthrough
<!-- what key point was found -->

### Step 3: Exploitation
<!-- how it was exploited -->

## Key Code/Payload

```python
# exploit code
```

## Flag

```
flag{...}
```

## Pitfalls Encountered

<!-- detours taken -->

## Knowledge Points

<!-- knowledge points covered by this challenge, for later review -->
```

---

## 4. JS/Web Signing Reverse Report Template

```markdown
# [Site/App] Signature Parameter Reverse Report

> Analysis date: YYYY-MM-DD
> Target endpoint: [URL]
> Signature field: [field name]

## 1. Target Request

```http
POST /api/xxx HTTP/1.1
Host: example.com

param1=xxx&sign=<target field>
```

## 2. Locating Process

### 2.1 Breakpoint/Hook Method
<!-- how the signature generation location was found -->

### 2.2 Call Stack
<!-- key call chain -->

## 3. Algorithm Recovery

### 3.1 Algorithm Type
<!-- HMAC-SHA256 / AES / custom / ... -->

### 3.2 Parameter Construction
<!-- which fields participate, sort order, separators -->

### 3.3 Key Source
<!-- hardcoded / API return / timestamp-derived / ... -->

## 4. Local Reproduction Code

```javascript
// Node.js reproduction
```

## 5. Verification Results

<!-- compare signatures generated by the reproduction code with actual requests -->

## 6. Anti-Crawler / Risk-Control Notes

<!-- rate limits, device fingerprinting, environment checks, etc. -->
```

---

## 5. Document Output Standards

### Output Location

- Documents default to the **user's current project directory** (not the skill pack directory)
- Filename format: `YYYY-MM-DD_[type]-[target short name]-report.md`
- If the user's project has a `docs/` directory, prefer placing it there

### Output Timing

The AI auto-invokes this skill to generate documents at:

1. Reverse task complete, core conclusions produced
2. Pentest complete, vulnerabilities found and verified
3. CTF challenge solved, flag obtained
4. User explicitly asks to "write a report/document"

### Quality Requirements

- Every code block must be runnable as-is or have clear context
- No placeholders/TODOs (if a part is genuinely unfinished, mark "to be completed" and explain why)
- Key findings must be backed by evidence (command output, screenshot descriptions, code snippets)
- Reproduction steps must let a third party reproduce independently

