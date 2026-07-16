---
name: weire-design-review
description: Evidence-based design review for 微热/Weire/Wira/Laboo mobile product screenshots, screen recordings, production baselines, design systems, exported design files, or Figma links. Use when Codex or Claude is asked to 评审微热设计稿、比较微热新版和线上版、审查首页/房间/社交流程、检查品牌与设计系统、分析交互视频、评价 Figma 页面或生成微热设计评分。 Requires a user-confirmed design goal, runs the current host's full native Product Design or Claude Design critique, then adaptively complements uncovered Wira dimensions before deterministic scoring.
---

# Weire Design Review

Run a repeatable mobile design review whose conclusions point to visible evidence and declared product context. Treat scores as summaries of supported findings, never as unsupported aesthetic opinions.

## Select the review profile and mode

- Use `generic-mobile-v1` for products without a configured product profile.
- Use `wira-v1` for 微热, Wira, or Laboo when only product context is available.
- Use `wira-v2` for a Wira redesign when matched production evidence and the existing design system are available. Read [wira-brand-standard.md](references/wira-brand-standard.md), [wira-product-context.md](references/wira-product-context.md), and [wira-design-system-evidence.md](references/wira-design-system-evidence.md) completely before reviewing.
- Use `artifact` mode for one design source, `redesign-comparison` for current versus new, `flow-audit` for a task journey, and `direction-comparison` for A/B/C design directions.
- Default Wira homepage optimization work to `redesign-comparison`. Follow [comparison-workflow.md](references/comparison-workflow.md).

## Orchestrate required and optional specialist capabilities

Read [capability-orchestration.md](references/capability-orchestration.md) whenever Codex Product Design, Claude Design, Figma, browser capture, research data, ideation, or developer handoff is available or requested.

- Keep this skill's evidence rules, Wira brand standard, finding consolidation, and score as the authority.
- Identify `review.execution_host` as `codex`, `claude`, or `other` before specialist routing.
- After the design goal is confirmed, run the host-native baseline pass for every review with readable visual evidence: Product Design `audit` on Codex; Design `design-critique` on Claude. This pass is required even for a single static screenshot and even when its checklist overlaps the core review.
- Let the host-native expert review at full breadth. Do not pre-assign it only selected Wira dimensions or suppress material conclusions because another host tends to cover them.
- Record the other platform's baseline pass as `unavailable` because host plugins cannot be invoked across platforms. Do not call it `skipped`.
- If the host-native baseline capability is missing, disabled, or fails, stop before scoring. State how to install or restore it and do not deliver a completed review.
- After the required baseline, select the smallest useful set of additional specialist passes. Do not run every optional capability by default.
- Honor an explicit Product Design or Claude Design invocation when the matching host capability is available and the supplied artifact is readable. Run the pass first and deduplicate its output later; overlap with the core review is not a skip reason.
- Treat specialist output as candidate findings or follow-on material until it is checked against accepted evidence and normalized into this skill's schema.
- After the full native pass, run [adaptive-dimension-complement.md](references/adaptive-dimension-complement.md). Build `scope.dimension_coverage`, then use the Wira adaptive complement only for applicable dimensions whose native coverage is `partial` or `missing`.
- Never label the Wira complement as the unavailable cross-host expert. Preserve the native expert's complete material contributions and record complement provenance separately.
- Continue with the core workflow when an additional optional capability is unavailable. Record the unavailable or skipped pass; do not imply that it ran.
- Do not start ideation, research, implementation, or handoff merely because those capabilities exist. Use them only when the user requests that stage or it is necessary for the declared review goal.

## Core workflow

