#!/usr/bin/env python3
"""Portable repository validation for the dual-platform plugin package."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "weire-design-review"
SKILL = PLUGIN / "skills" / "weire-design-review"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SCORER = SKILL / "scripts" / "review_score.py"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"root must be an object: {path.relative_to(ROOT)}")
    return value


def marketplace_entry(marketplace: dict, path: Path) -> dict:
    entries = marketplace.get("plugins")
    require(isinstance(entries, list), f"plugins must be an array: {path.relative_to(ROOT)}")
    matches = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == "weire-design-review"]
    require(len(matches) == 1, f"expected one weire-design-review entry: {path.relative_to(ROOT)}")
    return matches[0]


def validate_manifests() -> str:
    codex = load_json(CODEX_MANIFEST)
    claude = load_json(CLAUDE_MANIFEST)
    for label, manifest in (("Codex", codex), ("Claude", claude)):
        require(manifest.get("name") == "weire-design-review", f"{label} plugin name is invalid")
        version = manifest.get("version")
        require(isinstance(version, str) and SEMVER.fullmatch(version) is not None, f"{label} version is not SemVer")
        require(manifest.get("skills") == "./skills/", f"{label} skills path must be ./skills/")
        require(isinstance(manifest.get("description"), str) and manifest["description"].strip(), f"{label} description is missing")
    require(codex["version"] == claude["version"], "Codex and Claude plugin versions must match")

    codex_marketplace = load_json(CODEX_MARKETPLACE)
    claude_marketplace = load_json(CLAUDE_MARKETPLACE)
    require(codex_marketplace.get("name") == "bluebone-ai", "Codex marketplace name must be bluebone-ai")
    require(claude_marketplace.get("name") == "bluebone-ai", "Claude marketplace name must be bluebone-ai")
    require(
        "knowledge-work-plugins" in claude_marketplace.get("allowCrossMarketplaceDependenciesOn", []),
        "Claude marketplace must allow the official Design dependency",
    )
    codex_entry = marketplace_entry(codex_marketplace, CODEX_MARKETPLACE)
    claude_entry = marketplace_entry(claude_marketplace, CLAUDE_MARKETPLACE)
    require(
        codex_entry.get("source") == {"source": "local", "path": "./plugins/weire-design-review"},
        "Codex marketplace source is invalid",
    )
    require(claude_entry.get("source") == "./plugins/weire-design-review", "Claude marketplace source is invalid")
    design_dependency = {"name": "design", "marketplace": "knowledge-work-plugins"}
    require(design_dependency in claude_entry.get("dependencies", []), "Claude marketplace Design dependency is missing")
    require(design_dependency in claude.get("dependencies", []), "Claude plugin Design dependency is missing")
    return codex["version"]


def validate_skill() -> None:
    skill_file = SKILL / "SKILL.md"
    report_template = SKILL / "references" / "report-template.md"
    require(skill_file.is_file(), "shared SKILL.md is missing")
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    require(match is not None, "SKILL.md frontmatter is invalid")
    frontmatter = match.group(1)
    require(re.search(r"^name:\s*weire-design-review\s*$", frontmatter, re.MULTILINE) is not None, "SKILL.md name is invalid")
    require(re.search(r"^description:\s*\S.+$", frontmatter, re.MULTILINE) is not None, "SKILL.md description is missing")
    require((SKILL / "agents" / "openai.yaml").is_file(), "agents/openai.yaml is missing")
    require(SCORER.is_file(), "review_score.py is missing")
    require("host-native baseline pass" in text, "SKILL.md must require the host-native design expert baseline")
    require("adaptive-dimension-complement.md" in text, "SKILL.md must run adaptive dimension complement routing")
    require(
        (SKILL / "references" / "adaptive-dimension-complement.md").is_file(),
        "adaptive-dimension-complement.md is missing",
    )
    require((SKILL / "references" / "design-goal-gate.md").is_file(), "design-goal-gate.md is missing")
    require("design-goal-gate.md" in text, "SKILL.md must run the mandatory design goal gate")
    require((SKILL / "references" / "native-expert-snapshot.md").is_file(), "native-expert-snapshot.md is missing")
    require("native-expert-snapshot.md" in text, "SKILL.md must freeze the host-native expert snapshot")
    require("designer_summary" in text, "SKILL.md must define the default designer summary mode")
    require("audit_full" in text, "SKILL.md must retain the optional full audit mode")
    require(report_template.is_file(), "report-template.md is missing")
    report_text = report_template.read_text(encoding="utf-8")
    for required_section in (
        "评审结果",
        "优先改稿清单",
        "本轮需要保留",
        "修改后复审条件",
        "完整审计",
    ):
        require(required_section in report_text, f"report-template.md is missing {required_section}")
    for forbidden_label in (
        "Review Result / 评审结果",
        "Revision Tasks / 优先改稿清单",
        "Preserve / 本轮需要保留",
        "Re-review Checklist / 修改后复审条件",
        "Full Audit / 完整审计",
        "Overall Impression / 整体印象",
        "Usability / 易用性",
        "Visual Hierarchy / 视觉层级",
        "Consistency / 一致性",
        "Accessibility / 无障碍性",
        "What Works Well / 做得好的地方",
        "Priority Recommendations / 优先改进建议",
        "Development Readiness / 开发准入",
        "重大 Major",
        "一般 Moderate",
        "轻微 Minor",
        "阻断 Blocker",
    ):
        require(forbidden_label not in report_text, f"report-template.md contains bilingual label: {forbidden_label}")

    markdown_files = [skill_file, *sorted((SKILL / "references").glob("*.md"))]
    for markdown_file in markdown_files:
        content = markdown_file.read_text(encoding="utf-8")
        require("[TODO" not in content, f"TODO placeholder in {markdown_file.relative_to(ROOT)}")
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "codex://")):
                continue
            resolved = (markdown_file.parent / unquote(target)).resolve()
            require(resolved.exists(), f"broken local link in {markdown_file.relative_to(ROOT)}: {raw_target}")


def validate_scorer() -> None:
    with tempfile.TemporaryDirectory(prefix="weire-plugin-validation-") as temp_dir:
        py_compile.compile(str(SCORER), cfile=str(Path(temp_dir) / "review_score.pyc"), doraise=True)
    result = subprocess.run(
        [sys.executable, str(SCORER), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    require(result.returncode == 0, f"review_score.py --help failed: {result.stderr.strip()}")


def main() -> int:
    try:
        version = validate_manifests()
        validate_skill()
        validate_scorer()
    except (ValidationError, py_compile.PyCompileError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"portable validation passed: weire-design-review {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
