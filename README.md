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

## Layout

```text
CLAUDE.md          global instructions  -> ~/.claude/CLAUDE.md
skills/<name>/     public skills        -> ~/.claude/skills/<name>
local/skills/      gitignored; client/employer-internal skills, linked the same way
ralph/             loop scripts; copy into a project, not installed
DECISIONS.md       what was tried or rejected, and why
```

This repo is public. Anything client- or employer-specific goes in `local/`, which is never committed.

## Credits

`grill-me`, `improve-codebase-architecture`, `tdd`, `to-issues`, `to-prd`, and `ralph` come from [mattpocock/skills](https://github.com/mattpocock/skills) and are being adapted over time.
