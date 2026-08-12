# OLLVM Deobfuscation / Obfuscator-LLVM Deobfuscation

> OLLVM deobfuscation workflow for APK .so files, ELF binaries, and control-flow-flattening scenarios.
> Tool and variant information based on research into active 2026 community projects, not training memory.
> Applies to: Android NDK hardening, CTF reversing, packed .so analysis, commercial obfuscator countermeasures.

---

## 0. Quick Decision: Which Tool Should I Use?

Match your environment and judgment of the target obfuscation type directly:

| Your situation | First choice | Alternative | Notes |
|---------|---------|------|------|
| Have IDA Pro 7.5-7.7 + Hex-Rays, want one-click deflattening | **obpo-plugin** | d810-ng | obpo uses microcode + data flow + concolic execution; strongest results, but it's a cloud plugin (needs network, core is closed-source) |
| Have IDA Pro (any reasonably recent version), want a local all-in-one deobfuscator | **d810-ng** | D-810 original | Local, open source, integrated Z3, supports many OLLVM/Tigress/Hodur/Approov variants |
| Have Binary Ninja | **ollvm-breaker** | — | Built for real Android .so samples (libvdog and other hardened samples) |
| No IDA/BN, pure script, x86/x64 target | **ollvm-unflattener** (Miasm) | angr deflat | Miasm-based symbolic execution, BFS multi-layer handling |
| No IDA/BN, pure script, x86/x64 target | **ollvm-unflattener** (Miasm) | angr deflat | Miasm-based symbolic execution, BFS multi-layer handling |
| Pure Python symbolic execution, CTF scenarios | **angr** Deobfuscator | Triton | No GUI dependency, scriptable |
| ARM64 .so target, no IDA | **deollvm** (Unicorn) | angr | Unicorn-based ARM64 deflat |
| BR obfuscation (indirect branches) | **DeObfBR** | set data section read-only | Goron/Arkari-style BR obfuscation can be countered simply with a read-only data section |
| Tigress obfuscation | d810-ng `UnflattenerSwitchCase`/`UnflattenerTigressIndirect` | — | d810-ng has built-in Tigress-specific unflatteners |

> **Core recommendation:** prefer **d810-ng** (local, actively maintained, broad variant coverage). When the cloud service is available, **obpo-plugin** gives the best results. If both fail, escalate to **angr/Miasm** symbolic execution for custom handling.

---

## 1. The Modern OLLVM Variant Ecosystem (2026 community research)

OLLVM is no longer just the original 2017 repo. The following obfuscator forks are currently active; **you must determine which variant the target is before deobfuscating**, because countermeasures differ significantly between variants:

### 1.1 Obfuscator Fork Lineage

| Variant | Base LLVM | New features vs original OLLVM | Countermeasure focus |
|------|----------|----------------------|---------|
| **Obfuscator** (original) | 3.3~4.0 | sub + bcf + fla (the three base passes) | All standard tools handle it |
| **Hikari** | 6~8 | Anti Class Dump, Function Call Obfuscate, Function Wrapper, Indirect Branching, Split BB, String Encryption | Decrypt strings first + fix indirect jumps |
| **Hikari-LLVM15** | 15~19 | + Anti Debugging, Anti Hook, Constant Encryption | Closed source; Constant Encryption increases static analysis difficulty |
| **goron** | 7~10 | Indirect Branch/Call/GlobalVariable | ⚠️ Goron-style indirect obfuscation can be countered simply by making the data section read-only |
| **Arkari** (komimoe/Hikari) | 14~latest | Based on goron, continuously maintained | Same as goron; read-only data section partially counters it |
| **Pluto** | 14 | MBA Obfuscation, Random CF, Split BB, **Trap Angr** (specifically breaks angr) | ⚠️ The Trap Angr pass makes angr symbolic execution fail; switch tools or dodge the trap |
| **Polaris** (formerly Pluto) | 16 | Alias Access, Indirect Branch/Call, String Encryption, Merge Function, Linear MBA, Dirty Bytes Insertion, Function Splitting, Junk Insertion | Combines Hikari+Pluto; the trickiest, needs layered handling |
| **O-MVLL** | open-obfuscator | Python-driven pass manager; Anti Hooking, Arithmetic(MBA), BB Duplicate, CF Breaking, Function Outline, Indirect Branch/Call, Opaque Constants | Common in modern Android hardening; Python config is easy to customize |
| **amice** (Rust) | Rust implementation | Full suite + VM Flatten, Instruction Virtualization, Delayed Offset Loading, Parameter Aggregation | Includes VM-ization; needs VM handler recovery, not plain deflat |
| **VMP family** (SmallVmp/VMPilot/xVMP/VMPacker) | — | Instruction virtualization | **Not OLLVM territory**; needs VM reversing — see VM-specific tools |

