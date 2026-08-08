# Port notes: soundshuman

Ported from [aashaexo/soundshuman](https://github.com/aashaexo/soundshuman) at
revision `a45cfbba9fde843d670e553a0aa98f6a23d7fb28`.

## Included runtime payload

- `SKILL.md`
- `bin/sloplint.js`
- `rules/slop-rules.json`
- All six files under `references/`

## Catalog adaptations

- Renamed the frontmatter skill id from `humanize` to the collision-resistant
  package id `soundshuman`.
- Removed upstream plugin-only frontmatter fields so the skill loads in both
  supported providers.
- Replaced PATH-dependent `sloplint` examples with provider-neutral commands
  that resolve the bundled scanner relative to the loaded `SKILL.md`.
- Omitted plugin manifests, CI configuration, tests, package-manager metadata,
  contributor guidance, and the optional Git hook installer. None is required
  at runtime; the hook installer would mutate a consuming repository's Git
  metadata.
