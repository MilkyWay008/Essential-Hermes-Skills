# Red Team Sharp* Tool Analysis & Tool Install Matrix & dnSpy MCP

## Red Team Sharp* Tool Analysis

Red team tools are heavily written in C# (the Sharp* family); reversing them is a common scenario: understand detection logic, change signatures, extract embedded configs.

### Common Sharp* Tools Quick Reference

| Tool | Function | Reversing focus |
|------|------|-----------|
| **Rubeus** | Kerberos attacks (AS-REP roast / Kerberoast / S4U / pass-the-ticket) | Rubeus engineering structure is fixed; find the `Interop.*` P/Invoke section for native calls |
| **SharpHound** | BloodHound data collector | LDAP query logic, the attribute set being collected |
| **SharpShell / SharpWS** | remote execution, lateral movement | WMI / WinRM calls, command obfuscation |
| **Seatbelt** | information gathering | collection item list, judgment logic |
| **SharpRoast** | Kerberoasting | ticket request/parsing |
| **Inveigh / SharpSploit** | man-in-the-middle / general exploitation framework | reflective loading, API call chains |

### General Analysis Pattern

```text
1. Open in dnSpyEx (usually unobfuscated; a few teams add ConfuserEx)
2. Look at Program.Main or the entry command dispatcher (Rubeus is a switch(command) structure)
3. Find the implementation class/method of the target command
4. Look at the P/Invoke section (Interop.* namespace) — native API calls live here
5. Extract embedded resources (some tools embed config/templates)
6. To change signatures (EDR evasion): change command strings, API calls, string constants
```

### Rubeus Structure Example

Rubeus uses command dispatch; each subcommand is a class. To find Kerberoasting logic:

```text
Entry: Rubeus.CommandLineParser → parses args
Dispatch: switch(command) → "kerberoast" → executes Ask.TGS(...)
P/Invoke: Rubeus.Interop.Lsa* / Native.cs → native Kerberos API
Key: LsaCallAuthenticationPackage (KERB_RETRIEVE_TKT_REQUEST)
```

Changing signatures (evasion): rename the command string `"kerberoast"` to a custom name, change the `Rubeus` banner string, change P/Invoke call order.

### Embedded Config Extraction

Many loaders/tools embed C2, keys, certificates encrypted in resources or fields:

```powershell
# look at Resources in dnSpyEx (resource tree)
# or via command line
powershell -c "[System.Reflection.Assembly]::LoadFile('target.exe').GetManifestResourceNames()"
# after locating the resource, right-click in dnSpyEx → extract / Save
```

Runtime-decrypted config → dynamically break at the decryption method's return point and dump plaintext (see `common-workflow.md`).

---

## Tool Install Matrix

### Windows (preferred; dnSpyEx is a GUI)

```powershell
# Option A: Chocolatey
choco install dnspy ilspy de4dot detect-it-easy

# Option B: manual release download (recommended; version control)
# dnSpyEx:    https://github.com/dnSpyEx/dnSpy/releases
# de4dot:     https://github.com/de4dot/de4dot/releases
# ILSpy:      https://github.com/icsharpcode/ILSpy/releases
# DIE:        https://github.com/horsicq/Detect-It-Easy/releases
# dnlib:      dotnet add package dnlib  (NuGet)
```

### Linux / macOS (no dnSpyEx GUI; use CLI)

```bash
# ILSpy CLI decompilation
dotnet tool install -g ilspycmd
ilspycmd target.exe -p -o outdir/         # decompile to a directory

# de4dot cross-platform (needs mono or dotnet)
# download the de4dot .dll from releases and run with dotnet
dotnet de4dot.dll target.exe -o target-clean.exe

# dnlib (scripting; needs dotnet SDK)
dotnet new console -o dnclean && cd dnclean
dotnet add package dnlib

# DIE CLI (diec)
# Linux: install from https://github.com/horsicq/Detect-It-Easy
diec target.exe
```

### .NET Runtime Prerequisite

```bash
# Linux
sudo apt install dotnet-runtime-8.0        # or 6.0/7.0 depending on the target
# macOS
brew install --cask dotnet-sdk
```

> dnSpyEx (with IL editor + debugger) is Windows-GUI only. On Linux/macOS, .NET reversing is limited to `ilspycmd` decompilation + `dnlib` script patching — no equivalent interactive debugging GUI. Prefer Windows when patching is needed.

---

## dnSpy MCP Integration

The community has several dnSpy MCP projects exposing dnSpy's decompilation/IL inspection as MCP tools, callable directly by AI — fully aligned with reverse-skill's MCP philosophy.

### Mainstream dnSpy MCP Projects

| Project | Features | Fit |
|------|------|------|
| **soufianetahiri/dnspy-mcp** | core MCP Server exposing decompile, IL inspection and other tools | various agent clients |
| **AgentSmithers/DnSpy-MCPserver-Extension** | runs as a dnSpyEx extension, deep GUI integration | loaded inside dnSpyEx |
| **malwarecakefactory/dnspy-mcp-extension** | 33 tools covering triage → deobfuscation end-to-end | full-flow automation |

### Registering in the Agent's MCP Config

After installing the dnSpyEx extension per the corresponding project's README, register it in the agent's MCP config file (e.g. `<agent MCP config>`); the exact command/args and config location follow the project README and the client in use:

```json
{
  "mcpServers": {
    "dnspy": {
      "command": "dotnet",
      "args": ["path/to/dnspy-mcp.dll"]
    }
  }
}
```

After registration, this skill's AI integration path: user says "analyze this .NET" → route to `dotnet-reverse/` → prefer calling the `dnspy_decompile` / `dnspy_inspect_il` tool surface → fall back to GUI if that fails.

> dnSpy MCP is not a built-in bootstrap capability of reverse-skill; the user must manually install the extension per the project README and register it. It can be considered for `bootstrap-manifest.json` later.

---

## Community Resource Index

### Strongly Recommended

- **Washi's blog** — .NET reversing authority: https://blog.washi.dev/posts/misconceptions-about-dotnet/
  - Core view: **don't over-rely on dnSpy's C# decompiler; get familiar with the IL editor** (aligned with this project's IL-first principle)
- **dnSpyEx** — actively maintained dnSpy fork: https://github.com/dnSpyEx/dnSpy
- **de4dot** — .NET deobfuscation: https://github.com/de4dot/de4dot
- **dnlib** — metadata programming: https://github.com/dnlib/dnlib

### Practical Tutorials

- Medium "De-obfuscating and reversing a .NET/C# spyware" — dnSpy + de4dot info-stealer deobfuscation hands-on
- YouTube "dnSpy Patch .NET EXEs & DLLs" — step-by-step patching + keygen
- Kanxue forum .NET reversing section — search ".net reverse" / "dnSpy" / "ConfuserEx" for many field posts, Nuitka reversing, evasion discussions
- Guided Hacking "Top 5 .NET Reverse Engineering Tools" — dnSpy still #1
- StackExchange / Reverse Engineering — advanced topics like `DynamicMethod` debugging

### Existing .NET Resources in This Repo (cross-links)

- `reverse-engineering/tools.md` `.NET Analysis` section — dnSpy/ILSpy tool cheatsheet + Codegate 2013 two-stage XOR+AES-CBC pattern
- `reverse-engineering/field-notes.md` `.NET` section — tool notes
- `reverse-engineering/awesome-re-resources.md` — de4dot listed
- `field-journal/seed-014_unity-il2cpp-reverse.md` — Unity IL2CPP (native side, complements the .NET managed layer)

Deep .NET reversing content converges into this module; keep a quick-reference index in `reverse-engineering/`.

