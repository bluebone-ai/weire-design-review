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


def finding(dimension: str, severity: str) -> dict:
    return {
        "dimension": dimension,
        "severity": severity,
        "status": "confirmed",
        "confidence": 0.9,
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
            "summary": "The specialist pass found no additional material issue after evidence verification",
            "disposition": "not_adopted",
            "target_refs": [],
            "rationale": "All useful observations were already represented by the accepted core evidence",
        }
    ]
    return payload


class DevelopmentReadinessTests(unittest.TestCase):
    def test_85_is_normal_development_line(self) -> None:
        findings = [finding(dimension, "moderate") for dimension in SCORER.PROFILES["generic-mobile-v1"]]
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 85.0)
        self.assertEqual(scores["development_readiness"]["status"], "ready_for_development")

    def test_70_to_84_is_conditional(self) -> None:
        findings = []
        for dimension in SCORER.PROFILES["generic-mobile-v1"]:
            findings.extend([finding(dimension, "moderate"), finding(dimension, "minor")])
        scores = SCORER.score_review(make_review(findings))
        self.assertEqual(scores["overall_score"], 80.0)
        self.assertEqual(scores["development_readiness"]["status"], "conditional_handoff")
        self.assertIn("优先改进项", scores["development_readiness"]["recommended_action"])

    def test_one_major_prevents_normal_readiness(self) -> None:
        scores = SCORER.score_review(make_review([finding("usability", "major")]))
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
        self.assertEqual(scored["scores"]["scoring_version"], "1.9")
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

if __name__ == "__main__":
    unittest.main()
