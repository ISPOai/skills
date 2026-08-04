---
name: codebase-design
description: Shared vocabulary for designing deep modules — depth, seams, adapters, leverage, locality. Use when designing or improving a module interface, finding deepening opportunities, deciding where a seam goes, or making code more testable and AI-navigable.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever code is being designed or restructured. The aim is leverage for callers, locality for maintainers, and testability for everyone.

## ISPO project rules

These rules apply whenever this skill is used inside an ISPO project:

1. **Authority** — this skill never grants access. Do not edit `.ispo/project.json` grants, host grant stores, or install harness plugins for capabilities ISPO already mediates (`@ispo/sdk`, host connectors, powerbox, MCP tools). New authority goes through `request_grant` or Confirm plan only.
2. **Canonical docs** — product direction lives in `.ispo/spec.md` and project `devlog.md`. Do not invent `PLAN.md`, parallel PRDs, or issue-tracker specs as authority.
3. **Glossary vs spec** — optional `CONTEXT.md` is a **glossary only** (terms). Hard-to-reverse implementation trade-offs may become ADRs under `docs/adr/`. Product intent stays in `.ispo/spec.md`. Never treat `CONTEXT.md` as a second spec.
4. **Planning boundary** — alignment and grilling happen before Confirm plan / before acting. Do not install skills, seed grants, or start build work during a grill.
5. **Verify loop** (project-app changes): `typecheck` → `wait_for_fresh_build` → `get_console` → rendered QA with `query_dom` / `screenshot` (use `ui_outline` first when you need the semantic map) → `git commit` after DOM-confirmed success → `append_devlog_entry` (or `mark_devlog_gap`) citing MCP evidence. Typecheck alone is not success.
6. **Primitives first** — prefer ISPO MCP/SDK surfaces over generic browser/CLI substitutes when working in an ISPO project.
7. **Provider-neutral** — if parallel exploration helps, spawn parallel agents when the harness supports it; otherwise run sequential passes. Do not assume a Claude-Code-only Agent tool.


## Glossary

Use these terms exactly when talking about architecture. Do not substitute "service," "API," or "boundary" for them.

**Important for ISPO UI:** React **components** still exist as UI building blocks. Do not ban the word "component" for UI widgets. Do ban using "component" as a synonym for an architectural **module** or **seam**.

**Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. _Avoid as synonyms_: unit, service (when you mean module).

**Interface** — everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. _Avoid_: API, signature (too narrow).

**Implementation** — what's inside a module. Distinct from **Adapter**.

**Depth** — leverage at the interface: behaviour a caller (or test) can exercise per unit of interface they must learn. **Deep** = large behaviour behind a small interface. **Shallow** = interface nearly as complex as the implementation.

**Seam** _(Michael Feathers)_ — a place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. _Avoid_: boundary (overloaded with DDD bounded context).

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes *role*, not substance.

**Leverage** — what callers get from depth: more capability per unit of interface learned.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and verification concentrate in one place.

## Deep vs shallow

**Deep module** = small interface + lots of implementation.

**Shallow module** = large interface + little implementation (avoid).

When designing an interface, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small parts — they just aren't part of the interface. A module can have **internal seams** as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a seam unless something actually varies across it.
- **ISPO host seams are real.** Host-mediated surfaces (`@ispo/sdk` methods, MCP tools, grants) are seams you adapt to — do not re-implement host authority inside the project.

## Designing for testability

1. **Accept dependencies, don't create them** at system boundaries.
2. **Return results, don't hide unverifiable side effects** when the seam allows it.
3. **Small surface area.** Fewer methods = fewer tests. Fewer params = simpler setup.

## Relationships

- A **Module** has exactly one **Interface**.
- **Depth** is measured against that **Interface**.
- A **Seam** is where the **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Going deeper

- **Deepening a cluster given its dependencies** — see [DEEPENING.md](DEEPENING.md).
- **Exploring alternative interfaces** — see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md): design the interface several radically different ways (parallel agents when supported; otherwise sequential), then compare on depth, locality, and seam placement.
