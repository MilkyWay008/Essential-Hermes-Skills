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
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths
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
Step 1: 确认漏洞类型 + 保护机制
   ├─ checksec ./vuln（NX / Canary / PIE / RELRO / Fortify）
   ├─ file ./vuln  + readelf -d ./vuln
   ├─ 漏洞分类：栈溢出 / 格式化字符串 / 堆 (UAF/DF/OF) / 整数 / 竞态 / 内核
   └─ → 决定走哪个 references/

Step 2: 选择利用策略
   ├─ NX 关 + 无 ASLR → 直接 shellcode
   ├─ NX 开 + 给 libc → ret2libc / one_gadget
   ├─ NX 开 + 不给 libc → leak 后 libc-database 反查
   ├─ 堆 → 按 glibc 版本对应技术 (tcache/fastbin/unsorted/large)
   └─ 内核 → commit_creds / modprobe_path / core_pattern

Step 3: 准备 libc + gadget
   ├─ libc-database：./find puts 0x6f0
   ├─ ROPgadget --binary ./libc.so.6 --only "pop|ret"
   ├─ one_gadget ./libc.so.6
   └─ 计算 base：leak_addr - libc.sym['puts']

Step 4: 写 pwntools 模板（本地 process）
   ├─ context.binary = ELF('./vuln')
   ├─ p = process('./vuln')  /  p = gdb.debug('./vuln','b *main+xx')
   ├─ payload = cyclic(N) + p64(ret) + ...
   └─ p.interactive()

Step 5: 本地通
   ├─ 反复 attach + 看寄存器 + 调 offset
   ├─ 用 pwndbg/GEF 的 vmmap / heap / bins / telescope
   └─ 跑通后切 remote()

Step 6: 远程稳定化
   ├─ libc 偏移：用 leak 反查 libc-database，不要拍脑袋
   ├─ 栈对齐：16-byte 不对齐 → movaps 崩 → 加一个 ret gadget
   ├─ 远程网络延迟 → recvuntil 精确锚字符串，禁用模糊 sleep
   ├─ 远程缓冲：sendlineafter 比 sendline 更稳
   ├─ 堆喷成功率：放大 spray 数量 + 留 padding chunk 防合并
   └─ 多次跑：写 while True 验证成功率 ≥ 95%
```

## Typical Scenarios

### Scenario 1：Remote 64-bit binary (NX+PIE+canary, libc provided)

```text
已有：./vuln（64-bit ELF, NX, PIE, canary）+ ./libc.so.6 + nc host port
漏洞：read(buf, 0x200) 但 buf 只有 0x40 字节 → 栈溢出
保护：canary 拦住，PIE 让 .text 随机化

策略：
1. 先 leak canary（栈/格式化字符串/部分读）
2. 再 leak 一个 libc 函数地址（puts@got）
3. 用 libc.address = leaked - libc.sym['puts'] 算 libc base
4. one_gadget ./libc.so.6 选一个约束能满足的 magic gadget
5. payload = padding + canary + saved_rbp + (pop_rdi + bin_sh + system) 或直接 one_gadget
6. 加一个 ret gadget 修栈对齐（关键！）
```

See `references/stack-pwn.md` for the full template.

### Scenario 2：Linux kernel driver ioctl out-of-bounds write → root

```text
已有：vmlinux + bzImage + initramfs.cpio.gz + 自定义 vuln.ko
漏洞：ioctl(0x1337, ptr) 里 copy_from_user 长度可控 → kernel heap overflow (kmalloc-64 slab)
保护：SMEP, SMAP, KASLR, KPTI

策略：
1. 改 init 脚本拿到 root shell（CTF）或先 leak KASLR base 再继续（真实）
2. 通过 /proc/kallsyms（可能限权）或未初始化堆喷 leak 内核基址
3. 在 kmalloc-64 slab 里喷 tty_struct / msg_msg / pipe_buffer
4. 覆盖 vtable 指针指向用户态 → 不行（SMEP），改走 stack pivot + 内核 ROP
5. ROP 链：prepare_kernel_cred(0) → commit_creds → swapgs+iretq → 用户态 execve("/bin/sh")
6. 或更省事：覆盖 modprobe_path 为 "/tmp/x"，写一个 /tmp/x，然后触发 modprobe
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
# 一键检查 + 安装核心工具
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
