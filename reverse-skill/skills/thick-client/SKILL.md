---
name: thick-client
description: Use for authorized security testing of desktop thick clients including local storage, update channels, IPC, traffic, and client-side trust boundaries.
---

# Thick Client Security Testing

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md`
2. `NOW`: Confirm the target is a **desktop thick client** (Win/macOS/Linux GUI or companion service), not pure Web
3. `NOW`: case-init; write installer source and test accounts into scope
4. `NEXT`: Tools (Burp upstream proxy, process monitoring, reverse engineering tools)
5. `ACT`: Trust boundary map → local surface → network surface → update/supply chain

## When to Use

- C/S architecture clients, Electron/Qt/.NET WinForms/WPF
- Local config/credential storage, IPC, named pipes
- Client-side enforced validation bypass research (authorized)
- Auto-update channels and code signing verification

## Workflow

### 1. Map the Boundaries

```text
□ Process tree, child processes, drivers/services
□ Listening ports and outbound domains
□ Local sensitive paths: %APPDATA%, Keychain, registry
```

### 2. Local Attack Surface

```text
□ Plaintext config, hardcoded keys, debug switches
□ DLL hijacking/search order (Windows)
□ Database files (SQLite) permissions and encryption
□ IPC: who can connect? Is it authenticated?
```

### 3. Network Surface

```text
□ System proxy / app custom TLS
□ Certificate pinning → combine with mobile/js methodology or Frida
□ API privilege escalation: admin interfaces hidden in the client
```

### 4. Reverse Engineering Verification

```text
□ .NET → dotnet-reverse; native → ida/ghidra; Electron → asar + js-reverse
```

## Toolchain

| Tool | Purpose |
|------|------|
| Process Monitor / API Monitor | Behavior |
| Burp / mitmproxy | Traffic |
| dnSpy / IDA / Ghidra | Reverse engineering |
| Sysinternals | Windows surface |
| asar / nexe detection | Electron |

### Tool installation

- Burp: Community Edition from https://portswigger.net/burp/communitydownload.
- mitmproxy: `pip install mitmproxy`.
- Process Monitor / API Monitor / Sysinternals suite: Microsoft Sysinternals (https://learn.microsoft.com/sysinternals) — Windows binaries, not pip.
- dnSpy / IDA / Ghidra: see `../dotnet-reverse/`, `../ida-reverse/`, `../ghidra-reverse/`.

## References

- `references/thick-client-checklist.md`
- `../dotnet-reverse/` `../ida-reverse/` `../js-reverse/` `../api-security/`

## Routing Context

**Upstream**: MASTER R32  
**Downstream**: pure protocol `protocol-reverse`; supply chain updates `supply-chain-security`

## Task Completion Self-Check

- [ ] Was the trust boundary drawn?
- [ ] Were both local and network surfaces covered?
- [ ] Checklist?
