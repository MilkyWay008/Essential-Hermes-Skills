# zip-dist.ps1 - build a clean release zip from git-tracked files only
# Usage:
#   powershell -File scripts/zip-dist.ps1 [-OutPath ..\reverse-skill-dist.zip]
# Why git ls-files? The working tree contains untracked junk that must never
# ship: reports/ (un-desensitized pentest samples - anti-leak policy), .trash/,
# *.bak backups. `git archive` / `git ls-files` exclude all of it by
# construction. If you want the sample CTF report, copy it in deliberately.
param(
    [string]$OutPath = ''
)

$ErrorActionPreference = 'Stop'

# locate enclosing git work tree; pack root = <repo>/reverse-skill (fixed layout)
$ScriptDir = $PSScriptRoot
$GitRoot = & git -C $ScriptDir rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $GitRoot) {
    Write-Error "pack is not inside a git repo - zip-dist only builds from git-tracked files."
}
$RepoRoot = Join-Path $GitRoot 'reverse-skill'
if (-not (Test-Path $RepoRoot)) {
    Write-Error "expected pack at '$RepoRoot' (repo layout: <repo>/reverse-skill)."
}

if (-not $OutPath) {
    $OutPath = Join-Path (Split-Path -Parent $RepoRoot) 'reverse-skill-dist.zip'
}

# Collect tracked files (UTF-8-safe: PS 5.1 decodes native stdout as ANSI by
# default, which mangles CJK filenames like adcs攻击.md)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$files = git -c core.quotepath=false -C $RepoRoot ls-files -z
if ($LASTEXITCODE -ne 0) {
    Write-Error "git ls-files failed - is '$RepoRoot' inside a git repo?"
}
$fileList = @($files -split "`0" | Where-Object { $_ -ne '' })
Write-Host "Packaging $($fileList.Count) tracked files -> $OutPath"

# Stage into a temp dir preserving the reverse-skill/ prefix
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("zip-dist-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    foreach ($f in $fileList) {
        $src = Join-Path $RepoRoot $f
        $dst = Join-Path $tmp $f
        $dstDir = Split-Path -Parent $dst
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
        Copy-Item $src $dst -Force
    }
    if (Test-Path $OutPath) { Remove-Item $OutPath -Force }
    Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath $OutPath -CompressionLevel Optimal
    Write-Host "Done: $OutPath ($([math]::Round((Get-Item $OutPath).Length / 1MB, 2)) MB)"
} finally {
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
