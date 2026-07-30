# ISPO Skills

Project-installable skills for ISPO agents, sourced from the six selected
categories in
[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills).

Each package lives under `skills/<id>/` with one root `SKILL.md`, its governing
license, and an `UPSTREAM.md` attribution file. `catalog.json` is the
machine-readable registry consumed by ISPO. Catalog entries pin packages to an
immutable content commit.

## Catalog

| Category | Skills |
|---|---:|
| Document Processing | 4 |
| Data & Analysis | 15 |
| Business & Marketing | 41 |
| Communication & Writing | 23 |
| Creative & Media | 21 |
| Productivity & Organization | 42 |
| **Total** | **146** |

Multi-skill repositories listed in the source catalog are expanded into their
individual installable packages. Packages may declare external tools or services
in the catalog's `requirements` field.

## Deliberate exclusions

| Source entry | Reason |
|---|---|
| Anthropic `docx`, `pdf`, `pptx`, and `xlsx` | Their package license expressly prohibits reproduction and redistribution. |
| CSV Data Summarizer | The upstream repository publishes no software license, so redistribution is not authorized. |

The dead upstream links for `root-cause-tracing` and `tapestry` are preserved
from the last licensed revisions where those exact packages existed.
