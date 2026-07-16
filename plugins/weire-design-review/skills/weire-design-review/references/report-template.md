# 设计评审报告模板

The scored JSON is the source of truth. Keep one complete review model and render it in one of two modes:

- `designer_summary` is the default visible response for designers.
- `audit_full` is the complete evidence and governance report, rendered only when the user explicitly asks for the full report, scoring detail, coverage, expert logs, or an audit archive.

Both modes use the same findings, strengths, score, and development-readiness gate. Presentation must never change the score.

All designer-facing content must use Simplified Chinese only, including report titles, section headings, field labels, severity labels, conclusions, findings, recommendations, and checklist text. Keep stable IDs such as `F-001`, metric names supplied by the user, and necessary product or capability names unchanged. Never pair a Chinese label with an English translation.

Do not render either report while design-goal intake is incomplete. The intake response contains only artifact receipt/source confirmation and the required question from [design-goal-gate.md](design-goal-gate.md).

## 模式 A：设计师简版（默认）

The default report answers five practical questions in the smallest useful surface:

1. What did this design score?
2. Can it enter development?
3. What exactly must change, and how important is each issue?
4. What should not be lost during revision?
5. What conditions must the next version satisfy?

Do not expose dimension score tables, coverage matrices, capability logs, specialist synthesis, or raw confidence/delta/evidence-level metadata unless one of them is necessary to explain why the readiness result is `insufficient_evidence`.

### 1. 评审结果

Use a compact callout:

```markdown
## 评审结果

**{overall_score} 分｜{development_readiness.label}**

- **开发标准：** 85 分以上，且没有计分的阻断或重大问题，证据充分
- **本次目标：** {confirmed design goal}
- **判断依据：** {plain-language readiness reasons and blocker/major counts}
- **下一步：** {development_readiness.recommended_action}
```

Rules:

- Put the score and readiness label on the first visible line.
- Translate readiness reason codes into plain language. Mention related finding IDs where useful.
- If a severity override changed the result, say so directly: for example, `总分达到 85，但 F-001 为重大问题，因此不能正常进入开发`.
- If evidence is insufficient, replace false precision with `证据不足，暂不判定开发准入`, explain the missing source, and request the smallest evidence needed.
- Clarify in one sentence that this is design readiness, not technical feasibility or release approval.
- Include redesign delta only when matched evidence supports it.

### 2. 优先改稿清单

Show all confirmed findings. Order them by severity, core-task impact, dependency, then confidence. Use one compact task card per finding:

```markdown
### F-001｜重大｜{title}

**位置：** {finding.location}

**问题：** {one concrete visible issue}

**为什么重要：** {one short user, task, brand, accessibility, or guardrail consequence}

**怎么优化：**

- {specific design action}
- {optional dependent action}

**完成标准：**

- {observable acceptance criterion}
- {optional metric, prototype task, or implementation measurement}
```

Severity labels:

- `blocker` → `阻断`
- `major` → `重大`
- `moderate` → `一般`
- `minor` → `轻微`

Writing rules:

- `位置` must identify the screen/step and visible region or state. Do not use a vague label such as `首页整体` when a smaller location is observable.
- `问题` describes the visible mechanism, not a taste word. Translate `脏`, `土`, `暧昧`, or `下沉` into color, contrast, material, hierarchy, content, or category-signaling evidence.
- `怎么优化` must be an action a designer can perform. Avoid `加强层级`, `提升品质`, or `优化体验` without specifying what changes.
- `完成标准` must make closure reviewable. It can be a visible condition, token or measurement, prototype task result, or required user test.
- Keep evidence provenance and raw measurements in the full audit. Include a measurement in the summary only when the action depends on it, such as contrast or touch target size.
- Do not cap the number of confirmed problem cards. A concise report means compact cards, not hidden issues.

Put tentative findings in a separate subsection after all confirmed tasks:

```markdown
### 待验证（不扣分）

- `F-006` {hypothesis} → {evidence or test needed}
```

Never mix tentative findings into the must-fix list or present a validation hypothesis as observed behavior.

### 3. 本轮需要保留

Render up to three evidence-backed strengths that could be accidentally lost during revision:

```markdown
## 本轮需要保留

- `W-001` {specific strength} — {why it supports the goal, usability, brand, or system}
```

