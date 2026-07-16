from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORER_PATH = ROOT / "plugins" / "weire-design-review" / "skills" / "weire-design-review" / "scripts" / "review_score.py"
SPEC = importlib.util.spec_from_file_location("weire_review_score", SCORER_PATH)
assert SPEC is not None and SPEC.loader is not None
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


def make_review(findings: list[dict] | None = None, evidence_confidence: float = 0.9) -> dict:
    dimensions = {
        dimension: {"applicable": True, "evidence_confidence": evidence_confidence}
        for dimension in SCORER.PROFILES["generic-mobile-v1"]
    }
    return {
        "review": {"profile": "generic-mobile-v1"},
        "scope": {"dimensions": dimensions},
        "findings": findings or [],
    }


def finding(dimension: str, severity: str, goal_relevance: str = "supporting") -> dict:
    return {
        "dimension": dimension,
        "severity": severity,
        "status": "confirmed",
        "confidence": 0.9,
        "goal_relevance": goal_relevance,
    }


def make_validated_review(execution_host: str = "codex") -> dict:
    payload = make_review()
    payload["review"].update(
        {
            "title": "Required specialist baseline smoke test",
            "execution_host": execution_host,
            "review_engine": (
                "wira-core+codex-product-design"
                if execution_host == "codex"
                else "wira-core+claude-design"
            ),
            "source_type": "screenshot",
            "platform": "ios",
            "core_task": "Find the primary action",
            "output_mode": "designer_summary",
            "output_language": "zh-CN",
        }
    )
    payload["scope"]["limitations"] = ["Static screenshot only"]
    payload["context"] = {
        "design_goal_status": "confirmed",
        "design_goal": {
            "goal_type": "general_quality",
            "primary_goal": "Confirm that the design is ready for development",
            "success_criteria": ["Overall score is at least 85", "No blocker or major finding"],
            "source": "user_confirmed",
        },
    }
    codex_status = "used" if execution_host == "codex" else "unavailable"
    claude_status = "used" if execution_host == "claude" else "unavailable"
    payload["capability_passes"] = [
        {
            "id": "P-01",
            "provider": "codex-product-design",
            "capability": "audit",
            "invocation": "required",
            "status": codex_status,
            "purposes": ["candidate_findings", "specialist_review"],
            "input_kinds": ["static_screenshot"] if codex_status == "used" else [],
            "input_sources": ["SCREEN-01"] if codex_status == "used" else [],
            "limitations": [
                "Single static screenshot" if codex_status == "used" else "Product Design is unavailable outside Codex"
            ],
        },
        {
            "id": "C-01",
            "provider": "claude-design",
            "capability": "design-critique",
            "invocation": "required",
            "status": claude_status,
            "purposes": ["candidate_findings", "specialist_review"],
            "input_kinds": ["static_screenshot"] if claude_status == "used" else [],
            "input_sources": ["SCREEN-01"] if claude_status == "used" else [],
            "limitations": [
                "Single static screenshot" if claude_status == "used" else "Claude Design is unavailable outside Claude"
            ],
        },
    ]
    native_pass_id = "P-01" if execution_host == "codex" else "C-01"
    payload["native_expert_snapshot"] = {
        "pass_id": native_pass_id,
        "execution_mode": "isolated_subagent",
        "context_scope": "artifact_product_audience_stage_only",
        "completed_before_core_review": True,
        "raw_output_preserved": True,
        "artifact_ref": "inline:native-expert-snapshot",
        "input_sources": ["SCREEN-01"],
        "framework_coverage": {
            section: {
                "status": "no_material_issue",
                "summary": f"The native expert completed the {section} check without another material candidate",
                "candidate_ids": [],
            }
            for section in SCORER.NATIVE_FRAMEWORK_SECTIONS
        },
        "candidates": [],
    }
    payload["element_accountability"] = {
        "scan_completed": True,
        "input_sources": ["SCREEN-01"],
        "categories_checked": sorted(SCORER.ELEMENT_SCAN_CATEGORIES),
        "items": [
            {
                "id": "E-001",
                "source_id": "SCREEN-01",
                "screen_id": "SCREEN-01",
                "location": "Home / first viewport / primary action label",
                "element_type": "microcopy",
                "visible_content": "Start",
                "semantic_role": "action",
                "decision_value": "Identifies the primary action",
                "necessity": "necessary",
                "deletion_test": {
                    "result": "essential",
                    "rationale": "Removing the label would make the action unidentified",
                },
                "interaction": "The label belongs to the tappable primary action",
                "design_system_rule": "Uses the standard primary-action label role",
                "lifecycle": {
                    "requirement": "not_required",
                    "evidence_status": "not_applicable",
                    "appearance_trigger": "not_applicable",
                    "update_rule": "not_applicable",
                    "exit_rule": "not_applicable",
                    "recurrence_rule": "not_applicable",
                    "default_state": "not_applicable",
                },
                "verification_basis": ["visible_static", "design_system"],
                "assessment": "no_issue",
                "issue_basis": "none",
            }
        ],
    }
    payload["scope"]["dimension_coverage"] = {
        dimension: {
            "native_status": "full",
            "final_status": "full",
            "complement_status": "not_needed",
            "source_pass_ids": [native_pass_id],
        }
        for dimension in SCORER.PROFILES["generic-mobile-v1"]
    }
    payload["specialist_synthesis"] = [
        {
            "id": "SI-001",
            "source_pass_id": native_pass_id,
            "source_candidate_ids": [],
            "summary": "The specialist pass found no additional material issue after evidence verification",
            "disposition": "not_adopted",
            "target_refs": [],
            "rationale": "All useful observations were already represented by the accepted core evidence",
        }
    ]
    return payload


