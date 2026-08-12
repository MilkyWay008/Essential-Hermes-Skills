---
name: code-audit
description: Use for authorized source-code security review and SAST workflows including Semgrep, CodeQL patterns, dangerous API hunting, and fix verification.
---

# Source Code Security Audit

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` or the code audit authorization
2. `NOW`: confirm **source/repository access** (binary without source → route to RE skill)
3. `NOW`: clarify the language stack and scope (directory/service/PR diff)
4. `NEXT`: tool-index; semgrep etc.
5. `ACT`: threat model sketch → automated scan → manual verification

## Applicable Scenarios

- White-box audits, PR/diff security review
- SAST with Semgrep / CodeQL / Bandit / gosec etc.
- Dangerous APIs, injection points, missing auth, crypto misuse
- Division with `supply-chain-security/`: this skill focuses on **first-party code logic**, supply-chain focuses on dependencies and pipelines

## Workflow

### 1. Scope and Threat Model

```text
□ Trust boundaries: user input, files, deserialization, SSRF, auth middleware
□ High-value assets: auth, payments, admin consoles, key handling
```

### 2. Automated Scanning

```bash
semgrep --config auto .
# or project ruleset
semgrep --config p/owasp-top-ten .
```

### 3. Manual Verification (MUST)

```text
□ Each SAST hit: reachable? exploitable? false positive?
□ Auth: IDOR/privilege escalation, missing validation, broken multi-tenant isolation
□ Injection: SQL/command/template/LDAP
□ Crypto: hardcoded keys, ECB, custom crypto
```

### 4. Deliverables

```text
Finding: location + data flow + PoC + fix suggestion
Optional ATT&CK / CWE identifiers
```

## Toolchain

| Tool | Language/Scenario |
|------|-----------|
| Semgrep | multi-language fast rules |
| CodeQL | deep data flow (GitHub) |
| Bandit | Python |
| gosec / staticcheck | Go |
| SpotBugs / FindSecBugs | Java |

### Tool installation

- Semgrep: `pip install semgrep` (or the Docker image `returntocorp/semgrep`).
- Bandit: `pip install bandit`.
- gosec: `go install github.com/securego/gosec/v2/cmd/gosec@latest` (not a pip package).
- CodeQL: CLI bundle from https://github.com/github/codeql-cli-binaries/releases (some queries need a GitHub token).
- SpotBugs / FindSecBugs: from https://spotbugs.github.io/ (Java; not pip).

## References

- `references/sast-review-checklist.md`
- `../supply-chain-security/` `../api-security/` `../llm-security/` (Agent code)

## Routing Context

**Upstream**: MASTER R26  
**Role**: `ops/role-map.md` cae  
**Downstream**: dependency vulnerabilities → supply-chain; runtime verification → pentest-tools

## Task Completion Self-Check

- [ ] Was manual verification done rather than just pasting scanner output?
- [ ] Do findings include fix suggestions?
- [ ] Is it limited to authorized repositories?
- [ ] Checklist?