# Review result schema

## Contents

- Review and context
- Capability passes
- Native expert snapshot
- Specialist synthesis
- Scope dimensions
- Findings and deltas
- Validation hypotheses
- Element accountability
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
    "output_mode": "designer_summary",
    "output_language": "zh-CN",
    "execution_host": "codex",
    "review_engine": "wira-core+codex-product-design",
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
- `output_mode`: `designer_summary`, `audit_full`; default to `designer_summary` and use `audit_full` only when the user explicitly requests the complete audit surface
- `output_language`: always `zh-CN`; all designer-facing report content uses Simplified Chinese only, while schema keys and stable enum values remain unchanged
- `execution_host`: `codex`, `claude`, `other`
- `review_engine`: `wira-core+codex-product-design` on Codex; `wira-core+claude-design` on Claude
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
      "id": "W-01",
      "provider": "wira-core",
      "capability": "adaptive-dimension-complement",
      "invocation": "automatic",
      "status": "used",
      "purposes": ["candidate_findings", "specialist_review"],
      "input_kinds": ["static_screenshot"],
      "input_sources": ["candidate-home-static"],
      "coverage_dimensions": ["color_expression", "brand_alignment", "state_coverage"],
      "limitations": ["Static evidence cannot confirm interaction or unshown states"]
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
- A used baseline must cite accepted input kinds and sources, have one completed `native_expert_snapshot`, and have at least one `specialist_synthesis` item.

Use `coverage_dimensions` on `wira-core / adaptive-dimension-complement` to list only the supported profile gaps repaired after the native expert pass. Do not create this pass when every applicable dimension has full native coverage. Read [adaptive-dimension-complement.md](adaptive-dimension-complement.md).

For a readable static screenshot, the host-native baseline is `used`, not `skipped`. Record static-input limits in `limitations`; handle overlap with the core review during finding consolidation. The validator rejects a missing, skipped, or unavailable host-native baseline.

## Native expert snapshot

Create exactly one frozen snapshot for the used host-native baseline before Wira core analysis. Follow [native-expert-snapshot.md](native-expert-snapshot.md).

```json
{
  "native_expert_snapshot": {
    "pass_id": "P-01",
    "execution_mode": "isolated_subagent",
    "context_scope": "artifact_product_audience_stage_only",
    "completed_before_core_review": true,
    "raw_output_preserved": true,
    "artifact_ref": "artifacts/native-expert-report.md",
    "input_sources": ["candidate-home-static"],
    "framework_coverage": {
      "first_impression": {
        "status": "finding",
        "summary": "The warm mid-low-lightness palette creates a heavy first impression",
        "candidate_ids": ["NC-001"]
      },
      "usability": {
        "status": "finding",
        "summary": "Secondary gameplay entries are harder to understand from their labels and artwork",
        "candidate_ids": ["NC-002"]
      },
      "visual_hierarchy": {
        "status": "finding",
        "summary": "The promoted entrance is visually dominant but its illustration does not fully explain the interaction",
        "candidate_ids": ["NC-003"]
      },
      "consistency": {
        "status": "no_material_issue",
        "summary": "No additional material consistency issue was supported by the accepted screenshot",
        "candidate_ids": []
      },
      "accessibility": {
        "status": "unsupported",
        "summary": "The screenshot supports visible readability risks but not measured compliance",
        "candidate_ids": []
      }
    },
    "candidates": [
      {
        "id": "NC-001",
        "kind": "finding",
        "source_section": "first_impression",
        "category": "color_and_material",
        "summary": "Warm colors cluster at similar mid-low lightness and the brown card appears gray and heavy",
        "evidence": {
          "screen_id": "candidate-home-static",
          "description": "Orange, pink, purple, and brown modules in the first viewport"
        }
      },
      {
        "id": "NC-002",
        "kind": "finding",
        "source_section": "usability",
        "category": "content_comprehension",
        "summary": "Secondary gameplay entries do not clearly communicate their activity or outcome",
        "evidence": {
          "screen_id": "candidate-home-static",
          "description": "Small secondary entries rely on stylized artwork and short labels"
        }
      },
      {
        "id": "NC-003",
        "kind": "finding",
        "source_section": "visual_hierarchy",
        "category": "entry_hierarchy",
        "summary": "The promoted entrance dominates attention but its artwork only partially explains the interaction",
        "evidence": {
          "screen_id": "candidate-home-static",
          "description": "The largest gameplay card uses a mask illustration and the strongest size treatment"
        }
      }
    ]
  }
}
```

