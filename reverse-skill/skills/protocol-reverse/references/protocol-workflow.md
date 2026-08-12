# Protocol Reverse Cheatsheet

> Applies to: `protocol-reverse` skill · 2026-07-18

## Common Layout Patterns

| Pattern | Signature | Hint |
|------|------|------|
| Fixed-length header + body | First 2/4 bytes = length | Check whether header length is included |
| Magic number | Fixed `0xDEAD` etc. | Helps resync the stream |
| TLV | type-length-value repeats | The type enum is the message dictionary |
| Protobuf | varint field numbers | `protoc --decode_raw` |
| Encrypted frames | High entropy, no plaintext URLs | First look for the nonce/IV neighborhood |

## Minimal Python Skeleton

```python
import struct
def parse_frame(buf: bytes):
    magic, length, msg_type = struct.unpack_from(">IHI", buf, 0)
    body = buf[10:10+length]
    return {"magic": magic, "type": msg_type, "body": body}
```

## Extract TCP Payloads from PCAP

```bash
tshark -r cap.pcap -Y "tcp.port==4433" -T fields -e tcp.payload | head
```

