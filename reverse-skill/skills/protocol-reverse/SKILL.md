---
name: protocol-reverse
description: Use for authorized reverse engineering of custom binary protocols, Protobuf/gRPC, WebSocket frames, and PCAP-driven protocol recovery.
---

# Protocol Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm authorization and routine-operation boundaries
2. `NOW`: Confirm whether the task is **protocol/traffic/serialization-format** reversing (if it is purely Web parameter signing → route to `js-reverse/`)
3. `NOW`: If there will be network interaction with the target → run `../scripts/case-init.ps1` to complete scope; do not ACT on the target while `auth` is not granted
4. `NEXT`: Read `../tool-index.md`; bootstrap missing tools (tshark/wireshark etc. may need manual install)
5. `ACT`: Enter Phase 1 of the workflow and produce a frame-layout or message-dictionary draft

## Applicable Scenarios

- Custom TCP/UDP binary protocols
- Protobuf / gRPC / FlatBuffers / MessagePack
- WebSocket / MQTT / private RPC
- Recovering fields and state machines from PCAP / PCAPNG
- Client-server validation, sequence numbers, encrypted frame headers

## When Not to Use This Skill

| Situation | Go to |
|------|------|
| HTTP-only parameter signing / JS encryption | `js-reverse/` |
| TLS certificate issues only | `pentest-tools/` or a browser proxy |
| Deep-diving an in-firmware protocol stack + emulation | `firmware-pentest/` first, then back to this skill |

## Workflow

### Phase 1 — Capture and Triage

```text
□ 拿到样本：PCAP / 代理导出 / 客户端日志 / 二进制
□ 标记方向：C→S / S→C；是否有握手、心跳、重连
□ 固定头？魔数？长度字段？TLV？定长？
□ 是否压缩（zlib/gzip/lz4）或加密（AES/ChaCha 帧内）
□ tshark -r cap.pcap -T fields -e frame.number -e ip.src -e tcp.payload
```

### Phase 2 — Frame Layout Recovery

```text
□ 对齐多个同类消息，找不变字节 / 自增序列号
□ 长度字段：大端/小端、含头/不含头
□ 校验：CRC16/32、checksum、HMAC 位置
□ 画出状态机：Connect → Auth → Ready → Request/Response → Close
□ 工具：Wireshark 自定义 dissector 草稿 / ImHex / 010 Editor 模板 / Kaitai Struct
```

### Phase 3 — Serialization and Encryption

```text
□ Protobuf：.proto 恢复（blackboxprotobuf / pbtk / protoc --decode_raw）
□ gRPC：HTTP/2 headers + protobuf body
□ 加密：找密钥派生（客户端 so/dll/JS）→ 联合 ida-reverse / js-reverse / apk-reverse
□ 重放：仅在授权 scope 内；先无害字段再敏感操作
```

### Phase 4 — Deliverables

```text
MUST 产出：
- 消息类型表（name / opcode / fields）
- 至少 1 条可复现的解码命令或脚本
- Evidence：原始 hex 摘录 + 解码结果（脱敏）
```

## Toolchain

| Tool | Required | Purpose | Bootstrap |
|------|------|------|------|
| tshark / Wireshark | Highly recommended | PCAP parsing | Manual / winget |
| Python3 | Yes | Decoding scripts | System |
| blackboxprotobuf | Optional | Unknown protobuf | pip |
| ImHex / 010 | Optional | Structure templates | Manual |
| IDA / r2 / Ghidra | On demand | Client serialization functions | See the corresponding skill |

## References

- `references/protocol-workflow.md` — frame layout and Protobuf quick reference
- Related: `../ida-reverse/` `../js-reverse/` `../firmware-pentest/` `../pentest-tools/`

## Routing Context

**Upstream**: `MASTER-ROUTING` R21 · `routing.md`  
**Downstream**: need client algorithms → `ida-reverse`/`js-reverse`; need replay for exploitation → `pentest-tools`/`api-security`  
**Peers**: `malware-analysis` (C2 protocols), `digital-forensics` (traffic forensics)

## Task Completion Self-Check

- [ ] Was the message layout or state machine recovered (rather than just pasting hex)?
- [ ] Is there a reproducible decoding command?
- [ ] Was scope respected / sensitive data redacted?
- [ ] Was the field-journal / report Checklist written back?
