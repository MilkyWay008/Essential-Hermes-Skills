# .NET Obfuscator Deobfuscation Guide

Identification, unpacking, and anti-tamper bypass for mainstream .NET obfuscators. Core tools: **de4dot** (auto-identifies most packers) + **dnSpyEx** (manual patching) + **dnlib** (scripting).

## Master Decision Table

| Obfuscator | de4dot type | Typical characteristics | Auto-unpack | Manual points |
|--------|-------------|---------|---------|---------|
| ConfuserEx 1.x/2.x | `cfze` | anti-tamper, control-flow mutation, string encryption, anti-debug | ✅ mostly automatic | newer versions need anti-tamper patched first |
| ConfuserEx 3.x / custom | `cfze` | same + custom protectors | ⚠️ partial | runtime dump / dnlib |
| SmartAssembly | `sa` | string encoding, resource compression, method-call hiding | ✅ automatic | resource extraction |
| Babel.NET | `babel` | method body encryption, control flow, strings | ✅ automatic | — |
| Eazfuscator.NET | `eaz` | string/resource encryption, expression obfuscation | ⚠️ partial | string decryptor |
| .NET Reactor | `reactor` | necrobit (code section encryption) + anti-tamper | ⚠️ newer versions hard | dump + rebuild metadata |
| Themida .NET | — | packer + virtualization | ❌ de4dot can't | memory dump, native approach |
| Agile.NET / CliSecure | `agile` | method body encryption | ✅ automatic | — |

## Standard de4dot Usage

```powershell
# auto-detect (enough in most cases)
de4dot target.exe -o target-clean.exe

# explicit type (when auto-detect fails)
de4dot --type cfze target.exe -o target-clean.exe

# probe the packer type first
de4dot --detect target.exe

# batch
de4dot *.exe

# strings only, don't touch control flow (minimal intervention)
de4dot --strtyp delegate --strtok METHOD_TOKEN target.exe
```

de4dot's `--strtyp` / `strtok` mode: only resolve string decryptors (specify the decryption method token), keeping the original control flow. Best for "want to see plaintext strings without touching anti-tamper" scenarios.

---

## ConfuserEx (most common)

### Identification

- The entry module `<module>` class carries an anti-tamper check with `[MethodImpl(NoInlining)]`
- Lots of `Dictionary<string, T>` string-decryptor calls
- Control flow flattening (switch dispatch + state variables)
- `.cmp` compressed resources embedded
- dnSpyEx C# view: garbled class/method names (`\uXXXX` or meaningless characters), method bodies full of `int num = ...; switch(num)`

### Unpacking Workflow

```powershell
# 1. standard unpacking
de4dot target.exe -o target-clean.exe

# 2. if de4dot reports "unknown" or the result won't open → newer/custom ConfuserEx
#    confirm anti-tamper first:
dnSpyEx open → find the integrity check in Module .cctor or Main
```

### anti-tamper Bypass (common in newer ConfuserEx)

ConfuserEx's `anti tamper` validates method body hashes at runtime; modification crashes it. de4dot usually handles old versions; newer ones need manual work:

```text
Method A — patch the check function directly in dnSpyEx:
  1. find the anti-tamper check method (usually called from the <module> static constructor)
  2. IL edit: change the check method body to ret (return immediately)
  3. save → then feed to de4dot

Method B — runtime dump:
  1. run it and dump the in-memory assembly with MegaDumper / ExtremeDumper
  2. the dump is already decrypted; clean up residuals with de4dot
```

### After Control Flow Restoration

de4dot restores the flattened switch dispatch into normal if/while. If restoration is incomplete (residual state machine visible), run de4dot again or trace the IL manually.

---

## SmartAssembly

```powershell
de4dot --type sa target.exe -o target-clean.exe
```

Characteristics:
- Strings encoded with the `SmartAssembly.Runtime.Strong` family
- Resource compression (`{assembly}.Resources`)
- Method-call hiding (`ProcessCaller` / indirect calls)

de4dot has the best compatibility with SmartAssembly; basically one-click.

---

## .NET Reactor (necrobit)

`.NET Reactor`'s **necrobit** stores real method bodies encrypted in resources, decrypting and injecting at runtime; the original method bodies are shells. de4dot works on old versions; newer ones (4.x+) often fail.

```text
When de4dot fails:
1. run the program (dotnet target.exe or just double-click)
2. dump process memory with MegaDumper / ExtremeDumper → export the decrypted assembly
3. clean residual obfuscation from the dump with de4dot
4. if metadata is corrupted, rebuild with dnlib (see common-workflow.md)
```

---

## Manual String Decryptor Extraction

Obfuscators encrypt strings and call a decryption method at runtime. de4dot auto-detects most decryptors; when it fails, do it manually:

```text
1. Find the decryption method in dnSpyEx (signature is usually fixed: static string Decrypt(int) or Decrypt(string, int))
   - characteristics: called heavily, params are numeric constants, returns string
2. Note the method token (e.g. 0x06000012)
3. Tell de4dot the decryptor:
   de4dot --strtyp delegate --strtok 0x06000012 target.exe -o target-clean.exe
```

If the decryption method itself is obfuscated (control flow flattened), deobfuscate the control flow first, then locate the decryptor.

## Common anti-debug Techniques

| Technique | Location | Bypass |
|------|------|------|
| `Debugger.IsAttached` check | any method | IL change to `ldc.i4.0; ret` or patch the getter |
| `Debugger.IsLogging` | — | same as above |
| Timing check (`DateTime.Now` delta) | method entry | patch out the delta comparison |
| `CheckRemoteDebuggerPresent` P/Invoke | — | nop the call |
| Exception-driven control flow (try/catch path selection) | main logic | can't simply nop; analyze the real path of the catch block |

> .NET anti-debug is simpler than native — most are managed API calls; a one-line IL change in dnSpyEx suffices.

## Fallbacks When de4dot Fails

1. **de4dot --detect** — check the identification result against the table above
2. **Runtime dump** (MegaDumper / ExtremeDumper / Process Hacker module export)
3. **dnlib script** — manual resolution (see the dnlib section of common-workflow.md)
4. **Dynamic-first**: run it and break at the decryption point to read plaintext directly — intel without unpacking

Community references: Washi's blog "misconceptions-about-dotnet" (common IL analysis misconceptions), Kanxue .NET reversing forum, Guided Hacking "Top 5 .NET RE Tools".

