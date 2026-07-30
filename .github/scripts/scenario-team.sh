#!/usr/bin/env bash
# team scenario: install a leader and one member from the thread-native values
# files and verify the Kubernetes/runtime configuration that makes a visible
# Discord mention loop possible. This is intentionally structural: CI has no
# three bot identities and must not claim a live bot-to-bot completion proof.
set -euo pipefail

NS="${NS:-test-hermes-chart}"

# These values intentionally mirror the positional extraEnv overrides in
# examples/argocd/hermes-team.yaml. If either values file reorders its list,
# the runtime assertions below fail instead of allowing silent index drift.
team_channel_id="900000000000000000"
trusted_user_id="911111111111111111"
may_bot_id="922222222222222222"
march_bot_id="933333333333333333"
august_bot_id="944444444444444444"
member_name="may-ci"
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
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hermes-team-knowledge
  namespace: $NS
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: team-knowledge-ci
  volumeName: $knowledge_pv
  resources:
    requests:
      storage: 1Gi
---
apiVersion: batch/v1
kind: Job
metadata:
  name: init-team-knowledge
  namespace: $NS
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: permissions
          image: busybox:1.37
          command: ["sh", "-c", "chown -R 10000:10000 /knowledge"]
          volumeMounts:
            - name: team-knowledge
              mountPath: /knowledge
      volumes:
        - name: team-knowledge
          persistentVolumeClaim:
            claimName: hermes-team-knowledge
EOF
kubectl wait --for=condition=complete job/init-team-knowledge -n "$NS" \
  --timeout=2m

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
  --set-string "extraEnv[6].value=$may_bot_id" \
  --set-string "extraEnv[7].value=$march_bot_id" \
  --set-string "extraEnv[8].value=$august_bot_id" \
  "${common_args[@]}"

helm upgrade --install hermes-may charts/hermes-agent \
  -f charts/hermes-agent/values-team-member.yaml \
  --set-string "extraEnv[0].value=$team_channel_id" \
  --set-string "extraEnv[1].value=$trusted_user_id" \
  --set-string "extraEnv[6].value=$member_name" \
  --set-string "extraEnv[7].value=$august_bot_id" \
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

echo "[$NS] verifying local file and memory tools remain enabled"
for config in "$leader_config" "$member_config"; do
  if grep -Eq '^[[:space:]]+- (file|memory)$' <<<"$config"; then
    echo "file or memory unexpectedly disabled" >&2
    exit 1
  fi
  grep -Fq 'NEVER use a hook, watcher, scheduler,' <<<"$config"
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
assert_env hermes-august TEAM_KNOWLEDGE_ROOT "/opt/data/team-knowledge"
assert_env hermes-may DISCORD_HOME_CHANNEL "$team_channel_id"
assert_env hermes-may DISCORD_ALLOWED_USERS "$trusted_user_id"
assert_env hermes-may TEAM_MEMBER_NAME "$member_name"
assert_env hermes-may AUGUST_BOT_USER_ID "$august_bot_id"
assert_env hermes-may TEAM_KNOWLEDGE_ROOT "/opt/data/team-knowledge"

echo "[$NS] verifying the shared PVC is knowledge-only and single-writer"
leader_claim=$(kubectl get deployment hermes-august -n "$NS" \
  -o 'jsonpath={.spec.template.spec.volumes[?(@.name=="team-knowledge")].persistentVolumeClaim.claimName}')
member_claim=$(kubectl get deployment hermes-may -n "$NS" \
  -o 'jsonpath={.spec.template.spec.volumes[?(@.name=="team-knowledge")].persistentVolumeClaim.claimName}')
[ "$leader_claim" = "hermes-team-knowledge" ]
[ "$member_claim" = "hermes-team-knowledge" ]

member_read_only=$(kubectl get deployment hermes-may -n "$NS" \
  -o 'jsonpath={.spec.template.spec.containers[0].volumeMounts[?(@.name=="team-knowledge")].readOnly}')
[ "$member_read_only" = "true" ]

kubectl exec deployment/hermes-august -n "$NS" -- \
  sh -c 'printf "%s\n" "ci-shared-knowledge-ok" > /opt/data/team-knowledge/ci-probe.txt'
[ "$(kubectl exec deployment/hermes-may -n "$NS" -- \
  cat /opt/data/team-knowledge/ci-probe.txt)" = "ci-shared-knowledge-ok" ]
if kubectl exec deployment/hermes-may -n "$NS" -- \
  sh -c 'printf "%s\n" "unexpected" > /opt/data/team-knowledge/member-write.txt'; then
  echo "member unexpectedly wrote to the read-only knowledge mount" >&2
  exit 1
fi

echo "[$NS] verifying there is no shared-file coordination plane"
if kubectl get deployment -n "$NS" -o yaml | grep -q 'team-workspace'; then
  echo "unexpected team-workspace volume found" >&2
  exit 1
fi
[ "$(kubectl get pvc -n "$NS" --no-headers | wc -l | tr -d ' ')" = "3" ]

kubectl get pods,pvc -n "$NS"
echo "[$NS] thread-native team structure passed; live Discord E2E remains manual"
