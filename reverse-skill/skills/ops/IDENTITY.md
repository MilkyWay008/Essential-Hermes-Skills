# reverse-skill Identity Manifesto (relative to Z3r0)

> This file pins down **who we are**. It absorbs Z3r0's evidence/scope/division-of-labor/timeline ideas, but it is **not** built into a Z3r0 platform.

## Who we are

| Dimension | reverse-skill |
|------|----------------|
| Form | **Skill routing pack** — methodology + tool bootstrap for any AI client (e.g. Hermes Agent) |
| Entry | `RULES.md` → `MASTER-ROUTING` / `master-route.ps1` → sub-skill |
| Tool truth | `tool-index.md` + `bootstrap-manifest.json` (local paths, no guessing) |
| Evolution | de-identified experience written back to `field-journal/` |
| Output | Markdown reports + local working directory `work/<case>/` (gitignored) |
| Deployment | `git clone` is enough; no mandatory PG/UI/Docker pool |

## What we are not

| Z3r0 has | reverse-skill **deliberately does not do** |
|---------|---------------------------|
| React war console | ❌ |
| FastAPI control plane + WebSocket sessions | ❌ |
| PostgreSQL evidence database | ❌ |
| LightRAG service | ❌ |
| Docker host pool / noVNC control proxy | ❌ (may **document** recommended optional sandbox profiles) |
| Multi-agent process runtime | ❌ (only **role→skill mapping + handoff protocol**) |

## What we learn from Z3r0 (scaled-down implementation)

| Idea | reverse-skill form |
|------|-------------------|
| Authorization and project boundaries | `ops/scope-contract.md` → per-case `scope.md` |
| Evidence→Finding→Path | `ops/evidence-finding-path.md` + report template |
| Expert division of labor | `ops/role-map.md` (Lead/cie/cpe/cre…→ skill) |
| Replayability | append-only `work/<case>/timeline.md` |
| WorkItem/coverage | `workitems.md` + coverage checkboxes |
| Sandbox tooling ready | `ops/sandbox-profile.md` vs bootstrap-manifest |
| Outbound control | `network_profile` field (offline/lab/authorized) |

## Distinguishing features (must keep)

1. **Three-axis routing + PRIMARY fast path** (target type / intent / toolchain)  
2. **bootstrap installs tools on demand** across Windows/Kali/Linux/macOS  
3. **MCP friendly** (IDA/Burp/jshook/anything-analyzer)  
4. **field-journal de-identified evolution**  
5. **Compliance engineering**: ACTION REQUIRED / completion self-check / no fake stopping  

## Healthy relationship with Z3r0

```text
Z3r0 = 红队操作系统 / 团队协作平台
reverse-skill = Agent 的安全作业路由器 + 说明书

可选未来：把本包 skill 内容挂进 Z3r0 sandbox-local skills
当前：零依赖 Z3r0 安装即可完整工作
```

## Relationship with the "800+ community micro-skills"

- **Do not** submodule giant skill libraries (poisoning surface and maintenance cost; see `skill-supply-chain.md`)  
- **Do** maintain `references/community-security-skills.md` as an index and reference rule  
- **Do** use `domain-coverage-map.md` to prove: deep skills + routing > fragmented skill stacking  
- External skill installation: AST10 mindset + only trust curated sources (e.g. Trail of Bits curated)  
