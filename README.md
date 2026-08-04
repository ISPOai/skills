# ISPO Skills

Project-installable skills for ISPO agents, sourced from curated upstream
collections including
[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
and [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills),
and [mattpocock/skills](https://github.com/mattpocock/skills).

Each package lives under `skills/<id>/` with one root `SKILL.md`, its governing
license, and an `UPSTREAM.md` attribution file. `catalog.json` is the
machine-readable registry consumed by ISPO. Catalog entries pin packages to an
immutable content commit.

## Catalog

| Category | Skills |
|---|---:|
| Apple & Personal Devices | 4 |
| Autonomous AI Agents | 4 |
| Document Processing | 4 |
| Data & Analysis | 14 |
| Business & Marketing | 40 |
| Communication & Writing | 26 |
| Creative & Media | 37 |
| MLOps | 5 |
| Productivity & Organization | 50 |
| Research | 4 |
| Smart Home | 1 |
| Social Media | 6 |
| Software Development | 16 |
| **Total** | **211** |

Multi-skill repositories listed in the source catalog are expanded into their
individual installable packages. Packages may declare external tools or services
in the catalog's `requirements` field.

## Deliberate exclusions

| Source entry | Reason |
|---|---|
| Anthropic `docx`, `pdf`, `pptx`, and `xlsx` | Their package license expressly prohibits reproduction and redistribution. |
| CSV Data Summarizer | The upstream repository publishes no software license, so redistribution is not authorized. |
| `n8n-skills` | Bundled generated node/template content cites n8n's Sustainable Use License but omits the promised attribution manifest; publication is blocked until provenance and redistribution rights are verified. |
| `computer-use`, `dogfood`, `hermes-agent-skill-authoring`, `inspecting-hermes-desktop-dom`, `plan`, `research-paper-writing`, `teams-meeting-pipeline`, `touchdesigner-mcp` | These packages require Hermes-only tools, source-tree internals, desktop services, or delegation semantics unavailable to an installed project skill. |
| `brainstorming`, `competitive-ads-extractor`, `creative-brief-selector`, `deep-research`, `image-enhancer`, `tapestry` | These packages were incomplete, coupled to absent companion skills or private portfolio state, depended on obsolete APIs, or promised operations without a runnable implementation. |

The dead upstream link for `root-cause-tracing` is preserved from the last
licensed revision where that exact package existed.

## Validation

Validate catalog coverage, immutable refs, package structure, provenance,
redistribution rights, portable frontmatter, local links, helper syntax,
runtime-path assumptions, and declared dependencies before publishing:

```sh
python3 scripts/validate_catalog.py
```
