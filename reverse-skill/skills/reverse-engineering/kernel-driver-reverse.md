# Kernel Driver Reversing Reference

> Covers Windows/Linux kernel driver reversing, rootkit analysis, and C/C++ binary pattern recognition.

---

## Windows Driver Reversing

### Driver Types

| Type | Characteristics | Analysis focus |
|------|------|---------|
| WDM (Windows Driver Model) | legacy drivers, manually managed IRPs | DriverEntry → device creation → Dispatch routines |
| KMDF (Kernel Mode Driver Framework) | modern framework, event-driven | EvtDriverDeviceAdd → Queue → I/O callbacks |
| WDF (Windows Driver Foundation) | umbrella term for KMDF + UMDF | look at WdfDriverCreate calls |
| Minifilter | filesystem filter driver | FltRegisterFilter → Pre/Post callbacks |

### WDM Driver Analysis Flow

```text
1. Locate DriverEntry (entry point)
   - IDA auto-detects it, or search for IoCreateDevice / IoCreateSymbolicLink

2. Locate the device name and symbolic link
   - IoCreateDevice → DeviceName (e.g. \Device\MyDriver)
   - IoCreateSymbolicLink → SymLink (e.g. \DosDevices\MyDriver)

3. Locate Dispatch routines
   - DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DispatchIoctl
   - this is the entry point called from user mode via DeviceIoControl

4. Analyze IOCTL handling
   - switch(IoControlCode) dispatches different functions
   - IOCTL encoding: CTL_CODE(DeviceType, Function, Method, Access)
   - Method: METHOD_BUFFERED / METHOD_IN_DIRECT / METHOD_OUT_DIRECT / METHOD_NEITHER

5. Look for vulnerabilities
   - user-controlled buffer length not validated → overflow
   - METHOD_NEITHER uses user pointers directly → arbitrary read/write
   - IOCTL permissions not checked → callable by unprivileged users
```

### IOCTL Encoding Parsing

```python
# Parse the IOCTL code
def decode_ioctl(code):
    device_type = (code >> 16) & 0xFFFF
    access = (code >> 14) & 0x3
    function = (code >> 2) & 0xFFF
    method = code & 0x3
    
    methods = {0: "BUFFERED", 1: "IN_DIRECT", 2: "OUT_DIRECT", 3: "NEITHER"}
    access_types = {0: "ANY", 1: "READ", 2: "WRITE", 3: "READ|WRITE"}
    
    return f"DevType=0x{device_type:X} Func=0x{function:X} Method={methods[method]} Access={access_types[access]}"

# Example
decode_ioctl(0x80002034)
# DevType=0x8000 Func=0x80D Method=BUFFERED Access=ANY
```

### IDA Plugins

| Plugin | Purpose | Link |
|------|------|------|
| **Driver Buddy Reloaded** | auto-identifies IOCTLs, Dispatch routines, device names | https://github.com/VoidSec/DriverBuddyReloaded |
| **WinDbg + IDA** | kernel debugging + static analysis combined | built-in |
| **FLIRT/Lumina** | identify WDK library functions | built into IDA |

### Reference Articles

