# Optional capability orchestration

Use external design capabilities as scoped expert passes around the Wira review core. They expand evidence or depth; they do not replace the confirmed product objective, Wira brand standard, baseline comparison, finding schema, or deterministic score.

## Authority and normalization contract

1. Run the Wira core intake and evidence check first.
2. Select only capabilities whose trigger and required inputs are present.
3. Record every used, skipped, or unavailable pass in `capability_passes`.
4. Treat specialist output as candidate material.
5. Verify each candidate against an accepted screenshot, video frame, Figma node, implementation state, design-system rule, or research record.
6. Merge duplicate symptoms into one root finding and assign one primary scoring dimension.
7. Add the contributing pass IDs to `source_pass_ids`; use `core` for the Wira review itself.
8. Add every materially distinct specialist conclusion to `specialist_synthesis` and record whether it was adopted, retained for validation, or not adopted.
9. Score only the normalized final findings. Never average, add, or compare scores emitted by other plugins.

Do not run multiple generic critique passes merely to create apparent consensus. Add a specialist only when it contributes a different evidence source, checklist, or deliverable.

## Specialist synthesis contract

Summarize specialist output; do not paste the full plugin response or hidden reasoning into the report.

- Create one `specialist_synthesis` item for each materially distinct conclusion from a used critique or specialist-review pass.
- Use `adopted` when the conclusion is verified and merged into a final finding or strength. Point `target_refs` to those final IDs and include the pass ID in each target's `source_pass_ids`.
- Use `retained_for_validation` when the conclusion is useful but needs missing states, measurements, prototype behavior, user perception, or analytics. Point it to a tentative finding or validation hypothesis; it does not deduct score.
- Use `not_adopted` when the conclusion is unverifiable, outside scope, superseded by stronger evidence, or adds no material value after deduplication. Leave `target_refs` empty and state the reason in `rationale`.
- Preserve conflicting interpretations as retained items unless direct evidence clearly resolves the conflict. Agreement between plugins increases review breadth, not evidence confidence.
- Ensure every used pass whose purpose includes `candidate_findings` or `specialist_review` has at least one synthesis item, even when none of its candidates are adopted.

Use stable synthesis IDs such as `SI-001`. Keep `summary` concise and evidence-oriented so readers can understand the specialist's contribution without reopening its raw response.

Explicit invocation overrides automatic pass minimization. If the user explicitly invokes Product Design for a review and the capability is available, run the applicable focused skill before consolidation. Similarity to the Wira core is handled by merging duplicate findings afterward; it is never a reason to mark the requested pass `skipped`.

## Codex Product Design adapter

| Capability | Use in this workflow | Trigger | Boundary |
|---|---|---|---|
| `audit` | Inspect one supplied static screen or capture a real flow step by step; contribute UX, visual, and accessibility candidates tied to accepted screenshots | The user explicitly invokes Product Design for a screen or flow audit, or a live experience benefits from screenshot capture | A static screen becomes one numbered step; its concise report does not replace Wira coverage tables or scoring |
| `research` | Research current user problems before defining a redesign opportunity | The user explicitly requests external UX research and current sources are available | Research is context, not direct proof that the supplied design solves the problem |
| `ideate` | Generate visual alternatives after root issues and the brief are clear | The user asks for redesign directions or variants | Keep outside the current design score; review generated directions as new artifacts in a later pass |
| `design-qa` | Compare a coded prototype with its selected visual source | An implementation and matched source visual both exist | This is implementation fidelity, not a substitute for product-quality review |
| `image-to-code`, `url-to-code`, `share` | Build or share an approved direction | The user explicitly requests implementation or sharing | Follow-on delivery only; never trigger during a review-only request |

When Product Design is explicitly invoked, follow its current router and focused skill instructions. If it requires browser capture, preserve its accepted screenshots, step order, and capture limitations in the Wira evidence pack.

### Static screenshot protocol

A static screenshot is a valid Product Design `audit` input. It does not require a clickable prototype or browser session.