def validated_finding() -> dict:
    return {
        "id": "F-001",
        "dimension": "usability",
        "severity": "moderate",
        "status": "confirmed",
        "confidence": 0.9,
        "check_type": "semantic",
        "severity_rationale": "The issue creates repeated hesitation but does not prevent task completion",
        "goal_relevance": "direct",
        "goal_relevance_rationale": "The issue affects the declared primary-action goal",
        "source_pass_ids": ["core"],
        "delta": "unknown",
        "title": "The primary action is difficult to identify",
        "location": "Home / first viewport / primary action area",
        "evidence": {
            "screen_id": "SCREEN-01",
            "description": "Three actions use equal visual weight",
        },
        "impact": "Users may hesitate before starting the core task",
        "recommendation": "Give the primary action stronger hierarchy and demote the alternatives",
        "completion_criteria": [
            "The primary action is the first choice in a five-second first-click test",
        ],
    }


class DevelopmentReadinessTests(unittest.TestCase):
    def test_85_is_normal_development_line(self) -> None:
        dimensions = list(SCORER.PROFILES["generic-mobile-v1"])
        findings = [finding(dimensions[index % len(dimensions)], "minor") for index in range(10)]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 85.0)
        self.assertEqual(scores["development_readiness"]["status"], "ready_for_development")

    def test_70_to_84_is_conditional(self) -> None:
        dimensions = list(SCORER.PROFILES["generic-mobile-v1"])
        findings = [finding(dimensions[index], "moderate") for index in range(4)]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 80.0)
        self.assertEqual(scores["development_readiness"]["status"], "conditional_handoff")
        self.assertIn("优先改进项", scores["development_readiness"]["recommended_action"])

    def test_one_major_prevents_normal_readiness(self) -> None:
        scores = SCORER.score_review(make_review([finding("usability", "major")]))
        self.assertEqual(scores["overall_score"], 88.0)
        self.assertEqual(scores["development_readiness"]["status"], "conditional_handoff")
        self.assertIn("one_confirmed_major_finding", scores["development_readiness"]["reasons"])
        self.assertIn("重大问题", scores["development_readiness"]["recommended_action"])

    def test_blocker_requires_revision(self) -> None:
        scores = SCORER.score_review(make_review([finding("usability", "blocker")]))
        self.assertEqual(scores["development_readiness"]["status"], "revise_before_development")
        self.assertIn("confirmed_blocker_findings", scores["development_readiness"]["reasons"])

    def test_multiple_majors_require_revision(self) -> None:
        scores = SCORER.score_review(
            make_review([finding("usability", "major"), finding("visual_hierarchy", "major")])
        )
        self.assertEqual(scores["development_readiness"]["status"], "revise_before_development")
        self.assertIn("multiple_confirmed_major_findings", scores["development_readiness"]["reasons"])

    def test_low_weight_dimension_cannot_hide_a_moderate_finding(self) -> None:
        scores = SCORER.score_review(make_review([finding("platform_conventions", "moderate")]))
        self.assertEqual(scores["raw_weighted_score"], 98.8)
        self.assertEqual(scores["severity_calibrated_score"], 95.0)
        self.assertEqual(scores["overall_score"], 95.0)
        self.assertEqual(scores["calibration_limiter"], "severity_budget")

    def test_goal_relevance_changes_global_penalty(self) -> None:
        direct = SCORER.score_review(make_review([finding("usability", "moderate", "direct")]))
        supporting = SCORER.score_review(make_review([finding("usability", "moderate", "supporting")]))
        limited = SCORER.score_review(make_review([finding("usability", "moderate", "limited")]))
        self.assertLess(direct["overall_score"], supporting["overall_score"])
        self.assertLess(supporting["overall_score"], limited["overall_score"])

    def test_three_moderates_prevent_normal_readiness(self) -> None:
        findings = [
            finding("visual_hierarchy", "moderate"),
            finding("usability", "moderate"),
            finding("content", "moderate"),
        ]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 85.0)
        self.assertEqual(scores["development_readiness"]["status"], "conditional_handoff")
        self.assertIn("several_confirmed_moderate_findings", scores["development_readiness"]["reasons"])

    def test_six_moderates_require_revision(self) -> None:
        dimensions = list(SCORER.PROFILES["generic-mobile-v1"])
        findings = [finding(dimensions[index], "moderate") for index in range(6)]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 70.0)
        self.assertEqual(scores["development_readiness"]["status"], "revise_before_development")
        self.assertIn("many_confirmed_moderate_findings", scores["development_readiness"]["reasons"])

    def test_previous_high_score_issue_pattern_is_recalibrated(self) -> None:
        findings = [
            finding("visual_hierarchy", "major", "direct"),
            finding("content", "moderate"),
            finding("layout_consistency", "moderate"),
            finding("platform_conventions", "minor", "limited"),
            finding("interaction_motion", "minor", "limited"),
        ]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["severity_calibrated_score"], 72.8)
        self.assertEqual(scores["overall_score"], 72.8)
        self.assertEqual(scores["development_readiness"]["status"], "conditional_handoff")

    def test_low_evidence_confidence_defers_decision(self) -> None:
        scores = SCORER.score_review(make_review(evidence_confidence=0.5))
        self.assertEqual(scores["overall_score"], 100.0)
        self.assertEqual(scores["development_readiness"]["status"], "insufficient_evidence")

    def test_cli_writes_development_readiness(self) -> None:
        payload = make_validated_review()
        with tempfile.TemporaryDirectory() as temp_dir:
            review_path = Path(temp_dir) / "review.json"
            review_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCORER_PATH), str(review_path), "--write"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            scored = json.loads(review_path.read_text(encoding="utf-8"))
        self.assertEqual(scored["scores"]["scoring_version"], "2.0")
        self.assertEqual(scored["scores"]["development_readiness"]["status"], "ready_for_development")


