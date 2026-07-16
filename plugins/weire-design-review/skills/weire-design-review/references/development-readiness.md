# Development readiness gate

Use the deterministic `scores.development_readiness` output to tell the reader whether the reviewed design is ready to enter development. Do not replace it with a subjective recommendation.

## Decision rules

| Result | Rule | Development guidance |
|---|---|---|
| `ready_for_development` | Score `≥85`, score confidence `≥0.65`, no scored Blocker or Major, and fewer than 3 scored Moderates | The design may enter normal design handoff and development |
| `conditional_handoff` | Score `70–84`, exactly one scored Major, or 3–5 scored Moderates, with no stronger gate | Complete the priority improvements and confirm the adjusted design before full development; technical research or low-rework work may proceed in parallel |
| `revise_before_development` | Score `<70`, any scored Blocker, at least two scored Majors, or at least 6 scored Moderates | Do not enter normal development; run one design revision and re-review first |
| `insufficient_evidence` | Score confidence `<0.65` and no stronger revision gate applies | Add missing flow, state, prototype, implementation, or measurement evidence before making a development decision |

Only confirmed findings whose confidence meets the scorer threshold count toward severity and quantity gates. Tentative findings remain visible as validation work but do not block development by themselves. Read [scoring-calibration.md](scoring-calibration.md) for the global penalty and goal-relevance formula.

## Reporting contract

Render the gate prominently inside `整体印象` using the scored JSON fields. All visible labels and explanations must be Simplified Chinese only:

```markdown
### 开发准入

**结论：** 暂不建议进入开发

- **依据：** 总分 68.0，低于 70 分调整线；存在 1 个阻断问题
- **正常开发线：** 85 分
- **下一步：** 先完成一轮设计调整，关闭阻断或重大问题后重新评审
```

Translate stable reason codes into plain evidence-based language. Cite the related finding IDs for severity-based reasons. Never say only “the score is low”; state the threshold, severity override, evidence confidence, and action that produced the decision.

This is a design-readiness gate. It does not certify technical feasibility, requirement completeness, implementation cost, analytics instrumentation, QA readiness, or final release approval. A `ready_for_development` result still requires normal design handoff, engineering review, and acceptance criteria.
