---
name: ida-reverse
description: >-
  Use for IDA Pro reverse engineering assistance. When the user mentions reverse engineering, decompilation,
  binary/PE/ELF/APK/DLL/SO analysis, cracking, password finding, vulnerability analysis, malware analysis,
  firmware analysis, or needs to analyze exe/dll/so/elf/macho/sys files, use this skill.
---

# IDA Pro Reverse Engineering Skill

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm this skill's operations are an authorized, routine activity
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` and verify tool availability and actual paths (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Enter step one of the "workflow" and execute; do not stop at confirmation

## Known Issues and Lessons Learned (Must Read)

### Pitfalls Encountered

1. **`idalib_open` cannot be called directly through some code-AI-client MCPs**
   - Some code AI clients' MCP clients have a BUG validating `idalib_open`'s output schema
   - Error: `Structured content does not match the tool's output schema`
   - **Solution**: use the `scripts/open.ps1` script to call it directly via the HTTP API, bypassing the MCP validation layer
   - After the file opens, the database is bound to the shared context and all other `idapro_*` tools can be used directly

2. **Files under `C:\Windows\System32\` cannot be opened due to permission issues**
   - idalib cannot directly read files under the System32 directory
   - **Solution**: `scripts/open.ps1` auto-detects and copies the file to a `temp directory` before opening

3. **Starting the server command blocks the conversation**
   - After starting, `idalib-mcp` keeps outputting INFO logs to the console
   - **Solution**: use `scripts/start.ps1` (background silent start with `-WindowStyle Hidden`)
   - The script waits for the service to be ready, then exits automatically without blocking the conversation

4. **The MCP server name cannot contain a hyphen**
   - Previously used `ida-pro-mcp` as the server name, which could cause tool registration problems
   - **Current config**: server name `idapro`, tool prefix `idapro_*`

5. **Remote HTTP vs Local Stdio**
   - `type:"local"` (stdio) mode: `idalib_open` has the same schema validation problem
   - `type:"remote"` (HTTP) mode: you can first open the file directly with the script, then use the MCP tools
   - **Current approach**: Remote HTTP mode

6. **PR #389 fixed some schema issues**
   - Author mrexodia merged the fix via PR #389 after issue #388
   - Fixed the structuredContent schema in HTTP mode, but validation on some code-AI-client side still has issues
   - The latest `main` branch version is installed

7. **idalib timeout leaves orphaned worker processes holding lock files**
   - After the first `scripts/open.ps1` timeout, idalib's python worker child process becomes an orphan and keeps holding `.id0`/`.id1`/`.nam` files
   - Any subsequent tool or manual drag into the IDA GUI reports "insufficient permissions"
   - **Solution**: `scripts/start.ps1` now uses `taskkill /F /T` to kill the process tree, leaving no orphans
   - **Fallback**: `scripts/open.ps1` now auto-degrades — when an old database is detected as locked, it copies it to Temp with a GUID prefix

8. **Opening with auto-analysis looks like a hang**
   - `idalib_open(run_auto_analysis=true)` may not respond for a long time, but the backend is still opening and analyzing
   - Previously the user saw "PowerShell with no output" and could easily misjudge it as a hung script
   - **Current solution**: `scripts/open.ps1` adds `-TimeoutSeconds` and switches to background request + foreground polling + periodic progress output
   - When polling finds the session ready it returns `OK:filename:session_id` early; on timeout it returns `ERR:open_timeout_xxs`

### Workflow Principles

| Step | What to do | What to use |
|------|--------|--------|
| 1 | Ensure the HTTP server is running | `scripts/start.ps1` (no arguments) |
| 2 | Open the target binary | `scripts/open.ps1 -Path "xxx.exe"` |
| 3 | Use all 72 MCP tools | Call `idapro_*` tools directly |
| 4 | Analysis complete | Tools remain available automatically |

## Script Resources

### start.ps1 — Start the MCP HTTP server

Path: `scripts/start.ps1`

- Kill the old process tree with `taskkill /F /T` (cleaning up worker child processes too) → start `idalib-mcp` in the background → wait until ready (up to 15 seconds)
- On success prints `OK:72`; on failure prints `ERR:timeout`
- The server runs in the background and does not block the conversation

**Invocation**:
```
powershell -File "<skill-root>\ida-reverse\scripts\start.ps1"
```

### open.ps1 — Open a binary file

Path: `scripts/open.ps1`

- Calls `idalib_open` directly via the HTTP API, bypassing MCP schema validation
- Auto-detects System32 paths and copies to a temp directory
- Auto-cleans old database files with the same name (`.id0`/`.id1`/`.nam`/`.til`/`.i64`)
- Auto-degrades when the old database is locked: copies to Temp with a GUID prefix, then opens without error
- Runs the open request in the background to avoid long synchronous waits making the script unresponsive
- Supports `-TimeoutSeconds`; on timeout returns `ERR:open_timeout_xxs` instead of hanging forever
- Prints `INFO:opening:elapsed/timeout` every 10 seconds so you can tell analysis is still running
- On success prints `OK:filename:session_id`; adds the `(temp copy)` marker when degraded
- On failure automatically retries with a Temp copy

**Invocation**:
```
powershell -File "<skill-root>\ida-reverse\scripts\open.ps1" -Path "C:\path\to\file.exe"
```

**Optional parameters**:
```
# Specify SessionId
powershell -File "scripts\open.ps1" -Path "file.exe" -SessionId "my_session"