class RequiredSpecialistPassTests(unittest.TestCase):
    def test_codex_requires_product_design_audit(self) -> None:
        payload = make_validated_review("codex")
        SCORER.validate_review(payload)
        payload["capability_passes"][0]["status"] = "unavailable"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "host-native baseline"):
            SCORER.validate_review(payload)

    def test_claude_requires_design_critique(self) -> None:
        payload = make_validated_review("claude")
        SCORER.validate_review(payload)
        payload["capability_passes"][1]["status"] = "skipped"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "must be used or unavailable"):
            SCORER.validate_review(payload)

    def test_both_baseline_records_are_required(self) -> None:
        payload = make_validated_review("codex")
        payload["capability_passes"].pop()
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "must include required"):
            SCORER.validate_review(payload)

    def test_review_engine_must_match_execution_host(self) -> None:
        payload = make_validated_review("codex")
        payload["review"]["review_engine"] = "wira-core+claude-design"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "review_engine"):
            SCORER.validate_review(payload)


class NativeExpertSnapshotTests(unittest.TestCase):
    @staticmethod
    def add_adopted_native_candidate(payload: dict) -> None:
        native_pass_id = payload["native_expert_snapshot"]["pass_id"]
        payload["native_expert_snapshot"]["framework_coverage"]["first_impression"] = {
            "status": "finding",
            "summary": "Warm mid-low-lightness colors create a heavy first impression",
            "candidate_ids": ["NC-001"],
        }
        payload["native_expert_snapshot"]["candidates"] = [
            {
                "id": "NC-001",
                "kind": "finding",
                "source_section": "first_impression",
                "category": "color_and_material",
                "summary": "Warm colors cluster at similar mid-low lightness and make the palette feel heavy",
                "evidence": {
                    "screen_id": "SCREEN-01",
                    "description": "Orange, pink, purple, and brown surfaces in the first viewport",
                },
            }
        ]
        accepted_finding = validated_finding()
        accepted_finding["source_pass_ids"] = ["core", native_pass_id]
        payload["findings"] = [accepted_finding]
        payload["specialist_synthesis"] = [
            {
                "id": "SI-001",
                "source_pass_id": native_pass_id,
                "source_candidate_ids": ["NC-001"],
                "summary": "The native color and material concern was verified",
                "disposition": "adopted",
                "target_refs": [{"type": "finding", "id": "F-001"}],
                "rationale": "The visible evidence supports the reported mechanism",
            }
        ]

    def test_native_snapshot_is_required(self) -> None:
        payload = make_validated_review("claude")
        payload.pop("native_expert_snapshot")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "native_expert_snapshot must be an object"):
            SCORER.validate_review(payload)

    def test_native_snapshot_must_finish_before_core_review(self) -> None:
        payload = make_validated_review("codex")
        payload["native_expert_snapshot"]["completed_before_core_review"] = False
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "completed_before_core_review must be true"):
            SCORER.validate_review(payload)

    def test_native_snapshot_requires_all_framework_sections(self) -> None:
        payload = make_validated_review("claude")
        payload["native_expert_snapshot"]["framework_coverage"].pop("consistency")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "exactly the five native sections"):
            SCORER.validate_review(payload)

    def test_native_candidate_can_be_preserved_and_adopted(self) -> None:
        payload = make_validated_review("claude")
        self.add_adopted_native_candidate(payload)
        SCORER.validate_review(payload)

    def test_unmapped_native_candidate_is_rejected(self) -> None:
        payload = make_validated_review("claude")
        self.add_adopted_native_candidate(payload)
        payload["specialist_synthesis"][0]["source_candidate_ids"] = []
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "native candidates must have one"):
            SCORER.validate_review(payload)

    def test_duplicate_native_candidate_disposition_is_rejected(self) -> None:
        payload = make_validated_review("codex")
        self.add_adopted_native_candidate(payload)
        payload["specialist_synthesis"].append(
            {
                "id": "SI-002",
                "source_pass_id": "P-01",
                "source_candidate_ids": ["NC-001"],
                "summary": "The same candidate was incorrectly handled twice",
                "disposition": "not_adopted",
                "target_refs": [],
                "rationale": "Duplicate disposition fixture",
            }
        )
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "must not have multiple"):
            SCORER.validate_review(payload)


