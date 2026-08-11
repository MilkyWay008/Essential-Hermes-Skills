---
name: identity-federation
description: Use for authorized assessment of federated identity systems including SAML, OIDC, OAuth2 flows, SSO misconfiguration, and token confusion issues.
---

# Identity Federation (SAML / OIDC / OAuth)

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read precedent-pentest; bring SSO test accounts and IdP/SP scope into scope
2. `NOW`: No brute-force attempts that lock out real user accounts
3. `NEXT`: Packet-capture tools and documentation (metadata URLs)
4. `ACT`: Protocol flow mapping → common misconfigurations → verification

## Applicable Scenarios

- SAML Response signature / assertion tampering surface (classic flaw pattern)
- OIDC implicit / authorization code flows missing PKCE
- redirect_uri / state / nonce issues
- IdP vs SP metadata, multi-tenant issuer confusion
- Complementary to `api-security` JWT attacks (this skill focuses on federation and SSO flows)

## Workflow

```text
□ Map the flow: User → SP → IdP → Token → SP
□ Collect: /.well-known/openid-configuration, SAML metadata
□ Check: exact redirect_uri matching, state binding, PKCE
□ Check: SAML signature coverage scope, algorithm downgrade
□ Session fixation and logout invalidation
```

## Toolchain

| Tool | Purpose |
|------|------|
| Burp + SAML Raider, etc. | Assertion editing (authorized) |
| jwt_tool | JWT segments |
| Browser DevTools | Redirect chains |
| IdP admin logs | Audit |

## References

- `references/sso-flow-checklist.md`
- `../api-security/` `../windows-ad/` (enterprise IdP)

## Routing Context

**Upstream**: MASTER R37  
**Downstream**: pure API JWT → api-security; cloud IdP → cloud-k8s

## Task Completion Self-Check

- [ ] Was the complete SSO flow mapped?
- [ ] Does every finding have reproduction steps and impact?
- [ ] Checklist?
