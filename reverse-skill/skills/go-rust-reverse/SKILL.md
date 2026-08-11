---
name: go-rust-reverse
description: Use for reverse engineering stripped Go and Rust binaries including runtime recognition, pclntab/moduel data recovery, panic strings, and idiomatic decompilation recovery.
---

# Go / Rust Binary Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md`
2. `NOW`: Confirm the sample is a Go/Rust build artifact (`file`/strings/runtime characteristics)
3. `NEXT`: Check whether GoReSym / related plugins are available
4. `ACT`: Runtime identification → symbol/metadata recovery → business logic

## When to Use

- Stripped-symbol Go malware/tools
- Rust release binaries, panic-string-driven analysis
- Language-specific methods complementary to general ida/ghidra

## Workflow

### Go

```text
□ Identify go.buildid, runtime symbol remnants, pclntab
□ Recover function names with GoReSym / redress / IDA Go plugin
□ Note the shapes of interface, slice, and string structures in decompiled output
□ Network/crypto library paths: crypto/* net/http
```

### Rust

```text
□ panic strings, rust_begin_unwind, crate path hints
□ Code bloat from generic instantiation; locate string xrefs first
□ Async/tokio state machines require cross-reference analysis
```

### Dynamic

```text
□ Frida still works; mind Go stacks and scheduling
□ Prefer log and config string-driven breakpoints
```

## Toolchain

| Tool | Purpose |
|------|------|
| GoReSym | Go metadata |
| IDA/Ghidra + Go/Rust plugins | Decompilation |
| radare2 | Quick strings |
| strings / rabin2 | Triage |

## References

- `references/go-rust-notes.md`
- `../reverse-engineering/go-reverse.md` `../ida-reverse/` `../ghidra-reverse/`
- seed: `field-journal/seed-002_go-malware-stripped.md`

## Routing Context

**Upstream**: MASTER R33  
**Downstream**: malware sample workflow `malware-analysis`; general RE `reverse-engineering`

## Task Completion Self-Check

- [ ] Were key function names or equivalent mappings recovered?
- [ ] Was the language runtime evidence annotated?
- [ ] Checklist?
