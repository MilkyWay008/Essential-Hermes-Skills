---
name: apk-reverse
description: >-
  Use for Android APK reverse engineering from the CLI: APK unpacking, Java decompilation, smali patching,
  repackaging, Frida dynamic hooking, and on-demand switch to so/native analysis. Prefers locally installed
  jadx, apktool, frida, adb, ida-reverse, and radare2.
---

## ACTION REQUIRED (execute immediately after reading)

> Community references for endpoint extraction / Frida adaptation, etc.: ../references/community-security-skills.md; dynamic analysis MUST only target scope-authorized devices.

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm the operations in this skill are authorized routine operations
2. `NOW`: Confirm whether the current task falls within this skill's scope
3. `NEXT`: Read `../tool-index.md` to verify tool availability and actual paths (if missing at cold start, run `scripts/refresh-tool-index.ps1` on Windows or `bash scripts/refresh-tool-index.sh` on Linux/macOS first)
4. `NEXT`: If tools are missing, call bootstrap; do not guess paths
5. `ACT`: Move into the first step of the workflow and execute; do not stop at confirmation

# APK Reverse Engineering CLI Workflow Guide

## Scope

Use this skill first when the task falls into the following scenarios:

- Analyzing APK Java business logic
- Locating login, signature, risk control, certificate validation, and root detection
- Viewing and modifying `AndroidManifest.xml`
- Viewing and modifying smali
- Repackaging APKs
- Dynamic Java/native hooking with Frida
- Switching to native analysis when the APK contains `.so`

## CLI Tools Verified Available on This Machine

- `jadx` `1.5.5`
- `apktool` `3.0.2`
- `frida-ps` `17.9.6`
- `adb`
- `java`

## When to Prefer the Built-in Scripts

The following flows are high-frequency and error-prone in their parameters, so prefer the skill's built-in scripts:

- One-shot `jadx + apktool` extraction with summary output: `scripts/decode.ps1`
- Frida device checks, process listing, spawn/attach injection: `scripts/frida-run.ps1`
- Rebuild, align, sign, and install APK: `scripts/rebuild-sign-install.ps1`
- Quickly extract key Manifest components and permissions: `scripts/manifest-summary.ps1`

The following one-liner commands stay as direct invocations and are not wrapped:

- `adb devices`
- `adb logcat`
- `frida-ps -U`
- `jadx --version`
- `apktool --version`

## Built-in Scripts

### `scripts/decode.ps1`

Purpose:

- Runs `jadx` and `apktool` uniformly
- Creates the task output directory next to the original APK by default
- Outputs summaries such as `package`, `java_files`, `smali_dirs`, `so_files`
- Tolerates partial `jadx` decompilation errors when usable artifacts still exist

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\decode.ps1" -ApkPath "D:\DOWNLOAD\app.apk" -Clean
pwsh -File "<skill-root>\apk-reverse\scripts\decode.ps1" -ApkPath "D:\DOWNLOAD\app.apk" -Name demo -SkipJadx
```

### `scripts/frida-run.ps1`

Purpose:

- Unified entry for Frida devices, processes, and spawn/attach
- Avoids confusing `-f`, `-n`, `-U` when writing parameters by hand

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -ListDevices
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -Usb -ListProcesses
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -Usb -Spawn -Package com.example.app -ScriptPath "D:\hooks\test.js"
```

### `scripts/rebuild-sign-install.ps1`

Purpose:

- Rebuild the APK with `apktool b`
- Align with `zipalign`
- Sign and verify with `apksigner`
- Optional direct `adb install`

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "C:\work\apktool_out" -Clean
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "C:\work\apktool_out" -Install -Reinstall -DeviceSerial "127.0.0.1:7555"
```

Notes:

- Generates and reuses a debug keystore by default
- Outputs to the same directory as `ProjectDir` by default so results sit alongside the original package and unpacked directory

### `scripts/manifest-summary.ps1`

Purpose:

- Extract the package name
- List permissions
- List activities/services/receivers/providers
- Mark the main launcher activity

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\manifest-summary.ps1" -ManifestPath "C:\work\apktool_out\AndroidManifest.xml"
```

