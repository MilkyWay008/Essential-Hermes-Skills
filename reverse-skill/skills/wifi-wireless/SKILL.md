---
name: wifi-wireless
description: Use for authorized wireless security assessment including Wi-Fi capture, WPA handshake analysis, rogue AP detection research, and lab-only deauth testing.
---

# Wi-Fi / Wireless Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md`; **wireless attacks carry high legal risk** — written authorization and physical scope are mandatory
2. `NOW`: Write the scope clearly: target SSID/BSSID/venue; scanning neighbor networks is forbidden
3. `NEXT`: Confirm the adapter's monitor mode capability
4. `ACT`: Reconnaissance → capture → analysis (lab-first)

## Applicable Scenarios

- Authorized Wi-Fi security assessment
- WPA/WPA2 handshake capture and offline assessment
- Rogue AP / phishing hotspot detection research
- Enterprise wireless isolation and portal security

## Workflow

```text
□ Enter monitor mode with iwconfig / airmon-ng (lawful environment)
□ Lock onto the target BSSID channel with airodump-ng
□ Handshake or PMKID capture (target only)
□ Offline password policy assessment with hashcat/aircrack
□ Report: encryption type, isolation, portal bypass, recommendations
```

> **HARDWARE REQUIREMENT**: requires a Linux host (Kali preferred) WITH a wireless adapter that supports monitor mode. On Windows: stop and ask the user — this skill cannot run without the hardware; advise WSL2 does NOT expose the wireless adapter to monitor mode.

## Toolchain

| Tool | Purpose |
|------|------|
| aircrack-ng suite | capture/assessment |
| hcxdumptool / hcxtools | PMKID |
| hashcat | password assessment |
| Wireshark | management frame analysis |

## References

- `references/wireless-lab-rules.md`
- `../pentest-tools/` `../attack-chain/` (proximity section)

## Routing Context

**Upstream**: MASTER R29  
**MUST NOT**: unauthorized deauth, operating against non-target client networks

## Task Completion Self-Check

- [ ] Was the target BSSID strictly locked down?
- [ ] Did the report include hardening recommendations?
- [ ] Checklist?
