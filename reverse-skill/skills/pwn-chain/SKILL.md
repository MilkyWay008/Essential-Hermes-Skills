---
name: pwn-chain
description: >-
  Use for the full chain from reverse engineering to a working exploit: given a binary, vulnerability point,
  and target environment, write an exploit that reliably lands. Covers stack/heap/kernel pwn, pwntools,
  libc-database, and CTF-to-real-world stabilization.
---

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm this skill's operations are authorized routine work
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths (if missing at cold start, run `scripts/refresh-tool-index.ps1` on Windows or `bash scripts/refresh-tool-index.sh` on Linux/macOS first)
4. `NEXT`: Call bootstrap when tools are missing; don't guess paths
5. `ACT`: Proceed to the first step of the "Workflow" and execute it; don't stop at the confirmation stage

# From Vulnerability Point to Working Exploit (Pwn Chain)

## Scope

Use this skill when the task falls into the following scenarios:

1. **Binary in hand + known vulnerability point** — static analysis/audit/fuzzing already found an overflow/UAF/double free; need to go from triggering it to getting a shell
2. **CTF challenge works locally but fails remotely** — remote environment differences break the script; need to stabilize it
3. **Exploitation of real targets** — in SRC / red-team scenarios, a memory-corruption vulnerability has been identified and an RCE needs to be built
4. **ioctl bug in a Linux kernel driver** — triggered from userland, goal is privilege escalation to root

