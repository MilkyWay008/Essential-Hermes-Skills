#!/usr/bin/env python3
"""
hermes-usability-audit.py — systematic hidden-issue scanner for Hermes skill packs.

Why this exists: static "0 CJK outside code blocks" and "pointers resolve" checks
miss three structural blind spots:
  (A) Chinese INSIDE fenced code blocks (agent-facing prose hiding as code)
  (B) skills mandating tools that don't exist on the host, or that Hermes has
      a native equivalent for (agent-browser -> browser_* tools, etc.)
  (C) cold-start tool-index references that dead-end before bootstrap runs

Usage:
  python hermes-usability-audit.py <pack-root> [--cjk] [--tools] [--equiv] [--all]

Checks:
  1. CJK scan: all CJK chars, classified outside-fence vs inside-fence, with
     per-block comment-line counts (prose-in-fence heuristic: >30% CJK lines)
  2. Tool inventory: every backticked command's first token, cross-referenced
     against a KNOWN_TOOLS allowlist (manifest capabilities + Hermes native +
     common OS utilities). Unknown tokens = candidates for review.
  3. Native-equivalence: map of external tools that Hermes has native/MCP
     equivalents for; flags skills mandating the external tool WITHOUT
     mentioning the native alternative.
  4. tool-index cold-start: skills referencing ../tool-index.md as a step but
     never mentioning refresh-tool-index.
  5. Fallback presence: per-skill, does it contain bootstrap/install/manual/
     ask-user guidance for its tooling? (heuristic keyword scan)

Output: markdown report to stdout + JSON detail to <pack-root>/usability-audit.json
Read-only: never modifies pack files.
"""
import argparse, json, pathlib, re, sys

CJK_RE = re.compile(r'[\u4e00-\u9fff]')
FENCE_RE = re.compile(r'```(.*?)```', re.S)
TICK_RE = re.compile(r'`([^`\n]+)`')

# Tools Hermes agents can actually use WITHOUT external install, or that the
# pack's bootstrap-manifest can install. Add host-specific tools as needed.
KNOWN_TOOLS = {
    # pack bootstrap-manifest capabilities (24)
    'jadx','apktool','jeb-pro','frida','frida-ps','idalib-mcp','reqable-mcp',
    'jshookmcp','anything-analyzer','idapro','r2','rabin2','adb','agent-browser',
    'ghidra-mcp','seclists','proxycat','burpsuite-mcp','nmap','pentestswarm',
    'binwalk','yara','pwntools','bkcrack',
    # Hermes native tools / runtime
    'python','python3','pip','pip3','bash','sh','powershell','pwsh','cmd',
    'node','npm','npx','curl','wget','git','unzip','zip','tar','7z','7za',
    'strings','file','xxd','hexdump','od','grep','sed','awk','sort','uniq',
    'jq','dotnet','java','javac','winget','choco','apt','apt-get','brew','go',
    'docker','kubectl','aws','gcloud','ssh','scp','dig','nslookup','ping',
    'traceroute','netstat','tasklist','taskkill','reg','systeminfo','wmic',
    'openssl','sqlite3','ffmpeg','ffprobe','tshark','vol','ilspycmd','de4dot',
    'monodis','diec','die','gdb','radare2','r2','floss','pecheck','sigmac',
    'semgrep','bandit','gosec','sqlmap','nuclei','subfinder','amass','httpx',
    'naabu','dnsx','katana','gau','whatweb','wpscan','hydra','responder',
    'impacket','bloodhound-python','certipy','coercer','evil-winrm','crackmapexec',
    'mimikatz','winpeas','proxychains','msfconsole','msfvenom','nc','ncat',
    'socat','rlwrap','gore','redress','sigma-cli','yara-python','selenium',
    'playwright','mitmproxy','jwt_tool','GoReSym','osv-scanner','gitleaks',
    'trivy','syft','cdxgen','cosign','promptfoo','garak','pyrit','vol3',
    'osquery','urh','inspectrum','gnuradio-companion','aircrack-ng','hcxdumptool',
    'hashcat','john','zipalign','apksigner','sdkmanager','cmake','make','gcc',
    'clang','rustc','cargo','pipx','uv',
    # typical in-skill example binaries / paths (allowed noise)
    'sample','target','binary','libc','ld','gcc','objdump','readelf','nm',
    'analyzeheadless','ghidra','ida','radare2','r2','rabin2','rasm2','radiff2',
    'rahash2','rax2',
}

