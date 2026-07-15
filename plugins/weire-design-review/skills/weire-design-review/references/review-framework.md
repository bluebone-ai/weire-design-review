# Mobile design review framework

## Contents

- Generic and Wira scoring profiles
- Dimension review prompts
- Finding quality bar
- Score interpretation

## Profiles

### `generic-mobile-v1`

| ID | Dimension | Weight | Inspect |
|---|---|---:|---|
| `visual_hierarchy` | Visual hierarchy | 16 | focal point, primary action, grouping, density, scan order |
| `layout_consistency` | Layout and consistency | 14 | alignment, spacing, grids, components, color and type consistency |
| `usability` | Usability | 18 | task clarity, discoverability, cognitive load, error prevention, recovery |
| `content` | Information and copy | 10 | labels, comprehension, information order, tone, error and empty-state copy |
| `accessibility` | Accessibility | 14 | contrast, text legibility, touch targets, color dependence, visible focus risks |
| `platform_conventions` | Platform conventions | 8 | navigation, system areas, gestures, back behavior, native expectations |
| `state_coverage` | State coverage | 10 | loading, empty, error, disabled, success, permission and edge states |
| `interaction_motion` | Interaction and motion | 10 | feedback, continuity, transition meaning, timing, reduced-motion risks |

### `wira-v1`

| ID | Dimension | Weight | Inspect |
|---|---|---:|---|
| `brand_alignment` | Brand alignment | 14 | confirmed positive/negative traits, product category signal, emotional tone |
| `task_flow_clarity` | Task and flow clarity | 16 | primary task, room discovery, entry comprehension, first interaction, revisit |
| `visual_system` | Visual system | 14 | four-layer color roles, tokens, components, type, spacing, radius, icon and elevation |
| `social_connection` | Social connection | 14 | liveness, people-first signals, participation pressure, safety and belonging |
| `usability` | Usability | 14 | discoverability, predictability, cognitive load, prevention and recovery |
| `content_tone` | Information and tone | 8 | labels, hierarchy, copy clarity, friendliness, non-suggestive framing |
| `accessibility` | Accessibility | 8 | contrast, text, touch targets, color dependence and visible focus risks |
| `state_coverage` | State coverage | 6 | loading, empty, error, disabled, success, permission and first-time states |
| `interaction_motion` | Interaction and motion | 6 | feedback, liveness, continuity, restraint, reduced-motion risks |

### `wira-v2`

Use this profile for matched current-versus-new review with the supplied production recording and design system.

| ID | Dimension | Weight | Inspect |
|---|---|---:|---|
| `task_flow_delta` | Core-task delta | 16 | whether the redesign makes the intended homepage task faster and clearer than production |
| `baseline_capability` | Baseline capability retention | 8 | preserved entry points, live signals, navigation continuity, removed or hidden capabilities |
| `visual_hierarchy` | Information and visual hierarchy | 10 | first-screen priority, density, grouping, competing accents, scan order |
| `color_expression` | Color expression and category signal | 12 | cleanliness, lightness/chroma, temperature, material feel, palette balance, category association |
| `design_system_evolution` | Visual-language and design-system coherence | 10 | material, form, graphic/illustration, media, and motion language; tokens/components; intentional extensions and drift |
| `social_connection` | Social connection and participation | 14 | liveness, people-first signals, room activity, icebreakers, participation pressure |
| `brand_alignment` | Brand alignment | 8 | confirmed Wira traits, anti-traits, category promise, and emotional tone |
| `content_tone` | Information and tone | 6 | outcome labels, hierarchy, friendliness, non-suggestive framing |
| `accessibility` | Accessibility | 6 | contrast, legibility, touch targets, color dependence, focus risks |
| `state_coverage` | State coverage | 5 | first-time, loading, empty, error, disabled, success and permission states |
| `interaction_motion` | Interaction and motion | 5 | feedback, liveness, continuity, restraint and reduced motion |

Weights are normalized across applicable dimensions. Unsupported dimensions are `N/A`, not passed.

## Review prompts

### Core-task delta

- Name the specific optimization goal before judging the redesign.
- Compare matched states: time to first useful choice, number of competing entry groups, primary-action clarity, and content visible before scrolling.
- Do not call higher density an improvement unless it makes the target task clearer or faster.

### Baseline capability retention

- List production capabilities and live signals before judging visual changes.
- Mark every removed, merged, renamed, or hidden capability and whether users can still find it.
- Distinguish deliberate simplification from accidental loss; require a rationale for high-use features.

### Information and visual hierarchy

- Identify the first, second, and third visual priorities in both versions.
- Check whether area, color, motion, imagery, and copy tell the same priority story.
- Check whether the first viewport has one dominant purpose rather than several equal campaigns.
- Inspect each repeated entry independently; do not infer that every card is clear because the section hierarchy is clear.
- Check collection rules for featured, equal-grid, carousel, odd-item, and partial-visibility states.
- Scan every visible region and trace important details back to the whole-screen task; card layout is one possible target, not the default model for every scene.

