# Cybersecurity Skills Router — Kali Linux Edition

> This directory is an optimization/adaptation layer for Kali Linux 2026.1, tuned specifically for the Kali 2026.1 release (kernel 6.18) from March 2026.
> The core knowledge base (skills/, CTF-Sandbox-Orchestrator/) is shared with the Windows edition; the Kali-specific README and Bash entry points must cover the same core capability names as Windows, while additionally providing Kali-native tools/MCP capabilities.  
> The root-level [README-kali.md](../README-kali.md) is only a quick jump; **this file is authoritative**.

---

## For AI: Execute Immediately After Reading

```text
1. 检测包根目录（含 skills/ 与 kali/ 的仓库根）
2. 读取 kali/RULES-kali.md → 全局注入与工具扫描
3. bash kali/scripts/refresh-tool-index.sh
4. 与主包共用作战链：
   - skills/MASTER-ROUTING.md（或 pwsh skills/scripts/master-route.ps1）
   - skills/scripts/case-init.ps1 → work/<case>/scope.md
   - auth.status=granted + network_profile 后才对目标 ACT
   - skills/ops/（证据链 / 角色 / 时间线 / IDENTITY）
5. 向用户报告配置结果
```

General agent onboarding lives at the repository root in [README_AI.md](../README_AI.md) — read this file when Kali is detected.

---

## 0. Relationship to the Windows Edition (Capability Name Alignment)

```text
项目根目录/
├── skills/                    # 共享：SKILL、routing、MASTER-ROUTING、ops、scripts、field-journal
├── CTF-Sandbox-Orchestrator/  # 共享：40+ CTF 子技能
├── kali/                      # ← 你在这里
│   ├── scripts/
│   │   ├── bootstrap-reverse.sh
│   │   ├── refresh-tool-index.sh
│   │   ├── bootstrap-manifest.json
│   │   └── lib/
│   │       └── tool-discovery.sh
│   ├── RULES-kali.md
│   └── README-kali.md
├── RULES.md                   # Windows 版规则
└── Readme.md                  # Windows 版说明
```


### 0.1 Alignment Principles

The Kali-specific entry point is not a copy of the Windows README; it is the **same set of core capability names + Kali-specific extras**:

- Windows: `skills/scripts/bootstrap-reverse.ps1`
- Kali: `kali/scripts/bootstrap-reverse.sh`
- Generic Linux/macOS: `skills/scripts/bootstrap-reverse.sh`

JEB Pro is a commercial tool that users license and install themselves; Reqable MCP uses the official pinned `reqable-mcp-server` version, but still requires a separately installed Reqable desktop client.

The Kali scripts must cover the core capability names from the Windows manifest, e.g. `jadx`, `apktool`, `frida`, `jshookmcp`, `anything-analyzer`, `idapro`, `r2`, `adb`, `ghidra-mcp`, `seclists`, `burpsuite-mcp`, `nmap`, `pentestswarm`; they may also additionally support Kali-native tools, e.g. `mcp-kali-server`, `metasploitmcp`, `hexstrike-ai`, `sstimap`, `xsstrike`, `netexec`, etc.

**Shared components** (no changes needed):
- All `SKILL.md`, `routing.md`, `MASTER-ROUTING.md`
- `skills/ops/` operational contracts (scope / evidence chain / roles / timeline)
- All `references/` knowledge bases
- `field-journal/` self-evolution mechanism
- Everything under `CTF-Sandbox-Orchestrator/`
- `docs-generator/`, `diagram-generator/`
- `skills/scripts/case-init.ps1`, `master-route.ps1` (invocable via pwsh)

**Kali-specific components**:
- Scripts are all bash (`.sh`)
- Package management via `apt`
- Path conventions are Linux-style (`/opt/`, `~/tools/`, `/usr/bin/`)
- Many tools ship preinstalled on Kali, so bootstrap logic is greatly simplified

---

## 1. Kali's Built-in Advantages

The following tools work **out of the box** on Kali 2026.1 (no bootstrap needed):

### Classic Preinstalled Tools

