# Element accountability and lifecycle audit

Run this audit after the frozen native-expert snapshot and before finding consolidation. Its purpose is to catch small semantic elements that broad screen-level critique often skips, without turning unsupported interaction assumptions into scored findings.

## What must be inventoried

Inspect every accepted screen or frame and individually register semantically loaded micro-elements:

- badges, tags, corner marks, `NEW`, `HOT`, `上新`, limited-time, recommendation, and unread labels;
- counters, remaining-use labels, countdowns, quotas, prices, progress, and numeric status;
- presence dots, speaking indicators, unread dots, selection marks, and status icons;
- carousel dots, page indicators, overflow hints, and partial-item affordances;
- transient prompts, tooltips, bubbles, coach marks, and one-time guidance;
- icons, graphics, and microcopy whose removal or misreading changes a decision.

Group only conventional low-risk elements whose semantics, behavior, and design-system rule are already clear. Do not hide a novel, promotional, stateful, inconsistent, or core-task element inside a grouped row.

## Mandatory scan sequence

1. Inspect the original-resolution artifact region by region from top-left to bottom-right.
2. Perform a text-and-symbol sweep before making overall judgments. Transcribe short labels, numbers, dots, corner marks, and repeated indicators even when they are visually small.
3. Classify each transcribed or symbolic element by semantic role and whether it implies per-user, temporal, quantity, or interaction state.
4. Run the deletion test and lifecycle questions below.
5. Only then consolidate element items into findings, validation work, or no-issue records.

Do not rely on memory from the whole-screen critique for this pass. The structured ledger is the scan artifact.

## Element accountability questions

For every inventoried item, answer:

1. What semantic role does it claim: status, promotion, action, navigation, feedback, content, decoration, or unknown?
2. What user decision or understanding does it support?
3. Is it necessary, supportive, redundant, or still unknown?
4. If deleted, what material information or action is lost?
5. Does it require a lifecycle? If yes, what makes it appear, update, exit, recur, and what is the default state?
6. Does it look interactive, and if so, is the interaction result defined?
7. Is its component, token, placement, and terminology defined by the design system?

Apply the deletion test: when deleting the element produces no material loss, classify it as `redundant` or retain it for validation; never close it as `no_issue` without contrary evidence. This operationalizes “如无必要，勿增实体”.

## Lifecycle evidence boundary

Use these lifecycle evidence states:

- `complete`: appearance, update, exit, recurrence, and default-state rules are supported;
- `partial`: some rules are supported and others remain unknown;
- `missing`: an inspectable Figma flow, PRD, design-system rule, or implementation scope should define the lifecycle but does not;
- `unsupported`: the supplied screenshot or limited evidence cannot reveal the lifecycle;
- `not_applicable`: the element has no temporal or user-specific state.

A static screenshot can confirm that a state-like element is visible, but cannot by itself prove that its lifecycle is missing. Use `validation_required` for that case. A confirmed lifecycle finding requires stronger evidence such as an inspected Figma flow, PRD, design-system rule, video, or implementation.

Do not require one universal exit rule. For example, `上新` may disappear after first meaningful visit when it means “unseen by this user”, or expire by time/version when it means “recently released”. The problem is the absent or conflicting state contract, not failure to use a specific dismissal trigger.

## Assessment and target mapping

Each ledger item uses one assessment:

- `no_issue`: its purpose, necessity, and any required lifecycle are sufficiently supported;
- `finding`: direct evidence supports a confirmed problem; map it to one confirmed `F-xxx` finding;
- `validation_required`: necessity or lifecycle depends on missing evidence; map it to one tentative finding or `H-xxx` validation hypothesis and do not deduct score.

Use one primary scoring dimension when the item becomes a finding:

- state appearance, persistence, expiry, recurrence, and default variants → `state_coverage`;
- unclear interaction or false affordance → `usability` or the profile's task-flow dimension;
- misleading wording or role → `content` / `content_tone`;
- undocumented component or token → `layout_consistency`, `visual_system`, or `design_system_evolution`.

Never deduct twice for the same element.

## Example: `上新`

From a static homepage screenshot, record the visible `上新` tag as a status-like element, set lifecycle evidence to `unsupported`, and map it to a tentative finding or validation hypothesis asking for its appearance, exit, recurrence, and default-card rules. If inspected Figma/PRD later confirms that it is a permanent hard-coded sticker with no product rule, upgrade it to a confirmed finding. If a complete user-level or time-based lifecycle exists, close the lifecycle concern and review only its visible hierarchy, copy, and system consistency.
