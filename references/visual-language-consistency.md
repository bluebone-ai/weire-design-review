# Visual-language consistency

Evaluate whether the product has one understandable visual grammar. Consistency does not mean every element looks identical; different treatments are coherent when each has a stable role and the transitions between them are intentional.

## Observation lenses

- **Material language:** flat, solid, glass, translucent, luminous, outlined, textured, and elevated surfaces; inspect whether each material has a stable semantic and hierarchy role.
- **Form language:** silhouette, geometry, radius, stroke, volume, depth, proportion, and edge treatment; inspect whether components appear to belong to the same product family.
- **Graphic and illustration language:** icons, IP characters, motifs, entry graphics, illustrations, and decorative assets; inspect line, volume, perspective, rendering, light, detail, and emotional tone.
- **Image and media language:** photography, avatars, 2D, 3D, emoji, stickers, and mixed media; inspect whether their roles and transitions are deliberate rather than accumulated.
- **Motion character:** rhythm, easing, elasticity, spatial behavior, and intensity; inspect stylistic coherence here and route functional feedback or continuity issues to `interaction_motion`.

Typography and palette may provide evidence for visual-language coherence, but route their primary issues to the dedicated type, color, accessibility, or brand checks when available.

## Decision rules

Ask:

1. Can the visual rule be stated without naming one screen?
2. Does the same semantic role use the same visual treatment across screens?
3. If multiple styles coexist, is there an explicit role boundary between them?
4. Do new assets extend the system or merely introduce another isolated style?
5. Does the combined language express the confirmed brand traits?

Classify the result as:

- `coherent`: one grammar or a documented role-based family of grammars;
- `intentional_variation`: a different treatment with a clear semantic, campaign, or content role;
- `unresolved_mixture`: several styles coexist without stable role boundaries;
- `contradictory`: treatments communicate conflicting hierarchy, interaction, or brand meaning.

Use `design_system_evolution` as the primary scoring dimension. Use examples such as glass versus flat buttons, IP versus icons, or balloon graphics versus flat illustrations only as evidence. Do not turn each example into an independent dimension or deduct repeatedly for the same system-level cause.
