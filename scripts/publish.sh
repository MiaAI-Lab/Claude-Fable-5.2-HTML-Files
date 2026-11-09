#!/usr/bin/env bash
# Run on a machine with GitHub CLI authentication and network access.
set -euo pipefail
repo='MiaAI-Lab/Claude-Fable-5.2-HTML-Files'
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v gh >/dev/null || { echo 'Install GitHub CLI (gh) and run gh auth login first.' >&2; exit 1; }
gh auth status
if ! gh repo view "$repo" --json name >/dev/null 2>&1; then
  gh repo create "$repo" --private --description 'Claude Fable 5.2 HTML Files — visual studies with screenshots and original prompts'
fi
visibility="$(gh repo view "$repo" --json visibility --jq .visibility)"
if [[ "$visibility" != 'PRIVATE' ]]; then
  echo 'The target repository is not private; stopping without changing its visibility.' >&2
  exit 1
fi
checkout="$(mktemp -d /tmp/claude-fable-publish.XXXXXX)"
trap 'rm -rf -- "$checkout"' EXIT
gh repo clone "$repo" "$checkout/repo"
cd "$checkout/repo"
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git checkout main
else
  git checkout -b main
fi
cp "$source_dir"/*.html "$source_dir"/*.txt "$source_dir/favicon.svg" "$source_dir/.nojekyll" "$source_dir/README.md" .
mkdir -p scripts .github/workflows
cp "$source_dir"/scripts/*.py "$source_dir"/scripts/*.sh "$source_dir"/scripts/*.html "$source_dir"/scripts/*.txt scripts/
cp "$source_dir/.github/workflows/pages.yml" .github/workflows/
if [[ -d "$source_dir/thumbs" ]]; then cp -r "$source_dir/thumbs" .; fi
git add -- '*.html' '*.txt' favicon.svg .nojekyll README.md scripts .github/workflows/pages.yml
if [[ -d thumbs ]]; then git add thumbs; fi
if ! git diff --cached --quiet; then
  git commit -m 'Add Claude Fable 5.2 gallery with prompts and screenshot deployment'
fi
git push -u origin main
if gh api "repos/$repo/pages" >/dev/null 2>&1; then
  gh api --method PUT "repos/$repo/pages" -f build_type=workflow >/dev/null
else
  gh api --method POST "repos/$repo/pages" -f build_type=workflow >/dev/null
fi
gh workflow run pages.yml --repo "$repo" --ref main
echo "Deployment started. Follow it with: gh run list --repo $repo"
echo 'Expected URL after success: https://miaai-lab.github.io/Claude-Fable-5.2-HTML-Files/'