class ElementAccountabilityTests(unittest.TestCase):
    @staticmethod
    def set_new_badge_item(payload: dict, *, confirmed: bool) -> None:
        item = payload["element_accountability"]["items"][0]
        item.update(
            {
                "location": "Home / masquerade card / title-right badge",
                "element_type": "badge_tag",
                "visible_content": "上新",
                "semantic_role": "status",
                "decision_value": "May indicate an unseen or recently released gameplay entry",
                "interaction": "No independent interaction is visible",
                "design_system_rule": "No inspected badge rule was supplied",
                "issue_basis": "lifecycle",
            }
        )
        item["lifecycle"] = {
            "requirement": "required",
            "evidence_status": "missing" if confirmed else "unsupported",
            "appearance_trigger": "unknown",
            "update_rule": "unknown",
            "exit_rule": "unknown",
            "recurrence_rule": "unknown",
            "default_state": "unknown",
        }
        lifecycle_finding = validated_finding()
        lifecycle_finding.update(
            {
                "dimension": "state_coverage",
                "title": "The new badge has no defined lifecycle",
                "location": "Home / masquerade card / title-right badge",
                "evidence": {
                    "screen_id": "SCREEN-01",
                    "description": "The 上新 badge is visible beside the gameplay title",
                },
                "impact": "The state may remain stale or force engineering to invent behavior",
                "recommendation": "Define appearance, update, exit, recurrence, and default-card rules",
                "completion_criteria": ["Figma or PRD defines the complete badge lifecycle"],
                "status": "confirmed" if confirmed else "tentative",
            }
        )
        payload["findings"] = [lifecycle_finding]
        item["necessity"] = "necessary" if confirmed else "unknown"
        item["deletion_test"] = {
            "result": "essential" if confirmed else "unknown",
            "rationale": (
                "The inspected product rule treats the badge as user-specific state"
                if confirmed
                else "The screenshot cannot show whether removing it loses user-specific state"
            ),
        }
        item["verification_basis"] = ["visible_static", "figma", "prd"] if confirmed else ["visible_static"]
        item["assessment"] = "finding" if confirmed else "validation_required"
        item["target_ref"] = {"type": "finding", "id": "F-001"}

    def test_element_accountability_is_required(self) -> None:
        payload = make_validated_review("codex")
        payload.pop("element_accountability")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "element_accountability must be an object"):
            SCORER.validate_review(payload)

    def test_all_micro_element_categories_are_required(self) -> None:
        payload = make_validated_review("claude")
        payload["element_accountability"]["categories_checked"].remove("badge_tag")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "exactly the required micro-element categories"):
            SCORER.validate_review(payload)

    def test_every_accepted_source_requires_an_element_row(self) -> None:
        payload = make_validated_review("codex")
        payload["capability_passes"][0]["input_sources"].append("SCREEN-02")
        payload["native_expert_snapshot"]["input_sources"].append("SCREEN-02")
        payload["element_accountability"]["input_sources"].append("SCREEN-02")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "inspect every accepted input source"):
            SCORER.validate_review(payload)

    def test_static_new_badge_lifecycle_stays_tentative(self) -> None:
        payload = make_validated_review("claude")
        self.set_new_badge_item(payload, confirmed=False)
        SCORER.validate_review(payload)

    def test_static_only_evidence_cannot_confirm_missing_lifecycle(self) -> None:
        payload = make_validated_review("codex")
        self.set_new_badge_item(payload, confirmed=True)
        payload["element_accountability"]["items"][0]["verification_basis"] = ["visible_static"]
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "confirmed lifecycle finding requires"):
            SCORER.validate_review(payload)

    def test_figma_and_prd_can_confirm_missing_lifecycle(self) -> None:
        payload = make_validated_review("claude")
        self.set_new_badge_item(payload, confirmed=True)
        SCORER.validate_review(payload)

    def test_visible_status_element_makes_state_coverage_applicable(self) -> None:
        payload = make_validated_review("codex")
        self.set_new_badge_item(payload, confirmed=False)
        payload["scope"]["dimensions"]["state_coverage"] = {
            "applicable": False,
            "evidence_confidence": 0,
        }
        payload["scope"]["dimension_coverage"]["state_coverage"] = {
            "native_status": "unsupported",
            "final_status": "unsupported",
            "complement_status": "not_applicable",
            "source_pass_ids": [],
        }
        payload["findings"] = []
        payload["element_accountability"]["items"][0]["target_ref"] = {
            "type": "validation_hypothesis",
            "id": "H-001",
        }
        payload["validation_hypotheses"] = [
            {
                "id": "H-001",
                "hypothesis": "The visible status badge needs an explicit lifecycle contract",
                "primary_metric": "state_contract_completeness",
                "guardrails": [],
                "source_pass_ids": ["core"],
            }
        ]
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "state_coverage must be applicable"):
            SCORER.validate_review(payload)

    def test_redundant_element_cannot_be_closed_as_no_issue(self) -> None:
        payload = make_validated_review("codex")
        item = payload["element_accountability"]["items"][0]
        item["necessity"] = "redundant"
        item["deletion_test"] = {
            "result": "no_material_loss",
            "rationale": "Removing the element changes no information or action",
        }
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "cannot be closed as no_issue"):
            SCORER.validate_review(payload)


