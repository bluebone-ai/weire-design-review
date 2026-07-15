#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_MANIFEST="$ROOT/plugins/weire-design-review/.codex-plugin/plugin.json"
CLAUDE_MANIFEST="$ROOT/plugins/weire-design-review/.claude-plugin/plugin.json"
MARKETPLACE="bluebone-ai"
PLUGIN="weire-design-review"
DRY_RUN=false
PUSH=true
UPDATE_LOCAL=true

usage() {
  cat <<'EOF'
Usage: ./scripts/release.sh <patch|minor|major> [options]

Options:
  --dry-run            Calculate the next version and validate without changing files
  --no-push            Create the release commit and tag without pushing them
  --skip-local-update  Do not update local Codex and Claude installations
  -h, --help           Show this help
EOF
}

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

BUMP=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    patch|minor|major)
      if [[ -n "$BUMP" ]]; then
        echo "Only one version bump may be specified." >&2
        exit 2
      fi
      BUMP="$1"
      ;;
    --dry-run) DRY_RUN=true ;;
    --no-push) PUSH=false ;;
    --skip-local-update) UPDATE_LOCAL=false ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if [[ -z "$BUMP" ]]; then
  echo "A patch, minor, or major bump is required." >&2
  exit 2
fi

cd "$ROOT"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Release requires a clean working tree." >&2
  exit 1
fi

read -r CURRENT_CODEX CURRENT_CLAUDE < <(python3 - "$CODEX_MANIFEST" "$CLAUDE_MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

versions = [json.loads(Path(path).read_text(encoding="utf-8"))["version"] for path in sys.argv[1:]]
print(*versions)
PY
)

if [[ "$CURRENT_CODEX" != "$CURRENT_CLAUDE" ]]; then
  echo "Codex and Claude versions differ: $CURRENT_CODEX vs $CURRENT_CLAUDE" >&2
  exit 1
fi

NEXT_VERSION="$(python3 - "$CURRENT_CODEX" "$BUMP" <<'PY'
import re
import sys

version, bump = sys.argv[1:]
match = re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version)
if not match:
    raise SystemExit(f"release requires a stable x.y.z version, got {version}")
major, minor, patch = map(int, match.groups())
if bump == "major":
    major, minor, patch = major + 1, 0, 0
elif bump == "minor":
    minor, patch = minor + 1, 0
else:
    patch += 1
print(f"{major}.{minor}.{patch}")
PY
)"

TAG="v$NEXT_VERSION"
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag already exists: $TAG" >&2
  exit 1
fi

echo "Release plan: $CURRENT_CODEX -> $NEXT_VERSION ($BUMP)"
if $DRY_RUN; then
  "$ROOT/scripts/validate.sh"
  echo "Dry run passed; no files changed."
  exit 0
fi

python3 - "$NEXT_VERSION" "$CODEX_MANIFEST" "$CLAUDE_MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

version = sys.argv[1]
for raw_path in sys.argv[2:]:
    path = Path(raw_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = version
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

"$ROOT/scripts/validate.sh"
git add "$CODEX_MANIFEST" "$CLAUDE_MANIFEST"
git diff --cached --check
git commit -F - <<EOF
chore(release): 发布 $TAG

- 同步 Codex 与 Claude Plugin 版本为 $NEXT_VERSION
- 完成双平台清单、共享 Skill 与评分脚本校验

提交工具: release.sh
EOF
git tag -a "$TAG" -m "发布 $TAG"

BRANCH="$(git branch --show-current)"
if $PUSH; then
  git push --atomic origin "$BRANCH" "$TAG"
else
  echo "Push skipped; release commit and tag exist locally."
fi

if $UPDATE_LOCAL; then
  if command -v codex >/dev/null 2>&1; then
    codex plugin add "$PLUGIN@$MARKETPLACE" || echo "Warning: Codex local update failed; release remains published." >&2
  else
    echo "Codex CLI unavailable; skipped local Codex update."
  fi
  if command -v claude >/dev/null 2>&1; then
    claude plugin marketplace update "$MARKETPLACE" || echo "Warning: Claude marketplace refresh failed." >&2
    claude plugin update "$PLUGIN@$MARKETPLACE" || echo "Warning: Claude local update failed; release remains published." >&2
  else
    echo "Claude CLI unavailable; skipped local Claude update."
  fi
fi

echo "Released $TAG. Start a new Codex or Claude task to load the new plugin version."
