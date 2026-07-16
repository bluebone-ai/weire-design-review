# Design review report template

Use these seven user-facing sections for every review. Keep the underlying profile dimensions and deterministic score; the report sections reorganize evidence for readability and must not create duplicate deductions.

## 1. Overall Impression / 整体印象

Include:

- one-sentence verdict;
- the confirmed design goal and success criteria;
- the host-specific review engine: `Wira Core + Codex Product Design` or `Wira Core + Claude Design`;
- overall score and score confidence;
- the deterministic `Development Readiness / 开发准入` result, decision basis, 85-point normal development line, and next action;
- redesign delta when comparison is valid;
- redesign-goal status and the most important evidence limitation.

Do not claim the redesign is better when its primary objective is missing or inferred.

Do not render this report at all while design-goal intake is incomplete. The intake response must contain only artifact receipt/source confirmation and the required question from [design-goal-gate.md](design-goal-gate.md).

Render this callout immediately after the one-sentence verdict:

```markdown
### Development Readiness / 开发准入

**结论：** {scores.development_readiness.label}

- **依据：** {overall score, evidence confidence, and translated reason codes with related finding IDs}
- **正常开发线：** 85 分
- **下一步：** {scores.development_readiness.recommended_action}
```

Use the generated gate from [development-readiness.md](development-readiness.md). Do not manually promote a design because its total score looks high. Clarify that the result covers design readiness, not technical feasibility or release approval.

## 2. Usability / 易用性

Summarize whether users can understand the current goal, find the next action, predict the result, participate with low pressure, and recover from represented states.

Use existing findings rather than assigning a new deduction:

| Profile | Source dimensions |
|---|---|
| `generic-mobile-v1` | `usability`, `content`, `state_coverage`, `interaction_motion` |
| `wira-v1` | `task_flow_clarity`, `usability`, `social_connection`, `content_tone`, `state_coverage`, `interaction_motion` |
| `wira-v2` | `task_flow_delta`, `baseline_capability`, `social_connection`, `content_tone`, `state_coverage`, `interaction_motion` |

When `task_flow_delta` is `N/A`, state that product quality can be reviewed but improvement against the redesign objective cannot.

## 3. Visual Hierarchy / 视觉层级

Summarize focus, primary action, scan order, grouping, density, and competing accents. Use the explicit `visual_hierarchy` dimension when present; otherwise cite the most relevant visual-system evidence and mark numerical comparison `N/A` if unsupported.

## 4. Consistency / 一致性

Summarize visual-language coherence and design-system behavior. Cover material, form, graphic/illustration, media, motion character, components, and semantic tokens only where evidence exists. Use `layout_consistency`, `visual_system`, or `design_system_evolution` according to the profile.

## 5. Accessibility / 无障碍性

Summarize contrast, text legibility, touch targets, color dependence, focus, scaling, and reduced-motion risks. Separate measured violations from visually estimated risks. Never claim full compliance from screenshots alone.

## 6. What Works Well / 做得好的地方

Render evidence-backed `strengths`. Prefer strengths that support the core objective, brand, usability, or system coherence. Do not use generic praise or convert the absence of findings into a strength.

## 7. Priority Recommendations / 优先改进建议

Select at most three root-cause changes from confirmed findings. Order by task impact, severity, confidence, and dependency. Write each as:

`Action → expected design or user outcome → metric or validation method when needed.`

Do not repeat the full finding list here.

## Detailed Findings / 详细问题卡

Before the finding cards, follow [multi-scale-audit.md](multi-scale-audit.md) and render:

- `Dimension Coverage & Complement`: every profile dimension, native-expert coverage, observed gap, Wira complement status, final coverage, and source pass IDs;
- `Screen / Section Coverage`: every visible region, its purpose, review status, and related finding IDs;
- `Component / Element Audit`: core, repeated, novel, inconsistent, and risky components, with low-risk standard components grouped when appropriate;
- `State / Edge-case Audit`: relevant quantities, content boundaries, interaction states, device conditions, loading, empty, error, and recovery behavior.

After those tables, render every consolidated finding as an individual card. Use this exact information hierarchy:

```markdown
### F-001｜重大 Major｜Brand alignment / 品牌方向

`状态：Confirmed` · `置信度：0.92` · `相对现网：Worse` · `证据级别：Measured`

**问题**
One clear problem statement.

**证据**
Screen or step, visible region, exact copy or measurement, and baseline comparison when available.

**影响**
The user, task, brand, accessibility, or guardrail consequence. Keep unproven behavioral effects as risks.

**建议**
One actionable change and its expected design outcome.

**验证**
Metric, prototype task, implementation measurement, or perception test needed to close uncertainty.
```

