# SBOM + SCA Methodology

## SBOM Standard Comparison

| Standard | Format | Ecosystem | Recommended use |
|------|------|------|---------|
| SPDX | JSON/YAML/tag-value | Linux Foundation, Yocto | License compliance first |
| CycloneDX | JSON/XML | OWASP, Kubernetes | Security analysis first |
| SWID | XML | ISO standard | Enterprise asset management |

## SBOM Generation Toolchain

```bash
# cdxgen: generate CycloneDX SBOM from source
cdxgen -o bom.json -t cyclonedx

# Syft: generate from containers/filesystems
syft nginx:latest -o spdx-json > sbom.spdx.json

# SBOM-Tool: Microsoft toolchain
sbom-tool generate -b ./build -bc ./src -pn MyApp -pv 1.0
```

## SCA Tool Comparison

| Tool | Free | Speed | Database | Reachability |
|------|:--:|------|--------|:--:|
| OSV-Scanner | ✅ | very fast | OSV.dev | ❌ |
| Trivy | ✅ | fast | multi-source | ❌ |
| Dependency-Track | ✅ | medium | NVD+OSV+GitHub | ❌ (needs plugin) |
| Snyk | ❌ | medium | proprietary | ✅ |
| CodeQL | ✅ | slow | code-level | ✅ |

## Vulnerability Prioritization Strategy

```
CVSS ≥ 9.0 + public PoC + reachable → P0 fix immediately
CVSS ≥ 7.0 + PoC + reachable → P1 fix this week
CVSS ≥ 7.0 + no PoC or unreachable → P2 fix next iteration
Everything else → normal process
```

## Three-Step Manual Verification

```bash
# 1. Confirm the version (don't blindly trust SBOM fields)
# in container: dpkg -l | grep <package>
# Node: cat node_modules/<pkg>/package.json | jq .version
# Python: pip show <package>

# 2. Confirm the vulnerability
# search CVE: https://osv.dev / https://nvd.nist.gov
# check the affected version range
# find GitHub Advisory / oss-security mailing list

# 3. Verify impact
# search public PoCs: GitHub/Exploit-DB
# analyze exploit conditions: auth required? local access? specific config?
# verify in an isolated environment: docker run --rm -it vulnerable-image bash
```

## Continuous Monitoring

```yaml
# daily SBOM refresh + scan
schedule:
  - cron: "0 6 * * *"  # every day at 6 AM
    steps:
      - cdxgen -o bom.json
      - osv-scanner scan --sbom bom.json
      - trivy fs --exit-code 1 --severity CRITICAL .
```

Source: OWASP CycloneDX, SPDX, Google OSV, CISA SBOM Guidance

