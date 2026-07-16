#!/usr/bin/env python3
"""Validate and deterministically score a weire-design-review JSON file."""

from __future__ import annotations

import argparse
import json
import re
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
GLOBAL_SEVERITY_PENALTIES = {"blocker": 40, "major": 12, "moderate": 5, "minor": 1.5}
GOAL_RELEVANCE_MULTIPLIERS = {"direct": 1.25, "supporting": 1.0, "limited": 0.75}
CONDITIONAL_MODERATE_COUNT = 3
REVISION_MODERATE_COUNT = 6
STATUSES = {"confirmed", "tentative"}
SOURCE_TYPES = {"screenshot", "video", "figma", "mixed"}
REVIEW_MODES = {"artifact", "redesign-comparison", "flow-audit", "direction-comparison"}
OUTPUT_MODES = {"designer_summary", "audit_full"}
OUTPUT_LANGUAGE = "zh-CN"
EXECUTION_HOSTS = {"codex", "claude", "other"}
REVIEW_ENGINES = {
    "codex": "wira-core+codex-product-design",
    "claude": "wira-core+claude-design",
}
DELTA_VALUES = {"better", "same", "worse", "unknown"}
EVIDENCE_LEVELS = {"measured", "visually_estimated", "association_hypothesis"}
MIN_SCORING_CONFIDENCE = 0.65
DEVELOPMENT_READY_SCORE = 85
DEVELOPMENT_REVISION_SCORE = 70
DEVELOPMENT_MIN_CONFIDENCE = 0.65
REDESIGN_GOAL_STATUSES = {"missing", "inferred", "confirmed"}
OBJECTIVE_TYPES = {"behavior", "interaction", "visual-language", "systemization"}
DESIGN_GOAL_TYPES = {"behavior", "experience_or_brand", "general_quality"}
DESIGN_GOAL_SOURCES = {"user_declared", "user_confirmed"}
CAPABILITY_PASS_STATUSES = {"used", "skipped", "unavailable"}
CAPABILITY_INVOCATIONS = {"required", "explicit", "automatic"}
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
CAPABILITY_INPUT_KINDS = {
    "static_screenshot",
    "video",
    "figma",
    "live_flow",
    "design_system",
    "research_data",
    "implementation",
    "other",
}
SPECIALIST_DISPOSITIONS = {"adopted", "retained_for_validation", "not_adopted"}
SPECIALIST_TARGET_TYPES = {"finding", "strength", "validation_hypothesis"}
REQUIRED_BASELINE_PASSES = {
    ("codex-product-design", "audit"): "codex",
    ("claude-design", "design-critique"): "claude",
}
NATIVE_COVERAGE_STATUSES = {"full", "partial", "missing", "unsupported"}
FINAL_COVERAGE_STATUSES = {"full", "partial", "unsupported"}
COMPLEMENT_STATUSES = {"not_needed", "used", "not_applicable"}
ADAPTIVE_COMPLEMENT_PASS = ("wira-core", "adaptive-dimension-complement")
NATIVE_EXECUTION_MODES = {"isolated_subagent", "sealed_sequential"}
NATIVE_CONTEXT_SCOPE = "artifact_product_audience_stage_only"
NATIVE_FRAMEWORK_SECTIONS = {
    "first_impression",
    "usability",
    "visual_hierarchy",
    "consistency",
    "accessibility",
}
NATIVE_FRAMEWORK_STATUSES = {
    "finding",
    "strength",
    "mixed",
    "no_material_issue",
    "unsupported",
}
NATIVE_CANDIDATE_KINDS = {"finding", "strength", "validation_hypothesis"}
ELEMENT_SCAN_CATEGORIES = {
    "badge_tag",
    "counter_timer",
    "status_indicator",
    "pagination_indicator",
    "transient_prompt",
    "icon_graphic",
    "microcopy",
}
ELEMENT_TYPES = ELEMENT_SCAN_CATEGORIES | {"other"}
ELEMENT_SEMANTIC_ROLES = {
    "status",
    "promotion",
    "action",
    "navigation",
    "feedback",
    "content",
    "decoration",
    "unknown",
}
ELEMENT_NECESSITY_VALUES = {"necessary", "supportive", "redundant", "unknown"}
ELEMENT_DELETION_RESULTS = {"essential", "supportive", "no_material_loss", "unknown"}
ELEMENT_NECESSITY_TO_DELETION = {
    "necessary": "essential",
    "supportive": "supportive",
    "redundant": "no_material_loss",
    "unknown": "unknown",
}
ELEMENT_LIFECYCLE_REQUIREMENTS = {"required", "not_required", "unknown"}
ELEMENT_LIFECYCLE_EVIDENCE = {"complete", "partial", "missing", "unsupported", "not_applicable"}
ELEMENT_LIFECYCLE_FIELDS = (
    "appearance_trigger",
    "update_rule",
    "exit_rule",
    "recurrence_rule",
    "default_state",
)
ELEMENT_ASSESSMENTS = {"no_issue", "finding", "validation_required"}
ELEMENT_ISSUE_BASES = {"none", "necessity", "lifecycle", "semantics", "affordance", "system_consistency"}
ELEMENT_EVIDENCE_BASES = {
    "visible_static",
    "video",
    "figma",
    "prd",
    "design_system",
    "implementation",
    "analytics",
}
STRONG_LIFECYCLE_EVIDENCE = {"video", "figma", "prd", "design_system", "implementation"}
ELEMENT_TARGET_TYPES = {"finding", "validation_hypothesis"}


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
    output_mode = review.get("output_mode")
    require(output_mode in OUTPUT_MODES, f"review.output_mode must be one of {sorted(OUTPUT_MODES)}")
    require(
        review.get("output_language") == OUTPUT_LANGUAGE,
        f"review.output_language must be {OUTPUT_LANGUAGE}",
    )
    execution_host = review.get("execution_host")
    require(execution_host in EXECUTION_HOSTS, f"review.execution_host must be one of {sorted(EXECUTION_HOSTS)}")
    if execution_host in REVIEW_ENGINES:
        require(
            review.get("review_engine") == REVIEW_ENGINES[execution_host],
            f"review.review_engine must be {REVIEW_ENGINES[execution_host]} for {execution_host}",
        )
    assumptions = review.get("assumptions", [])
    require(isinstance(assumptions, list), "review.assumptions must be an array")

    context = data.get("context", {})
    require(isinstance(context, dict), "context must be an object when present")
    require(context.get("design_goal_status") == "confirmed", "context.design_goal_status must be confirmed before scoring")
    design_goal = context.get("design_goal")
    require(isinstance(design_goal, dict), "context.design_goal must be an object")
    require(
        design_goal.get("goal_type") in DESIGN_GOAL_TYPES,
        f"context.design_goal.goal_type must be one of {sorted(DESIGN_GOAL_TYPES)}",
    )
    validate_text(design_goal.get("primary_goal"), "context.design_goal.primary_goal")
    validate_text_list(
        design_goal.get("success_criteria"),
        "context.design_goal.success_criteria",
        allow_empty=False,
    )
    require(
        design_goal.get("source") in DESIGN_GOAL_SOURCES,
        f"context.design_goal.source must be one of {sorted(DESIGN_GOAL_SOURCES)}",
    )
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

    capability_passes = data.get("capability_passes")
    require(isinstance(capability_passes, list), "capability_passes must be an array")
    pass_statuses: dict[str, str] = {}
    pass_purposes: dict[str, set[str]] = {}
    pass_metadata: dict[str, dict[str, Any]] = {}
    baseline_passes: dict[tuple[str, str], dict[str, Any]] = {}
    for index, capability_pass in enumerate(capability_passes):
        prefix = f"capability_passes[{index}]"
        require(isinstance(capability_pass, dict), f"{prefix} must be an object")
        pass_id = capability_pass.get("id")
        validate_text(pass_id, f"{prefix}.id")
        require(pass_id != "core", f"{prefix}.id uses reserved value core")
        require(pass_id not in pass_statuses, f"duplicate capability pass id: {pass_id}")
        for field in ("provider", "capability"):
            validate_text(capability_pass.get(field), f"{prefix}.{field}")
        provider = capability_pass["provider"]
        capability = capability_pass["capability"]
        status = capability_pass.get("status")
        require(status in CAPABILITY_PASS_STATUSES, f"{prefix}.status is invalid")
        pass_statuses[pass_id] = status
        pass_metadata[pass_id] = capability_pass
        invocation = capability_pass.get("invocation", "automatic")
        require(invocation in CAPABILITY_INVOCATIONS, f"{prefix}.invocation is invalid")
        purposes = capability_pass.get("purposes")
        validate_text_list(purposes, f"{prefix}.purposes", allow_empty=False)
        require(len(purposes) == len(set(purposes)), f"{prefix}.purposes must not contain duplicates")
        require(set(purposes) <= CAPABILITY_PASS_PURPOSES, f"{prefix}.purposes contains an invalid value")
        pass_purposes[pass_id] = set(purposes)
        input_kinds = capability_pass.get("input_kinds", [])
        validate_text_list(input_kinds, f"{prefix}.input_kinds")
        require(len(input_kinds) == len(set(input_kinds)), f"{prefix}.input_kinds must not contain duplicates")
        require(set(input_kinds) <= CAPABILITY_INPUT_KINDS, f"{prefix}.input_kinds contains an invalid value")
        validate_text_list(capability_pass.get("input_sources", []), f"{prefix}.input_sources")
        validate_text_list(capability_pass.get("limitations", []), f"{prefix}.limitations")
        if "coverage_dimensions" in capability_pass:
            coverage_dimensions = capability_pass["coverage_dimensions"]
            validate_text_list(coverage_dimensions, f"{prefix}.coverage_dimensions", allow_empty=False)
            require(
                len(coverage_dimensions) == len(set(coverage_dimensions)),
                f"{prefix}.coverage_dimensions must not contain duplicates",
            )
            require(
                set(coverage_dimensions) <= set(weights),
                f"{prefix}.coverage_dimensions contains an invalid dimension for {profile_name}",
            )
        baseline_key = (provider, capability)
        if baseline_key == ADAPTIVE_COMPLEMENT_PASS:
            require(invocation == "automatic", f"{prefix}.invocation must be automatic for the Wira adaptive complement")
            require(status == "used", f"{prefix}.status must be used for a recorded Wira adaptive complement")
            require(
                set(purposes) & {"candidate_findings", "specialist_review"},
                f"{prefix}.purposes must include candidate_findings or specialist_review",
            )
            require(input_kinds, f"{prefix}.input_kinds must not be empty for the Wira adaptive complement")
            require(capability_pass.get("input_sources", []), f"{prefix}.input_sources must not be empty for the Wira adaptive complement")
            require("coverage_dimensions" in capability_pass, f"{prefix}.coverage_dimensions is required for the Wira adaptive complement")
        if baseline_key in REQUIRED_BASELINE_PASSES:
            require(baseline_key not in baseline_passes, f"duplicate required baseline pass: {provider}/{capability}")
            baseline_passes[baseline_key] = capability_pass
            require(invocation == "required", f"{prefix}.invocation must be required for a baseline pass")
            require(status in {"used", "unavailable"}, f"{prefix} required baseline pass must be used or unavailable")
            require(
                set(purposes) & {"candidate_findings", "specialist_review"},
                f"{prefix}.purposes must include candidate_findings or specialist_review",
            )
            if status == "used":
                require(len(input_kinds) > 0, f"{prefix}.input_kinds must not be empty for a used baseline pass")
                require(len(capability_pass.get("input_sources", [])) > 0, f"{prefix}.input_sources must not be empty for a used baseline pass")
            else:
                require(len(capability_pass.get("limitations", [])) > 0, f"{prefix}.limitations must explain baseline unavailability")
        if (
            capability_pass.get("provider") == "codex-product-design"
            and capability_pass.get("capability") == "audit"
            and invocation == "explicit"
            and "static_screenshot" in input_kinds
        ):
            require(status != "skipped", f"{prefix} explicit Product Design audit with a static screenshot must not be skipped")

    require(
        set(baseline_passes) == set(REQUIRED_BASELINE_PASSES),
        "capability_passes must include required codex-product-design/audit and claude-design/design-critique baselines",
    )
    require(execution_host != "other", "review.execution_host other cannot produce a scored final review")
    native_key = next(key for key, host in REQUIRED_BASELINE_PASSES.items() if host == execution_host)
    cross_host_key = next(key for key, host in REQUIRED_BASELINE_PASSES.items() if host != execution_host)
    require(
        baseline_passes[native_key]["status"] == "used",
        f"required host-native baseline {native_key[0]}/{native_key[1]} must be used before scoring",
    )
    require(
        baseline_passes[cross_host_key]["status"] == "unavailable",
        f"cross-host baseline {cross_host_key[0]}/{cross_host_key[1]} must be unavailable",
    )
    native_pass_id = baseline_passes[native_key]["id"]

    native_snapshot = data.get("native_expert_snapshot")
    require(isinstance(native_snapshot, dict), "native_expert_snapshot must be an object")
    require(
        native_snapshot.get("pass_id") == native_pass_id,
        "native_expert_snapshot.pass_id must reference the used host-native baseline",
    )
    require(
        native_snapshot.get("execution_mode") in NATIVE_EXECUTION_MODES,
        f"native_expert_snapshot.execution_mode must be one of {sorted(NATIVE_EXECUTION_MODES)}",
    )
    require(
        native_snapshot.get("context_scope") == NATIVE_CONTEXT_SCOPE,
        f"native_expert_snapshot.context_scope must be {NATIVE_CONTEXT_SCOPE}",
    )
    require(
        native_snapshot.get("completed_before_core_review") is True,
        "native_expert_snapshot.completed_before_core_review must be true",
    )
    require(
        native_snapshot.get("raw_output_preserved") is True,
        "native_expert_snapshot.raw_output_preserved must be true",
    )
    validate_text(native_snapshot.get("artifact_ref"), "native_expert_snapshot.artifact_ref")
    snapshot_input_sources = native_snapshot.get("input_sources")
    validate_text_list(snapshot_input_sources, "native_expert_snapshot.input_sources", allow_empty=False)
    require(
        len(snapshot_input_sources) == len(set(snapshot_input_sources)),
        "native_expert_snapshot.input_sources must not contain duplicates",
    )
    native_pass_input_sources = baseline_passes[native_key].get("input_sources", [])
    require(
        set(snapshot_input_sources) == set(native_pass_input_sources),
        "native_expert_snapshot.input_sources must match the used host-native baseline",
    )

    framework_coverage = native_snapshot.get("framework_coverage")
    require(isinstance(framework_coverage, dict), "native_expert_snapshot.framework_coverage must be an object")
    require(
        set(framework_coverage) == NATIVE_FRAMEWORK_SECTIONS,
        "native_expert_snapshot.framework_coverage must contain exactly the five native sections",
    )
    framework_candidate_ids: list[str] = []
    for section, coverage in framework_coverage.items():
        prefix = f"native_expert_snapshot.framework_coverage.{section}"
        require(isinstance(coverage, dict), f"{prefix} must be an object")
        status = coverage.get("status")
        require(status in NATIVE_FRAMEWORK_STATUSES, f"{prefix}.status is invalid")
        validate_text(coverage.get("summary"), f"{prefix}.summary")
        candidate_ids = coverage.get("candidate_ids")
        validate_text_list(candidate_ids, f"{prefix}.candidate_ids")
        require(len(candidate_ids) == len(set(candidate_ids)), f"{prefix}.candidate_ids must not contain duplicates")
        if status in {"finding", "strength", "mixed"}:
            require(candidate_ids, f"{prefix}.candidate_ids must not be empty when status is {status}")
        else:
            require(not candidate_ids, f"{prefix}.candidate_ids must be empty when status is {status}")
        framework_candidate_ids.extend(candidate_ids)

    native_candidates = native_snapshot.get("candidates")
    require(isinstance(native_candidates, list), "native_expert_snapshot.candidates must be an array")
    native_candidates_by_id: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(native_candidates):
        prefix = f"native_expert_snapshot.candidates[{index}]"
        require(isinstance(candidate, dict), f"{prefix} must be an object")
        candidate_id = candidate.get("id")
        validate_text(candidate_id, f"{prefix}.id")
        require(candidate_id not in native_candidates_by_id, f"duplicate native candidate id: {candidate_id}")
        require(candidate.get("kind") in NATIVE_CANDIDATE_KINDS, f"{prefix}.kind is invalid")
        source_section = candidate.get("source_section")
        require(source_section in NATIVE_FRAMEWORK_SECTIONS, f"{prefix}.source_section is invalid")
        validate_text(candidate.get("category"), f"{prefix}.category")
        validate_text(candidate.get("summary"), f"{prefix}.summary")
        evidence = candidate.get("evidence")
        require(isinstance(evidence, dict), f"{prefix}.evidence must be an object")
        validate_text(evidence.get("screen_id"), f"{prefix}.evidence.screen_id")
        validate_text(evidence.get("description"), f"{prefix}.evidence.description")
        require(
            candidate_id in framework_coverage[source_section]["candidate_ids"],
            f"{prefix}.id must be listed by its source framework section",
        )
        native_candidates_by_id[candidate_id] = candidate

    require(
        len(framework_candidate_ids) == len(set(framework_candidate_ids)),
        "native framework candidate IDs must not appear in more than one section",
    )
    require(
        set(framework_candidate_ids) == set(native_candidates_by_id),
        "native framework candidate IDs must match native_expert_snapshot.candidates exactly",
    )

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

    dimension_coverage = scope.get("dimension_coverage")
    require(isinstance(dimension_coverage, dict), "scope.dimension_coverage must be an object")
    require(
        set(dimension_coverage) == set(weights),
        f"scope.dimension_coverage must contain exactly the dimensions for {profile_name}",
    )
    referenced_complement_pass_ids: set[str] = set()
    for dimension, coverage in dimension_coverage.items():
        prefix = f"scope.dimension_coverage.{dimension}"
        require(isinstance(coverage, dict), f"{prefix} must be an object")
        native_status = coverage.get("native_status")
        final_status = coverage.get("final_status")
        complement_status = coverage.get("complement_status")
        require(native_status in NATIVE_COVERAGE_STATUSES, f"{prefix}.native_status is invalid")
        require(final_status in FINAL_COVERAGE_STATUSES, f"{prefix}.final_status is invalid")
        require(complement_status in COMPLEMENT_STATUSES, f"{prefix}.complement_status is invalid")

        source_pass_ids = coverage.get("source_pass_ids", [])
        validate_text_list(source_pass_ids, f"{prefix}.source_pass_ids")
        require(len(source_pass_ids) == len(set(source_pass_ids)), f"{prefix}.source_pass_ids must not contain duplicates")
        for source_pass_id in source_pass_ids:
            require(
                source_pass_id == "core" or source_pass_id in pass_statuses,
                f"{prefix}.source_pass_ids references unknown pass {source_pass_id}",
            )
            if source_pass_id != "core":
                require(pass_statuses[source_pass_id] == "used", f"{prefix}.source_pass_ids references non-used pass {source_pass_id}")

        if not dimensions[dimension]["applicable"]:
            require(native_status == "unsupported", f"{prefix}.native_status must be unsupported when the dimension is N/A")
            require(final_status == "unsupported", f"{prefix}.final_status must be unsupported when the dimension is N/A")
            require(complement_status == "not_applicable", f"{prefix}.complement_status must be not_applicable when the dimension is N/A")
            require(not source_pass_ids, f"{prefix}.source_pass_ids must be empty when the dimension is N/A")
            require("complement_pass_id" not in coverage, f"{prefix}.complement_pass_id is invalid when the dimension is N/A")
            continue

        require(native_status != "unsupported", f"{prefix}.native_status cannot be unsupported for an applicable dimension")
        require(final_status != "unsupported", f"{prefix}.final_status cannot be unsupported for an applicable dimension")
        require(source_pass_ids, f"{prefix}.source_pass_ids must not be empty for an applicable dimension")
        if native_status in {"full", "partial"}:
            require(native_pass_id in source_pass_ids, f"{prefix}.source_pass_ids must cite the host-native expert")

        if native_status == "full":
            require(complement_status == "not_needed", f"{prefix}.complement_status must be not_needed after full native coverage")
            require(final_status == "full", f"{prefix}.final_status must remain full after full native coverage")
            require("complement_pass_id" not in coverage, f"{prefix}.complement_pass_id is invalid when no complement is needed")
            continue

        require(complement_status == "used", f"{prefix}.complement_status must be used after partial or missing native coverage")
        validate_text(coverage.get("gap"), f"{prefix}.gap")
        complement_pass_id = coverage.get("complement_pass_id")
        validate_text(complement_pass_id, f"{prefix}.complement_pass_id")
        require(complement_pass_id in pass_metadata, f"{prefix}.complement_pass_id references unknown pass {complement_pass_id}")
        complement_pass = pass_metadata[complement_pass_id]
        require(complement_pass.get("status") == "used", f"{prefix}.complement_pass_id must reference a used pass")
        require(
            (complement_pass.get("provider"), complement_pass.get("capability")) == ADAPTIVE_COMPLEMENT_PASS,
            f"{prefix}.complement_pass_id must reference wira-core/adaptive-dimension-complement",
        )
        require(
            dimension in complement_pass.get("coverage_dimensions", []),
            f"{prefix}.complement_pass_id must list {dimension} in coverage_dimensions",
        )
        require(complement_pass_id in source_pass_ids, f"{prefix}.source_pass_ids must cite the complement pass")
        referenced_complement_pass_ids.add(complement_pass_id)

    recorded_complement_pass_ids = {
        pass_id
        for pass_id, capability_pass in pass_metadata.items()
        if (capability_pass.get("provider"), capability_pass.get("capability")) == ADAPTIVE_COMPLEMENT_PASS
    }
    require(
        recorded_complement_pass_ids == referenced_complement_pass_ids,
        "Wira adaptive complement passes must be created only for referenced partial or missing dimensions",
    )

    strengths = data.get("strengths", [])
    require(isinstance(strengths, list), "strengths must be an array")
    strengths_by_id: dict[str, dict[str, Any]] = {}
    for index, strength in enumerate(strengths):
        prefix = f"strengths[{index}]"
        require(isinstance(strength, dict), f"{prefix} must be an object")
        if "id" in strength:
            strength_id = strength["id"]
            validate_text(strength_id, f"{prefix}.id")
            require(strength_id not in strengths_by_id, f"duplicate strength id: {strength_id}")
            strengths_by_id[strength_id] = strength
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
    findings_by_id: dict[str, dict[str, Any]] = {}
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        require(isinstance(finding, dict), f"{prefix} must be an object")
        finding_id = finding.get("id")
        validate_text(finding_id, f"{prefix}.id")
        require(finding_id not in seen_ids, f"duplicate finding id: {finding_id}")
        seen_ids.add(finding_id)
        findings_by_id[finding_id] = finding
        dimension = finding.get("dimension")
        require(dimension in weights, f"{prefix}.dimension is invalid for {profile_name}")
        require(dimensions[dimension]["applicable"], f"{prefix} uses non-applicable dimension {dimension}")
        require(finding.get("severity") in DEDUCTIONS, f"{prefix}.severity is invalid")
        require(finding.get("status") in STATUSES, f"{prefix}.status is invalid")
        require(finding.get("check_type") in {"rule", "semantic", "contextual"}, f"{prefix}.check_type is invalid")
        require(
            finding.get("goal_relevance") in GOAL_RELEVANCE_MULTIPLIERS,
            f"{prefix}.goal_relevance is invalid",
        )
        validate_text(finding.get("severity_rationale"), f"{prefix}.severity_rationale")
        validate_text(finding.get("goal_relevance_rationale"), f"{prefix}.goal_relevance_rationale")
        confidence = finding.get("confidence")
        require(isinstance(confidence, (int, float)) and not isinstance(confidence, bool), f"{prefix}.confidence must be numeric")
        require(0 <= confidence <= 1, f"{prefix}.confidence must be between 0 and 1")
        for field in ("title", "location", "impact", "recommendation"):
            validate_text(finding.get(field), f"{prefix}.{field}")
        validate_text_list(
            finding.get("completion_criteria"),
            f"{prefix}.completion_criteria",
            allow_empty=False,
        )
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
    hypotheses_by_id: dict[str, dict[str, Any]] = {}
    for index, hypothesis in enumerate(hypotheses):
        prefix = f"validation_hypotheses[{index}]"
        require(isinstance(hypothesis, dict), f"{prefix} must be an object")
        for field in ("id", "hypothesis", "primary_metric"):
            validate_text(hypothesis.get(field), f"{prefix}.{field}")
        hypothesis_id = hypothesis["id"]
        require(hypothesis_id not in hypotheses_by_id, f"duplicate validation hypothesis id: {hypothesis_id}")
        hypotheses_by_id[hypothesis_id] = hypothesis
        require(isinstance(hypothesis.get("guardrails", []), list), f"{prefix}.guardrails must be an array")
        if "source_pass_ids" in hypothesis:
            validate_source_pass_ids(hypothesis["source_pass_ids"], f"{prefix}.source_pass_ids")

    element_accountability = data.get("element_accountability")
    require(isinstance(element_accountability, dict), "element_accountability must be an object")
    require(
        element_accountability.get("scan_completed") is True,
        "element_accountability.scan_completed must be true",
    )
    element_input_sources = element_accountability.get("input_sources")
    validate_text_list(element_input_sources, "element_accountability.input_sources", allow_empty=False)
    require(
        len(element_input_sources) == len(set(element_input_sources)),
        "element_accountability.input_sources must not contain duplicates",
    )
    require(
        set(element_input_sources) == set(snapshot_input_sources),
        "element_accountability.input_sources must match the accepted native snapshot inputs",
    )
    categories_checked = element_accountability.get("categories_checked")
    validate_text_list(categories_checked, "element_accountability.categories_checked", allow_empty=False)
    require(
        set(categories_checked) == ELEMENT_SCAN_CATEGORIES,
        "element_accountability.categories_checked must contain exactly the required micro-element categories",
    )
    require(
        len(categories_checked) == len(set(categories_checked)),
        "element_accountability.categories_checked must not contain duplicates",
    )
    element_items = element_accountability.get("items")
    require(isinstance(element_items, list) and element_items, "element_accountability.items must be a non-empty array")
    element_ids: set[str] = set()
    covered_element_sources: set[str] = set()
    has_stateful_element = False
    for index, item in enumerate(element_items):
        prefix = f"element_accountability.items[{index}]"
        require(isinstance(item, dict), f"{prefix} must be an object")
        element_id = item.get("id")
        validate_text(element_id, f"{prefix}.id")
        require(re.fullmatch(r"E-\d{3,}", element_id) is not None, f"{prefix}.id must use E-xxx format")
        require(element_id not in element_ids, f"duplicate element accountability id: {element_id}")
        element_ids.add(element_id)
        source_id = item.get("source_id")
        validate_text(source_id, f"{prefix}.source_id")
        require(source_id in element_input_sources, f"{prefix}.source_id references unknown input source {source_id}")
        covered_element_sources.add(source_id)
        for field in ("screen_id", "location", "visible_content", "decision_value", "interaction", "design_system_rule"):
            validate_text(item.get(field), f"{prefix}.{field}")
        require(item.get("element_type") in ELEMENT_TYPES, f"{prefix}.element_type is invalid")
        semantic_role = item.get("semantic_role")
        require(semantic_role in ELEMENT_SEMANTIC_ROLES, f"{prefix}.semantic_role is invalid")

        necessity = item.get("necessity")
        require(necessity in ELEMENT_NECESSITY_VALUES, f"{prefix}.necessity is invalid")
        deletion_test = item.get("deletion_test")
        require(isinstance(deletion_test, dict), f"{prefix}.deletion_test must be an object")
        deletion_result = deletion_test.get("result")
        require(deletion_result in ELEMENT_DELETION_RESULTS, f"{prefix}.deletion_test.result is invalid")
        require(
            deletion_result == ELEMENT_NECESSITY_TO_DELETION[necessity],
            f"{prefix}.deletion_test.result must match necessity",
        )
        validate_text(deletion_test.get("rationale"), f"{prefix}.deletion_test.rationale")

        lifecycle = item.get("lifecycle")
        require(isinstance(lifecycle, dict), f"{prefix}.lifecycle must be an object")
        lifecycle_requirement = lifecycle.get("requirement")
        lifecycle_status = lifecycle.get("evidence_status")
        require(
            lifecycle_requirement in ELEMENT_LIFECYCLE_REQUIREMENTS,
            f"{prefix}.lifecycle.requirement is invalid",
        )
        require(lifecycle_status in ELEMENT_LIFECYCLE_EVIDENCE, f"{prefix}.lifecycle.evidence_status is invalid")
        if semantic_role == "status":
            require(
                lifecycle_requirement != "not_required",
                f"{prefix} status role must define or validate a lifecycle",
            )
        if semantic_role == "status" or lifecycle_requirement in {"required", "unknown"}:
            has_stateful_element = True
        lifecycle_values: dict[str, str] = {}
        for field in ELEMENT_LIFECYCLE_FIELDS:
            value = lifecycle.get(field)
            validate_text(value, f"{prefix}.lifecycle.{field}")
            lifecycle_values[field] = value.strip().lower()
        if lifecycle_requirement == "not_required":
            require(
                lifecycle_status == "not_applicable",
                f"{prefix}.lifecycle.evidence_status must be not_applicable when lifecycle is not required",
            )
        else:
            require(
                lifecycle_status != "not_applicable",
                f"{prefix}.lifecycle.evidence_status cannot be not_applicable when lifecycle may be required",
            )
        if lifecycle_status == "complete":
            require(
                all(value != "unknown" for value in lifecycle_values.values()),
                f"{prefix}.lifecycle complete status requires all lifecycle rules",
            )

        verification_basis = item.get("verification_basis")
        validate_text_list(verification_basis, f"{prefix}.verification_basis", allow_empty=False)
        require(
            len(verification_basis) == len(set(verification_basis)),
            f"{prefix}.verification_basis must not contain duplicates",
        )
        require(
            set(verification_basis) <= ELEMENT_EVIDENCE_BASES,
            f"{prefix}.verification_basis contains an invalid value",
        )
        assessment = item.get("assessment")
        issue_basis = item.get("issue_basis")
        require(assessment in ELEMENT_ASSESSMENTS, f"{prefix}.assessment is invalid")
        require(issue_basis in ELEMENT_ISSUE_BASES, f"{prefix}.issue_basis is invalid")
        if assessment == "no_issue":
            require(issue_basis == "none", f"{prefix}.issue_basis must be none when assessment is no_issue")
            require("target_ref" not in item, f"{prefix}.target_ref is invalid when assessment is no_issue")
        else:
            require(issue_basis != "none", f"{prefix}.issue_basis must identify the concern")
            target_ref = item.get("target_ref")
            require(isinstance(target_ref, dict), f"{prefix}.target_ref must be an object")
            target_type = target_ref.get("type")
            target_id = target_ref.get("id")
            require(target_type in ELEMENT_TARGET_TYPES, f"{prefix}.target_ref.type is invalid")
            validate_text(target_id, f"{prefix}.target_ref.id")
            if assessment == "finding":
                require(target_type == "finding", f"{prefix}.finding assessment must target a finding")
                require(target_id in findings_by_id, f"{prefix}.target_ref references unknown finding {target_id}")
                require(
                    findings_by_id[target_id].get("status") == "confirmed",
                    f"{prefix}.finding assessment must target a confirmed finding",
                )
            elif target_type == "finding":
                require(target_id in findings_by_id, f"{prefix}.target_ref references unknown finding {target_id}")
                require(
                    findings_by_id[target_id].get("status") == "tentative",
                    f"{prefix}.validation_required finding target must be tentative",
                )
            else:
                require(
                    target_id in hypotheses_by_id,
                    f"{prefix}.target_ref references unknown validation hypothesis {target_id}",
                )

        if necessity in {"redundant", "unknown"} or deletion_result in {"no_material_loss", "unknown"}:
            require(assessment != "no_issue", f"{prefix} unresolved or redundant necessity cannot be closed as no_issue")
        if lifecycle_requirement == "unknown":
            require(assessment == "validation_required", f"{prefix} unknown lifecycle requirement must be validated")
        if lifecycle_requirement == "required" and lifecycle_status in {"partial", "missing", "unsupported"}:
            require(assessment != "no_issue", f"{prefix} incomplete required lifecycle cannot be closed as no_issue")
        if issue_basis == "lifecycle" and assessment == "finding":
            require(
                lifecycle_status != "unsupported",
                f"{prefix} unsupported lifecycle evidence cannot produce a confirmed finding",
            )
            require(
                bool(set(verification_basis) & STRONG_LIFECYCLE_EVIDENCE),
                f"{prefix} confirmed lifecycle finding requires Figma, PRD, design-system, video, or implementation evidence",
            )

    missing_element_sources = sorted(set(element_input_sources) - covered_element_sources)
    require(
        not missing_element_sources,
        f"element_accountability must inspect every accepted input source: {missing_element_sources}",
    )
    if has_stateful_element:
        require(
            dimensions["state_coverage"]["applicable"] is True,
            "scope.dimensions.state_coverage must be applicable when a visible element implies state",
        )

    specialist_synthesis = data.get("specialist_synthesis", [])
    require(isinstance(specialist_synthesis, list), "specialist_synthesis must be an array")
    synthesis_ids: set[str] = set()
    synthesized_pass_ids: set[str] = set()
    native_candidate_disposition_counts = {candidate_id: 0 for candidate_id in native_candidates_by_id}
    for index, item in enumerate(specialist_synthesis):
        prefix = f"specialist_synthesis[{index}]"
        require(isinstance(item, dict), f"{prefix} must be an object")
        synthesis_id = item.get("id")
        validate_text(synthesis_id, f"{prefix}.id")
        require(synthesis_id not in synthesis_ids, f"duplicate specialist synthesis id: {synthesis_id}")
        synthesis_ids.add(synthesis_id)
        source_pass_id = item.get("source_pass_id")
        validate_text(source_pass_id, f"{prefix}.source_pass_id")
        require(source_pass_id in pass_statuses, f"{prefix}.source_pass_id references unknown pass {source_pass_id}")
        require(pass_statuses[source_pass_id] == "used", f"{prefix}.source_pass_id references non-used pass {source_pass_id}")
        synthesized_pass_ids.add(source_pass_id)
        if source_pass_id == native_pass_id:
            source_candidate_ids = item.get("source_candidate_ids")
            validate_text_list(source_candidate_ids, f"{prefix}.source_candidate_ids")
            require(
                len(source_candidate_ids) == len(set(source_candidate_ids)),
                f"{prefix}.source_candidate_ids must not contain duplicates",
            )
            for candidate_id in source_candidate_ids:
                require(
                    candidate_id in native_candidates_by_id,
                    f"{prefix}.source_candidate_ids references unknown native candidate {candidate_id}",
                )
                native_candidate_disposition_counts[candidate_id] += 1
        else:
            require(
                "source_candidate_ids" not in item,
                f"{prefix}.source_candidate_ids is reserved for the host-native snapshot",
            )
        for field in ("summary", "rationale"):
            validate_text(item.get(field), f"{prefix}.{field}")
        disposition = item.get("disposition")
        require(disposition in SPECIALIST_DISPOSITIONS, f"{prefix}.disposition is invalid")
        target_refs = item.get("target_refs")
        require(isinstance(target_refs, list), f"{prefix}.target_refs must be an array")
        if disposition == "not_adopted":
            require(len(target_refs) == 0, f"{prefix}.target_refs must be empty when disposition is not_adopted")
        else:
            require(len(target_refs) > 0, f"{prefix}.target_refs must not be empty when disposition is {disposition}")

        seen_target_refs: set[tuple[str, str]] = set()
        for target_index, target_ref in enumerate(target_refs):
            target_prefix = f"{prefix}.target_refs[{target_index}]"
            require(isinstance(target_ref, dict), f"{target_prefix} must be an object")
            target_type = target_ref.get("type")
            target_id = target_ref.get("id")
            require(target_type in SPECIALIST_TARGET_TYPES, f"{target_prefix}.type is invalid")
            validate_text(target_id, f"{target_prefix}.id")
            target_key = (target_type, target_id)
            require(target_key not in seen_target_refs, f"{prefix}.target_refs must not contain duplicates")
            seen_target_refs.add(target_key)

            if target_type == "finding":
                require(target_id in findings_by_id, f"{target_prefix} references unknown finding {target_id}")
                target = findings_by_id[target_id]
            elif target_type == "strength":
                require(target_id in strengths_by_id, f"{target_prefix} references unknown strength {target_id}")
                target = strengths_by_id[target_id]
            else:
                require(target_id in hypotheses_by_id, f"{target_prefix} references unknown validation hypothesis {target_id}")
                target = hypotheses_by_id[target_id]

            target_source_pass_ids = target.get("source_pass_ids", ["core"])
            require(source_pass_id in target_source_pass_ids, f"{target_prefix} target must cite source pass {source_pass_id}")
            if disposition == "adopted":
                require(target_type in {"finding", "strength"}, f"{target_prefix} adopted items may target only findings or strengths")
                if target_type == "finding":
                    require(target.get("status") == "confirmed", f"{target_prefix} adopted finding must have confirmed status")
            elif disposition == "retained_for_validation":
                require(target_type in {"finding", "validation_hypothesis"}, f"{target_prefix} retained items may target only tentative findings or validation hypotheses")
                if target_type == "finding":
                    require(target.get("status") == "tentative", f"{target_prefix} retained finding must have tentative status")

    synthesis_required_pass_ids = {
        pass_id
        for pass_id, status in pass_statuses.items()
        if status == "used" and pass_purposes[pass_id] & {"candidate_findings", "specialist_review"}
    }
    missing_synthesis = sorted(synthesis_required_pass_ids - synthesized_pass_ids)
    require(not missing_synthesis, f"specialist_synthesis is required for used review passes: {missing_synthesis}")
    unmapped_native_candidates = sorted(
        candidate_id
        for candidate_id, count in native_candidate_disposition_counts.items()
        if count == 0
    )
    duplicate_native_candidates = sorted(
        candidate_id
        for candidate_id, count in native_candidate_disposition_counts.items()
        if count > 1
    )
    require(
        not unmapped_native_candidates,
        f"native candidates must have one specialist_synthesis disposition: {unmapped_native_candidates}",
    )
    require(
        not duplicate_native_candidates,
        f"native candidates must not have multiple specialist_synthesis dispositions: {duplicate_native_candidates}",
    )

    return data