# Skip auto-analysis (recommended for large files)
powershell -File "scripts\open.ps1" -Path "large.exe" -NoAutoAnalysis

# Set a timeout to avoid long no-response periods when auto-analysis is enabled
powershell -File "scripts\open.ps1" -Path "file.exe" -TimeoutSeconds 600
```

**Output conventions**:
```
# Analysis in progress (printed every 10 seconds)
INFO:opening:11/600s

# Successfully opened
OK:sample.exe:abcd1234

# Successfully opened, but degraded to a Temp copy due to locked files
OK:1234abcd-sample.exe:abcd1234 (temp copy)

# Reached the timeout limit
ERR:open_timeout_600s
```

**Measured notes**:
- With auto-analysis, `Snipaste.exe` took about `324s` to return success in testing — that's "long analysis", not a "script deadlock"
- So for GUI programs or more complex samples, prefer explicitly setting `-TimeoutSeconds 600`

## Core Tool List

### Survey Analysis (First Step)
- `idapro_survey_binary(detail_level="minimal")` — quick overview: function count, strings, segments, entry point, import classification (crypto/network/file I/O)
- `idapro_list_funcs(queries)` — list functions (paginated, filterable by name)
- `idapro_list_globals(queries)` — list global variables
- `idapro_entity_query(kind, filter)` — unified query: functions/globals/imports/strings/names

### Decompilation and Disassembly
- `idapro_decompile(addr)` — decompile to pseudocode
- `idapro_disasm(addr, max_instructions=N)` — disassemble
- `idapro_analyze_function(addr, include_asm=false)` — comprehensive analysis (pseudocode + strings + constants + callers + callees + blocks)
- `idapro_func_profile(queries)` — function profile metrics

### Cross-References and Data Flow
- `idapro_xrefs_to(addrs)` — find who references the target address
- `idapro_xref_query(addr, direction)` — advanced xref query (direction/type filtering)
- `idapro_callees(addrs)` — list of callees
- `idapro_callgraph(roots, max_depth)` — call graph
- `idapro_trace_data_flow(addr, direction, max_depth)` — data flow tracing (forward/backward)

### Search
- `idapro_find_regex(pattern, limit)` — regex search for strings
- `idapro_search_text(pattern)` — search text in the disassembly listing
- `idapro_find_bytes(patterns, limit)` — byte pattern search (supports ?? wildcards)
- `idapro_find(type, targets)` — advanced search (immediates/strings/references)

### Memory and Data
- `idapro_get_bytes(addrs)` — read raw bytes
- `idapro_get_string(addrs)` — read strings
- `idapro_get_int(queries)` — read integer values
- `idapro_get_global_value(queries)` — read global variable values
- `idapro_read_struct(queries)` — read struct field values
- `idapro_search_structs(filter)` — search structs

### Modification Operations
- `idapro_set_comments(items)` — add comments (bidirectionally synced between disassembly and decompilation)
- `idapro_append_comments(items)` — append comments
- `idapro_rename(batch)` — batch rename (functions/globals/locals/stack variables)
- `idapro_patch_asm(items)` — patch assembly instructions
- `idapro_patch(patches)` — patch bytes
- `idapro_define_func(items)` — define functions
- `idapro_undefine(items)` — undefine
- `idapro_define_code(items)` — convert bytes to code

### Type System
- `idapro_declare_type(decls)` — declare C structs/enums/unions
- `idapro_set_type(edits)` — apply types to functions/globals/locals
- `idapro_infer_types(addrs)` — infer types
- `idapro_type_query(queries)` — query declared types
- `idapro_type_inspect(queries)` — inspect type details

### Stack Frames
- `idapro_stack_frame(addrs)` — view stack frame variables
- `idapro_declare_stack(items)` — declare stack variables
- `idapro_delete_stack(items)` — delete stack variables

### Signatures
- `idapro_make_signature(addrs)` — generate a unique byte signature for an address
- `idapro_make_signature_for_function(addrs)` — generate a signature for a function
- `idapro_find_xref_signatures(addrs)` — generate signatures for code referencing the address

### Debugger (requires ?ext=dbg)
- `idapro_open_file(file_path)` — open the file in a GUI IDA instance
- Debugger tools are hidden by default; enable them via the URL parameter `?ext=dbg`

### Session Management
- `idapro_idalib_open(input_path)` — ⚠️ has a schema validation BUG; use the `scripts/open.ps1` script instead
- `idapro_idalib_list()` — list all sessions
- `idapro_idalib_current()` — the session bound to the current context
- `idapro_idalib_switch(session_id)` — switch to another session
- `idapro_idalib_close(session_id)` — close a session
- `idapro_idalib_save(path)` — save the database
- `idapro_idalib_health(session_id)` — check worker health

### Other
- `idapro_int_convert(inputs)` — base conversion (**MUST use this; do not compute bases yourself!**)
- `idapro_export_funcs(addrs, format)` — export functions (json/c_header/prototypes)
- `idapro_py_eval(code)` — execute Python in the IDA context
- `idapro_server_health()` — server health check
- `idapro_server_warmup()` — warm up subsystems (string cache, Hex-Rays, etc.)

## Complete Reverse Engineering Workflow

### Step 1: Start the Server
Make sure the HTTP service is running in the background.
```
powershell -File "scripts/start.ps1"
```
Output `OK:72` means it is ready.

### Step 2: Open the File
```
powershell -File "scripts/open.ps1" -Path "C:\target.exe" -TimeoutSeconds 600
```
Output `OK:filename:session_id` means success (followed by `(temp copy)` means it automatically degraded to a temp copy).
If analysis takes long, `INFO:opening:...` is printed periodically; if the timeout is reached, `ERR:open_timeout_xxs` is printed.

### Step 3: Global Overview (with Hard Gate on Import Table)
```
idapro_survey_binary(detail_level="minimal")
```
Focus on:
- Architecture (x86/x64/ARM)
- Entry point (main/WinMain/DllMain)
- Interesting strings (URLs, paths, error messages)
- **Import classification (MUST)**: crypto functions / network APIs / file operations / process injection / registry — MUST be recorded as Evidence (suggested id: `E-imports`), using `idapro_entity_query(kind="imports")` or the imports section of the survey output
- Popular functions (functions with high xref counts are usually critical logic)

**Hard gate**: until the imports view/classification summary is written to Evidence, MUST NOT proceed to Step 4 for deep-dive conclusions and MUST NOT claim the survey is complete. Even when the import table is empty or the query fails, you MUST still record the failure. When the user asks to redo the import table check, you MUST redo this step and are forbidden from substituting other steps.

### Step 4: Deep-Dive Key Functions
```
idapro_analyze_function(addr="key_function")
```
Or:
```
idapro_decompile(addr="function_name")
idapro_disasm(addr="function_name", max_instructions=50)
```

### Step 5: Data Flow and Cross-References
```
idapro_xrefs_to(addrs="key_address/string")
idapro_callgraph(roots=["key_function"], max_depth=3)
idapro_trace_data_flow(addr="key_address", direction="backward", max_depth=5)
```

### Step 6: Annotate and Refine
```
idapro_set_comments(items=[{"addr": "0x140001000", "comment": "your_understanding"}])
idapro_rename(batch={"func": [{"addr": "function_address", "name": "meaningful_name"}]})
```

### Step 7: Produce the Report
After analysis is complete, generate `report.md` recording findings and steps.

## Prompt Engineering Guidelines

1. **Never compute bases manually** — whenever you need to convert a number, use `idapro_int_convert`
2. **Survey before deep-diving** — look at the overview first, then analyze with a purpose
3. **Keep adding comments and renames** — continuously update function and variable names during analysis to improve downstream accuracy
4. **Track cross-references** — when you find interesting data/strings, use `xrefs_to` to see who references them
5. **On obfuscated code** — first do preprocessing such as string decryption, import-hash removal, and control-flow-flattening removal
6. **C++ STL code** — use FLIRT/Lumina to identify library functions before analyzing business logic
7. **Don't brute-force** — analysis should derive solutions from the disassembly, using simple Python only for auxiliary computation
8. **On "No database bound"** — no binary has been opened yet; run `scripts/open.ps1` first
9. **On "Failed to open database"** — old database files may be locked; `scripts/open.ps1` will auto-degrade to a Temp copy (output includes the `(temp copy)` marker)
10. **When opening GUI/complex samples with auto-analysis** — add `-TimeoutSeconds 600` by default; don't mistake long `INFO:opening:...` output for a hung script

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternative**: `radare2/` (if you don't want to launch IDA, do a quick r2 recon first)
**Downstream exits**:
- Need Frida dynamic verification → `reverse-engineering/tools-dynamic.md`
- Need symbolic execution/angr → `reverse-engineering/tools-dynamic.md`
- Need general reverse engineering methodology → `reverse-engineering/SKILL.md`

**Peer module**: `radare2/` (fallback when IDA is unavailable)

---

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system.

### Automation Capability Boundaries

| Tool | Auto-installable | Installation method | Notes |
|------|-----------|---------|------|
| idalib-mcp | ✓ | pip install (from GitHub) | `scripts/start.ps1` auto-installs it when missing |
| IDA Pro itself | ✗ | Commercial software, manual install required | Set the `IDADIR` environment variable to point at the installation directory |

### Installation Steps (Verified)

```cmd
# 1. Set the IDA path (replace with your actual IDA installation directory)
setx IDADIR "<your_IDA_install_dir>"

# 2. Install ida-pro-mcp from GitHub (ida-mcp on PyPI is a different project — don't install the wrong one!)
pip install git+https://github.com/mrexodia/ida-pro-mcp.git

# 3. Install the IDA plugin (select Streamable HTTP + Global + all clients)
ida-pro-mcp --install

# 4. Restart IDA Pro and open the target file
# The plugin automatically listens on 127.0.0.1:13337

# 5. Verify
ida-pro-mcp --config
```

> ⚠️ **Note**: the `ida-mcp` package on PyPI (author jtsylve) is a different project — not the one we need.
> You MUST install `mrexodia/ida-pro-mcp` from GitHub.

### Bootstrap Trigger Points

- `scripts/start.ps1`: automatically calls `bootstrap-reverse.ps1` when `idalib-mcp` is missing
- MCP registration: bootstrap automatically writes `idapro` into the agent's MCP configuration (e.g. Hermes `config.yaml` `mcp_servers`)

### Prerequisites

- IDA Pro installed and the `IDADIR` environment variable set (or the default path in the script is correct)
- Python installed (idalib-mcp depends on Python)


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading it)?
- [ ] Has the survey/imports been written to Evidence (E-imports)? If the user asked to redo the import table, did I redo the same step?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
