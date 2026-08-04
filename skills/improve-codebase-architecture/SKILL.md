---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report in a temp directory, then grill through the candidate you pick. Use when rescuing a ball-of-mud area, improving testability, or finding architectural leverage. User-invoked orchestration skill.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


This skill is **user-invoked orchestration**. Prefer it when the user asks to improve architecture, deepen modules, or rescue a tangled area — not as a silent background rewrite.

It is informed by the project's domain model and built on shared design vocabulary:

- Use the `codebase-design` skill for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles. Use those terms exactly — don't drift into "service," "API," or "boundary" as architecture synonyms.
- Domain language in `CONTEXT.md` (glossary) names good seams; ADRs in `docs/adr/` record decisions this skill should not casually re-litigate.
- Product intent stays in `.ispo/spec.md` — this skill does not publish tickets or replace Confirm plan.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening pays off by making future changes easier, so weight recently changed areas.

- If the user named a direction, take it.
- Otherwise walk recent commit history for hot spots, then explore those paths first.

Read `.ispo/spec.md` for product context, `CONTEXT.md` for glossary terms, and ADRs in the area you're touching.

Explore organically (parallel explore agents when the harness supports it; otherwise sequential) and note friction:

- Understanding one concept requires bouncing between many small modules
- Modules are **shallow** — interface nearly as complex as the implementation
- Pure functions extracted only for testability while real bugs hide in call sites (no **locality**)
- Tightly-coupled modules leak across seams
- Areas that are untested or hard to test through their current interface

Apply the **deletion test** to anything you suspect is shallow.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `architecture-review-<timestamp>.html`. Open it for the user (`open` on macOS, `xdg-open` on Linux, `start` on Windows) and tell them the absolute path.

This report is a **host-side artifact**, not an ISPO Store surface, Project Home page, or committed project file.

See [HTML-REPORT.md](HTML-REPORT.md) for scaffold and card structure. Use Tailwind/Mermaid via CDN. Each candidate gets Files, Problem, Solution, Benefits (locality/leverage/tests), Before/After visualisation, and recommendation strength (`Strong` / `Worth exploring` / `Speculative`).

**Use `CONTEXT.md` vocabulary for the domain, and `codebase-design` vocabulary for architecture.**

**ADR conflicts**: only surface a candidate that contradicts an ADR when friction is real enough to reopen it. Mark that clearly. Don't list every theoretical refactor an ADR forbids.

Do NOT propose interfaces yet. After the file is written, ask: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, run the `grilling` skill to walk the decision tree — constraints, dependencies, deepened module shape, what sits behind the seam, what tests survive.

As decisions crystallize, use `domain-modeling` to keep the glossary/ADRs current:

- Naming a deepened module after a concept not in `CONTEXT.md`? Add the term (glossary only).
- Sharpening a fuzzy term? Update `CONTEXT.md`.
- User rejects with a load-bearing reason? Offer an ADR when the three ADR criteria in `domain-modeling` hold.
- Exploring alternative interfaces? Use `codebase-design` and its design-it-twice guidance.

Do not publish to an issue tracker. Do not edit grants. When implementation begins, prefer `test-driven-development` at the agreed seams and close with the ISPO verify loop.
