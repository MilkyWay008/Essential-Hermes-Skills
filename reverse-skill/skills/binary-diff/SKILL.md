---
name: binary-diff
description: >-
  Use for cross-version symbol migration and binary diffing: derive missing symbols for a new version from
  an old version results, migrate function names in bulk after an update, and locate new offsets quickly.
  Core method: LLM-driven structured diff comparison with programmatic I/O. Trigger keywords: symbol
  migration, bindiff, cross-version, missing PDB, function offset migration, binary diff, version
  comparison.
---

# Cross-Version Symbol Migration (Binary Diff)

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm the operations in this skill are authorized routine operations
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Move into the first step of the workflow and execute; do not stop at confirmation

## Scope

Use this skill when the task falls into the following scenarios:

1. **Kernel/driver missing PDB** — you have symbols for an old ntoskrnl.exe but the new version's PDB has been pulled by Microsoft; derive the new version's non-exported function addresses from the old symbols
2. **Symbol migration after a program update** — you reversed a program before, it got updated, and you don't want to redo the whole reversal; migrate in bulk from the old-version results
3. **Protection mechanism updates** — the old version has complete reversal results; quickly locate the new offsets of the same functions in the new version
4. **Any "old version with symbols + new version without symbols" binary comparison scenario**

### Division of Labor with Other Skills

| Scenario | What to use |
|------|--------|
| Reverse a binary from scratch | `ida-reverse/` or `radare2/` |
| Have old-version results, migrate to the new version | **This skill** |
| Compare two completely different binaries | BinDiff / Diaphora (traditional tools) |

### Core Advantages

Compared with traditional approaches:

| Approach | Cost for 200 functions | Time | Accuracy |
|------|--------------|------|--------|
| Manually compare across two IDA windows | Free but exhausting | Several hours | High |
| BinDiff auto-matching | Free | Fast | Medium (fails when structure changes significantly) |
| Fully delegated to a generic coding agent | ¥50-100 | Slow | High |
| **This skill (LLM batch comparison)** | **~¥1** | **~10 s/function** | **High** |

## Core Principle

```text
旧版函数（有符号）          新版同一函数（无符号）
    ↓                              ↓
导出反汇编 + 伪代码          导出反汇编 + 伪代码
    ↓                              ↓
    └──────── LLM 结构化比对 ────────┘
                    ↓
         输出 YAML（符号映射表）
                    ↓
         程序化解析 → 批量应用到新版 IDB
```

Key points:
- The prompt is a fixed template filled programmatically
- Input/output formats are fixed and parsed programmatically
- The LLM only handles the "look at two code snippets and find the correspondence" step
- Time and token costs are extremely low

## Prompt Template

### Standard Comparison Prompt

```text
I have disassembly outputs and procedure code of the same function.

This is the function for reference:

**Disassembly for Reference**
```c
{disasm_for_reference}
```

**Procedure code for Reference**
```c
{procedure_for_reference}
```

This is the function you need to reverse-engineering:

**Disassembly to reverse-engineering**
```c
{disasm_code}
```

**Procedure code to reverse-engineering**
```c
{procedure}
```

What you need to do is to collect all references to "{symbol_name_list}" in the function you need to reverse-engineering and output those references as YAML.

Example:
```yaml
found_vcall: # This is for indirect call to virtual function or virtual function pointer fetching.
  - insn_va: '0x180777700' # Always be the instruction with displacement offset
    insn_disasm: call [rax+68h] # Always be the instruction with displacement offset
    vfunc_offset: '0x68'
    func_name: ILoopMode_OnLoopActivate
  - insn_va: '0x180777778' # Always be the instruction with displacement offset
    insn_disasm: mov rax, [rax+80h] # Always be the instruction with displacement offset
    vfunc_offset: '0x80'
    func_name: INetworkMessages_GetNetworkGroupCount

