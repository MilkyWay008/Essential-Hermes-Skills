# IDA Pro MCP Tool Cheatsheet

> 72 MCP tools grouped by function, with common parameters and typical usage.
> Server name: `idapro`, tool prefix: `idapro_*`, runs in HTTP mode.

---

## Startup and Session Management

### Server Startup

```powershell
# start the MCP HTTP server (silent background)
powershell -File "scripts/start.ps1"
# output OK:72 means ready

# open the target file (bypasses schema validation)
powershell -File "scripts/open.ps1" -Path "C:\target.exe"
# output OK:filename:session_id

# large files/GUI programs: add a timeout
powershell -File "scripts/open.ps1" -Path "C:\big.exe" -TimeoutSeconds 600

# skip auto analysis (fast open)
powershell -File "scripts/open.ps1" -Path "C:\huge.sys" -NoAutoAnalysis
```

### Session Tools

| Tool | Purpose | Example |
|------|------|------|
| `idapro_idalib_list()` | list all sessions | — |
| `idapro_idalib_current()` | currently bound session | — |
| `idapro_idalib_switch(session_id)` | switch session | when comparing multiple files |
| `idapro_idalib_close(session_id)` | close a session | free resources |
| `idapro_idalib_save(path)` | save the database | save analysis progress |
| `idapro_idalib_health(session_id)` | check worker status | troubleshoot hangs |
| `idapro_server_health()` | server health check | — |
| `idapro_server_warmup()` | warm up subsystems | before first use |

---

## First Step: Global Overview

### survey_binary — Quick Profile

```
idapro_survey_binary(detail_level="minimal")
```

Returns:
- Architecture (x86/x64/ARM/MIPS)
- Entry point
- Total function count
- String statistics
- Segment info
- Import classification (crypto/network/file IO/registry)
- High-xref hot functions

**detail_level options**:
- `"minimal"` — quick profile (recommended first)
- `"standard"` — includes more detail
- `"full"` — complete information

### Function Listing

```
# list all functions (paged)
idapro_list_funcs(queries=[{"offset": 0, "limit": 50}])

# filter by name
idapro_list_funcs(queries=[{"filter": "crypt", "offset": 0, "limit": 20}])
idapro_list_funcs(queries=[{"filter": "main", "offset": 0, "limit": 10}])
```

### Unified Query

```
# query imported functions
idapro_entity_query(kind="imports", filter="Create")

# query strings
idapro_entity_query(kind="strings", filter="http")

# query all named symbols
idapro_entity_query(kind="names", filter="")
```

---

## Decompilation and Disassembly

### Decompile (pseudocode)

```
# by function name
idapro_decompile(addr="main")
idapro_decompile(addr="sub_140001000")

# by address
idapro_decompile(addr="0x140001000")
```

### Disassembly

```
# default instruction count
idapro_disasm(addr="main")

# specify instruction count
idapro_disasm(addr="0x401000", max_instructions=100)
```

### Combined Analysis (recommended)

```
# get everything at once: pseudocode + strings + constants + callers + callees + basic blocks
idapro_analyze_function(addr="main", include_asm=false)

# include assembly
idapro_analyze_function(addr="sub_401000", include_asm=true)
```

### Function Profile

```
# batch function metrics (size, block count, xref count)
idapro_func_profile(queries=["main", "sub_401000", "sub_402000"])
```

---

## Cross-References and Call Graphs

### Who References the Target

```
# see who calls a function
idapro_xrefs_to(addrs=["sub_401000"])

# see who references a string/data
idapro_xrefs_to(addrs=["0x404000"])

# batch query
idapro_xrefs_to(addrs=["CreateFileW", "ReadFile", "WriteFile"])
```

### Advanced Xref Query

```
# specify direction and type
idapro_xref_query(addr="0x401000", direction="to")    # who references me
idapro_xref_query(addr="0x401000", direction="from")  # who I reference
```

### Callee Listing

```
idapro_callees(addrs=["main"])
```

### Call Graph

```
# from main, depth 3
idapro_callgraph(roots=["main"], max_depth=3)

# multiple roots
idapro_callgraph(roots=["sub_401000", "sub_402000"], max_depth=2)
```

