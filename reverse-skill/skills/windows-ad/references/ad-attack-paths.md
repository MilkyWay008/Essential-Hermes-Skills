# AD Attack Paths Cheatsheet

| Path | Prerequisite | Tool Leads |
|------|------|----------|
| Kerberoast | SPN account | GetUserSPNs / Rubeus |
| AS-REP Roast | Pre-auth not required | GetNPUsers |
| ESC1 | Enrollable template + forgeable SAN | Certipy |
| ESC8 | HTTP enrollment + relay | ntlmrelayx |
| ACL → DA | GenericAll on user/group | BloodHound |
| NTLM Relay | Signing not enforced | Responder + relay |

Always: authorize → enumerate → score paths → minimal validation → clean up.

