---
name: domain-modeling
description: Build and sharpen a project's domain glossary and sparingly record ADRs. Use when pinning terminology, maintaining CONTEXT.md, or when another skill needs the domain model updated. Glossary only — product direction stays in .ispo/spec.md.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* `CONTEXT.md` for vocabulary is not this skill.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Hard split (do not blur)

| Document | Holds |
| --- | --- |
| `CONTEXT.md` | Glossary terms only — what words mean, what to avoid |
| `.ispo/spec.md` | Product direction, workflows, acceptance criteria, roadmap |
| `docs/adr/` | Hard-to-reverse implementation trade-offs |
| `devlog.md` | Hard-earned evidence and decisions with verification |

Never treat `CONTEXT.md` as a spec, scratch pad, or implementation log.

Do **not** rewrite user-authored `AGENTS.md` or `CLAUDE.md`.

## File structure

Most projects have a single context:

```
/
├── CONTEXT.md
├── docs/adr/
├── .ispo/spec.md
└── src/
```

If `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. Create files lazily — only when you have something to write.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with `CONTEXT.md`, call it out immediately.

### Sharpen fuzzy language

Propose a precise canonical term when language is vague or overloaded.

### Discuss concrete scenarios

Stress-test relationships with specific edge-case scenarios.

### Cross-reference with code

When the user states how something works, check whether the code agrees. Surface contradictions.

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` immediately. Use [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md).

### Offer ADRs sparingly

Only offer an ADR when all three are true:

1. **Hard to reverse** — changing your mind later is costly
2. **Surprising without context** — a future reader will wonder why
3. **Real trade-off** — genuine alternatives were considered

If any is missing, skip the ADR. Use [ADR-FORMAT.md](ADR-FORMAT.md).

If the decision is product-facing (what the app should do for users), update `.ispo/spec.md` instead of forcing it into an ADR or glossary entry.