Prefer strengths related to the confirmed goal or effective existing behavior. Do not use generic praise. If no strength is confirmed, write `暂无需要特别锁定的保留项`.

### 4. 修改后复审条件

Convert the accepted findings into a closure checklist:

```markdown
## 修改后复审条件

- [ ] F-001：{short completion criterion}
- [ ] F-002：{short completion criterion}
- [ ] 总分达到 85 分以上
- [ ] 没有计分的阻断或重大问题
- [ ] 关键结论的证据充分；截图无法判断的交互或状态已用原型、录屏、Figma 数值或实现验证补齐
```

Include every blocker and major finding. Add high-impact moderate findings when they are dependencies for the redesign goal or development handoff. Do not turn every minor polish item into a release gate.

If files were saved, end with one unobtrusive line:

```markdown
完整审计与评分依据已保存：{full_report_path} · {scored_json_path}
```

Do not paste the full audit after the designer summary unless the user requested it.

## 模式 B：完整审计（按需）

Render these seven user-facing sections in order:

1. 整体印象
2. 易用性
3. 视觉层级
4. 一致性
5. 无障碍性
6. 做得好的地方
7. 优先改进建议

### 整体印象

Include the one-sentence verdict, confirmed design goal and success criteria, host-specific review engine, overall score and score confidence, development-readiness result, redesign delta when valid, design-goal status, and the most important evidence limitation.

Render the readiness callout immediately after the verdict:

```markdown
### 开发准入

**结论：** {scores.development_readiness.label}

- **依据：** {overall score, evidence confidence, translated reason codes, and related finding IDs}
- **正常开发线：** 85 分
- **下一步：** {scores.development_readiness.recommended_action}
```

Clarify that this covers design readiness, not technical feasibility or release approval.

### 易用性

Summarize whether users can understand the current goal, find the next action, predict the result, participate with low pressure, and recover from represented states. Reuse the relevant profile findings; do not create another deduction.

### 视觉层级

Summarize focus, primary action, scan order, grouping, density, and competing accents. Use `visual_hierarchy` when present; otherwise cite the closest supported visual-system evidence.

### 一致性

Summarize visual-language coherence and design-system behavior. Cover material, form, graphic or illustration style, media, motion character, components, and semantic tokens only where evidence exists.

### 无障碍性

Summarize contrast, text legibility, touch targets, color dependence, focus, scaling, and reduced-motion risks. Separate measured violations from visual estimates. Never claim full compliance from screenshots alone.

### 做得好的地方

Render evidence-backed strengths. Prefer strengths that support the design goal, brand, usability, or system coherence. Do not invent praise.

### 优先改进建议

Select at most three root-cause changes from confirmed findings. Write each as `action → expected design or user outcome → metric or validation method when needed`. This summary does not replace the full finding list.

## Full-audit detail order

After the seven sections, render:

1. `Dimension Coverage & Complement`: every profile dimension, native-expert coverage, gap, Wira complement status, final coverage, and source pass IDs.
2. `Screen / Section Coverage`: every visible region, its purpose, review status, and related finding IDs.
3. `Component / Element Audit`: core, repeated, novel, inconsistent, and risky components; group low-risk standard components when appropriate.
4. `State / Edge-case Audit`: relevant quantities, content boundaries, interaction states, device conditions, loading, empty, error, and recovery behavior.
5. Detailed finding cards.
6. Validation hypotheses and evidence limitations.
7. Dimension score detail and deterministic readiness reasons.
8. Frozen native-expert snapshot and its full candidate list.
9. Specialist synthesis, including the final disposition of every native candidate.
10. Capability-pass log.

For detailed cards, preserve ID, severity, status, confidence, delta, evidence level, location, evidence, impact, recommendation, completion criteria, and validation. Tentative findings remain visible but explicitly do not deduct score.

The frozen native snapshot must precede specialist synthesis. Show its execution mode, preserved artifact reference, five native framework conclusions, and complete `NC-xxx` candidate list. The specialist-synthesis table must map every native candidate exactly once before the capability-pass log. Show which conclusions were adopted, retained for validation, or rejected, with target IDs and rationale. The capability log must make the required host-native baseline visible, distinguish the Wira adaptive complement from the unavailable cross-host expert, and record optional capabilities as used, skipped, or unavailable.

Use `N/A` for unsupported dimensions. Never represent `N/A` as zero.
