"""Offline test for scripts/merge_settings.py against a throwaway settings.json."""
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(REPO, "scripts", "merge_settings.py")
FRAGMENT = os.path.join(REPO, "scripts", "settings.fragment.json")
fails = 0


def check(name, got, want):
    global fails
    if got == want:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}: expected {want!r}, got {got!r}")
        fails += 1


def merge(settings, *extra):
    return subprocess.run([sys.executable, "-I", SCRIPT, settings, FRAGMENT, "/h", *extra],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as t:
    s = os.path.join(t, "settings.json")
    with open(s, "w") as f:
        json.dump({"model": "x", "permissions": {"allow": ["Bash(ls)"], "deny": ["Read(~/.ssh/**)"]}}, f)
    fragment_rules = json.load(open(FRAGMENT))["permissions"]["deny"]

    merge(s, "--dry-run")
    check("dry-run leaves file alone", json.load(open(s))["permissions"]["deny"], ["Read(~/.ssh/**)"])

    r = merge(s, "--backup-dir", os.path.join(t, "bak"))
    cfg = json.load(open(s))
    check("other settings kept", (cfg["model"], cfg["permissions"]["allow"]), ("x", ["Bash(ls)"]))
    check("all deny rules present", set(cfg["permissions"]["deny"]), set(fragment_rules))
    check("existing rule not duplicated", cfg["permissions"]["deny"].count("Read(~/.ssh/**)"), 1)
    check("hooks added", "PreToolUse" in cfg["hooks"], True)
    check("backup written", os.path.exists(os.path.join(t, "bak", "settings.json")), True)

    r = merge(s)
    check("rerun is a no-op", r.stdout.startswith("ok"), True)

    with open(s, "w") as f:
        f.write("{not json")
    check("invalid JSON refused", merge(s).returncode, 1)

sys.exit(1 if fails else 0)
