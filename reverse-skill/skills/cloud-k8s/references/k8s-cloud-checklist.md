# Cloud / K8s Checklist (condensed)

## IMDS
- [ ] Can SSRF reach 169.254.169.254
- [ ] Is IMDSv2 enforced
- [ ] Privilege surface of the returned IAM role

## K8s high-risk
- [ ] Too many cluster-admin bindings
- [ ] Secrets in plaintext env vars
- [ ] privileged + hostPID/hostPath combinations
- [ ] Anonymous auth / insecure apiserver port

## Containers
- [ ] Running as root
- [ ] Kernel module loading / docker.sock mounted

