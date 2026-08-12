# Go Binary Reversing Guide

> Go-compiled binaries present unique challenges: static linking makes them huge, function counts reach tens of thousands, string formats are unusual, and symbol recovery after strip is difficult.
> This document covers the toolchain, recovery techniques, and real-world workflows.

---

## Identifying Go Binary Traits

Quickly determine whether a binary is Go-compiled:

```bash
# String traits
strings binary | grep -E "runtime\.|go\.buildid|GOROOT"

# rabin2 recon
rabin2 -z binary | grep -i "runtime"

# abnormally large file size (statically linked runtime)
# typical Hello World: C ~20KB, Go ~2MB
```

Common traits:
- a large number of functions with the `runtime.` prefix
- contains a `go.buildid` section
- contains `GOROOT`/`GOPATH` path strings
- 5,000-50,000+ functions (includes the whole runtime and stdlib)

---

## Core Toolchain

### Symbol Recovery

| Tool | Purpose | Link |
|------|------|------|
| **GoReSym** | by Mandiant; parses Go symbol info (pclntab/moduledata) | https://github.com/mandiant/GoReSym |
| **GoResolver** | by Volexity; auto-deobfuscates Garble binaries via CFG similarity | https://github.com/volexity/GoResolver |
| **redress** | analyzes stripped Go binaries; recovers types/interfaces/package structure | https://github.com/goretk/redress |
| **GoStringUngarbler** | by Google; recovers Garble-obfuscated strings | https://github.com/mandiant/GoStringUngarbler |

### IDA Plugins

| Tool | Purpose | Link |
|------|------|------|
| **go_parser** | IDA plugin; parses moduledata/pclntab/type info | https://github.com/0xjiayu/go_parser |
| **IDAGolangHelper** | IDA script set; parses Go type info | https://github.com/sibears/IDAGolangHelper |
| **AlphaGolang** | SentinelLabs IDAPython script set | https://github.com/SentineLabs/AlphaGolang |
| **IDA 9.2+ native support** | Hex-Rays official Go decompilation improvements | https://hex-rays.com/blog/stop-guessing-and-start-going |

### Ghidra Plugins

| Tool | Purpose | Link |
|------|------|------|
| **Ghidra + GoReSym output** | export symbols with GoReSym, then import into Ghidra | used together |
| **golang_loader_assist** | Ghidra Go loading helper | community script |

### Standalone Analysis Tools

| Tool | Purpose | Link |
|------|------|------|
| **gore** | Go reverse-engineering library (underlies redress) | https://github.com/goretk/gore |
| **garble** | Go obfuscator (know it to fight it) | https://github.com/burrowers/garble |

---

## Key Structures in Go Binaries

### pclntab (PC Line Table)

The most important structure in Go binaries; it contains:
- all function-name to address mappings
- source file paths
- line-number info
- stack-frame sizes

Even after stripping symbols, pclntab usually survives (the Go runtime depends on it).

```text
How to locate it:
1. search for the magic bytes: 0xFFFFFFF0 (Go 1.16+) or 0xFFFFFFFB (Go 1.18+)
2. let GoReSym locate it automatically
3. parse it automatically with the go_parser IDA plugin
```

### moduledata

Contains:
- the pclntab pointer
- the type-info table
- itab (interface table)
- global-variable info

### String Format

Go strings are not C-style null-terminated; they are `(pointer, length)` structures:

```text
C string:   "hello\0"
Go string:  struct { ptr *byte; len int } → ptr points at "hello" (no \0)
```

As a result, IDA/Ghidra default string recognition misses many Go strings.

**Solutions**:
- use `go_parser` to auto-identify Go strings
- export the string list with GoReSym
- manually: locate `runtime.stringtable` or use cross-references

---

## Real-World Workflows

### Scenario 1: Unstripped Go Binary

