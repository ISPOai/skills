"""Resolve provider-neutral, versioned runtime storage for NotebookLM helpers."""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent


def get_runtime_dir() -> Path:
    """Return an external cache directory keyed by dependencies and Python."""
    override = os.environ.get("NOTEBOOKLM_SKILL_RUNTIME_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    xdg_cache = os.environ.get("XDG_CACHE_HOME", "").strip()
    cache_root = Path(xdg_cache).expanduser() if xdg_cache else Path.home() / ".cache"
    requirements = (SKILL_DIR / "requirements.txt").read_bytes()
    digest = hashlib.sha256(requirements).hexdigest()[:12]
    version = f"py{sys.version_info.major}.{sys.version_info.minor}-{digest}"
    return cache_root / "ispo" / "notebooklm" / version


def get_venv_dir() -> Path:
    return get_runtime_dir() / "venv"


def get_venv_python() -> Path:
    venv_dir = get_venv_dir()
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"
