# Required and optional capability orchestration

Use the host-native design expert as a required independent full-breadth baseline around the Wira review core only after the design-goal intake gate is confirmed. Then inspect dimension coverage and adaptively fill supported gaps before adding any other scoped specialists. Specialists do not replace the confirmed product objective, Wira brand standard, baseline comparison, finding schema, or deterministic score.

## Mandatory baseline passes

Every review with a confirmed goal and at least one readable screenshot, accepted video frame, or inspectable Figma frame must log both baseline capabilities and successfully run the current host's native one.

If goal intake is incomplete, do not run or log a specialist pass as though a review started. Ask the goal question and stop before this orchestration stage.

| Execution host | Required used pass | Required cross-host record |
|---|---|---|
| `codex` | `codex-product-design` / `audit` | `claude-design` / `design-critique` = `unavailable` |
| `claude` | `claude-design` / `design-critique` | `codex-product-design` / `audit` = `unavailable` |
| `other` | No native expert can be invoked | Both baseline passes = `unavailable`; do not produce a scored final report |

Use `invocation: required` for both records. A readable static screenshot is sufficient input for either native baseline. Checklist overlap, routine review risk, or the Wira core's existing coverage is never a reason to skip the required pass.

If the native pass is missing, disabled, or fails, stop before deterministic scoring. Explain how to restore the dependency and mark the review incomplete; do not silently downgrade it to a core-only review.

## Authority and normalization contract

1. Confirm the user-declared or user-confirmed design goal and success criteria.
2. Run the Wira core intake and evidence check.
3. Run the mandatory host-native baseline pass against the accepted evidence at its full native breadth; do not reduce it to a preselected Wira checklist.
4. Build the dimension coverage matrix defined in [adaptive-dimension-complement.md](adaptive-dimension-complement.md).
5. When supported dimensions are `partial` or `missing`, run one Wira adaptive complement over only those gaps.
6. Select only additional capabilities whose trigger and required inputs are present.
7. Record every used, skipped, or unavailable pass in `capability_passes`.
8. Treat specialist and complement output as candidate material.
9. Verify each candidate against an accepted screenshot, video frame, Figma node, implementation state, design-system rule, or research record.
10. Merge duplicate symptoms into one root finding and assign one primary scoring dimension.
11. Add the contributing pass IDs to `source_pass_ids`; use `core` for the Wira review itself.
12. Add every materially distinct native or complement conclusion to `specialist_synthesis` and record whether it was adopted, retained for validation, or not adopted.
13. Score only the normalized final findings. Never average, add, or compare scores emitted by other plugins.

After the mandatory baseline, do not run additional generic critique passes merely to create apparent consensus. Add an optional specialist only when it contributes a different evidence source, checklist, or deliverable. This minimization rule never suppresses the mandatory baseline.

The Wira adaptive complement is not a second generic expert and does not simulate the unavailable cross-host plugin. It is a product-specific coverage repair triggered only by `partial` or `missing` dimensions. Do not create it when native coverage is already `full` for every applicable dimension.

## Specialist synthesis contract

Summarize specialist output; do not paste the full plugin response or hidden reasoning into the report.

- Create one `specialist_synthesis` item for each materially distinct conclusion from a used critique or specialist-review pass.
- Use `adopted` when the conclusion is verified and merged into a final finding or strength. Point `target_refs` to those final IDs and include the pass ID in each target's `source_pass_ids`.
- Use `retained_for_validation` when the conclusion is useful but needs missing states, measurements, prototype behavior, user perception, or analytics. Point it to a tentative finding or validation hypothesis; it does not deduct score.
- Use `not_adopted` when the conclusion is unverifiable, outside scope, superseded by stronger evidence, or adds no material value after deduplication. Leave `target_refs` empty and state the reason in `rationale`.
- Preserve conflicting interpretations as retained items unless direct evidence clearly resolves the conflict. Agreement between plugins increases review breadth, not evidence confidence.
- Preserve verified findings unique to the native expert or the Wira complement. Lack of a matching conclusion from the other source is not a rejection reason.
- Ensure every used pass whose purpose includes `candidate_findings` or `specialist_review` has at least one synthesis item, even when none of its candidates are adopted.

