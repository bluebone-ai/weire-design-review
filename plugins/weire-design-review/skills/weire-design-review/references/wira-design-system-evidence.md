# Wira production and design-system evidence

## Evidence status

- Production recording: local recording supplied during the initial evidence extraction; not bundled with this skill
- Design system: local 微热设计系统 2.0 source supplied during the initial evidence extraction; not bundled with this skill
- Extracted on: 2026-07-15
- Design-system version: `alpha`, `dark-only`
- Candidate homepage: user-supplied screenshot, confirmed as the redesign; not bundled with this skill

Treat these source descriptions as captured evidence, not timeless product truth. Reinspect the original inputs whenever they change or become available in a new review workspace.

## Production homepage baseline

The accepted 2000ms frame shows:

1. A large animated balloon scene occupies roughly the first half of the viewport.
2. Viewer avatars and the live count communicate that other people are present now.
3. Two large actions, `升气球` and `捞一个`, dominate the task choice.
4. Six equal-weight entry cards expose social games, matching, family, voice, swap, and newcomer benefits.
5. Friend recommendations begin below the activity entries.
6. A floating five-item glass tab bar provides stable global navigation.

The recording also covers party discovery, a room interior, feed, messages, chat, profile, and recommendations. It is useful as a broader baseline, but it does not show a complete first-speech or first-on-mic task.

## Candidate homepage delta visible from the screenshot

The redesign:

- compresses the balloon scene into a small live-status banner;
- removes `捞一个` from the visible first-screen action set;
- changes six equal entries into a mixed hierarchy led by `假面舞会`;
- brings a full newcomer post into the first viewport;
- adds top-level `首页 / 热气球` tabs while retaining bottom `首页`;
- keeps the dark base, orange selected state, rounded cards, real-person content, and floating bottom navigation.

These are comparison facts, not automatic quality judgments.

## Confirmed foundation rules

### Color semantics

- App background `#070713`; page background `#10101c`.
- Brand action uses `brand-600 #ff7a1a`; measured product button orange is `#ff7300`.
- Pink supports identity, honor, and emotion; red is unread/danger/failure; green is online/available/positive connection; violet is level/decoration/relationship/assets; yellow is hot/reward/progress/benefit.
- Large backgrounds should remain dark and stable; semitransparent white surfaces carry depth.
- Gradient buttons are restricted to rewards, gifts, payment, wallet, benefits, and asset gain. Normal join, send, confirm, follow, save, and continue actions use solid or relation-button treatments.

### Typography and spacing

- Chinese uses PingFang SC, English uses SF Pro, brand display uses Alimama ShuHeiTi, and numbers use Montserrat.
- Body text is at least 12px; continuous reading is at least 14px; 10px is reserved for badges and metadata.
- Spacing follows a 4px base, commonly 8px inside, 16px between groups, and 32px between sections.
- Core radii are 12px media/room, 16px panels, full pills, and 20px playful entry cards.

### Navigation and actions

- Top tabs use 20px labels, tertiary inactive text, bold white active text, and a 2px orange indicator.
- The bottom tab bar has five 32px icons, orange active state, disabled inactive state, glass surface, and safe-area spacing.
- Primary actions are solid orange. Relationship actions use 56x28 solid `加入` or outlined `聊天` variants.
- Interactive hit areas are at least 44px even when the visible icon is smaller.

### Motion, states, and accessibility

- State change 120ms, panel/input 200ms, overlay 260ms; standard easing is `cubic-bezier(.2,.8,.2,1)`.
- Reduced motion is required.
- Buttons, tabs, rows, and inputs require pressed/loading/disabled/focus/error states as applicable.
- Body and critical action text target WCAG AA. Image text requires an `overlay-400`-strength dark overlay.
- State cannot rely on color alone; combine online, unread, failure, and hot states with text, badges, or icons.

### Voice

- Copy should be short, close, and emotional without becoming oily or overpromotional.
- Buttons use verb plus object.
- Empty states state the situation and point to a first action.
- Error copy explains what happened and what to do next.

## Page-composition caveat

The current system fixes the production home composition: 395px sky, 62px balloon actions, 67px entries, and friend feed below. Treat these as baseline implementation tokens, not untouchable design principles. A homepage redesign may replace them.

Evaluate a replacement by asking:

- Does it serve the stated optimization goal better?
- Does it preserve or deliberately relocate important capabilities and live signals?
- Does it reuse foundation semantics and component behavior?
- Are new card hierarchy, gradients, navigation, and states documented as reusable system extensions?

## Visual-language governance gap

The current evidence defines many component and token rules but does not yet provide a complete cross-product grammar for material, form, graphic/illustration style, mixed media, or motion character. Treat glass versus flat buttons, IP versus icons, and balloon versus card or flat-illustration graphics as examples of this broader gap, not as three independent rules.

Until the system documents stable role boundaries, review cross-screen coherence using [visual-language-consistency.md](visual-language-consistency.md). A redesign should either reuse one grammar or explicitly define how multiple visual families map to different semantic roles.

## Candidate-specific checks for the next review

- Is removing the large live balloon scene an acceptable loss of liveness for earlier content discovery?
- What happens to `捞一个`, newcomer benefits, and the other original entry points?
- Does `假面舞会` deserve the strongest card hierarchy based on product goals or data?
- Does `首页 / 热气球` clarify navigation or create a duplicated `首页` hierarchy?
- Do bright gradients on activity cards represent content, campaign hierarchy, or undocumented decoration?
- Are secondary texts on gradients and inactive navigation compliant with actual contrast targets?
- Is the feed-first shift intended to improve greeting, room entry, retention, or another metric?

## Stakeholder color signal

A stakeholder explicitly reported that the redesign's orange feels dark, gray-contaminated, dirty, and old-fashioned, while the purple and red feel downward and suggestive, closer to adult-dating products such as 爱聊 or 心遇 than to a young social-entertainment product.

Treat this as valid stakeholder evidence that makes color perception a mandatory review area. It is not yet proof of target-user perception. Decompose it into:

- color appearance: lightness, chroma, gray contamination, transparency and background interaction;
- palette balance: the proportion and adjacency of warm orange, red, pink and purple versus clean neutral or cool breathing room;
- material impression: clear/luminous versus dusty/muddy/heavy;
- category signal: young social entertainment versus suggestive dating, nightlife live streaming, or promotion-heavy entertainment.

The first three may produce confirmed findings when visible or measurable. The confirmed Wira brand standard now makes visible drift toward `暧昧猎艳`, `夜场直播`, or `灰暗陈旧` a scoreable brand risk. Similarity to a named competitor, and the strength of that association among target users, remain hypotheses until supported by perception testing.
