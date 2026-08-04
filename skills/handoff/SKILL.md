---
name: handoff
description: Compact the current conversation into a handoff document in the OS temp directory so another agent can continue. User-invoked. Use when ending a session or preparing a fresh agent to pick up the work.
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to the temporary directory of the user's OS — **not** the project workspace.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Contents

Include:

- Goal and current status
- Decisions already made (link out; don't restate large docs)
- Exact next actions
- Risks / open questions
- **Suggested skills** — ISPO catalog ids that fit the next session (for example `grilling`, `test-driven-development`, `systematic-debugging`, `spike`, `domain-modeling`, `codebase-design`, `improve-codebase-architecture`, `ispo-sdk` if present in the project)

## Rules

- Do not duplicate content already captured in artifacts. Reference `.ispo/spec.md`, `devlog.md`, `CONTEXT.md`, `docs/adr/`, commits, and diffs by path or URL.
- Redact secrets, tokens, API keys, passwords, and personally identifiable information. Never paste grant tokens or connector credentials.
- If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
- Tell the user the absolute path to the handoff file when done.
