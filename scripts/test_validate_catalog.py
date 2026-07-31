#!/usr/bin/env python3
"""Focused tests for actionable catalog portability validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_catalog import (
    ValidationError,
    skill_name,
    package_has_runtime_helpers,
    validate_package_licensing,
    validate_local_skill_links,
    validate_package_portability,
    validate_python_scripts,
    validate_skill_portability,
)


class SkillPortabilityValidationTests(unittest.TestCase):
    def test_accepts_atomic_declared_uv_dependency(self) -> None:
        validate_skill_portability(
            "portable-skill",
            "uv run --no-project --with youtube-transcript-api python helper.py",
            ["claude", "codex"],
            ["uv", "youtube-transcript-api"],
        )

    def test_rejects_provider_managed_environment_claim_for_portable_skill(self) -> None:
        with self.assertRaisesRegex(ValidationError, "provider-specific environment claim"):
            validate_skill_portability(
                "provider-bound-skill",
                "Install this into the same Hermes-managed environment.",
                ["claude", "codex"],
                [],
            )

    def test_requires_description_frontmatter(self) -> None:
        with self.assertRaisesRegex(ValidationError, "exactly one description"):
            skill_name("---\nname: example\n---\n", "SKILL.md")

    def test_rejects_provider_specific_frontmatter(self) -> None:
        with self.assertRaisesRegex(ValidationError, "only name and description"):
            skill_name(
                "---\nname: example\ndescription: Portable.\nallowed-tools: Bash\n---\n",
                "SKILL.md",
            )

    def test_rejects_missing_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            with self.assertRaisesRegex(ValidationError, "missing from its package"):
                validate_local_skill_links(
                    "example",
                    package,
                    "Read [the reference](references/missing.md).",
                )

    def test_rejects_link_outside_installable_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "example"
            package.mkdir()
            (package.parent / "peer.md").write_text("peer", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "escapes its installable package"):
                validate_local_skill_links("example", package, "[peer](../peer.md)")

    def test_ignores_links_inside_code_examples(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            validate_local_skill_links(
                "example",
                Path(directory),
                "```markdown\n[placeholder](missing.md)\n```",
            )

    def test_rejects_invalid_bundled_python(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scripts = Path(directory) / "scripts"
            scripts.mkdir()
            (scripts / "broken.py").write_text("if True print('no')\n", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "cannot be parsed"):
                validate_python_scripts("example", Path(directory))

    def test_rejects_restricted_redistribution_license(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "UPSTREAM.md").write_text("# Upstream\n", encoding="utf-8")
            (package / "LICENSE.txt").write_text(
                "ADDITIONAL RESTRICTIONS: users may not distribute this material.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "redistribution restrictions"):
                validate_package_licensing("example", package)

    def test_requires_package_provenance_and_license(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValidationError, "UPSTREAM.md"):
                validate_package_licensing("example", Path(directory))

    def test_detects_runtime_helper_outside_scripts_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            core = package / "core"
            core.mkdir()
            (core / "helper.py").write_text("print('ok')\n", encoding="utf-8")
            self.assertTrue(package_has_runtime_helpers(package))

    def test_ignores_code_assets_for_runtime_helper_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            assets = package / "assets"
            assets.mkdir()
            (assets / "starter.js").write_text("export {};\n", encoding="utf-8")
            self.assertFalse(package_has_runtime_helpers(package))

    def test_rejects_legacy_runtime_path_in_bundled_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            reference = package / "references" / "setup.md"
            reference.parent.mkdir()
            reference.write_text("Store state under ~/.hermes/data.", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "Hermes home path"):
                validate_package_portability("example", package)

    def test_allows_hermes_paths_only_in_hermes_product_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "SKILL.md").write_text(
                "Configure ~/.hermes/config.yaml.\n", encoding="utf-8"
            )
            validate_package_portability("hermes-agent", package)

    def test_rejects_hosted_path_in_hermes_product_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "SKILL.md").write_text(
                "Save output under /mnt/data.\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "hosted-only workspace path"):
                validate_package_portability("hermes-agent", package)

    def test_rejects_legacy_runtime_tool_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "SKILL.md").write_text(
                'terminal(command="tool --version")\n', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "Hermes terminal call"):
                validate_package_portability("example", package)

    def test_rejects_hosted_only_workspace_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "SKILL.md").write_text(
                "Save the result under /mnt/user-data/outputs.\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "hosted-only workspace path"):
                validate_package_portability("example", package)

    def test_rejects_browser_sandbox_disabling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "helper.js").write_text(
                "launch({args: ['--no-sandbox']});\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "disabled browser sandbox"):
                validate_package_portability("example", package)

    def test_rejects_ambient_uv_install(self) -> None:
        with self.assertRaisesRegex(ValidationError, "mutates an ambient environment"):
            validate_skill_portability(
                "ambient-install-skill",
                "Run uv pip install example-package before using the helper.",
                ["claude", "codex"],
                ["uv", "example-package"],
                has_scripts=True,
            )

    def test_allows_declared_cli_setup_without_a_bundled_helper(self) -> None:
        validate_skill_portability(
            "external-cli-skill",
            "Run uv pip install example-cli, then invoke example-cli.",
            ["claude", "codex"],
            ["uv", "example-cli"],
            has_scripts=False,
        )

    def test_rejects_undeclared_uv_tool(self) -> None:
        with self.assertRaisesRegex(ValidationError, "do not declare uv"):
            validate_skill_portability(
                "undeclared-uv-skill",
                "uv run --with example-package python helper.py",
                ["claude", "codex"],
                ["example-package"],
            )

    def test_rejects_undeclared_atomic_dependency(self) -> None:
        with self.assertRaisesRegex(ValidationError, "is not declared"):
            validate_skill_portability(
                "undeclared-package-skill",
                "uv run --with example-package python helper.py",
                ["claude", "codex"],
                ["uv"],
            )


if __name__ == "__main__":
    unittest.main()
