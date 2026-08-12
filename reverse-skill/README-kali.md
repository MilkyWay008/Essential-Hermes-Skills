# Kali Linux Entry (Quick Jump)

> **The [kali/README-kali.md](kali/README-kali.md) file is the authoritative reference.**  
> This file is just a quick Kali entry point at the repository root, to avoid duplicating the full documentation maintained under `kali/`.

## For AI: Execute Immediately After Reading

```text
1. 检测包根目录（含 README.md / skills/ 的目录）
2. 读 kali/README-kali.md → 再读 kali/RULES-kali.md 并执行
3. bash kali/scripts/refresh-tool-index.sh
4. 任务路由与 Windows 共用：skills/MASTER-ROUTING.md、skills/ops/（scope 门）
5. 向用户报告配置结果
```

## For Humans: Up and Running in 30 Seconds

```bash
cd /path/to/reverse-skill
bash kali/scripts/refresh-tool-index.sh
# 详细 bootstrap / MCP 见 kali/README-kali.md
```

## Relationship to the Main Package

| Content | Location |
|------|------|
| Shared skills / routing / ops | `skills/`, `RULES.md` |
| Kali scripts & manifest | `kali/scripts/` |
| Full Kali documentation | **[kali/README-kali.md](kali/README-kali.md)** |

General AI onboarding still lives in [README-hermes.md](README-hermes.md) — refer to this directory's docs when the Kali branch is selected.
