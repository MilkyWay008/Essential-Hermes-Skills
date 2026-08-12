# EDR Hook Survey Cheatsheet

> Authorized red team / adversary simulation / own-product testing only. Using against unauthorized targets is forbidden.

This document summarizes the user-mode and kernel-mode monitoring points of mainstream EDR/AV products, for quick "what needs to be handled" orientation during red team recon.

## 1. Mainstream EDR Fingerprints and Hook Patterns

| Vendor / product | User-mode component | Kernel driver | Main monitoring surface |
|------------|-----------|---------|-----------|
| CrowdStrike Falcon | `CSFalconService.exe`, `CSAgent.sys` injected into target processes | `CSAgent.sys`, `CSBoot.sys` | Heavy kernel callbacks + ETW-TI; fewer user-mode hooks (cloud-based) |
| Microsoft Defender for Endpoint (MDE) | `MsMpEng.exe`, `MpClient.dll` | `WdFilter.sys`, `WdBoot.sys`, `WdNisDrv.sys` | AMSI + ETW-TI + ntdll inline hooks + kernel callbacks, comprehensive |
| SentinelOne | `SentinelAgent.exe`, `SentinelHelperService.exe` | `SentinelMonitor.sys`, `SentinelDeviceControl.sys` | Heavy ntdll user-mode hooks + kernel callbacks + own ETW provider |
| Elastic Defend (formerly Endpoint Security) | `elastic-endpoint.exe` | `elastic-endpoint-driver.sys` | Mostly ETW + a few ntdll hooks, uploaded via Elastic Agent |
| ESET | `ekrn.exe`, `eamsi.dll` | `eamonm.sys`, `epfwwfp.sys` | Very many user-mode hooks (NtCreateFile / NtOpenProcess etc.) |
| Sophos Intercept X | `SophosFileScanner.exe`, `SophosNtpService.exe` | `SophosED.sys`, `hmpalert.sys` | ntdll hooks + HMPA memory protection + kernel callbacks |
| Kaspersky | `avp.exe`, `klif.sys` | `klif.sys`, `klhk.sys` | Heavy user-mode hooks + KLIF own minifilter + network filter driver |
| Trend Micro Apex One | `TmListen.exe`, `TmCCSF.dll` | `tmcomm.sys`, `tmactmon.sys` | User-mode hooks + behavior monitoring driver |
| Carbon Black | `RepMgr.exe`, `RepWAV.exe` | `ParityDriver.sys` | Kernel callbacks + ETW oriented |

### Quick Fingerprint Script

```powershell
$edrSigs = @{
    'CSAgent'           = 'CrowdStrike Falcon'
    'SentinelAgent'     = 'SentinelOne'
    'elastic-endpoint'  = 'Elastic Defend'
    'ekrn'              = 'ESET'
    'MsMpEng'           = 'Microsoft Defender'
    'SophosFileScanner' = 'Sophos Intercept X'
    'avp'               = 'Kaspersky'
    'TmListen'          = 'Trend Micro Apex One'
    'cb'                = 'Carbon Black'
}

Get-Process | ForEach-Object {
    foreach ($k in $edrSigs.Keys) {
        if ($_.ProcessName -match $k) {
            "[+] $($edrSigs[$k]) detected: $($_.ProcessName) (PID $($_.Id))"
        }
    }
}

Get-ChildItem 'C:\Windows\System32\drivers\*.sys' |
    Where-Object { $_.Name -match 'CSAgent|Sentinel|elastic|eam|WdFilter|Sophos|klif|tmcomm|Parity' } |
    Select-Object Name, VersionInfo
```

## 2. Key User-Mode ntdll Hook Functions

`ntdll.dll` exports that EDR almost certainly hooks (grouped by ATT&CK behavior):

