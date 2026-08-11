---
name: supply-chain-security
description: Use for software supply-chain security assessment covering SBOM, SCA, CI/CD pipelines, container images, build integrity, dependency provenance, and vulnerability reachability.
---
# Supply Chain Security Testing

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md` — confirm this skill's operations are authorized routine operations
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths
4. `NEXT`: If tools are missing, call bootstrap — don't guess paths
5. `ACT`: Move to the first step of the "Workflow" and execute it — don't stop at confirmation

> SBOM / SCA / CI/CD pipelines / dependency provenance
> Regulation-driven: US executive order SBOM, China national standard, EU CRA

## Applicable Scenarios

- Software supply-chain security assessment
- Open-source dependency vulnerability scanning and validation
- CI/CD pipeline security audit
- Container image security analysis
- Third-party component compliance review
- Build artifact provenance and integrity verification

## Six-Layer Supply-Chain Governance Framework

```text
Layer 1: 源码信任评估 → 上游仓库/维护者/发布历史审查
Layer 2: 构建管道集成 → CI/CD 安全门禁、签名验证
Layer 3: 制品分发完整性 → 签名、校验和、SBOM 附加
Layer 4: 运行时保护 → 容器扫描、准入控制
Layer 5: 持续监控 → CVE 实时追踪、漏洞可达性分析
Layer 6: 事件响应 → 供应链攻击应急、回滚策略
```

## Workflow

### 1. SBOM Generation and Audit

```text
生成 SBOM：
□ CycloneDX 格式: cdxgen → bom.json
□ SPDX 格式: sbom-tool generate
□ Syft: syft <image|dir> -o spdx-json

审计要点：
□ 是否存在未知/未授权的依赖
□ 是否存在已废弃/停止维护的包
□ 许可证冲突检测
□ 直接依赖 vs 传递依赖清单
□ 每个组件的发布时间线和维护者状态
```

### 2. Software Composition Analysis (SCA)

```bash
# OSV-Scanner（免费、Google 维护）
osv-scanner scan -r . --format json

# OWASP Dependency-Track（企业级持续监控）
docker run -p 8080:8080 dependencytrack/apiserver
# → 上传 SBOM → 自动匹配 NVD/OSV/GitHub Advisory

# Snyk（商业）
snyk test --all-projects
snyk monitor  # 持续监控

# Trivy（容器 + 依赖 + IaC）
trivy fs .          # 文件系统扫描
trivy image nginx   # 容器镜像
trivy config .      # IaC 配置
```

### 3. Vulnerability Reachability Validation

```text
SCA 告警 ≠ 实际风险！大多数 SCA 工具只有 ~15% 的告警是实际可达的。

验证步骤：
1. 用 Dependency-Track 或 Trivy 获取 CVE 列表
2. 筛选 CVSS ≥ 7.0 的漏洞
3. 对有 PoC 的 CVE 做可达性分析
   - Code Property Graph 切片: 追踪用户输入到漏洞函数的路径
   - DEPTEX 方法: EPD (Execution Path Dominance) + LLM 语义验证
4. 在隔离环境中验证 PoC
5. 对可达的漏洞按实际影响排序修复优先级
```

Tool references:
- CodeQL: GitHub code querying → data-flow analysis
- Snyk Code: reachability marking
- DEPTEX: LLM-assisted context-aware risk assessment

### 4. CI/CD Pipeline Security

```text
安全检查点：
□ 代码提交 → pre-commit hook: gitleaks (密钥扫描)
□ PR 阶段 → SCA 扫描 (Trivy/OSV-Scanner)
□ 构建阶段 → 制品签名 (cosign)
□ 推送阶段 → SBOM 附加 (syft + attest)
□ 部署阶段 → 准入控制 (OPA/Kyverno + 镜像扫描)
□ 运行时 → 持续漏洞监控 (Dependency-Track)

管道自身安全：
□ Pipeline as Code 审计（GitHub Actions / GitLab CI 配置注入）
□ Runner 隔离（防止恶意构建突破容器）
□ 密钥管理（Actions Secrets / Vault，禁止硬编码）
□ 第三方 Action 审查（锁定 commit SHA，非 tag）
```

### 5. Container Image Security

```bash
# Dockerfile 审计
hadolint Dockerfile

# 镜像扫描（多层：OS + 应用依赖 + 配置）
trivy image --severity HIGH,CRITICAL nginx:latest

# 最小基础镜像
# 优先: distroless → alpine → slim → 避免 latest
docker scout quickview nginx:latest

# 镜像签名
cosign sign --key cosign.key myimage:tag
cosign verify --key cosign.pub myimage:tag
```

### 6. Third-Party Dependency Review

```text
新增依赖 Checklist：
□ 维护状态：最近 6 个月有提交？维护者活跃度？
□ 安全历史：过去有无被植入恶意代码？
□ 依赖树：引入后新增多少传递依赖？
□ 许可证：与项目许可证兼容？
□ 替代方案：有无更安全的替代（Snyk Advisor / Socket.dev 评分）？

风险评估矩阵：
  高维护 × 低依赖数 × 兼容许可证 → 低风险
  低维护 × 高依赖数 × 许可证冲突 → 高风险
```

## Toolchain

| Tool | Purpose | Source |
|------|------|------|
| OWASP Dependency-Track | enterprise-grade continuous SCA | `docker pull dependencytrack/apiserver` |
| OSV-Scanner | free SCA (OSV.dev ecosystem) | `go install github.com/google/osv-scanner` |
| Trivy | image + dependency + IaC scanning | `apt install trivy` |
| Syft | SBOM generation | `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh` |
| cdxgen | CycloneDX SBOM generation | `npm install -g @cyclonedx/cdxgen` |
| Cosign | container signing | `go install github.com/sigstore/cosign/v2/cmd/cosign` |
| Gitleaks | secret/credential scanning | `go install github.com/gitleaks/gitleaks/v8` |
| Snyk | commercial SCA + reachability | `npm install -g snyk` |
| CodeQL | code querying + data flow | built into GitHub Actions |

## References

- `references/sbom-sca-methodology.md` — SBOM + SCA methodology
- `references/cicd-pipeline-security.md` — CI/CD pipeline security audit


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
