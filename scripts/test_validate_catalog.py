#!/usr/bin/env python3
"""Focused tests for actionable catalog portability validation."""

from __future__ import annotations

import unittest

from scripts.validate_catalog import ValidationError, validate_skill_portability


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