def get_development_readiness(
    overall_score: float,
    score_confidence: float,
    blocker_count: int,
    major_count: int,
    moderate_count: int,
) -> dict[str, Any]:
    thresholds = {
        "ready_score": DEVELOPMENT_READY_SCORE,
        "revision_score": DEVELOPMENT_REVISION_SCORE,
        "minimum_score_confidence": DEVELOPMENT_MIN_CONFIDENCE,
        "conditional_moderate_count": CONDITIONAL_MODERATE_COUNT,
        "revision_moderate_count": REVISION_MODERATE_COUNT,
    }
    reasons: list[str] = []

    if overall_score < DEVELOPMENT_REVISION_SCORE:
        reasons.append("overall_score_below_70")
    if blocker_count:
        reasons.append("confirmed_blocker_findings")
    if major_count >= 2:
        reasons.append("multiple_confirmed_major_findings")
    if moderate_count >= REVISION_MODERATE_COUNT:
        reasons.append("many_confirmed_moderate_findings")
    if reasons:
        return {
            "status": "revise_before_development",
            "label": "暂不建议进入开发",
            "recommended_action": "先完成一轮设计调整，关闭阻断或重大问题后重新评审。",
            "reasons": reasons,
            "thresholds": thresholds,
            "requires_re_review": True,
        }

    if score_confidence < DEVELOPMENT_MIN_CONFIDENCE:
        return {
            "status": "insufficient_evidence",
            "label": "证据不足，暂不做开发准入判断",
            "recommended_action": "补齐关键流程、状态或可测量证据后重新评分。",
            "reasons": ["score_confidence_below_0.65"],
            "thresholds": thresholds,
            "requires_re_review": True,
        }

    if overall_score < DEVELOPMENT_READY_SCORE or major_count == 1 or moderate_count >= CONDITIONAL_MODERATE_COUNT:
        if overall_score < DEVELOPMENT_READY_SCORE:
            reasons.append("overall_score_below_85")
        if major_count == 1:
            reasons.append("one_confirmed_major_finding")
        if moderate_count >= CONDITIONAL_MODERATE_COUNT:
            reasons.append("several_confirmed_moderate_findings")
        recommended_action = (
            "先关闭重大问题并确认修改方案；仅可并行开展技术预研或低返工风险工作。"
            if major_count == 1
            else "先完成优先改进项并确认修改方案；仅可并行开展技术预研或低返工风险工作。"
        )
        return {
            "status": "conditional_handoff",
            "label": "需修改后进入开发",
            "recommended_action": recommended_action,
            "reasons": reasons,
            "thresholds": thresholds,
            "requires_re_review": True,
        }

    return {
        "status": "ready_for_development",
        "label": "可正常进入开发",
        "recommended_action": "进入设计交付与开发，并把一般和轻微问题纳入实现验收清单。",
        "reasons": ["score_at_or_above_85", "no_confirmed_blocker_or_major", "sufficient_score_confidence"],
        "thresholds": thresholds,
        "requires_re_review": False,
    }


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
    moderate_count = sum(finding["severity"] == "moderate" for finding in scored_findings)
    severity_penalty_items: list[dict[str, Any]] = []
    severity_penalty_total = 0.0
    for index, finding in enumerate(scored_findings):
        goal_relevance = finding.get("goal_relevance", "supporting")
        base_penalty = GLOBAL_SEVERITY_PENALTIES[finding["severity"]]
        multiplier = GOAL_RELEVANCE_MULTIPLIERS[goal_relevance]
        penalty = base_penalty * multiplier
        severity_penalty_total += penalty
        severity_penalty_items.append(
            {
                "finding_id": finding.get("id", f"finding-{index + 1}"),
                "severity": finding["severity"],
                "goal_relevance": goal_relevance,
                "base_penalty": base_penalty,
                "multiplier": multiplier,
                "penalty": round(penalty, 2),
            }
        )
    severity_calibrated_score = max(0.0, 100 - severity_penalty_total)
    calibrated_overall = min(raw_overall, severity_calibrated_score)
    if blocker_count:
        overall = min(calibrated_overall, 59)
    elif major_count >= 2:
        overall = min(calibrated_overall, 79)
    elif major_count == 1:
        overall = min(calibrated_overall, 89)
    else:
        overall = calibrated_overall
    score_confidence = sum(
        dimensions[dimension]["evidence_confidence"] * weights[dimension]
        for dimension in applicable
    ) / total_weight
    rounded_overall = round(overall, 1)
    rounded_confidence = round(score_confidence, 2)

    return {
        "overall_score": rounded_overall,
        "raw_weighted_score": round(raw_overall, 1),
        "severity_calibrated_score": round(severity_calibrated_score, 1),
        "severity_penalty_total": round(severity_penalty_total, 1),
        "severity_penalties": severity_penalty_items,
        "calibration_limiter": (
            "severity_budget"
            if severity_calibrated_score < raw_overall
            else "dimension_weighted"
            if raw_overall < severity_calibrated_score
            else "both"
        ),
        "score_confidence": rounded_confidence,
        "dimension_scores": dimension_scores,
        "scoring_profile": profile_name,
        "scoring_version": "2.0",
        "development_readiness": get_development_readiness(
            rounded_overall,
            rounded_confidence,
            blocker_count,
            major_count,
            moderate_count,
        ),
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
