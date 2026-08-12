# .NET Reverse Engineering General Workflow

Full workflow details, IL patch reliability, string decryptor extraction, state machine identification, dnlib scripting.

## Full Workflow (end-to-end)

```text
1. Identify  → confirm it's a .NET managed program (not native)
2. Detect    → DIE / de4dot --detect to identify the obfuscator
3. Deobf     → de4dot deobfuscation (keep the original sample)
4. Static    → dnSpyEx browse the C# view to orient, IL view for key logic
5. Dynamic   → dnSpyEx debugger, breakpoints at key methods, see runtime plaintext
6. Patch     → IL editor modifications, Save Module
```

Persist artifacts at every step: original sample `target.exe` → unpacked `target-clean.exe` → patched `target-patched.exe`.

## IL Patch vs C# Patch Reliability

**Core conclusion: use the IL editor for critical modifications, not the C# editor.**

| Dimension | C# editor (Edit Method C#) | IL editor (Edit IL) |
|------|---------------------------|---------------------|
| Compile failure risk | High (missing references, syntax, lambda rewrite failures) | Near zero |
| Information fidelity | Compiler regenerates IL, may differ from original IL | Replace in place, instruction-by-instruction |
| Best for | Changing a string, a constant, simple logic | Changing branches, deleting checks, changing control flow |
| async/await/state machines | Often fails to compile or distorts | Directly modify state machine fields, reliable |

dnSpyEx's C# decompiler is based on read-only decompilation + attempted recompilation; recompiling compiler-generated code (state machines, closures, `yield`) fails easily. The IL editor edits instruction by instruction — WYSIWYG.

### Typical IL Patch Patterns

```text
Change a branch (if (check) → always true):
  original: call bool Foo::Check()
      brfalse.s SKIP
  change: ldc.i4.1            ; push true
      brfalse.s SKIP      ; never jumps now, SKIP not executed
  or more directly:
      ldc.i4.1
      ret                 ; method returns true directly

Change a branch (if (check) → always false):
  ldc.i4.0
  ret

Delete an entire check:
  nop everything, or change to ret + correct return value

Change a string constant:
  The C# editor usually handles strings OK (ldstr swaps the token directly), but if the string lives in resources/encryption you must change the decryption logic

Change a numeric constant:
  Edit the operand of the ldarg / ldc instruction directly
```

## State Machine Identification (async/await / yield)

C# `async/await` and `IEnumerator` yield compile into **state machines**: the compiler generates a nested class whose `MoveNext()` uses a `state` field for switch dispatch. dnSpyEx's C# view restores async, but the decompilation may distort; the IL view of `MoveNext` is most accurate.

```text
async/await MoveNext structure:
  switch(this.<>1__state) {
    case 0: ... logic before await; this.<>1__state = 1; await MoveNext;
    case 1: ... logic after await;
  }

To patch async logic: modify the state transition in MoveNext or the branch in the specific case.
Editing async in the C# editor almost always fails → must use IL.
```

## String Decryptor Extraction

See `obfuscators.md` for details. This supplements with dnlib-scripted batch string decryption:

```csharp
// dnlib script: scan all string decryptor calls, restore at runtime and write back
// usage: dotnet script decrypt.csproj target.exe 0x06000012
using System;
using System.Reflection;
using dnlib.DotNet;
using dnlib.DotNet.Writer;
using dnlib.DotNet.Emit;

var module = ModuleDefMD.Load(args[0]);
var decryptorToken = uint.Parse(args[1], System.Globalization.NumberStyles.HexNumber);

// find the decryption method, invoke it via reflection (requires loading the assembly into the AppDomain)
// iterate all methods, replace call Decryptor(token) with ldstr "decrypted result"
foreach (var type in module.GetTypes())
    foreach (var method in type.Methods)
    {
        if (!method.HasBody) continue;
        var instrs = method.Body.Instructions;
        for (int i = 0; i < instrs.Count; i++)
        {
            // recognize the call-decryptor pattern, invoke the decryptor for plaintext, replace with ldstr
            // (reflection-call boilerplate omitted: load the original assembly →
            //   MethodInfo.Invoke for plaintext → instrs[i] = OpCodes.Ldstr + operand=plaintext)
        }
    }

var opts = new ModuleWriterOptions(module);
module.Write("target-decrypted.exe", opts);
```

dnlib is the de facto standard for .NET metadata programming; de4dot uses it internally. First choice when writing custom deobfuscation scripts.

## Dynamic Debugging Points

The dnSpyEx debugger is far friendlier to .NET programs than native:

- **Breakpoint at method entry**: right-click method → Add Breakpoint
- **View object values**: when paused, the Locals / Watch windows show object fields and string content directly
- **Memory writes**: you can change runtime variable values directly (Edit Value)
- **Exception breakpoints**: Debug → Exceptions, check the exception types to break on — obfuscators often use exception-driven control flow; breaking on exceptions reveals the real path

### Exception-Driven Control Flow

Some obfuscators stuff normal logic into `try` and use `throw` + `catch` for jumps. Static IL looks like exception handling but is actually control flow:

```text
try { throw new CustomException(0x42); }
catch (CustomException e) {
    switch(e.Code) {
        case 0x42: real logic A; break;
        case 0x43: real logic B; break;
    }
}
```

Set an exception breakpoint (break on `CustomException`) and trace the `Code` value flow — faster than grinding through IL.

## Module Initializer (Module .cctor)

A `.NET` module's static constructor (the `<module>` `.cctor`) runs first when the assembly loads; obfuscators often put anti-tamper / decryption initialization here. Analysis order:

```text
1. Look at <module>.cctor (Module .cctor) first — decryption/anti-debug initialization
2. Then Program.Main / Startup
3. anti-tamper in .cctor → patch .cctor first, then unpack
```

## General Pattern for Extracting Config / C2 / Keys

Red team tools and loaders often embed encrypted config in resources or fields, decrypted at runtime:

```text
Locating workflow:
1. strings for plaintext URL/IP (usually absent after obfuscation)
2. find byte[] fields + a decryption method (AES/XOR)
3. dynamically break at the decryption method's return point, dump the decrypted plaintext
4. common: AES-256-CBC with Key==IV (Codegate 2013 pattern; see reverse-engineering/tools.md .NET section)
```

See `references/sharp-tools.md` for concrete config structures of red team tools.

## Boundary With reverse-engineering

- **IL2CPP / NativeAOT** → compiled native, no CLR metadata → go through `reverse-engineering/` (IDA/r2); this skill only identifies them
- **Managed .NET** (standard C# exe/dll, Mono/Unity managed layer, Xamarin) → this skill
- **Hybrid (native loader + .NET payload)** → loader part goes through `reverse-engineering/`; switch to this skill after dumping the .NET payload

## Artifact Checklist

Each .NET reversing task should produce:
- `target-original.exe` (original sample, untouched)
- `target-clean.exe` (after de4dot unpacking)
- `notes.md` (identified obfuscator, decryptor token, key method addresses, config/C2/key)
- `target-patched.exe` (after patching, if needed)
- `il-diff.txt` (IL before/after comparison, if patching)
