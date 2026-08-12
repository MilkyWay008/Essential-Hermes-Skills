# reverse-skill Package Security Audit (executable surface)

> Date: 2026-08-02
> Scope: executable scripts and bootstrap manifests under `skills/**/scripts`, `skills/scripts`, `kali/scripts`, `burp-mcp-full`  
> **Excludes**: **educational payload docs** such as `src-hunter` / payloader (their DROP/injection samples are methodology, not auto-executed)

## Conclusion (Overall)

| Level | Verdict |
|------|------|
| **Backdoor / deliberate DB wipe / disk formatting** | **Not found** |
| **Piped download-and-execute (curl\|sh / IEX DownloadString)** | **Not found** |
| **Hardcoded cloud keys / private keys** | **Not found** (the `sk-` / `BEGIN RSA` in docs are detection examples) |
| **Residual supply-chain risk** | **Partially hardened (med-low→low)**: pinned `@latest`; GitHub downloads support **manifest SHA256 + API digest** |

**Overall: no implanted backdoors or "one-click DB wipe" logic found on the executable skill-script surface; dangerous deletions are confined to tool-reinstall temp directories / case output directories.**

### 2026-07-18 Hardening (this commit)

| Item | Action |
|----|------|
| jshookmcp | `@latest` → `@0.3.4` |
| pentestswarm | `@latest` / docker `:latest` → `@v0.1.0` / `:v0.1.0` |
| jadx | pin `v1.5.6` + `assetSha256` |
| apktool | pin `v3.0.2` + `assetSha256` |
| bootstrap PS/sh | After download, run `Assert-DownloadedFileIntegrity` / `verify_sha256`; prefer the manifest hash, then GitHub `digest`; on failure delete the file and abort |
| Release without pinned hash | Still installable, but **WARN** and print the actual sha256 |

### 2026-08-02 Security Fixes

| Item | Fix |
|----|------|
| Kali quick setup | Resolve the sudo user's home with `getent`; removed `eval` |
| Frida process listing | Use a `frida-ps` argument array; removed inline Python code splicing |
| Burp MCP token | Atomic replace via a restricted temp file; POSIX file permissions pinned to `0600` |
| Burp MCP bridge | Parse MCP newline-delimited messages; reconnect on demand after Burp starts |
| Anything Analyzer MCP | bootstrap enables bearer auth by default and registers credentials via an optional host adapter |
| IDA MCP startup | Terminate old processes one by one to avoid multi-PID argument-expansion errors |

## Scan Methodology

Searched executable extensions (`.ps1` / `.sh` / `.py` / `.js` / `.java`) for:

- `Invoke-Expression` / `IEX` / `FromBase64String` / `DownloadString`
- `curl|bash` / `wget|sh` piped execution
- `DROP DATABASE|TABLE`, `rm -rf /`, `Remove-Item ... C:\Windows`
- Reverse-shell patterns (`/dev/tcp` abuse, `TcpClient` callback)
- Hidden-window launches (purpose re-verified)

Round two: manual review of `bootstrap-reverse.ps1/.sh` download and deletion paths, `mcp-bridge.js`, and the diagram/crypto Python scripts.

## Detailed Findings

### 1. Deletion Operations (all expected cleanup, not DB wipes)

| Location | Behavior | Risk |
|------|------|------|
| `bootstrap-reverse.ps1` `Expand-ArchiveIntoDirectory` | Deletes the target install dir then reinstalls; deletes `%TEMP%\reverse-bootstrap-*` | Tool install paths only, not user business data |
| `bootstrap-reverse.ps1` anything-analyzer | On failure `Remove-Item node_modules` then `pnpm install` | Confined to the cloned tool repo |
| `apk-reverse/scripts/decode.*` | Cleans task output dirs jadx/apktool out | Confined to the task root |
| `case-init.ps1` | Cleans temp directories | Temporary |
| `bootstrap-reverse.sh` | Same kind of temp / install-target cleanup | Same as left |

**No** executable `DROP`/`TRUNCATE` logic targeting `C:\`, system directories, or arbitrary database connection strings was found.

### 2. Network Behavior (tool bootstrapping, not C2)

| Location | Behavior | Notes |
|------|------|------|
| `bootstrap-reverse.ps1` | Fetches releases from `api.github.com`; downloads zip/jar via `Invoke-WebRequest` | Repo names come from a **manifest whitelist** |
| `bootstrap-reverse.sh` | `curl` / `git clone` / `pipx` / `npm` | Same as above |
| `mcp-bridge.js` | HTTP to `127.0.0.1:9876` only → Burp | Local loopback |
| `ToolDiscovery.ps1` | Probes `http://host:port/mcp` | Health check |
| `kali/.../tool-discovery.sh` | `(echo >/dev/tcp/$host/$port)` | **Port probe**, not a reverse shell |

### 3. Hidden Windows

| Location | Purpose |
|------|------|
| `bootstrap-reverse.ps1` `Start-Process ... -WindowStyle Hidden` | Starts `pnpm dev` in the background (anything-analyzer) |
| `ida-reverse/scripts/start.ps1` | Starts IDA-related processes (must stay in the background) |

Service-launch form; no hidden malicious-payload downloads found.

### 4. "Dangerous Terms" in Docs / Payloads (not auto-executed)

**Markdown/JSON teaching materials** such as `pentest-tools/src-hunter`, `attack-chain` contain SQL injection, `DROP` examples, and log-cleanup **red-team methodology**.  
These are **not auto-executed by bootstrap or master-route**; execution depends on AI/humans choosing to use them under an **authorized scope**.

See the related constraints: `ops/scope-contract.md`, `ops/skill-supply-chain.md`, `field-journal/precedent-*.md`.

### 5. Residual Supply-Chain Risk (hardening recommended, not a confirmed backdoor)

| Item | Risk | Recommendation |
|----|------|------|
| `@jshookmcp/jshook@0.3.4`, `pentestswarm@v0.1.0` in `bootstrap-manifest.json` | Tag drift / supply-chain poisoning surface | Pin version numbers + checksums |
| GitHub release zip **without SHA256 verification** | Hard to detect a swapped release promptly | Add `assetSha256` to the manifest and verify in bootstrap |
| `npm install -g` / `pip` default sources | Inherent dependency-ecosystem risk | Install only manifest capabilities; use private sources/locking in production |

## Executable Script Inventory (audit baseline)

```
skills/scripts/*.ps1|*.sh + lib/ToolDiscovery.ps1
skills/apk-reverse/scripts/*
skills/radare2/scripts/*
skills/ida-reverse/scripts/*
skills/browser-automation/scripts/*
skills/diagram-generator/scripts/*.py
skills/case-review/scripts/*.py
kali/scripts/*
burp-mcp-full/mcp-bridge.js (+ Java extension source)
```

## Recommended Ongoing Checks

```powershell
# Quick executable-surface health check (example)
rg -n "Invoke-Expression|FromBase64String|DownloadString|rm -rf /|DROP DATABASE" skills/scripts skills/*/scripts kali/scripts burp-mcp-full -g "*.ps1" -g "*.sh" -g "*.py" -g "*.js"
```

Re-run this checklist before merging any new skill's **executable scripts**; pure Markdown methodology changes are not required.

## Sign-off

- Audit performed: local static scan of the repo + manual review of critical paths  
- Result: no backdoors / no automatic DB wipes; supply-chain hardening listed as a follow-up item  
'@
