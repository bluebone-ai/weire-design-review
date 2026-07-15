#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN="$ROOT/plugins/weire-design-review"
SKILL="$PLUGIN/skills/weire-design-review"
CODEX_TOOLS="${CODEX_HOME:-$HOME/.codex}/skills/.system"
CODEX_PYTHON="${CODEX_VALIDATION_PYTHON:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3}"

python3 "$ROOT/scripts/validate_release.py"
bash -n "$ROOT/scripts/release.sh"

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN" --strict
  claude plugin validate "$ROOT" --strict
else
  echo "Claude CLI unavailable; portable Claude manifest validation already passed."
fi

if [[ -x "$CODEX_PYTHON" && -f "$CODEX_TOOLS/plugin-creator/scripts/validate_plugin.py" ]]; then
  "$CODEX_PYTHON" "$CODEX_TOOLS/plugin-creator/scripts/validate_plugin.py" "$PLUGIN"
else
  echo "Codex validator unavailable; portable Codex manifest validation already passed."
fi

if [[ -x "$CODEX_PYTHON" && -f "$CODEX_TOOLS/skill-creator/scripts/quick_validate.py" ]]; then
  "$CODEX_PYTHON" "$CODEX_TOOLS/skill-creator/scripts/quick_validate.py" "$SKILL"
else
  echo "Codex Skill validator unavailable; portable Skill validation already passed."
fi

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$ROOT" diff --check
fi

echo "All available validations passed."
