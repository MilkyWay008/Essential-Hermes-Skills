# Evidence → Finding → Path Chain

> Inspired by the Z3r0 Evidence Plane, implemented as a **Markdown field contract**.  
> reverse-skill feature: ties into `docs-generator` report templates, `field-journal` sanitized writeback, and reproducible commands.

## 1. Evidence (immutable observations)

Each piece of evidence is its own paragraph or table row:

```markdown
### E-{nnn}
- title:
- observed_at:
- source_type: command | screenshot | file | log | memory | network | manual
- source_ref: {path or command id}
- content_hash: {sha256 of artifact if file, else n/a}
- artifact_path: {relative path under case root when content_hash is recorded, else n/a}
- repro_command: |
    {exact command}
- raw_excerpt: |
    {sanitized excerpt}
- linked_workitem: WI-{nnn} | n/a
- supersedes: E-{nnn} | none
```

**MUST**: every Finding references at least 1 Evidence; `repro_command` must be runnable by a third party or flagged as offline-limited.

**CLI helper** (writes `work/<case>/evidence/E-*.md`):

```powershell
powershell -File scripts/append-evidence.ps1 -CaseRoot work/<case> `
  -Id E-001 -Title "..." -ReproCommand "..." -Severity info -Status observed
```

When the evidence is a case-local file, pass `-ArtifactPath` to record a SHA-256 fixity value and a relative artifact path. Review the complete case graph before handoff:

```bash
python3 case-review/scripts/review_case.py work/<case> --verify-hashes --strict
```

The review is read-only and checks scope fields, Evidence records, work item and timeline references, structured Findings, Paths, and artifact hash matches.

## 2. Finding (security/reversing conclusion)

```markdown
### F-{nnn}
- title:
- severity: critical | high | medium | low | info | n/a_re
- category: vuln | misconfig | design | reverse_algo | bypass | other
- status: candidate | validated | false_positive | accepted_risk
- evidence_ids: [E-001, E-002]
- location: {file:line | addr | url | class.method}
- impact:
- confidence: high | medium | low
- repro_steps:
  1.
  2.
- remediation: {or n/a for pure RE}
- optional_attack: {ATT&CK ID or empty}
```

**MUST**: `evidence_ids` non-empty; when `status=validated`, confidence must not be low (unless residual risk is flagged).

## 3. Path (attack path / call path / solve path)

Uniformly called **Path**, interpreted by task type:

| Task | Path meaning |
|------|-----------|
| Pentest / attack chain | attack path steps |
| Reversing | key call/data-flow steps |
| CTF | solve steps |

```markdown
### P-{nnn}
- title:
- path_type: attack | callflow | solve
- start:
- goal:
- steps:
  1. action: — evidence: E-xxx — finding: F-xxx | none
  2. action: — evidence: E-xxx — finding: F-yyy | none
- residual_risks:
```

**MUST**: every step links to Evidence; a terminal-path Finding claiming "obtained access/data" requires validated evidence.

## 4. Position in the report

The `docs-generator` security report **MUST** contain:

1. Scope summary (linked to case `scope.md`)  
2. Evidence table or section  
3. Findings list (including evidence_ids)  
4. At least 1 Path (attack/call/solve)  
5. Timeline summary (optional, linking to `timeline.md`)

See the **Evidence Chain** section of `docs-generator/references/security-report-templates.md`.

## 5. field-journal Hook

When writing back to the journal, **SHOULD** excerpt:

- up to 3 key Evidence ids + commands  
- 1 core Finding  
- one sentence describing a reusable Path pattern  

Full sensitive content stays only in the user project report; the journal **MUST** be sanitized (`anonymization.md`).

## 6. Differences from Z3r0 (features)

| Z3r0 | reverse-skill |
|------|----------------|
| PG immutable rows + API | Markdown files + hash fields |
| UI review queue | report + next-step menu + journal |
| deep ATT&CK binding | optional tags, no forced UI |
