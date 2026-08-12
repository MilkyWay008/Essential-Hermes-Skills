# Optional Sandbox Tool Profile (vs bootstrap-manifest)

> The Z3r0 default image ships a full toolset; reverse-skill **does not bundle an image** — this table is a coverage comparison and optional Docker suggestion.

## Capabilities reverse-skill can auto-bootstrap

Source: `skills/scripts/bootstrap-manifest.json` (the file wins):

| Capability | Typical use |
|------|----------|
| jadx / apktool / adb / frida / frida-ps | Android |
| r2 / rabin2 | binary CLI |
| idalib-mcp / idapro | IDA MCP |
| jeb-pro | commercial Android/ARM decompiler (manual license install) |
| jshookmcp / reqable-mcp / anything-analyzer / agent-browser | web/JS/packet-capture/browser |
| ghidra-mcp | Ghidra |
| nmap / seclists / proxycat / burpsuite-mcp / pentestswarm | pentest |
| binwalk / pwntools / yara | firmware/pwn/malware |

```powershell
powershell -File skills\scripts\bootstrap-reverse.ps1 -Capability @('jadx','nmap','yara') -StartServices
powershell -File skills\scripts\refresh-tool-index.ps1
```

## Common in the Z3r0 sandbox but NOT auto-installed by this manifest

| Tool | reverse-skill policy |
|------|-------------------|
| subfinder / amass / httpx / ffuf / nuclei / sqlmap | documented install / Kali script / external MCP; **never claim bootstrap already has them** |
| full Ghidra GUI | ghidra-mcp capability + manual plugin steps |
| gdb / pwndbg | manual per platform docs; pwntools can bootstrap |
| hydra / hashcat | manual or Kali |
| JEB Pro | manual install once the user holds a license; third-party MCP bridges must pass supply-chain review first |
| Reqable desktop client | manual user install; `reqable-mcp` only registers the official pinned-version MCP runtime |
| SecLists | seclists capability |

## Recommended "lightweight Docker ops" profile (optional, not a dependency)

Only when the user **themselves** has Docker and an authorized lab:

```text
Minimal: nmap + nuclei + sqlmap containers or a pentestMCP-style image
Mobile: jadx + apktool + frida on the host
Reversing: IDA/r2 on the host + tool-index
```

**MUST NOT** require the user to install Z3r0 in order to use reverse-skill.

## network_profile Integration

Scanning inside the sandbox still obeys the `network_profile` in the case `scope.md`:

- `offline` → do not launch outward-scanning containers  
- `authorized_target_only` → containers may only hit in_scope targets  
