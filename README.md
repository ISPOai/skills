# ISPO Skills

Project-installable skills for ISPO agents, sourced from curated upstream
collections including
[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
and [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills).

Each package lives under `skills/<id>/` with one root `SKILL.md`, its governing
license, and an `UPSTREAM.md` attribution file. `catalog.json` is the
machine-readable registry consumed by ISPO. Catalog entries pin packages to an
immutable content commit.

## Catalog

| Category | Skills |
|---|---:|
| Apple & Personal Devices | 4 |
| Autonomous AI Agents | 5 |
| Document Processing | 4 |
| Data & Analysis | 15 |
| Business & Marketing | 41 |
| Communication & Writing | 24 |
| Creative & Media | 40 |
| MLOps | 5 |
| Productivity & Organization | 54 |
| Research | 5 |
| Smart Home | 1 |
| Social Media | 1 |
| Software Development | 17 |
| **Total** | **216** |

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

## Validation

Validate catalog coverage, package structure, and immutable refs before
publishing:

```sh
python3 scripts/validate_catalog.py
```
