# Review result schema

## Contents

- Review and context
- Capability passes
- Specialist synthesis
- Scope dimensions
- Findings and deltas
- Validation hypotheses
- Scoring output
- Report rendering

## Review and context

Create UTF-8 JSON. `profile` defaults to `generic-mobile-v1`; use `wira-v1` for context-only Wira review and `wira-v2` for a matched production/design-system redesign comparison. `mode` defaults to `artifact`.

```json
{
  "review": {
    "title": "微热新版首页评审",
    "profile": "wira-v2",
    "mode": "redesign-comparison",
    "execution_host": "codex",
    "source_type": "mixed",
    "platform": "ios",
    "core_task": "找到感兴趣的房间并愿意进入",
    "assumptions": ["候选稿与现网截图处于相同首页状态"]
  },
  "context": {
    "design_goal_status": "confirmed",
    "design_goal": {
      "goal_type": "behavior",
      "primary_goal": "提升用户从首页进入感兴趣房间的效率",
      "success_criteria": ["room_entry_rate 提升", "post_entry_dwell 不下降"],
      "source": "user_declared"
    },
    "brand_charter_status": "confirmed",
    "baseline_status": "available",
    "design_system_status": "available",
    "redesign_goal_status": "confirmed",
    "redesign_goal": {
      "objective_type": "behavior",
      "primary_objective": "提升用户从首页进入感兴趣房间的效率",
      "primary_metric": "room_entry_rate",
      "guardrail_metrics": ["post_entry_dwell", "next_day_revisit"],
      "primary_changed_variable": "活跃房间入口的首屏层级",
      "held_constant": ["底部导航", "房间内参与流程"]
    }
  }
}
```

Allowed values:

- `profile`: `generic-mobile-v1`, `wira-v1`, `wira-v2`
- `mode`: `artifact`, `redesign-comparison`, `flow-audit`, `direction-comparison`
- `execution_host`: `codex`, `claude`, `other`
- `source_type`: `screenshot`, `video`, `figma`, `mixed`
- `brand_charter_status`: `missing`, `candidate`, `confirmed`
- `design_goal_status`: final scored reviews require `confirmed`
- `design_goal.goal_type`: `behavior`, `experience_or_brand`, `general_quality`
- `design_goal.source`: `user_declared`, `user_confirmed`
- `redesign_goal_status`: `missing`, `inferred`, `confirmed`

Every scored review requires a user-declared or user-confirmed design goal plus at least one non-empty success criterion. Do not write this contract from model inference. If the user supplied only an artifact, run [design-goal-gate.md](design-goal-gate.md), ask the required question, and stop before creating review JSON.

For `wira-v2` redesign comparisons, also include `redesign_goal_status`. Keep `design_goal` and `redesign_goal` aligned. When `redesign_goal_status` is `confirmed` or `inferred`, include the redesign goal object shown above. Only a confirmed redesign goal makes `task_flow_delta` applicable; missing or inferred redesign goals keep it `N/A` while the remaining artifact dimensions may still be reviewed.

## Capability passes

Record both mandatory baseline capabilities on every review. The array is required: the current host's native baseline must be `used`, while the other platform's baseline is `unavailable` because of the host boundary. Additional specialist passes remain optional.

```json
{
  "capability_passes": [
    {
      "id": "P-01",
      "provider": "codex-product-design",
      "capability": "audit",
      "invocation": "required",
      "status": "used",
      "purposes": ["evidence_capture", "candidate_findings"],
      "input_kinds": ["static_screenshot"],
      "input_sources": ["candidate-home-static"],
      "limitations": ["Single static screenshot; interaction behavior and unshown states are unsupported"]
    },
    {
      "id": "P-02",
      "provider": "claude-design",
      "capability": "accessibility-review",
      "invocation": "automatic",
      "status": "skipped",
      "purposes": ["specialist_review"],
      "input_kinds": [],
      "input_sources": [],
      "limitations": ["No implementation or inspectable Figma values were supplied"]
    },
    {
      "id": "C-01",
      "provider": "claude-design",
      "capability": "design-critique",
      "invocation": "required",
      "status": "unavailable",
      "purposes": ["candidate_findings", "specialist_review"],
      "input_kinds": [],
      "input_sources": [],
      "limitations": ["Claude Design cannot be invoked from the Codex execution host"]
    }
  ]
}
```

Allowed values:

- `status`: `used`, `skipped`, `unavailable`
- `invocation`: `required`, `explicit`, `automatic`
- `purposes`: `evidence_capture`, `candidate_findings`, `specialist_review`, `validation_plan`, `research_synthesis`, `ideation`, `handoff`, `implementation_qa`
- `input_kinds`: `static_screenshot`, `video`, `figma`, `live_flow`, `design_system`, `research_data`, `implementation`, `other`