class AdaptiveDimensionComplementTests(unittest.TestCase):
    def test_partial_native_coverage_requires_complement(self) -> None:
        payload = make_validated_review("codex")
        payload["scope"]["dimension_coverage"]["content"]["native_status"] = "partial"
        payload["scope"]["dimension_coverage"]["content"]["gap"] = "Copy tone was mentioned without a comprehension check"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "complement_status must be used"):
            SCORER.validate_review(payload)

    def test_used_complement_repairs_missing_dimension(self) -> None:
        payload = make_validated_review("claude")
        payload["capability_passes"].append(
            {
                "id": "W-01",
                "provider": "wira-core",
                "capability": "adaptive-dimension-complement",
                "invocation": "automatic",
                "status": "used",
                "purposes": ["candidate_findings", "specialist_review"],
                "input_kinds": ["static_screenshot"],
                "input_sources": ["SCREEN-01"],
                "coverage_dimensions": ["usability"],
                "limitations": ["Static screenshot only"],
            }
        )
        payload["scope"]["dimension_coverage"]["usability"] = {
            "native_status": "missing",
            "final_status": "partial",
            "complement_status": "used",
            "gap": "The native critique did not evaluate next-action predictability",
            "complement_pass_id": "W-01",
            "source_pass_ids": ["W-01"],
        }
        payload["specialist_synthesis"].append(
            {
                "id": "SI-002",
                "source_pass_id": "W-01",
                "summary": "The Wira complement checked the missing usability dimension",
                "disposition": "not_adopted",
                "target_refs": [],
                "rationale": "No additional issue was supported by the static evidence",
            }
        )
        SCORER.validate_review(payload)

    def test_complement_must_list_repaired_dimension(self) -> None:
        payload = make_validated_review("claude")
        payload["capability_passes"].append(
            {
                "id": "W-01",
                "provider": "wira-core",
                "capability": "adaptive-dimension-complement",
                "invocation": "automatic",
                "status": "used",
                "purposes": ["candidate_findings", "specialist_review"],
                "input_kinds": ["static_screenshot"],
                "input_sources": ["SCREEN-01"],
                "coverage_dimensions": ["content"],
                "limitations": ["Static screenshot only"],
            }
        )
        payload["scope"]["dimension_coverage"]["usability"] = {
            "native_status": "partial",
            "final_status": "partial",
            "complement_status": "used",
            "gap": "The native critique did not evaluate next-action predictability",
            "complement_pass_id": "W-01",
            "source_pass_ids": ["C-01", "W-01"],
        }
        payload["specialist_synthesis"].append(
            {
                "id": "SI-002",
                "source_pass_id": "W-01",
                "summary": "The complement pass was recorded",
                "disposition": "not_adopted",
                "target_refs": [],
                "rationale": "No accepted finding",
            }
        )
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "must list usability"):
            SCORER.validate_review(payload)