### Color expression and category signal

- Follow [color-perception-audit.md](color-perception-audit.md) on every redesign or visual-direction review.
- Inspect color cleanliness, lightness/chroma separation, warm/cool balance, neutral breathing room, gradient and transparency stacking, and surface material impression.
- Identify whether orange is clear and energetic or becomes brown/gray when combined with dark purple, warm overlays, low lightness, or reduced chroma.
- Identify whether large areas of orange, red, pink, and purple create a downward, suggestive, nightlife, live-streaming, or promotion-heavy category signal.
- Use the confirmed Wira charter to score visible drift toward its anti-traits. Keep named-competitor similarity and population-level category perception as validation hypotheses until target-user testing supports them.
- Route semantic token misuse to `design_system_evolution`, text contrast to `accessibility`, and the overall visual/material impression to `color_expression` to avoid double deductions.

### Design-system alignment and evolution

- Follow [visual-language-consistency.md](visual-language-consistency.md). Judge the coherence of the visual grammar rather than requiring every element to use one treatment.
- Inspect material language, form language, graphic/illustration language, image/media language, and motion character. Treat buttons, IP, icons, balloons, and illustrations as evidence, not separate dimensions.
- Permit multiple styles only when each has a stable semantic or content role and transitions between them are intentional.
- Classify each change as `compliant`, `intentional_extension`, `undocumented_drift`, or `violation`.
- Do not penalize removal of the production home composition when the redesign goal requires it; evaluate whether replacement rules are documented and reusable.
- Deduct only for `violation` and high-impact `undocumented_drift`. Report intentional extensions as design-system update work.

### Brand alignment

- Does the screen communicate the confirmed product category within two seconds?
- Which confirmed positive traits are visible in layout, content, imagery, and interaction?
- Does any element drift toward a confirmed anti-trait?
- For `wira-v2`, load [wira-brand-standard.md](wira-brand-standard.md) and treat it as binding. For other products, keep candidate-only brand judgments tentative.

### Task and flow clarity

- What is the user's goal now, and what is the one primary action?
- What must be understood before entering a room or interacting?
- Where could unfamiliarity, embarrassment, or participation pressure stop the user?
- Across the five Wira journeys, is the next step visible and predictable?

### Visual system

- Do base, brand, content, and state colors retain separate responsibilities?
- Is only one action given the strongest brand emphasis?
- Are bright content assets allowed to stand out against a stable base layer?
- Do typography, spacing, radius, elevation, borders, icons, and motion follow the confirmed system?

### Social connection

- Does the interface show people connecting now rather than only static covers or attractive portraits?
- Are speaking, responding, presence, common interests, and room activity understandable?
- Does the design lower the cost of entering, speaking, or going on mic?
- Do gifts and promotional effects support rather than overpower human interaction?

### Usability

- Is the next step discoverable without remembering another screen?
- Are cards and controls consistent and predictable?
- Can the user prevent, understand, and recover from mistakes?

### Information and tone

- Do labels describe outcomes?
- Is critical information placed before commitment?
- Does the copy feel light and friendly without becoming childish, suggestive, or promotional?
- Does each card's graphic accurately support its title, intended function, and expected outcome rather than only setting a mood?

### Accessibility

- Measure contrast when possible; otherwise label it as a visual risk.
- Check likely text-scaling, touch-target, color-only, focus, and motion risks.
- Reserve compliance claims for implementation testing.

### State coverage

- Review only represented states unless the design scope explicitly claims flow completeness.
- Include first-time, empty, loading, permission, failure, success, and recovery states when relevant.

### Interaction and motion

- Confirm cause and effect across video frames or prototype edges.
- Use motion to explain presence, speech, response, and continuity.
- Keep gifts, neon, and promotional effects subordinate to interaction; consider reduced motion.

## Finding quality bar

Each finding must include one problem, direct evidence, user impact, an actionable recommendation, severity, confidence, status, and primary dimension. Group repeated symptoms caused by one root issue.

Do not deduct for:

- an unconfirmed brand principle;
- an unavailable state;
- an outcome that needs user testing or analytics;
- a deliberate design-system deviation with a documented rationale.

## Score interpretation

| Score | Interpretation |
|---:|---|
| 90–100 | Strong; remaining issues are mainly minor or limited in scope |
| 80–89 | Good; a few meaningful issues should be addressed |
| 70–79 | Needs revision before handoff or broad validation |
| 60–69 | High-risk experience with several major problems |
| 0–59 | Core task, comprehension, or access is seriously compromised |

The score summarizes the declared evidence set. It is not a universal rating of the designer or product. Apply the deterministic severity gates from `review_score.py`.
