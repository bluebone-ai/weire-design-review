# Multi-scale design audit

Review every artifact from the whole experience down to visible details. Card layout is only one example. Apply this method to navigation, feeds, forms, room screens, chat, media, lists, dialogs, settings, profiles, search, permissions, system feedback, and any other mobile surface.

## Six audit levels

1. **Flow:** entry, goal, sequence, continuity, exit, recovery, and outcome.
2. **Screen:** purpose, first impression, primary action, hierarchy, brand, and task fit.
3. **Region:** header, navigation, hero, content group, input area, action area, footer, overlay, or other functional zone.
4. **Component:** button, card, row, field, tab, avatar, media, badge, menu, sheet, control, or repeated pattern.
5. **Element and property:** label, icon, image, graphic, copy, color, typography, spacing, alignment, radius, border, shadow, and affordance.
6. **State and boundary:** quantity, long content, localization, loading, empty, error, disabled, selected, pressed, focus, permission, offline, keyboard, safe area, scaling, motion, and device adaptation.

## Coverage contract

- List every visible region in a `Screen / Section Coverage` table, including regions with no confirmed problem. This proves the screen was scanned rather than sampled selectively.
- Inspect every visible component. Give individual rows to core-task, repeated, novel, inconsistent, or risky components; group low-risk standard components when individual rows would add no decision value.
- Trace every confirmed or tentative issue to the smallest useful target: screen, region, component, element, property, or state.
- Preserve the whole-screen consequence after identifying the detail. Do not report spacing, copy, or icon issues without explaining why they matter to the task or brand.
- Prioritize depth by core-task relevance, blocker/major risk, accessibility, design-system reuse, and then polish. Complete coverage does not require a verbose note for every harmless pixel.
- Treat unshown interactions or states as unknown coverage, not as confirmed failures. Name the screenshot, prototype, implementation, or data needed to inspect them.

## Component and element checks

Run the structured ledger in [element-accountability-audit.md](element-accountability-audit.md) before summarizing component findings. The coverage table proves that regions were scanned; the ledger proves that semantically loaded micro-elements were not skipped.

For important components, record:

- stable ID or visible label;
- intended function or missing definition;
- hierarchy and location;
- copy and information clarity;
- graphic, icon, or image semantic fit;
- action and gesture affordance;
- material, form, and style consistency;
- accessibility and content resilience;
- represented and missing states;
- related finding IDs.

Classify graphic or icon semantic fit as:

- `direct`: identifies the function or outcome with little interpretation;
- `supportive`: reinforces the label or mood but needs copy;
- `ambiguous`: supports several functions or mainly decorates;
- `conflicting`: suggests a different function, audience, or brand promise.

If the real function is unavailable, keep exact semantic fit tentative.

## Structure, collection, and content boundaries

Choose checks that match the component rather than forcing every scene into a card-grid model:

- **Collections:** `0/1/2/3/4+` items, ordering, odd items, pagination, overflow, snap, truncation, virtualization, loading, empty, and failure.
- **Forms:** empty, filled, focus, keyboard, validation, error, disabled, submitting, success, autofill, long labels, and permission denial.
- **Navigation:** selected, unselected, back, deep link, hierarchy, overflow, badge, safe area, and state restoration.
- **Live rooms and media:** presence, speaking, muted, reconnecting, ended, buffering, permission, moderation, and first participation.
- **Chat and feeds:** short/long content, image/video, sending, failed, unread, deleted, blocked, pagination, refresh, empty, and keyboard overlap.
- **Dialogs and overlays:** trigger, focus, dismissal, destructive confirmation, keyboard, stacked overlays, and interrupted state.

For dynamic equal-card collections, useful defaults are:

- `1`: keep normal width and reading-start alignment unless promotion is intentional;
- `2`: show both completely;
- `3`: show three completely when width supports it;
- `4+`: use an explicit grid or carousel; a next-item peek must be deliberate and the final item must become fully visible;
- odd item in two columns: keep normal width and start alignment, or use a documented featured variant rather than automatic stretching.

A featured `1 + 2` composition is valid when priority is intentional. Define its behavior when a secondary item is missing or added.

## Output requirements

Before detailed finding cards, render:

1. `Screen / Section Coverage` for every visible region;
2. `Component / Element Audit` for core, repeated, novel, inconsistent, and risky components;
3. `Element Accountability Ledger` for semantic badges, tags, counters, indicators, prompts, icons, graphics, and microcopy;
4. `State / Edge-case Audit` using the relevant scene family above.

Convert supported details into normal finding cards. Keep missing states tentative and non-scoring unless the supplied design claims complete coverage.
