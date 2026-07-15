# Redesign comparison workflow

Use this workflow when current production UI, a design system, and a candidate redesign exist.

## Minimum evidence matrix

| Evidence | Purpose | If missing |
|---|---|---|
| Current production screen or flow | establish behavioral and visual baseline | mark delta `unknown`; run standalone review |
| Candidate design at matched state | inspect the proposed change | block comparison for that state |
| Confirmed design system | evaluate token and component consistency | report visual consistency only; do not claim system violations |
| Primary redesign objective | understand intended improvement and isolate the main variable | set goal status to `missing` or `inferred`; do not claim a core-task improvement |
| Prototype or video | evaluate sequence, feedback, and motion | mark interaction dimensions `N/A` |
| Analytics or user test | validate behavioral outcome | output hypotheses, not outcomes |

## Procedure

1. Complete the goal contract below before judging whether the redesign is better.
2. Match baseline and candidate by task, viewport, platform, content, and state.
3. Inventory visible changes before judging them: information, hierarchy, navigation, components, color roles, material, form, graphic/illustration style, media, copy, state, and motion.
4. Check visual-language coherence and confirmed design-system compliance; label intentional deviations separately.
5. Compare task clarity and social participation pressure across the matched flow.
6. Mark each meaningful change `better`, `same`, `worse`, or `unknown`, with evidence and rationale.
7. Score baseline and candidate with the same profile, applicable dimensions, and evidence standard. If scope differs, do not present the numerical difference as a clean improvement.
8. Convert unresolved product effects into testable hypotheses.

## Redesign goal contract

Record:

- one `primary_objective`;
- `objective_type`: behavior, interaction, visual-language, or systemization;
- target user and target behavior or perception;
- one `primary_metric` and guardrail metrics;
- the `primary_changed_variable`;
- important areas intentionally held constant;
- secondary changes required to support the primary variable.

One objective may require several coordinated changes. The problem is not the number of changed pixels; it is the lack of a declared causal priority. If navigation, interaction, content hierarchy, palette, and visual style all change independently, report a variable-isolation risk.

Set `redesign_goal_status` to:

- `confirmed`: explicitly supplied or approved; core-task delta may be scored;
- `inferred`: plausible but not approved; show the assumption and keep core-task delta `N/A`;
- `missing`: no defensible primary objective; audit the artifact, but do not issue an overall “redesign is better” verdict and keep core-task delta `N/A`.

For Wira `wira-v2`, classify system differences as:

- `compliant`: uses an existing token, component, state, or documented pattern;
- `intentional_extension`: changes the system for a stated product goal and can become a reusable rule;
- `undocumented_drift`: differs without a reusable rule or rationale;
- `violation`: conflicts with a confirmed semantic, accessibility, or component constraint.

Do not make “matches the old homepage composition” a quality requirement. The current design system documents production accurately, but a redesign may need to replace page-composition tokens. Require the replacement to be coherent and documented.

## Delta table

For each important change report:

| Area | Baseline | Candidate | Delta | Evidence | Risk or next test |
|---|---|---|---|---|---|

Do not use `better` to mean merely newer, cleaner, or more fashionable. Tie it to a confirmed goal, reduced friction, clearer structure, stronger system fit, or better-supported brand direction.

## Validation hypothesis format

Write:

`Because <design change>, we expect <user behavior> for <target users>, measured by <primary metric>, while guarding <secondary metric or risk>.`

Example:

`Because active room interaction replaces static portrait emphasis, we expect more users to enter a room based on shared activity, measured by room-entry rate, while guarding post-entry dwell and gift conversion.`