### 1.2 Key Identification Clues

- **Trap Angr** (Pluto/Polaris): if angr explodes or path-explodes mid-run, suspect the Trap Angr pass → switch to d810-ng or Unicorn dynamic methods
- **Goron/Arkari indirect jumps**: if the dispatcher uses indirect jumps (BR x8 instead of switch), first try making the relevant data section read-only; indirect jump targets often become statically solvable
- **Constant Encryption** (Hikari-LLVM15/Polaris/O-MVLL): constants are decrypted at runtime; pure static analysis can't see real values → use Unicorn to dynamically execute the decryption stub
- **VM Flatten** (amice): control flow becomes a VM dispatch loop; **don't treat it as ordinary fla** — first identify the VM handler table

---

## 2. OLLVM Obfuscation Type Detection

Recognition characteristics of OLLVM's three core passes:

### 2.1 Control Flow Flattening (`fla`)

**IDA view characteristics:**
- The function entry first jumps to a single dispatcher block
- The main logic is split into many basic blocks, each ending by jumping back to the dispatcher
- The dispatcher decides the next block to execute via a **state variable**
- A huge `switch` structure whose cases have no logical relation to each other

```
Original:             OLLVM flattened:
  block_A               entry -> dispatcher
  block_B                 ↓
  block_C              state_machine:
                         switch(state):
                           0 → block_A
                           1 → block_B
                           2 → block_C
```

**Variant forms (dispatchers recognized by d810-ng):**
- O-LLVM: switch / if-chain + state variable
- Tigress: `m_jtbl` (switch-case) or `m_ijmp` (indirect jump, needs `goto_table_info` config)
- Hodur (PlugX): nested `while(1)` state machine, `jnz state, #CONST`, **no switch dispatcher**
- Approov: `while(v8 != C)`, state constants concentrated in `0xF6000–0xF6FFF`

### 2.2 Bogus Control Flow (`bcf`)

