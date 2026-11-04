#!/usr/bin/env bash
# Install this repo's Claude Code resources into ~/.claude via symlinks.
#
#   ./install.sh            link everything; refuse to replace existing paths
#   ./install.sh --force    replace existing paths (moved to a timestamped backup first)
#   ./install.sh --dry-run  show what would happen, change nothing
#
# Links (per entry, so skills installed by other means are left alone):
#   CLAUDE.md          -> ~/.claude/CLAUDE.md
#   skills/<name>      -> ~/.claude/skills/<name>
#   local/skills/<name>-> ~/.claude/skills/<name>   (gitignored; client/employer-internal)
#
# Safe to rerun: links that already point here are left untouched.

set -euo pipefail

FORCE=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
BACKUP_DIR="$HOME/.skills-backups/$(date +%Y%m%d-%H%M%S)"
status=0

run() { if [[ $DRY -eq 1 ]]; then echo "  (dry-run) $*"; else "$@"; fi; }

link() {
  local src="$1" dest="$2"

  if [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]]; then
    echo "ok       $dest"
    return
  fi

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ $FORCE -ne 1 ]]; then
      echo "SKIPPED  $dest exists (rerun with --force to back it up and replace)" >&2
      status=1
      return
    fi
    run mkdir -p "$BACKUP_DIR"
    run mv "$dest" "$BACKUP_DIR/$(basename "$dest")"
    if [[ $DRY -eq 1 ]]; then echo "would back up $dest -> $BACKUP_DIR/"; else echo "backup   $dest -> $BACKUP_DIR/"; fi
  fi

  run mkdir -p "$(dirname "$dest")"
  run ln -s "$src" "$dest"
  if [[ $DRY -eq 1 ]]; then echo "would link $dest -> $src"; else echo "linked   $dest -> $src"; fi
}

link "$REPO/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"

for dir in "$REPO"/skills/*/ "$REPO"/local/skills/*/; do
  [[ -f "${dir}SKILL.md" ]] || continue
  dir="${dir%/}"
  link "$dir" "$CLAUDE_DIR/skills/$(basename "$dir")"
done

exit $status
