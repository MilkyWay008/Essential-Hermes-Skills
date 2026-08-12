# Penetration/Attack Chain Lifecycle Checklist

> Cross-referenced with community pentest skill packs (e.g. Orizon's six-phase AI pentest skill) and integrated with this pack's `attack-chain` + `ops`.  
> Inspirational source: public AI-agent pentest lifecycle skills (retrieved 2026-07); **commands and authorization follow this pack's scope**.  
> Date: 2026-07-17

## Before Use

- [ ] `case-init` done, `auth.status=granted`
- [ ] `network_profile` not misused as unrestricted against production
- [ ] `lead` has assigned specialist_roles (`ops/role-map.md`)

## Phase Gates

| Phase | Role | Pack skill | Completion criteria |
|------|------|------------|----------|
| 0 Scope | lead | ops/scope-contract | ready_for_act |
| 1 Recon | cie | pentest-tools | assets list + timeline |
| 2 Enum/Vuln | cpe | pentest-tools / api-security | candidate F-* drafts |
| 3 Validate | cpe | pentest-tools | E-* + validated Finding |
| 4 Post-ex (if authorized) | cpe/lead | attack-chain second half | stays in scope |
| 5 RE support | cre | ida/apk/js/… | only when client/binary needed |
| 6 Report | doc | docs-generator | Evidence→Finding→Path |
| 7 Journal | lead | field-journal | desensitized |

## Differences From "Give Me a Domain, Automate It to Pwned" Style Skills (differentiators)

| Common in external automation packs | reverse-skill |
|------------------|---------------|
| Default to blasting the domain | Scope asset list required |
| Weak evidence goes straight into reports | E/F/P chain enforced |
| Single session, no roles | role-map handoffs |
| No tool index | tool-index + bootstrap |

## At Least One Timeline Entry Per Phase

Format per `ops/timeline-workitem.md`.

