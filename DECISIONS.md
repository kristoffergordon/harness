# Decisions

Newest last. Record what was refused and why, so it is not re-proposed. Skip routine steps.

### 1 · Claude Code only
Not Pi, Codex, or a shared harness-neutral layer. Revisit if a second harness is used regularly.

### 2 · Per-entry symlinks, not a linked `skills/` directory
`install.sh` links each skill individually into `~/.claude/skills/`. On client machines other skills may already exist there, and linking the whole directory would replace them.

### 3 · `local/` for anything client- or employer-specific
The repo is public. `local/` is gitignored but still linked by `install.sh`, so internal skills deploy without being published.

### 4 · Not adopted from Simon's coding-harness (for now)
Pi extensions, probes suite, sandbox and read-routing layers, `stay-awake`. They solve problems of a multi-harness setup. Revisit individual pieces only when a concrete problem shows up.

### 5 · Inherited skills stay until used
The Pocock-derived skills remain as a baseline. Keep, rewrite, or delete each based on whether it gets invoked.

### 6 · Removed `grill-with-docs`; no `domain-modeling` skill
`grill-with-docs` was a one-line wrapper around a `/domain-modeling` skill this repo never had. Client repos may not want `CONTEXT.md`/ADR files, so the docs-writing step was dropped from `improve-codebase-architecture` as well. Reading `CONTEXT.md`/ADRs when they exist is kept. Revisit if domain docs become a regular deliverable.

### 7 · Removed `/codebase-design` references
`improve-codebase-architecture`, `tdd` and the HTML report pointed at a skill this repo never had. The seven-term vocabulary (module, interface, depth, seam, adapter, leverage, locality) now lives inline in `improve-codebase-architecture`; the terms are no longer defined, only named. The "deletion test" and related principles were dropped. Revisit if the architecture skill's output uses these terms inconsistently.
