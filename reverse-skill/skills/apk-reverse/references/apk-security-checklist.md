# APK Security Testing Cheatsheet

> Organized from OWASP MASTG (Mobile Application Security Testing Guide).
> Covers six dimensions: static analysis, dynamic analysis, network communication, data storage, authentication/authorization, code protection.

---

## Static Analysis Checklist

### Manifest Audit

```text
□ android:debuggable="true" → debuggable (should not appear in production)
□ android:allowBackup="true" → data can be backed up/extracted
□ Components with android:exported="true" → exposed Activity/Service/Receiver/Provider
□ Custom permission protectionLevel → is it normal (should be signature)
□ scheme in intent-filter → can the custom deeplink be hijacked
□ android:usesCleartextTraffic="true" → plaintext HTTP allowed
□ minSdkVersion too low → may lack security features
```

### Code Audit Key Points

```text
□ Hardcoded keys/tokens (search "key", "secret", "password", "api_key")
□ Insecure randomness (java.util.Random instead of SecureRandom)
□ Insecure crypto (ECB mode, DES, MD5 for passwords)
□ WebView configuration (setJavaScriptEnabled + addJavascriptInterface = RCE risk)
□ SQL injection (rawQuery concatenating user input)
□ Path traversal (ContentProvider openFile without path validation)
□ Log leakage (Log.d/Log.i outputting sensitive info)
□ Clipboard leakage (ClipboardManager storing sensitive data)
□ Implicit Intent leakage (sendBroadcast without specifying a package)
```

### Third-Party Library Audit

```text
□ Outdated OkHttp/Retrofit versions (known vulnerabilities)
□ Outdated WebView engine
□ SDKs with known vulnerabilities (check CVEs)
□ Ad SDK data collection scope
□ Push SDK configuration (does it leak tokens)
```

---

## Dynamic Analysis Checklist

### Priority Frida Hook Targets

| Target | Hook point | Purpose |
|------|---------|------|
| Login auth | `LoginActivity.login()` | observe credential handling |
| Signature generation | `*Sign*`, `*sign*`, `*encrypt*` | recover the signing algorithm |
| SSL Pinning | `CertificatePinner.check` | bypass for traffic capture |
| Root detection | `*root*`, `*su*`, `*magisk*` | bypass detection |
| Crypto operations | `javax.crypto.Cipher` | extract key/IV |
| Token storage | `SharedPreferences.getString` | observe token reads/writes |
| Network requests | `OkHttpClient.newCall` | observe request construction |

### Useful One-Liner Frida Commands

```bash
# trace all crypto operations
frida-trace -U -f com.target.app -j '*Cipher*!*'

# trace all HTTP requests
frida-trace -U -f com.target.app -j '*OkHttp*!*'

# trace SharedPreferences reads/writes
frida-trace -U -f com.target.app -j '*SharedPreferences*!*'

# trace all native function calls
frida-trace -U -f com.target.app -i 'Java_*'
```

### Quick Objection Commands

```bash
# connect
objection -g com.target.app explore

# common commands
android hooking list activities
android hooking list services
android sslpinning disable
android root disable
android clipboard monitor
env                              # view the app directory
sqlite connect <db_path>         # connect to a database
```

---

## Network Communication Security

### Traffic Capture Setup

```text
Method 1: system proxy + Burp/mitmproxy
- set WiFi proxy → Burp listen address
- install the CA certificate on the device
- Android 7+ needs network_security_config or a Frida bypass

Method 2: VPN mode (recommended)
- use HttpCanary / Packet Capture
- no root needed, no proxy config needed
- but cannot decrypt SSL-pinned traffic

Method 3: Frida + r2frida
- intercept network calls directly in-process
- not limited by proxy/VPN
```

### Check Items

```text
□ Is HTTPS used (all API calls)
□ Is there SSL Pinning (certificate binding)
□ Is certificate validation correct (no self-signed accepted)
□ Is there Certificate Transparency (CT) checking
□ Are API keys sent in plaintext in requests
□ Do tokens have an expiry mechanism
□ Is there request signing against tampering
□ Is there replay protection (nonce/timestamp)
□ Is WebSocket encrypted
□ Is sensitive data in URL parameters (gets logged)
```

---

## Data Storage Security

### Locations to Check

| Location | Risk | Check command |
|------|------|---------|
| SharedPreferences | tokens/passwords in plaintext | `adb shell cat /data/data/pkg/shared_prefs/*.xml` |
| SQLite databases | unencrypted sensitive data | `adb pull /data/data/pkg/databases/` |
| External storage | readable by any app | `adb shell ls /sdcard/Android/data/pkg/` |
| App logs | debug info leakage | `adb logcat \| grep pkg` |
| Backup files | allowBackup=true | `adb backup -f backup.ab pkg` |
| Keyboard cache | input history | check whether `inputType` is `textPassword` |
| Screenshot protection | sensitive pages screenshotable | check for `FLAG_SECURE` |

### Encrypted Storage Options Compared

| Option | Security | Notes |
|------|--------|------|
| Plain SharedPreferences | ❌ | directly readable after root |
| EncryptedSharedPreferences | ✓ | AndroidX Security library |
| SQLCipher | ✓ | encrypted SQLite |
| Android Keystore | ✓✓ | hardware-level key protection |
| Custom AES encryption | ⚠️ | depends on key management |

---

## Authentication and Authorization

### Common Vulnerabilities

| Vulnerability | Test method |
|------|---------|
| Weak password policy | try 123456, password, etc. |
| No lockout mechanism | brute force the login endpoint |
| Token never expires | replay an old token after logout |
| IDOR | modify user_id in requests |
| Brute-forceable SMS code | 4/6-digit code with no rate limit |
| OAuth misconfiguration | tamperable redirect_uri |
| Biometric auth bypass | hook BiometricPrompt |
| Device binding bypass | modify device_id |

### Test Payloads

```bash
# IDOR test
curl -H "Authorization: Bearer USER_A_TOKEN" \
     "https://api.target.com/users/USER_B_ID/profile"

# Token replay
# 1. log in normally to get a token
# 2. log out
# 3. request with the old token → should return 401

# SMS code brute force
for code in $(seq 0000 9999); do
    curl -X POST "https://api.target.com/verify" \
         -d "phone=13800138000&code=$code"
done
```

---

## Code Protection Assessment

| Protection | Detection method | Bypass difficulty |
|---------|---------|---------|
| ProGuard obfuscation | check jadx for class names like a/b/c | Low (just renaming) |
| String encryption | find the decryption function, hook for plaintext | Medium |
| Anti-debug | try attaching a debugger | Medium (Frida can bypass) |
| Root detection | run on a rooted device | Medium (generic scripts bypass) |
| Emulator detection | run on an emulator | Low-Medium |
| Integrity checking | install a modified APK | Medium (patch the check function) |
| Hardening/packer | look at the entry class and .so | Medium-High (needs unpacking) |
| Native protection | core logic in .so | High (needs IDA analysis) |
| VMP virtualization | code executed virtualized | Very high |

---

## Quick Test Flow (30 minutes)

```text
1. [5min] Unpack + Manifest audit
   apktool d app.apk
   check debuggable/allowBackup/exported/cleartext

2. [10min] Quick code audit
   jadx -d out app.apk
   search: password, key, secret, token, http://

3. [5min] Network testing
   configure proxy → operate the APP → check for plaintext/weak encryption

4. [5min] Storage check
   adb shell → check shared_prefs and databases

5. [5min] Dynamic validation
   Frida hook key functions → confirm findings
```

