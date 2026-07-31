#!/usr/bin/env python3
"""Validate the published skill catalog and every pinned package."""

from __future__ import annotations

import ast
import json
import re
import stat
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


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
PROVIDER_ENVIRONMENT_PATTERN = re.compile(
    r"\b(?P<provider>Hermes(?: Agent)?|Claude(?: Code)?|Codex)[ -]+managed environment\b",
    re.IGNORECASE,
)
AMBIENT_UV_INSTALL_PATTERN = re.compile(r"\buv\s+pip\s+install\b", re.IGNORECASE)
UV_WITH_PATTERN = re.compile(
    r"\buv\s+run[^\n]*?--with(?:=|\s+)(?P<package>[A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_REFERENCE_PATTERN = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
LEGACY_RUNTIME_PATTERNS = {
    "Hermes home path": re.compile(
        r"\$\{?HERMES_HOME\}?|(?<![A-Za-z0-9_])(?:~/)?\.hermes/|/home/bb/hermes-agent",
        re.IGNORECASE,
    ),
    "Hermes terminal call": re.compile(r"\bterminal\s*\(\s*command\s*=", re.IGNORECASE),
    "Hermes process call": re.compile(r"\bprocess\s*\(\s*action\s*=", re.IGNORECASE),
    "Hermes skill call": re.compile(r"\b(?:skill_view|skill_manage)\s*\(", re.IGNORECASE),
    "Hermes delegation call": re.compile(r"\bdelegate_task\s*\(", re.IGNORECASE),
    "hosted-only workspace path": re.compile(r"/mnt/(?:user-data|data)(?:/|\b)"),
    "unsafe system-Python override": re.compile(r"--break-system-packages"),
    "disabled browser sandbox": re.compile(r"--(?:no-sandbox|disable-setuid-sandbox|disable-web-security)"),
}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".js", ".cjs", ".mjs", ".ts", ".tsx"}
NON_RUNTIME_DIRECTORIES = {"assets", "references", "templates", "tests"}
FRONTMATTER_KEYS = {"name", "description"}
# This package documents an external product whose real configuration and tool
# names are necessarily Hermes-specific. It must still pass every other catalog
# check, including the ban on hosted-only workspace paths.
PRODUCT_RUNTIME_DOCUMENTATION = {"hermes-agent"}
RESTRICTED_REDISTRIBUTION_MARKERS = {
    "ADDITIONAL RESTRICTIONS",
    "users may not reproduce",
    "users may not distribute",
}


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
    descriptions: list[str] = []
    keys: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key_match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):", line)
        if key_match:
            keys.append(key_match.group(1))
        match = re.match(r"^name:\s*(.+?)\s*$", line)
        if match:
            names.append(match.group(1).strip().strip("\"'"))
        match = re.match(r"^description:\s*(.*?)\s*$", line)
        if match:
            descriptions.append(match.group(1).strip().strip("\"'"))
    else:
        fail(f"{source}: SKILL.md frontmatter is not closed")

    unexpected_keys = sorted(set(keys) - FRONTMATTER_KEYS)
    if unexpected_keys:
        fail(
            f"{source}: SKILL.md frontmatter may contain only name and description; "
            f"remove {unexpected_keys}"
        )

    if len(names) != 1 or not names[0]:
        fail(f"{source}: SKILL.md frontmatter must contain exactly one name")
    if len(descriptions) != 1:
        fail(f"{source}: SKILL.md frontmatter must contain exactly one description")
    if not descriptions[0] and not any(
        line.startswith((" ", "\t")) and line.strip()
        for line in lines[2 : lines.index("---", 1)]
    ):
        fail(f"{source}: SKILL.md description must not be empty")
    return names[0]


def markdown_without_code(markdown: str) -> str:
    """Remove fenced and inline code before interpreting Markdown links."""
    visible: list[str] = []
    fence: str | None = None
    for line in markdown.splitlines():
        marker = re.match(r"^\s*(```+|~~~+)", line)
        if marker:
            delimiter = marker.group(1)[0]
            if fence is None:
                fence = delimiter
            elif fence == delimiter:
                fence = None
            visible.append("")
            continue
        visible.append("" if fence else re.sub(r"`[^`\n]*`", "", line))
    return "\n".join(visible)


def validate_local_skill_links(
    skill_id: str,
    package: Path,
    markdown: str,
    source: Path | None = None,
) -> None:
    """Ensure local Markdown links stay inside the package and resolve."""
    visible = markdown_without_code(markdown)
    raw_targets = MARKDOWN_LINK_PATTERN.findall(visible)
    raw_targets.extend(MARKDOWN_REFERENCE_PATTERN.findall(visible))
    package_root = package.resolve()
    source = source or package / "SKILL.md"

    for raw_target in raw_targets:
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if (
            not target
            or target.startswith(("/", "//"))
            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
        ):
            continue
        target = unquote(target)
        candidate = (source.parent / target).resolve()
        try:
            candidate.relative_to(package_root)
        except ValueError:
            fail(
                f"{skill_id}: {source.relative_to(package)} link escapes its "
                f"installable package: {target}"
            )
        if not candidate.exists():
            fail(
                f"{skill_id}: {source.relative_to(package)} link is missing from its "
                f"package: {target}"
            )