found_call: # This is for direct call to non-virtual regular function.
  - insn_va: '0x180888800'
    insn_disasm: call sub_180999900
    func_name: CLoopMode_RegisterEventMapInternal
  - insn_va: '0x180888880'
    insn_disasm: call sub_180555500
    func_name: CLoopMode_SetSystemState

found_funcptr: # This is for non-virtual regular function pointer.
  - insn_va: '0x180666600' # Must load/reference the function pointer target address
    insn_disasm: lea rdx, sub_15BC910 # Must load/reference the function pointer target address
    funcptr_name: CLoopMode_OnClientPollNetworking

found_gv: # This is for reference to global variable.
  - insn_va: '0x180444400'
    insn_disasm: mov rcx, cs:qword_180666600 # Must load/reference the global variable
    gv_name: g_pNetworkMessages
  - insn_va: '0x180333300'
    insn_disasm: lea rax, unk_180222200 # Must load/reference the global variable
    gv_name: s_EventManager

found_struct_offset: # This is for reference to struct offset. NOTE THAT virtual function pointer should not be here! virtual function pointer should ALWAYS be in found_vcall !
  - insn_va: '0x1801BA12A' # Always be the instruction with displacement offset
    insn_disasm: mov rcx, [r14+58h] # Always be the instruction with displacement offset
    offset: '0x58'
    size: 8
    struct_name: CResourceService
    member_name: m_pEntitySystem
```

If nothing found, output an empty YAML. DO NOT output anything other than the desired YAML. DO NOT collect unrelated symbols.
```

### Variable Reference

| Variable | Source | Description |
|------|------|------|
| `{disasm_for_reference}` | Exported from the old-version IDA | Symbolized disassembly |
| `{procedure_for_reference}` | Exported from the old-version IDA | Symbolized pseudocode |
| `{disasm_code}` | Exported from the new-version IDA | Unsymbolized disassembly |
| `{procedure}` | Exported from the new-version IDA | Unsymbolized pseudocode |
| `{symbol_name_list}` | Extracted from the old version | The list of symbols to locate in the new version |

## Workflow

### Full Process

```text
Step 1: 准备数据
  - 旧版二进制加载到 IDA（有 PDB/符号）
  - 新版二进制加载到 IDA（无符号）
  - 找到两个版本中相同的锚点函数（导出函数、字符串引用等）

Step 2: 批量导出
  - 从旧版导出：锚点函数的反汇编 + 伪代码（含符号名）
  - 从新版导出：同一锚点函数的反汇编 + 伪代码（无符号名）

Step 3: LLM 比对
  - 用 prompt 模板填充数据
  - 调用 LLM API（推荐：deepseek 量大便宜，超大函数切 gpt）
  - 解析返回的 YAML

Step 4: 应用结果
  - 将 YAML 中的符号映射批量应用到新版 IDB
  - 用 idapro_rename 或 IDAPython 脚本批量重命名

Step 5: 迭代
  - 第一轮迁移的函数成为新的锚点
  - 进入这些函数，继续对比内部调用
  - 重复直到覆盖所有目标函数
```

### Anchor Selection Strategy

| Anchor type | Reliability | Description |
|---------|--------|------|
| Exported functions | Highest | Names stay the same, addresses may change |
| String references | High | String contents stay the same, reference locations may change |
| Constants/magic numbers | Medium | Characteristic values stay the same |
| Code patterns | Medium | Function structures are similar but all addresses change |

### Batch Processing Recommendations

- Compare one function at a time (avoid context explosion)
- Use deepseek for medium functions (<200 lines)
- Switch to gpt-4o or claude for very large functions (>500 lines)
- Use concurrent calls to improve speed (10-20 concurrent)
- Cache results to avoid repeated calls

## Output Format

### The 5 Symbol Types in YAML Output