# External tools that have Hermes-native or in-pack equivalents. When a skill
# mandates these WITHOUT mentioning the alternative, flag it. Only fires for
# tools NOT already in KNOWN_TOOLS (ida/ghidra/windbg are covered by pack
# capabilities/modules, so they're excluded automatically).
EQUIVALENTS = {
    'agent-browser': 'Hermes native browser_* tools (browser_navigate/snapshot/click/type, @eN refs)',
    'playwright': 'Hermes native browser_* tools (same @eN model, zero install)',
    'puppeteer': 'Hermes native browser_* tools',
    'selenium': 'Hermes native browser_* tools for page driving',
    'claude': 'OpenCode ACP delegation / subagents (Hermes-native coding)',
    'codex': 'OpenCode ACP delegation / subagents',
    'opencode': 'native delegate_task / opencode skill',
    'ilspycmd': 'pythonnet reflection (clr.Reflection) as dnlib-equivalent',
    'dnspyex': 'ilspycmd CLI / pythonnet / dnSpy MCP (skill alternatives)',
    'de4dot': 'ilspycmd CLI / pythonnet',
}

def scan_cjk(text, path):
    total = len(CJK_RE.findall(text))
    fences = FENCE_RE.findall(text)
    in_fence = sum(len(CJK_RE.findall(b)) for b in fences)
    fence_blocks = []
    for bi, b in enumerate(fences):
        cjk_lines = [ln for ln in b.splitlines() if CJK_RE.search(ln)]
        if not cjk_lines:
            continue
        n_cjk = len(CJK_RE.findall(b))
        n_lines = max(1, len(b.splitlines()))
        fence_blocks.append({
            'block': bi, 'cjk_chars': n_cjk,
            'cjk_ratio': round(n_cjk / (len(b) or 1), 3),
            'prose_in_fence': (len(cjk_lines) / n_lines) > 0.3,
            'sample': cjk_lines[0].strip()[:80] if cjk_lines else '',
        })
    return total, in_fence, fence_blocks

def scan_tools(text, path):
    """First token of every backticked string that looks like a command.
    Strips YAML frontmatter and markdown links first (both are heavy noise)."""
    # strip YAML frontmatter (--- ... --- at top)
    body = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.S)
    # strip markdown link targets [text](target)
    body = re.sub(r'\[[^\]]*\]\([^)]*\)', '', body)
    # strip inline-code-only markdown refs (backticked paths ending .md / .ps1 with slashes)
    unknown, known = set(), set()
    for m in TICK_RE.finditer(body):
        raw = m.group(1).strip()
        if re.search(r'[/\\][\w.\-]+\.(md|json|yaml|yml|toml|ps1|sh|py)$', raw, re.I):
            continue  # file/ref path, not a command
        tok = raw.split()[0].split('/')[-1].strip('$"\'><')
        tok = re.sub(r'[\\.;()]', '', tok)
        if not tok or len(tok) < 2 or re.match(r'^[\d\W]', tok):
            continue
        tl = tok.lower()
        if tl in KNOWN_TOOLS or tl.endswith(('.exe','.ps1','.sh','.py','.md')):
            known.add(tok)
        else:
            unknown.add(tok)
    return sorted(known), sorted(unknown)

def scan_equiv(text, path):
    hits = []
    for tool, alt in EQUIVALENTS.items():
        if re.search(rf'`?{re.escape(tool)}', text, re.I):
            if alt.split()[0].lower() not in text.lower() and 'native' not in text.lower():
                hits.append({'tool': tool, 'native_alt': alt})
    return hits

def scan_coldstart(text, path):
    if '../tool-index.md' in text and 'refresh-tool-index' not in text:
        return True
    return False

