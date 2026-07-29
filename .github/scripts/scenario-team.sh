#!/usr/bin/env bash
# team scenario: install a leader and one member from the thread-native values
# files and verify the Kubernetes/runtime configuration that makes a visible
# Discord mention loop possible. This is intentionally structural: CI has no
# three bot identities and must not claim a live bot-to-bot completion proof.
set -euo pipefail

NS="${NS:-test-hermes-chart}"

common_args=(
  --namespace "$NS"
  --create-namespace
  --set-string env.NVIDIA_API_KEY=
  --set-string env.OPENAI_API_KEY=sk-test
  --set-string env.DISCORD_BOT_TOKEN=
  --set tests.enabled=false
  --wait
  --timeout 5m
)

helm upgrade --install hermes-august charts/hermes-agent \
  -f charts/hermes-agent/values-team-leader.yaml \
  "${common_args[@]}"

helm upgrade --install hermes-may charts/hermes-agent \
  -f charts/hermes-agent/values-team-member.yaml \
  "${common_args[@]}"

echo "[$NS] verifying one shared transcript and Discord history backfill"
for configmap in hermes-august-config hermes-may-config; do
  config=$(kubectl get configmap "$configmap" -n "$NS" \
    -o jsonpath='{.data.config\.yaml}')
  grep -q '^group_sessions_per_user: false$' <<<"$config"
  grep -q '^  history_backfill: true$' <<<"$config"
  grep -q '^  thread_require_mention: true$' <<<"$config"
done

echo "[$NS] verifying explicit mention contracts are rendered"
leader_config=$(kubectl get configmap hermes-august-config -n "$NS" \
  -o jsonpath='{.data.config\.yaml}')
member_config=$(kubectl get configmap hermes-may-config -n "$NS" \
  -o jsonpath='{.data.config\.yaml}')
grep -Fq '<@${MAY_BOT_USER_ID}>' <<<"$leader_config"
grep -Fq '[TEAM run=<short-id> step=<n> TASK]' <<<"$leader_config"
grep -Fq '<@${AUGUST_BOT_USER_ID}>' <<<"$member_config"
grep -Fq '[TEAM run=<same-id> step=<same-n> RESULT]' <<<"$member_config"

echo "[$NS] verifying mention-only loop brakes on both Deployments"
for deployment in hermes-august hermes-may; do
  env_json=$(kubectl get deployment "$deployment" -n "$NS" \
    -o jsonpath='{.spec.template.spec.containers[0].env}')
  grep -q '"name":"DISCORD_ALLOW_BOTS","value":"mentions"' <<<"$env_json"
  grep -q '"name":"DISCORD_THREAD_REQUIRE_MENTION","value":"true"' <<<"$env_json"
  grep -q '"name":"DISCORD_REPLY_TO_MODE","value":"off"' <<<"$env_json"
  grep -q '"name":"DISCORD_ALLOW_MENTION_REPLIED_USER","value":"false"' \
    <<<"$env_json"
done

echo "[$NS] verifying there is no shared-file coordination plane"
if kubectl get deployment -n "$NS" -o yaml | grep -q 'team-workspace'; then
  echo "unexpected team-workspace volume found" >&2
  exit 1
fi
[ "$(kubectl get pvc -n "$NS" --no-headers | wc -l | tr -d ' ')" = "2" ]

kubectl get pods,pvc -n "$NS"
echo "[$NS] thread-native team structure passed; live Discord E2E remains manual"
