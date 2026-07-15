#!/usr/bin/env python3
"""Validate and deterministically score a weire-design-review JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROFILES = {
    "generic-mobile-v1": {
        "visual_hierarchy": 16,
        "layout_consistency": 14,
        "usability": 18,
        "content": 10,
        "accessibility": 14,
        "platform_conventions": 8,
        "state_coverage": 10,
        "interaction_motion": 10,
    },
    "wira-v1": {
        "brand_alignment": 14,
        "task_flow_clarity": 16,
        "visual_system": 14,
        "social_connection": 14,
        "usability": 14,
        "content_tone": 8,
        "accessibility": 8,
        "state_coverage": 6,
        "interaction_motion": 6,
    },
    "wira-v2": {
        "task_flow_delta": 16,
        "baseline_capability": 8,
        "visual_hierarchy": 10,
        "color_expression": 12,
        "design_system_evolution": 10,
        "social_connection": 14,
        "brand_alignment": 8,
        "content_tone": 6,
        "accessibility": 6,
        "state_coverage": 5,
        "interaction_motion": 5,
    },
}

DEDUCTIONS = {"blocker": 100, "major": 40, "moderate": 15, "minor": 5}
STATUSES = {"confirmed", "tentative"}
SOURCE_TYPES = {"screenshot", "video", "figma", "mixed"}
REVIEW_MODES = {"artifact", "redesign-comparison", "flow-audit", "direction-comparison"}
DELTA_VALUES = {"better", "same", "worse", "unknown"}
EVIDENCE_LEVELS = {"measured", "visually_estimated", "association_hypothesis"}
MIN_SCORING_CONFIDENCE = 0.65
REDESIGN_GOAL_STATUSES = {"missing", "inferred", "confirmed"}
OBJECTIVE_TYPES = {"behavior", "interaction", "visual-language", "systemization"}
CAPABILITY_PASS_STATUSES = {"used", "skipped", "unavailable"}
CAPABILITY_PASS_PURPOSES = {
    "evidence_capture",
    "candidate_findings",
    "specialist_review",
    "validation_plan",
    "research_synthesis",
    "ideation",
    "handoff",
    "implementation_qa",
}


class ReviewValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewValidationError(message)


def validate_text(value: Any, path: str) -> None:
    require(isinstance(value, str) and value.strip() != "", f"{path} must be non-empty text")


def validate_text_list(value: Any, path: str, *, allow_empty: bool = True) -> None:
    require(isinstance(value, list), f"{path} must be an array")
    require(allow_empty or len(value) > 0, f"{path} must not be empty")
    for index, item in enumerate(value):
        validate_text(item, f"{path}[{index}]")


def get_profile(review: dict[str, Any]) -> tuple[str, dict[str, int]]:
    profile_name = review.get("profile", "generic-mobile-v1")
    require(profile_name in PROFILES, f"review.profile must be one of {sorted(PROFILES)}")
    return profile_name, PROFILES[profile_name]


def validate_review(data: Any) -> dict[str, Any]:
    require(isinstance(data, dict), "root must be an object")

    review = data.get("review")
    require(isinstance(review, dict), "review must be an object")
    for field in ("title", "source_type", "platform", "core_task"):
        validate_text(review.get(field), f"review.{field}")
    require(review["source_type"] in SOURCE_TYPES, f"review.source_type must be one of {sorted(SOURCE_TYPES)}")
    profile_name, weights = get_profile(review)
    mode = review.get("mode", "artifact")
    require(mode in REVIEW_MODES, f"review.mode must be one of {sorted(REVIEW_MODES)}")
    assumptions = review.get("assumptions", [])
    require(isinstance(assumptions, list), "review.assumptions must be an array")

    context = data.get("context", {})
    require(isinstance(context, dict), "context must be an object when present")
    if "brand_charter_status" in context:
        require(context["brand_charter_status"] in {"missing", "candidate", "confirmed"}, "context.brand_charter_status is invalid")
    if profile_name == "wira-v2" and mode == "redesign-comparison":
        goal_status = context.get("redesign_goal_status")
        require(goal_status in REDESIGN_GOAL_STATUSES, "context.redesign_goal_status is required and must be missing, inferred, or confirmed")
        if goal_status in {"inferred", "confirmed"}:
            goal = context.get("redesign_goal")
            require(isinstance(goal, dict), "context.redesign_goal must be an object when redesign_goal_status is inferred or confirmed")
            require(goal.get("objective_type") in OBJECTIVE_TYPES, f"context.redesign_goal.objective_type must be one of {sorted(OBJECTIVE_TYPES)}")
            for field in ("primary_objective", "primary_metric", "primary_changed_variable"):
                validate_text(goal.get(field), f"context.redesign_goal.{field}")
            for field in ("guardrail_metrics", "held_constant"):
                require(isinstance(goal.get(field, []), list), f"context.redesign_goal.{field} must be an array")

    capability_passes = data.get("capability_passes", [])
    require(isinstance(capability_passes, list), "capability_passes must be an array")
    pass_statuses: dict[str, str] = {}
    for index, capability_pass in enumerate(capability_passes):
        prefix = f"capability_passes[{index}]"
        require(isinstance(capability_pass, dict), f"{prefix} must be an object")
        pass_id = capability_pass.get("id")
        validate_text(pass_id, f"{prefix}.id")
        require(pass_id != "core", f"{prefix}.id uses reserved value core")
        require(pass_id not in pass_statuses, f"duplicate capability pass id: {pass_id}")
        for field in ("provider", "capability"):
            validate_text(capability_pass.get(field), f"{prefix}.{field}")
        status = capability_pass.get("status")
        require(status in CAPABILITY_PASS_STATUSES, f"{prefix}.status is invalid")
        pass_statuses[pass_id] = status
        purposes = capability_pass.get("purposes")
        validate_text_list(purposes, f"{prefix}.purposes", allow_empty=False)
        require(len(purposes) == len(set(purposes)), f"{prefix}.purposes must not contain duplicates")
        require(set(purposes) <= CAPABILITY_PASS_PURPOSES, f"{prefix}.purposes contains an invalid value")
        validate_text_list(capability_pass.get("input_sources", []), f"{prefix}.input_sources")
        validate_text_list(capability_pass.get("limitations", []), f"{prefix}.limitations")

    def validate_source_pass_ids(value: Any, path: str) -> None:
        validate_text_list(value, path, allow_empty=False)
        require(len(value) == len(set(value)), f"{path} must not contain duplicates")
        for source_id in value:
            require(source_id == "core" or source_id in pass_statuses, f"{path} references unknown pass {source_id}")
            if source_id != "core":
                require(pass_statuses[source_id] == "used", f"{path} references non-used pass {source_id}")

    scope = data.get("scope")
    require(isinstance(scope, dict), "scope must be an object")
    dimensions = scope.get("dimensions")
    require(isinstance(dimensions, dict), "scope.dimensions must be an object")
    require(set(dimensions) == set(weights), f"scope.dimensions must contain exactly the dimensions for {profile_name}")
    for dimension, settings in dimensions.items():
        require(isinstance(settings, dict), f"scope.dimensions.{dimension} must be an object")
        applicable = settings.get("applicable")
        confidence = settings.get("evidence_confidence")
        require(isinstance(applicable, bool), f"scope.dimensions.{dimension}.applicable must be boolean")
        require(isinstance(confidence, (int, float)) and not isinstance(confidence, bool), f"scope.dimensions.{dimension}.evidence_confidence must be numeric")
        require(0 <= confidence <= 1, f"scope.dimensions.{dimension}.evidence_confidence must be between 0 and 1")
        require(applicable or confidence == 0, f"scope.dimensions.{dimension}.evidence_confidence must be 0 when not applicable")
    require(any(settings["applicable"] for settings in dimensions.values()), "at least one dimension must be applicable")
    require(isinstance(scope.get("limitations", []), list), "scope.limitations must be an array")
    if profile_name == "wira-v2" and mode == "redesign-comparison":
        goal_confirmed = context["redesign_goal_status"] == "confirmed"
        require(dimensions["task_flow_delta"]["applicable"] == goal_confirmed, "task_flow_delta must be applicable only when redesign_goal_status is confirmed")

    strengths = data.get("strengths", [])
    require(isinstance(strengths, list), "strengths must be an array")
    for index, strength in enumerate(strengths):
        prefix = f"strengths[{index}]"
        require(isinstance(strength, dict), f"{prefix} must be an object")
        require(strength.get("dimension") in weights, f"{prefix}.dimension is invalid for {profile_name}")
        validate_text(strength.get("statement"), f"{prefix}.statement")
        require(isinstance(strength.get("evidence"), dict), f"{prefix}.evidence must be an object")
        if "delta" in strength:
            require(strength["delta"] in DELTA_VALUES, f"{prefix}.delta is invalid")
        if "source_pass_ids" in strength:
            validate_source_pass_ids(strength["source_pass_ids"], f"{prefix}.source_pass_ids")

    findings = data.get("findings")
    require(isinstance(findings, list), "findings must be an array")
    seen_ids: set[str] = set()
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        require(isinstance(finding, dict), f"{prefix} must be an object")
        finding_id = finding.get("id")
        validate_text(finding_id, f"{prefix}.id")
        require(finding_id not in seen_ids, f"duplicate finding id: {finding_id}")
        seen_ids.add(finding_id)
        dimension = finding.get("dimension")
        require(dimension in weights, f"{prefix}.dimension is invalid for {profile_name}")
        require(dimensions[dimension]["applicable"], f"{prefix} uses non-applicable dimension {dimension}")
        require(finding.get("severity") in DEDUCTIONS, f"{prefix}.severity is invalid")
        require(finding.get("status") in STATUSES, f"{prefix}.status is invalid")
        require(finding.get("check_type") in {"rule", "semantic", "contextual"}, f"{prefix}.check_type is invalid")
        confidence = finding.get("confidence")
        require(isinstance(confidence, (int, float)) and not isinstance(confidence, bool), f"{prefix}.confidence must be numeric")
        require(0 <= confidence <= 1, f"{prefix}.confidence must be between 0 and 1")
        for field in ("title", "impact", "recommendation"):
            validate_text(finding.get(field), f"{prefix}.{field}")
        evidence = finding.get("evidence")
        require(isinstance(evidence, dict), f"{prefix}.evidence must be an object")
        validate_text(evidence.get("screen_id"), f"{prefix}.evidence.screen_id")
        validate_text(evidence.get("description"), f"{prefix}.evidence.description")
        if "region" in evidence:
            region = evidence["region"]
            require(isinstance(region, list) and len(region) == 4, f"{prefix}.evidence.region must have four values")
            require(all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in region), f"{prefix}.evidence.region values must be numeric")
        if "delta" in finding:
            require(finding["delta"] in DELTA_VALUES, f"{prefix}.delta is invalid")
        if "evidence_level" in finding:
            require(finding["evidence_level"] in EVIDENCE_LEVELS, f"{prefix}.evidence_level is invalid")
        if "source_pass_ids" in finding:
            validate_source_pass_ids(finding["source_pass_ids"], f"{prefix}.source_pass_ids")

    hypotheses = data.get("validation_hypotheses", [])
    require(isinstance(hypotheses, list), "validation_hypotheses must be an array")
    for index, hypothesis in enumerate(hypotheses):
        prefix = f"validation_hypotheses[{index}]"
        require(isinstance(hypothesis, dict), f"{prefix} must be an object")
        for field in ("id", "hypothesis", "primary_metric"):
            validate_text(hypothesis.get(field), f"{prefix}.{field}")
        require(isinstance(hypothesis.get("guardrails", []), list), f"{prefix}.guardrails must be an array")

    return data


def score_review(data: dict[str, Any]) -> dict[str, Any]:
    profile_name, weights = get_profile(data["review"])
    dimensions = data["scope"]["dimensions"]
    findings = data["findings"]
    dimension_scores: dict[str, dict[str, Any]] = {}

    for dimension, weight in weights.items():
        settings = dimensions[dimension]
        if not settings["applicable"]:
            dimension_scores[dimension] = {
                "applicable": False,
                "score": None,
                "weight": weight,
                "confirmed_findings": 0,
            }
            continue

        scored_findings = [
            finding
            for finding in findings
            if finding["dimension"] == dimension
            and finding["status"] == "confirmed"
            and finding["confidence"] >= MIN_SCORING_CONFIDENCE
        ]
        deduction = sum(DEDUCTIONS[finding["severity"]] for finding in scored_findings)
        dimension_scores[dimension] = {
            "applicable": True,
            "score": max(0, 100 - deduction),
            "weight": weight,
            "confirmed_findings": len(scored_findings),
        }

    applicable = [dimension for dimension in weights if dimensions[dimension]["applicable"]]
    total_weight = sum(weights[dimension] for dimension in applicable)
    raw_overall = sum(
        dimension_scores[dimension]["score"] * weights[dimension]
        for dimension in applicable
    ) / total_weight
    scored_findings = [
        finding
        for finding in findings
        if finding["status"] == "confirmed"
        and finding["confidence"] >= MIN_SCORING_CONFIDENCE
    ]
    blocker_count = sum(finding["severity"] == "blocker" for finding in scored_findings)
    major_count = sum(finding["severity"] == "major" for finding in scored_findings)
    if blocker_count:
        overall = min(raw_overall, 59)
    elif major_count >= 2:
        overall = min(raw_overall, 79)
    elif major_count == 1:
        overall = min(raw_overall, 89)
    else:
        overall = raw_overall
    score_confidence = sum(
        dimensions[dimension]["evidence_confidence"] * weights[dimension]
        for dimension in applicable
    ) / total_weight

    return {
        "overall_score": round(overall, 1),
        "raw_weighted_score": round(raw_overall, 1),
        "score_confidence": round(score_confidence, 2),
        "dimension_scores": dimension_scores,
        "scoring_profile": profile_name,
        "scoring_version": "1.3",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_json", type=Path, help="Path to review JSON")
    parser.add_argument("--write", action="store_true", help="Write scores back into the input file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = json.loads(args.review_json.read_text(encoding="utf-8"))
        validated = validate_review(data)
        validated["scores"] = score_review(validated)
    except (OSError, json.JSONDecodeError, ReviewValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(validated, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        args.review_json.write_text(output, encoding="utf-8")
        print(f"Scored review written to {args.review_json}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