**Prerequisite**: you already know "where it blows up". This skill does not discover vulnerabilities (that's fuzzing / auditing) — it only handles "writing an exploit from the vulnerability point".

### Division of Labor with Other Skills

| Scenario | What to use |
|------|--------|
| Identify custom VMs / anti-debug / complex obfuscation | `reverse-engineering/` |
| Open the binary from scratch for static analysis | `ida-reverse/` or `radare2/` |
| **Have a vulnerability point, write an exploit that lands remotely** | **this skill** |
| Integrate the pwned shell into a full attack chain | `attack-chain/` (downstream) |

`reverse-engineering/` is about "understanding what the program does" (pattern recognition, protocol recovery, solving odd mechanisms in CTF challenges); this skill is about "turning an understood vulnerability into a working attack". The two are often used together, but the division is clear.

## Core Workflow

```text
Step 1: Confirm vulnerability type + protection mechanisms
   ├─ checksec ./vuln (NX / Canary / PIE / RELRO / Fortify)
   ├─ file ./vuln  + readelf -d ./vuln
   ├─ Vulnerability class: stack overflow / format string / heap (UAF/DF/OF) / integer / race / kernel
   └─ → decide which references/ to use

Step 2: Choose exploitation strategy
   ├─ NX off + no ASLR → direct shellcode
   ├─ NX on + libc given → ret2libc / one_gadget
   ├─ NX on + no libc given → leak, then look up libc-database
   ├─ Heap → technique per glibc version (tcache/fastbin/unsorted/large)
   └─ Kernel → commit_creds / modprobe_path / core_pattern

Step 3: Prepare libc + gadgets
   ├─ libc-database: ./find puts 0x6f0
   ├─ ROPgadget --binary ./libc.so.6 --only "pop|ret"
   ├─ one_gadget ./libc.so.6
   └─ Compute base: leak_addr - libc.sym['puts']

Step 4: Write pwntools template (local process)
   ├─ context.binary = ELF('./vuln')
   ├─ p = process('./vuln')  /  p = gdb.debug('./vuln','b *main+xx')
   ├─ payload = cyclic(N) + p64(ret) + ...
   └─ p.interactive()

Step 5: Make it work locally
   ├─ Repeatedly attach + inspect registers + adjust offset
   ├─ Use pwndbg/GEF vmmap / heap / bins / telescope
   └─ Once it works locally, switch to remote()

Step 6: Stabilize the remote exploit
   ├─ libc offsets: look up libc-database from the leak, don't guess
   ├─ Stack alignment: 16-byte misalignment → movaps crash → add a ret gadget
   ├─ Remote network latency → anchor recvuntil on exact strings, avoid fuzzy sleep
   ├─ Remote buffering: sendlineafter is more reliable than sendline
   ├─ Heap spray success rate: increase spray size + keep padding chunks to prevent consolidation
   └─ Run repeatedly: loop with while True to verify success rate ≥ 95%
```

## Typical Scenarios

### Scenario 1: Remote 64-bit binary (NX+PIE+canary, libc provided)

```text
Have: ./vuln (64-bit ELF, NX, PIE, canary) + ./libc.so.6 + nc host port
Bug: read(buf, 0x200) but buf is only 0x40 bytes → stack overflow
Mitigations: canary blocks us, PIE randomizes .text

Plan:
1. First leak canary (stack / format string / partial read)
2. Then leak a libc function address (puts@got)
3. Compute libc base with libc.address = leaked - libc.sym['puts']
4. Pick a magic gadget whose constraints are satisfiable via one_gadget ./libc.so.6
5. payload = padding + canary + saved_rbp + (pop_rdi + bin_sh + system) or use one_gadget directly
6. Add a ret gadget to fix stack alignment (critical!)
```

See `references/stack-pwn.md` for the full template.

### Scenario 2: Linux kernel driver ioctl out-of-bounds write → root

```text
Have: vmlinux + bzImage + initramfs.cpio.gz + custom vuln.ko
Bug: ioctl(0x1337, ptr) has controllable copy_from_user length → kernel heap overflow (kmalloc-64 slab)
Mitigations: SMEP, SMAP, KASLR, KPTI

Plan:
1. Modify the init script to get a root shell (CTF) or first leak the KASLR base and continue (real-world)
2. Leak the kernel base via /proc/kallsyms (may be restricted) or an uninitialized heap spray
3. Spray tty_struct / msg_msg / pipe_buffer in the kmalloc-64 slab
4. Overwriting the vtable pointer to userspace → blocked (SMEP), switch to stack pivot + kernel ROP
5. ROP chain: prepare_kernel_cred(0) → commit_creds → swapgs+iretq → userspace execve("/bin/sh")
6. Or easier: overwrite modprobe_path with "/tmp/x", write a /tmp/x, then trigger modprobe
```

See `references/kernel-pwn.md` for the full template.

## On-Demand Bootstrap

### Tool Dependencies

| Tool | Purpose | Install method |
|------|------|---------|
| pwntools | exploit-writing framework | `pip install pwntools` |
| GEF | gdb enhancement (recommended for both kernel and userland) | `git clone https://github.com/bata24/gef` (actively maintained fork) |
| pwndbg | gdb enhancement (best heap-debugging experience) | `git clone https://github.com/pwndbg/pwndbg && ./setup.sh` |
| ROPgadget | gadget search | `pip install ropgadget` |
| Ropper | gadget search (alternative, supports more architectures) | `pip install ropper` |
| one_gadget | find libc magic gadgets | `gem install one_gadget` (requires ruby) |
| libc-database | libc fingerprint lookup | `git clone https://github.com/niklasb/libc-database && ./get` |
| qemu-system-x86_64 | kernel-challenge debugging | `apt install qemu-system-x86` |
| binwalk / cpio | initramfs unpacking | `apt install binwalk cpio` |
| patchelf | switch libc versions | `apt install patchelf` |

### Bootstrap Check Script

```bash
# one-shot check + install core tools
for t in pwntools ropgadget ropper; do
  pip show $t >/dev/null 2>&1 || pip install $t
done

command -v one_gadget >/dev/null || gem install one_gadget

[ -d ~/tools/libc-database ] || git clone https://github.com/niklasb/libc-database ~/tools/libc-database
[ -d ~/tools/libc-database/db ] || (cd ~/tools/libc-database && ./get ubuntu debian)

[ -d ~/tools/pwndbg ] || (git clone https://github.com/pwndbg/pwndbg ~/tools/pwndbg && cd ~/tools/pwndbg && ./setup.sh)
```

### After an Automatic Install Fails Twice for the Same Tool

Stop retrying; output structured manual install steps (pip registry / gem registry / git mirror / apt sources) for the user to confirm.

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Trigger condition**: binary in hand + identified vulnerability point, need to write an exploit

**Upstream skills (use them first, then return here)**:
- Don't yet understand what the binary does → `reverse-engineering/`
- Need detailed static analysis → `ida-reverse/`
- Quick recon to confirm architecture/protection mechanisms → `radare2/`

**Downstream skills (after getting the shell)**:
- Integrate into a full attack chain (lateral movement, privilege escalation, persistence) → `attack-chain/`

**Submodule navigation**:
- Stack-based exploitation (ret2libc / ret2csu / one_gadget / stack alignment) → `references/stack-pwn.md`
- Heap-based exploitation (tcache / fastbin / unsorted / large bin / FILE struct) → `references/heap-pwn.md`
- Kernel pwn (kROP / SMEP-SMAP bypass / KASLR leak / modprobe_path) → `references/kernel-pwn.md`

## Notes

- **Don't call it done just because it works locally** — local libc / ASLR / network conditions all differ from remote; you MUST run it 20+ consecutive times in remote mode to verify stability
- **The libc version MUST be confirmed** — look it up via leak + libc-database; don't assume the Ubuntu 22.04 default libc
- **Stack alignment is a common 64-bit pitfall** — `movaps xmm0, [rsp]` faults when rsp isn't 16-byte aligned; fix it by adding a dummy `ret` gadget
- **Heap exploitation is extremely glibc-version-sensitive** — tcache was introduced in 2.27, safe-linking in 2.32, hooks removed in 2.34; each version has a different exploitation path
- **Kernel pwn requires confirming CPU flags first** — whether qemu launch args include +smep +smap +pku directly determines how the ROP chain is written
- **One KASLR leak is enough** — once you have one kernel address, all others are offsets; don't keep leaking

## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
