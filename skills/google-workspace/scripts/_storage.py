"""Resolve provider-neutral persistent storage for Google Workspace scripts.

Credentials must not live in a project or installed skill directory. Users may
set ``GOOGLE_WORKSPACE_HOME`` explicitly. Otherwise use
``$XDG_CONFIG_HOME/ispo/google-workspace`` or
``~/.config/ispo/google-workspace``.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_google_workspace_home() -> Path:
    """Return the persistent config/credential directory."""
    override = os.environ.get("GOOGLE_WORKSPACE_HOME", "").strip()
    if override:
        return Path(override).expanduser()
    xdg_config = os.environ.get("XDG_CONFIG_HOME", "").strip()
    config_root = Path(xdg_config).expanduser() if xdg_config else Path.home() / ".config"
    return config_root / "ispo" / "google-workspace"


def display_google_workspace_home() -> str:
    """Return a user-friendly ``~/``-shortened display string."""
    home = get_google_workspace_home()
    try:
        return "~/" + str(home.relative_to(Path.home()))
    except ValueError:
        return str(home)
