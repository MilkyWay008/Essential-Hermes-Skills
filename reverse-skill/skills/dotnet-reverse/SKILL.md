---
name: dotnet-reverse
description: >-
  Use for .NET / C# binary reverse engineering: .NET assemblies (PE with CLR header, .exe/.dll managed
  programs), C# builds (incl. NativeAOT), red-team Sharp* tools (Rubeus / SharpHound / SeatBelt etc.),
  obfuscated .NET (ConfuserEx / SmartAssembly / Babel / Eazfuscator), and .NET loaders / info-stealers /
  wrapped malware. Prefers dnSpyEx + de4dot; pairs with dnSpy MCP when direct AI-driven manipulation is
  needed. Not for pure native binaries (use reverse-engineering / ida-reverse instead).
license: MIT
compatibility: >-
  Requires a filesystem-based code agent or CLI with shell access, Windows host preferred (dnSpyEx is a Windows
  GUI); Linux/macOS can use ILSpy/de4dot CLI + mono/dotnet runtime.
---

# .NET / C# Reverse Engineering Guide

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Confirm the target is .NET managed using DIE/`file`/the CLR header (otherwise SWITCH to `ida-reverse/` / `reverse-engineering/`)
2. `NOW`: If obfuscation is suspected → unpack with `de4dot` first, produce `*-clean.exe`, and keep the original sample
3. `NEXT`: Static analysis with dnSpyEx (or dnSpy MCP / `ilspycmd`): browse C# and use the **IL view** for key logic
4. `ACT`: Use dynamic debugging when plaintext/C2 is needed; prefer **IL patch** over C# recompilation when changing logic
5. At the end of each phase, present the user with a 3–6 item next-step menu (including report export)

## Scope

Use this skill first when the task falls into any of the following scenarios:

- Identify and reverse-engineer .NET / C# compiled artifacts (managed PE / .exe / .dll)
- Analyze red-team Sharp* toolchains (Rubeus, SharpHound, SharpShell, etc.)
- Deobfuscate protectors such as ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor
- Reverse the decryption and C2 logic of .NET loaders / info-stealers / RATs
- Patch C# programs (change branches, change constants, keygen)
- Analyze the Mono/Unity managed layer before IL2CPP (note: IL2CPP output is native — use `../reverse-engineering/` + `../field-journal/seed-014_unity-il2cpp-reverse.md`)

If the target is a pure native binary (C/C++/Go/Rust compiled, no CLR), use `reverse-engineering/`, `ida-reverse/`, or `radare2/` instead.

## Core Principles

- **Identify first, then act**: confirm it's a .NET managed program (PE header CLR + `#~` / `#Strings` streams + mscoree `_CorExeMain`) before deciding to use dnSpy instead of IDA
- **Prefer IL over C#**: dnSpyEx's C# decompiler can lose or distort information (compiler-generated state machines, async/await, yield); key logic and patches must be done in the **IL editor** — use the C# view only for quick browsing
- **de4dot first**: when you hit an obfuscator, run `de4dot` once before static analysis, otherwise strings and control flow are a mess
- **MCP integration**: if the environment has a registered dnSpy MCP (`dnspy_*` tools), prefer the MCP surface for decompile / IL inspection to avoid GUI round-trips
- **Evidence-based output**: persist deobfuscated artifacts, extracted config/C2/key, and patch diffs to disk

## Toolchain Mapping

| Capability | First choice | Notes |
|------|------|------|
| Decompile + debug + patch | **dnSpyEx** | The ace: the only GUI with an IL editor; legacy dnSpy is discontinued, use the Ex fork |
| Lightweight CLI / headless decompile | **ILSpy** (`ilspycmd`) | Suited to batch, scripted, Linux/macOS use |
| Deobfuscation | **de4dot** | Default solution for the ConfuserEx family, SmartAssembly, and other mainstream protectors |
| Obfuscator detection | **Detect It Easy (DIE)** / **file** | Determine the protector type first, then choose de4dot arguments |
| Programmatic IL manipulation | **dnlib** | Write C# scripts for batch metadata changes / string decryptors |
| Direct AI manipulation | **dnSpy MCP** | Tool surfaces such as `dnspy_decompile` / `dnspy_inspect_il` |

> Prerequisite: install dnSpyEx + de4dot on a Windows host (choco or release); on Linux/macOS use `ilspycmd` + `dotnet runtime`. See the install matrix in `references/sharp-tools.md`.

## Six-Phase Workflow

### 1. Identify (.NET)

Confirm the target is a managed program; don't analyze a native PE as .NET:

```powershell
# Windows
file target.exe                       # "PE32 executable ... for MS Windows" is not enough
# Key: check whether a CLR header is present
powershell -c "[System.Reflection.AssemblyName]::GetAssemblyName('target.exe')"
# or
just drag it into dnSpyEx - if it opens, it is managed code

# Generic
strings target.exe | grep -iE "mscoree|_CorExeMain|mscorlib|System\\."
```

**.NET identification markers:**
- PE header `Data Directory[14]` (CLR Runtime Header) is non-zero
- `mscoree.dll` import / `_CorExeMain` entry point
- `#~`, `#Strings`, `#US`, `#GUID`, `#Blob` metadata streams
- `mscorlib` / `System.Private.CoreLib` strings

**NativeAOT exception:** compiled to native with no CLR header, but has `System.Private.CoreLib` strings and reorganized type metadata — such binaries go to `reverse-engineering/` (IDA/r2); this skill only flags them for identification.

