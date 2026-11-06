# harness

My Claude Code harness: a global `CLAUDE.md`, skills, hooks and an installer, versioned here and symlinked into `~/.claude`.

## Install

```sh
git clone https://github.com/kristoffergordon/harness
cd harness
./install.sh --dry-run   # preview
./install.sh             # link; refuses to replace existing paths
./install.sh --force     # back up (~/.skills-backups/<timestamp>) and replace
```

The links point at the clone, so do not move it afterwards. Rerun after pulling. Start a new Claude Code session to pick up changes.

## Claude app (claude.ai, desktop, mobile)

Custom skills in the app are uploaded as zips per skill, and they are separate from Claude Code: uploading to the app does not touch `~/.claude`, and nothing you do in Claude Code reaches the app. Claude Code does download your app skills (into `~/.claude/skills/synced/`) when signed in with the same account, never the reverse. So this repo stays the source of truth and the app copies are built from it.

```sh
scripts/package_app_skills.py   # builds dist/app/<skill>.zip for each skill in app-skills.txt
```

Upload each zip in the app under Customize > Skills (Settings > Features in older UIs). Needs a paid plan with code execution on. Re-upload a zip after changing a skill. Only skills that need no repo, shell or git belong in `app-skills.txt`.

Differences to expect in the app: Claude Code-only frontmatter such as `disable-model-invocation` is stripped, so explicit-only skills can trigger on their own; hooks and `CLAUDE.md` do not apply (put the "How to work with me" section of `CLAUDE.md` into your personal preferences instead); and a skill you upload is also synced down to Claude Code, so it appears twice on a machine where this repo is installed. The local copy wins by name; set `syncClaudeAiSkills` to `false` in `~/.claude/settings.json` if the duplicate bothers you.

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
app-skills.txt     skills also packaged for the Claude app
hooks/             hook scripts         -> ~/.claude/hooks/ (registered in settings.json)
scripts/           install helpers (settings merge); not installed
local/skills/      gitignored; client/employer-internal skills, linked the same way
ralph/             loop scripts; copy into a project, not installed
DECISIONS.md       what was tried or rejected, and why
```

This repo is public. Anything client- or employer-specific goes in `local/`, which is never committed.

## Credits

`grill-me`, `improve-codebase-architecture`, `tdd`, `to-issues`, `to-prd`, `ralph`, `to-questionnaire`, `wizard`, and `writing-for-agents` come from [mattpocock/skills](https://github.com/mattpocock/skills). `explain-code`, `diagnose-failure`, `primary-source-research`, `technical-writing`, `over-engineering-audit`, `handoff`, and `humanize-writing` come from [simonamtoft/coding-harness](https://github.com/simonamtoft/coding-harness), with references to his Pi-specific tooling removed. All are being adapted over time.