Allowed values:

- `execution_mode`: `isolated_subagent`, `sealed_sequential`
- `context_scope`: exactly `artifact_product_audience_stage_only`
- framework sections: exactly `first_impression`, `usability`, `visual_hierarchy`, `consistency`, `accessibility`
- framework status: `finding`, `strength`, `mixed`, `no_material_issue`, `unsupported`
- candidate kind: `finding`, `strength`, `validation_hypothesis`

`pass_id` must be the used host-native baseline. `input_sources` must match that pass. Both completion flags must be `true`; otherwise the review cannot be scored. Every framework section needs a non-empty summary. `finding`, `strength`, and `mixed` require candidate IDs; `no_material_issue` and `unsupported` require none.

Every candidate requires a unique ID, one source section, a concise category and summary, and visible evidence with `screen_id` and `description`. The union of framework `candidate_ids` must equal the candidate array exactly.

## Specialist synthesis

For every used pass whose purposes include `candidate_findings` or `specialist_review`, summarize the material conclusions and their final disposition.

```json
{
  "specialist_synthesis": [
    {
      "id": "SI-001",
      "source_pass_id": "P-01",
      "source_candidate_ids": ["NC-003"],
      "summary": "The promoted entrance is visually dominant but its illustration does not fully explain the masquerade interaction",
      "disposition": "adopted",
      "target_refs": [{"type": "finding", "id": "F-001"}],
      "rationale": "Verified on the supplied screenshot and consolidated with the core semantic check"
    },
    {
      "id": "SI-002",
      "source_pass_id": "P-01",
      "source_candidate_ids": ["NC-001"],
      "summary": "The warm purple-red palette may cue dating or livestream categories",
      "disposition": "retained_for_validation",
      "target_refs": [{"type": "validation_hypothesis", "id": "H-001"}],
      "rationale": "Category association is plausible but requires a perception test"
    },
    {
      "id": "SI-003",
      "source_pass_id": "P-01",
      "source_candidate_ids": ["NC-002"],
      "summary": "Add a persistent tooltip to every gameplay card",
      "disposition": "not_adopted",
      "target_refs": [],
      "rationale": "The recommendation adds unsupported complexity and is not required by visible evidence"
    },
    {
      "id": "SI-004",
      "source_pass_id": "W-01",
      "summary": "The Wira complement completed the uncovered color and brand checks without finding another material issue",
      "disposition": "not_adopted",
      "target_refs": [],
      "rationale": "The supported observations were already represented by the accepted final findings"
    }
  ]
}
```

Allowed values:

- `disposition`: `adopted`, `retained_for_validation`, `not_adopted`
- `target_refs.type`: `finding`, `strength`, `validation_hypothesis`

`source_pass_id` must reference a `used` pass. `adopted` items target final findings or strengths. `retained_for_validation` items target tentative findings or validation hypotheses and never deduct score. `not_adopted` items have no target and require a clear rationale.

