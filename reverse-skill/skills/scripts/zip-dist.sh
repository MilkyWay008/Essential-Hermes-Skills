#!/usr/bin/env bash
# zip-dist.sh — build a clean release zip from git-tracked files only
# Usage:
#   bash scripts/zip-dist.sh [-o ../reverse-skill-dist.zip]
# Why git ls-files? The working tree contains untracked junk that must never
# ship: reports/ (un-desensitized pentest samples — anti-leak policy), .trash/,
# *.bak backups. `git ls-files` excludes all of it by construction. If you
# want the sample CTF report, copy it in deliberately.
# The zip contains the pack as a folder named reverse-skill/ (same layout as
# the repo), so extraction yields one tidy folder.
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

if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="$(dirname "$PACK_ROOT")/reverse-skill-dist.zip"
fi

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

# tracked paths relative to git root, filtered to the pack dir
# core.quotepath=false -> CJK filenames come out literal, not \NNN-escaped
PACK_REL="reverse-skill"
FILES="$(cd "$GIT_ROOT" && git -c core.quotepath=false ls-files -- "$PACK_REL/")"
if [[ -z "$FILES" ]]; then
  echo "ERROR: no tracked files under '$PACK_REL' — nothing to package." >&2
  exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

COUNT=0
while IFS= read -r f; do
  rel="${f#"$PACK_REL"/}"          # strip pack prefix -> reverse-skill/<rel>
  dst="$TMP/reverse-skill/$rel"
  mkdir -p "$(dirname "$dst")"
  cp "$GIT_ROOT/$f" "$dst"
  COUNT=$((COUNT + 1))
done <<< "$FILES"

echo "Packaging $COUNT tracked files -> $OUT_PATH"
rm -f "$OUT_PATH"
if command -v zip >/dev/null 2>&1; then
  (cd "$TMP" && zip -qr "$OUT_PATH" reverse-skill)
else
  OUT_PATH="${OUT_PATH%.zip}.tar.gz"
  tar -czf "$OUT_PATH" -C "$TMP" reverse-skill
fi
SIZE="$(du -h "$OUT_PATH" | cut -f1)"
echo "Done: $OUT_PATH ($SIZE)"
