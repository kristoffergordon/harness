#!/usr/bin/env bash
# Approve a project's .agent/verify.sh for the verify-turn hook.
# Usage: verify-trust.sh [project-dir]   (default: current directory)
# Review the script first. Approval is bound to its exact contents.
set -euo pipefail

project="$(cd "${1:-$PWD}" && pwd -P)"
verifier="$project/.agent/verify.sh"
[[ -x "$verifier" ]] || { echo "no executable $verifier" >&2; exit 1; }

if command -v shasum >/dev/null 2>&1; then hash=$(shasum -a 256 < "$verifier"); else hash=$(sha256sum < "$verifier"); fi
hash="${hash%% *}"
trust_file="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/verify-trusted"
mkdir -p "$(dirname "$trust_file")"
grep -v " $verifier\$" "$trust_file" 2>/dev/null > "$trust_file.tmp" || true
echo "$hash $verifier" >> "$trust_file.tmp"
mv "$trust_file.tmp" "$trust_file"
echo "trusted $verifier ($hash)"
