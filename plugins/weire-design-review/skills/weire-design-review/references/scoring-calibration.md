# Scoring calibration

Use deterministic scoring version `2.0`. The score must be strict enough that real confirmed issues cannot disappear inside low-weight dimensions.

## Two-lens score

Calculate two independent views and use the lower one before severity caps:

1. `raw_weighted_score`: the existing weighted dimension score, used to show where quality is weak;
2. `severity_calibrated_score`: `100 - sum(global finding penalties)`, used to represent the number and seriousness of confirmed root findings.

This is not double deduction. The final pre-cap score is `min(raw_weighted_score, severity_calibrated_score)`.

## Global finding penalties

| Severity | Base total-score penalty |
|---|---:|
| `blocker` | 40 |
| `major` | 12 |
| `moderate` | 5 |
| `minor` | 1.5 |

Multiply each penalty by goal relevance:

| Goal relevance | Multiplier | Meaning |
|---|---:|---|
| `direct` | 1.25 | Directly affects the confirmed primary goal or a named guardrail |
| `supporting` | 1.0 | Affects product quality needed to support the goal |
| `limited` | 0.75 | Localized quality impact with limited relation to the current goal |

Every finding requires `severity_rationale`, `goal_relevance`, and a concrete `goal_relevance_rationale`. Use Major only for material core-task, structural, repeated-system, trust, or handoff-rework risk; use Moderate for localized hesitation, inconsistency, unnecessary effort, or likely accessibility risk. Do not mark a problem `limited` merely to preserve a high score. Findings must already be consolidated by root cause before scoring.

## Quantity and severity gates

- Any Blocker or at least two Majors: revise before development.
- Six or more confirmed Moderates: revise before development.
- One Major or three to five confirmed Moderates: modification is required before normal development.
- Normal development requires score at least 85, sufficient evidence, no Blocker or Major, and fewer than three confirmed Moderates.

Tentative findings and findings below the confidence threshold remain visible but do not affect either score.

## Interpretation

Keep `raw_weighted_score`, `severity_calibrated_score`, `severity_penalty_total`, per-finding penalty details, and `calibration_limiter` in the structured result and full audit. The designer summary shows only the final score, readiness decision, and the confirmed issues that caused it.
