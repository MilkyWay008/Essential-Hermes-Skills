# CI/CD Pipeline Security Audit

## Pipeline Attack Surface

```text
Threat model (STRIDE):
□ Spoofing: forged builds/signatures/sources
□ Tampering: modified source code/build artifacts/dependencies
□ Repudiation: malicious actions with no audit log
□ Information disclosure: pipeline logs/build artifacts leaking secrets
□ Denial of service: exhausting CI resources/breaking builds
□ Elevation of privilege: runner escape/secret theft
```

## Audit Checklist

### 1. Pipeline as Code Configuration

```yaml
# GitHub Actions audit points
# ❌ dangerous patterns
on:
  pull_request_target:  # PR-triggered with secrets access
    types: [opened]

# ❌ script injection
- run: echo "${{ github.event.issue.title }}"  # user input → shell

# ❌ unrestricted token permissions
permissions: write-all

# ✅ safe patterns
on:
  pull_request:  # no secrets access
    types: [opened]

# ✅ pin to SHA
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

# ✅ least privilege
permissions:
  contents: read
```

### 2. Secret Management

```bash
# scan historical commits for secrets
gitleaks detect --source . --verbose
trufflehog git file://. --only-verified

# check Actions Secrets usage
gh secret list
# confirm: no hardcoded secrets, regular rotation, least privilege

# runtime secret injection
# ✅ use OIDC instead of long-lived secrets
# ✅ expose secrets only to specific steps when needed
```

### 3. Build Integrity

```bash
# build provenance
# generate tamper-evident build records (SLSA L2+)
slsa-provenance generate --source . --output provenance.json

# artifact signing
cosign sign-blob --key cosign.key artifact.tar.gz

# verification
cosign verify-blob --key cosign.pub --signature artifact.tar.gz.sig artifact.tar.gz
```

### 4. Runner Security

```text
□ GitHub-hosted runner? (recommended, fresh environment every time)
□ Self-hosted runner: running in an isolated VM/container?
□ Has it ever run fork PRs? (extremely high risk for self-hosted runners)
□ Does the runner have network egress restrictions?
□ Can build caches leak across builds?
```

### 5. Dependency Fetch Security

```text
□ npm: is package-lock.json committed? Forbid --force / --legacy-peer-deps
□ pip: are requirements.txt versions pinned? Forbid pip install <unverified source>
□ Docker: is FROM pinned to a digest? Forbid latest tag
□ Go: is go.sum committed?
□ Private packages: does registry auth use short-lived tokens?
```

## Automated Check Pipeline

```yaml
# .github/workflows/supply-chain.yml
name: Supply Chain Security
on: [push, pull_request]

jobs:
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: SBOM Generate
        run: |
          npm install -g @cyclonedx/cdxgen
          cdxgen -o sbom.json
      
      - name: OSV Scan
        run: |
          go install github.com/google/osv-scanner/cmd/osv-scanner@latest
          osv-scanner scan --sbom sbom.json --format sarif > osv-results.sarif
      
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: CRITICAL,HIGH
          exit-code: 1
      
      - name: Secret Scan
        run: |
          docker run --rm -v $PWD:/src ghcr.io/gitleaks/gitleaks:latest \
            detect --source /src --verbose
      
      - name: Dependency-Track Upload
        run: |
          curl -X POST https://dtrack.example.com/api/v1/bom \
            -H "X-Api-Key: ${{ secrets.DTRACK_API_KEY }}" \
            -F "autoCreate=true" -F "project=myapp" -F "bom=@sbom.json"
```

Source: SLSA Framework, OWASP CI/CD Top 10, GitHub Security Lab

