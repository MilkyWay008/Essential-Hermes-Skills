# Expert Role → Skill Mapping (no multi-agent server)

> Role codenames are inspired by the Z3r0 expert team; the **implementation** is the reverse-skill routing and handoff protocol, not process orchestration.

## Role Table

| Code | Name (localizable) | Responsibility | PRIMARY / tool skill |
|------|------------------|------|----------------------|
| **lead** | Lead / commander | task decomposition, scope, phase gates, report consolidation | `attack-chain/` or current PRIMARY hub; wrap-up → `docs-generator/` |
| **cie** | Intelligence | asset discovery, attack surface, relationships | `pentest-tools/` (recon); browser → `browser-automation/`; cloud → `cloud-k8s/` |
| **cpe** | Penetration | scanning, exploit verification, impact confirmation | `pentest-tools/`; API → `api-security/`; AD → `windows-ad/`; wireless → `wifi-wireless/`; DB → `database-security/`; SSO → `identity-federation/`; OT → `ot-ics/` |
| **cre** | Reverse engineering | binary/firmware/mobile/frontend logic | `ida-reverse/` `ghidra-reverse/` `radare2/` `apk-reverse/` `mobile-reverse/` `macos-reverse/` `js-reverse/` `browser-extension-reverse/` `dotnet-reverse/` `go-rust-reverse/` `firmware-pentest/` `hardware-security/` `malware-analysis/` `protocol-reverse/` `thick-client/` `reverse-engineering/` |
| **cae** | Code audit | source/dependency/supply chain | `code-audit/` + `supply-chain-security/` |
| **cbe** | Blue team/forensics | hunting, detection, IR artifacts | `threat-hunting/` `digital-forensics/` |
| **cce** | Cryptography | algorithms/protocols/key misuse | `reverse-engineering` pattern docs |
| **llm** | AI security | Prompt/Agent | `llm-security/` |
| **doc** | Documentation | reports/writeups/diagrams | `docs-generator/` + `diagram-generator/` |

## Lead Mandatory Protocol

```text
1. Output PRIMARY (master-route) + lead_role=lead
2. Write scope.md (ops/scope-contract)
3. Specify specialist_roles[] and handoff conditions
4. At each phase end: update timeline + workitems; decide continue/switch role/report
5. Never skip scope and go straight to cpe scanning production
```

## Handoff Rules

| From → To | Trigger | Deliverable |
|---------|------|--------|
| lead → cie | asset surface needed | scope + known domains/IPs |
| cie → cpe | live surface/services found | assets list + ports/URLs |
| cpe → cre | reverse verification/client logic needed | sample path + suspicious points |
| cre → cpe | protocol/key/check recovered | algorithm description + repro command |
| any → doc | phase or task complete | Evidence/Finding/Path draft |
| any → lead | blocked/out-of-scope/reroute | timeline note + blocked reason |

## Single-Agent Usage (feature)

You do not need to actually spawn 6 agents:

```text
Within the same session:
  [lead] plan
  [cie] run recon skills
  [cpe] switch to pentest-tools
  …
Prefix outputs with the role tag for easy timeline retrieval:
  [cpe] nuclei high findings → E-003
```

## Relationship to master-route

- `master-route` picks the **PRIMARY skill**  
- `role-map` decides **who is responsible for the current phase** (may go in scope.md)  
- For multi-phase tasks the PRIMARY is usually `attack-chain/`, re-dispatched by the lead  

## MUST NOT

- Do not assume a Z3r0 session API exists  
- Do not start additional scans against unauthorized targets for any role  
