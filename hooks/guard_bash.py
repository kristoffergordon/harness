#!/usr/bin/env python3
"""PreToolUse hook for Bash: block a small set of irreversible commands.

Exit 2 blocks the call and returns the reason to Claude. Everything else passes
through to the normal permission flow.

The command is split into simple commands and parsed into arguments, so quoted
text (a commit message mentioning `reset --hard`) is not matched. It is a
guard against accidents, not a sandbox: `$(...)`, aliases and scripts that call
git internally are not inspected. Set CLAUDE_HOOK_DISABLE=1 to bypass.
"""
import json
import os
import re
import shlex
import sys

SHELLS = {"sh", "bash", "zsh", "dash"}
WRAPPERS = {"env", "command", "exec", "nohup", "time", "nice", "builtin"}
FETCHERS = {"curl", "wget"}
ESCALATION = {"sudo", "doas", "su"}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
DESTRUCTIVE_RM_TARGETS = {"/", "/*", "~", "~/", "~/*", "$HOME", "${HOME}", "$HOME/", "$HOME/*", ".", "..", ".*"}


def strip_heredocs(cmd):
    out, end = [], None
    for line in cmd.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = re.search(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_]\w*)\1", line)
        if m:
            end = m.group(2)
    return "\n".join(out)


def newlines_to_semicolons(cmd):
    """Turn unquoted newlines into ';' so shlex sees command boundaries."""
    out, quote, escaped = [], None, False
    for ch in cmd:
        if escaped:
            escaped = False
        elif ch == "\\" and quote != "'":
            escaped = True
        elif quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "\n":
            ch = ";"
        out.append(ch)
    return "".join(out)


def split_commands(cmd):
    """Return [(argv, piped_from_previous)] or None when the command cannot be parsed."""
    lexer = shlex.shlex(newlines_to_semicolons(strip_heredocs(cmd)), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    commands, current, piped = [], [], False
    for tok in tokens + [";"]:
        if tok in SEPARATORS:
            if current:
                commands.append((current, piped))
            current, piped = [], tok in {"|", "|&"}
        else:
            current.append(tok)
    return commands


def unwrap(argv):
    while argv:
        name = os.path.basename(argv[0])
        if re.match(r"^[A-Za-z_]\w*=", argv[0]):
            argv = argv[1:]
        elif name in WRAPPERS:
            argv = argv[1:]
            while name == "env" and argv and argv[0].startswith("-"):
                argv = argv[1:]
        else:
            break
    return argv


def has_short(flag, args):
    return any(a.startswith("-") and not a.startswith("--") and flag in a[1:] for a in args)


def check_git(args):
    i = 0
    while i < len(args):
        if args[i] in {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}:
            i += 2
        elif args[i].startswith("-"):
            i += 1
        else:
            break
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    if sub == "push" and (
        "--force" in rest or "--mirror" in rest or has_short("f", rest) or any(a.startswith("+") for a in rest)
    ):
        return "force push"
    if sub == "reset" and "--hard" in rest:
        return "git reset --hard"
    if sub == "clean" and (has_short("f", rest) or "--force" in rest) and not (has_short("n", rest) or "--dry-run" in rest):
        return "git clean -f"
    if sub == "branch" and has_short("D", rest):
        return "git branch -D"
    if sub in {"checkout", "restore"} and "." in rest and "--staged" not in rest:
        return f"git {sub} . (discards all working-tree changes)"
    if sub in {"filter-branch", "filter-repo"}:
        return f"git {sub} (history rewrite)"
    return None


def check_rm(args):
    recursive = has_short("r", args) or has_short("R", args) or "--recursive" in args
    targets = [a for a in args if not a.startswith("-")]
    if recursive and any(t in DESTRUCTIVE_RM_TARGETS for t in targets):
        return "recursive rm of a root, home, or current directory"
    return None


def analyse(cmd, depth=0):
    commands = split_commands(cmd)
    if commands is None or depth > 3:
        return None
    previous = None
    for argv, piped in commands:
        argv = unwrap(argv)
        if not argv:
            continue
        name = os.path.basename(argv[0])
        reason = None
        if name in ESCALATION:
            reason = "privilege escalation"
        elif name in SHELLS and piped and previous in FETCHERS:
            reason = "piping a download into a shell"
        elif name in SHELLS or name == "eval":
            payload = None
            if name == "eval":
                payload = " ".join(argv[1:])
            else:
                for j, a in enumerate(argv[1:], start=1):
                    if a.startswith("-") and not a.startswith("--") and "c" in a[1:] and j + 1 < len(argv):
                        payload = argv[j + 1]
                        break
            reason = analyse(payload, depth + 1) if payload else None
        elif name == "git":
            reason = check_git(argv[1:])
        elif name == "rm":
            reason = check_rm(argv[1:])
        if reason:
            return reason
        previous = name
    return None


def main():
    if os.environ.get("CLAUDE_HOOK_DISABLE") == "1":
        return 0
    try:
        cmd = (json.load(sys.stdin).get("tool_input") or {}).get("command") or ""
    except (ValueError, AttributeError):
        return 0
    reason = analyse(cmd)
    if reason:
        print(f"BLOCKED by guard_bash: {reason}. If this is really intended, ask the user to run it themselves.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
