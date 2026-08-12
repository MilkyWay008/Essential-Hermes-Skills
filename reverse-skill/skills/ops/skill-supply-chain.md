# Agent Skill Supply-Chain Security (this package's hallmark)

> Sources combined: OWASP Agentic Skills Top 10 (AST10), Anthropic Agent Skills security recommendations, public poisoning incidents (e.g. ClawHavoc, see the AST10 timeline)  
> Retrieved: 2026-07-17  
> Applies when installing/writing/merging **any** skill, MCP, or bootstrap script

Static audit of this package's **executable script surface** (backdoors / database deletion / pipe execution): [`docs/PACKAGE-SECURITY-AUDIT.md`](../../docs/PACKAGE-SECURITY-AUDIT.md).

## 1. Why reverse-skill manages this separately

This package will:

- Direct AI to **execute commands and bootstrap downloads**
- Touch local and network resources through MCP  
- Write to field-journal / reports  

Malicious skills can cause: credential theft, persistent prompt injection, supply-chain backdoors.  
We use **documentation latches + tool truth sources** instead of building another skill app store.

## 2. Threat mapping (condensed AST10 thinking)

| Risk class | Manifestation | This package's control |
|--------|------|----------|
| Malicious/poisoned skill | Induce exfiltration, write memory/backdoors | Only trust this repo + user-authorized external sources; manually read the external SKILL.md and scripts first |
| Excessive permissions | Indiscriminate `curl \| bash`, full-disk reads | bootstrap only with manifest capabilities; scope `network_profile` |
| Dependency poisoning | Malicious pip/npm packages | Prefer official releases; record versions in tool-index |
| Blind MCP trust | Unaudited MCP servers | tool-index registration status + port probing; no default trust in remote MCP |
| MCP/CLI auto-execution poisoning | A repo `.env` rewriting agent home/config env vars so a malicious MCP executes on startup (HackTricks / CVE-class cases) | Don't trust in-repo default MCP config; check env and the MCP list before starting the agent |
| Prompt injection into skills | Hidden instructions in the SKILL.md body | Review diffs; forbid "execution instructions hidden in HTML comments" without user consent |
| Scope drift | Skills induce expanded scanning / "one domain fully auto-pwned" | ops/scope-contract: out_of_scope + auth; no wild scans without in_scope |
| Skill-stacking overload | Mounting too many skills at once causes missed detections (observed in public evaluations) | Only load PRIMARY + necessary secondary (MASTER-ROUTING) |

## 3. MUST checklist for installing external skills

```text
□ 来源：官方 org / 已审计列表（如 ToB curated）/ 用户自有
□ 阅读全部 SKILL.md + scripts/* + package 依赖
□ 无神秘外连、无读取 ~/.ssh / 浏览器库 的默认步骤
□ 与本包路由冲突时：以本包 MASTER-ROUTING + scope 为准
□ 不复制进 monorepo 除非走 CONTRIBUTING 与脱敏
□ 更新 skills/references/community-security-skills.md 记录来源日期
```

## 4. Boundaries with bootstrap / MCP

| Action | Allowed | Forbidden |
|------|------|------|
| `bootstrap-reverse.ps1 -Capability X` | X ∈ bootstrap-manifest.json | Any new name without updating the manifest |
| Register MCP | User confirmation + tool-index refresh | Silently writing global MCP pointing at unknown URLs |
| Run community one-click Python pentest | Authorized lab + after reading the source | Directly against production targets + unknown scripts |

## 5. Authors/contributors of this package

- New skill: CONTRIBUTING + ACTION REQUIRED + completion self-check  
- Citing community content: note URL + date (this file / community-security-skills.md)  
- On suspicious behavior: stop execution, inform the user, never auto-"try to bypass"  

## 6. Quick self-check (before merging any external material)

```powershell
# 列出将引入的脚本扩展名
Get-ChildItem -Recurse -Include *.ps1,*.sh,*.py,*.js | Select-Object FullName
# 粗搜危险模式（人工复核，非完备）
# 在外部目录执行：Select-String -Pattern 'Invoke-WebRequest|curl .\\||wget .\\||~/.ssh|exfil'
```

## 7. Related

- Identity: `IDENTITY.md`  
- External directory: `../references/community-security-skills.md`  
- Authorization: `scope-contract.md` + `field-journal/precedent-auth.md`  
