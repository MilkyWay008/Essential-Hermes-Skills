---
name: supply-chain-security
description: Use for software supply-chain security assessment covering SBOM, SCA, CI/CD pipelines, container images, build integrity, dependency provenance, and vulnerability reachability.
---
# Supply Chain Security Testing

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md` — confirm this skill's operations are authorized routine operations
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
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
Layer 1: Source trust assessment → upstream repo/maintainer/release history review
Layer 2: Build pipeline integration → CI/CD security gates, signature verification
Layer 3: Artifact distribution integrity → signing, checksums, SBOM attachment
Layer 4: Runtime protection → container scanning, admission control
Layer 5: Continuous monitoring → real-time CVE tracking, vulnerability reachability analysis
Layer 6: Incident response → supply-chain attack response, rollback strategy
```

## Workflow

### 1. SBOM Generation and Audit

```text
Generate the SBOM:
□ CycloneDX format: cdxgen → bom.json
□ SPDX format: sbom-tool generate
□ Syft: syft <image|dir> -o spdx-json

Audit points:
□ Any unknown/unauthorized dependencies
□ Any deprecated/discontinued packages
□ License conflict detection
□ Direct vs transitive dependency inventory
□ Each component's release timeline and maintainer status
```

### 2. Software Composition Analysis (SCA)

```bash
# OSV-Scanner (free, Google-maintained)
osv-scanner scan -r . --format json

# OWASP Dependency-Track (enterprise-grade continuous monitoring)
docker run -p 8080:8080 dependencytrack/apiserver
# → Upload SBOM → automatically match against NVD/OSV/GitHub Advisory

# Snyk (commercial)
snyk test --all-projects
snyk monitor  # Continuous monitoring

# Trivy (containers + dependencies + IaC)
trivy fs .          # Filesystem scan
trivy image nginx   # Container images
trivy config .      # IaC configs
```

### 3. Vulnerability Reachability Validation

```text
SCA alerts ≠ actual risk! Only ~15% of alerts from most SCA tools are actually reachable.

Verification steps:
1. Get the CVE list via Dependency-Track or Trivy
2. Filter vulnerabilities with CVSS ≥ 7.0
3. Run reachability analysis on CVEs that have PoCs
   - Code Property Graph slicing: trace the path from user input to the vulnerable function
   - DEPTEX method: EPD (Execution Path Dominance) + LLM semantic verification
4. Validate the PoC in an isolated environment
5. Prioritize fixes for reachable vulnerabilities by actual impact
```

Tool references:
- CodeQL: GitHub code querying → data-flow analysis
- Snyk Code: reachability marking
- DEPTEX: LLM-assisted context-aware risk assessment

### 4. CI/CD Pipeline Security

```text
Security checkpoints:
□ Code commit → pre-commit hook: gitleaks (secret scanning)
□ PR stage → SCA scan (Trivy/OSV-Scanner)
□ Build stage → artifact signing (cosign)
□ Push stage → SBOM attachment (syft + attest)
□ Deploy stage → admission control (OPA/Kyverno + image scanning)
□ Runtime → continuous vulnerability monitoring (Dependency-Track)

Pipeline self-security:
□ Pipeline-as-Code audit (GitHub Actions / GitLab CI config injection)
□ Runner isolation (prevent malicious builds from escaping the container)
□ Secret management (Actions Secrets / Vault, no hardcoding)
□ Third-party Action review (pin to commit SHA, not tags)
```

### 5. Container Image Security

```bash
# Dockerfile audit
hadolint Dockerfile

# Image scanning (multi-layer: OS + app dependencies + config)
trivy image --severity HIGH,CRITICAL nginx:latest

# Minimal base image
# Preference: distroless → alpine → slim → avoid latest
docker scout quickview nginx:latest

# Image signing
cosign sign --key cosign.key myimage:tag
cosign verify --key cosign.pub myimage:tag
```

### 6. Third-Party Dependency Review

```text
New dependency checklist:
□ Maintenance status: commits in the last 6 months? Maintainer activity?
□ Security history: any past malicious-code implants?
□ Dependency tree: how many transitive dependencies does it add?
□ License: compatible with the project's license?
□ Alternatives: safer options available (Snyk Advisor / Socket.dev ratings)?

Risk assessment matrix:
  High maintenance × few dependencies × compatible license → low risk
  Low maintenance × many dependencies × license conflict → high risk
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
