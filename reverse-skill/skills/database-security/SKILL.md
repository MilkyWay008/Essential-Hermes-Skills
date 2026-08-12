---
name: database-security
description: Use for authorized database security assessment covering PostgreSQL/MySQL/MSSQL/Mongo/Redis exposure, authz, UDF/command paths, and misconfiguration review.
---

# Database Security Assessment

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read precedent-pentest; **destructive statements are forbidden on production databases** unless explicitly permitted
2. `NOW`: Write the scope clearly: instances, account permissions, whether writes/deletes are allowed
3. `NEXT`: Client tool paths
4. `ACT`: Exposure surface → authentication → authorization → configuration → exploitation chain verification (safe)

## Applicable Scenarios

- Databases with no auth / weak passwords / misbound to 0.0.0.0
- Excessive privileges, dangerous features (xp_cmdshell, COPY PROGRAM, UDF)
- Lateral movement: from application account to DBA
- NoSQL injection and Redis file writes, etc. (authorized environments)

## Workflow

```text
□ Network exposure and TLS
□ Account roles and grantees
□ Access control on sensitive tables
□ Dangerous configuration: file_priv, xp_cmdshell, load_file
□ Whether audit logging is enabled
□ Backup and snapshot permissions
```

## Toolchain

| Tool | Purpose |
|------|------|
| Official CLI | connection and enumeration |
| sqlmap | injection verification (authorized) |
| nuclei | known exposure templates |
| Cloud RDS console audit | configuration |

### Tool installation

- `sqlmap`: `pip install sqlmap` (or `apt install sqlmap` on Debian/Ubuntu).
- `nuclei`: `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest`, or a prebuilt release from https://github.com/projectdiscovery/nuclei/releases.
- Official DB CLIs (`psql`, `mysql`/`mysqlsh`, `sqlcmd`, `mongosh`, `redis-cli`) come from each vendor's installer or distro packages — not pip.

## References

- `references/db-misconfig-checklist.md`
- `../pentest-tools/` `../cloud-k8s/`

## Routing Context

**Upstream**: MASTER R35  
**Downstream**: OS command access → attack-chain; cloud-hosted → cloud-k8s

## Task Completion Self-Check

- [ ] Did you avoid unauthorized writes/deletes?
- [ ] Did you distinguish configuration issues from exploitable chains?
- [ ] Checklist?