Use stable synthesis IDs such as `SI-001`. Keep `summary` concise and evidence-oriented so readers can understand the specialist's contribution without reopening its raw response.

Required and explicit invocations override optional pass minimization. Run the applicable focused skill before consolidation. Similarity to the Wira core is handled by merging duplicate findings afterward; it is never a reason to mark the pass `skipped`.

## Host routing

Use the capability exposed by the current host. Codex and Claude plugins cannot call each other across host boundaries, so do not pretend that the cross-host pass ran.

| Host | Preferred pass | Typical registered name | Result handling |
|---|---|---|---|
| Codex | Required Product Design screenshot or flow audit | `product-design:audit` | Must run before scoring; normalize candidates into `specialist_synthesis`, then merge verified items into final findings or strengths |
| Claude | Required Design critique | `design:design-critique` | Must run before scoring; normalize candidates into `specialist_synthesis`, then merge verified items into final findings or strengths |
| Claude | Focused specialist pass | `design:accessibility-review`, `design:design-system`, `design:ux-copy`, `design:user-research`, `design:research-synthesis`, or `design:design-handoff` | Use only when its trigger and inputs are present; never import its score directly |

On either host, add `wira-core / adaptive-dimension-complement` only after the native pass exposes supported coverage gaps. On Codex it commonly deepens color, brand, visual-language, copy-tone, or visible-accessibility checks. On Claude it commonly deepens goal-to-task fit, entry comprehension, baseline retention, social participation, state boundaries, or metric design. Route from observed coverage rather than assuming either expert is permanently limited to those areas.

Plugin namespacing is host-managed. In Claude Code, an explicitly invoked skill normally appears as `/design:design-critique`; automatic routing may invoke the same registered skill without a slash command. In Codex, follow the currently exposed Product Design router and focused skill. The shared report contract is identical on both hosts.

## Codex Product Design adapter

| Capability | Use in this workflow | Trigger | Boundary |
|---|---|---|---|
| `audit` | Inspect one supplied static screen or accepted frame, or capture a real flow step by step; contribute UX, visual, and accessibility candidates tied to accepted screenshots | Every readable design review executed on Codex | A static screen becomes one numbered step; its concise report does not replace Wira coverage tables or scoring |
| `research` | Research current user problems before defining a redesign opportunity | The user explicitly requests external UX research and current sources are available | Research is context, not direct proof that the supplied design solves the problem |
| `ideate` | Generate visual alternatives after root issues and the brief are clear | The user asks for redesign directions or variants | Keep outside the current design score; review generated directions as new artifacts in a later pass |
| `design-qa` | Compare a coded prototype with its selected visual source | An implementation and matched source visual both exist | This is implementation fidelity, not a substitute for product-quality review |
| `image-to-code`, `url-to-code`, `share` | Build or share an approved direction | The user explicitly requests implementation or sharing | Follow-on delivery only; never trigger during a review-only request |

Follow the current Product Design router and focused audit skill instructions. If it requires browser capture, preserve its accepted screenshots, step order, and capture limitations in the Wira evidence pack.

### Static screenshot protocol

A static screenshot is a valid Product Design `audit` input. It does not require a clickable prototype or browser session.

1. Treat each user-supplied screenshot in the current request as a numbered audit step, starting with `Step 1`.
2. Inspect the exact supplied image and reject it only when it is unreadable, blank, corrupted, or not the requested product surface.
3. Render or cite the accepted image in the audit output and tie every Product Design candidate to that step.
4. Review visible first impression, hierarchy, comprehension, consistency, content, and visible accessibility risks.
5. Mark interaction behavior, navigation outcomes, motion, loading, errors, focus order, screen-reader output, and unshown states as unsupported rather than failed.
6. Log the Product Design pass as `used` with `invocation: required`. State `single static screenshot` in its limitations and describe the candidate contribution range.

Do not mark a readable static screenshot pass `skipped` because the core review covers similar dimensions. Deduplicate shared observations during Wira consolidation and keep both pass IDs only when both materially contributed to the final finding.

## Claude Design adapter