1. Treat each user-supplied screenshot in the current request as a numbered audit step, starting with `Step 1`.
2. Inspect the exact supplied image and reject it only when it is unreadable, blank, corrupted, or not the requested product surface.
3. Render or cite the accepted image in the audit output and tie every Product Design candidate to that step.
4. Review visible first impression, hierarchy, comprehension, consistency, content, and visible accessibility risks.
5. Mark interaction behavior, navigation outcomes, motion, loading, errors, focus order, screen-reader output, and unshown states as unsupported rather than failed.
6. Log the Product Design pass as `used`. State `single static screenshot` in its limitations and describe the candidate contribution range.

Do not mark a readable static screenshot pass `skipped` because the core review covers similar dimensions. Deduplicate shared observations during Wira consolidation and keep both pass IDs only when both materially contributed to the final finding.

## Claude Design adapter

| Capability | Use in this workflow | Trigger | Boundary |
|---|---|---|---|
| `design-critique` | Independent usability, hierarchy, consistency, and first-impression pass | A high-stakes review needs a peer pass, or the user explicitly asks for Claude critique | Normalize and deduplicate; do not import its severity or score unchanged |
| `accessibility-review` | Focused contrast, touch-target, readability, keyboard, and assistive-technology checklist | Accessibility is requested, the design is near handoff, or implementation/Figma data can support it | A screenshot supports visible risks only; never claim WCAG compliance without implementation and manual testing |
| `design-system` | Audit tokens, components, variants, states, naming, and intentional extensions | A design system or inspectable Figma library is supplied, or the redesign introduces reusable patterns | Preserve Wira's `compliant / intentional_extension / undocumented_drift / violation` classification |
| `ux-copy` | Review labels, CTAs, errors, empty states, onboarding, and localization pressure | Copy affects comprehension, tone, participation pressure, or layout resilience | Apply the confirmed Wira voice and product vocabulary before accepting alternatives |
| `user-research` | Turn validation hypotheses into a research or usability-test plan | The review exposes unresolved behavior or perception questions | A plan does not change the current design score |
| `research-synthesis` | Convert real transcripts, surveys, usability notes, tickets, or NPS data into evidence-backed themes | Raw research data is supplied or connected | Never invent participants, prevalence, quotes, or behavioral evidence |
| `design-handoff` | Produce specs after a direction passes review | The user confirms a direction is ready for engineering | Follow-on deliverable; unresolved major findings and unknown states must remain visible |

Claude command names and installed-skill names may differ by host version. Route by capability purpose rather than assuming an exact slash command.

## Default routing by review stage

| Stage | Required core | Optional capability |
|---|---|---|
| Objective and scope | Goal contract, baseline, Wira context | Product Design research only when explicitly requested |
| Evidence acquisition | Screenshot/video/Figma inspection | Product Design audit for a supplied static screen or live-flow capture |
| Main review | Wira multi-scale and color passes | Claude design-critique for an independent high-stakes pass |
| Specialist verification | Wira evidence and status rules | Accessibility, design-system, or UX-copy pass when triggered |
| Consolidation and score | Wira schema, deduplication, deterministic scorer | No external score import |
| Validation | Wira hypotheses and guardrail metrics | User-research plan or research synthesis with real data |
| Improvement | New artifact reviewed separately | Product Design ideate when visual alternatives are requested |
| Handoff and QA | Approved direction and unresolved-risk log | Claude design-handoff or Product Design design-qa |

## Failure and availability rules

- Do not install, enable, or call an external plugin without the user's request or the host's normal capability rules.
- Do not skip an explicitly requested, available Product Design audit merely because the input is static or the Wira core covers similar topics.
- If a named capability is unavailable, set the pass to `unavailable`, state the missing capability, and continue with the Wira core.
- If required inputs are absent, set the pass to `skipped` and name the missing input rather than simulating the specialist result.
- If two passes conflict, prefer stronger direct evidence. Otherwise preserve both as tentative interpretations and create a validation hypothesis.
- Never present plugin agreement as user validation, analytics evidence, or proof of business impact.

## Reference snapshot

- Codex Product Design package inspected: `product-design@openai-curated-remote`, version `0.1.50`, on 2026-07-15. Always follow the currently installed router because capabilities may change.
- Claude Design capability mapping inspected from Anthropic's `knowledge-work-plugins/design` at commit `13710bc278e9f1a9c40e0c37056529d302f276d8`: <https://github.com/anthropics/knowledge-work-plugins/tree/13710bc278e9f1a9c40e0c37056529d302f276d8/design>.