| Function | Behavior monitored | ATT&CK |
|------|-----------|--------|
| `NtCreateThreadEx` | remote thread injection, QueueUserAPC injection | T1055.002 / T1055.004 |
| `NtAllocateVirtualMemory` | shellcode allocating RWX memory | T1055 |
| `NtAllocateVirtualMemoryEx` | cross-process memory allocation (Win10+ new API) | T1055 |
| `NtProtectVirtualMemory` | changing page permissions RW→RX | T1055 |
| `NtWriteVirtualMemory` | writing shellcode cross-process | T1055.012 |
| `NtMapViewOfSection` | section-based injection (Process Doppelganging / Ghosting) | T1055.013 |
| `NtCreateSection` | paired with MapViewOfSection | T1055.013 |
| `NtOpenProcess` | opening the target process for a handle | T1057 |
| `NtQueueApcThread` / `NtQueueApcThreadEx` | APC injection | T1055.004 |
| `NtCreateProcess` / `NtCreateProcessEx` / `NtCreateUserProcess` | creating child processes (incl. PPID spoofing) | T1106 |
| `NtSetContextThread` | changing thread context (thread hijacking injection) | T1055.003 |
| `NtResumeThread` | resuming threads after injection | T1055 |
| `NtQuerySystemInformation` | enumerating processes / drivers / handles | T1057 / T1082 |
| `NtAdjustPrivilegesToken` | privilege escalation for SeDebugPrivilege etc. | T1134 |
| `NtLoadDriver` | loading kernel drivers (BYOVD) | T1543.003 |

### Verifying Whether a Hook Exists

```powershell
# simple: disassemble-diff the on-disk ntdll against the current process's ntdll
# 1. grab the on-disk ntdll
copy C:\Windows\System32\ntdll.dll C:\temp\ntdll_clean.dll

# 2. attach any process in windbg, export the live ntdll .text section
# .writemem c:\temp\ntdll_live.bin ntdll!.text L?<size>

# 3. disassemble NtAllocateVirtualMemory in IDA / radare2; the normal form is:
#    mov r10, rcx
#    mov eax, <SSN>
#    test byte ptr [...]
#    jne ...
#    syscall
#    ret
# if the first instruction becomes jmp <some address>, that's a hook
```

## 3. Kernel Callback Monitoring Points

Common kernel callbacks registered by EDR (all could be unregistered via the BYOVD route in `attack-chain`, but at high cost):

| API | Callback timing | Defender purpose |
|-----|--------------|-----------|
| `PsSetCreateProcessNotifyRoutineEx` | process create / exit | intercept suspicious child processes |
| `PsSetCreateThreadNotifyRoutine` | thread create / exit | detect remote thread injection |
| `PsSetLoadImageNotifyRoutine` | DLL / EXE loaded into any process | module integrity / unsigned interception |
| `CmRegisterCallback` / `CmRegisterCallbackEx` | registry operations | persistence detection |
| `ObRegisterCallbacks` | `OpenProcess` / `OpenThread` handle requests | prevent LSASS handle acquisition (T1003.001) |
| `MmRegisterPhysicalMemoryCallback` | physical memory mapping | anti-DMA / memory forensics |
| `IoRegisterFsRegistrationChange` | filesystem registration | minifilter coordination |
| `KeRegisterNmiCallback` | NMI (rarely used by EDR) | anomaly monitoring |
| `EtwRegister` (kernel side) | kernel ETW reporting | symbiotic with ETW-TI |

### Enumerating Registered Callbacks With windbg

```text
0: kd> dx -r1 nt!PspCreateProcessNotifyRoutine
0: kd> dx -r1 nt!PspCreateThreadNotifyRoutine
0: kd> dx -r1 nt!PspLoadImageNotifyRoutine

0: kd> !object \Callback
0: kd> !object \Callback\ProcessObject
```

Or use tools like PChunter / DRVHV for a visual callback list as a normal user.

## 4. Statically Dumping Hook Tables (IDA + windbg workflow)

### Workflow A: Single-Process Comparison

