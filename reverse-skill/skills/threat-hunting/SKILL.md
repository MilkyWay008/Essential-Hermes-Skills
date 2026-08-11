---
name: threat-hunting
description: Use for blue-team threat hunting, detection engineering with Sigma/YARA, SIEM query design, and incident detection validation.
---

# Threat Hunting & Detection Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm blue-team/hunting authorization and data source scope (SIEM, EDR exports)
2. `NOW`: define a hypothesis before querying data; avoid mindlessly churning alerts
3. `NEXT`: tools and data access methods
4. `ACT`: hypothesis → query → validate → rule

## Applicable Scenarios

- Threat hunting (hypothesis-driven)
- Sigma / YARA detection engineering
- Alert tuning, false-positive analysis
- With `malware-analysis/`: sample-side IOCs → this skill operationalizes detection
- With `digital-forensics/`: case artifacts → lateral hunting

## Workflow

### 1. Build a Hypothesis

```text
Example: attacker uses living-off-the-land for lateral movement
→ Data sources: Sysmon 1/3/10, Windows Security 4624/4648
→ Success criteria: abnormal parent process or rare account logon source
```

### 2. Query and Stacking

```text
□ Baseline: normal admin behavior windows and hosts
□ Anomalies: new services, encoded PowerShell, unusual outbound traffic
□ Correlation: short-time logons from the same account across multiple hosts
```

### 3. Rule Creation

```yaml
# Sigma skeleton in malware-analysis; this skill emphasizes:
# - false-positive surface
# - data source field mapping
# - response playbook links
```

### 4. Validation

```text
□ Atomic tests (Atomic Red Team) only in authorized labs
□ Replay historical logs to validate recall
```

## Toolchain

| Tool | Purpose |
|------|------|
| Sigma CLI / sigmac | rule conversion |
| YARA | files/memory |
| SIEM (ELK/Splunk etc.) | querying |
| osquery | endpoint hunting |
| Atomic Red Team | detection validation (lab) |

## References

- `references/hunting-loop.md`
- `../malware-analysis/references/yara-sigma-rules.md`
- `../digital-forensics/`

## Routing Context

**Upstream**: MASTER R27  
**Downstream**: confirmed intrusion → forensics; malicious samples → malware-analysis  
**MUST NOT**: run attack simulations in unauthorized production environments

## Task Completion Self-Check

- [ ] Is there a clear hypothesis and conclusion?
- [ ] Do rules document false positives and data sources?
- [ ] Checklist?