def validate_python_scripts(skill_id: str, package: Path) -> None:
    """Parse bundled Python helpers without importing or executing them."""
    for script in sorted(package.rglob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except (OSError, UnicodeError, SyntaxError) as error:
            fail(f"{skill_id}: bundled Python helper cannot be parsed: {script.name}: {error}")


def validate_package_licensing(skill_id: str, package: Path) -> None:
    """Require explicit provenance and reject known non-redistributable packages."""
    upstream = package / "UPSTREAM.md"
    if not upstream.is_file():
        fail(f"{skill_id}: package must include UPSTREAM.md provenance")
    licenses = sorted(
        path for path in package.iterdir() if path.is_file() and path.name.startswith("LICENSE")
    )
    if not licenses:
        fail(f"{skill_id}: package must include a root LICENSE file")
    for license_path in licenses:
        contents = license_path.read_text(encoding="utf-8", errors="replace")
        lowered = contents.lower()
        for marker in RESTRICTED_REDISTRIBUTION_MARKERS:
            if marker.lower() in lowered:
                fail(
                    f"{skill_id}: {license_path.name} contains redistribution "
                    f"restrictions incompatible with a public installable catalog"
                )


def package_has_runtime_helpers(package: Path) -> bool:
    """Return whether a package contains executable helper code, wherever vendored."""
    for path in package.rglob("*"):
        relative_parts = path.relative_to(package).parts
        if (
            path.is_file()
            and path.suffix.lower() in EXECUTABLE_SUFFIXES
            and not NON_RUNTIME_DIRECTORIES.intersection(relative_parts)
        ):
            return True
    return False


def validate_package_portability(skill_id: str, package: Path) -> None:
    """Reject concrete calls and paths that only exist in the upstream runtime."""
    checked_suffixes = {".md", ".py", ".sh", ".js", ".cjs", ".mjs"}
    for path in sorted(package.rglob("*")):
        if (
            not path.is_file()
            or path.name == "UPSTREAM.md"
            or path.name.startswith("LICENSE")
            or path.suffix.lower() not in checked_suffixes
        ):
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            fail(f"{skill_id}: cannot inspect {path.relative_to(package)}: {error}")
        for label, pattern in LEGACY_RUNTIME_PATTERNS.items():
            if skill_id in PRODUCT_RUNTIME_DOCUMENTATION and label.startswith("Hermes "):
                continue
            if pattern.search(contents):
                fail(
                    f"{skill_id}: {path.relative_to(package)} contains a {label}; "
                    "use capability-based instructions and provider-neutral state paths"
                )


def requirement_name(requirement: str) -> str:
    """Return the normalized leading tool/package token from a requirement."""
    token = re.split(r"[\s<>=!~;\[]", requirement.strip(), maxsplit=1)[0]
    return token.lower().replace("_", "-")


def validate_skill_portability(
    skill_id: str,
    markdown: str,
    providers: list[str],
    requirements: list[str],
    has_scripts: bool = False,
) -> None:
    """Reject high-confidence provider and ambient-environment assumptions."""
    provider_claim = PROVIDER_ENVIRONMENT_PATTERN.search(markdown)
    if provider_claim:
        claim = provider_claim.group("provider").lower()
        claim_provider = "claude" if claim.startswith("claude") else claim.split()[0]
        if len(providers) > 1 or claim_provider not in providers:
            fail(
                f"{skill_id}: provider-specific environment claim "
                f"{provider_claim.group(0)!r} is incompatible with providers {providers}; "
                "state concrete tool and path prerequisites instead"
            )

    if has_scripts and AMBIENT_UV_INSTALL_PATTERN.search(markdown):
        fail(
            f"{skill_id}: 'uv pip install' mutates an ambient environment; "
            "invoke the bundled helper with an atomic "
            "'uv run --with <package>' command instead"
        )

    declared = {requirement_name(requirement) for requirement in requirements}
    atomic_dependencies = list(UV_WITH_PATTERN.finditer(markdown))
    if atomic_dependencies and "uv" not in declared:
        fail(f"{skill_id}: uses uv run but catalog requirements do not declare uv")
    for match in atomic_dependencies:
        package = match.group("package")
        if requirement_name(package) not in declared:
            fail(
                f"{skill_id}: uv run --with dependency {package!r} is not declared "
                "in catalog requirements"
            )


def validate_worktree_package(
    skill_id: str,
    subpath: str,
    has_scripts: bool,
    providers: list[str],
    requirements: list[str],
) -> None:
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

    markdown = (package / "SKILL.md").read_text(encoding="utf-8")
    current_name = skill_name(markdown, str((package / "SKILL.md").relative_to(ROOT)))
    if current_name != skill_id:
        fail(f"{skill_id}: SKILL.md name is {current_name!r}")
    for document in sorted(package.rglob("*.md")):
        if document.name == "UPSTREAM.md" or document.name.startswith("LICENSE"):
            continue
        validate_local_skill_links(
            skill_id,
            package,
            document.read_text(encoding="utf-8"),
            source=document,
        )
    validate_python_scripts(skill_id, package)
    validate_package_licensing(skill_id, package)
    validate_package_portability(skill_id, package)
    validate_skill_portability(
        skill_id,
        markdown,
        providers,
        requirements,
        has_scripts=has_scripts,
    )

    scripts_present = package_has_runtime_helpers(package)
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
    entries: list[tuple[str, str, str, bool, list[str], list[str]]] = []

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

        entries.append(
            (skill_id, subpath, ref, item["hasScripts"], providers, requirements)
        )

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

    for skill_id, subpath, ref, has_scripts, providers, requirements in entries:
        validate_worktree_package(
            skill_id,
            subpath,
            has_scripts,
            providers,
            requirements,
        )
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