If you need to analyze `.so` files such as `lib/arm64-v8a/*.so` or `lib/armeabi-v7a/*.so`, also use:

- `ida-reverse`
- `radare2`

## Tool Division of Labor

### `jadx`

Use for:

- Java decompilation and reading
- Searching package names, class names, and method names
- Understanding the APK from high-level logic first

Common commands:

```bash
jadx -d jadx_out app.apk
jadx --single-class com.example.LoginActivity -d jadx_out app.apk
jadx --deobf -d jadx_out app.apk
```

### `JEB Pro` (optional commercial tool)

Use for:

- Cross-validation and deep decompilation of Android DEX / APK / ARM
- Supplementing static analysis when JADX output is incomplete or heavily obfuscated
- Second-toolchain verification of classes, methods, and call relationships for the same target

Boundaries:

- JEB Pro is commercial software; the user MUST obtain and install a valid license themselves. This package will not download, crack, or circumvent licenses.
- Only invoke JEB when `tool-index` confirms it is available on this machine; otherwise continue with `jadx`, `apktool`, Ghidra, IDA, or radare2.
- Third-party JEB MCP bridges are not dependencies of this package. Before installing, you MUST review source code, permissions, network behavior, and versions per `../ops/skill-supply-chain.md`, and only register after explicit user confirmation.

### `apktool`

Use for:

- Unpacking APKs
- Viewing and modifying `AndroidManifest.xml`
- Viewing and modifying smali
- Rebuilding APKs

Common commands:

```bash
apktool d app.apk -o apktool_out
apktool b apktool_out -o rebuilt.apk
```

### `frida`

Use for:

- Dynamically observing Java method calls
- Hooking native exported functions
- Bypassing root detection, certificate validation, and debugger detection

Common commands:

```bash
frida-ps -U
frida -U -f com.example.app -l hook.js
frida-trace -U -f com.example.app -j '*!*certificate*'
```

### `adb`

Use for:

- Device connection
- Installing APKs
- Viewing logs
- Pulling files

Common commands:

```bash
adb devices
adb install -r app.apk
adb shell pm list packages
adb logcat
adb pull /data/local/tmp/file .
```

## Recommended Workflow

### 1. Triage

First determine the APK's overall composition; don't rush into patching or hooking.

Recommended actions:

1. Export Java code with `jadx -d jadx_out app.apk`
2. Export smali and resources with `apktool d app.apk -o apktool_out`
3. Then inspect:
   - `AndroidManifest.xml`
   - Main `package`
   - `application`, `activity`, `service`, `receiver`
   - Whether `lib/` contains `.so` files

### 2. Java Logic Inspection

Read from `jadx_out` first:

- `MainActivity`
- `Application`
- Classes related to login, networking, encryption, and risk control
- Third-party SDK initialization classes

Common keywords:

- `login`
- `sign`
- `encrypt`
- `cipher`
- `token`
- `root`
- `certificate`
- `trust`
- `okhttp`
- `retrofit`
- `webview`

If the Java code is readable, locate the business logic here first.

### 3. Smali and Resource Layer Confirmation

When `jadx` results are incomplete, heavily obfuscated, or an actual patch is needed, switch to `apktool_out`:

- Inspect `smali*/`
- Inspect `res/values/strings.xml`
- Inspect `AndroidManifest.xml`

Prioritize patching:

- `android:exported`
- Debug flags
- Root detection return values
- Login verification logic
- Certificate validation branches

### 4. Rebuild and Install

After modification:

```bash
apktool b apktool_out -o rebuilt.apk
```