1. Establish the context pack.
   - Run [design-goal-gate.md](references/design-goal-gate.md) before inspecting design quality. If a screenshot, video, or Figma link arrives without a confirmed goal and success criterion, ask the required intake question and stop this turn.
   - Do not infer or silently choose the goal. Do not run core checks, specialist passes, findings, recommendations, scoring, or development readiness until the user confirms the goal contract.
   - Identify platform, target users, core task, review mode, design stage, profile, and requested screens or flow.
   - Locate the current production baseline, design system, new design, target metrics, and any confirmed brand charter.
   - For redesigns, establish one primary redesign objective, its metric, guardrails, main changed variable, and held-constant areas before claiming improvement. Follow [comparison-workflow.md](references/comparison-workflow.md).
   - Treat production UI as a comparison baseline, not as proof that an existing choice is correct.
   - Treat candidate brand principles as hypotheses. Do not issue confirmed deductions from them until the user marks them confirmed. The Wira brand standard is confirmed and binding for `wira-v2`.
2. Acquire and inspect evidence.
   - Start this step only after `context.design_goal_status` is `confirmed` with a `user_declared` or `user_confirmed` source.
   - Follow [input-handling.md](references/input-handling.md) for each source type.
   - Inspect every accepted screenshot or key frame before citing it.
   - Assign stable screen IDs. Preserve video timestamps, Figma node IDs, version labels, and design-system references when available.
3. Define applicability before reviewing.
   - Mark each profile dimension applicable or unsupported.
   - Record evidence confidence from 0 to 1 for every applicable dimension.
   - Do not convert missing evidence into a low score.
4. Run the required host-native expert pass.
   - Follow [capability-orchestration.md](references/capability-orchestration.md) and record each considered pass in `capability_passes`.
   - On Codex, load and run Product Design `audit` for accepted screenshots or screenshot-first flow steps before consolidation.
   - On Claude, load and run Design `design-critique` against the same accepted evidence before consolidation.
   - For a readable static screenshot, run the required baseline as a one-step critique and mark interaction, motion, unshown states, and full accessibility compliance unsupported.
   - Run the native expert without narrowing its framework. Preserve every materially distinct conclusion in `specialist_synthesis`, including verified unique findings that the Wira core did not anticipate.
5. Run the Wira core and adaptive complement passes.
   - Run measurable checks: contrast when measurable, text size, touch target, clipping, alignment, tokens, components, and platform-rule violations.
   - Run semantic checks: hierarchy, comprehension, task clarity, cognitive load, recovery, state continuity, participation pressure, and motion meaning.
   - Run contextual checks: confirmed brand alignment, design-system fit, baseline delta, and intended product behavior.
   - Run [visual-language-consistency.md](references/visual-language-consistency.md) when reviewing a redesign, style refresh, design-system change, or cross-screen experience.
   - Run [multi-scale-audit.md](references/multi-scale-audit.md) for every artifact. Review flow, screen, region, component, element/property, and state/boundary levels; record every visible region in the coverage table.
   - Run the mandatory color-perception pass in [color-perception-audit.md](references/color-perception-audit.md) whenever the task evaluates visual style, palette, brand direction, or a redesign.
   - Follow [review-framework.md](references/review-framework.md). Record strengths as well as problems.
   - Read [adaptive-dimension-complement.md](references/adaptive-dimension-complement.md) completely. Mark native coverage for every applicable profile dimension; supplement only `partial` or `missing` dimensions with one `wira-core / adaptive-dimension-complement` pass.
   - Do not score while an applicable dimension remains `missing`. Use `partial` after supplementation when the accepted evidence still limits the conclusion; use `unsupported` and `N/A` when the evidence cannot support the dimension.
   - Use Claude accessibility, design-system, or UX-copy capabilities only for their additional scoped checks.
   - Map accepted specialist contributions to `source_pass_ids`. A specialist label never substitutes for evidence.
   - Record each materially distinct specialist conclusion in `specialist_synthesis`: map adopted conclusions to final findings or strengths, retain uncertain conclusions as tentative findings or validation hypotheses, and state why rejected conclusions were not used.
