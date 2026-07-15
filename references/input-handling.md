# Input handling

Choose the narrowest workflow that preserves reliable evidence.

## Context pack and version labels

Before inspecting a redesign, separate inputs into:

- `baseline`: current production UI or existing flow;
- `design_system`: confirmed tokens, components, patterns, and guidelines;
- `candidate`: the new design under review;
- `behavioral_evidence`: prototype tests, analytics, or research.

Do not mix baseline and candidate screenshots without labels. Match the same viewport, task state, content type, and platform whenever possible. A missing baseline lowers comparison confidence but does not block a standalone artifact review.

## Screenshot or exported image

1. Locate the original file. Do not analyze a thumbnail when the original is available.
2. Inspect the image at sufficient detail and record its pixel dimensions.
3. Reject blank, loading, severely cropped, or unrelated images.
4. Assign a stable screen ID and preserve the original file.
5. If several screenshots form a flow, order them from the user's task rather than filename alone.
6. Cite regions as `[x, y, width, height]` only when coordinates can be established reliably. Otherwise describe the location in plain language.

Default unsupported areas: motion, transition timing, focus order, screen-reader semantics, runtime keyboard behavior, device adaptation, and unshown states.

## Screen recording or video

1. Inspect metadata and duration before extracting frames.
2. Prefer meaningful state changes over uniform sampling. Use scene changes plus additional frames around taps, transitions, errors, loading, and confirmations.
3. Preserve timestamps in milliseconds for every accepted frame.
4. Inspect adjacent frames before judging animation direction, latency, or continuity.
5. Do not infer a complete flow from interactions that are not present in the recording.

When local command-line tools are available, use `ffprobe` for metadata and `ffmpeg` for frame extraction. Save accepted frames with ordered names such as `01-0000ms-start.png`.

## Figma link

1. Load and follow the available Figma-use skill before invoking any Figma tool.
2. Resolve the file and node IDs from the link.
3. Inspect only the requested page, frames, components, variables, and prototype edges needed by the review.
4. Export or capture visible frames and inspect those images before citing them.
5. Preserve node IDs in evidence records.
6. If access or tooling is unavailable, ask for exported frames or screenshots. Do not claim to have inspected inaccessible nodes.

Inspect component variants, spacing, text styles, color variables, reuse, and prototype links only when the tool returns those properties. Treat hidden or missing properties as unknown.

## Mixed sources and version comparison

- Normalize all sources into ordered screens, states, and transitions.
- Identify which source supports each dimension.
- For version comparison, match screens by stable names, node IDs, or task position. Report `resolved`, `remaining`, `new`, and `changed` findings.
- Recalculate both versions with the same applicable dimensions and weights. If the evidence scope changes, explain why the scores are not directly comparable.
- Treat design-system deviations as findings only after checking whether the new pattern is deliberate and documented.
