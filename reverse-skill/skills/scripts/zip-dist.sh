#!/usr/bin/env bash
# zip-dist.sh — build a clean release archive from git-tracked files only
# Usage:
#   bash scripts/zip-dist.sh [-o ../reverse-skill-dist.zip]
# Why git archive? The working tree contains untracked junk that must never
# ship: reports/ (un-desensitized pentest samples - anti-leak policy), .trash/,
# *.bak backups. `git archive` excludes all of it by construction. If you want
# the sample CTF report, copy it in deliberately.
# The archive contains the pack as a folder named reverse-skill/ (same layout
# as the repo), so extraction yields one tidy folder.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../reverse-skill/skills/scripts
OUT_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--out) OUT_PATH="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# locate the enclosing git work tree (repo root is the PARENT of the pack dir)
# NOTE: use (cd ... && git) not `git -C <path>` — native git.exe can't chdir
# into MSYS-style /c/... paths (fails with "cannot change to ...").
GIT_ROOT="$(cd "$SCRIPT_DIR" && git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$GIT_ROOT" ]]; then
  echo "ERROR: pack is not inside a git repo — zip-dist only builds from git-tracked files." >&2
  exit 2
fi

# pack root = <repo>/reverse-skill (fixed layout — avoids junction/relpath pitfalls)
PACK_ROOT="$GIT_ROOT/reverse-skill"
if [[ ! -d "$PACK_ROOT" ]]; then
  echo "ERROR: expected pack at '$PACK_ROOT' (repo layout: <repo>/reverse-skill)." >&2
  exit 2
fi

COUNT="$(cd "$GIT_ROOT" && git ls-files -- reverse-skill/ | wc -l)"

# git archive: single fast pass, tracked-only, keeps the reverse-skill/ prefix.
# IMPORTANT (MSYS git quirk): `git archive -o <file>` silently writes NOTHING
# on this host — always capture stdout with a redirect instead.
# Prefer zip when the zip binary exists (git's builtin zip), else tar.gz.
USE_ZIP=0
if command -v zip >/dev/null 2>&1; then
  USE_ZIP=1
fi

if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="$(dirname "$PACK_ROOT")/reverse-skill-dist.zip"
fi
if [[ "$OUT_PATH" != *.zip && "$OUT_PATH" != *.tar.gz && "$OUT_PATH" != *.tgz ]]; then
  OUT_PATH="$OUT_PATH.zip"
fi

echo "Packaging $COUNT tracked files -> $OUT_PATH"
rm -f "$OUT_PATH"

if [[ $USE_ZIP -eq 1 ]]; then
  (cd "$GIT_ROOT" && git archive --format=zip HEAD -- reverse-skill/) > "$OUT_PATH"
else
  OUT_PATH="${OUT_PATH%.zip}.tar.gz"
  (cd "$GIT_ROOT" && git archive --format=tar HEAD -- reverse-skill/) | gzip > "$OUT_PATH"
fi

SIZE="$(du -h "$OUT_PATH" | cut -f1)"
echo "Done: $OUT_PATH ($SIZE)"