6. Separate conclusions by evidence type.
   - `confirmed`: directly supported by the inspected artifact, baseline, confirmed design system, or confirmed product principle.
   - `tentative`: plausible but depends on missing context or an unconfirmed product principle. Do not deduct score.
   - `validation_hypothesis`: requires prototype testing or behavioral data. Never present it as an observed outcome.
7. Consolidate findings.
   - Merge repeated symptoms caused by one root issue and keep one primary dimension per finding.
   - Consolidate the native expert and Wira complement together. A verified native-only or complement-only conclusion remains eligible for the final report and score; agreement never creates a second deduction.
   - Avoid fabricated measurements. State `visually estimated` when no measurement tool was used.
   - For redesigns, mark every finding or strength `better`, `same`, `worse`, or `unknown` relative to the matched baseline when the schema supports it.
8. Score deterministically.
   - Create review JSON matching [result-schema.md](references/result-schema.md).
   - Run `python3 scripts/review_score.py <review.json> --write` from this skill directory.
   - Fix validation errors instead of manually inventing a score.
   - Read [development-readiness.md](references/development-readiness.md) and use the generated `development_readiness` gate without overriding its thresholds or severity rules.
9. Deliver the review.
   - Lead with verdict, score, confidence, development readiness, and redesign delta when applicable.
   - Render accepted evidence inline when possible.
   - Render the seven fixed report sections and appendix in [report-template.md](references/report-template.md).
   - Save evidence, scored JSON, and a Markdown report when the environment supports files.

## Source boundaries

- A screenshot supports static visual, content, and some usability or accessibility observations. It does not prove interaction quality, responsiveness, performance, or full accessibility compliance.
- A video supports temporal flow, feedback, transition, and state continuity only for interactions shown.
- A Figma file supports structure and design-system checks only for nodes and properties successfully inspected. A prototype does not prove production behavior.
- Analytics support observed behavioral outcomes but do not by themselves explain causality.
- Mixed evidence expands applicability only when each conclusion cites its supporting source.

## Severity rules

- `blocker`: prevents the core task, creates an unrecoverable state, or introduces a critical accessibility barrier.
- `major`: materially harms comprehension, completion, trust, or repeated use.
- `moderate`: creates hesitation, inconsistency, unnecessary effort, or a likely accessibility problem.
- `minor`: polish issue with limited task impact.

Write recommendations as an action plus expected outcome. Phrase metric effects as hypotheses unless user evidence proves them.

Never translate stakeholder words such as `脏`, `土`, `暧昧`, or `下沉` directly into a deduction. Identify the visible mechanism first, then separate measurable color evidence, perceptual risk, and category-association hypothesis.

## Required output surface

Use these fixed user-facing sections in order:

1. Overall Impression / 整体印象
2. Usability / 易用性
3. Visual Hierarchy / 视觉层级
4. Consistency / 一致性
5. Accessibility / 无障碍性
6. What Works Well / 做得好的地方
7. Priority Recommendations / 优先改进建议

Follow them with the evidence and scoring appendix defined in [report-template.md](references/report-template.md). Keep detailed profile dimensions underneath this presentation layer and never deduct twice when a finding appears in a roll-up section.

Inside `Overall Impression`, always render the scored `Development Readiness / 开发准入` callout. State the 85-point normal development line, any score or severity override, evidence sufficiency, and the required next action.

After the seven summary sections, render every finding as a numbered detail card with severity, status, confidence, delta, evidence, impact, recommendation, and validation. Do not replace these cards with a one-line issue list.

Before the finding cards, render dimension coverage/adaptive complement, screen/section coverage, component/element audit, and relevant state/edge-case tables. Apply these to every scene, not only repeated cards or collections.

In the appendix, render the specialist synthesis before the capability-pass log. Show what each used specialist contributed, where it entered the report, and why a candidate was retained or rejected. Then render the capability-pass log so readers can confirm the host-native baseline actually ran, distinguish the core review from additional specialist contributions, and see which cross-host or optional capabilities were unavailable or deliberately skipped.

Use `N/A` for unsupported dimensions. Never represent `N/A` as zero.
