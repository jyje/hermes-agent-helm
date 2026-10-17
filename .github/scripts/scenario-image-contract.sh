#!/usr/bin/env bash
# image-contract scenario: run the two Helm test checks that guard chart code
# living inside the Hermes image. Both features are off by default, so none of
# the other scenarios ever exercises them:
#   - the OpenAI Codex device login imports its helpers from hermes_cli.auth;
#   - the ready message is a gateway:startup hook that Hermes loads in-process.
# An image bump that renames or moves either one would otherwise break a user's
# login or ready message with no signal in CI. No secret and no network call to
# a provider is needed: the helper check is an import, and the hook check sets
# an unknown channel so the handler logs and returns.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

kubectl create namespace "$NS" 2>/dev/null || true
echo "[$NS] installing with the Codex device login and the ready hook enabled"
# No --wait and no wait_for_hermes_startup: with the device login on, the main Pod
# waits for a person to approve a code, and the test Job does not depend on it.
helm upgrade --install hermes-agent charts/hermes-agent \
  --namespace "$NS" --create-namespace \
  --set-string env.OPENAI_API_KEY=sk-test \
  --set auth.deviceFlow.enabled=true \
  --set auth.deviceFlow.provider=openai-codex \
  --set auth.deviceFlow.notify=logs \
  --set readyNotify.enabled=true \
  --set readyNotify.notify=telegram

run_hook_test || { kubectl logs -n "$NS" "job/hermes-agent-test" --tail=-1 || true; exit 1; }

logs="$(kubectl logs -n "$NS" "job/hermes-agent-test" --tail=-1)"
printf '%s\n' "$logs"
for step in 'OK: hermes_cli.auth provides the OpenAI Codex helpers' \
            'OK: the gateway:startup hook was discovered and its handler ran.'; do
  if ! printf '%s\n' "$logs" | grep -Fq "$step"; then
    echo "::error::[$NS] the Helm test did not report: $step"
    exit 1
  fi
done
echo "[$NS] both image-contract checks passed"