| Tool | Kali Package | Status |
|------|----------|------|
| nmap | nmap | Preinstalled |
| sqlmap | sqlmap | Preinstalled |
| hashcat | hashcat | Preinstalled |
| john | john | Preinstalled |
| hydra | hydra | Preinstalled |
| metasploit | metasploit-framework | Preinstalled |
| gobuster | gobuster | Preinstalled |
| ffuf | ffuf | Preinstalled |
| radare2 | radare2 | Preinstalled |
| binwalk | binwalk | Preinstalled |
| frida | python3-frida-tools | Preinstalled or pip |
| burpsuite | burpsuite | Preinstalled |
| wireshark | wireshark | Preinstalled |
| nikto | nikto | Preinstalled |
| wfuzz | wfuzz | Preinstalled |
| impacket | impacket-scripts | Preinstalled |
| netexec | netexec | Preinstalled |
| responder | responder | Preinstalled |
| aircrack-ng | aircrack-ng | Preinstalled |
| bloodhound | bloodhound | Installable via apt |
| ghidra | ghidra | Installable via apt |

### New Tools in Kali 2026.1 (March 2026)

| Tool | Package | Purpose |
|------|------|------|
| AdaptixC2 | adaptixc2 | Post-exploitation and adversary simulation framework |
| Atomic-Operator | atomic-operator | Cross-platform Atomic Red Team test execution |
| Fluxion | fluxion | WiFi security auditing and social engineering |
| GEF | gef | Modern enhanced debugging framework for GDB |
| MetasploitMCP | metasploitmcp | MCP server interface for Metasploit |
| SSTImap | sstimap | Automated server-side template injection detection and exploitation |
| WPProbe | wpprobe | Fast WordPress plugin enumeration |
| XSStrike | xsstrike | Advanced XSS scanner |

### New Tools in Kali 2025.4 (December 2025)

| Tool | Package | Purpose |
|------|------|------|
| evil-winrm-py | evil-winrm-py | Python-based WinRM remote command execution |
| hexstrike-ai | hexstrike-ai | AI MCP security automation platform (150+ tools) |
| bpf-linker | bpf-linker | BPF static linker |

### Kali-Native MCP Tools (Key Optimization)

| Tool | Package | Purpose | Install |
|------|------|------|------|
| mcp-kali-server | mcp-kali-server | Official Kali MCP — AI directly invokes terminal tools | `apt install mcp-kali-server` |
| MetasploitMCP | metasploitmcp | Metasploit MCP interface | `apt install metasploitmcp` |
| HexStrike AI | hexstrike-ai | MCP automation for 150+ security tools | `apt install hexstrike-ai` |

> **This is the biggest advantage of the Kali edition over the Windows edition**: all three MCP tools install directly via apt — no manual GitHub/npm/Docker configuration needed.

This means `bootstrap-reverse.sh` does far less work on Kali than on Windows.

---

## 2. Quick Start

### 2.0 One-Command Initialization (Recommended for Fresh Systems)

```bash
# 全新 Kali 2026.1 系统一键配置（需要 root）
sudo bash kali/scripts/quick-setup.sh

# 跳过系统更新（网络慢时）
sudo bash kali/scripts/quick-setup.sh --skip-update

# 最小安装（不装 AD/内网工具）
sudo bash kali/scripts/quick-setup.sh --minimal
```

The script automatically handles: system update → install new 2026.1 tools → configure native MCP → install reverse-engineering tools → refresh the index → output a report.

### 2.1 First-Time Setup

```bash
# 1. 进入项目根目录
cd /path/to/cybersecurity-skills-router

# 2. 给脚本加执行权限
chmod +x kali/scripts/*.sh kali/scripts/lib/*.sh

# 3. 刷新工具索引（检测本机工具状态）
bash kali/scripts/refresh-tool-index.sh

# 4. 查看结果
cat skills/tool-index.md
```

### 2.2 One-Command Setup of Kali-Native MCP (Highly Recommended)

```bash
# 安装 Kali 官方 MCP 三件套
bash kali/scripts/bootstrap-reverse.sh mcp-kali-server metasploitmcp hexstrike-ai

# 安装后 MCP 配置自动写入 ~/.claude/mcp.json
# 如果用 Kiro，手动复制到 ~/.kiro/settings/mcp.json
```

### 2.3 Installing the New 2026.1 Tools

```bash
# 全部新工具一键安装
bash kali/scripts/bootstrap-reverse.sh adaptixc2 atomic-operator sstimap xsstrike wpprobe fluxion gef

# AD/内网渗透套件
bash kali/scripts/bootstrap-reverse.sh coercer evil-winrm-py netexec responder bloodhound certipy
```

### 2.4 Installing Missing Tools

```bash
# 安装单个工具
bash kali/scripts/bootstrap-reverse.sh jadx

# 安装多个工具
bash kali/scripts/bootstrap-reverse.sh jadx apktool frida jshookmcp

# 安装并启动服务
bash kali/scripts/bootstrap-reverse.sh idapro --start-services
```