```text
1. GoReSym -t -d -p binary > symbols.json
   → exports all function names, types, and source file paths
2. load into IDA/Ghidra
3. import GoReSym's symbol info
4. filter out runtime.* and stdlib functions, focus on user code
5. start analysis at main.main
```

### Scenario 2: Stripped Go Binary

```text
1. GoReSym -t -d -p binary > symbols.json
   → even stripped, pclntab usually survives
2. if GoReSym fails → use redress
   redress -src binary    # recover source file paths
   redress -pkg binary    # recover package structure
   redress -type binary   # recover type info
3. load into IDA + the go_parser plugin
4. run go_parser to auto-recover
5. start from the recovered main.main
```

### Scenario 3: Garble-Obfuscated Go Binary

```text
Garble will:
- randomize function names (main.main → main.a3f2b1c)
- encrypt strings
- remove file-path info
- obfuscate package names

Countermeasures:
1. GoResolver (CFG signature matching)
   → recovers stdlib function names via control-flow-graph similarity
2. GoStringUngarbler (string decryption)
   → auto-identifies and decrypts Garble's string-encryption patterns
3. dynamic analysis (Frida/dlv)
   → hook runtime functions to observe actual behavior
4. comparative analysis
   → compile a same-version Go Hello World and use binary-diff to compare the runtime section
```

### Scenario 4: CGo Mixed Compilation

```text
1. identify the CGo boundary (_cgo_* functions)
2. recover the Go part with go_parser
3. analyze the C part with normal IDA
4. watch the bridging functions: _cgo_topofstack, crosscall2, etc.
```

---

## Common Commands Quick Reference

```bash
# GoReSym: export symbols
GoReSym -t -d -p binary > symbols.json
GoReSym -t -d -p binary -o ida_script.py  # generate an IDA script

# redress: analyze a stripped binary
redress -src binary          # source file paths
redress -pkg binary          # package structure
redress -type binary         # type info
redress -interface binary    # interface info
redress -filepath binary     # full file paths

# GoResolver: deobfuscate Garble
GoResolver -binary binary -output resolved.json

# GoStringUngarbler: decrypt Garble strings
GoStringUngarbler -i binary -o deobfuscated_binary

# quickly determine the Go version
strings binary | grep "go1\."
GoReSym -p binary | grep "Version"
```

---

## Go Analysis Flow in IDA

```text
1. load the binary (select the correct architecture)
2. wait for auto-analysis to finish
3. run the go_parser plugin:
   - File → Script File → go_parser.py
   - or Edit → Plugins → Go Parser
4. the plugin will automatically:
   - parse pclntab
   - recover function names
   - mark Go strings
   - parse type info
5. filter the view:
   - hide runtime.* functions
   - focus on main.* and third-party packages
6. start reversing from main.main
```

---

## Common Pitfalls

| Pitfall | Description | Solution |
|------|------|------|
| too many functions | static linking yields 5,000-50,000 functions | filter by package; look at main.* and business packages only |
| incomplete string recognition | Go strings are not null-terminated | recover with go_parser or GoReSym |
| hard-to-read decompilation | Go defer/goroutine/interface complicate pseudocode | IDA 9.2+ improved; or assist with dynamic analysis |
| Garble obfuscation | function names/strings all randomized | GoResolver + GoStringUngarbler |
| version differences | pclntab format varies across Go versions | GoReSym supports Go 1.2-1.23+ |
| CGo boundary | Go and C code mixed | treat _cgo_* functions as the boundary |

---

## Working with Other Skills

| Need | Use |
|------|--------|
| deep IDA analysis of Go binaries | `ida-reverse/` + the go_parser plugin |
| Ghidra analysis (free) | Ghidra + GoReSym symbol import |
| quick recon | `radare2/` — `rabin2 -z` for strings |
| dynamic hooking | Frida (hook runtime functions) or dlv (Go-native debugger) |
| cross-version comparison | `binary-diff/` — migrate symbols from the old version to the new |
| Garble deobfuscation | GoResolver + GoStringUngarbler |
