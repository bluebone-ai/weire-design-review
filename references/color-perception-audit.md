# Color perception and category audit

Use this pass proactively for every visual redesign, palette decision, brand-direction review, or complaint using words such as `脏`, `灰`, `土`, `闷`, `下沉`, `暧昧`, `廉价`, or `不年轻`.

## Evidence levels

1. `measured`: exact token, sampled value, opacity, contrast, or OKLCH/Lab relationship is available.
2. `visually_estimated`: the screenshot visibly suggests a mechanism but exact values are unavailable.
3. `association_hypothesis`: the judgment depends on cultural or category perception and needs brand or user evidence.

State the evidence level in every color finding.

## Mandatory checks

### 1. Accent cleanliness

- Check whether the brand accent remains distinct from the base surface.
- Look for low lightness, reduced chroma, gray or black overlays, semitransparent stacking, warm-purple adjacency, and compression that can turn orange toward brown or dust.
- Do not call a color dirty without naming the visible or measured mechanism.

### 2. Palette temperature and depth

- Estimate how much of the first viewport is occupied by warm orange, red, pink, purple, cool hues, and neutral surfaces.
- Check whether several warm hues cluster at similar middle or low lightness, making the screen feel heavy or downward.
- Check whether neutral and cool areas provide enough separation for vivid content.

### 3. Material impression

- Check whether gradients and translucent overlays feel luminous and intentional or muddy and layered.
- Inspect whether surfaces share too many brown, dusty-purple, or low-contrast midtones.
- Check whether glow, shadow, blur, and texture reinforce clarity or simulate a smoky/nightlife atmosphere.

### 4. Semantic color roles

- Verify that brand, content, state, reward, danger, and online colors retain separate jobs.
- Route confirmed token or role violations to the design-system dimension.
- Do not deduct twice for the same root color misuse.

### 5. Category and age signal

- Ask which product category the palette suggests before reading detailed copy.
- Check for cues commonly associated with youth social entertainment, dating, live streaming, nightlife, gaming, or promotion-heavy products.
- Phrase the result as a risk, not a universal fact, unless supported by confirmed brand criteria or target-user research.

### 6. Accessibility and device resilience

- Measure text/background contrast when possible.
- Check the palette at lower brightness, common device gamut, and over photographs or gradients.
- Route contrast findings to accessibility rather than duplicating them under color expression.

## Finding format

Use:

`<observable mechanism> creates <perceptual effect>, which risks <brand/category/user consequence>. Evidence level: <level>.`

Example:

`The orange cards sit at similar middle lightness to the warm purple base and are softened by dark overlays, shifting the accent toward brown-gray rather than clear orange. This risks a dusty, older material impression instead of a lively youth signal. Evidence level: visually_estimated.`

## Validation method

When category perception matters, keep content and layout fixed and test palette variants only. Ask target users within two to five seconds:

- What kind of product is this?
- Which three adjectives fit it?
- Does it feel young, clean, lively, safe, suggestive, nightlife-like, live-streaming-like, or promotion-heavy?

Compare adjective distribution and category answers. Use behavioral metrics only after the perception direction is understood.
