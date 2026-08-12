# Generic Scope Contract (hard gate before task start)

> **MUST**: every security/reversing/pentest task materializes `scope.md` in the user project or `work/<case>/` **before ACT**.  
> No scope → only doc/routing reads allowed; **forbidden** to actively scan, hook, or exploit targets.  
> Template is copyable; field names keep English keys for script validation.

## How to Initialize

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills\scripts\case-init.ps1 -Hint "<one-line task description>" -CaseName "my-case"
# Default output: work/<case>/scope.md etc. in the current analysis project
# When invoking the skill from another directory, specify explicitly: -ProjectRoot "C:\path\to\analysis-project"
```

## Full scope.md Template

```markdown
# Case Scope

## meta
- case_id: {YYYYMMDD-short}
- created: {ISO-8601}
- operator: {name or local}
- primary_skill: {from master-route}
- lead_role: lead   # see ops/role-map.md
- specialist_roles: []  # e.g. cie, cpe, cre

## auth
- status: granted | pending | denied
- basis: written_contract | bug_bounty_scope | ctf_public | own_system | lab_only
- evidence_of_auth: {ticket/path or "CTF public" or "owner-operated"}
- MUST NOT proceed if status != granted

## in_scope
- assets: []          # hosts, domains, APK paths, binaries, URLs
- surfaces: []        # web, mobile, binary, network, api
- activities: []      # recon, reverse, exploit_validate, report

## out_of_scope
- assets: []
- activities: []      # e.g. DoS, phishing real users, data exfil

## network_profile
- mode: offline | lab_only | authorized_target_only | unrestricted_lab
- notes: |
    offline = no outbound packets (purely static/local samples)
    lab_only = lab/VM IPs only
    authorized_target_only = in_scope assets only
- MUST NOT use unrestricted against production without written auth

## deliverables
- report: true
- field_journal: true
- diagrams: true
- timeline: true

## constraints
- timebox: {}
- stealth: low | medium | high
- data_handling: anonymize | no_user_pii

## signoff
- ready_for_act: false
- checklist:
  - [ ] auth.status = granted
  - [ ] in_scope.assets non-empty OR offline sample path set
  - [ ] network_profile.mode chosen
  - [ ] out_of_scope reviewed
```

## Routing Hooks (AI MUST execute)

```text
RULES / MASTER-ROUTING / SKILL:
  1) master-route → PRIMARY
  2) case-init or hand-write scope.md
  3) auth not granted → STOP; only authorization materials may be added
  4) ready_for_act = true → open PRIMARY SKILL.md → ACT
```

## network_profile Quick Reference

| mode | allowed | forbidden |
|------|------|------|
| `offline` | static analysis, local files, simulation | any external connection, public RPC |
| `lab_only` | lab/CTF target ranges | production/unauthorized IPs |
| `authorized_target_only` | in_scope list | assets outside the list |
| `unrestricted_lab` | isolated lab network (written) | internet production |

## Highlights

- Pure Markdown, **no database**  
- Orthogonal to `tool-index` / bootstrap: scope governs "may we attack", tool-index governs "with what"
