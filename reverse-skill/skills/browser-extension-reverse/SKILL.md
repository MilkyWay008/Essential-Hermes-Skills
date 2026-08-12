---
name: browser-extension-reverse
description: Use for authorized reverse engineering of browser extensions (Chrome/Firefox) including manifest analysis, background workers, and extension-based credential or traffic logic recovery.
---

# Browser Extension Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md`
2. `NOW`: Confirm the target is a **browser extension** (crx/xpi/unpacked directory), not ordinary web page JS (ordinary → `../js-reverse/`)
3. `NEXT`: Unpack the extension; read the manifest
4. `ACT`: Permission surface → background scripts → network/storage hooks

## Applicable Scenarios

- Chrome/Edge MV2/MV3 extension analysis
- Firefox extensions
- Malicious extension IOC and supply-chain extension poisoning investigations
- Recovery of signing/encryption/proxy logic implemented by extensions

## Workflow

### 1. Package

```text
□ Unpack crx / pull extension directory from profile
□ manifest.json: permissions, host_permissions, background, content_scripts
□ Assess over-permissions (<all_urls>, webRequest, debugger)
```

### 2. Logic

```text
□ service_worker / background entry point
□ content_script injection points and world (isolated)
□ chrome.storage / IndexedDB keys
□ Same as `js-reverse`: observe network and message passing (runtime.sendMessage)
```

### 3. Dynamic

```text
□ Load unpacked directory in developer mode
□ Check chrome://extensions for errors
□ Attach DevTools to the service worker
□ Frida / browser CDP when needed (jshookmcp)
```

## Toolchain

| Tool | Purpose |
|------|------|
| Unpack/jq | manifest |
| Chrome DevTools | worker debugging |
| js-reverse toolchain | deep JS |
| YARA | malicious extension rules |

> **Tool fallback:** Frida / jshookmcp are manifest-installable (pip / npm). If missing: **objection** (wraps Frida) or Hermes native `browser_*` tools for CDP observation; heavy JS obfuscation → `js-reverse` module (see `../RULES.md` equivalent-tools table).

## References

- `references/extension-analysis.md`
- field-journal entries related to extension recovery
- `../js-reverse/` `../malware-analysis/`

## Routing Context

**Upstream**: MASTER R30  
**Downstream**: heavily obfuscated JS → `js-reverse`; poisoning investigation → supply-chain / malware

## Task Completion Self-Check

- [ ] Are the permission surface and entry scripts listed?
- [ ] Were the critical data flows recovered?
- [ ] Checklist?