Every synthesis item sourced from the host-native baseline requires `source_candidate_ids`. Across those items, every native candidate must appear exactly once. Items from adaptive complement or other optional passes omit this field unless they have their own separately defined candidate registry.

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
      "state_coverage": {"applicable": true, "evidence_confidence": 0.45},
      "interaction_motion": {"applicable": false, "evidence_confidence": 0}
    },
    "dimension_coverage": {
      "task_flow_delta": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "baseline_capability": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "visual_hierarchy": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "color_expression": {
        "native_status": "partial",
        "final_status": "full",
        "complement_status": "used",
        "gap": "The native pass noted contrast but did not inspect palette cleanliness or Wira category signal",
        "complement_pass_id": "W-01",
        "source_pass_ids": ["P-01", "W-01"]
      },
      "design_system_evolution": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "social_connection": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "brand_alignment": {
        "native_status": "missing",
        "final_status": "partial",
        "complement_status": "used",
        "gap": "The native pass did not compare the screen with the confirmed Wira traits and anti-traits",
        "complement_pass_id": "W-01",
        "source_pass_ids": ["W-01"]
      },
      "content_tone": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "accessibility": {"native_status": "full", "final_status": "full", "complement_status": "not_needed", "source_pass_ids": ["P-01"]},
      "state_coverage": {
        "native_status": "missing",
        "final_status": "partial",
        "complement_status": "used",
        "gap": "The native pass did not account for the visible 上新 badge or its unsupported lifecycle",
        "complement_pass_id": "W-01",
        "source_pass_ids": ["W-01"]
      },
      "interaction_motion": {"native_status": "unsupported", "final_status": "unsupported", "complement_status": "not_applicable", "source_pass_ids": []}
    },
    "limitations": ["Only static matched screenshots were supplied"]
  }
}
```

Use the dimension IDs in `review-framework.md`. Non-applicable dimensions require confidence `0` and score as `N/A`.

`dimension_coverage` must contain the same complete dimension set as `dimensions`.

- `native_status`: `full`, `partial`, `missing`, `unsupported`
- `final_status`: `full`, `partial`, `unsupported`
- `complement_status`: `not_needed`, `used`, `not_applicable`

For an applicable dimension, `native_status: full` requires `complement_status: not_needed`. A `partial` or `missing` native result requires a used Wira adaptive complement, a non-empty `gap`, and a `complement_pass_id` whose `coverage_dimensions` includes that dimension. Non-applicable dimensions use `unsupported / unsupported / not_applicable` with no sources. An applicable dimension may not remain missing in a scored report.

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
      "location": "首页首屏 / 玩法入口区上方",
      "evidence": {
        "screen_id": "candidate-home",
        "description": "Four promotional modules precede the first room card"
      },
      "impact": "Users must scan promotional content before starting the core task",
      "recommendation": "Move active room discovery into the first viewport and demote secondary promotions",
      "completion_criteria": [
        "The first viewport contains a recognizable active-room entry point",
        "A five-second first-click test identifies room discovery as the primary next action"
      ]
    },
    {
      "id": "F-002",
      "dimension": "state_coverage",
      "severity": "moderate",
      "status": "tentative",
      "confidence": 0.55,
      "check_type": "semantic",
      "source_pass_ids": ["core"],
      "delta": "unknown",
      "title": "The 上新 badge lacks an inspectable lifecycle contract",
      "location": "首页 / 假面舞会卡片 / 标题右侧",
      "evidence": {
        "screen_id": "candidate-home",
        "description": "A visible 上新 badge implies temporary or user-specific state"
      },
      "impact": "Without more evidence, design and engineering cannot determine appearance, exit, recurrence, or default-card behavior",
      "recommendation": "Inspect Figma or PRD and define the badge lifecycle, or remove it when no material user value is lost",
      "completion_criteria": [
        "Figma or PRD defines appearance, update, exit, recurrence, and default-card rules",
        "The card remains structurally stable after the badge exits"
      ]
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

Every finding requires a concise `location` that names the screen or step plus the smallest observable region or state. It also requires a non-empty `completion_criteria` array. Each criterion must be observable in a later screenshot, prototype, Figma inspection, implementation measurement, or user test; do not use subjective closure language such as `looks better`.

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

## Element accountability

Run [element-accountability-audit.md](element-accountability-audit.md) for every accepted input and store the complete internal ledger. The default designer report shows only mapped problems and validation items, not this full table.

```json
{
  "element_accountability": {
    "scan_completed": true,
    "input_sources": ["candidate-home-static"],
    "categories_checked": [
      "badge_tag",
      "counter_timer",
      "status_indicator",
      "pagination_indicator",
      "transient_prompt",
      "icon_graphic",
      "microcopy"
    ],
    "items": [
      {
        "id": "E-001",
        "source_id": "candidate-home-static",
        "screen_id": "candidate-home",
        "location": "首页 / 假面舞会卡片 / 标题",
        "element_type": "microcopy",
        "visible_content": "假面舞会",
        "semantic_role": "content",
        "decision_value": "Identifies the gameplay entrance",
        "necessity": "necessary",
        "deletion_test": {
          "result": "essential",
          "rationale": "Removing it would leave the gameplay entrance unidentified"
        },
        "interaction": "The label belongs to the tappable card",
        "design_system_rule": "Uses the gameplay-card title role",
        "lifecycle": {
          "requirement": "not_required",
          "evidence_status": "not_applicable",
          "appearance_trigger": "not_applicable",
          "update_rule": "not_applicable",
          "exit_rule": "not_applicable",
          "recurrence_rule": "not_applicable",
          "default_state": "not_applicable"
        },
        "verification_basis": ["visible_static", "design_system"],
        "assessment": "no_issue",
        "issue_basis": "none"
      },
      {
        "id": "E-002",
        "source_id": "candidate-home-static",
        "screen_id": "candidate-home",
        "location": "首页 / 假面舞会卡片 / 标题右侧",
        "element_type": "badge_tag",
        "visible_content": "上新",
        "semantic_role": "status",
        "decision_value": "May signal an unseen or recently released gameplay entry",
        "necessity": "unknown",
        "deletion_test": {
          "result": "unknown",
          "rationale": "The screenshot does not show whether removing it loses user-specific state"
        },
        "interaction": "No independent interaction is visible",
        "design_system_rule": "No inspected badge rule was supplied",
        "lifecycle": {
          "requirement": "required",
          "evidence_status": "unsupported",
          "appearance_trigger": "unknown",
          "update_rule": "unknown",
          "exit_rule": "unknown",
          "recurrence_rule": "unknown",
          "default_state": "unknown"
        },
        "verification_basis": ["visible_static"],
        "assessment": "validation_required",
        "issue_basis": "lifecycle",
        "target_ref": {"type": "finding", "id": "F-002"}
      }
    ]
  }
}
```

`categories_checked` must contain exactly the seven categories shown above, and `items` must include at least one inspected item for every accepted input source. Give every item a stable `E-xxx` ID. Novel, stateful, promotional, inconsistent, and core-task elements require individual rows.

Allowed values:

- `element_type`: the seven scan categories plus `other`
- `semantic_role`: `status`, `promotion`, `action`, `navigation`, `feedback`, `content`, `decoration`, `unknown`
- `necessity`: `necessary`, `supportive`, `redundant`, `unknown`
- `deletion_test.result`: `essential`, `supportive`, `no_material_loss`, `unknown`; it must correspond to necessity
- `lifecycle.requirement`: `required`, `not_required`, `unknown`
- `lifecycle.evidence_status`: `complete`, `partial`, `missing`, `unsupported`, `not_applicable`
- `verification_basis`: `visible_static`, `video`, `figma`, `prd`, `design_system`, `implementation`, `analytics`
- `assessment`: `no_issue`, `finding`, `validation_required`
- `issue_basis`: `none`, `necessity`, `lifecycle`, `semantics`, `affordance`, `system_consistency`

`no_issue` has no target. `finding` maps to one confirmed finding. `validation_required` maps to one tentative finding or validation hypothesis. Unknown or redundant necessity and incomplete required lifecycles cannot be closed as `no_issue`. A screenshot-only lifecycle observation must remain `validation_required`; a confirmed lifecycle failure requires stronger inspected evidence from video, Figma, PRD, design-system rules, or implementation.

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
    "scoring_version": "1.13",
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

The scored JSON remains the source of truth. `review.output_mode` changes only presentation, never evidence, findings, score, or readiness. `review.output_language` is always `zh-CN`: translate all visible section headings, field labels, severity labels, conclusions, findings, recommendations, and checklist items into Simplified Chinese. Do not render bilingual labels. Keep stable IDs, user-supplied metric names, and necessary product or capability names unchanged.

For `designer_summary`, follow the four default sections in [report-template.md](report-template.md): 评审结果、优先改稿清单、本轮需要保留、修改后复审条件. Lead with score and readiness. Render every confirmed finding as a compact task card with ID, severity, location, concrete problem, impact, recommendation, and completion criteria. Separate tentative findings under `待验证（不扣分）`. Render at most three strengths and derive closure checks from all blocker and major findings plus goal-critical moderate findings.

Do not render dimension score tables, dimension or multi-scale coverage, the full element-accountability ledger, raw confidence/delta/evidence-level metadata, specialist synthesis, or capability-pass logs in the default visible response. These fields remain required in the JSON and full audit. When the environment supports files, save the full audit and scored JSON and provide only their paths after the concise report.

For `audit_full`, render the seven audit sections—整体印象、易用性、视觉层级、一致性、无障碍性、做得好的地方、优先改进建议—then the evidence, coverage, detailed score, findings, validation, limitations, specialist synthesis, and capability-pass log defined in [report-template.md](report-template.md). 易用性 is a presentation roll-up for `wira-v2`, not a new scoring dimension; never deduct twice.

In the full audit, render the coverage tables and `element_accountability` ledger before detailed finding cards. Every visible region must appear in `Screen / Section Coverage`; use component, element, and state tables to show inspection depth without creating extra scoring dimensions. Render `scope.dimension_coverage` so readers can trace the native expert, adaptive complement, final coverage, and source passes. Render the frozen `native_expert_snapshot` and complete native candidate list before `specialist_synthesis`, then render the capability-pass log.
