# Port Notes — baoyu-infographic

Ported from [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.56.1.

## Changes from upstream

Only `SKILL.md` was modified. All 45 reference files are verbatim copies.

### SKILL.md adaptations

| Change | Upstream | Catalog version |
|--------|----------|--------|
| Metadata namespace | `openclaw` | Catalog metadata |
| Trigger | `/baoyu-infographic` slash command | Natural language skill matching |
| User config | EXTEND.md file (project/user/XDG paths) | Removed — not part of the portable workflow |
| User prompts | `AskUserQuestion` (batched) | Provider-neutral user confirmation |
| Image generation | baoyu-imagine (Bun/TypeScript) | Any available image-generation capability, with a prompt-only fallback |
| Platform support | Linux/macOS/Windows/WSL/PowerShell | Linux/macOS only |
| File operations | Bash commands | Any available file capability |

### What was preserved

- All layout definitions (21 files)
- All style definitions (21 files)
- Core reference files (analysis-framework, base-prompt, structured-content-template)
- Recommended combinations table
- Keyword shortcuts table
- Core principles and workflow structure
- Author, version, homepage attribution

## Syncing with upstream

To pull upstream updates:
```bash
# Compare versions
curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-infographic/SKILL.md | head -5
# Look for version: line

# Diff reference files
diff <(curl -sL https://raw.githubusercontent.com/.../references/layouts/bento-grid.md) references/layouts/bento-grid.md
```

Reference files can be overwritten directly (they're unchanged from upstream). SKILL.md must be manually merged because it contains catalog-specific portability adaptations.
