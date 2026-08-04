---
name: spike
description: Build a throwaway spike or prototype to answer a design question — a runnable logic harness or several UI variants inside an ISPO project. Use when sanity-checking a state model, comparing UI directions, or validating feasibility before a real build.
---

# Spike / Throwaway Prototype

A spike is **throwaway code that answers a question**. The question decides the shape.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a tiny interactive terminal (or script) harness that pushes the state machine through hard cases.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations switchable inside the project iframe.

If the question is ambiguous and the user isn't reachable, default to whichever branch matches the surrounding code and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked.** Locate the prototype close to where it will be used, but name it so a casual reader sees it is not production.
2. **One command to run.** Use the project's existing task runner (`pnpm <script>`, etc.).
3. **No persistence by default.** State lives in memory. Persistence is what you are checking, not what you depend on.
4. **Skip the polish.** No tests, no abstractions, no error handling beyond runnable. Learn fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), show the full relevant state.
6. **No new authority.** A spike does not call Confirm plan, install skills, or request grants "just in case."
7. **Capture when done.** Fold any validated decision into real code and record the verdict in `.ispo/spec.md` or an ADR. Keep the prototype itself only as a primary source on a throwaway branch (or delete it). Main keeps the validated decision, not the scaffolding.

## When NOT to use

- The answer is knowable from docs or reading code — research instead of building
- The work is already on the production path after Confirm plan — use `test-driven-development`
- The idea is already validated — implement for real
