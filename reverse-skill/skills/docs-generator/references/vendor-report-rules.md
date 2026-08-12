# Vendor Report Rules (professional vendor report structure overlay)

> Issue #65, problem 2.  
> **Extract structure and writing rules only; never copy any vendor report body text, figures, real IOC instances, or large passages.**  
> This file is an **overlay**: it does not replace the task templates in `security-report-templates.md`, nor weaken the §0 Evidence→Finding→Path contract.

Structural references (public samples, skeleton only):

| Flavor | Primary reference | Scenario |
|--------|--------|------|
| `malware` | Huorong Security virus/technical analysis reports | clearly ordinary trojans, white-plus-black, phishing poisoning, malicious samples |
| `apt` | Kaspersky Securelist / APT campaign reports (e.g. MATA) | APT, gang campaigns, multi-stage infection chains, industry targeting |

Principle: **fewer templates, better templates** — only 2 vendor flavors + 1 set of generic professional elements; ordinary reverse, pentest, CTF, and JS reports keep their task templates and don't masquerade as malware reports by default.

---

## 0. When to Enable

When `docs-generator` produces **security-class** reports (reverse / malware / pentest wrap-up / user explicitly asking for a "professional report" or "vendor style"), this file **MUST** be read. Select a vendor flavor only when task evidence or an explicit user request supports it; otherwise use `flavor = null` and overlay only the generic professional elements plus the original task template.

| Signal | Flavor |
|------|--------|
| APT / gangs / campaigns / multi-stage C2 / industry targeting / ICS / spear-phish campaigns | `apt` |
| clearly malicious samples, trojans, stealers, white-plus-black, impersonation sites | `malware` |
| ordinary APK/ELF/PE/Mach-O reversing, algorithm analysis, firmware analysis, pentest, CTF, JS signing | `flavor = null`; use the original task template and the minimal generic-element set |

An explicit user request such as "Kaspersky/APT style" or "Huorong/virus report style" overrides auto-selection.

---

## 1. Generic Professional Elements (Base)

Apply the following Base elements per report type. Items marked **MUST** are non-optional; flavor-specific elements must not be forced into unrelated tasks just to fill a template. When nothing applies, use `n/a` with a reason.

| # | Element | Requirement |
|---|------|------|
| G1 | Executive summary / overview | **MUST**: 3–8 sentences: what was analyzed, most severe conclusion, impact surface, recommended actions |
| G2 | Scope and authorization | **MUST**: link to the case `scope.md` (see template §0.1) |
| G3 | Evidence→Finding→Path | **MUST**: see `security-report-templates.md` §0 and `skills/ops/evidence-finding-path.md` |
| G4 | IOC table | `malware` / `apt` **MUST**; other tasks only when relevant indicators exist |
| G5 | Recommendations / handling | `malware` / `apt` **MUST**: at least 1 actionable recommendation; other tasks per the original task template |
| G6 | Appendix metadata | **SHOULD**: tools and versions, sample hashes, full reproduction commands |
| G7 | ATT&CK mapping | **MUST** (under `apt`; `n/a` + reason when no technique applies); other tasks **SHOULD** |

### 1.1 IOC Table Minimum Columns

```markdown
| Type | Value | Context | First/Last seen | Source evidence | Confidence |
|------|----|--------|---------------|----------|--------|
| file_sha256 / file_md5 / domain / ip:port / url / mutex / path / registry | … | where found | YYYY-MM-DD / n/a | E-id | high/med/low |
```

### 1.2 Copyright and Security Boundaries

- Never paste vendor PDF/webpage paragraphs or figure captions as your own analysis.
- Real tokens, internal URLs, and client identifiers go in placeholders.
- Do not output directly-exploitable attack step details for unauthorized targets (follow case scope / RULES).

---

## 2. Flavor: `malware` (Huorong-style · explicit selection)

**Narrative goal**: readers understand in 5 minutes "what it is → how it got in → what the sample does → how to handle it → what the IOCs are".

### 2.1 Recommended Section Order

```markdown
# [Title: one-sentence threat classification]

> Analysis date / analyst / sample identifier (hash)

## 1. Overview
(G1: discovery channel, disguise methods, core technical points, whether the product side can detect it — n/a if unknown)

## 2. Attack / Infection Flow
(flow diagram: Mermaid or step list; maps to Path `path_type=attack`)

## 3. Sample Analysis
### 3.1 Sample Provenance
### 3.2 Static Analysis
(**MUST** include import-table / basic-identity Evidence: E-imports or equivalent; see radare2/ida/malware hard gates)
### 3.3 Dynamic Analysis / Behavior
(n/a + reason if no dynamic environment)
### 3.4 Core Findings (Findings table or numbered list, attached evidence_ids)

## 4. Incident Response
(only within the authorized scope: first confirm scope and preserve evidence such as samples, memory, process trees, network connections, and logs, then isolate the host; only after owner approval terminate processes, quarantine/remove files, check hosts/startup items, run full scans, and re-verify. Never delete files before evidence preservation.)

## 5. Summary Notes
(risk reminders and prevention for ordinary users/ops)

## 6. IOC Information
(G4 table)

## 7. Evidence Chain Summary
(§0: E / F / P / Timeline; may merge with §3.4 but fields stay)

## 8. Appendix
(tool versions, reproduction commands, script paths)
```