### 2.5 Letting AI Clients Route Automatically

Tell your AI client to read `kali/RULES-kali.md`; it will handle the global injection automatically.

---

## 3. Path Conventions

| Purpose | Kali Path |
|------|----------|
| Tool install directory | `~/tools/` or `/opt/` |
| jadx | `/opt/jadx/` or `~/tools/jadx/` |
| apktool | `/usr/local/bin/apktool` (apt) or `~/tools/apktool/` |
| Ghidra | `/opt/ghidra/` or `~/tools/ghidra/` |
| IDA Pro | `/opt/idapro/` (if a Linux version is available) |
| Android SDK | `~/Android/Sdk/` |
| SecLists | `/usr/share/seclists/` (apt) or `~/tools/SecLists/` |
| Node.js | `/usr/bin/node` (apt/nvm) |
| Python | `/usr/bin/python3` (bundled with the system) |
| MCP config | `~/.claude/mcp.json` or `~/.kiro/settings/mcp.json` |

---

## 4. Summary of Differences from the Windows Edition

| Dimension | Windows Edition | Kali Edition |
|------|-----------|---------|
| Scripting language | PowerShell (.ps1) | Bash (.sh) |
| Package management | winget / GitHub Release ZIP | apt / pip / npm / GitHub Release tar.gz |
| Path separator | `\` | `/` |
| Environment variable | `%USERPROFILE%` | `$HOME` |
| Preinstalled tools | Almost none | Many security tools preinstalled |
| IDA launch | `start.ps1` | Launch the Linux IDA manually; scripts only register/check MCP unless a launcher was added locally |
| MCP config path | `%USERPROFILE%\.claude\mcp.json` | `~/.claude/mcp.json` |
| Port checking | `TcpClient` | `nc -z` or `ss` |

---

## 5. Verification Checklist

```bash
# ─── 基础命令 ───
java -version
python3 --version
pip3 --version
node -v
npx -v

# ─── 逆向工具 ───
jadx --version
apktool --version
adb version
frida --version
r2 -v
gdb --version          # GEF 自动加载

# ─── 渗透工具（Kali 预装） ───
nmap --version
sqlmap --version
hashcat --version
hydra -h | head -1
msfconsole --version
gobuster version
ffuf -V
nuclei -version

# ─── Kali 2026.1 新工具 ───
sstimap -h 2>&1 | head -3
xsstrike -h 2>&1 | head -3
wpprobe --help 2>&1 | head -3
coercer -h 2>&1 | head -3
evil-winrm-py -h 2>&1 | head -3

# ─── AD/内网工具 ───
netexec --help 2>&1 | head -3
responder -h 2>&1 | head -3
certipy --version 2>&1 | head -1

# ─── Kali 原生 MCP ───
which kali-server-mcp && echo "mcp-kali-server OK"
which metasploitmcp && echo "metasploitmcp OK"
which hexstrike-ai && echo "hexstrike-ai OK"

# ─── 刷新工具索引 ───
bash kali/scripts/refresh-tool-index.sh

# ─── 检查 MCP 服务（如果已配置） ───
nc -z 127.0.0.1 5000 && echo "mcp-kali-server OK" || echo "mcp-kali-server offline"
nc -z 127.0.0.1 8085 && echo "metasploitmcp OK" || echo "metasploitmcp offline"
nc -z 127.0.0.1 13337 && echo "IDA MCP OK" || echo "IDA MCP offline"
nc -z 127.0.0.1 23816 && echo "anything-analyzer OK" || echo "anything-analyzer offline"
```

---

## 6. Frequently Asked Questions

### Q: The radare2 bundled with Kali is too old — what do I do?

```bash
# 用官方源安装最新版
bash kali/scripts/bootstrap-reverse.sh r2
# Kali 版默认优先 apt 安装/补齐 radare2；如需最新版可按平台文档改用 GitHub/source
```

### Q: I use Parrot OS / BlackArch — will this work?

Yes. The scripts check whether commands exist; they aren't tied to any specific distro. Only `apt`-based auto-installs may need to switch to `pacman` (BlackArch).

### Q: How do I set up the Linux version of IDA Pro?

Install IDA to `/opt/idapro/`, then adjust the `startScript` path for `idapro` in `kali/scripts/bootstrap-manifest.json`.

### Q: I want to use this system on both Windows and Kali

No problem. The `skills/` directory syncs via Git, and experience in `field-journal/` is shared across both. Just use `skills/scripts/*.ps1` on Windows and `kali/scripts/*.sh` on Kali when running scripts.
