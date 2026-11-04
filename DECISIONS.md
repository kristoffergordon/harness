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

### 8 · First skill batch from Simon and Pocock
Added: `to-questionnaire`, `explain-code`, `diagnose-failure`, `primary-source-research`, `technical-writing`, `over-engineering-audit`, `handoff`, `humanize-writing`, `wizard`, `writing-for-agents`. Chosen for consulting, strategy and devops work (discovery, entering unfamiliar client repos, handovers, deployment walkthroughs).
Left out on purpose: anything tied to Backlog.md or GitHub-issue workflows (`to-spec`, `to-tickets`, `wayfinder`, `triage`), TypeScript-only skills, and Pi-specific tooling. Subagent delegation (`bulk-read`, `test-log-analyst`, `present`) was removed from the copied skills rather than ported.
Review after about two weeks of use. Delete what was not invoked.

### 9 · Own hooks instead of copying Simon's or Pocock's
Simon's bash guard is 512 lines and his verifier needs a Python fingerprinter; Pocock's guard regex-matches the raw command, so a commit message that mentions `reset --hard` is blocked. `guard_bash.py` parses commands into arguments instead. Plain `git push` is deliberately not blocked (Pocock blocks it): Claude should be able to push when asked, and the normal permission prompt covers the rest. Revisit if an unwanted push slips through.

### 10 · Verifier is opt-in per project and content-trusted
`.agent/verify.sh` is repo-controlled code run by a hook with no prompt, which is a code-execution path on client repos. It runs only after `verify-trust.sh` approves its exact hash, so Claude editing the verifier to make it pass also revokes trust. Taskfile discovery from Simon's version was dropped; add it if a project needs it.

### 11 · Hooks registered by merging into settings.json, not by linking it
Linking `settings.json` (Simon's approach) would overwrite client-specific permissions and settings. `scripts/merge_settings.py` adds only missing hook entries and backs the file up. Alternative not taken: shipping hooks as a Claude Code plugin, which avoids editing settings but may be restricted on client machines and cannot carry `CLAUDE.md`. Revisit if the merge proves fragile.

### 12 · Claude app skills are built from the repo, not authored there
Sources: claude.ai uploads are manual per-skill zips and do not sync with Claude Code in either direction, apart from Claude Code downloading app skills. So `app-skills.txt` selects the skills that need no repo or shell (`grill-me`, `to-questionnaire`, `humanize-writing`, `technical-writing`) and `scripts/package_app_skills.py` builds the zips. Code-centric skills (`tdd`, `diagnose-failure`, `explain-code`, `wizard` and so on) are not ported: they have nothing to work on in chat. Better app skills are probably new, consulting-native ones (proposals, workshop design, decision memos) rather than ports.
Renamed `grilling` to `grill-me` because the app requires the folder name to equal the `name` field.
Open: the app's description limit is documented as 1,024 characters in one place and 200 in another; two skills exceed 200. Upload `humanize-writing` first to find out.
Revisit: shipping everything as a plugin would put skills and hooks on one account-synced path, but plugin sync needs a claude.ai sign-in, which may not hold on client machines.

### 13 · Three consulting-native skills, written here rather than ported
`decision-memo`, `workshop-design` and `meeting-to-actions` are original, built for consulting and strategy work and for both the app and Claude Code. Each has a "challenge the brief" step because the stated preference is a sparring partner, not a formatter: the memo skill must consider "do nothing" and the cheapest alternative, the workshop skill must ask whether a workshop is the right format, and the meeting skill refuses to invent owners or dates. Descriptions are under 200 characters on purpose.
Not yet exercised on real tasks. Review after two weeks of use, like the rest.