Use stable pass IDs such as `P-01`. `provider` and `capability` describe the capability actually used or the required cross-host baseline. A skipped or unavailable pass cannot be cited as a finding source.

Mandatory baseline rules:

- Include exactly one `codex-product-design` / `audit` and one `claude-design` / `design-critique` pass.
- Set both to `invocation: required`; neither may be `skipped`.
- With `execution_host: codex`, Product Design must be `used` and Claude Design must be `unavailable`.
- With `execution_host: claude`, Claude Design must be `used` and Product Design must be `unavailable`.
- With `execution_host: other`, both are `unavailable` and the scorer rejects a completed review; use this only for an incomplete-review diagnostic.
- An unavailable pass must state the host boundary or missing dependency in `limitations`.
- A used baseline must cite accepted input kinds and sources and must have at least one `specialist_synthesis` item.

For a readable static screenshot, the host-native baseline is `used`, not `skipped`. Record static-input limits in `limitations`; handle overlap with the core review during finding consolidation. The validator rejects a missing, skipped, or unavailable host-native baseline.

## Specialist synthesis

For every used pass whose purposes include `candidate_findings` or `specialist_review`, summarize the material conclusions and their final disposition.

```json
{
  "specialist_synthesis": [
    {
      "id": "SI-001",
      "source_pass_id": "P-01",
      "summary": "The promoted entrance is visually dominant but its illustration does not fully explain the masquerade interaction",
      "disposition": "adopted",
      "target_refs": [{"type": "finding", "id": "F-001"}],
      "rationale": "Verified on the supplied screenshot and consolidated with the core semantic check"
    },
    {
      "id": "SI-002",
      "source_pass_id": "P-01",
      "summary": "The warm purple-red palette may cue dating or livestream categories",
      "disposition": "retained_for_validation",
      "target_refs": [{"type": "validation_hypothesis", "id": "H-001"}],
      "rationale": "Category association is plausible but requires a perception test"
    },
    {
      "id": "SI-003",
      "source_pass_id": "P-01",
      "summary": "Add a persistent tooltip to every gameplay card",
      "disposition": "not_adopted",
      "target_refs": [],
      "rationale": "The recommendation adds unsupported complexity and is not required by visible evidence"
    }
  ]
}
```

Allowed values:

- `disposition`: `adopted`, `retained_for_validation`, `not_adopted`
- `target_refs.type`: `finding`, `strength`, `validation_hypothesis`

`source_pass_id` must reference a `used` pass. `adopted` items target final findings or strengths. `retained_for_validation` items target tentative findings or validation hypotheses and never deduct score. `not_adopted` items have no target and require a clear rationale.

Do not copy a plugin's raw score into this structure. Do not create one synthesis item per sentence; consolidate duplicates from the same pass into the smallest useful set of conclusions.

## Scope dimensions

Include exactly the dimensions belonging to the selected profile. Every dimension must state applicability and evidence confidence.

```json
{
  "scope": {
    "dimensions": {
      "task_flow_delta": {"applicable": true, "evidence_confidence": 0.82},
      "baseline_capability": {"applicable": true, "evidence_confidence": 0.86},
      "visual_hierarchy": {"applicable": true, "evidence_confidence": 0.9},
      "color_expression": {"applicable": true, "evidence_confidence": 0.78},
      "design_system_evolution": {"applicable": true, "evidence_confidence": 0.9},
      "social_connection": {"applicable": true, "evidence_confidence": 0.7},
      "brand_alignment": {"applicable": true, "evidence_confidence": 0.55},
      "content_tone": {"applicable": true, "evidence_confidence": 0.8},
      "accessibility": {"applicable": true, "evidence_confidence": 0.65},
      "state_coverage": {"applicable": false, "evidence_confidence": 0},
      "interaction_motion": {"applicable": false, "evidence_confidence": 0}
    },
    "limitations": ["Only static matched screenshots were supplied"]
  }
}
```

Use the dimension IDs in `review-framework.md`. Non-applicable dimensions require confidence `0` and score as `N/A`.

## Findings and deltas

```json
{
  "strengths": [
    {
      "id": "W-001",
      "dimension": "design_system_evolution",
      "statement": "The candidate separates the neutral base from vivid room content",
      "delta": "better",
      "source_pass_ids": ["core", "P-01"],
      "evidence": {"screen_id": "candidate-home", "description": "Room card region"}
    }
  ],
  "findings": [
    {
      "id": "F-001",
      "dimension": "task_flow_delta",
      "severity": "major",
      "status": "confirmed",
      "confidence": 0.88,
      "check_type": "contextual",
      "source_pass_ids": ["core", "P-01"],
      "delta": "worse",
      "title": "The primary room-discovery action lost emphasis",
      "evidence": {
        "screen_id": "candidate-home",
        "description": "Four promotional modules precede the first room card"
      },
      "impact": "Users must scan promotional content before starting the core task",
      "recommendation": "Move active room discovery into the first viewport and demote secondary promotions"
    }
  ]
}
```

