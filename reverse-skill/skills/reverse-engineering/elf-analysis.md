# ELF Binary Deep-Analysis Reference

> Structure parsing, anti-analysis technique identification, and analysis tips when reversing Linux/Android ELF files.

---

## ELF Structure Quick Reference

### File Header (ELF Header)

```text
Offset  Size  Field             Description
0x00  4    e_ident[EI_MAG]   Magic: 7f 45 4c 46 ("\x7fELF")
0x04  1    e_ident[EI_CLASS] 1=32bit, 2=64bit
0x05  1    e_ident[EI_DATA]  1=LE, 2=BE
0x10  2    e_type            2=EXEC, 3=DYN(PIE/SO), 4=CORE
0x12  2    e_machine         0x03=x86, 0x3E=x86_64, 0xB7=AArch64, 0x28=ARM
0x18  8    e_entry           entry-point virtual address
0x20  8    e_phoff           program-header table offset
0x28  8    e_shoff           section-header table offset (may be 0 after strip)
0x38  2    e_phnum           number of program headers
0x3C  2    e_shnum           number of section headers
```

### Program Header

```text
Type    Name        Description
0x01   PT_LOAD    loadable segment (code/data)
0x02   PT_DYNAMIC dynamic linking info
0x03   PT_INTERP  interpreter path (/lib/ld-linux.so)
0x04   PT_NOTE    auxiliary info
0x06   PT_PHDR    the program-header table itself
0x6474e550 PT_GNU_EH_FRAME  exception handling
0x6474e551 PT_GNU_STACK     stack-executable marker
0x6474e552 PT_GNU_RELRO     read-only relocations
```

### Common Sections

| Section | Description |
|------|------|
| `.text` | code |
| `.rodata` | read-only data (string constants) |
| `.data` | initialized global variables |
| `.bss` | uninitialized global variables |
| `.plt` / `.got` | dynamic-linking jump tables |
| `.init_array` | constructor pointer array |
| `.fini_array` | destructor pointer array |
| `.dynamic` | dynamic-linking info |
| `.symtab` / `.dynsym` | symbol tables |
| `.strtab` / `.dynstr` | string tables |

---

## Anti-Analysis Technique Identification

### Common ELF Anti-Analysis Techniques

| Technique | Characteristics | Countermeasure |
|------|------|---------|
| corrupted program headers | PHDR filled with junk (e.g. 0x0a) | manually repair or ignore the corrupted PHDR |
| no section headers | `e_shoff = 0`, `e_shnum = 0` | analyze using program headers only, no section reliance |
| stripped symbols | no `.symtab`, all function names gone | GoReSym (Go) / signature matching / FLIRT |
| statically linked | no `.dynamic`, huge size | use FLIRT/Lumina to identify library functions |
| disguised file type | .sh/.txt/.jpg extensions | judge with the `file` command / magic bytes |
| UPX packed | contains the `UPX!` marker | unpack with `upx -d` |
| custom packer | entry point jumps to unpacking code | run dynamically to OEP then dump |
| anti-debug | ptrace(TRACEME) | LD_PRELOAD hook / patch |
| anti-VM | checks /proc/cpuinfo | modify cpuinfo or hook the read |
| code encryption | decrypts .text at runtime | breakpoint after decryption then dump |

### Identifying Self-Unpacking / Self-Modifying Code

```text
Signatures:
1. mmap(PROT_READ|PROT_WRITE|PROT_EXEC) call near the entry point
2. memcpy or a copy loop right after
3. then mprotect changes permissions
4. finally br/jmp to the newly mapped address

Analysis strategy:
1. find the mmap call → record the returned address
2. set a breakpoint after mprotect(PROT_EXEC)
3. dump the unpacked memory region
4. analyze it as a new binary
```

---

## ARM64 (AArch64) Reversing Quick Reference

### Registers

| Register | Purpose |
|--------|------|
| x0-x7 | arguments/return values |
| x8 | indirect result (syscall number) |
| x9-x15 | temporary registers |
| x16-x17 | IP0/IP1 (PLT jumps) |
| x18 | platform register (Android: shadow call stack) |
| x19-x28 | callee-saved |
| x29 (FP) | frame pointer |
| x30 (LR) | link register (return address) |
| SP | stack pointer |
| PC | program counter |

### Common Instruction Patterns

```text
Function prologue:
  stp x29, x30, [sp, #-N]!    # save FP and LR
  mov x29, sp                  # set the frame pointer

Function epilogue:
  ldp x29, x30, [sp], #N      # restore FP and LR
  ret                          # return (br x30)

Syscalls:
  mov x8, #NR                  # syscall number
  svc #0                       # trigger the syscall

Conditional branches:
  cmp x0, #0
  b.eq label                   # branch if equal
  b.ne label                   # branch if not equal
  cbz x0, label                # branch if x0 == 0
  cbnz x0, label               # branch if x0 != 0

Address loading:
  adrp x0, page                # load the upper page address
  add x0, x0, #offset          # add the low 12-bit offset
  ldr x0, [x1, #offset]        # load from memory
```

### Linux ARM64 Syscall Numbers

