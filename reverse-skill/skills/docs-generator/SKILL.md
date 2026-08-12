---
name: docs-generator
description: >-
  Creates task-oriented technical documentation with progressive disclosure. Use when writing READMEs, API
  docs, architecture docs, or markdown documentation. Also use this skill at the END of any completed
  reverse engineering, penetration testing, CTF, or security analysis task to generate a formal report in
  the user project directory. Trigger keywords: report, writeup, technical documentation, security report.
---

# Technical Documentation

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Confirm whether the current task falls within this skill's scope
2. `NOW`: Read `../tool-index.md` to verify tool availability and actual paths
3. `NEXT`: If tools are missing, call bootstrap — don't guess paths
4. `ACT`: Move to the first step of the "Workflow" and execute it — don't stop at confirmation

For writing style, tone, and voice guidance, follow the project's documented style conventions (see the module's references/ for tone guidance).

## Documentation Output for Security / Reverse-Engineering Tasks

When a reverse-engineering, penetration testing, CTF, or security analysis task is complete, this skill generates formal technical documentation in the **user's project directory**.

### Trigger Conditions

1. Reverse-engineering task complete, with core conclusions produced (algorithm recovery, signature cracking, bypass approaches, etc.)
2. Penetration test complete, with vulnerabilities discovered and verified
3. CTF challenge solved, flag obtained
4. User explicitly requests "write a report/document/writeup"

### Template Selection

| Task Type | Template to Use |
|---------|---------|
| APK/binary/so reverse-engineering | `references/security-report-templates.md` → Reverse-engineering report |
| Penetration testing / vulnerability hunting | `references/security-report-templates.md` → Penetration test report |
| CTF solving | `references/security-report-templates.md` → CTF Writeup |
| JS/Web signature reverse-engineering | `references/security-report-templates.md` → Signature reverse-engineering report |
| Malware / APT / virus analysis reports | `references/security-report-templates.md` + **`references/vendor-report-rules.md`** |
| General technical documentation | `references/templates.md` → README / API docs |

### Vendor Report Structure (Issue #65)