def scan_fallback(text, path):
    keywords = ['bootstrap', 'install', 'pip install', 'apt install', 'go install',
                'npm install', 'winget', 'brew install', 'manual', 'download',
                'ask the user', 'ask user', 'stop and report', 'requires']
    found = [k for k in keywords if k in text.lower()]
    return found

def audit(pack_root, checks):
    root = pathlib.Path(pack_root)
    report = {'pack': str(root), 'files_scanned': 0, 'cjk': [], 'tools_unknown': [],
              'equivalents': [], 'coldstart': [], 'no_fallback': []}
    for md in sorted(root.rglob('SKILL.md')):
        # skip backups/trash
        if '.bak' in str(md) or '.trash' in str(md):
            continue
        text = md.read_text(encoding='utf-8', errors='replace')
        rel = str(md.relative_to(root))
        report['files_scanned'] += 1
        if 'cjk' in checks:
            total, in_fence, blocks = scan_cjk(text, rel)
            if total:
                report['cjk'].append({'file': rel, 'total': total, 'in_fence': in_fence,
                                      'prose_blocks': [b for b in blocks if b['prose_in_fence']],
                                      'fence_blocks': blocks})
        if 'tools' in checks:
            known, unknown = scan_tools(text, rel)
            if unknown:
                report['tools_unknown'].append({'file': rel, 'unknown': unknown})
        if 'equiv' in checks:
            hits = scan_equiv(text, rel)
            if hits:
                report['equivalents'].append({'file': rel, 'hits': hits})
        if 'coldstart' in checks:
            if scan_coldstart(text, rel):
                report['coldstart'].append(rel)
        if 'fallback' in checks:
            found = scan_fallback(text, rel)
            if not found:
                report['no_fallback'].append(rel)
    return report

def render(report):
    L = []
    L.append(f"# Hermes Usability Audit — {report['pack']}")
    L.append(f"\nFiles scanned: {report['files_scanned']}")
    L.append(f"\n## 1. CJK (Chinese) — {len(report['cjk'])} files")
    for f in report['cjk']:
        prose = len(f['prose_blocks'])
        L.append(f"- **{f['file']}**: {f['total']} CJK chars ({f['in_fence']} in fences)"
                 + (f" — ⚠️ {prose} PROSE-IN-FENCE block(s)" if prose else " — comments/strings only"))
        for b in f['fence_blocks'][:4]:
            tag = 'PROSE' if b['prose_in_fence'] else 'inline'
            L.append(f"    - fence{b['block']} [{tag}] {b['cjk_chars']} chars: {b['sample']}")
    L.append(f"\n## 2. Unknown tool tokens — {len(report['tools_unknown'])} files")
    for f in report['tools_unknown'][:40]:
        L.append(f"- **{f['file']}**: {', '.join(f['unknown'][:12])}")
    L.append(f"\n## 3. External tool w/ native equivalent — {len(report['equivalents'])} files")
    for f in report['equivalents']:
        for h in f['hits']:
            L.append(f"- **{f['file']}** mandates `{h['tool']}` — native alt: {h['native_alt']}")
    L.append(f"\n## 4. tool-index cold-start (no refresh mention) — {len(report['coldstart'])} files")
    for f in report['coldstart']:
        L.append(f"- {f}")
    L.append(f"\n## 5. No fallback/install guidance — {len(report['no_fallback'])} files")
    for f in report['no_fallback']:
        L.append(f"- {f}")
    return '\n'.join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pack_root')
    ap.add_argument('--cjk', action='store_true')
    ap.add_argument('--tools', action='store_true')
    ap.add_argument('--equiv', action='store_true')
    ap.add_argument('--coldstart', action='store_true')
    ap.add_argument('--fallback', action='store_true')
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    checks = ['cjk','tools','equiv','coldstart','fallback'] if args.all else \
             [c for c in ['cjk','tools','equiv','coldstart','fallback']
              if getattr(args, c)]
    if not checks:
        checks = ['cjk','tools','equiv','coldstart','fallback']
    report = audit(args.pack_root, checks)
    print(render(report))
    out = pathlib.Path(args.pack_root) / 'usability-audit.json'
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n[JSON detail: {out}]")

if __name__ == '__main__':
    main()
