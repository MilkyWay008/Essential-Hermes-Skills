---
name: mobile-reverse
description: Use for authorized Android or iOS application reverse engineering and security testing, including APK or IPA analysis, runtime instrumentation, SSL pinning, and platform protection checks.
---

# Mobile Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm that this skill's operations are an authorized routine
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Move to the first step of the "Workflow" and execute it; do not stop at confirmation

> Unified Android + iOS reverse engineering methodology
> Frida / Objection / OWASP MSTG / SSL Pinning Bypass

## Applicable Scenarios

- Android APK reverse engineering and security testing
- iOS IPA reverse engineering and security testing
- Runtime dynamic instrumentation of mobile applications
- Bypassing SSL Pinning / Root detection / Jailbreak detection
- Mobile crypto algorithm extraction (AES/RSA/HMAC keys)
- Mobile application penetration testing (OWASP MASTG)
- Application testing in non-Root / non-jailbroken environments

## Four-Phase Workflow

### Phase 1: Information Gathering

```text
Android：
□ APK 获取（Google Play / APKMirror / adb pull）
□ Manifest 分析: 权限、导出组件、Intent Filter、backup 标志
□ androguard: androguard analyze APK → 组件/权限/签名
□ APKLeaks: 硬编码 API Key / Token / Secret 扫描
□ 加固检测: 是否加壳（360/腾讯/梆梆/爱加密）

iOS：
□ IPA 获取（App Store / ipatool / Apple Configurator）
□ 解密 App Store 二进制: frida-ios-dump / Clutch
□ Info.plist 分析: ATS 配置、URL Scheme、Queries Schemes
□ class-dump: 导出 ObjC 类结构
□ 加固检测: 是否使用 Swift/ObjC 混淆
```

### Phase 2: Static Analysis

```text
跨平台：
□ JADX-GUI: APK → Java 源码（Android）
□ Ghidra / Hopper: .so / Mach-O 反编译
□ radare2 / Cutter: CLI 快速侦察

Android 专项：
□ apktool d app.apk → smali 代码 + 资源
□ dex2jar: DEX → JAR → JD-GUI
□ smali/baksmali: Dalvik 字节码修改

iOS 专项：
□ class-dump: 导出 ObjC 头文件
□ Swift 符号恢复: swift-demangle
□ dsymutil: 调试符号提取
□ otool -L: 查看动态库依赖
□ jtool2: Mach-O 分析
```

### Phase 3: Dynamic Analysis

```text
Frida — 通用动态插桩：
□ frida-ps -U: 列出设备进程
□ frida-trace -U -i "open*" com.app: 追踪函数调用
□ 自定义 Hook 脚本: 修改参数/返回值、调用私有方法

Objection — Frida 增强层（无需写脚本）：
□ objection -g "com.app" explore
□ android root disable / ios jailbreak disable
□ android sslpinning disable / ios sslpinning disable
□ android keystore list / ios keychain dump
□ env / ls / sqlite connect

Frida Gadget（免 Root/越狱）：
□ 注入 frida-gadget.so / FridaGadget.dylib 到 APK/IPA
□ 重新签名 → 安装 → 无需设备权限即可 Hook
□ objection patchapk --source app.apk（全自动）
```

### Phase 4: Network Analysis

```text
□ Burp Suite: 拦截 HTTP/HTTPS，修改请求/响应
□ mitmproxy: 脚本化代理（Python API）
□ Wireshark: PCAP 抓包分析
□ 证书安装: Android 用户证书 → 系统证书（Magisk + MoveCert）
□ SSL Pinning 绕过: Frida/Objection/Xposed/SSL Kill Switch 2
□ WebSocket / gRPC 流量分析
```

## Common Bypass Quick Reference

### SSL Pinning

```bash
# Objection（最简）
objection -g "com.app" explore
android sslpinning disable

# Frida 通用脚本
frida -U -l ssl_pinning_bypass.js -f com.app

# Xposed（Android）
TrustMeAlready 模块 → 全局禁用证书校验
```

### Root / Jailbreak Detection

```bash
# Objection
android root disable
ios jailbreak disable

# Frida 自定义（多层检测）
Java.perform(function() {
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    RootBeer.isRooted.implementation = function() { return false; };
    // 额外绕过: Magisk su 检测、frida-server 检测、/proc/self/maps 检测
});
```

### Anti-Debugging

```bash
# Android
frida -U -l anti_debug_bypass.js -f com.app
# 绕过: ptrace(TracerPid)、/proc/self/status、isDebuggerConnected()

# iOS
# 绕过: PT_DENY_ATTACH、sysctl CTL_KERN/KERN_PROC/KERN_PROC_PID
frida -U -l ios_anti_debug.js -f com.app
```

## Mobile Crypto Extraction

```javascript
// Android — Hook Cipher.getInstance 获取密钥+算法
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.getInstance.overload('java.lang.String').implementation = function(algo) {
        console.log("[Cipher] Algorithm: " + algo);
        return this.getInstance(algo);
    };
    Cipher.init.overload('int', 'java.security.Key').implementation = function(mode, key) {
        console.log("[Cipher] Key: " + bytesToHex(key.getEncoded()));
        return this.init(mode, key);
    };
});

// iOS — Hook CCCrypt
Interceptor.attach(Module.findExportByName("libcommonCrypto.dylib", "CCCrypt"), {
    onEnter: function(args) {
        console.log("CCCrypt op: " + args[0] + " alg: " + args[1]);
        console.log("Key: " + hexdump(args[3], { length: args[4].toInt32() }));
    }
});
```

## Toolchain

| Tool | Platform | Purpose |
|------|:--:|------|
| JADX-GUI | A | Java decompilation |
| apktool | A | APK unpacking/rebuilding |
| Ghidra | A+I | Multi-architecture decompilation |
| Hopper | I | iOS-specific disassembly |
| Frida | A+I | Dynamic instrumentation |
| Objection | A+I | Frida REPL enhancement |
| MobSF | A+I | Automated SAST+DAST |
| class-dump | I | ObjC class export |
| frida-ios-dump | I | IPA decryption |
| jtool2 | I | Mach-O analysis |
| Burp Suite | A+I | HTTP interception |
| mitmproxy | A+I | Scriptable proxy |

> A=Android, I=iOS

## References

- `references/frida-objection-deep.md` — Frida + Objection in-depth usage
- `references/ios-reverse-guide.md` — iOS reverse engineering deep-dive
- `references/anti-detection-bypass.md` — Root/Jailbreak/anti-debug/SSL Pinning bypass


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (instead of only reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
