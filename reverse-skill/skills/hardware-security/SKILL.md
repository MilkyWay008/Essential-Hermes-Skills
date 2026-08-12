---
name: hardware-security
description: Use for authorized hardware and embedded interface security research including UART/JTAG discovery, debug pad triage, secure boot overview, and offline firmware extraction support.
---

# Hardware / Embedded Interface Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Confirm **physical-access authorization** and device ownership
2. `NOW`: ESD/power safety; read-only probing by default
3. `NEXT`: Coordinate with firmware-pentest for image analysis
4. `ACT`: Enclosure and debug interface identification → consoles → extraction

## Applicable Scenarios

- UART / JTAG / SWD debug port discovery
- Boot logs, root shell, boot interruption
- Flash extraction during teardown
- Feasibility assessment of secure boot / encrypted Flash (non-destructive first)

## Workflow

```text
□ Disassemble the authorized device; photograph and label test points
□ Use a multimeter to locate GND/VCC/TX/RX; logic levels 1.8/3.3/5V
□ USB-TTL read-only logging; record baud rate
□ JTAG: enumerate IDCODE; assess whether locked
□ Extract image → hand off to firmware-pentest / ghidra
```

> **Physical hardware + human required**: This skill requires PHYSICAL hardware + a human. The agent's job: identify the interface (UART/JTAG/SWD), give the user exact wiring + command steps, ask the user to perform the physical connection and report back. Never attempt to skip hardware steps.

## Toolchain

| Tool | Purpose |
|------|------|
| USB-TTL / logic analyzer | UART |
| J-Link / CMSIS-DAP | Debug |
| bus pirate / flipper (lab) | Multi-protocol |
| binwalk / flashrom | Extraction |

> **Tool fallback:** binwalk is manifest-installable (winget ReFirmLabs v2) or `cargo install binwalk` (v3, manual). If missing: **unblob** (pip) as equivalent. Ghidra/radare2 via `ghidra-mcp`/`r2` (see `../RULES.md` equivalent-tools table).

## References

- `references/debug-interface-triage.md`
- `../firmware-pentest/` `../ot-ics/`

## Routing Context

**Upstream**: MASTER R34  
**MUST NOT**: Disassemble without authorization / damage others' devices

## Task Completion Self-Check

- [ ] Were interface levels and pinout diagram recorded?
- [ ] Was the image hash preserved?
- [ ] Checklist?
