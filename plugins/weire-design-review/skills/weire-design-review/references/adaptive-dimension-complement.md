# Adaptive dimension complement

Run the current host's native design expert at full breadth first. Then inspect its material output against every applicable review-profile dimension and fill only supported gaps with Wira-specific checks. The complement expands coverage; it does not imitate the unavailable cross-host plugin or constrain the native expert's framework.

## Sequence

1. Complete the required Product Design `audit` on Codex or Design `design-critique` on Claude without pre-limiting it to assigned dimensions.
2. Build `scope.dimension_coverage` before consolidating findings.
   - Use exactly the dimension IDs from the selected scoring profile in [review-framework.md](review-framework.md).
   - Map native labels such as `first impression`, `consistency`, or `goal-task fit` into those profile IDs; never add them as extra score or coverage dimensions.
3. Mark each dimension's native coverage as `full`, `partial`, `missing`, or `unsupported`.
4. Run one `wira-core / adaptive-dimension-complement` pass for all applicable dimensions marked `partial` or `missing`.
5. Recheck the supplied evidence only for those gaps. Do not manufacture interaction, state, measurement, or behavioral evidence.
6. Normalize native and complement conclusions together. Merge duplicate symptoms, retain verified unique findings, and preserve provenance through `source_pass_ids` and `specialist_synthesis`.

## Coverage statuses

| Native status | Meaning | Required action |
|---|---|---|
| `full` | The native pass inspected the dimension and produced an evidence-aware conclusion or explicit no-material-issue result | Do not rerun the dimension |
| `partial` | The native pass mentioned the area but omitted a material mechanism, impact, evidence boundary, or relevant subcheck | Run the complement for the named gap |
| `missing` | No material conclusion covers the applicable dimension | Run the complement |
| `unsupported` | The accepted evidence cannot support the dimension and it is `N/A` | Do not supplement with inference |

After supplementation, `final_status` is `full` or `partial` for applicable dimensions. Use `partial` when the complement completed every supported static check but video, Figma values, implementation, states, or research remain unavailable. An applicable dimension may not remain `missing` in a scored review.

Examples: on `wira-v1`, map native goal/task observations to `task_flow_clarity`, visual consistency to `visual_system`, and copy observations to `content_tone`. On `wira-v2`, keep the distinct `visual_hierarchy`, `color_expression`, and `design_system_evolution` dimensions. Presentation sections such as Overall Impression are never coverage dimensions.

## Host-oriented gap priorities

These are routing priorities based on observed output tendencies, not permanent limits on either expert. Always use the actual coverage matrix.

### Codex complement priorities

When Product Design leaves gaps, inspect:

- `color_expression`: lightness/chroma separation, warm/cool balance, neutral breathing room, orange contamination, gradient/transparency stacking, material impression, and category signal;
- `brand_alignment`: confirmed Wira traits and anti-traits, two-second product-category impression, emotional tone, and people-versus-promotion balance;
- `design_system_evolution` or `visual_system`: material, form, graphic/illustration, IP, media, motion, component, and semantic-token coherence;
- `content_tone`: brand voice, suggestive framing, outcome clarity, and graphic-to-label semantic fit;
- `accessibility`: visible legibility and color-dependence risks, while reserving compliance claims for measured evidence.

### Claude complement priorities

When Design critique leaves gaps, inspect:

- `task_flow_delta`, `task_flow_clarity`, or `usability`: goal-to-hierarchy fit, target-entry comprehension, next-action predictability, participation pressure, prevention, and recovery;
- `baseline_capability`: removed, hidden, renamed, or demoted production capabilities and live signals;
- `social_connection`: visible liveness, people-first evidence, icebreakers, entry pressure, and first-participation support;
- `state_coverage` and `interaction_motion`: only states or transitions present in accepted screenshots, video, or Figma; otherwise keep them `N/A`;
- metric and validation implications: separate section CTR from target-entry CTR, define exposure and activation, isolate variables, and preserve guardrails. Store behavioral effects as validation hypotheses rather than observed findings.

## Complement pass record

When at least one applicable dimension is `partial` or `missing`, add one pass:

```json
{
  "id": "W-01",
  "provider": "wira-core",
  "capability": "adaptive-dimension-complement",
  "invocation": "automatic",
  "status": "used",
  "purposes": ["candidate_findings", "specialist_review"],
  "input_kinds": ["static_screenshot"],
  "input_sources": ["CAND-HOME-01"],
  "coverage_dimensions": ["color_expression", "brand_alignment"],
  "limitations": ["Static evidence cannot confirm interaction, motion, unshown states, or measured accessibility compliance"]
}
```

Do not create this pass when every applicable dimension already has `native_status: full`. Do not use a skipped pass as proof of coverage.

## Coverage matrix example

```json
{
  "color_expression": {
    "native_status": "partial",
    "final_status": "full",
    "complement_status": "used",
    "gap": "The native pass noted contrast but did not inspect palette cleanliness or Wira category signal",
    "complement_pass_id": "W-01",
    "source_pass_ids": ["P-01", "W-01"]
  },
  "state_coverage": {
    "native_status": "unsupported",
    "final_status": "unsupported",
    "complement_status": "not_applicable",
    "source_pass_ids": []
  }
}
```

## Consolidation rules

- A native-expert conclusion is not rejected merely because the Wira core did not anticipate it.
- A complement conclusion may become a scored finding when accepted evidence supports it and it meets the common status, confidence, and severity rules.
- Merge a native and complement conclusion only when they describe the same root mechanism and require the same corrective action.
- Never increase confidence because two analysis passes agree; confidence follows evidence strength.
- Label the complement as `Wira adaptive complement`, never as the unavailable Product Design or Claude Design capability.