Allowed values:

- severity: `blocker`, `major`, `moderate`, `minor`
- status: `confirmed`, `tentative`
- check type: `rule`, `semantic`, `contextual`
- delta: `better`, `same`, `worse`, `unknown`
- evidence level: `measured`, `visually_estimated`, `association_hypothesis`
- confidence: number from `0` to `1`

Evidence requires `screen_id` and `description`; it may also include `region`, `timestamp_ms`, `node_id`, `baseline_screen_id`, or `design_system_ref`.

`source_pass_ids` is optional and defaults conceptually to `["core"]`. It may contain `core` and IDs of `used` entries in `capability_passes`. It records contribution provenance, not independent evidence and not extra scoring weight.

Give strengths stable IDs such as `W-001` when a specialist synthesis item targets them.

Tentative findings stay visible but do not reduce scores. Use tentative status for candidate brand principles or missing comparison context. The confirmed Wira charter may support confirmed `brand_alignment` findings in `wira-v2`.

## Validation hypotheses

Store product effects that require a prototype test or analytics separately from design findings.

```json
{
  "validation_hypotheses": [
    {
      "id": "H-001",
      "hypothesis": "Because active room behavior is visible on cards, more users will enter based on shared activity",
      "primary_metric": "room_entry_rate",
      "guardrails": ["post_entry_dwell", "gift_conversion"],
      "source_pass_ids": ["core", "P-01"]
    }
  ]
}
```

## Scoring output

Run `python3 scripts/review_score.py <review.json> --write`. The script adds:

```json
{
  "scores": {
    "overall_score": 84.0,
    "raw_weighted_score": 84.0,
    "score_confidence": 0.77,
    "dimension_scores": {},
    "scoring_profile": "wira-v2",
    "scoring_version": "1.8",
    "development_readiness": {
      "status": "conditional_handoff",
      "label": "有条件进入开发",
      "recommended_action": "先完成优先改进项并确认修改方案；仅可并行开展技术预研或低返工风险工作。",
      "reasons": ["overall_score_below_85"],
      "thresholds": {
        "ready_score": 85,
        "revision_score": 70,
        "minimum_score_confidence": 0.65
      },
      "requires_re_review": true
    }
  }
}
```

Confirmed findings deduct `100`, `40`, `15`, or `5` points from their primary dimension for blocker, major, moderate, or minor severity. Only findings with confidence at least `0.65` affect the score. Any blocker caps the total at `59`, two or more major findings cap it at `79`, and one major finding caps it at `89`.

The normal development line is `85`. Scores from `70` through `84` are conditional; scores below `70` require design revision. Any scored Blocker or at least two scored Majors forces `revise_before_development`; one scored Major prevents normal readiness. When score confidence is below `0.65` and no stronger revision gate applies, use `insufficient_evidence`. Follow [development-readiness.md](development-readiness.md) and never hand-edit this generated result.

Allowed `development_readiness.status` values:

- `ready_for_development`
- `conditional_handoff`
- `revise_before_development`
- `insufficient_evidence`

`reasons` contains stable machine-readable codes such as `overall_score_below_85`, `overall_score_below_70`, `one_confirmed_major_finding`, `multiple_confirmed_major_findings`, `confirmed_blocker_findings`, or `score_confidence_below_0.65`. Render those codes as plain-language evidence and related finding IDs rather than exposing only the raw code.

For redesign comparisons, score both versions separately with matched scope. A delta label is an evidence-based comparison; the scoring script does not manufacture a numeric improvement from unmatched evidence.

## Report rendering

The scored JSON remains the source of truth. Render it with the seven fixed sections in [report-template.md](report-template.md): Overall Impression, Usability, Visual Hierarchy, Consistency, Accessibility, What Works Well, and Priority Recommendations. Render `development_readiness` prominently inside Overall Impression.

`Usability` is a presentation roll-up for `wira-v2`, not a new scoring dimension. Pull its evidence from the mapped source dimensions and do not deduct again. Follow the seven sections with the evidence, detailed score, findings, validation, limitation, and artifact appendix.

Render each item in `findings` as a detailed problem card following [report-template.md](report-template.md). Preserve the finding ID and keep evidence, impact, recommendation, and validation visibly separate. Priority recommendations summarize at most three root causes and do not replace the full cards.

Render the coverage tables before the cards. Every visible region must appear in `Screen / Section Coverage`; use the component and state tables to show the depth inspected without creating extra scoring dimensions.

Render `specialist_synthesis` as a compact appendix table before the capability-pass log. Readers must be able to trace adopted entries to final finding or strength IDs, retained entries to tentative findings or hypotheses, and rejected entries to an explicit rationale.
