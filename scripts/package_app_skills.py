#!/usr/bin/env python3
"""Build upload-ready zips of the skills listed in app-skills.txt for the Claude app.

usage: package_app_skills.py [--out DIR]      (default: dist/app)

claude.ai wants <name>.zip containing <name>/SKILL.md, with the folder name equal
to the `name` field. Claude Code-only frontmatter (disable-model-invocation, ...)
is stripped from the copy so the app only sees name and description; the skill in
skills/ is not modified. Fails if a skill breaks the rules the app enforces.
"""
import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP = ("name", "description")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")
DESC_MAX = 1024        # claude.com/docs/skills/how-to; an older support article says 200
DESC_WARN = 200


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("no YAML frontmatter")
    fields = {}
    for line in m.group(1).split("\n"):
        key, sep, value = line.partition(":")
        if sep and re.match(r"^[A-Za-z_-]+$", key):
            fields[key] = value.strip()
        else:
            raise ValueError(f"unsupported frontmatter line (multi-line values are not handled): {line!r}")
    return fields, m.group(2)


def build(name, out):
    src = ROOT / "skills" / name
    problems, notes = [], []
    if not (src / "SKILL.md").is_file():
        return [f"skills/{name}/SKILL.md not found"], notes
    try:
        fields, body = split_frontmatter((src / "SKILL.md").read_text())
    except ValueError as e:
        return [str(e)], notes

    if fields.get("name") != name:
        problems.append(f"name field {fields.get('name')!r} must equal the folder name {name!r}")
    if not NAME_RE.match(name) or len(name) > 64 or any(w in name for w in RESERVED):
        problems.append("folder name must be lowercase-hyphen, max 64 chars, without 'anthropic' or 'claude'")
    desc = fields.get("description", "")
    if not desc:
        problems.append("missing description")
    if len(desc) > DESC_MAX:
        problems.append(f"description is {len(desc)} chars (max {DESC_MAX})")
    elif len(desc) > DESC_WARN:
        notes.append(f"description is {len(desc)} chars; an older help article says 200, so upload may reject it")
    if re.search(r"<[A-Za-z/]", desc):
        problems.append("description contains something that looks like an XML tag")
    dropped = sorted(set(fields) - set(KEEP))
    if "disable-model-invocation" in dropped:
        notes.append("explicit-only in Claude Code; in the app Claude may load it automatically")
    for rel in re.findall(r"\]\((?!https?:|#)([^)\s]+)\)", body):
        if not (src / rel).exists():
            problems.append(f"references missing file {rel}")
    if problems:
        return problems, notes

    stage = out / "_stage" / name
    shutil.rmtree(stage, ignore_errors=True)
    shutil.copytree(src, stage)
    kept = "\n".join(f"{k}: {fields[k]}" for k in KEEP)
    (stage / "SKILL.md").write_text(f"---\n{kept}\n---\n{body}")

    zip_path = out / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(stage.parent).as_posix())
    shutil.rmtree(out / "_stage")
    notes.append(f"-> {zip_path.relative_to(ROOT)}" + (f" (dropped: {', '.join(dropped)})" if dropped else ""))
    return [], notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "app"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)

    names = [l.strip() for l in (ROOT / "app-skills.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    failed = False
    for name in names:
        problems, notes = build(name, out)
        print(("FAIL " if problems else "ok   ") + name)
        for p in problems:
            print(f"       ! {p}")
        for n in notes:
            print(f"       {n}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