| Capability | Use in this workflow | Trigger | Boundary |
|---|---|---|---|
| `design-critique` | Independent usability, hierarchy, consistency, and first-impression pass | Every readable design review executed on Claude | Required before scoring; normalize and deduplicate, and do not import its severity or score unchanged |
| `accessibility-review` | Focused contrast, touch-target, readability, keyboard, and assistive-technology checklist | Accessibility is requested, the design is near handoff, or implementation/Figma data can support it | A screenshot supports visible risks only; never claim WCAG compliance without implementation and manual testing |
| `design-system` | Audit tokens, components, variants, states, naming, and intentional extensions | A design system or inspectable Figma library is supplied, or the redesign introduces reusable patterns | Preserve Wira's `compliant / intentional_extension / undocumented_drift / violation` classification |
| `ux-copy` | Review labels, CTAs, errors, empty states, onboarding, and localization pressure | Copy affects comprehension, tone, participation pressure, or layout resilience | Apply the confirmed Wira voice and product vocabulary before accepting alternatives |
| `user-research` | Turn validation hypotheses into a research or usability-test plan | The review exposes unresolved behavior or perception questions | A plan does not change the current design score |
| `research-synthesis` | Convert real transcripts, surveys, usability notes, tickets, or NPS data into evidence-backed themes | Raw research data is supplied or connected | Never invent participants, prevalence, quotes, or behavioral evidence |
| `design-handoff` | Produce specs after a direction passes review | The user confirms a direction is ready for engineering | Follow-on deliverable; unresolved major findings and unknown states must remain visible |

The names above match the inspected official Design plugin snapshot. If a later installed version exposes different names, route by capability purpose and record the actual registered name in the capability-pass log.

## Default routing by review stage

| Stage | Required core | Optional capability |
|---|---|---|
| Objective and scope | Goal contract, baseline, Wira context | Product Design research only when explicitly requested |
| Evidence acquisition | Screenshot/video/Figma inspection | Required Product Design audit on Codex or required Claude design-critique on Claude |
| Main review | Wira multi-scale and color passes | Optional focused accessibility, design-system, or UX-copy passes when triggered |
| Coverage repair | Wira dimension coverage matrix | Adaptive Wira complement for supported `partial` or `missing` dimensions only |
| Specialist verification | Wira evidence and status rules | Accessibility, design-system, or UX-copy pass when triggered |
| Consolidation and score | Wira schema, deduplication, deterministic scorer | No external score import |
| Validation | Wira hypotheses and guardrail metrics | User-research plan or research synthesis with real data |
| Improvement | New artifact reviewed separately | Product Design ideate when visual alternatives are requested |
| Handoff and QA | Approved direction and unresolved-risk log | Claude design-handoff or Product Design design-qa |

## Failure and availability rules

- The user's invocation of this Plugin authorizes the required host-native baseline pass. Do not broaden that authorization to ideation, research, implementation, or handoff.
- Do not skip a required Product Design audit or Claude design critique merely because the input is static, the review is routine, or the Wira core covers similar topics.
- If the cross-host capability is unavailable, set it to `unavailable` and state the host boundary.
- If an applicable dimension is partial or missing after the native pass, run the adaptive complement before scoring; if it still lacks support, change the dimension to `N/A` or leave the review incomplete rather than inventing coverage.
- If the host-native required capability is unavailable or fails, stop before scoring and return an incomplete-review notice with the recovery action.
- If required visual evidence is unreadable or absent, do not create a scored review. Optional passes with missing inputs may be `skipped` with the missing input named.
- If two passes conflict, prefer stronger direct evidence. Otherwise preserve both as tentative interpretations and create a validation hypothesis.
- Never present plugin agreement as user validation, analytics evidence, or proof of business impact.

## Reference snapshot

- Codex Product Design package inspected: `product-design@openai-curated-remote`, version `0.1.50`, on 2026-07-15. Always follow the currently installed router because capabilities may change.
- Claude Design capability mapping inspected from Anthropic's `knowledge-work-plugins/design` at commit `13710bc278e9f1a9c40e0c37056529d302f276d8`: <https://github.com/anthropics/knowledge-work-plugins/tree/13710bc278e9f1a9c40e0c37056529d302f276d8/design>.
