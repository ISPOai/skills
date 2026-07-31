#!/usr/bin/env python3
"""Validate the published skill catalog and every pinned package."""

from __future__ import annotations

import json
import re
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"
SKILLS_PATH = ROOT / "skills"
ROOT_KEYS = {"schemaVersion", "skills"}
SKILL_KEYS = {
    "id",
    "name",
    "description",
    "category",
    "subpath",
    "ref",
    "providers",
    "hasScripts",
    "requirements",
}
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PROVIDERS = {"claude", "codex"}


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def run_git(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        fail(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def require_string(value: object, field: str, skill_id: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{skill_id}: {field} must be a non-empty string")
    return value


def skill_name(markdown: str, source: str) -> str:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{source}: SKILL.md must start with YAML frontmatter")

    names: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^name:\s*(.+?)\s*$", line)
        if match:
            names.append(match.group(1).strip().strip("\"'"))
    else:
        fail(f"{source}: SKILL.md frontmatter is not closed")

    if len(names) != 1 or not names[0]:
        fail(f"{source}: SKILL.md frontmatter must contain exactly one name")
    return names[0]


def validate_worktree_package(skill_id: str, subpath: str, has_scripts: bool) -> None:
    package = ROOT / subpath
    if package.is_symlink() or not package.is_dir():
        fail(f"{skill_id}: package directory is missing or is a symlink")

    skill_files = sorted(package.rglob("SKILL.md"))
    if skill_files != [package / "SKILL.md"]:
        fail(f"{skill_id}: package must contain exactly one root SKILL.md")

    for path in package.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            fail(f"{skill_id}: symlink is not allowed: {path.relative_to(ROOT)}")
        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            fail(f"{skill_id}: special file is not allowed: {path.relative_to(ROOT)}")

    current_name = skill_name(
        (package / "SKILL.md").read_text(encoding="utf-8"),
        str((package / "SKILL.md").relative_to(ROOT)),
    )
    if current_name != skill_id:
        fail(f"{skill_id}: SKILL.md name is {current_name!r}")

    scripts = package / "scripts"
    scripts_present = scripts.is_dir() and any(path.is_file() for path in scripts.rglob("*"))
    if has_scripts != scripts_present:
        fail(f"{skill_id}: hasScripts does not match package contents")


def validate_pinned_package(skill_id: str, subpath: str, ref: str) -> None:
    run_git("cat-file", "-e", f"{ref}^{{commit}}")
    if run_git("cat-file", "-t", f"{ref}:{subpath}").strip() != b"tree":
        fail(f"{skill_id}: {subpath} is not a directory at {ref}")

    tree = run_git("ls-tree", "-r", "-z", "--full-tree", ref, "--", subpath)
    entries = [entry for entry in tree.split(b"\0") if entry]
    if not entries:
        fail(f"{skill_id}: package is empty at {ref}")

    paths: list[str] = []
    for entry in entries:
        metadata, raw_path = entry.split(b"\t", 1)
        mode, object_type, _object_id = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8")
        if object_type != "blob" or mode not in {"100644", "100755"}:
            fail(f"{skill_id}: symlink or special file at {ref}: {path}")
        paths.append(path)

    root_skill = f"{subpath}/SKILL.md"
    skill_paths = [path for path in paths if path.endswith("/SKILL.md")]
    if skill_paths != [root_skill]:
        fail(f"{skill_id}: pinned package must contain exactly one root SKILL.md")

    pinned_skill = run_git("show", f"{ref}:{root_skill}").decode("utf-8")
    pinned_name = skill_name(pinned_skill, f"{ref}:{root_skill}")
    if pinned_name != skill_id:
        fail(f"{skill_id}: pinned SKILL.md name is {pinned_name!r}")

    diff = subprocess.run(
        ["git", "diff", "--quiet", ref, "--", subpath],
        cwd=ROOT,
        check=False,
    )
    if diff.returncode == 1:
        fail(f"{skill_id}: worktree package differs from pinned ref {ref}")
    if diff.returncode != 0:
        fail(f"{skill_id}: could not compare worktree package with {ref}")
    untracked = run_git("ls-files", "--others", "--exclude-standard", "--", subpath)
    if untracked:
        fail(f"{skill_id}: package contains untracked files")


def validate() -> int:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"catalog.json is unreadable: {error}")

    if not isinstance(catalog, dict) or set(catalog) != ROOT_KEYS:
        fail(f"catalog.json must contain exactly: {sorted(ROOT_KEYS)}")
    if type(catalog["schemaVersion"]) is not int or catalog["schemaVersion"] != 1:
        fail("schemaVersion must be 1")
    if not isinstance(catalog["skills"], list):
        fail("skills must be an array")

    seen_ids: set[str] = set()
    seen_subpaths: set[str] = set()
    entries: list[tuple[str, str, str, bool]] = []

    for index, item in enumerate(catalog["skills"]):
        if not isinstance(item, dict) or set(item) != SKILL_KEYS:
            fail(f"skills[{index}] must contain exactly: {sorted(SKILL_KEYS)}")

        skill_id = require_string(item["id"], "id", f"skills[{index}]")
        if not ID_PATTERN.fullmatch(skill_id):
            fail(f"{skill_id}: id must be lowercase kebab-case")
        if skill_id in seen_ids:
            fail(f"{skill_id}: duplicate id")
        seen_ids.add(skill_id)

        for field in ("name", "description", "category"):
            require_string(item[field], field, skill_id)

        subpath = require_string(item["subpath"], "subpath", skill_id)
        if subpath != f"skills/{skill_id}":
            fail(f"{skill_id}: subpath must be skills/{skill_id}")
        if subpath in seen_subpaths:
            fail(f"{skill_id}: duplicate subpath")
        seen_subpaths.add(subpath)

        ref = require_string(item["ref"], "ref", skill_id)
        if not REF_PATTERN.fullmatch(ref):
            fail(f"{skill_id}: ref must be a full lowercase commit SHA")

        providers = item["providers"]
        if not isinstance(providers, list) or not providers:
            fail(f"{skill_id}: providers must be a non-empty array")
        if any(not isinstance(provider, str) or provider not in PROVIDERS for provider in providers):
            fail(f"{skill_id}: providers must use values from {sorted(PROVIDERS)}")
        if len(providers) != len(set(providers)):
            fail(f"{skill_id}: providers must be unique values from {sorted(PROVIDERS)}")

        if not isinstance(item["hasScripts"], bool):
            fail(f"{skill_id}: hasScripts must be boolean")

        requirements = item["requirements"]
        if not isinstance(requirements, list) or any(
            not isinstance(value, str) or not value.strip() for value in requirements
        ):
            fail(f"{skill_id}: requirements must contain non-empty strings")
        if len(requirements) != len(set(requirements)):
            fail(f"{skill_id}: requirements must contain unique non-empty strings")

        entries.append((skill_id, subpath, ref, item["hasScripts"]))

    if not SKILLS_PATH.is_dir():
        fail("skills/ directory is missing")

    package_ids = {
        path.name
        for path in SKILLS_PATH.iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    unexpected = sorted(path.name for path in SKILLS_PATH.iterdir() if path.name not in package_ids)
    if unexpected:
        fail(f"skills/ contains non-package entries: {unexpected}")
    if package_ids != seen_ids:
        fail(
            "catalog/package coverage differs: "
            f"catalog-only={sorted(seen_ids - package_ids)}, "
            f"directory-only={sorted(package_ids - seen_ids)}"
        )

    for skill_id, subpath, ref, has_scripts in entries:
        validate_worktree_package(skill_id, subpath, has_scripts)
        validate_pinned_package(skill_id, subpath, ref)

    return len(entries)


def main() -> int:
    try:
        count = validate()
    except ValidationError as error:
        print(f"catalog validation failed: {error}", file=sys.stderr)
        return 1
    print(f"catalog validation passed: {count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