Or close the loop directly with the script:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "apktool_out" -Install -Reinstall -DeviceSerial "127.0.0.1:7555"
```

Notes:

- This skill only guarantees the `apktool` rebuild chain
- If the APK must be formally installed on a device, a signing step is usually required
- If the task reaches signing/alignment, bring in `apksigner` / `zipalign`

### 5. Dynamic Hooking

When static analysis is insufficient, use Frida:

- Hook login functions
- Hook key points in `OkHttp` / `Retrofit` / `WebView`
- Hook `javax.crypto` and `MessageDigest`
- Hook root detection functions
- Hook SSL pinning logic

Principles:

- Hook the Java layer first, then decide whether native hooking is needed
- Log arguments and return values first, then decide whether to modify return values

Recommendations:

- For simple one-off commands, use `frida-*` directly
- For injection flows that need stable reuse, prefer `scripts/frida-run.ps1`

### 6. Native `.so` Routing

If the APK contains critical `.so` files:

- Locate `lib/**/*.so` with `apktool` or `jadx`
- If you only need exported symbols, strings, or quick triage, use `radare2`
- For long-term deep analysis, decompilation, renaming, and type recovery, use `ida-reverse`

Switch to native analysis quickly when you see these signals:

- The Java layer is only a JNI wrapper
- Core signing logic is not in Java
- Critical logic disappears after `System.loadLibrary()`
- Certificate validation/risk control lives in `.so`

## Output Requirements

The final output MUST at least cover:

- Entry components and key classes
- Whether the key logic is in Java, smali, or `.so`
- Confirmed sensitive points: login, signing, root, SSL, WebView, JNI
- If patched, describe what was changed
- If hooked, describe which class/method/exported function was hooked

## Prohibited Practices

- Do not blindly modify smali from the start
- Do not write hooks before reviewing the manifest and main entry
- Do not equate incomplete Java decompilation with "logic unanalyzable"
- Do not keep grinding on the Java layer when `.so` clearly carries the core logic

## Quick Command Cheat Sheet

```bash
# Decompile Java
jadx -d jadx_out app.apk

# Unpack APK
apktool d app.apk -o apktool_out

# Rebuild APK
apktool b apktool_out -o rebuilt.apk

# Devices and processes
adb devices
frida-ps -U

# Spawn and inject
frida -U -f com.example.app -l hook.js
```

---

## Routing Context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exits**:
- Core logic in `.so` → `ida-reverse/` or `radare2/`
- Dynamic hooking/verification needed → `../reverse-engineering/tools-dynamic.md` (Frida section)
- General reverse engineering methodology → `../reverse-engineering/SKILL.md`

**Peer modules**: `reverse-engineering/` (.so analysis and advanced Frida usage)

---

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system. When a tool is missing, they do not fail directly — they automatically attempt an install.

### Automation Capability Boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| jadx | ✓ | GitHub Release ZIP | Automatically downloads and extracts to `%USERPROFILE%\Tools\jadx\` |
| apktool | ✓ | GitHub Release JAR + wrapper | Automatically downloads the jar and generates a bat in `%USERPROFILE%\Tools\apktool\` |
| JEB Pro | ✗ | Manual install with a valid license | Optional Android / ARM cross-validation tool; third-party MCP bridges require separate review |
| frida / frida-ps | ✓ | pip install frida-tools | Requires Python to be installed |
| adb | ✓ | winget / fallback path | Automatically installs Android Platform-Tools |
| zipalign | ✗ | Must manually install Android Build-Tools | `sdkmanager "build-tools;35.0.0"` |
| apksigner | ✗ | Must manually install Android Build-Tools | Same as above |

### Bootstrap Trigger Points

- `scripts/decode.ps1`: calls `bootstrap-reverse.ps1` automatically when jadx or apktool is missing
- `scripts/rebuild-sign-install.ps1`: calls bootstrap automatically when adb or apktool is missing
- `scripts/frida-run.ps1`: still a manual check for now (frida is usually already installed via pip)

### When Bootstrap Fails

If auto-install fails, the scripts raise a clear error with manual install links. Common causes:
- No network access (GitHub API / PyPI unreachable)
- winget unavailable (Windows version too old)
- Java not installed (apktool depends on the JDK)


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than only reading)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
