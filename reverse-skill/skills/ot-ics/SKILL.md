---
name: ot-ics
description: Use for authorized OT/ICS security assessment covering Purdue model zoning, PLC/SCADA exposure, industrial protocol discovery, and safe passive-first evaluation.
---

# OT / ICS Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md` — **misoperation in industrial control environments can cause physical harm**
2. `NOW`: Written authorization must clearly specify: sites, network segments, and whether active scanning / register writes are permitted
3. `NOW`: case-init; default to **passive-first**; no PLC write operations before `ready_for_act`
4. `NEXT`: tool-index; most ICS tools need manual install and an isolated lab network
5. `ACT`: asset and zone identification → exposure surface → read-only verification

## Applicable Scenarios

- Industrial control / SCADA / DCS security assessment (authorized)
- Purdue model zoning and cross-zone channels
- Exposure of protocols such as Modbus/DNP3/S7/EtherNet/IP
- Engineering workstations, HMI, historians, jump hosts
- IT/OT convergence boundaries (firewall rules, unidirectional gateways)

## Safety Iron Rules (MUST)

```text
MUST NOT 在未明确允许时：
- 对 PLC 写线圈/寄存器
- 全网高速率扫描生产 OT
- 中断安全仪表系统（SIS）相关路径
优先：只读识别、流量镜像、离线固件/配置分析
```

## Workflow

### Phase 1 — Zoning and Assets

```text
□ Purdue L0–L5 草图：现场设备 → 控制 → 监督 → 站点 DMZ → 企业
□ 资产清单：PLC/RTU/HMI/工程师站/历史库/Jump host
□ 协议与端口基线（仅授权网段）
```

### Phase 2 — Passive and Read-Only

```text
□ SPAN/镜像 PCAP → protocol-reverse / Wireshark 工控解析器
□ 配置与工程文件离线审计（TIA/RSLogix 导出等）
□ 默认口令与明文协议（Modbus 无认证）记录为 Finding，不写盘改值
```

### Phase 3 — Limited Active (Authorized Only)

```text
□ 低速识别，维护窗口
□ 只读功能码优先
□ 每步 Evidence；异常立即停止并通报
```

### Phase 4 — Firmware/Patch Surface

```text
□ 控制器固件版本 → CVE 映射（不盲刷固件）
□ 联合 firmware-pentest 做离线镜像分析
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
- `../firmware-pentest/` `../protocol-reverse/` `../network` via pentest-tools

## Routing Context

**Upstream**: MASTER R28  
**Downstream**: firmware deep-dive `firmware-pentest`; protocols `protocol-reverse`; IT lateral movement `windows-ad`/`attack-chain`  
**Peers**: do not attack OT with generic web scanning of default parameters

## Task Completion Self-Check

- [ ] Did I default to passive/read-only and record the authorization boundary?
- [ ] Did I avoid write operations on control loops (unless explicitly permitted)?
- [ ] Do the Findings include physical/process impact descriptions?
- [ ] Checklist / journal updated?
