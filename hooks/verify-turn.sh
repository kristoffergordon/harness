#!/usr/bin/env bash
# Run a project's own verifier after Claude finishes a turn, and send failures back.
#
#   UserPromptSubmit:  verify-turn.sh snapshot   remember the working tree before the turn
#   Stop:              verify-turn.sh            if the turn changed the tree, run .agent/verify.sh
#
# A project opts in by providing an executable .agent/verify.sh (exit 0 = pass).
# Projects without one are untouched. The verifier is repo-controlled code run
# without a permission prompt, so it only runs once you have approved its exact
# contents with verify-trust.sh. Editing it revokes that approval.
#
# On failure the output goes back to Claude (exit 2) for up to MAX_ROUNDS fix
# attempts; after that the hook stops blocking so a turn can never loop.
# CLAUDE_HOOK_DISABLE=1 bypasses it.

set -uo pipefail

MAX_ROUNDS=3
[[ "${CLAUDE_HOOK_DISABLE:-}" == "1" ]] && exit 0

mode="${1:-stop}"
input=$(cat)
project="${CLAUDE_PROJECT_DIR:-$PWD}"
verifier="$project/.agent/verify.sh"
[[ -x "$verifier" ]] || exit 0
git -C "$project" rev-parse --git-dir >/dev/null 2>&1 || exit 0

state_dir="${TMPDIR:-/tmp}"; state_dir="${state_dir%/}"
sid=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)
sid="${sid//[^A-Za-z0-9_-]/_}"; sid="${sid:-nosession}"
baseline="$state_dir/claude-verify-baseline-$sid"
counter="$state_dir/claude-verify-rounds-$sid"
notified="$state_dir/claude-verify-notified-$sid"
trust_file="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/verify-trusted"

hash_stdin() { if command -v shasum >/dev/null 2>&1; then shasum -a 256; else sha256sum; fi | cut -d' ' -f1; }

# Fingerprint of tracked and untracked content, so read-only turns are skipped.
fingerprint() {
  cd "$project" || return
  {
    git status --porcelain=v1 -z
    git diff HEAD
    while IFS= read -r -d '' f; do git hash-object -- "$f"; done < <(git ls-files -o --exclude-standard -z)
  } 2>/dev/null | hash_stdin
}

if [[ "$mode" == "snapshot" ]]; then
  fingerprint > "$baseline"
  exit 0
fi

verifier_hash=$(hash_stdin < "$verifier")
if ! grep -qxF "$verifier_hash $verifier" "$trust_file" 2>/dev/null; then
  if [[ ! -f "$notified" ]]; then
    : > "$notified"
    printf '{"systemMessage":"verify-turn: %s is not approved, so it was not run. Review it, then run: %s"}\n' \
      "$verifier" "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/verify-trust.sh $project"
  fi
  exit 0
fi

rounds=0
[[ -f "$counter" ]] && rounds=$(cat "$counter" 2>/dev/null)
[[ "$rounds" =~ ^[0-9]+$ ]] || rounds=0

current=$(fingerprint)
if (( rounds == 0 )) && [[ "$current" == "$(cat "$baseline" 2>/dev/null)" ]]; then
  exit 0
fi

out=$(cd "$project" && "$verifier" 2>&1); status=$?
if (( status == 0 )); then
  printf '%s\n' "$current" > "$baseline"
  rm -f "$counter"
  exit 0
fi

rounds=$((rounds + 1))
if (( rounds > MAX_ROUNDS )); then
  rm -f "$counter"
  echo "verify-turn: still failing after $MAX_ROUNDS attempts; leaving it for the user." >&2
  exit 0
fi
echo "$rounds" > "$counter"

if (( rounds == MAX_ROUNDS )); then
  echo "verify-turn: verification failed, attempt $rounds/$MAX_ROUNDS (final). If this fix does not make it pass, stop and summarize the remaining failure for the user:" >&2
else
  echo "verify-turn: verification failed, attempt $rounds/$MAX_ROUNDS. Fix it before finishing:" >&2
fi
printf '%s\n' "$out" | tail -n 150 >&2
exit 2
