# Design review report template

Use these seven user-facing sections for every review. Keep the underlying profile dimensions and deterministic score; the report sections reorganize evidence for readability and must not create duplicate deductions.

## 1. Overall Impression / 整体印象

Include:

- one-sentence verdict;
- overall score and score confidence;
- redesign delta when comparison is valid;
- redesign-goal status and the most important evidence limitation.

Do not claim the redesign is better when its primary objective is missing or inferred.

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
4. screen/section, component/element, and state/edge-case audit tables;
5. detailed finding cards ordered by severity and task impact;
6. validation hypotheses and target metrics;
7. evidence limitations and untested areas;
8. capability-pass log with provider, purpose, status, inputs, contribution scope, and limitations;
9. saved artifact locations.

Render the capability-pass log as:

| ID | Provider | Capability | Trigger | Status | Input kind / source | Contribution scope | Limitations |
|---|---|---|---|---|---|---|---|
| P-01 | Codex Product Design | audit | Explicit | Used | Static screenshot / CAND-HOME-01 | Evidence and candidate findings | Interaction and unshown states unsupported |

## Rendering rules

- `Overall Impression`, `What Works Well`, and `Priority Recommendations` are report sections, not scoring dimensions.
- `Usability` is a non-duplicating roll-up of existing dimensions for `wira-v2`; do not subtract points again.
- `Visual Hierarchy`, `Consistency`, and `Accessibility` expose their underlying dimension scores where an exact mapping exists.
- Use `N/A` rather than an inferred pass when evidence or redesign context is insufficient.
- Show specialist provenance through `source_pass_ids`, but never use the number of agreeing passes as evidence strength or an extra deduction.
- Mark an explicitly requested Product Design audit of a readable static screenshot as `Used`; describe unsupported interaction evidence in `限制`, and deduplicate overlapping findings after the pass runs.
