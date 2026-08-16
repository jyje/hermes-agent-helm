#!/usr/bin/env bash
set -euo pipefail

# The template ships with THIS skill, not with the target --repo: --repo may
# be checked out to any branch/commit of the implementation, including one
# that predates this skill's own merge. Resolve it relative to this script,
# not to $repo's working tree.
SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

usage() {
  cat <<'EOF'
Usage:
  validation-cycle.sh preflight --repo DIR --feature-branch BRANCH --sha SHA
  validation-cycle.sh create --repo DIR --feature-branch BRANCH --test-branch BRANCH --worktree DIR --sha SHA [--apply]
  validation-cycle.sh classify --phase PHASE --result RESULT
  validation-cycle.sh evidence --sha SHA --run-url URL --input TEXT --expected TEXT --actual TEXT
  validation-cycle.sh cleanup --repo DIR --test-branch BRANCH --worktree DIR --comment-url URL [--apply]
EOF
}

die() { echo "error: $*" >&2; exit 1; }
require_full_sha() { [[ "$1" =~ ^[0-9a-f]{40}$ ]] || die "SHA must contain exactly 40 lowercase hexadecimal characters"; }

command_name=${1:-}
shift || true
repo=
feature_branch=
test_branch=
worktree=
sha=
run_url=
comment_url=
input=
expected=
actual=
phase=
result=
apply=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) repo=${2:?}; shift 2 ;;
    --feature-branch) feature_branch=${2:?}; shift 2 ;;
    --test-branch) test_branch=${2:?}; shift 2 ;;
    --worktree) worktree=${2:?}; shift 2 ;;
    --sha) sha=${2:?}; shift 2 ;;
    --run-url) run_url=${2:?}; shift 2 ;;
    --comment-url) comment_url=${2:?}; shift 2 ;;
    --input) input=${2:?}; shift 2 ;;
    --expected) expected=${2:?}; shift 2 ;;
    --actual) actual=${2:?}; shift 2 ;;
    --phase) phase=${2:?}; shift 2 ;;
    --result) result=${2:?}; shift 2 ;;
    --apply) apply=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

preflight() {
  [[ -d $repo/.git || -f $repo/.git ]] || die "--repo is not a Git worktree: $repo"
  [[ $feature_branch == feat/* || $feature_branch == fix/* || $feature_branch == docs/* || $feature_branch == ci/* || $feature_branch == chore/* ]] || die "unexpected feature branch: $feature_branch"
  require_full_sha "$sha"
  local local_sha remote_sha
  local_sha=$(git -C "$repo" rev-parse --verify "${sha}^{commit}")
  [[ $local_sha == "$sha" ]] || die "local commit does not match the requested SHA"
  remote_sha=$(git -C "$repo" ls-remote --heads origin "refs/heads/$feature_branch" | awk '{print $1}')
  [[ -n $remote_sha ]] || die "remote feature branch does not exist: $feature_branch"
  [[ $remote_sha == "$sha" ]] || die "remote feature tip ($remote_sha) does not match requested SHA ($sha)"
  printf 'preflight=pass\nfeature_branch=%s\nimplementation_sha=%s\n' "$feature_branch" "$sha"
}

render_workflow() {
  local template="$SKILL_DIR/assets/validate-implementation.yaml.tmpl"
  local target="$worktree/.github/workflows/validate-implementation.yaml"
  local remote
  remote=$(git -C "$repo" config --get remote.origin.url | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')
  [[ $remote == */* ]] || die "origin must name a GitHub repository"
  mkdir -p "$(dirname "$target")"
  sed -e "s#__TEST_BRANCH__#$test_branch#g" \
      -e "s#__REPOSITORY__#$remote#g" \
      -e "s#__IMPLEMENTATION_SHA__#$sha#g" "$template" > "$target"
}

case "$command_name" in
  preflight)
    [[ -n $repo && -n $feature_branch && -n $sha ]] || { usage; exit 2; }
    preflight
    ;;
  create)
    [[ -n $repo && -n $feature_branch && -n $test_branch && -n $worktree && -n $sha ]] || { usage; exit 2; }
    [[ $test_branch == test/* ]] || die "test branch must start with test/"
    preflight
    printf 'test_branch=%s\ntest_worktree=%s\nworkflow=.github/workflows/validate-implementation.yaml\n' "$test_branch" "$worktree"
    if [[ $apply != true ]]; then
      echo 'dry_run=true'
      exit 0
    fi
    [[ ! -e $worktree ]] || die "test worktree path already exists: $worktree"
    git -C "$repo" worktree add --orphan -b "$test_branch" "$worktree"
    render_workflow
    git -C "$worktree" add .github/workflows/validate-implementation.yaml
    git -C "$worktree" commit -m "🧪 test(ci): validate ${feature_branch}"
    git -C "$worktree" push -u origin "$test_branch"
    ;;
  classify)
    [[ $result == failure ]] || die "classification only accepts --result failure"
    case "$phase" in
      checkout|workflow|pinned-sha) echo 'failure_class=harness' ;;
      assertion|workload|chart-test) echo 'failure_class=implementation' ;;
      runner|registry|network) echo 'failure_class=infrastructure' ;;
      *) die "unknown validation phase: $phase" ;;
    esac
    ;;
  evidence)
    [[ -n $sha && -n $run_url && -n $input && -n $expected && -n $actual ]] || { usage; exit 2; }
    require_full_sha "$sha"
    cat <<EOF
## Validation evidence

**Tested implementation SHA:** \`$sha\`

**Run:** $run_url

**Input:** $input

**Expected:** $expected

**Actual:** $actual

\`\`\`text
[Paste a short secret-safe excerpt from the successful run here.]
\`\`\`
EOF
    ;;
  cleanup)
    [[ -n $repo && -n $test_branch && -n $worktree && -n $comment_url ]] || { usage; exit 2; }
    [[ $test_branch == test/* ]] || die "refusing to clean a non-test branch"
    [[ $comment_url == *'/pull/'*'#issuecomment-'* ]] || die "--comment-url must be a PR comment URL"
    canonical_worktree=$(cd "$worktree" && pwd -P)
    registered=false
    while IFS= read -r entry; do
      [[ $entry == worktree\ * ]] || continue
      registered_path=${entry#worktree }
      if [[ -d $registered_path ]] && [[ $(cd "$registered_path" && pwd -P) == "$canonical_worktree" ]]; then
        registered=true
        break
      fi
    done < <(git -C "$repo" worktree list --porcelain)
    [[ $registered == true ]] || die "worktree is not registered: $worktree"
    printf 'cleanup_target_branch=%s\ncleanup_target_worktree=%s\ncomment=%s\n' "$test_branch" "$worktree" "$comment_url"
    if [[ $apply != true ]]; then
      echo 'dry_run=true'
      exit 0
    fi
    git -C "$repo" push origin --delete "$test_branch"
    git -C "$repo" worktree remove "$worktree"
    git -C "$repo" branch -D "$test_branch"
    ;;
  *) usage; exit 2 ;;
esac
