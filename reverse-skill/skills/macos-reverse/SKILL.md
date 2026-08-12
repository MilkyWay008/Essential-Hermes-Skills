---
name: macos-reverse
description: Use for authorized macOS and Mach-O reverse engineering including codesign, Objective-C/Swift recovery, endpoint security surfaces, and Apple platform malware analysis.
compatibility: macOS host required — otool, codesign, spctl, class-dump, lldb, jtool2 are macOS-only and do not run on Windows/Linux
---

# macOS / Mach-O Reverse Engineering

> **Host requirement**: REQUIRES a macOS host (or macOS VM) — otool/codesign/spctl/class-dump do not run on Windows/Linux. If the agent runs on Windows: stop and ask the user to either run this on a Mac or provide a macOS VM/remote; do not attempt to install these on Windows.

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md`
2. `NOW`: Confirm the target is macOS / Mach-O / App bundle (iOS IPA → `mobile-reverse/`)
3. `NEXT`: tool-index; jtool2/lldb, etc.
4. `ACT`: Signature and load information → static → dynamic (lldb/Frida)

## Applicable Scenarios

- Mach-O executables / dylibs / frameworks
- .app bundles, LaunchAgents/Daemons
- Objective-C / Swift symbols and runtime
- Notarization / signing, Hardened Runtime, and TCC-related behavior analysis
- macOS malware static/dynamic analysis (jointly with malware-analysis)

## Workflow

### 1. Bundle and Signature

```bash
file target
codesign -dv --verbose=4 target
spctl -a -vv target 2>&1
otool -L target
```

### 2. Static

```text
□ class-dump / swift-demangle / Hopper / Ghidra / IDA
□ Strings and XPC service names, TCC-sensitive APIs
□ LC_LOAD_dylib dependencies and rpath
```

### 3. Dynamic

```text
□ lldb / Frida
□ Observe with fs_usage / log stream
□ Network: combine protocol-reverse or a proxy
```

## Toolchain

| Tool | Purpose |
|------|------|
| otool / nm / codesign | Built-in |
| Hopper / Ghidra / IDA | Decompilation |
| class-dump / dsdump | ObjC |
| Frida / lldb | Dynamic |
| jtool2 | Mach-O |

## References

- `references/macho-triage.md`
- `../mobile-reverse/` (iOS) `../ghidra-reverse/` `../malware-analysis/`

## Routing Context

**Upstream**: MASTER R31  
**Downstream**: iOS → mobile-reverse; generic samples → malware-analysis

## Task Completion Self-Check

- [ ] Was the signature / Hardened Runtime status recorded?
- [ ] Were address-level / symbol-level conclusions reached?
- [ ] Checklist?
