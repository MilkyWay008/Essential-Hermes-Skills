---
name: email-security
description: Use for authorized email security review including phishing analysis, header authentication (SPF/DKIM/DMARC), BEC patterns, and mailbox token abuse research.
---

# Email Security & Phishing Analysis

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Confirm authorization (analyzing sample emails / tenant config review)
2. `NOW`: Do not re-deliver malicious samples to real users
3. `ACT`: Header authentication → content/URL → attachment sandbox → tenant control plane recommendations

## When to Use

- Phishing email dissection and IOC extraction
- SPF/DKIM/DMARC configuration assessment
- BEC business email compromise patterns
- OAuth app phishing / mailbox token abuse (combine with llm/cloud identity)
- Security awareness exercise design (authorized)

## Workflow

```text
□ Full raw headers: Received chain, From/Return-Path consistency
□ SPF/DKIM/DMARC alignment results
□ URL sandboxing and attachment static analysis (combine with malware-analysis)
□ Brand impersonation and reply-address discrepancies
□ Tenant: anti-phishing policies, external labeling, MFA, OAuth app consent
```

## Toolchain

| Tool | Purpose |
|------|------|
| Mail client "View Source" | Headers |
| dig/nslookup | SPF/DMARC records |
| urlscan / sandbox | Links and attachments |
| Tenant admin center | Policies |

### Tool installation

- No pip packages required — `dig`/`nslookup` are OS utilities, not pip-installable.
- `dig` is not on Windows git-bash by default — use `nslookup`/`Resolve-DnsName` on Windows, or install `bind-utils` on Linux.
- `urlscan` is a web service (https://urlscan.io) — use the web UI or API; no local install.
- Mail client "View Source" is built into the mail client itself; no install.

## References

- `references/email-auth-checklist.md`
- `../malware-analysis/` `../attack-chain/` (phishing stage) `../windows-ad/` (tokens)

## Routing Context

**Upstream**: MASTER R36  
**MUST NOT**: Mass test phishing to third-party domains without authorization

## Task Completion Self-Check

- [ ] Is the header authentication conclusion complete?
- [ ] Are IOCs made detectable (combine with threat-hunting)?
- [ ] Checklist?