```text
1. Find a process that EDR has already injected its user-mode component into (any surviving process)
2. windbg attach (-pn target.exe)
3. lm m ntdll  → get the module base
4. .writemem c:\temp\ntdll_live.bin ntdll+0x0 L?<image size>
5. copy C:\Windows\System32\ntdll.dll to c:\temp\ntdll_disk.dll
6. Load both files in IDA, jump to NtAllocateVirtualMemory:
     - disk: standard prologue
     - live: first instruction jmp <0x7FFE000000xx>
7. Follow the jmp target → that's the EDR trampoline; dump it
8. Enter the trampoline to see which DLL it finally lands in; confirm the EDR module name
```

### Workflow B: Batch Hook Table Generation

Use `HookHunter` or a custom script:

```powershell
# pseudo workflow; see the scripts referenced in the references
$disk = Get-Content C:\Windows\System32\ntdll.dll -Encoding Byte
$live = # obtained via OpenProcess + ReadProcessMemory
# compare the first 16 bytes of every export in the .text section
```

## 5. pe-sieve Automatic Detection

`pe-sieve` is the first choice for recon of EDR hooks and implant self-checks:

```powershell
# basic scan
pe-sieve64.exe /pid 1234

# recommended combo (shellcode + hook detection)
pe-sieve64.exe /pid 1234 /shellc 3 /modules 3 /imp 3 /data 3 /dir hooks_dump

# key parameters:
#   /shellc N    shellcode scan level (0-3)
#   /modules N   module integrity check (0-3)
#   /imp N       IAT hook check
#   /data N      data section scan
#   /dir <path>  dump output directory
```

Output produces `*.tag` files under `hooks_dump/<pid>.<name>/` listing hook addresses:

```text
modified_modules.tag example:
71f10000;ntdll.dll
71f1a3b0;hook;jmp_far
71f1c020;hook;jmp_near
```

Feed directly into IDA and jump to the corresponding RVA for follow-up analysis.

### Embedding pe-sieve in an Implant (self-check)

In practice, compile `pe-sieve` as a lib (`libpe-sieve`) so the implant self-checks at startup: if ntdll has hooks, trigger the unhook flow; if it finds itself hooked, be careful — it might be in a sandbox.

## 6. API Monitor v2 Dynamic Observation

API Monitor v2 (Rohitab) is good for watching in the lab where and when EDR inserts hooks:

```text
1. start API Monitor v2 (admin)
2. in API Filter tick:
     - NT Native API → Memory Management
     - NT Native API → Process and Thread
     - Windows Defender / AMSI (if visible)
3. Monitor New Process → select the implant test sample
4. observe:
     - NtAllocateVirtualMemory call order
     - whether it is relayed through an EDR DLL
5. in the Modules tab, see which EDR DLLs were LoadLibrary-injected
```

## 7. Common EDR DLLs (user mode) Cheatsheet

| DLL | Vendor | Notes |
|-----|------|------|
| `umppc*.dll` | Microsoft Defender | MpClient userland |
| `mpoav.dll` | Microsoft Defender | AMSI provider |
| `aswAMSI.dll` | Avast | AMSI provider |
| `eamsi.dll` | ESET | AMSI provider |
| `IDPMServiceClient.dll` | Sophos | HMPA injection |
| `klsihk64.dll` | Kaspersky | injected into target processes |
| `CrowdStrike.Sensor.dll` | CrowdStrike | old versions; newer relies mainly on kernel |
| `SentinelInjection64.dll` | SentinelOne | user-mode injection |
| `TmUmEvt64.dll` | Trend Micro | behavior monitoring |

After confirming the target EDR, decide which DLL to reverse for the hook table.

## Reference Links

- pe-sieve: <https://github.com/hasherezade/pe-sieve>
- HollowsHunter: <https://github.com/hasherezade/hollows_hunter>
- API Monitor v2: <http://www.rohitab.com/apimonitor>
- MITRE ATT&CK T1562: <https://attack.mitre.org/techniques/T1562/>
- MITRE ATT&CK T1055: <https://attack.mitre.org/techniques/T1055/>
- ired.team EDR notes: <https://www.ired.team/offensive-security/defense-evasion>

## Routing Callback

After the hook survey, return to Step 3 of `../SKILL.md` to select the bypass technique combination, then execute per `unhook-techniques.md` and `telemetry-blinding.md`.

