---
name: ghidra-reverse
description: Use for free/open reverse engineering with Ghidra (headless or GUI), including decompile, cross-refs, and optional Ghidra MCP workflows when IDA is unavailable.
---

# Ghidra Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm **Ghidra** is needed (no IDA / prefer open source / batch headless)
3. `NEXT`: read `../tool-index.md` for ghidra / ghidra-mcp paths (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
4. `NEXT`: missing tool → bootstrap `ghidra-mcp` (the manifest supports it) or install Ghidra: download the latest release ZIP from https://github.com/NationalSecurityAgency/ghidra/releases/latest, unzip to a tools dir, then run `support/analyzeHeadless` (Linux/macOS) or `support\analyzeHeadless.bat` (Windows); alternatively `winget install ghidra` or your package manager
5. `ACT`: import sample → auto analyze → export decompilation of key functions

## Applicable Scenarios

- Primary reverse-engineering entry point when no IDA license is available
- Batch headless analysis / decompilation in CI
- Ghidra scripting automation (Java/Python Jython/PyGhidra)
- ghidriff integration with `binary-diff` / `patch-diff-exploit`

## Division of Work with IDA

| Requirement | Priority |
|------|------|
| Existing IDA MCP deep-dive | `ida-reverse/` |
| Open source / batch / teaching | **this skill** |
| CLI-only quick recon | `radare2/` |

## Workflow

### 1. Project and Auto Analysis

```text
□ New Project → Import file → Analyze (default analyzers)
□ Record language/compiler identification results and base address
□ Mark entry points, export tables, string xrefs
```

### 2. Key Functions

```text
□ Trace back from strings / imported APIs
□ Reconstruct algorithms in the Decompile window
□ Rename functions/variables; write Plate comments
□ When dynamic analysis is needed, hand off to Frida/GDB (reverse-engineering dynamic chapter)
```

### 3. Headless (Batch)

```bash
# Example: analyzeHeadless path varies by install, MUST take it from tool-index
analyzeHeadless /path/to/project Proj -import sample.bin -postScript ExportDecomp.py
```

### 4. MCP (if configured)

```text
□ Confirm the ghidra MCP port (commonly 8765, tool-index is authoritative)
□ Pull decompilation / xrefs with MCP tools; do not guess ports
```

## Toolchain

| Tool | Purpose | Bootstrap |
|------|------|------|
| Ghidra | main decompilation tool | manual release / package manager |
| ghidra-mcp | AI bridge | bootstrap capability name `ghidra-mcp` |
| ghidriff | patch diffing | see `patch-diff-exploit` |

## References

- `references/ghidra-cheatsheet.md`
- `../ida-reverse/` `../radare2/` `../binary-diff/`

## Routing Context

**Upstream**: MASTER R22  
**Downstream**: dynamic verification → Frida/GDB; exploitation → `pwn-chain`  
**Peer**: `ida-reverse` (commercial deep-dive)

## Task Completion Self-Check

- [ ] Are real Ghidra/tool-index paths used?
- [ ] Are function addresses and renames noted?
- [ ] Are steps reproducible?
- [ ] Checklist / journal?