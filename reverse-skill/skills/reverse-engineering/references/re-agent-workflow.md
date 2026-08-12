# RE Agent Workflow Gates (Static ↔ Dynamic)

> Inspirational sources: binary-re phase division, community RE skills (Frida/r2/Ghidra/IDA loops), Cerberus three-head ring (static/dynamic/instrumentation)  
> Date: 2026-07-17  
> Applies to: `reverse-engineering/`, `ida-reverse/`, `radare2/`, and handoffs with the cre role

## 0. Startup

```text
□ scope.md: offline sample path or authorized device/target
□ tool-index: actual paths for file/strings/r2/ida/frida etc.
□ role: cre (ops/role-map)
```

## 1. Triage (5–15 minutes)

```text
□ file / DIE / entropy / packer characteristics
□ strings / rabin2 -z sweep
□ architecture/linking/.NET/Go/Rust/packed
□ MUST imports/exports: rabin2 -i / -E (or IDA imports / equivalent)
□ Output: E-triage (MUST include imports classification summary: network/file/crypto/injection/registry) + hypothesis list (no premature conclusions)
```

**Phase gate (Triage → Static/Dynamic)**: until the imports summary is recorded in E-triage, MUST NOT enter Dynamic, and MUST NOT claim "basic triage complete". If the import table fails to parse, the failure output MUST still be written to Evidence — skipping is not allowed. When the user asks to "redo the import table check", the imports step itself MUST be redone; substituting other analysis steps is forbidden.

## 2. Static

| Tool | When |
|------|------|
| radare2 / rabin2 | Fast functions/imports/strings (imports already MUST-completed in Triage) |
| IDA / Ghidra (MCP or headless) | Deep dive, cross-references, types; re-check imports classification during survey |
| jadx / dnSpy | Android / .NET |
| OLLVM docs | When control flow flattening is suspected |

```text
□ Confirm E-imports / E-triage already contains the import-table Evidence (fill it first if missing; deferring is forbidden)
□ Locate key functions (crypto/validation/network/licensing)
□ Record addresses/symbols → Evidence
□ If one path fails → switch tools (IDA?r2?Ghidra)
```

**Without MCP**: export decompiled text and analyze it (per P4nda0s reverse-skills / IDA-NO-MCP approach); still record the Evidence path.

## 3. Dynamic

```text
□ Frida / gdb / emulator: validate static hypotheses
□ Anti-debug / anti-Frida → reverse-engineering/anti-analysis
□ Android: generate root detection / SSL pinning bypass scripts as needed, **only on authorized devices**
□ Crash logs drive the next hook round (adaptive loop)
```

## 4. Synthesis

```text
□ Finding: algorithm/validation logic/exploitable points
□ Path: callflow or solve steps attached to E-*
□ Report via docs-generator + optional diagrams
□ field-journal, desensitized
```

## 5. Differences From "Stacked RE Skill Plugins"

- This pack uses **phase gates + tool-index**; it does not enable Hex-Rays-style "unsafe full-auto execution" plugins by default  
- Dynamic instrumentation defaults to the **offline/lab** network_profile