| Number | Name | Description |
|------|------|------|
| 56 | openat | open a file |
| 63 | read | read |
| 64 | write | write |
| 57 | close | close |
| 222 | mmap | memory mapping |
| 226 | mprotect | change memory permissions |
| 117 | ptrace | process tracing |
| 220 | clone | create a process/thread |
| 221 | execve | execute a program |
| 93 | exit | exit |
| 94 | exit_group | exit the process group |

---

## Common Compression/Packing Algorithm Identification

| Algorithm | Identifying traits | Decompression |
|------|---------|---------|
| **LZSS** | bitstream + literal/match markers | custom decompressor (like this report) |
| **ZLIB/Deflate** | Magic: `78 01`/`78 9C`/`78 DA` | `zlib.decompress()` |
| **GZIP** | Magic: `1F 8B` | `gzip -d` / `gunzip` |
| **LZ4** | Magic: `04 22 4D 18` | `lz4 -d` |
| **LZMA/XZ** | Magic: `FD 37 7A 58 5A 00` (XZ) | `xz -d` / `lzma -d` |
| **Brotli** | no fixed magic, judge by context | `brotli -d` |
| **Zstandard** | Magic: `28 B5 2F FD` | `zstd -d` |
| **UPX** | string `UPX!` | `upx -d` |
| **custom** | unpacking loop at the entry point | reverse the algorithm then write a decompressor |

### Clues for Identifying Custom Compression

```text
1. a loop + bit operations (shifts, AND, OR) near the entry point
2. "sliding window" back-copy (reading backwards from the output buffer) → LZ family
3. frequency table / Huffman tree construction → Deflate/Huffman
4. fixed-size block processing → block compression (LZ4/Snappy)
5. arithmetic-coding traits (interval narrowing) → LZMA/ANS
```

---

## Linux Process Injection Techniques

### mmap + Code Injection

```text
Flow:
1. mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_ANON|MAP_PRIVATE, -1, 0)
2. write shellcode/payload into the mapped region
3. mprotect(addr, size, PROT_READ|PROT_EXEC)  # make it executable
4. jump to the mapped address and execute

Signatures:
- the mmap return value is saved
- memcpy or a write loop follows
- then mprotect changes permissions
- finally br/blr to that address
```

### ptrace Injection

```text
Flow:
1. ptrace(PTRACE_ATTACH, target_pid)
2. waitpid(target_pid)
3. ptrace(PTRACE_GETREGS, target_pid, &regs)
4. point regs.pc at the injected code
5. ptrace(PTRACE_SETREGS, target_pid, &regs)
6. ptrace(PTRACE_CONT, target_pid)

Signatures:
- opens /proc/<pid>/mem or uses ptrace
- reads/modifies the target process registers
- writes shellcode into the target process space
```

### /proc/self/mem Self-Modification

```text
Flow:
1. open("/proc/self/mem", O_RDWR)
2. lseek(fd, target_addr, SEEK_SET)
3. write(fd, new_code, size)

Uses:
- bypass W^X (mmap pages cannot be W+X at once)
- modify the own code section (.text is usually read-only)
- patch instructions at runtime
```

---

## Strategy for Analyzing Large ELFs

For binaries of 5MB+:

```text
1. Fast recon (5 min)
   - file / rabin2 -I → architecture, type, protections
   - strings | grep -i "error\|fail\|http\|/proc\|/dev" → key strings
   - rabin2 -i → imported functions (if any)
   - rabin2 -E → exported functions

2. Structure analysis (10 min)
   - readelf -l → program headers (LOAD segment layout)
   - code near the entry point → unpacking/decryption present?
   - find .init_array → constructors (may contain anti-debug)

3. Locate key logic
   - start from string cross-references
   - start from syscalls (mmap/ptrace/open)
   - start from network functions (connect/send/recv)

4. Divide and conquer
   - if self-unpacking → unpack first, analyze the payload
   - if multi-module → analyze in functional blocks
   - use binary-diff to compare versions
```

---

## Tool Commands Quick Reference

```bash
# Basic info
file binary
readelf -h binary          # ELF header
readelf -l binary          # program headers
readelf -S binary          # section headers (if any)
rabin2 -I binary           # combined info

# Strings
strings -a binary | less
rabin2 -z binary           # data-section strings
rabin2 -zz binary          # whole-file strings

# Disassembly
r2 -A binary               # radare2 analysis
objdump -d binary          # GNU disassembly
aarch64-linux-gnu-objdump -d binary  # ARM64 cross-disassembly

# Dynamic analysis
strace -f ./binary         # syscall tracing
ltrace -f ./binary         # library-function tracing
qemu-aarch64 -strace ./binary  # ARM64 emulated execution

# Memory dump
gdb -p <pid> -ex "dump memory out.bin 0xADDR 0xADDR+SIZE" -ex quit

# Fixing a corrupted ELF
# manually edit e_phnum or patch the corrupted PHDR
python -c "
import struct
with open('binary', 'r+b') as f:
    f.seek(0x38)  # e_phnum offset (64-bit)
    f.write(struct.pack('<H', 2))  # set the correct PHDR count
"
```