- **Unreachable fake branches** inserted between real branches
- Fake branches are protected by **opaque predicates** (always-true/always-false conditions that static analysis can't directly prove)
- Lots of dead code inflates function size

```c
// classic opaque predicate: x(x+1) is always even, but the compiler can't prove it
if (x * (x + 1) % 2 == 0) {
    // real logic
} else {
    // unreachable junk code
}
```

### 2.3 Instruction Substitution (`sub`) → MBA

- Simple arithmetic/bitwise ops replaced with equivalent complex expressions (MBA, Mixed Boolean-Arithmetic)

```
a + b  →  (a ^ b) + 2*(a & b)
a ^ b  →  (a | b) - (a & b)
a - b  →  a + (~b) + 1
```

### 2.4 Quick Classification Table

| Obfuscation type | IDA characteristics | Main countermeasure |
|---------|---------|------------|
| fla (flattening) | huge switch + dispatcher | obpo / d810-ng / deflat |
| bcf (bogus control flow) | unreachable branches + dead code | d810-ng opaque predicate removal / symbolic execution |
| sub/MBA | complex arithmetic expressions | d810-ng MBA simplifier / SiMBA (Z3) |
| fla + bcf + sub | everything, massively inflated | **layered deobfuscation (bcf first, then fla, then sub)** |

---

## 3. Mainstream Tools in Detail (active community projects)

### 3.1 obpo-plugin — strongest results, cloud plugin

> [obpo-project/obpo-plugin](https://github.com/obpo-project/obpo-plugin) · 629⭐ · active 2026-06

Hex-Rays **microcode**-based pseudocode optimizer using **data-flow tracking + program slicing + concolic execution** to rebuild flattened control flow. Community-recognized as one of the strongest.

**Key features:**
- Operates at the microcode layer, directly optimizing decompiler output (not modifying ASM)
- Supports IDA 7.5.0 / 7.6.0 / 7.7.0 + Hex-Rays
- Architectures: ARM, ARM64, x86, x86_64, PowerPC, PowerPC64, MIPS (7.6/7.5)
- **Cloud plugin**: target function binaries are uploaded to an obpo-server for processing (core closed-source, plugin free/open)
- Server maintained at the author's own cost; 600s timeout; **no multithreading/malicious calls**

**Installation and usage:**
```text
1. Download obpo_plugin.py and the obpoplugin directory
2. Copy to the IDA plugins path
3. Restart IDA, open the target binary
4. Locate the dispatcher block in the CFG, usually looks like:
   [screenshot reference: repo assets/dispatchblock.png]
5. Right-click → OBPO → Mark and process function
6. Refresh the decompiler after processing
7. You can keep marking new dispatcher blocks as the decompilation changes (iterative handling of nested fla)
```

**Best-fit scenarios and limitations:**
- ✅ Standard and nested fla work well
- ⚠️ Needs network; use caution with sensitive samples (unpublished internal vulnerabilities, trade secrets) — the binary gets uploaded
- ⚠️ The server may be down; depends on the author's maintenance
- ❌ Can't solve all obfuscation (explicitly stated by the author)

### 3.2 d810-ng — first choice for local all-in-one

> [w00tzenheimer/d810-ng](https://github.com/w00tzenheimer/d810-ng) · 223⭐ · updated 2026-06-26

Modern maintained/refactored version of D-810 (Next Generation). Runs locally, open source, integrated **Z3 SMT** solver, broadest variant coverage.

**Core capabilities (organized per d810-ng README):**

*Instruction-level optimizations:*
| Category | Description |
|------|------|
| MBA simplification | `(a+b)-2*(a&b) => a^b`, Z3-verified DSL rules |
| Hacker's Delight | bitwise equivalences (from the Hacker's Delight book) |
| O-LLVM patterns | Obfuscator-LLVM-specific MBA patterns |
| Constant folding | 22 constant simplification rules |
| Predicate simplification | opaque predicate removal (setz/setnz/lnot/smod) |
| Z3 rules | SMT solving when template matching fails |
| Hodur-specific | PlugX (Hodur) malware MBA patterns |

*Control-flow unflatteners (classified by target obfuscation):*
| Unflattener | Target | Description |
|------------|------|------|
| `Unflattener` | O-LLVM | standard switch/if-chain + state variable |
| `UnflattenerSwitchCase` | Tigress | Tigress switch-case dispatch (`m_jtbl`) |
| `UnflattenerTigressIndirect` | Tigress | Tigress indirect jumps (`m_ijmp`), needs `goto_table_info` config |
| `HodurUnflattener` | Hodur (PlugX) | nested `while(1)` + `jnz state, #CONST`, no switch |
| `BadWhileLoop` | Approov | `while(v8 != C)`, state constants in 0xF6000–0xF6FFF |
| `UnflattenerFakeJump` | general | removes always-true/always-false conditional jumps |
| `SingleIterationLoopUnflattener` | residual | cleans single-iteration loops where `INIT == CHECK` and `UPDATE != CHECK` |
| `UnflattenControlFlowRule` (experimental) | general | CFG unflattener based on path emulation |

**Installation and usage:**
```text
1. clone d810-ng
2. install dependencies (including Z3)
3. copy to the IDA plugins directory
4. In IDA press Ctrl-Shift-D to load the plugin
5. Check the rule sets you want to apply in the GUI
6. Apply to the target functions
```

**Why d810-ng over the original D-810:**
- The original D-810 is less maintained
- d810-ng has CI tests, refactored code, and new Tigress/Hodur/Approov-specific unflatteners
- Integrated Z3; falls back to SMT solving when template matching fails — higher success rate

### 3.3 ollvm-unflattener — Miasm symbolic execution, pure script

> [cdong1012/ollvm-unflattener](https://github.com/cdong1012/ollvm-unflattener) · 265⭐ · active 2026-06

Based on the **Miasm** symbolic execution engine; no IDA/BN dependency, pure Python command line.

**Features:**
- Uses Miasm symbolic execution to recover the original control flow (unlike MODeflattener's pure static approach)
- **BFS multi-layer handling**: automatically follows the target function's calls and deobfuscates recursively
- Supports Windows/Linux x86/x64
- Outputs a deobfuscated new binary

**Installation and usage:**
```bash
git clone https://github.com/cdong1012/ollvm-unflattener.git
cd ollvm-unflattener
pip install -r requirements.txt   # miasm, graphviz, keystone-engine

# basic usage
python unflattener -i <input.bin> -o <output.bin> -t <function_addr> -a
# -a: automatically follow calls for multi-layer handling
```

**Best for:** no IDA, x86/x64 targets, batch scripted processing.

### 3.4 ollvm-breaker — Binary Ninja field-tested

> [amimo/ollvm-breaker](https://github.com/amimo/ollvm-breaker) · 441⭐

Uses **Binary Ninja** for deflattening; the repo ships the Android hardened sample `libvdog.so` as a test case, with JNI_OnLoad, crazy::GetPackageName, prevent_attach_one and other functions already fixed.

**Best for:** Binary Ninja users, real Android .so work.

### 3.5 deollvm — ARM64 Unicorn

> [GeT1t/deollvm](https://github.com/GeT1t/deollvm) · 34⭐ · 2026-04

Unicorn-based ARM64 OLLVM deflat. An alternative for handling ARM64 .so files without IDA.

### 3.6 DeObfBR — BR obfuscation specialist

> [Mrack/DeObfBR](https://github.com/Mrack/DeObfBR) · 96⭐ · 2026-06-25

Specifically removes **BR obfuscation** (indirect-branch obfuscation, Goron/Arkari style).

**⚠️ Easy countermeasure (from awesome-ollvm):** Goron/Arkari-style indirect obfuscation can be countered simply by **making the data section read-only** — indirect jump targets often depend on a runtime-writable data section; making it read-only makes them statically solvable.

### 3.7 angr — general symbolic execution framework

```python
import angr

proj = angr.Project("target.so", auto_load_libs=False)
cfg = proj.analyses.CFGFast()
func = proj.kb.functions[0x12345]

# built-in Deobfuscator
deob = proj.analyses.Deobfuscator(func=func)
deob.normalize()
```

**⚠️ Pluto/Polaris Trap Angr pass:** these two variants wrote traps specifically to break angr symbolic execution. If angr path-explodes or errors out, suspect Trap Angr → switch to d810-ng or Unicorn dynamic methods.

---

## 4. Complete Deobfuscation Workflows (by scenario)

### 4.1 General Decision Tree

```
target binary
  ↓
1. Identify the OLLVM variant (see section 1.2 clues)
  ├── original OLLVM / Hikari / O-MVLL  → standard fla/bcf/sub
  ├── Pluto / Polaris                → watch for Trap Angr, avoid angr
  ├── Goron / Arkari                 → try read-only data section first, then handle BR
  ├── Tigress                        → d810-ng Tigress unflattener
  ├── Hodur (PlugX)                  → d810-ng HodurUnflattener
  └── amice (with VM)                → not plain fla; needs VM handler recovery
  ↓
2. Choose the tool (see section 0 decision table)
  ├── have IDA + network + non-sensitive sample → obpo-plugin
  ├── have IDA + local              → d810-ng
  ├── have Binary Ninja            → ollvm-breaker
  ├── no GUI + x86/x64           → ollvm-unflattener (Miasm)
  ├── no GUI + ARM64             → deollvm (Unicorn) / angr
  └── pure symbolic execution / CTF           → angr
  ↓
3. Layered deobfuscation (order matters)
  a) remove opaque predicates first (bcf)   → d810-ng opaque predicate removal
  b) then remove control flow flattening (fla) → unflattener
  c) finally simplify MBA (sub)       → d810-ng MBA simplifier / SiMBA
  ↓
4. Verify
  ├── function size significantly reduced?
  ├── CFG changed from star/radial to chain/tree?
  └── Frida hook of key functions confirms the logic is correct?
```

### 4.2 Android NDK .so Deobfuscation

OLLVM-hardened .so files from the Android NDK are the most common APK reversing scenario.

**Step 1 — extract the .so:**
```bash
adb pull /data/app/~~/lib/arm64/libnative.so
# or unzip directly from the APK: unzip target.apk -d out/ ; find out -name "*.so"
```

**Step 2 — identify OLLVM and the variant:**
```bash
readelf -a libnative.so | grep -E "Size|text"   # abnormally large .text but few functions → likely OLLVM
# open in IDA and look at function characteristics:
#   huge switch → fla
#   unreachable branches → bcf
#   complex arithmetic → sub/MBA
#   indirect jumps BR x8 → Goron/Arkari, try read-only data section
#   while(1) + jnz state → Hodur, use d810-ng HodurUnflattener
```

**Step 3 — deobfuscate (layered):**
```
a) bcf: d810-ng opaque predicate removal  (or obpo handles it automatically)
b) fla: d810-ng Unflattener / obpo-plugin / deollvm(ARM64)
c) sub: d810-ng MBA simplifier
```

**Step 4 — Frida dynamic validation:**
```javascript
// Trace OLLVM state variables to help deflat determine the state variable address
const target = Module.findBaseAddress("libnative.so");
console.log("[+] libnative.so @", target);

// hook at the dispatcher entry and observe the state change sequence
Interceptor.attach(target.add(0x1234), {  // dispatcher offset
    onEnter(args) {
        // read the state variable (register/stack position depends on the decompilation)
        console.log("[state]", this.context.x8);  // assuming state is in x8
    }
});
```

### 4.3 Quick CTF Deobfuscation

CTF is usually time-constrained; take the fastest path:

```python
#!/usr/bin/env python3
"""CTF OLLVM quick deflat with angr"""
import angr

proj = angr.Project("challenge", auto_load_libs=False)
cfg = proj.analyses.CFGFast()

# find the largest functions (most likely obfuscated)
funcs = sorted(cfg.functions.values(), key=lambda f: f.size, reverse=True)[:5]
for func in funcs:
    print(f"[*] {func.name} @ {hex(func.addr)} size={hex(func.size)}")
    try:
        deob = proj.analyses.Deobfuscator(func=func)
        deob.normalize()
        print(f"    [+] deobfuscated")
    except Exception as e:
        print(f"    [-] failed: {e}")
        # angr failed → suspect Trap Angr → switch to d810-ng / Unicorn
```

---

## 5. MBA Expression Simplification

### 5.1 Common OLLVM MBA Patterns

```python
# these identities are the simplification targets for expressions generated by the OLLVM sub pass
"(a | b) + (a & b)"        # → a + b
"(a | b) - (a & b)"        # → a ^ b
"(a ^ b) + 2*(a & b)"      # → a + b
"(a | b) & ~(a & b)"       # → a ^ b
"~(~a & ~b)"               # → a | b (De Morgan)
```

### 5.2 Tool Selection

| Tool | Method | Best for |
|------|------|------|
| **d810-ng MBA simplifier** | in-IDA batch, Z3-verified | first choice, integrated into the decompile flow |
| **SiMBA** (`pip install simba-simplifier`) | CLI/library | pure expression simplification, batch processing |
| **Arybo** | symbolic bit-vectors | large numbers of MBA expressions |
| **Z3 direct solving** | SMT | most general; when template matching all fails |

```python
# SiMBA example
from simba import simplify_mba
exprs = ["(a | b) + (a & b)", "(a ^ b) + 2*(a & b)"]
for e in exprs:
    print(f"{e}  →  {simplify_mba(e)}")
```

---

## 6. Complete Deobfuscation Case Script

```bash
#!/bin/bash
# OLLVM deobfuscation pipeline (2026 community tools)
# for standard OLLVM / Hikari / O-MVLL hardened ELF/.so

BINARY=$1

echo "[*] Stage 0: basic analysis and variant identification"
file $BINARY
readelf -h $BINARY 2>/dev/null | head -5
echo "    → confirm the variant in IDA (see section 1)"

echo "[*] Stage 1: d810-ng local deobfuscation (first choice)"
echo "    IDA → Ctrl-Shift-D to load d810-ng"
echo "    check: MBA + Opaque predicate + Unflattener"
echo "    Apply to target functions"
echo "    save the IDB"

echo "[*] Stage 2: obpo-plugin (if d810-ng is insufficient and network is available)"
echo "    IDA → right-click dispatcher → OBPO → Mark and process"
echo "    ⚠️ don't use on sensitive samples (binary uploaded to cloud service)"

echo "[*] Stage 3: no-IDA alternative (x86/x64)"
echo "    python unflattener -i $BINARY -o deobf.bin -t <func_addr> -a"

echo "[*] Stage 4: ARM64 .so no-IDA alternative"
echo "    deollvm (Unicorn) or angr Deobfuscator"

echo "[+] Done. Re-analyze and verify in IDA."
```

---

## 7. Common Pitfalls (community field experience)

| Problem | Cause | Solution |
|------|------|---------|
| angr path explosion/abnormal exit | Pluto/Polaris **Trap Angr** pass | switch to d810-ng or Unicorn dynamic methods |
| obpo-plugin can't connect | server maintained at author's cost, may be down | use local d810-ng; can file an issue on the obpo repo |
| Goron/Arkari indirect-jump deflat fails | dispatcher uses BR x8 instead of switch | make the data section read-only first, then use DeObfBR |
| function still messy after d810-ng | OLLVM customized pass params/seed | remove opaque predicates with symbolic execution first, then unflatten |
| nested fla (multi-layer flattening) not fully cleaned in one pass | obpo/d810-ng clear one layer per pass | **iterate**: mark each newly appearing dispatcher |
| deflat errors on ARM64 .so | old deflat scripts only support x86 | use d810-ng / obpo (ARM64 support) / deollvm |
| Hikari strings invisible | String Encryption pass | use Unicorn to emulate the decryption stub and dump decrypted strings |
| deflat completely ineffective on amice targets | contains VM Flatten / Instruction Virtualization | **not OLLVM fla**; needs VM handler recovery (see VM reversing) |
| Hodur(PlugX) sample has no switch dispatcher | nested while(1) + jnz state | use d810-ng **HodurUnflattener**, not the normal Unflattener |
| Approov state constants show no pattern | constants concentrated in 0xF6000–0xF6FFF | use d810-ng **BadWhileLoop** unflattener |
| sensitive sample mistakenly run through obpo | binary uploaded to cloud service | classified/unpublished-vuln samples: **local tools only** (d810-ng/angr) |
| Frida hook of OLLVM function hangs | state variable modified causing infinite loop | add a conditional breakpoint at dispatcher entry to limit executions |

---

## 8. Tool Quick Reference (2026 community activity)

| Tool | Platform | Method | Stars/price | Last update | Open source | Notes |
|------|------|------|---------|---------|------|------|
| **obpo-plugin** | IDA | microcode+concolic (cloud) | 629 | 2026-06 | plugin open/core closed | strongest results, needs network |
| **ollvm-breaker** | Binary Ninja | BN API | 441 | 2026-06 | ✅ | real Android .so work |
| **ollvm-unflattener** | CLI | Miasm symbolic execution | 265 | 2026-06 | ✅ | x86/x64, BFS multi-layer |
| **d810-ng** | IDA | microcode+Z3 | 223 | 2026-06 | ✅ | **local first choice**, broad variant coverage |
| **DeObfBR** | — | BR obfuscation specialist | 96 | 2026-06 | ✅ | Goron/Arkari indirect branches |
| **IDA_Ollvm-unflattener** | IDA | Miasm plugin version | 90 | 2026-04 | ✅ | IDA plugin wrapper of ollvm-unflattener |
| **deollvm** | CLI | Unicorn | 34 | 2026-04 | ✅ | ARM64 specialist |
| **angr** | CLI | symbolic execution | — | active | ✅ | general; countered by Trap Angr |
| **SiMBA** | CLI/library | MBA simplification | — | — | ✅ | expression simplification |
| **Triton** | CLI | symbolic execution + taint | — | active | ✅ | dynamic symbolic execution |

---

## 9. Reference Links

**Obfuscators (to understand the adversarial target):**
- [obfuscator-llvm/obfuscator](https://github.com/obfuscator-llvm/obfuscator) — original OLLVM
- [HikariObfuscator/Hikari](https://github.com/HikariObfuscator/Hikari) — Hikari
- [komimoe/Hikari](https://github.com/komimoe/Hikari) — Arkari (based on goron, LLVM 14+)
- [amimo/goron](https://github.com/amimo/goron) — goron
- [bluesadi/Pluto](https://github.com/bluesadi/Pluto) — Pluto
- [za233/Polaris-Obfuscator](https://github.com/za233/Polaris-Obfuscator) — Polaris (formerly Pluto)
- [open-obfuscator/o-mvll](https://github.com/open-obfuscator/o-mvll) — O-MVLL
- [fuqiuluo/amice](https://github.com/fuqiuluo/amice) — Rust implementation of OLLVM passes
- [lich4/awesome-ollvm](https://github.com/lich4/awesome-ollvm) — **variant ecosystem overview (strongly recommended to read first)**

**Deobfuscation tools:**
- [obpo-project/obpo-plugin](https://github.com/obpo-project/obpo-plugin) — strongest cloud plugin
- [w00tzenheimer/d810-ng](https://github.com/w00tzenheimer/d810-ng) — local first choice
- [cdong1012/ollvm-unflattener](https://github.com/cdong1012/ollvm-unflattener) — Miasm pure script
- [amimo/ollvm-breaker](https://github.com/amimo/ollvm-breaker) — Binary Ninja
- [GeT1t/deollvm](https://github.com/GeT1t/deollvm) — ARM64 Unicorn
- [Mrack/DeObfBR](https://github.com/Mrack/DeObfBR) — BR obfuscation specialist
- [maskelihileci/IDA_Ollvm-unflattener](https://github.com/maskelihileci/IDA_Ollvm-unflattener) — IDA plugin version
- [angr](https://angr.io/) — symbolic execution framework
- [SiMBA](https://github.com/tech-srl/simba) — MBA simplification

**Academic/blogs:**
- [Quarkslab: Deobfuscation: Recovering an OLLVM-protected program](https://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html) — classic deflat principles
- [MODeflattener](https://github.com/mrT4ntr4/MODeflattener) — static deflat (counterpart of ollvm-unflattener)

> Related docs: [[anti-analysis.md]] (anti-debug/anti-analysis master table), [[tools-advanced.md]] (advanced tool set), [[elf-analysis.md]] (ELF file analysis), [[ai-assisted-re.md]] (AI-assisted reversing)

