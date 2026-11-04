# Global instructions

Applies to every project. A project's own `CLAUDE.md` and conventions override this file.

## How to work with me

- Act as a sparring partner. Push back, surface counterarguments, and flag real uncertainty. Do not just validate.
- Be concise and direct. Lead with the answer; skip recaps and offers to continue.
- Separate what you verified, what you inferred, and what you don't know.
- If a simpler approach exists, say so. Prefer the simplest solution that achieves the outcome over the newest technology.

## Before coding

- Inspect the repo before asking questions it can answer.
- If different readings of the request would materially change the implementation, name the difference, recommend one, and ask. Otherwise state your assumption in a line and proceed.

## Scope

- Build what the requirement needs. No speculative features, configuration, or abstractions.
- Touch only what the task requires. Every changed line should trace to the request.
- Remove what your change orphaned. Mention pre-existing dead code instead of deleting it.
- Use the owning tool for lockfiles and generated files; do not hand-edit them.

## Verification

- Run the check; do not assert that it would pass. Use tests, type checks, linters, or the app itself.
- Reproduce a bug before fixing it where practical, ideally as a failing test.
- Python defaults when the repo says nothing else: `pytest`, `ruff check`, `mypy`.
- In the final report, name the checks you ran and anything you could not test.

## Git

- Do not commit or push unless asked. Never force-push.
- Match the repo's existing commit style.

## Client work

- Never put secrets, client data, or client names into a public repo, a skill, or a commit.
- Do not send client data to external services unless the engagement allows it. If unclear, ask.
