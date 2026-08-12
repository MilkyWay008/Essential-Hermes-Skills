---
name: protocol-reverse
description: Use for authorized reverse engineering of custom binary protocols, Protobuf/gRPC, WebSocket frames, and PCAP-driven protocol recovery.
---

# Protocol Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-reverse.md` — confirm authorization and routine-operation boundaries
2. `NOW`: Confirm whether the task is **protocol/traffic/serialization-format** reversing (if it is purely Web parameter signing → route to `js-reverse/`)
3. `NOW`: If there will be network interaction with the target → run `../scripts/case-init.ps1` to complete scope; do not ACT on the target while `auth` is not granted
4. `NEXT`: Read `../tool-index.md`; bootstrap missing tools (tshark/wireshark etc. may need manual install) (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
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
□ Obtain samples: PCAP / proxy export / client logs / binaries
□ Mark direction: C→S / S→C; check for handshake, heartbeat, reconnect
□ Fixed header? Magic? Length field? TLV? Fixed-length?
□ Compressed (zlib/gzip/lz4) or encrypted (AES/ChaCha within frames)?
□ tshark -r cap.pcap -T fields -e frame.number -e ip.src -e tcp.payload
```

### Phase 2 — Frame Layout Recovery

```text
□ Align multiple same-type messages, find invariant bytes / incrementing sequence numbers
□ Length field: big/little endian, header included/excluded
□ Checksums: CRC16/32, checksum, HMAC locations
□ Draw the state machine: Connect → Auth → Ready → Request/Response → Close
□ Tools: Wireshark custom dissector draft / ImHex / 010 Editor templates / Kaitai Struct
```

### Phase 3 — Serialization and Encryption

```text
□ Protobuf: recover .proto (blackboxprotobuf / pbtk / protoc --decode_raw)
□ gRPC: HTTP/2 headers + protobuf body
□ Encryption: find key derivation (client so/dll/JS) → combine ida-reverse / js-reverse / apk-reverse
□ Replay: only within authorized scope; benign fields first, then sensitive operations
```

### Phase 4 — Deliverables

```text
MUST deliverables:
- Message type table (name / opcode / fields)
- At least 1 reproducible decode command or script
- Evidence: raw hex excerpts + decoded results (redacted)
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

**Upstream**: `MASTER-ROUTING` R21 · `../routing.md`  
**Downstream**: need client algorithms → `ida-reverse`/`js-reverse`; need replay for exploitation → `pentest-tools`/`api-security`  
**Peers**: `malware-analysis` (C2 protocols), `digital-forensics` (traffic forensics)

## Task Completion Self-Check

- [ ] Was the message layout or state machine recovered (rather than just pasting hex)?
- [ ] Is there a reproducible decoding command?
- [ ] Was scope respected / sensitive data redacted?
- [ ] Was the field-journal / report Checklist written back?