class DesignGoalGateTests(unittest.TestCase):
    def test_confirmed_design_goal_is_required(self) -> None:
        payload = make_validated_review("codex")
        payload["context"].pop("design_goal_status")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "design_goal_status must be confirmed"):
            SCORER.validate_review(payload)

    def test_success_criterion_is_required(self) -> None:
        payload = make_validated_review("codex")
        payload["context"]["design_goal"]["success_criteria"] = []
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "success_criteria must not be empty"):
            SCORER.validate_review(payload)

    def test_inferred_goal_source_is_rejected(self) -> None:
        payload = make_validated_review("claude")
        payload["context"]["design_goal"]["source"] = "model_inferred"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "design_goal.source"):
            SCORER.validate_review(payload)


class ReportModeTests(unittest.TestCase):
    def test_designer_summary_is_valid(self) -> None:
        payload = make_validated_review("codex")
        SCORER.validate_review(payload)

    def test_full_audit_is_valid(self) -> None:
        payload = make_validated_review("claude")
        payload["review"]["output_mode"] = "audit_full"
        SCORER.validate_review(payload)

    def test_output_mode_is_required(self) -> None:
        payload = make_validated_review("codex")
        payload["review"].pop("output_mode")
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "review.output_mode"):
            SCORER.validate_review(payload)

    def test_invalid_output_mode_is_rejected(self) -> None:
        payload = make_validated_review("codex")
        payload["review"]["output_mode"] = "verbose"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "review.output_mode"):
            SCORER.validate_review(payload)

    def test_simplified_chinese_output_is_required(self) -> None:
        payload = make_validated_review("codex")
        payload["review"]["output_language"] = "bilingual"
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "review.output_language must be zh-CN"):
            SCORER.validate_review(payload)


class DesignerFindingCardTests(unittest.TestCase):
    def test_location_and_completion_criteria_are_accepted(self) -> None:
        payload = make_validated_review("codex")
        payload["findings"] = [validated_finding()]
        SCORER.validate_review(payload)

    def test_location_is_required(self) -> None:
        payload = make_validated_review("codex")
        item = validated_finding()
        item.pop("location")
        payload["findings"] = [item]
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "findings\[0\].location"):
            SCORER.validate_review(payload)

    def test_completion_criteria_are_required(self) -> None:
        payload = make_validated_review("codex")
        item = validated_finding()
        item["completion_criteria"] = []
        payload["findings"] = [item]
        with self.assertRaisesRegex(SCORER.ReviewValidationError, "completion_criteria must not be empty"):
            SCORER.validate_review(payload)

if __name__ == "__main__":
    unittest.main()