### 2. Detect (obfuscator)

```powershell
# Quick identification with DIE
diec target.exe                        # Detect It Easy CLI
# or drag it into dnSpyEx and look for heavily garbled class names / control-flow mangling
```

Or drag it into dnSpyEx and check for garbled class names / control-flow mangling.

Common obfuscators → unpacking strategy (see `references/obfuscators.md`):

| Obfuscator | Signature | de4dot handling |
|--------|------|------------|
| ConfuserEx (1.0.0 / 2.x) | `<module>` anti-tamper, control-flow mangling, string encryption | `de4dot target.exe` usually auto-detects |
| SmartAssembly | `circular`/`string encoding`, resource compression | `de4dot target.exe` |
| Babel.NET | method-body encryption, control flow | `de4dot target.exe` |
| Eazfuscator.NET | string/resource encryption | `de4dot`, some versions need manual handling |
| .NET Reactor | anti-tamper + necrobit | `de4dot`; newer versions may fail and need manual handling |

### 3. Deobfuscate

```powershell
# de4dot auto-detects most protectors by default
de4dot target.exe -o target-clean.exe

# Force a specific type (when auto-detection fails)
de4dot --type cfze target.exe          # ConfuserEx
de4dot --type sa target.exe            # SmartAssembly

# Multi-layer obfuscation / de4dot reports unknown
de4dot --detect target.exe             # see what it detects it as
# You may need to patch anti-tamper first, then run de4dot (see references/obfuscators.md)
```

Output: `target-clean.exe` — use it for all subsequent analysis. **Keep the original sample** for comparison.

### 4. Static Analysis

Load the unpacked sample in dnSpyEx:

- **C# view**: quickly browse class structure, method signatures, and strings (for locating code)
- **IL view**: key branches, crypto logic, and state machines must be examined in IL (right-click → Edit IL, or the IL view)
- Find entry points: `Main` / `Startup` / module initializer (`Module .cctor`)
- Find key logic: search for `flag`, `password`, `verify`, `check`, `encrypt`, `http`, `Config`

```text
Locate the string → find its cross-references → find the method that uses it → inspect the decision logic in the IL view
```

### 5. Dynamic Debugging

dnSpyEx debugger: attach to a process / start debugging, set breakpoints on key methods, observe at runtime:
- Decrypted plaintext strings (many obfuscators only decrypt strings at runtime)
- C2 addresses, decrypted config results
- Exception-driven control flow (anti-debug commonly uses `try/catch` to hide the real path)

> .NET dynamic debugging is far friendlier than native — you can directly see object values and string contents. Prefer dynamic over grinding through static.

### 6. Patch (as needed)

```text
dnSpyEx → right-click the method → Edit Method (C#) or Edit IL
  - Flip a check: ldc.i4.0 → ldc.i4.1 (false→true)
  - Change a constant: edit the string/number directly
  - Remove a validation: nop out the whole block
File → Save Module → replace the original file
```

**IL patch reliability > C# patch**: C# recompilation can fail (missing references, wrong syntax), while IL editing almost never loses fidelity. See `references/common-workflow.md`.

## Trigger Scenario Routing

Enter this skill when the user says any of the following:
- ".NET / C# binary reverse engineering" / "C# program decompilation"
- "dnSpy analysis" / "dnSpyEx patch"
- "ConfuserEx / SmartAssembly / Babel deobfuscation / unpacking"
- "Sharp* tool analysis" (Rubeus / SharpHound / SharpShell)
- ".NET malware / loader / info-stealer reverse engineering"
- "C# program patch / keygen / branch modification"

## When to Switch Out

- IL2CPP-compiled Unity games → `reverse-engineering/` + `../field-journal/seed-014_unity-il2cpp-reverse.md` (IL2CPP is native; dnSpy does not apply)
- NativeAOT artifacts → `reverse-engineering/` (same as above, native)
- Pure native PE (no CLR) → `reverse-engineering/` / `ida-reverse/`
- Need to batch-migrate symbols/functions to another version → `binary-diff/`
- Need attack-path / call-chain diagrams → `diagram-generator/`

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exits**:
- IL2CPP / NativeAOT (native) → `reverse-engineering/`
- Deep native .so/.dll section analysis → `ida-reverse/` / `radare2/`
- Need AI to directly drive dnSpy → register and integrate dnSpy MCP (see `references/sharp-tools.md`)

**Peer modules**:
- `../reverse-engineering/languages-compiled.md` (.NET intro points to this module)
- `apk-reverse/` (Xamarin/MAUI Android reversing can return here for the C# layer)

## Reference Documents

- [references/obfuscators.md](references/obfuscators.md) — ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor deobfuscation details + anti-tamper bypass
- [references/common-workflow.md](references/common-workflow.md) — full workflow, IL patch reliability, string-decryptor extraction, state-machine recognition
- [references/sharp-tools.md](references/sharp-tools.md) — red-team Sharp* tool analysis, tool install matrix, dnSpy MCP integration, community resource index

## Task Completion Self-Check

- [ ] Did I confirm the CLR / managed identity (or already SWITCH out of this skill)?
- [ ] Was the obfuscated sample de4dot'd / equivalently unpacked before deep analysis?
- [ ] Was key logic verified in the IL view (rather than only the C# pseudo-code)?
- [ ] Were artifacts (clean sample / config / patch diff) persisted to disk and reproducible?
- [ ] Was a next-step menu or report exit provided?
