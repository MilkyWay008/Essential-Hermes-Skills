---
name: windows-ad
description: Use for authorized Active Directory and Windows identity attacks including Kerberos, AD CS, BloodHound paths, NTLM relay, and domain privilege escalation research.
---

# Windows / Active Directory Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md`
2. `NOW`: **Domain/AD testing MUST have explicitly authorized scope** (including DCs, and whether poisoning/relaying is allowed)
3. `NOW`: case-init; write network_profile and prohibited actions clearly
4. `NEXT`: tool-index (impacket/certipy/bloodhound etc. are often manual)
5. `ACT`: Start with identity enumeration and BloodHound graph — do not jump straight to destructive exploitation

## When to Use

- Domain penetration, Kerberoasting, AS-REP, delegation
- AD CS certificate attacks (ESC1–ESC8 etc.)
- BloodHound / SharpHound attack paths
- NTLM Relay / Coercer forced authentication
- Local privilege escalation to domain paths (Potato etc. as a foothold)

## Relationship to attack-chain

- **Multi-stage from external network to domain controller** → PRIMARY can remain `attack-chain/`; this skill is the **AD specialty**
- **Already inside the domain, focused on identity** → PRIMARY = this skill

## Workflow

### 1. Enumeration

```bash
# Example Impacket / built-in (requires credentials and authorization)
nxc smb <range> -u user -p pass
bloodhound-python -d domain.local -u user -p pass -c All -ns <DC>
```

### 2. Common Paths (map first, shoot later)

```text
□ Kerberoast / AS-REP → offline cracking
□ ACL abuse (GenericAll/WriteDacl)
□ Delegation (unconstrained/constrained/resource-based)
□ AD CS template misconfiguration → Certipy
□ Relay: LLMNR/NBT-NS + ntlmrelayx (confirm authorization)
```

### 3. Credentials & Lateral Movement

```text
□ secretsdump / lsassy / mimikatz (strict authorization and cleanup)
□ PtH / PtT / golden tickets only within authorized red team scope
□ Write Evidence for every step; wait for user confirmation on high-risk actions
```

## Toolchain

| Tool | Purpose |
|------|------|
| BloodHound / SharpHound | Path mapping |
| Certipy | AD CS |
| Impacket / NetExec | Lateral movement & enumeration |
| Rubeus / Mimikatz | Tickets & credentials (authorized) |
| Coercer / Responder | Forced authentication / poisoning |

## References

- `references/ad-attack-paths.md`
- `../pentest-tools/references/network-attack-defense.md`
- `../attack-chain/`
- seeds: `../field-journal/seed-005_ad-certipy-esc1.md` `../field-journal/seed-007_ntlm-relay-coercer.md` `../field-journal/seed-013_kerberoasting-spn.md`

## Routing Context

**Upstream**: MASTER R24  
**Downstream**: report `docs-generator`; EDR research `edr-bypass-re`  
**MUST NOT**: DCSync / golden tickets against production without authorization

## Task Completion Self-Check

- [ ] Was the graph/enumeration done before exploitation?
- [ ] Were reproducible commands recorded and redacted?
- [ ] Were scope prohibitions respected?
- [ ] Checklist?