Formal security reports **MUST** read `references/vendor-report-rules.md` (take only the structure, not the vendor's original text). Choose a vendor flavor only when task evidence or the user explicitly requires it; use `flavor = null` for ordinary reverse-engineering and other tasks.

| Flavor | When to Use | Primary Reference Skeleton |
|--------|--------|------------|
| `malware` | Clearly malicious samples, trojans, white+black loading, phishing poisoning | Huorong-style: overview → flow → sample analysis → incident response → IOC |
| `apt` | APT / campaigns / groups / multi-stage infection chains / industry-targeted | Kaspersky Securelist-style: summary → infection chain → investigation narrative → Interesting findings → technical analysis → detection & mitigation → IOC |
| `flavor = null` | Ordinary APK/ELF/PE/Mach-O reverse-engineering, algorithm/firmware analysis, pentest / CTF / JS signatures | Original task template + Base common elements; don't apply malware/APT-specific sections |

Principle: **quality over quantity for templates** — only the 2 vendor flavors above; don't build a third full-text template.
Applies **together with** §0 Evidence→Finding→Path; the Evidence contract takes precedence on conflict.

### Output Specifications

- **Output location**: the user's current project directory (not the skill package directory)
- **Filename format**: `YYYY-MM-DD_[type]-[target-short-name]-report.md`
- **If the project has a `docs/` directory**: prefer placing it under `docs/`
- **Encoding**: UTF-8
- **Language**: follow the user's conversation language (Chinese conversation → Chinese report, English conversation → English report)

### Quality Requirements

- All code blocks must be directly runnable or have clear context
- No placeholders/TODOs
- Key findings must be supported by evidence
- Reproduction steps must let a third party reproduce independently
- Replace sensitive information (real tokens, passwords, internal URLs) with placeholders
- **MUST** include the Evidence → Finding → Path chain (see `../ops/evidence-finding-path.md` and template §0)
- **MUST** read `references/vendor-report-rules.md`: select `malware` / `apt` or `flavor = null`; with no flavor, output only the original task template and applicable Base elements, without forcing IOC/ATT&CK
- **SHOULD** reference case `scope.md` / `timeline.md` (`../scripts/case-init.ps1`)

### Diagram Integration

When generating a report, call the `diagram-generator` skill at appropriate points to produce visual diagrams:

| Report Type | Suggested Diagram | Diagram Type |
|---------|---------|---------|
| Reverse-engineering report | Function call graph, data flow diagram | Mermaid flowchart / sequenceDiagram |
| Penetration test report | Attack path diagram, network topology | Mermaid flowchart / Graphviz |
| CTF Writeup | Solution approach flowchart | Mermaid flowchart |
| JS signature reverse-engineering report | Request chain sequence diagram, algorithm flowchart | Mermaid sequenceDiagram / flowchart |

Embed diagrams in the report markdown as Mermaid code blocks so they render directly on GitHub/GitLab.

---

## Core Principles

### 1. Progressive Disclosure

Reveal information in layers:

| Layer | Content | User Question |
|-------|---------|---------------|
| 1 | One-sentence description | What is it? |
| 2 | Quick start code block | How do I use it? |
| 3 | Full API reference | What are my options? |
| 4 | Architecture deep dive | How does it work? |

**Warnings, breaking changes, and prerequisites go at the TOP.**

### 2. Task-Oriented Writing

```markdown
<!-- Bad: Feature-oriented -->
## AuthService Class
The AuthService class provides authentication methods...

<!-- Good: Task-oriented -->
## Authenticating Users
To authenticate a user, call login() with credentials:
```

### 3. Show, Don't Tell

Every concept needs a concrete example.

## Formatting Standards

- **Sentence case headings**: "Getting started" not "Getting Started"
- **Max 3 heading levels**: Deeper means split the doc
- **Always specify language** in code blocks
- **Relative paths** for internal links
- **Tables** for structured data with 3+ attributes

## Quality Checklist

- [ ] Code examples tested and runnable
- [ ] No placeholder text or TODOs
- [ ] Matches actual code behavior
- [ ] Scannable without reading everything
- [ ] Reader knows what to do next

## Anti-Patterns

| Problem | Fix |
|---------|-----|
| Wall of text | Break up with headings, bullets, code, tables |
| Buried critical info | Warnings/breaking changes at TOP |
| Missing error docs | Always document what can go wrong |

## Templates

For README, API endpoint, and file organization templates, see [references/templates.md](references/templates.md).

## Related Skills

- Writing style, tone, and voice guidance — follow documented conventions
- Architecture and flow diagrams — use the agent's diagram tools (e.g. Mermaid)


---

## On-Demand Bootstrap

This skill has no external tool dependencies — pure text generation. No bootstrap needed.

If diagrams need to be rendered and embedded in a report, the `diagram-generator/` skill is called.

---

## Routing Context

**Upstream entry**: all security/reverse-engineering skills call this skill automatically after their task completes
**Trigger methods**:
- Automatic: executed as step 9 of the behavior chain after task completion
- Manual: user says "write report", "produce documentation", "writeup"

**Peer modules**:
- `apk-reverse/` — generates a reverse-engineering report after APK reverse-engineering completes
- `ida-reverse/` — generates a reverse-engineering report after binary analysis completes
- `radare2/` — generates a reverse-engineering report after CLI analysis completes
- `js-reverse/` — generates a signature report after JS signature reverse-engineering completes
- `reverse-engineering/` — generates a reverse-engineering report after general reverse-engineering completes
- `field-journal/` — report content also serves as the data source for the evolution journal

**Security report template**: `references/security-report-templates.md`
**Vendor report rules**: `references/vendor-report-rules.md` (flavor: malware | apt | null)
**General documentation template**: `references/templates.md`


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Does the report contain Evidence / Finding / Path (ops contract)?
- [ ] Did I complete and write back the Checklist items required by RULES?
