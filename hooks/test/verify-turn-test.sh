#!/usr/bin/env bash
# Offline test for verify-turn.sh in a throwaway repo and HOME.
set -uo pipefail
HOOKS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
export HOME="$T/home" TMPDIR="$T/tmp" CLAUDE_PROJECT_DIR="$T/proj"; mkdir -p "$HOME" "$TMPDIR" "$CLAUDE_PROJECT_DIR"
unset CLAUDE_CONFIG_DIR CLAUDE_HOOK_DISABLE
fails=0
check() { if [[ "$2" == "$3" ]]; then echo "ok   $1"; else echo "FAIL $1: expected '$3', got '$2'"; fails=$((fails+1)); fi; }
stop() { echo '{"session_id":"s1"}' | "$HOOKS/verify-turn.sh" 2>"$T/err" >"$T/out"; echo $?; }
snap() { echo '{"session_id":"s1"}' | "$HOOKS/verify-turn.sh" snapshot; }

cd "$CLAUDE_PROJECT_DIR" && git init -q && git config user.email t@t && git config user.name t
echo a > a.txt && git add . && git -c commit.gpgsign=false commit -qm init

check "no verifier is a no-op" "$(stop)" 0

mkdir .agent && printf '#!/bin/sh\necho ran >> "%s/runs"\n[ -f fail ] && { echo "boom: assertion failed"; exit 1; }\nexit 0\n' "$T" > .agent/verify.sh && chmod +x .agent/verify.sh
snap; echo b >> a.txt
check "untrusted verifier does not run" "$(stop)" 0
check "untrusted verifier warns once" "$(grep -c 'not approved' "$T/out")" 1
check "no second warning" "$(stop >/dev/null; grep -c 'not approved' "$T/out")" 0
check "verifier never ran" "$(cat "$T/runs" 2>/dev/null | wc -l | tr -d ' ')" 0

"$HOOKS/verify-trust.sh" "$CLAUDE_PROJECT_DIR" >/dev/null
snap
check "unchanged tree skips verifier" "$(stop)" 0
check "verifier still not run" "$(cat "$T/runs" 2>/dev/null | wc -l | tr -d ' ')" 0

echo c >> a.txt; touch fail
check "failing verifier blocks (1)" "$(stop)" 2
check "failure output returned" "$(grep -c 'boom' "$T/err")" 1
check "failing verifier blocks (2)" "$(stop)" 2
check "failing verifier blocks (3, final)" "$(stop)" 2
check "final attempt says so" "$(grep -c 'final' "$T/err")" 1
check "cap reached, stops blocking" "$(stop)" 0

rm fail
check "passing verifier allows stop" "$(stop)" 0
stop >/dev/null
check "passing result remembered, no rerun" "$(wc -l < "$T/runs" | tr -d ' ')" 5

echo '# weakened' >> .agent/verify.sh; echo d >> a.txt
check "edited verifier is untrusted again" "$(stop)" 0
check "edited verifier was not run" "$(wc -l < "$T/runs" | tr -d ' ')" 5

CLAUDE_HOOK_DISABLE=1 check "disable switch" "$(CLAUDE_HOOK_DISABLE=1 stop)" 0
exit $((fails > 0))
