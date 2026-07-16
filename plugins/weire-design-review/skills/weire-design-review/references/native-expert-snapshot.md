# Native expert snapshot

Run the host-native Product Design audit or Claude Design critique as a sealed first-stage review before Wira analysis. The purpose is to preserve the expert's spontaneous full-breadth observations instead of letting the Wira objective, score, known complaints, or report format narrow them prematurely.

## Execution order

1. Confirm the design goal gate and accepted visual evidence.
2. Start a fresh isolated subagent when the host supports it. Give it only:
   - the exact accepted screenshot, video frames, or Figma frame;
   - product identity, target audience, platform, and design stage;
   - the instruction to run the host-native critique at full native breadth.
3. Do not give the native stage Wira score weights, Wira dimension names, known findings, stakeholder color complaints, target-metric priority, or proposed conclusions.
4. If an isolated subagent cannot load the native capability, use a sealed sequential phase in the current agent. Complete and freeze the native output before reading Wira brand, scoring, complement, or report-rendering rules.
5. Preserve the raw native output as an artifact or stable inline snapshot. Do not rewrite it after Wira analysis starts.
6. Extract every material native observation into a stable candidate such as `NC-001`.
7. Only after the snapshot is frozen, run the Wira core, coverage mapping, adaptive complement, consolidation, and scoring.

Use `execution_mode: isolated_subagent` when the native capability ran in a fresh context. Use `sealed_sequential` only as the fallback and record the lack of context isolation in the native pass limitations.

## Native framework coverage

The snapshot must record an evidence-aware result for all five native review sections:

- `first_impression`
- `usability`
- `visual_hierarchy`
- `consistency`
- `accessibility`

For each section, use one status:

- `finding`: one or more material problems or validation risks were found;
- `strength`: one or more material strengths were found;
- `mixed`: both strengths and problems were found;
- `no_material_issue`: the section was inspected and no material conclusion was supported;
- `unsupported`: the supplied evidence cannot support the section.

Mentioning a section name is not enough. Record a concise conclusion and link every material observation to one or more candidate IDs. `no_material_issue` and `unsupported` use no candidate IDs.

## Candidate preservation

Each material native observation becomes one candidate:

```json
{
  "id": "NC-001",
  "kind": "finding",
  "source_section": "first_impression",
  "category": "color_and_material",
  "summary": "Warm mid-low-lightness colors and a dark brown card make the palette feel heavy and dusty",
  "evidence": {
    "screen_id": "CAND-HOME-01",
    "description": "Orange, pink, purple, and brown modules cluster at similar mid-low lightness"
  }
}
```

Allowed candidate kinds are `finding`, `strength`, and `validation_hypothesis`. Categories are concise descriptive identifiers such as `color_and_material`, `entry_hierarchy`, `content_comprehension`, or `visible_accessibility` and do not become scoring dimensions.

Do not discard a candidate because it falls outside the declared redesign goal or because Wira did not anticipate it.

## Lossless disposition

Every native candidate must appear exactly once in `specialist_synthesis.source_candidate_ids`:

- `adopted`: verified and mapped to a confirmed final finding or strength;
- `retained_for_validation`: useful but uncertain, mapped to a tentative finding or validation hypothesis;
- `not_adopted`: not used, with an explicit evidence-based rationale.

Several native candidates may be merged into one synthesis item when they describe the same root issue. One candidate may not disappear, appear in two dispositions, or be replaced by a generic statement that does not preserve its material meaning.

The raw snapshot is an audit artifact, not the designer-facing report. The default designer summary still shows all accepted confirmed findings and separates tentative items under `待验证（不扣分）`.

## Completion gate

Do not score when any of these conditions is true:

- the host-native pass did not finish;
- the raw output was not preserved before Wira analysis;
- any native framework section lacks a conclusion;
- a material candidate has no final disposition;
- a candidate is assigned more than one disposition;
- the snapshot cites different visual inputs from the native capability pass.
