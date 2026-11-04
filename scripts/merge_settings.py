#!/usr/bin/env python3
"""Add this repo's hook entries to a Claude Code settings.json without touching anything else.

usage: merge_settings.py SETTINGS FRAGMENT HOOKS_DIR [--dry-run] [--backup-dir DIR]

Idempotent: an entry is added only if no hook with the same command exists under
the same event and matcher. Refuses to touch a file that is not valid JSON.
"""
import argparse
import json
import os
import shutil
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("settings")
    ap.add_argument("fragment")
    ap.add_argument("hooks_dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backup-dir")
    args = ap.parse_args()

    with open(args.fragment) as f:
        fragment = json.loads(f.read().replace("{{HOOKS}}", args.hooks_dir))

    config = {}
    if os.path.exists(args.settings):
        try:
            with open(args.settings) as f:
                config = json.load(f)
        except ValueError as e:
            print(f"SKIPPED  {args.settings} is not valid JSON ({e}); add the hooks by hand", file=sys.stderr)
            return 1
        if not isinstance(config, dict):
            print(f"SKIPPED  {args.settings} is not a JSON object", file=sys.stderr)
            return 1

    added = 0
    hooks = config.setdefault("hooks", {})
    for event, groups in fragment["hooks"].items():
        existing = hooks.setdefault(event, [])
        for group in groups:
            target = next((g for g in existing if g.get("matcher") == group.get("matcher")), None)
            if target is None:
                existing.append(group)
                added += len(group["hooks"])
                continue
            present = {h.get("command") for h in target.setdefault("hooks", [])}
            for hook in group["hooks"]:
                if hook["command"] not in present:
                    target["hooks"].append(hook)
                    added += 1

    if not added:
        print(f"ok       hooks already in {args.settings}")
        return 0
    if args.dry_run:
        print(f"would add {added} hook entries to {args.settings}")
        return 0

    if os.path.exists(args.settings) and args.backup_dir:
        os.makedirs(args.backup_dir, exist_ok=True)
        shutil.copy2(args.settings, os.path.join(args.backup_dir, "settings.json"))
    os.makedirs(os.path.dirname(args.settings) or ".", exist_ok=True)
    with open(args.settings, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"updated  {args.settings} (+{added} hook entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