### 2.2 Style

- Chinese users default to Chinese; conclusions before details.
- Static analysis is layered by "component/phase"; avoid pasting long unstructured logs.
- Handling steps must be independently executable; no empty "raise security awareness" filler.

---

## 3. Flavor: `apt` (Kaspersky Securelist style)

**Narrative goal**: tell the campaign-level story — who attacked whom, when, with what chain; how the investigation progressed; how components divide work; what defenders can detect with.

### 3.1 Recommended Section Order

```markdown
# [Campaign/cluster name]: [one-sentence impact]

> Date / team / industry and region scope (if known)

## 1. Executive summary
(G1: time window, victim profile, entry point, family/cluster attribution, duration, most important conclusions)

## 2. The infection chain
(phased: delivery → exploit/loader → main payload → post-exploitation/stealing; mark unknown phases explicitly as "limited visibility"
maps to Path; a chain diagram is recommended)

## 3. Incident investigation
(investigation narrative: key turns, internal proxy/C2 characteristics, how scope expanded; attach Timeline)

## 4. Interesting findings
(3–7 non-obvious points, each attached to E-id / F-id where possible)

## 5. Technical analysis
### 5.1 Component overview table (loader / trojan / stealer / …)
### 5.2 Per-component behavior and configuration
### 5.3 Static highlights (including import-table/packing/persistence Evidence)
### 5.4 Network and C2
(ATT&CK table G7 may be attached)

## 6. Detection and mitigation
(detection ideas / hunting leads / mitigation priorities; not vague slogans)

## 7. IOC
(G4; grouped by type)

## 8. Evidence Chain Summary
(§0 fields)

## 9. Appendix
(sample list with hashes, tool versions, public reference numbers; do not copy external report body text)
```

### 3.2 Style

- Be honest about the timeline and "visibility limits".
- Interesting findings ≠ restating the overview; write the truly critical anomalies from the investigation.
- Component analysis uses tables: role / persistence / C2 / dependencies, then expands.

---

## 4. Hooking Into Existing Task Templates

| Task template (`security-report-templates.md`) | Overlay method |
|------------------------------------------|----------|
| 1. Reverse engineering report | default `flavor = null`; keep the original static/dynamic/reproduction skeleton and hard-gate Evidence like import tables; only clearly malicious samples use §2 |
| 2. Penetration test report | `flavor = null`; add applicable G1–G3 from Base, align the attack path with §0 Path, no forced IOC |
| 3. CTF Writeup | `flavor = null`; keep the original challenge, solution approach, and reproduction structure; no forced IOC/ATT&CK |
| 4. JS/Web signing reverse | `flavor = null`; use the original overview → locate → algorithm → reproduction skeleton; do not apply malware |
| Malware / APT specific | explicitly select the `malware` or `apt` full skeleton |

**Conflict resolution**: §0 Evidence chain fields and scope gates **always win**; the flavor only changes narrative order and professional framing — it must never remove E/F/P.

---

## 5. Selection Pseudocode

```
if user_requests_kaspersky or apt or threat_campaign:
    flavor = apt
elif user_requests_huorong or vir_report or explicit_malware:
    flavor = malware
else:
    flavor = null  # original task template + applicable Base elements
emit(base_report)
if flavor in (malware, apt):
    emit(report with flavor outline)
```

---

## 6. Completion Checklist (self-check at the end of a report)

- [ ] flavor selected, or explicitly "task template + minimal set"
- [ ] G1 overview present and substantive
- [ ] §0 E/F/P fields complete
- [ ] `malware` / `apt` reports have an IOC table (or n/a + reason)
- [ ] `malware` / `apt` reports have actionable recommendations/handling
- [ ] flavor-less tasks were not forced into malware/APT-specific sections
- [ ] no vendor original text pasted, no placeholders/TODOs
- [ ] hard-gate Evidence such as the import table is in the static/technical analysis (if binary analysis was part of this task)

---

## 7. Source Registry

- Kaspersky Securelist, "Updated MATA attacks industrial companies in Eastern Europe": <https://securelist.com/updated-mata-attacks-industrial-companies-in-eastern-europe/110829> (structure reference; accessed: 2026-08-11)
- Huorong Security public technical article portal: <https://www.huorong.cn/> (site portal; accessed: 2026-08-11. Specific article URLs, titles, and access dates should be registered when actually cited)
- ATT&CK technique IDs serve only as normalized mapping and must be supported by this task's Evidence; never auto-import IOCs from external reports into the current report.

---

## 8. Non-Goals

- No full templates for Mandiant/CrowdStrike/QiAnXin etc. (the two flavors cover common needs structurally).
- No auto-crawling vendor sites to fill reports.
- No flavor may lower the Evidence contract or authorization scope.

