# Design goal intake gate

Run this gate before inspecting design quality, invoking a specialist, creating findings, or scoring.

## Trigger

Pause intake when the user supplies a screenshot, video, or Figma link without a confirmed design goal. Apply the same gate when several artifacts are supplied but their intended outcome is unclear.

Do not ask again when the same message already states both:

- the primary behavior, experience, brand, or quality outcome the design should achieve;
- at least one metric or observable criterion that would count as success.

## Required question

Ask one concise compound question:

> 在开始评审前，请先确认本次设计的唯一核心目标：你希望它让用户行为、使用体验或品牌感受发生什么变化？什么指标或可观察结果代表成功？

Do not include design findings, preliminary scores, specialist output, or aesthetic judgments in this intake response. You may only confirm that the artifact was received and identify its source type.

## Clarification rules

Do not accept `帮我看看`, `优化一下`, `更好看`, `更年轻`, or similar direction-only phrases as a complete goal. Ask a follow-up that turns the direction into an observable outcome.

Accept one of these goal types:

- `behavior`: a target action and metric, such as increasing a gameplay-entry click-through rate;
- `experience_or_brand`: a target perception or comprehension outcome plus an observable test, such as two-second category recognition or a reduction in dating-category association;
- `general_quality`: an explicit request for a general quality audit, using score `>= 85` and no blocker or major finding as the default success criteria.

Metrics are preferred but not mandatory for experience or brand goals. A concrete prototype task, perception test, comprehension check, or design-quality gate is acceptable.

If the user declines to choose a product goal, offer `general_quality` and ask them to confirm it. Never silently assign that fallback.

## Goal contract

After the user answers, restate a compact contract before continuing:

```text
评审目标：{primary_goal}
成功标准：{success_criteria}
```

Store it in the final review JSON:

```json
{
  "context": {
    "design_goal_status": "confirmed",
    "design_goal": {
      "goal_type": "behavior",
      "primary_goal": "提升假面舞会入口点击率",
      "success_criteria": ["入口点击率提升", "其他玩法总点击率不下降"],
      "source": "user_declared"
    }
  }
}
```

Allowed `source` values:

- `user_declared`: the user supplied a complete goal without prompting;
- `user_confirmed`: the user confirmed or completed the goal after the intake question.

Never use inferred model context as the source of a confirmed goal. For redesign comparisons, keep the existing `redesign_goal` fields aligned with this universal goal contract.

## Hard stop

Until the goal contract is confirmed:

- do not inspect the artifact for design quality beyond checking that it exists and is readable;
- do not invoke Product Design, Claude Design, accessibility, design-system, or other specialist passes;
- do not create findings, recommendations, scores, or development-readiness decisions;
- do not write a completed review JSON or report.
