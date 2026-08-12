# Frida Bypass Kit — Generic Android Security Bypass Framework

> Source: [FridaBypassKit](https://github.com/okankurtuluss/FridaBypassKit) (2025)
> When to use: APK dynamic analysis requiring bypass of root detection, SSL pinning, emulator detection, and anti-debugging

## Overview

FridaBypassKit is a Frida script integrating four bypass capabilities. No per-APP customization needed — works out of the box.

## Four Bypass Capabilities

### 1. Root Detection Bypass

- Hooks `File.exists()` to hide the su binary
- Intercepts `Runtime.exec()` root-check calls
- Hides root-related packages from PackageManager (Magisk, SuperSU, etc.)
- Modifies system properties to make the device look unrooted

### 2. SSL Pinning Bypass

- Hooks `TrustManagerImpl.verifyChain()`
- Hooks `TrustManagerImpl.checkTrustedRecursive()`
- Bypasses certificate chain validation
- Returns an empty certificate chain to avoid validation
- Compatible with OkHttp, Retrofit, and custom implementations

### 3. Emulator Detection Bypass

- Fakes TelephonyManager return values
- Returns fake phone numbers and carrier names
- Modifies Build properties

### 4. Anti-Debug Bypass

- Hooks `Debug.isDebuggerConnected()`
- Blocks debugger detection
- Bypasses anti-debug checks

## Usage

```bash
# prerequisites
pip install frida-tools
adb push frida-server /data/local/tmp/
adb shell chmod 755 /data/local/tmp/frida-server
adb shell su -c /data/local/tmp/frida-server &

# inject into the target APP
frida -U -f com.example.app -l FridaBypassKit.js
```

## Other Recommended Frida Bypass Scripts

| Project | Features | Link |
|------|------|------|
| httptoolkit/frida-interception-and-unpinning | direct MitM of all HTTPS traffic | [GitHub](https://github.com/httptoolkit/frida-interception-and-unpinning) |
| 0xCD4/SSL-bypass | generic non-custom SSL bypass | [GitHub](https://github.com/0xCD4/SSL-bypass) |
| incogbyte/ssl-bypass gist | bypasses common SSL pinning methods | [Gist](https://gist.github.com/incogbyte/1e0e2f38b5602e72b1380f21ba04b15e) |
| Zero3141/Frida-OkHttp-Bypass | specifically targets OkHttp CertificatePinner | [GitHub](https://github.com/Zero3141/Frida-OkHttp-Bypass) |

## Integration With This Pack

In the `apk-reverse` workflow, use it when:

1. The APP detects root and refuses to run → enable Root Detection Bypass
2. HTTPS requests show no plaintext during capture → enable SSL Pinning Bypass
3. The APP detects the emulator and refuses to run → enable Emulator Detection Bypass
4. The APP crashes after Frida attaches → enable Debug Detection Bypass

Recommended combo: run the full FridaBypassKit first, then tune per-target.