| Type | Meaning | Key fields |
|------|------|---------|
| `found_vcall` | Virtual function call (indirect call) | `vfunc_offset`, `func_name` |
| `found_call` | Direct function call | `insn_va`, `func_name` |
| `found_funcptr` | Function pointer reference | `insn_va`, `funcptr_name` |
| `found_gv` | Global variable reference | `insn_va`, `gv_name` |
| `found_struct_offset` | Struct offset reference | `offset`, `struct_name`, `member_name` |

### Post-Parse Application Actions

```text
found_call → idapro_rename(addr=call_target, name=func_name)
found_vcall → idapro_set_comments(addr=insn_va, comment="vcall: {func_name} @ +{offset}")
found_funcptr → idapro_rename(addr=funcptr_target, name=funcptr_name)
found_gv → idapro_rename(addr=gv_addr, name=gv_name)
found_struct_offset → idapro_set_comments(addr=insn_va, comment="{struct_name}.{member_name}")
```

## Typical Scenario Examples

### Scenario 1: ntoskrnl.exe Missing PDB

```text
已有：ntoskrnl.exe 10.0.26100.2000 + 完整 PDB
目标：ntoskrnl.exe 10.0.26100.2605（PDB 被下架）
需求：定位 PspSetCreateProcessNotifyRoutine 的新地址

步骤：
1. 两个版本都加载到 IDA
2. 找到导出函数 PsSetCreateProcessNotifyRoutine（两个版本都有）
3. 旧版中它调用了 PspSetCreateProcessNotifyRoutine（有符号）
4. 新版中它调用了 sub_140822108（无符号）
5. LLM 一眼看出：sub_140822108 = PspSetCreateProcessNotifyRoutine
6. 批量应用
```

### Scenario 2: Migration After an App Update

```text
已有：target.exe v1.0 的完整逆向结果（200+ 函数已命名）
目标：target.exe v1.1（所有符号丢失）
需求：批量迁移 200 个函数名

步骤：
1. 从旧版导出所有已命名函数的反汇编+伪代码
2. 在新版中通过导出函数/字符串找到对应锚点
3. 批量调用 LLM 比对
4. 解析 YAML，批量 rename
5. 迭代深入
```

## LLM Selection Recommendations

| Model | Best for | Cost | Speed |
|------|---------|------|------|
| DeepSeek V3 | Small-to-medium functions (<200 lines), batch processing | Extremely low | Fast |
| GPT-4o | Very large functions, complex control flow | Medium | Fast |
| Claude Sonnet | Medium-to-large functions needing reasoning | Medium | Fast |
| Claude Opus | Extremely complex functions needing deep understanding | High | Slow |

Recommended strategy: default to DeepSeek; automatically upgrade when context limits are hit or results are inaccurate.

## Notes

- **Do not throw the whole binary at the LLM** — compare one function at a time
- **Anchors MUST be reliable** — if an anchor itself is matched wrong, everything downstream is wasted
- **Spot-check results manually** — the LLM is not 100% accurate; verify critical symbols
- **Cache intermediate results** — avoid wasting tokens on repeated calls
- **Mind context limits** — very large functions (>1000 lines of disassembly) need splitting or a large-context model

---

## On-Demand Bootstrap

### Tool Dependencies

| Tool | Purpose | Auto-installable |
|------|------|-----------|
| IDA Pro | Export disassembly/pseudocode | ✗ (commercial software) |
| Python | Script execution, API calls | ✓ |
| PyYAML | Parse the YAML returned by the LLM | ✓ (pip install pyyaml) |
| LLM API | Perform the comparison | Requires an API key |

### Notes

The core of this skill does not depend on heavy tool installs; it mainly relies on:
- IDA Pro already available (managed by the `ida-reverse/` skill)
- Python + requests/httpx (for API calls)
- An LLM API endpoint

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Trigger condition**: you have old-version symbols/reversal results and need to migrate them to a new version
**Downstream exits**:
- Need to open the binary first → `ida-reverse/`
- Need quick recon to confirm version differences → `radare2/`

**Peer modules**: `ida-reverse/` (both data export and symbol application go through IDA)


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than only reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