- [Windows Drivers RE Methodology (VoidSec)](https://voidsec.com/windows-drivers-reverse-engineering-methodology/) — the most complete WDM driver reversing methodology
- [Driver Reversing 101](https://eversinc33.com/posts/driver-reversing.html) — WDM vs KMDF comparison
- [Methodology of Reversing Vulnerable Killer Drivers](https://whiteknightlabs.com/2025/10/28/methodology-of-reversing-vulnerable-killer-drivers/) — vulnerable-driver analysis

---

## Linux Kernel Module Reversing

### LKM (Loadable Kernel Module) Structure

```text
Key functions:
- init_module / module_init → executed when the module loads
- cleanup_module / module_exit → executed when the module unloads

Key structures:
- struct file_operations → open/read/write/ioctl of char devices
- struct net_device_ops → network device operations
- struct block_device_operations → block device operations
```

### Analysis Flow

```text
1. Confirm it is a kernel module
   file module.ko → "ELF 64-bit ... relocatable" (note: relocatable, not executable)

2. Locate init/exit functions
   readelf -s module.ko | grep -E "init_module|cleanup_module"
   or look for module info in the .modinfo section

3. Locate the file_operations structure
   search for register_chrdev / cdev_add / misc_register
   → find the fops struct → locate the ioctl/read/write handlers

4. Analyze ioctl handling
   unlocked_ioctl / compat_ioctl functions
   → switch(cmd) dispatch

5. Look for Rootkit behavior
   - modifying sys_call_table → syscall hook
   - modifying the /proc filesystem → hiding processes/files
   - registering a netfilter hook → hiding network connections
   - modifying the VFS layer → hiding files
```

### Common Rootkit Techniques

| Technique | Characteristics | Detection |
|------|------|---------|
| syscall table hook | modifies `sys_call_table` entries | compare the in-memory table with the on-disk vmlinux |
| VFS hook | modifies `file_operations` function pointers | check whether fops pointers point outside the kernel code section |
| Netfilter hook | `nf_register_net_hook` | walk the netfilter hook list |
| kprobe/ftrace hook | registers kprobe or ftrace callbacks | inspect the ftrace registration list |
| eBPF rootkit | loads malicious BPF programs | `bpftool prog list` |
| DKOM | directly modifies kernel objects (process lists) | walk the task_struct list and compare with /proc |

### Tools

| Tool | Purpose |
|------|------|
| `crash` | kernel dump analysis |
| `volatility3` | memory forensics (Linux profile) |
| `dmesg` / `journalctl` | kernel logs |
| `lsmod` / `/proc/modules` | loaded-module list |
| `modinfo` | module metadata |
| `strace` | syscall tracing (user-mode perspective) |

---

## C/C++ Reversing Pattern Recognition

### Common C Patterns

| Source pattern | Disassembly signature |
|---------|-----------|
| `if-else` | `cmp` + `jcc` (conditional jump) |
| `switch-case` | jump table (`jmp [rax*8 + table]`) or a chain of `cmp` |
| `for` loop | `cmp` + `jl/jle` + loop body + `inc/add` + `jmp` back |
| `while` loop | condition check at the top of the loop |
| `do-while` | condition check at the bottom of the loop |
| function pointer call | `call rax` or `call [reg+offset]` |
| `struct` access | `[reg+fixed offset]` (e.g. `[rdi+0x10]`) |
| `malloc` + use | `call malloc` → return value into a register → later accessed via that register + offset |
| string comparison | `call strcmp` or `repe cmpsb` |

### C++-Specific Patterns

| Source pattern | Disassembly signature |
|---------|-----------|
| **virtual call** | `mov rax, [rcx]` (load vtable) → `call [rax+offset]` (call the virtual function) |
| **constructor** | allocate memory → write vtable pointer → initialize members |
| **destructor** | clean up members → may call `operator delete` |
| **this pointer** | the first argument (rcx/rdi) is the object pointer |
| **inheritance** | vtable contains parent virtuals + child overrides |
| **multiple inheritance** | multiple vtable pointers in the object (different offsets) |
| **RTTI** | a `type_info` pointer precedes the vtable |
| **exception handling** | `__cxa_throw` / `_CxxThrowException` |
| **STL containers** | `std::vector`: three-pointer structure `{begin, end, capacity}` |
| **std::string** | small-string optimization (SSO): short strings inline, long strings heap-allocated |

### vtable Reversing Approach

```text
1. Locate the vtable
   - search for a contiguous array of function pointers (in .rodata or .rdata)
   - `mov [rcx], offset vtable` in the constructor writes the vtable pointer

2. Determine the class hierarchy
   - the RTTI pointer is usually at vtable offset -8 (if not stripped)
   - multiple vtables sharing the first few entries → inheritance relationship

3. Annotate virtual functions
   - vtable[0] is usually the destructor (or deleting destructor)
   - then annotate by offset: vtable[1] = func1, vtable[2] = func2...

4. Work inside IDA
   - create a struct at the vtable address (each field is a function pointer)
   - annotate `call [rax+offset]` with the virtual function it invokes
```

### Struct Recovery

```text
Method 1: infer from access patterns
  mov eax, [rdi+0x00]  → field_0: int/ptr (4/8 bytes)
  mov ecx, [rdi+0x08]  → field_8: int/ptr
  movss xmm0, [rdi+0x10] → field_10: float

Method 2: infer from sizeof
  call malloc(0x30) → struct size 0x30 (48 bytes)
  
Method 3: infer from the constructor
  the constructor initializes every field → field types and offsets become obvious

Method 4: use IDA's "Create struct" feature
  select the access pattern → Edit → Struct → Create struct from selection
```

---

## Common Compiler Signatures

| Compiler | Identifying traits |
|--------|---------|
| MSVC | `_security_cookie` checks, `__fastcall` calling convention, Rich Header |
| GCC | `__stack_chk_fail`, `-fstack-protector`, `.note.GNU-stack` |
| Clang/LLVM | like GCC but different optimization modes, `__asan_*` (if sanitizers enabled) |
| MinGW | GCC traits + Windows API calls |
| AOSP Clang | Android-specific `__android_log_print`, PGO markers |

### Optimization-Level Identification

| Opt level | Characteristics |
|---------|------|
| -O0 | lots of redundant movs, every variable on the stack, no inlining |
| -O1 | basic optimization, some variables in registers |
| -O2 | loop unrolling, inlining, tail-call optimization |
| -O3 / -Os | aggressive inlining, vectorization (SIMD), harder to read |
| PGO | hot-path optimization, cold code split into `.text.cold` |
| LTO | cross-module inlining, global dead-code elimination |

---

## Kernel Debugging Environment

### Windows

```text
Debugger: WinDbg Preview
Connection: network debugging (recommended) or serial

Target machine setup:
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.x.x port:50000

Debugger machine connection:
WinDbg → File → Attach to Kernel → Net → Port:50000 Key:xxx

Common commands:
!analyze -v          # auto-analyze the crash
lm                   # list loaded modules
!drvobj \Driver\xxx  # inspect the driver object
dt nt!_DRIVER_OBJECT # display the struct
bp module!function   # set a breakpoint
```

### Linux

```text
Debugger: GDB + QEMU or kgdb

QEMU kernel debugging:
qemu-system-x86_64 -kernel bzImage -s -S ...
gdb vmlinux -ex "target remote :1234"

Common commands:
info threads         # kernel threads
lx-symbols           # load kernel symbols (requires scripts/gdb/)
p init_task          # view the init process
lx-dmesg             # kernel log
```

---

## Reference Resources

| Resource | Description | Link |
|------|------|------|
| VoidSec driver reversing methodology | complete Windows WDM driver analysis flow | https://voidsec.com/windows-drivers-reverse-engineering-methodology/ |
| Elastic rootkit series | Linux rootkit classification + detection | https://security-labs.elastic.co/security-labs/linux-rootkits-1-hooked-on-linux |
| Driver Buddy Reloaded | IDA driver-analysis plugin | https://github.com/VoidSec/DriverBuddyReloaded |
| LOLDrivers | list of known vulnerable drivers | https://www.loldrivers.io/ |
| Windows Driver Samples | official Microsoft driver samples | https://github.com/microsoft/Windows-driver-samples |
| Linux Kernel Module Programming | kernel-module dev tutorial | https://sysprog21.github.io/lkmpg/ |
| Trail of Bits - Devirtualizing C++ | vtable reversing approach | https://blog.trailofbits.com/2017/02/13/devirtualizing-c-with-binary-ninja/ |
