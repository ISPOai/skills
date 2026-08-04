---
name: test-driven-development
description: Test-driven development with a red-green loop at pre-agreed seams. Use when building features or fixing bugs test-first, mentioning red-green-refactor, or wanting integration-style tests in an ISPO project.
---

# Test-Driven Development

TDD is the red → green loop. This skill makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle — consult them before and during the loop, not after.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Before you start

1. Read `.ispo/spec.md` for product intent in the area you are changing.
2. Read `CONTEXT.md` if it exists so test names and interface vocabulary match the project's domain language.
3. Respect ADRs under `docs/adr/` in the area you are touching.
4. Call `get_project_context` when you need the host snapshot (surface, installed skills, recent evidence).

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams — where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything — agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

Prefer existing seams. Prefer the highest seam that still gives a sharp signal. For ISPO project UI, a seam may be a pure module boundary, a command/RPC surface, or a rendered DOM assertion via MCP after a controlled action — do not reach past the interface into private helpers.

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does, so it passes by construction. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Work in **vertical slices** instead — one test → one implementation → repeat.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** Keep red→green tight. Broaden structure in a later review pass after the slice is green and verified.
- **Close the slice with ISPO verification.** For project-app UI changes, run the verify loop above after green. For pure logic, run `typecheck`, the focused tests, commit the verified slice, then `append_devlog_entry` citing the test command and results.
