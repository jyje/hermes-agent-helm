#!/usr/bin/env bash
# team scenario: install a chart-native leader and one member, then verify the
# leader-created shared roster skill, safe Discord settings, and shared RWX
# knowledge PVC.
# This is intentionally structural: CI has no three bot identities and must not
# claim a live bot-to-bot completion proof.
set -euo pipefail

NS="${NS:-test-hermes-chart}"

team_channel_id="900000000000000000"
trusted_user_id="911111111111111111"
may_bot_id="922222222222222222"
march_bot_id="933333333333333333"
august_bot_id="944444444444444444"
knowledge_pv="hermes-team-knowledge-$NS"

kubectl get namespace "$NS" >/dev/null 2>&1 || kubectl create namespace "$NS"
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: $knowledge_pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: team-knowledge-ci
  hostPath:
    path: /tmp/$knowledge_pv
    type: DirectoryOrCreate
EOF

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
  --set-string "extraEnv[0].value=$team_channel_id" \
  --set-string "extraEnv[1].value=$trusted_user_id" \
  --set-string "extraEnv[2].value=$may_bot_id" \
  --set-string "extraEnv[3].value=$march_bot_id" \
  --set-string "extraEnv[4].value=$august_bot_id" \
  --set-string team.sharedVolume.storageClass=team-knowledge-ci \
  --set-string team.sharedVolume.size=1Gi \
  "${common_args[@]}"

helm upgrade --install hermes-may charts/hermes-agent \
  -f charts/hermes-agent/values-team-member.yaml \
  --set-string "extraEnv[0].value=$team_channel_id" \
  --set-string "extraEnv[1].value=$trusted_user_id" \
  --set-string "extraEnv[2].value=$august_bot_id" \
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
grep -Fq '<@${AUGUST_BOT_USER_ID}>' <<<"$member_config"

team_skill=$(kubectl get configmap hermes-team-skill -n "$NS" \
  -o jsonpath='{.data.SKILL\.md}')
grep -Fq '[TEAM run=<short-id> step=<n> TASK]' <<<"$team_skill"
grep -Fq '[TEAM run=<same-id> step=<same-n> RESULT]' <<<"$team_skill"
grep -Fq "Discord's typing indicator is display state" <<<"$leader_config"
grep -Fq 'Never infer that a member is online' <<<"$team_skill"
[ "$(kubectl get configmap -n "$NS" -o name | grep -c '/hermes-team-skill$')" = "1" ]
if kubectl get configmap hermes-may-team-skill -n "$NS" >/dev/null 2>&1; then
  echo "member unexpectedly created a private team skill ConfigMap" >&2
  exit 1
fi

echo "[$NS] verifying the injected skill toolset remains enabled"
for config in "$leader_config" "$member_config"; do
  if grep -Eq '^[[:space:]]+- skills$' <<<"$config"; then
    echo "skills unexpectedly disabled" >&2
    exit 1
  fi
done

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

echo "[$NS] verifying Argo CD positional extraEnv mappings"
assert_env() {
  local deployment="$1"
  local name="$2"
  local expected="$3"
  local actual
  actual=$(kubectl get deployment "$deployment" -n "$NS" \
    -o "jsonpath={.spec.template.spec.containers[0].env[?(@.name==\"$name\")].value}")
  if [ "$actual" != "$expected" ]; then
    echo "$deployment: expected $name=$expected, got $actual" >&2
    exit 1
  fi
}

assert_env hermes-august DISCORD_HOME_CHANNEL "$team_channel_id"
assert_env hermes-august DISCORD_ALLOWED_USERS "$trusted_user_id"
assert_env hermes-august MAY_BOT_USER_ID "$may_bot_id"
assert_env hermes-august MARCH_BOT_USER_ID "$march_bot_id"
assert_env hermes-august AUGUST_BOT_USER_ID "$august_bot_id"
assert_env hermes-may DISCORD_HOME_CHANNEL "$team_channel_id"
assert_env hermes-may DISCORD_ALLOWED_USERS "$trusted_user_id"
assert_env hermes-may AUGUST_BOT_USER_ID "$august_bot_id"

echo "[$NS] verifying the chart-owned shared PVC and role-specific mounts"
[ "$(kubectl get pvc hermes-team-knowledge -n "$NS" -o jsonpath='{.metadata.annotations.helm\.sh/resource-policy}')" = "keep" ]
leader_claim=$(kubectl get deployment hermes-august -n "$NS" \
  -o 'jsonpath={.spec.template.spec.volumes[?(@.name=="team-shared")].persistentVolumeClaim.claimName}')
member_claim=$(kubectl get deployment hermes-may -n "$NS" \
  -o 'jsonpath={.spec.template.spec.volumes[?(@.name=="team-shared")].persistentVolumeClaim.claimName}')
[ "$leader_claim" = "hermes-team-knowledge" ]
[ "$member_claim" = "hermes-team-knowledge" ]

member_read_only=$(kubectl get deployment hermes-may -n "$NS" \
  -o 'jsonpath={.spec.template.spec.containers[0].volumeMounts[?(@.name=="team-shared")].readOnly}')
[ "$member_read_only" = "true" ]

for deployment in hermes-august hermes-may; do
  skill_configmap=$(kubectl get deployment "$deployment" -n "$NS" \
    -o 'jsonpath={.spec.template.spec.volumes[?(@.name=="team-skill")].configMap.name}')
  [ "$skill_configmap" = "hermes-team-skill" ]
  skill_read_only=$(kubectl get deployment "$deployment" -n "$NS" \
    -o 'jsonpath={.spec.template.spec.containers[0].volumeMounts[?(@.name=="team-skill")].readOnly}')
  [ "$skill_read_only" = "true" ]
  kubectl exec deployment/"$deployment" -n "$NS" -- \
    test -f /opt/data/skills/hermes-team-roster/SKILL.md
done

kubectl exec deployment/hermes-august -n "$NS" -- \
  sh -c 'printf "%s\n" "ci-shared-knowledge-ok" > /opt/data/team-knowledge/ci-probe.txt'
[ "$(kubectl exec deployment/hermes-may -n "$NS" -- \
  cat /opt/data/team-knowledge/ci-probe.txt)" = "ci-shared-knowledge-ok" ]
if kubectl exec deployment/hermes-may -n "$NS" -- \
  sh -c 'printf "%s\n" "unexpected" > /opt/data/team-knowledge/member-write.txt'; then
  echo "member unexpectedly wrote to the read-only knowledge mount" >&2
  exit 1
fi

echo "[$NS] verifying there is no shared-file task coordination plane"
if kubectl get deployment -n "$NS" -o yaml | grep -q 'team-workspace'; then
  echo "unexpected team-workspace volume found" >&2
  exit 1
fi
[ "$(kubectl get pvc -n "$NS" --no-headers | wc -l | tr -d ' ')" = "3" ]

kubectl get pods,pvc -n "$NS"
echo "[$NS] thread-native team structure passed; live Discord E2E remains manual"
