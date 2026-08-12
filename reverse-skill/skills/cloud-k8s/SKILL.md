---
name: cloud-k8s
description: Use for authorized cloud, container, and Kubernetes security assessment including metadata SSRF, IAM misconfig, container escape paths, and cluster RBAC review.
---

# Cloud / Container / Kubernetes Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` — **cloud/K8s testing MUST have written authorization**
2. `NOW`: case-init + scope; clarify account boundaries, forbid destructive operations
3. `NOW`: confirm this is cloud metadata/container/K8s/IAM, not ordinary web scanning (use `pentest-tools/` for the latter)
4. `NEXT`: tool-index; kubectl/aws/gcloud etc. are mostly manual installs (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
5. `ACT`: start with "identity and exposure surface"; no default full-network scanning

## Applicable Scenarios

- Cloud metadata SSRF (169.254.169.254 / IMDS)
- IAM over-privilege, public storage buckets, misconfigured security groups
- Docker/containerd escape path assessment
- Kubernetes RBAC, Secrets, Admission, supply-chain images
- Container image vulnerabilities (can coordinate with `supply-chain-security/`)

## Workflow

### Phase 1 — Identity and Boundary

```text
□ Current identity: cloud AK/SK, K8s SA, node SSH?
□ Scope: single account / single cluster / single namespace
□ Network profile: authorized_target_only
```

### Phase 2 — Cloud Control Plane

```bash
# Example (replace per vendor; MUST stay within authorized accounts)
aws sts get-caller-identity
aws s3 ls
# Corresponding Azure / GCP identity commands
```

```text
□ Public buckets / wrong ACLs
□ Metadata: IMDSv1 vs v2; SSRF chains
□ Assumable roles (PassRole) and lateral movement
```

### Phase 3 — Containers

```text
□ privileged / hostPath / hostNetwork?
□ capabilities (SYS_ADMIN, etc.)
□ Writable host paths → escape candidates
□ Image history and known CVEs → Trivy
```

### Phase 4 — Kubernetes

```bash
kubectl auth can-i --list
kubectl get pods,secrets,svc -A
kubectl get clusterrolebindings
```

```text
□ SA token mounts and permissions
□ Missing dangerous admission webhooks
□ etcd / dashboard exposure
□ Network policies default-allow?
```

## Toolchain

| Tool | Purpose | Bootstrap |
|------|------|------|
| kubectl | cluster interaction | manual |
| trivy | images/IaC | bootstrap `trivy` if available |
| kube-bench / kubeaudit | CIS/config | manual |
| pacu / scoutsuite | cloud auditing (authorized) | manual |
| nuclei | known cloud vulnerability templates | bootstrap nmap/nuclei ecosystem |

## References

- `references/k8s-cloud-checklist.md`
- CTF counterpart: `../CTF-Sandbox-Orchestrator/competition-agent-cloud/`
- `../supply-chain-security/` `../pentest-tools/`

## Routing Context

**Upstream**: MASTER R23  
**Downstream**: node shell → `attack-chain` / `windows-ad`; image vulnerabilities → supply-chain  
**MUST NOT**: scan other tenants of public clouds without authorization

## Task Completion Self-Check

- [ ] Is it limited to authorized accounts/clusters?
- [ ] Do findings include reproduction steps and impact?
- [ ] Were destructive operations avoided?
- [ ] Report / journal?