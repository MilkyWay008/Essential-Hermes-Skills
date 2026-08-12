# Attack Chain Playbook Cheatsheet

> Pick the matching playbook by target type; each playbook defines the standard path from initial access to goal achievement.

---

## Playbook 1: External Web App → Domain Controller

```
1. Subdomain enumeration + port scanning
2. Web fingerprinting → find known-vulnerable components
3. Exploit to get Webshell / RCE
4. Internal network recon (ipconfig/ifconfig, arp, net user)
5. Set up tunneling (frp/chisel/ssh)
6. Internal scan (live hosts, open ports)
7. Credential harvesting (mimikatz/hashdump/config files)
8. Lateral movement (PTH/WMI/PsExec)
9. Domain recon (BloodHound)
10. Domain privilege escalation (Kerberoasting/DCSync/constrained delegation)
11. Obtain domain controller access
```

**Key toolchain**: subfinder → httpx → nuclei → sqlmap/sstimap → frp → nmap → mimikatz → crackmapexec → bloodhound → certipy

---

## Playbook 2: Phishing → Internal Network Penetration

```
1. Recon on target employees (LinkedIn/Maimai)
2. Craft phishing emails (forged sender/legitimate subject)
3. Build payloads (macro docs/LNK/ISO/HTML smuggling)
4. Send phishing emails
5. Wait for callback (C2 beacon)
6. Local recon + privilege escalation
7. Credential extraction
8. Lateral movement
9. Persistence
10. Goal achieved
```

**Key toolchain**: theHarvester → gophish → msfvenom/cobalt-strike → mimikatz → bloodhound

---

## Playbook 3: Proximity Penetration → Internal Network

```
1. Physical recon (WiFi signals, access control types, USB ports)
2. WiFi attack (Fluxion rogue AP / WPA cracking)
   or BadUSB implant (Rubber Ducky keyboard injection)
   or network implant (Raspberry Pi / LAN Turtle)
3. Get an internal network foothold
4. Internal scan
5. Continue with Playbook 1 steps 5-11
```

**Key toolchain**: fluxion/aircrack-ng → rubber-ducky → frp → nmap → crackmapexec

---

## Playbook 4: Cloud Environment Penetration

```
1. Cloud asset discovery (subdomains → CNAME → cloud provider)
2. Storage bucket enumeration (S3/OSS/Blob public access)
3. SSRF → cloud metadata (169.254.169.254)
4. Obtain temporary credentials (AK/SK/Token)
5. Cloud API enumeration (IAM/EC2/Lambda/RDS)
6. Privilege escalation (PassRole/AssumeRole)
7. Lateral movement (cross-account/cross-region)
8. Data exfiltration
```

**Key toolchain**: subfinder → nuclei(ssrf) → aws-cli → pacu → ScoutSuite

---

## Playbook 5: Bug Bounty / SRC Quick Wins

```
1. Asset collection (subdomains + ports + JS files)
2. Fingerprinting → quick validation of known vulns (nuclei)
3. Parameter discovery (arjun/paramspider)
4. Test category by category:
   - IDOR/privilege escalation (change ID/change role)
   - SSRF (internal probing/cloud metadata)
   - SQL injection (sqlmap)
   - XSS (xsstrike)
   - File upload (bypass detection)
   - Logic flaws (payment/CAPTCHA/password reset)
5. Write PoC + submit report
```

**Key toolchain**: subfinder → httpx → nuclei → arjun → sqlmap → xsstrike → burpsuite

---

## Playbook 6: AD CS Certificate Attacks

```
1. Discover AD CS services (certipy find)
2. Identify vulnerable templates (ESC1-ESC8)
3. Request a malicious certificate
4. Authenticate as the target user with the certificate
5. Obtain NTLM hash or TGT
6. DCSync to export all credentials
```

**Key toolchain**: certipy → rubeus → mimikatz → secretsdump

---

## Generic Decision Matrix

| Current state | Next priority |
|---------|-------------|
| Only have the target domain | Subdomain enumeration → port scan → web fingerprint |
| Have a web vuln | Get a shell → internal recon |
| Have a low-privilege shell | Privilege escalation → credential extraction |
| Have one internal machine | Tunnel → internal scan → lateral |
| Have domain user credentials | BloodHound → find attack paths |
| Have domain admin hash | DCSync → Golden Ticket |
| Have cloud AK/SK | Enumerate privileges → escalate → data access |
| Phishing callback | Local privesc → credentials → lateral |
| Proximity access | Internal scan → same as above |

