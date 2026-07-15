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
        payload = make_review()
        payload["review"].update(
            {
                "title": "Development gate smoke test",
                "source_type": "screenshot",
                "platform": "ios",
                "core_task": "Find the primary action",
            }
        )
        payload["scope"]["limitations"] = ["Static screenshot only"]
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
        self.assertEqual(scored["scores"]["scoring_version"], "1.6")
        self.assertEqual(scored["scores"]["development_readiness"]["status"], "ready_for_development")


if __name__ == "__main__":
    unittest.main()
