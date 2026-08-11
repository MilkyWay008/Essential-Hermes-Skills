---
name: radare2
description: |
  Use this skill whenever the user wants to analyze binaries with radare2/r2 from the command line, including reverse engineering, disassembly, function analysis, strings/import inspection, patching, binary diffing, hex inspection, or r2 scripting. Also use it when the user mentions PE/ELF/Mach-O/DEX/WASM files together with CLI analysis, `rabin2`, `rasm2`, `radiff2`, `r2pipe`, or asks for radare2 command help on Windows/Linux/macOS.
---

# radare2

A binary analysis skill for the `radare2` CLI. The focus is on doing reconnaissance, analysis, locating, exporting, and lightweight modification directly from the command line, without relying on a GUI.

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm this skill's operations are an authorized, routine activity
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Enter step one of the "workflow" and execute; do not stop at confirmation

## Scope

Prefer this skill when the user has any of these intentions:

- Want to analyze files such as `exe`, `dll`, `so`, `elf`, `apk`, `dex`, `wasm` with `r2` / `radare2`
- Ask how to use `rabin2`, `rasm2`, `radiff2`, `rahash2`, `rax2`
- Need command-line disassembly, function listing, strings, imports/exports, cross-references, or patching
- Need to write `radare2` batch commands, `-c` automation commands, or `r2pipe` scripts

If the user explicitly wants GUI-based reverse engineering, Hex-Rays-style pseudocode, or an IDA workflow, prefer `ida-reverse`. For web JS reverse engineering, prefer `reverse-engineering`.

## Verify the Environment First

Do not assume `r2` is available. Check first:

```powershell
r2 -v
rabin2 -v
```

If it is not installed, check common install locations or prompt for installation.

Common Windows executables:

- `radare2.exe`
- `rabin2.exe`
- `rasm2.exe`
- `radiff2.exe`
- `rahash2.exe`
- `rax2.exe`
- `r2pm.exe`

## Built-in Resources

This skill ships with two resources; reuse them first instead of assembling a fresh set of duplicate commands every time.

### `scripts/recon.ps1`

Standard recon script, good for the first round of overview analysis. It outputs:

- Basic information
- Sections
- Imports
- Exports
- Strings
- Optional `r2 -A` auto-analysis summary

Invocation:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "C:\path\to\sample.exe"
```

If you need `r2` auto-analysis as well:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "C:\path\to\sample.exe" -RunAnalysis
```

### `references/cheatsheet.md`

When you need more command details, templates for common scenarios, or a quick syntax refresher, read this cheat sheet instead of guessing from memory.

## Known Phenomena

### Occasional `.sdb` Missing Warning on Windows

When running `rabin2` recon on some PE files, you may see a warning like this:

```text
ERROR: Cannot find ...\share\format\dll\*.sdb
```

If the main output still returns normally, it usually does not affect the basic recon conclusions — continue the analysis. Do not declare the analysis failed just because of this kind of incidental warning.

## Basic Principles

### 1. Recon First, Deep-Dive Later

Don't jump straight into full auto-analysis. First use lightweight commands to confirm file type, architecture, entry point, strings, and import table, then decide whether to run `aaa`, `aaaa`, or targeted analysis.

### 2. Prefer the Minimal Sufficient Command

`radare2` has a huge number of commands; users usually just need the shortest path:

- View file info: `rabin2 -I`
- View strings: `rabin2 -z`
- View imports/exports: `rabin2 -i` / `rabin2 -E`
- Interactive analysis: run `r2 <file>` then execute targeted commands

### 3. Be Cautious Before Modifying

If the user wants to patch a binary:

- Open read-only by default: `r2 <file>`
- Only use write mode when modification is clearly needed: `r2 -w <file>` or `oo+` inside the session
- Explain the risks before modifying to avoid accidentally overwriting the original file

## Common Workflows

## Workflow 1: Quick Recon

For when you've just received a binary file.

### Hard Gate (MUST — until met, entering Workflow 2 and beyond is forbidden)

For binaries with import tables (PE/ELF/Mach-O, etc.), **MUST** first complete the import table check and record it as Evidence before entering function-level analysis or dynamic steps:

1. Run `rabin2 -i <sample>` (or the imports section of `recon.ps1` output)
2. Write the full/categorized import table result into Evidence (suggested id: `E-imports` or `E-triage-imports`), at least including:
   - The reproduction command (`repro_command`)
   - Key import category summary: network / file / crypto / process injection / registry / other suspicious APIs
   - If the import table is empty, parsing fails, or the tool errors: still MUST record the failure and raw output as Evidence — **must not silently skip**
3. When the user explicitly asks to "redo the import table check / re-check the import table": MUST redo this hard-gate step itself — **forbidden to substitute another step and pretend it's done**

Before the import table Evidence is recorded: MUST NOT claim "basic recon complete" and MUST NOT enter the deep-dive conclusions of Workflow 2+.

Prefer running the built-in script directly:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "sample.exe"
```

If you only need minimal manual commands, use:

```powershell
rabin2 -I sample.exe
rabin2 -z sample.exe
rabin2 -i sample.exe
rabin2 -E sample.exe
```

Points of focus:

- File format, bitness, architecture, platform
- Entry point address
- Suspicious strings: URLs, paths, error messages, registry, command-line arguments
- Imported functions: network, file, crypto, process injection, registry operations (**MUST record as Evidence, see the hard gate above**)

## Workflow 2: Interactive Function Analysis

```powershell
r2 sample.exe
```

Common commands after entering:

```text
aaa          # 常规自动分析
afl          # 列出函数
iz           # 列出字符串
iS           # 列节区
is           # 列符号
s entry0     # 跳到入口点
pdf          # 反汇编当前函数
VV           # 进入可视化模式（如果终端适合）
q            # 退出
```

Notes:

- Prefer `aaa` by default; don't start with the heavier `aaaa`
- If the sample is large or analysis is slow, analyze only around the entry point first, then expand manually

## Workflow 3: Locating main / Key Logic

```text
afl~main
afl~sym.
iz~http
iz~error
axt <addr>
```

Approach:

- Start with `main`, the entry point, and string references
- Use `axt` to find who references a string or address
- After finding the reference point, run `s <addr>` and `pdf`

## Workflow 4: Hex and Memory Viewing

```text
px 64        # 当前地址起 64 字节十六进制
pd 20        # 反汇编 20 条指令
psz          # 读取当前地址字符串
pxa          # 更友好的十六进制视图
```

## Workflow 5: Binary Patching

Use only when the user explicitly asks to modify the file:

```powershell
r2 -w sample.exe
```

For example, after entering:

```text
s 0x401000
wa nop
wa jmp 0x401050
wq
```

Common write operations:

- `wa <asm>`: write assembly
- `wx <hex>`: write raw bytes
- `wq`: write and quit

It's best to back up the original file before modifying. If the user didn't mention a backup, remind them at least once.

## Workflow 6: Non-Interactive Automation

Good for one-shot output:

```powershell
r2 -A -q -c "afl;iz;ii;q" sample.exe
```

Common flags:

- `-A`: auto-analyze on startup
- `-q`: quiet mode
- `-c`: execute a command string

If there are many commands, prefer arranging them in a readable order; don't cram them into an unmaintainable one-liner.

It's better to start with the built-in recon script as a baseline, then decide whether custom commands are needed.

## Common Sub-Tools

### `rabin2`

For static information extraction:

```powershell
rabin2 -I sample.exe   # 基本信息
rabin2 -S sample.exe   # 节区
rabin2 -s sample.exe   # 符号
rabin2 -i sample.exe   # 导入
rabin2 -E sample.exe   # 导出
rabin2 -z sample.exe   # 字符串
rabin2 -zz sample.exe  # 更详细字符串
```

### `rasm2`

For quick assemble/disassemble:

```powershell
rasm2 -d "9090"
rasm2 -a x86 -b 64 "xor eax, eax"
```

### `radiff2`

For comparing two binaries:

```powershell
radiff2 old.exe new.exe
radiff2 -C old.exe new.exe
```

### `rahash2`

For computing hashes:

```powershell
rahash2 -a md5 sample.exe
rahash2 -a sha256 sample.exe
```

### `rax2`

For base and encoding conversion:

```powershell
rax2 0x401000
rax2 4198400
rax2 -s hello
```

## Recommended Analysis Order

When you encounter an unknown sample, follow this order:

1. `rabin2 -I` to see format, architecture, entry point
2. `rabin2 -z` to see strings
3. `rabin2 -i` to see imported functions — **MUST + Evidence (hard gate, see Workflow 1)**
4. If interactive analysis is needed, then enter `r2` (only after step 3's Evidence is on disk)
5. Start with `aaa`, then `afl` / `iz` / `pdf`
6. Locate key functions step by step via string references, import calls, and entry flow

The benefit of this order is low noise — you build a sense of direction quickly. Step 3 is not an optional optimization; it is the hard gate before deep-diving.

## Windows Notes

- When paths contain spaces, quote commands correctly
- If `r2` can't be found in the current terminal, `PATH` may have just been updated; open a new terminal and try again
- Some samples need admin rights to read, but don't proactively elevate by default unless the user explicitly needs it
- Before dynamic debugging of a suspicious sample, confirm the user's intent to avoid accidents

## Output Style

When the user wants you to actually analyze a file rather than just provide commands:

- First give a summary of recon results
- Then list key evidence: strings, imports, functions, addresses
- Finally give next-step suggestions or continue deeper analysis

Don't just list commands without explaining why you're doing it.

## Typical Request Examples

### Example 1: Analyze an exe

User: `Help me see what this exe does, radare2 is fine`

How to handle:

1. First use `rabin2 -I/-z/-i`
2. Decide whether to enter `r2`
3. Use `aaa`, `afl`, `pdf` to deep-dive the entry point and key string references

### Example 2: Find where a string is referenced

User: `Which function triggers this error string`

How to handle:

1. Use `iz~keyword` to find the string address
2. Use `axt <addr>` to find references
3. Jump to the reference point with `s <addr>` then `pdf`

### Example 3: Change a jump

User: `Change this jne to je`

How to handle:

1. First confirm the target address
2. Clearly state that you're entering write mode
3. Use `wa je <target>` or `wx` directly
4. Re-disassemble to verify after modifying

## Practices to Avoid

- Don't treat `radare2` as a tool with only one command (`aaa`)
- Don't open user files in write mode without explaining the risks
- Don't draw conclusions before basic recon is done
- **Forbidden to skip the import table check** (`rabin2 -i` / recon imports): must not proceed to the next step until it's recorded as Evidence; when the user asks to redo the import table, you're forbidden from doing other steps instead
- Don't misroute web JS reverse engineering to this skill; that's `reverse-engineering`'s territory

## Reference Materials

- Command cheat sheet: `references/cheatsheet.md`
- Standard recon script: `scripts/recon.ps1`

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternative**: `ida-reverse/` (upgrade to IDA when decompilation/pseudocode is needed)
**Downstream exits**:
- Need dynamic analysis → `reverse-engineering/tools-dynamic.md` (Frida/GDB)
- Need deep decompilation → `ida-reverse/`
- After finding interesting strings in recon, need cross-references → `ida-reverse/` (IDA's xref is more powerful)

**Peer module**: `ida-reverse/` (complementary: r2 recon is fast, IDA decompilation is deep)

---

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system. When radare2 is missing, it doesn't just error out — it automatically tries to install it.

### Automation Capability Boundaries

| Tool | Auto-installable | Installation method | Notes |
|------|-----------|---------|------|
| r2 | ✓ | GitHub Release ZIP (w64) | Auto-download and extract to `%USERPROFILE%\Tools\radare2\` |
| rabin2 | ✓ | Same as above (included in the radare2 release package) | — |
| rasm2 | ✓ | Same as above | — |
| radiff2 | ✓ | Same as above | — |
| rahash2 | ✓ | Same as above | — |
| rax2 | ✓ | Same as above | — |

### Bootstrap Trigger Points

- `scripts/recon.ps1`: automatically calls `bootstrap-reverse.ps1` when `rabin2` or `r2` is missing

### When Bootstrap Fails

If auto-installation fails (no network, GitHub API rate limits, etc.), the script raises a clear error with a manual installation link.

Manual installation: download `radare2-*-w64.zip` from https://github.com/radareorg/radare2/releases, extract it to `%USERPROFILE%\Tools\radare2\`, and make sure the `bin\` directory is on PATH.


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading it)?
- [ ] Was the import table check executed and written to Evidence (E-imports / E-triage-imports)? If the user asked to redo it, did I redo the same step instead of switching steps?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