### Data Flow Tracing

```
# backward trace: where does this value come from
idapro_trace_data_flow(addr="0x401050", direction="backward", max_depth=5)

# forward trace: where does this value flow to
idapro_trace_data_flow(addr="0x401050", direction="forward", max_depth=5)
```

---

## Search

### String Search (regex)

```
# search URLs
idapro_find_regex(pattern="https?://", limit=20)

# search file paths
idapro_find_regex(pattern="C:\\\\", limit=20)

# search error messages
idapro_find_regex(pattern="error|fail|invalid", limit=30)

# search key/password related
idapro_find_regex(pattern="key|password|secret|token", limit=20)
```

### Disassembly Text Search

```
# search within the disassembly listing
idapro_search_text(pattern="call    sub_")
idapro_search_text(pattern="xor     eax, eax")
```

### Byte Pattern Search

```
# exact bytes
idapro_find_bytes(patterns=["48 8B 05"], limit=10)

# with wildcards
idapro_find_bytes(patterns=["48 89 ?? 24 ??"], limit=10)

# multiple patterns
idapro_find_bytes(patterns=["CC CC CC CC", "90 90 90 90"], limit=5)
```

### Advanced Search

```
# search immediates
idapro_find(type="immediate", targets=["0xDEADBEEF"])

# search string references
idapro_find(type="string", targets=["password"])
```

---

## Memory and Data Reading

### Read Raw Bytes

```
idapro_get_bytes(addrs=[{"addr": "0x401000", "size": 64}])
```

### Read Strings

```
idapro_get_string(addrs=["0x404000", "0x404100"])
```

### Read Integers

```
idapro_get_int(queries=[{"addr": "0x405000", "size": 4}])
```

### Read Global Variables

```
idapro_get_global_value(queries=["g_flag", "g_key_size"])
```

### Read Structs

```
idapro_read_struct(queries=[{"addr": "0x405000", "type": "HEADER"}])
```

### Search Structs

```
idapro_search_structs(filter="FILE")
```

---

## Modification Operations

### Add Comments

```
# single comment
idapro_set_comments(items=[{"addr": "0x401000", "comment": "decryption function entry"}])

# batch comments
idapro_set_comments(items=[
    {"addr": "0x401000", "comment": "XOR decryption loop"},
    {"addr": "0x401050", "comment": "key initialization"},
    {"addr": "0x4010A0", "comment": "result validation"}
])

# append comment (without overwriting existing)
idapro_append_comments(items=[{"addr": "0x401000", "comment": "supplement: key length 16"}])
```

### Rename

```
# rename functions
idapro_rename(batch={"func": [
    {"addr": "sub_401000", "name": "decrypt_payload"},
    {"addr": "sub_402000", "name": "verify_license"}
]})

# rename global variables
idapro_rename(batch={"global": [
    {"addr": "0x405000", "name": "g_encryption_key"}
]})

# rename local variables
idapro_rename(batch={"local": [
    {"func": "decrypt_payload", "old": "v1", "name": "plaintext_buf"}
]})
```

### Patch Assembly

```
# NOP out detection code
idapro_patch_asm(items=[{"addr": "0x401050", "asm": "nop"}])

# modify a jump
idapro_patch_asm(items=[{"addr": "0x401060", "asm": "jmp 0x401080"}])

# force return true
idapro_patch_asm(items=[
    {"addr": "0x401000", "asm": "mov eax, 1"},
    {"addr": "0x401005", "asm": "ret"}
])
```

### Patch Bytes

```
# write bytes directly
idapro_patch(patches=[{"addr": "0x401050", "bytes": "9090909090"}])
```

---

## Type System

### Declare Structs

```
idapro_declare_type(decls=[{
    "name": "PacketHeader",
    "decl": "struct PacketHeader { uint32_t magic; uint16_t type; uint16_t length; uint8_t data[0]; };"
}])
```

### Apply Types

