# Timeline + WorkItem / Coverage

> Replayable operation log (Z3r0 timeline concept) + coverage checkboxes (WorkItem concept).  
> Everything lives under **`work/<case>/`** (gitignored in the repo), not in the skill-pack body.

## Directory Conventions

```text
work/<case>/
  scope.md           # contract (ops/scope-contract.md)
  timeline.md        # append-only; never rewrite history
  workitems.md       # work items & coverage
  evidence/          # raw artifacts (screenshots, pcap, logs)
  notes/
  report/            # final report draft or copy
```

Initialize:

```powershell
powershell -File skills\scripts\case-init.ps1 -Hint "full pentest" -CaseName "acme-2026"
```

## timeline.md Format

Every entry **appends only**:

```markdown
## {ISO-8601} | {role} | {phase}
- action:
- command_or_ref:
- result_summary:
- artifacts: []      # relative paths under this case
- evidence_ids: []   # E-xxx when promoted
- next:
```

**MUST NOT** delete or rewrite existing `##` time blocks (correct via a new entry + `corrects: {timestamp}`).

## workitems.md Template

```markdown
# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Port scan edge | cie | {ip} | network | done | E-001 | |
| WI-002 | Auth bypass check | cpe | /api/login | web | blocked | | need creds |

status: pending | in_progress | blocked | done | cancelled

## Coverage
- [ ] Recon complete for in_scope assets
- [ ] Critical/High candidates triaged
- [ ] Validated findings have Evidence
- [ ] Path documented (attack/call/solve)
- [ ] Timeline continuous (no silent gaps >1 major phase)
- [ ] Report exported via docs-generator
- [ ] field-journal written (anonymized)
```

## attack-chain / pentest Hooks

| Skill | MUST |
|-------|------|
| `attack-chain/` | multi-stage tasks create a case dir; update workitems + timeline at each phase end |
| `pentest-tools/` | at least 1 timeline entry per tool batch; findings → Evidence draft |
| other RE skills | timeline recommended; at minimum complete the Evidence chain before reporting |

## Highlights

- Agent-friendly plain text; diff/review friendly  
- Cross-references tool-index command paths  
- No WebSocket dependency; paste the timeline into the report when needed  
