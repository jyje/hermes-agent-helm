#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
helper="$skill_dir/scripts/validation-cycle.sh"
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT

git init --bare "$fixture/origin.git" >/dev/null
git init -b main "$fixture/repo" >/dev/null
git -C "$fixture/repo" config user.name test
git -C "$fixture/repo" config user.email test@example.invalid
git -C "$fixture/repo" config commit.gpgSign false
git -C "$fixture/repo" remote add origin "$fixture/origin.git"
# The template ships with the skill's own checkout (SKILL_DIR in
# validation-cycle.sh), not with --repo, so the fixture repo deliberately
# does NOT carry a .claude/skills/ copy - this is what --repo looks like on
# any branch that predates the skill's own merge.
printf 'fixture\n' > "$fixture/repo/file"
git -C "$fixture/repo" add file
git -C "$fixture/repo" -c commit.gpgSign=false commit -m fixture >/dev/null
git -C "$fixture/repo" push -u origin main >/dev/null
git -C "$fixture/repo" switch -c feat/fixture >/dev/null
printf 'feature\n' >> "$fixture/repo/file"
git -C "$fixture/repo" -c commit.gpgSign=false commit -am feature >/dev/null
git -C "$fixture/repo" push -u origin feat/fixture >/dev/null
sha=$(git -C "$fixture/repo" rev-parse HEAD)

"$helper" preflight --repo "$fixture/repo" --feature-branch feat/fixture --sha "$sha" | grep -Fq 'preflight=pass'
"$helper" create --repo "$fixture/repo" --feature-branch feat/fixture --test-branch test/fixture --worktree "$fixture/test" --sha "$sha" | grep -Fq 'dry_run=true'
"$helper" evidence --sha "$sha" --run-url https://example.invalid/run --input fixture --expected pass --actual pass | grep -Fq "Tested implementation SHA:** \`$sha\`"
"$helper" classify --phase checkout --result failure | grep -Fq 'failure_class=harness'
"$helper" classify --phase chart-test --result failure | grep -Fq 'failure_class=implementation'
"$helper" classify --phase runner --result failure | grep -Fq 'failure_class=infrastructure'

wrong_sha="0${sha:1}"
if [[ $sha == 0* ]]; then wrong_sha="1${sha:1}"; fi
if "$helper" preflight --repo "$fixture/repo" --feature-branch feat/fixture --sha "$wrong_sha" >/dev/null 2>&1; then
  echo 'expected SHA mismatch to fail' >&2
  exit 1
fi

"$helper" create --repo "$fixture/repo" --feature-branch feat/fixture --test-branch test/fixture --worktree "$fixture/test" --sha "$sha" --apply
test "$(find "$fixture/test/.github" -type f | sed "s#$fixture/test/##")" = '.github/workflows/validate-implementation.yaml'
grep -Fq "$sha" "$fixture/test/.github/workflows/validate-implementation.yaml"
"$helper" cleanup --repo "$fixture/repo" --test-branch test/fixture --worktree "$fixture/test" --comment-url https://example.invalid/pull/1#issuecomment-1 --apply
test ! -e "$fixture/test"

echo 'validation-cycle fixture tests passed'
