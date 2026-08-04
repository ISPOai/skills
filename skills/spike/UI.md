# UI Prototype (ISPO)

Generate **several radically different UI variations** switchable inside the project iframe. The user flips between variants, picks one (or steals bits from each), then throws the rest away.

If the question is about logic/state rather than what something looks like — wrong branch. Use [LOGIC.md](LOGIC.md).

## When this is the right shape

- "What should this page look like?"
- "I want to see a few options before committing."
- "Try a different layout for this screen."

## ISPO constraints

- Stay inside the **project iframe**. Use `@ispo/sdk` / `@ispo/sdk/react` and the project's design tokens (`@ispo/design`, shadcn primitives already in the project).
- Do **not** add floating host-chrome bars, native `title` tooltips, image `alt` fallbacks, or author-written `aria-*` labels.
- Do **not** replace Project Home as the primary surface unless the confirmed plan surface mode is `custom` and rendered QA has verified the replacement. Prefer mounting variants inside the existing Home or an existing project route.
- Mark files so a casual reader sees they are throwaway (`prototype` in path or filename).
- No new grants for a spike. No harness plugins for ISPO-mediated capabilities.
- Verify with `wait_for_fresh_build`, `get_console`, `query_dom` / `screenshot` while evaluating variants — not by opening an external browser when the project frame is available.

## Two sub-shapes — prefer A

### Sub-shape A — adjustment to an existing surface (preferred)

Variants render on the same project route/surface, gated by a `?variant=` search param (or an in-app control if routing is unavailable). Existing data fetching stays; only the rendering swaps.

### Sub-shape B — a new throwaway surface (last resort)

Only when there is genuinely no existing page to host the variants. Follow the project's routing conventions; name the path/file with `prototype`. Do not invent a new top-level host navigation surface.

## Process

### 1. State the question and pick N

Default to **3** variants; cap at 5. Write the plan in one line at the top of the prototype file.

### 2. Generate radically different variants

Variants must be **structurally different** — layout, information hierarchy, primary affordance — not just different colours. Use the project's component library and theme tokens.

### 3. Wire a switcher

```tsx
// pseudo-code — adapt to the project
const variant = searchParams.get('variant') ?? 'A'
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A','B','C']} current={variant} />
  </>
)
```

Keep the switcher **inside the project iframe** as ordinary project UI (compact control cluster), not as host chrome. Prefer URL search-param switching so a variant is reload-stable. Keyboard ←/→ may cycle when focus is not in an input.

### 4. Hand it over

Surface how to open each variant. Useful feedback is often "header from B with layout from C."

### 5. Capture and clean up

Record which variant won and why into `.ispo/spec.md` (product intent) or a short ADR if the choice is a hard-to-reverse trade-off. Fold the winner into real code. Move leftover prototype files off main (throwaway branch) or delete them. Do not leave switcher scaffolding in the production path.

## Anti-patterns

- Vacuum prototypes that ignore real project density/data when an existing surface could host them
- Shipping the switcher to users
- Treating the spike as authority to widen grants or replace Home early
- Parallel UI-only implementations of a command the project already exposes
