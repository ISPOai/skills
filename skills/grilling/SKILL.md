---
name: grilling
description: Relentless interview loop to stress-test a plan, decision, or idea until every decision-tree branch is resolved. Use when the user wants to be grilled, align before building, or another skill needs a grilling session. Model-invoked reusable loop.
---

# Grilling

Interview the user relentlessly about every aspect of the topic until you reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Rules

- Ask **one question at a time**, waiting for feedback before continuing. Multiple questions at once is bewildering.
- If a *fact* can be found by exploring the environment, look it up rather than asking. Prefer `get_project_context`, `.ispo/spec.md`, `CONTEXT.md`, ADRs, and the filesystem.
- The *decisions* are the user's — put each one to them and wait for an answer.
- Lead with your recommended answer so they can accept it in a word when the choice is clear.
- **Do not act** on the plan (edit production code, install skills, seed grants, call Confirm plan, start a build) until the user confirms you have reached a shared understanding.
- When terminology crystallizes, you may use `domain-modeling` to update the glossary — still no build work.

## Done when

The user confirms shared understanding. Summarize the resolved decisions briefly. Hand back to the caller (or wait for the user to ask for the next step such as plan updates or implementation).
