---
name: radio-sdr
description: Use for authorized RF/SDR security research including signal identification, replay feasibility study in shielded labs, and wireless protocol analysis outside classic Wi-Fi.
---

# RF / SDR Security Research

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: **Spectrum use and transmission are strictly regulated by law**; only authorized bands/shielded rooms/experimental targets
2. `NOW`: Write the scope clearly: devices, bands, whether transmission is allowed (receive-only by default)
3. `ACT`: Receive-only identification → demodulation analysis → lab reproduction assessment

## Applicable Scenarios

- Non-Wi-Fi RF such as wireless remotes/sensors (authorized)
- Protocol research on ADS-B/remotes, etc. (lawful reception)
- Division of labor with wifi-wireless: this skill covers **general-purpose SDR RF**; Wi-Fi attacks/defense go through R29

## Workflow

```text
□ Confirm regulations and licensing
□ Receive-only: identify center frequency and modulation
□ GNU Radio / URH analysis
□ Replay only in a shielded room with written permission
□ Conclusions focus on: whether unauthorized control is possible / hardening recommendations
```

## Toolchain

| Tool | Purpose |
|------|------|
| RTL-SDR / HackRF (compliant) | TX/RX hardware |
| URH / GNU Radio | analysis |
| Inspectrum | signals |

## References

- `references/sdr-lab-rules.md`
- `../wifi-wireless/` `../ot-ics/` `../hardware-security/`

## Routing Context

**Upstream**: MASTER R38  
**MUST NOT**: interfere with public communications, unauthorized transmission

## Task Completion Self-Check

- [ ] Is receive-only the default and were regulatory boundaries documented?
- [ ] Checklist?
