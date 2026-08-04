---
name: systematic-debugging
description: Disciplined diagnosis loop for hard bugs and performance regressions in ISPO projects. Use when diagnosing, debugging, or investigating something broken, failing, throwing, or slow. Reproduce with a tight feedback loop before hypothesizing.
---

# Systematic Debugging

A discipline for hard bugs. Skip phases only when explicitly justified.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


When exploring the codebase, read `.ispo/spec.md`, `CONTEXT.md` (if it exists) for domain vocabulary, and ADRs in the area you're touching. Call `get_project_context` for the host project snapshot and recent evidence.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug — one that goes red on _this_ bug — you will find the cause. If you don't have one, no amount of staring at code will save you.

Spend disproportionate effort here. Be aggressive. Be creative. Refuse to give up.

### Ways to construct one — try them in this order for ISPO projects

1. **Failing test** at whatever seam reaches the bug — unit, integration, or project test.
2. **ISPO console / network / page events** — `get_console`, `get_network`, `get_page_events` against the live project frame.
3. **Rendered DOM signal** — `ui_outline`, then `query_dom` / `screenshot` asserting the user's exact symptom.
4. **Fresh build gate** — after code edits, `wait_for_fresh_build` so the frame under test is the build you just made.
5. **Host CDP scripts** — when the desktop renderer is sluggish, frozen, or leaking, use the host CDP tooling (`scripts/cdp/*` in the ISPO host checkout) rather than guessing from logs.
6. **CLI / fixture invocation** with a known-good snapshot when the bug is non-UI.
7. **Throwaway harness** exercising one code path with a single function call.
8. **Property / fuzz loop** when the bug is intermittent wrong output.
9. **Bisection harness** across commits or configs when the regression window is known.
10. **Generic browser automation (Playwright / Puppeteer) or curl** only after the ISPO MCP surfaces above cannot reach the symptom — and never install a harness-level browser/mail/calendar plugin for a capability ISPO already provides.

Build the right feedback loop, and the bug is 90% fixed.

### Tighten the loop

- Faster? Cache setup, skip unrelated init, narrow scope.
- Sharper? Assert the specific symptom, not "didn't crash".
- More deterministic? Pin time, seed RNG, isolate filesystem, freeze network.

A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is a debugging superpower.

### Non-deterministic bugs

Raise the reproduction rate until the bug is debuggable. Loop the trigger, add stress, narrow timing windows. A 50%-flake bug is debuggable; 1% is not.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for environment access, a captured artifact, or permission for temporary instrumentation. Do **not** proceed to hypothesise without a loop.

### Completion criterion — a tight loop that goes red

Phase 1 is done when you can name **one command or MCP sequence** you have already run at least once, and that is:

- **Red-capable** — drives the actual bug path and asserts the user's exact symptom.
- **Deterministic** (or a pinned high reproduction rate).
- **Fast** — seconds, not minutes.
- **Agent-runnable** without an ad-hoc human click train.

If you catch yourself reading code to build a theory before this exists, **stop**.

## Phase 2 — Reproduce + minimise

Run the loop. Watch it go red. Confirm it matches the user's symptom. Shrink the repro one cut at a time until every remaining element is load-bearing.

## Phase 3 — Hypothesise

Generate **3–5 ranked, falsifiable hypotheses** before testing any. Show the ranked list to the user before testing when they are available. Don't block if they are AFK.

Format: "If <cause>, then <probe> will make the bug disappear / worsen."

## Phase 4 — Instrument

Each probe maps to a specific Phase 3 prediction. Change one variable at a time.

Tool preference:

1. Debugger / REPL if available.
2. Targeted logs at distinguishing boundaries — tag every debug log with a unique prefix like `[DEBUG-a4f2]` for cleanup.
3. ISPO MCP reads (`get_console`, `query_dom`, etc.) before scattering logs.
4. For performance regressions: measure first (timing harness, profiler), then bisect. Never "log everything and grep".

## Phase 5 — Fix + regression test

Write the regression test **before the fix** only if a **correct seam** exists — one that exercises the real bug pattern at the call site.

1. Turn the minimised repro into a failing test (or MCP assertion sequence) at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 loop against the original scenario.
6. Close with the ISPO verify loop.

If no correct seam exists, that itself is the finding — architecture is preventing lockdown. Flag for `improve-codebase-architecture`.

## Phase 6 — Cleanup + post-mortem

Required before declaring done:

- Original Phase 1 loop no longer reproduces the bug
- Regression test / assertion passes (or missing seam is documented)
- All `[DEBUG-...]` instrumentation removed
- Throwaway prototypes deleted or clearly marked
- Correct hypothesis stated in the commit message
- `append_devlog_entry` (or `mark_devlog_gap`) cites the evidence

Then ask: what would have prevented this bug? If the answer is architectural, hand off to `improve-codebase-architecture` after the fix is in.
