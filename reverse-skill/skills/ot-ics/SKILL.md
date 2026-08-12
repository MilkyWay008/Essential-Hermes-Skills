---
name: ot-ics
description: Use for authorized OT/ICS security assessment covering Purdue model zoning, PLC/SCADA exposure, industrial protocol discovery, and safe passive-first evaluation.
---

# OT / ICS Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md` — **misoperation in industrial control environments can cause physical harm**
2. `NOW`: Written authorization must clearly specify: sites, network segments, and whether active scanning / register writes are permitted
3. `NOW`: run `../scripts/case-init.ps1`; default to **passive-first**; no PLC write operations before `ready_for_act`
4. `NEXT`: tool-index; most ICS tools need manual install and an isolated lab network (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
5. `ACT`: asset and zone identification → exposure surface → read-only verification

## Applicable Scenarios

- Industrial control / SCADA / DCS security assessment (authorized)
- Purdue model zoning and cross-zone channels
- Exposure of protocols such as Modbus/DNP3/S7/EtherNet/IP
- Engineering workstations, HMI, historians, jump hosts
- IT/OT convergence boundaries (firewall rules, unidirectional gateways)

## Safety Iron Rules (MUST)

```text
MUST NOT, when not explicitly permitted:
- Write PLC coils/registers
- High-rate scanning of production OT across the network
- Interrupt safety instrumented system (SIS) related paths
Prioritize: read-only identification, traffic mirroring, offline firmware/config analysis
```

## Workflow

### Phase 1 — Zoning and Assets

```text
□ Purdue L0–L5 sketch: field devices → control → supervision → site DMZ → enterprise
□ Asset inventory: PLC/RTU/HMI/engineering workstations/historians/jump hosts
□ Protocol and port baseline (authorized segments only)
```

### Phase 2 — Passive and Read-Only

```text
□ SPAN/mirrored PCAP → protocol-reverse / Wireshark ICS dissectors
□ Offline audit of configuration and engineering files (TIA/RSLogix exports, etc.)
□ Record default credentials and plaintext protocols (Modbus without auth) as Findings; do not write to disks or change values
```

### Phase 3 — Limited Active (Authorized Only)

```text
□ Low-rate identification, maintenance windows
□ Read-only function codes first
□ Evidence at every step; stop and report immediately on anomalies
```

### Phase 4 — Firmware/Patch Surface

```text
□ Controller firmware versions → CVE mapping (no blind firmware flashing)
□ Combine with firmware-pentest for offline image analysis
```

## Toolchain

| Tool | Purpose | Notes |
|------|------|------|
| Wireshark ICS dissectors | Passive parsing | Mirror traffic |
| Nmap NSE (restricted) | Identification | Rate and time windows |
| Claroty/Nozomi etc. | Asset discovery | Commercial/on-site |
| PLC vendor engineering software | Configuration audit | Offline first |
| binwalk / Ghidra | Firmware | Offline |

## References

- `references/ot-safe-assessment.md`
- `../firmware-pentest/` `../protocol-reverse/` `../pentest-tools/` via pentest-tools

## Routing Context

**Upstream**: MASTER R28  
**Downstream**: firmware deep-dive `firmware-pentest`; protocols `protocol-reverse`; IT lateral movement `windows-ad`/`attack-chain`  
**Peers**: do not attack OT with generic web scanning of default parameters

## Task Completion Self-Check

- [ ] Did I default to passive/read-only and record the authorization boundary?
- [ ] Did I avoid write operations on control loops (unless explicitly permitted)?
- [ ] Do the Findings include physical/process impact descriptions?
- [ ] Checklist / journal updated?
