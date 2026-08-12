# Community Security-Skill Ecosystem Survey (2026-07)

> Source retrieval date: **2026-07-17**  
> Purpose: let reverse-skill **know what's out there**, borrow on demand, and **NOT** merge external mega-repositories wholesale into this pack.  
> This pack's identity: routing + tool bootstrap + evidence/scope contracts + field-journal (see `ops/IDENTITY.md`).

## 1. External High-Value Repositories (learn, don't blind-install)

| Repository | Scale / Positioning | Value to This Pack | Risk |
|------|-----------|------------|------|
| [trailofbits/skills](https://github.com/trailofbits/skills) | ToB security-research Claude plugin marketplace | Quality benchmark for audit / vuln-analysis / RE plugins | Must install via the ToB marketplace; don't trust non-curated copies by default |
| [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated) | Audited plugin list | Preferred over any community skill | Same as above |
| [Orizon-eu/claude-code-pentest](https://github.com/Orizon-eu/claude-code-pentest) | 6 pentest-lifecycle skills + pure-Python scripts | Recon->exploit->report pipeline comparable to our `attack-chain`+`pentest-tools` | Verify authorization boundaries yourself; scripts need sandboxing |
| [trilwu/secskills](https://github.com/trilwu/secskills) | 16 skills + 6 expert subagents | Multi-role division comparable to `ops/role-map.md` | Plugin-shaped, unlike this pack's monorepo |
| [Masriyan/Claude-Code-CyberSecurity-Skill](https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill) | ~15-19 domain skills (incl. RE/OT/CSOC) | Domain-coverage checklist | Shallower than this pack's per-domain skills |
| [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | **800+** skills · ATT&CK/NIST mapping | **Framework mapping** and domain catalog are referable; don't depend on the whole repo | Too large; huge maintenance and poisoning surface |
| [Eyadkelleh/awesome-skills-security](https://github.com/Eyadkelleh/awesome-claude-skills-security) | SecLists packaged as agent skills | Dictionary/payload entry point | Overlaps with the seclists bootstrap |
| [securityfortech/awesome-security-skills](https://github.com/securityfortech/awesome-security-skills) | Curated list of security skills | Index for discovering new skills | List-style; needs per-item auditing |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 1000+ cross-vendor skill index | Discover official/community skills | Not security-specific |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | PR security-review GitHub Action | Comparable to our docs/report-side "change audit" scenario | A CI product, not an RE router |
| [agentskills.io](https://agentskills.io) | Open Agent Skills standard | Aligns frontmatter/directory conventions | The standard itself has no offense/defense content |

### 1.1 Second-Round Retrieval Additions (re-searched 2026-07-17)

| Repository / Resource | Positioning | Landing Spot in This Pack |
|-------------|------|----------|
| [trailofbits/skills](https://github.com/trailofbits/skills) plugins: `audit-context-building` `differential-review` `semgrep-rule-creator` `sharp-edges` `dwarf-expert` `burpsuite-project-parser` | Audit context, differential security review, dangerous APIs, DWARF, Burp project parsing | Compare against `ida-reverse`/`docs-generator`/audit workflows; **do not** merge the whole repo |
| [HexRaysSA/ida-claude-code-plugins](https://github.com/HexRaysSA/ida-claude-code-plugins) | Official IDA Claude plugins (incl. domain automation, marked unsafe) | Reference for `ida-reverse` MCP paths; unsafe plugins disabled by default |
| [P4nda0s/reverse-skills](https://github.com/P4nda0s/reverse-skills) | IDA-NO-MCP: export decompilation then analyze; rev-frida/dex-dump/u3d | Complements "offline export when MCP is unavailable" |
| [2389-research/binary-re](https://github.com/2389-research/binary-re) | triage->static(r2/Ghidra)->dynamic(QEMU/GDB/Frida)->synthesis | `reverse-engineering` stage gates in `re-agent-workflow.md` |
| [incogbyte/android-reverse-engineering-claude-skill](https://github.com/incogbyte/android-reverse-engineering-claude-skill) | APK unpacking, endpoint extraction, adaptive Frida bypass | Compare against `apk-reverse`; dynamic scripts need scope |
| [OwenPawl/cerberus-re-skill](https://github.com/OwenPawl/cerberus-re-skill) | Apple-oriented Ghidra+LLDB+Frida triple loop | Referable for macOS/iOS dynamic loops |
| [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) | CTF reverse/pwn; tools installed on demand | Compare against CTF-Sandbox + `pwn-chain` |
| [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty) | /recon->/hunt->/validate->/report | Compare against `recon-pipeline.md` + scope gate |
| [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | Web payloads + Prompt Injection chapter | `pentest-tools/payloads` first; LLM topics in `llm-security` |
| [HackTricks](https://hacktricks.wiki/) | Pentest methodology + **AI/MCP abuse** | See the MCP section of skill-supply-chain |
| [appsecsanta AI pentesting agents 2026](https://appsecsanta.com/research/ai-pentesting-agents-2026) | Taxonomy of 39+ open-source AI pentesting agent architectures | Multi-agent != mandatory; we use role-map |
| Snyk eval "more skills != better" | Skill stacking can lower audit quality | Reinforces the "deep skills + routing" strategy |

## 2. Security Standards and Threats (2025-2026)

| Source | Key Points | Landing Spot in This Pack |
|------|------|----------|
| [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) | Malicious skills, supply chain, permission abuse, memory poisoning, etc. | `ops/skill-supply-chain.md` |
| [Anthropic Agent Skills engineering post](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Install only trusted sources; review scripts and dependencies | Same as above + bootstrap must not guess paths |
| ClawHavoc and other poisoning campaigns (documented in AST10) | Mass malicious skills in registries | Never one-click install from unknown registries into this pack |

## 3. What This Pack Has vs External "Broad" Coverage

| Domain | reverse-skill | Why external broad coverage isn't merged wholesale |
|------|---------------|--------------------------------|
| APK/JS/IDA/r2/firmware/pwn | **Deep** skills + scripts | Keeps depth bound to tool-index |
| Pentest / attack chains / SRC | pentest-tools + attack-chain + src-hunter | Orizon-like packs serve as methodology references |
| LLM/Agent security | llm-security | AST10 hardens the skills themselves |
| Evidence / scope / roles | **ops/** (a differentiator) | Most skill packs lack case contracts |
| OT/ICS / pure GRC / fraud F3 | No standalone skill | Routing miss -> propose new or link out, don't force it in |
| 800+ micro-skills | Not copied | MASTER routing + domain skills replace fragmentation |

## 4. Borrowing Rules (MUST)

```text
1. Forbidden: pulling 800+ skills as a git submodule runtime dependency
2. When borrowing: extract "stages/checklists/command patterns" into this pack's references or existing skills
3. External scripts: inspect dependencies and network behavior in an isolated environment before considering bootstrap-manifest
4. New scenarios: add skills via CONTRIBUTING, and update routing + RULES keywords
5. Record source URL + retrieval date (this file's format)
6. Run the ops/skill-supply-chain.md checklist before installing/merging
7. At runtime load only MASTER-ROUTING's PRIMARY (+ necessary secondaries) to avoid skill-stacking overload
```

## 4.1 Borrowed Artifacts This Pack Has Solidified (not external dependencies)

| Artifact | Path |
|------|------|
| RE four stages | `reverse-engineering/references/re-agent-workflow.md` |
| Authorized recon | `pentest-tools/references/recon-pipeline.md` |
| Attack-chain gates | `attack-chain/references/lifecycle-checklist.md` |
| Skill supply chain | `ops/skill-supply-chain.md` |
| Domain coverage | `references/domain-coverage-map.md` |

## 5. Suggested Priorities (future iterations)

| Priority | Action |
|--------|------|
| P0 done | ops contracts, MASTER routing, skill supply-chain security docs |
| P1 | Add pentest phase checklists to attack-chain references, modeled on Orizon/ToB |
| P2 | Optional "external-skill allowlist" config, not on the default path |