```
# set a prototype for a function
idapro_set_type(edits=[{
    "addr": "sub_401000",
    "type": "int __fastcall decrypt(void *buf, int size, const char *key)"
}])

# set a type for a global variable
idapro_set_type(edits=[{
    "addr": "0x405000",
    "type": "PacketHeader"
}])
```

### Infer Types

```
idapro_infer_types(addrs=["sub_401000", "sub_402000"])
```

### Query/Inspect Types

```
idapro_type_query(queries=["Packet"])
idapro_type_inspect(queries=["PacketHeader"])
```

---

## Stack Frame Analysis

```
# view a function's stack frame
idapro_stack_frame(addrs=["main", "sub_401000"])

# declare stack variables
idapro_declare_stack(items=[{
    "func": "sub_401000",
    "offset": -0x20,
    "name": "local_buf",
    "type": "char [32]"
}])
```

---

## Signature Generation

```
# generate a unique byte signature for an address
idapro_make_signature(addrs=["0x401000"])

# generate a signature for a whole function
idapro_make_signature_for_function(addrs=["decrypt_payload"])

# generate signatures for code referencing an address
idapro_find_xref_signatures(addrs=["0x405000"])
```

---

## Base Conversion

```
# hex → decimal
idapro_int_convert(inputs=["0x401000"])

# decimal → hex
idapro_int_convert(inputs=["4198400"])

# batch conversion
idapro_int_convert(inputs=["0xDEAD", "0xBEEF", "12345"])
```

> ⚠️ **Always use this tool for base conversion, never compute it yourself!**

---

## Export and Scripting

### Export Functions

```
# JSON format
idapro_export_funcs(addrs=["main", "sub_401000"], format="json")

# C header file
idapro_export_funcs(addrs=["main", "sub_401000"], format="c_header")

# function prototypes
idapro_export_funcs(addrs=["main", "sub_401000"], format="prototypes")
```

### Execute Python Scripts

```
# execute Python in the IDA context
idapro_py_eval(code="import idautils; print(list(idautils.Functions())[:10])")

# get segment info
idapro_py_eval(code="import idc; print(idc.get_segm_name(0x401000))")

# batch operations
idapro_py_eval(code="import ida_funcs; f=ida_funcs.get_func(0x401000); print(f.size())")
```

---

## Typical Analysis Flows

### Malware Analysis

```text
1. survey_binary → look at imports (network APIs? crypto? registry?)
2. find_regex("http|socket|connect") → find network-related strings
3. xrefs_to(network string address) → find the referencing function
4. decompile(referencing function) → examine the communication logic
5. trace_data_flow(crypto parameter, "backward") → trace the key source
6. set_comments + rename → annotate findings
```

### License Validation Cracking

```text
1. find_regex("serial|license|register|valid") → find validation-related strings
2. xrefs_to(validation string) → locate the validation function
3. analyze_function(validation function) → understand the logic
4. callgraph(validation function, 2) → see the call chain
5. patch_asm(conditional jump address, "jmp always_pass") → patch
```

### CTF Reversing

```text
1. survey_binary → confirm architecture and entry point
2. decompile("main") → see the main logic
3. find_regex("flag|correct|wrong") → find check points
4. trace_data_flow(check point, "backward") → trace input transformations
5. use Python to assist computation/decryption → get the flag
```

### Vulnerability Analysis

```text
1. entity_query(kind="imports", filter="strcpy|sprintf|gets") → find dangerous functions
2. xrefs_to(dangerous function) → find call sites
3. analyze_function(containing function) → see the context
4. stack_frame(function) → confirm the buffer size
5. trace_data_flow(dangerous parameter, "backward") → confirm user controllability
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|------|------|------|
| "No database bound" | no file open | run `open.ps1` |
| "Failed to open database" | old database locked | `open.ps1` auto-falls back to Temp |
| schema validation failure | MCP client BUG | use `open.ps1` instead of `idalib_open` |
| tool timeout | large file still analyzing | add `-TimeoutSeconds 600` |
| "ERR:timeout" (start.ps1) | server startup failure | check Python/idalib-mcp installation |
| base conversion error | manual computation mistake | use `idapro_int_convert` |
| function name not found | name not exact | use `list_funcs` + filter to search first |