Severity labels:

- `blocker` → `阻断 Blocker`
- `major` → `重大 Major`
- `moderate` → `一般 Moderate`
- `minor` → `轻微 Minor`

Order cards by severity, core-task impact, and confidence. Preserve IDs from the scored JSON. Show tentative findings too, but label them `Tentative / 待验证` and state that they do not reduce the score. Do not merge evidence, impact, and recommendation into one paragraph.

## Required appendix

After the seven sections, include:

1. evidence scope, context, and assumptions;
2. current-versus-new delta table when applicable;
3. detailed dimension scores with `N/A` preserved;
4. dimension coverage and adaptive-complement table;
5. screen/section, component/element, and state/edge-case audit tables;
6. detailed finding cards ordered by severity and task impact;
7. validation hypotheses and target metrics;
8. evidence limitations and untested areas;
9. specialist capability synthesis with adopted, retained, and not-adopted conclusions;
10. capability-pass log with provider, purpose, status, inputs, contribution scope, and limitations;
11. saved artifact locations.

Render dimension coverage as:

| Dimension | Native expert | Native coverage | Gap | Wira complement | Final coverage | Sources |
|---|---|---|---|---|---|---|
| `color_expression` | Product Design audit | Partial | Palette cleanliness and Wira category signal not inspected | Used / W-01 | Full | P-01, W-01 |
| `state_coverage` | Product Design audit | Unsupported | Static screenshot | N/A | Unsupported / N/A | — |

Use `Wira adaptive complement`, not the unavailable cross-host expert, as the supplement label. Do not claim that a dimension was complemented when its source pass did not run. Keep `partial` after supplementation when the accepted evidence still limits the conclusion.

Render the specialist synthesis as:

| ID | Source pass | Specialist conclusion | Disposition | Report destination | Rationale |
|---|---|---|---|---|---|
| SI-001 | P-01 / Product Design audit | The promoted entrance is dominant but its illustration is semantically incomplete | Adopted | F-003 | Verified on CAND-HOME-01 and merged with the core finding |
| SI-002 | C-01 / Claude Design critique | The palette may cue dating-category associations | Retained for validation | H-001 | Requires a target-user perception test |
| SI-003 | P-01 / Product Design audit | Add persistent tooltips to all gameplay cards | Not adopted | — | Adds unsupported complexity |

Keep this table concise, but do not omit a used critique pass because its candidates were rejected. Do not paste raw plugin responses. The final report remains authoritative; this table explains how specialist material was handled.

Render the capability-pass log as:

| ID | Provider | Capability | Invocation | Status | Input kind / source | Contribution scope | Limitations |
|---|---|---|---|---|---|---|---|
| P-01 | Codex Product Design | audit | Required | Used | Static screenshot / CAND-HOME-01 | Evidence and candidate findings | Interaction and unshown states unsupported |
| W-01 | Wira Core | adaptive-dimension-complement | Automatic | Used | Static screenshot / CAND-HOME-01 | Color expression and brand-alignment gaps | Interaction and unshown states unsupported |
| C-01 | Claude Design | design-critique | Required | Unavailable | — | None | Claude plugin cannot run in the Codex host |

Always show both required baseline rows. The row matching `review.execution_host` must be `Used`; the cross-host row must be `Unavailable`. If the host-native row was not used, do not render a scored final report.

## Rendering rules

- `Overall Impression`, `What Works Well`, and `Priority Recommendations` are report sections, not scoring dimensions.
- `Usability` is a non-duplicating roll-up of existing dimensions for `wira-v2`; do not subtract points again.
- `Visual Hierarchy`, `Consistency`, and `Accessibility` expose their underlying dimension scores where an exact mapping exists.
- Use `N/A` rather than an inferred pass when evidence or redesign context is insufficient.
- Show specialist provenance through `source_pass_ids`, but never use the number of agreeing passes as evidence strength or an extra deduction.
- Map every adopted or retained synthesis item to a stable finding, strength, or hypothesis ID. Keep not-adopted items visible with an explicit rationale and no score effect.
- Mark the host-native Product Design audit or Claude Design critique of a readable static screenshot as `Used`; describe unsupported interaction evidence in `限制`, and deduplicate overlapping findings after the pass runs.
