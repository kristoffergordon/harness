# skills

My Claude Code harness: a global `CLAUDE.md` and a set of skills, versioned here and symlinked into `~/.claude`.

## Install

```sh
git clone https://github.com/kristoffergordon/skills
cd skills
./install.sh --dry-run   # preview
./install.sh             # link; refuses to replace existing paths
./install.sh --force     # back up (~/.skills-backups/<timestamp>) and replace
```

The links point at the clone, so do not move it afterwards. Rerun after pulling. Start a new Claude Code session to pick up changes.

## Hooks

`install.sh` links `hooks/` into `~/.claude/hooks/` and adds three entries to `~/.claude/settings.json`. Anything else in that file is left alone, and the original is backed up first. Needs `python3`.

- **`guard_bash.py`** (PreToolUse on Bash) blocks force-push, `git reset --hard`, `git clean -f`, `git branch -D`, `git checkout .`/`git restore .`, `sudo`, download-piped-to-shell, and recursive `rm` of `/`, `~` or `.`. Plain `git push` is not blocked. It guards against accidents, not a determined bypass.
- **`verify-turn.sh`** (UserPromptSubmit + Stop) runs a project's `.agent/verify.sh` after a turn that changed the working tree, and returns failures to Claude for up to three fix attempts. It does nothing in projects without that file.
- **`verify-trust.sh`** approves a project's verifier. The verifier is repo-controlled code that runs without a prompt, so it only runs after you approve its exact contents, and any edit (including by Claude) revokes that.

```sh
# in a project: create the verifier, read it, approve it
printf '#!/bin/sh\npytest -q && ruff check . && mypy .\n' > .agent/verify.sh && chmod +x .agent/verify.sh
~/.claude/hooks/verify-trust.sh
```

In client repos, add `.agent/` to `.git/info/exclude` rather than committing it.

`CLAUDE_HOOK_DISABLE=1` bypasses both hooks. Run the offline tests with `hooks/test/run.sh`.

## Layout

```text
CLAUDE.md          global instructions  -> ~/.claude/CLAUDE.md
skills/<name>/     public skills        -> ~/.claude/skills/<name>
hooks/             hook scripts         -> ~/.claude/hooks/ (registered in settings.json)
scripts/           install helpers (settings merge); not installed
local/skills/      gitignored; client/employer-internal skills, linked the same way
ralph/             loop scripts; copy into a project, not installed
DECISIONS.md       what was tried or rejected, and why
```

This repo is public. Anything client- or employer-specific goes in `local/`, which is never committed.

## Credits

`grill-me`, `improve-codebase-architecture`, `tdd`, `to-issues`, `to-prd`, `ralph`, `to-questionnaire`, `wizard`, and `writing-for-agents` come from [mattpocock/skills](https://github.com/mattpocock/skills). `explain-code`, `diagnose-failure`, `primary-source-research`, `technical-writing`, `over-engineering-audit`, `handoff`, and `humanize-writing` come from [simonamtoft/coding-harness](https://github.com/simonamtoft/coding-harness), with references to his Pi-specific tooling removed. All are being adapted over time.
