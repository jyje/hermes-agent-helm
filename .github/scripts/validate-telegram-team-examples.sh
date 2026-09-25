#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
CHART="$ROOT/charts/hermes-agent"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

assert_env() {
  local rendered=$1 name=$2 value=$3
  yq -e "select(.kind == \"Deployment\").spec.template.spec.containers[] | select(.name == \"hermes-agent\").env[] | select(.name == \"$name\" and .value == \"$value\")" "$rendered" >/dev/null
}

assert_telegram_team() {
  local name=$1 values=$2
  local full="$TMP/$name.yaml" cm="$TMP/$name-config.yaml"
  helm template "$name" "$CHART" -f "$values" > "$full"
  helm template "$name" "$CHART" -f "$values" --show-only templates/configmap.yaml > "$cm"

  yq -e 'select(.kind == "Deployment").spec.template.spec.containers[0].env | length > 0' "$full" >/dev/null
  assert_env "$full" TELEGRAM_ALLOW_BOTS mentions
  assert_env "$full" TELEGRAM_BOTS_REQUIRE_MENTION true
  assert_env "$full" TELEGRAM_REQUIRE_MENTION true
  assert_env "$full" TELEGRAM_REPLY_TO_MODE off

  local config
  config=$(yq -r '.data."config.yaml"' "$cm")
  yq -e '.group_sessions_per_user == false' <<<"$config" >/dev/null
  yq -e '.telegram.exclusive_bot_mentions == true' <<<"$config" >/dev/null
  yq -e '.telegram.mention_patterns | length == 0' <<<"$config" >/dev/null
}

echo "[telegram-team] validating the shared assistant example"
helm template telegram-assistant "$CHART" \
  -f "$CHART/values-telegram-team-assistant.yaml" > "$TMP/telegram-assistant.yaml"
helm template telegram-assistant "$CHART" \
  -f "$CHART/values-telegram-team-assistant.yaml" \
  --show-only templates/configmap.yaml > "$TMP/telegram-assistant-config.yaml"
config=$(yq -r '.data."config.yaml"' "$TMP/telegram-assistant-config.yaml")
yq -e '.group_sessions_per_user == true and .telegram.require_mention == true' <<<"$config" >/dev/null
assert_env "$TMP/telegram-assistant.yaml" TELEGRAM_ALLOWED_USERS '111111111,222222222'
assert_env "$TMP/telegram-assistant.yaml" TELEGRAM_GROUP_ALLOWED_CHATS '-1001234567890'

echo "[telegram-team] validating leader and member values examples"
assert_telegram_team telegram-leader "$CHART/values-telegram-team-leader.yaml"
assert_telegram_team telegram-member "$CHART/values-telegram-team-member.yaml"

echo "[telegram-team] rejecting operator overrides of enforced routing gates"
if helm template invalid-telegram-team "$CHART" \
  -f "$CHART/values-telegram-team-leader.yaml" \
  --set-string 'extraEnv[0].name=TELEGRAM_ALLOW_BOTS' \
  --set-string 'extraEnv[0].value=all' > /dev/null 2>&1; then
  echo "::error::team mode must reject a conflicting TELEGRAM_ALLOW_BOTS override"
  exit 1
fi

echo "[telegram-team] preserving the existing Discord team contract"
helm template discord-team "$CHART" \
  -f "$CHART/values-team-leader.yaml" > "$TMP/discord-team.yaml"
helm template discord-team "$CHART" \
  -f "$CHART/values-team-leader.yaml" \
  --show-only templates/configmap.yaml > "$TMP/discord-team-config.yaml"
assert_env "$TMP/discord-team.yaml" DISCORD_ALLOW_BOTS mentions
assert_env "$TMP/discord-team.yaml" DISCORD_THREAD_REQUIRE_MENTION true
assert_env "$TMP/discord-team.yaml" DISCORD_REPLY_TO_MODE off
assert_env "$TMP/discord-team.yaml" DISCORD_ALLOW_MENTION_REPLIED_USER false
config=$(yq -r '.data."config.yaml"' "$TMP/discord-team-config.yaml")
yq -e '.group_sessions_per_user == false and .discord.thread_require_mention == true and .discord.history_backfill == true' <<<"$config" >/dev/null

echo "[telegram-team] expanding the ApplicationSet template for each release"
APPSET="$ROOT/examples/argocd/hermes-team-telegram.yaml"

render_app() {
  local identity=$1 role=$2 profile=$3 owns=$4 secret=$5
  local appset values rendered cm
  appset="$TMP/$identity-appset.yaml"
  values="$TMP/$identity-values.yaml"
  rendered="$TMP/$identity-rendered.yaml"
  cm="$TMP/$identity-config.yaml"

  sed \
    -e "s/{{ .name }}/$identity/g" \
    -e "s/{{ .teamRole }}/$role/g" \
    -e "s/{{ .valuesProfile }}/$profile/g" \
    -e "s/{{ .ownsSharedResources }}/$owns/g" \
    -e "s/{{ .botSecret }}/$secret/g" \
    "$APPSET" > "$appset"

  yq -e '.spec.generators[0].list.elements | length == 3' "$appset" >/dev/null
  yq -r '.spec.template.spec.source.helm.values' "$appset" > "$values"
  yq -e ".team.identity == \"$identity\" and .team.role == \"$role\" and .team.platform == \"telegram\"" "$values" >/dev/null
  yq -e ".team.skill.create == $owns and .team.sharedVolume.create == $owns" "$values" >/dev/null
  yq -e ".extraEnvFrom[1].secretRef.name == \"$secret\"" "$values" >/dev/null

  helm template "hermes-$identity" "$CHART" \
    -f "$CHART/values-telegram-team-$profile.yaml" \
    -f "$values" > "$rendered"
  helm template "hermes-$identity" "$CHART" \
    -f "$CHART/values-telegram-team-$profile.yaml" \
    -f "$values" --show-only templates/configmap.yaml > "$cm"
  assert_env "$rendered" TELEGRAM_ALLOW_BOTS mentions
  assert_env "$rendered" TELEGRAM_BOTS_REQUIRE_MENTION true
  yq -e '.data."config.yaml" | from_yaml | .group_sessions_per_user == false' "$cm" >/dev/null
}

render_app august leader leader true hermes-august-telegram-secrets
render_app may member member false hermes-may-telegram-secrets
render_app march member member false hermes-march-telegram-secrets

echo "[telegram-team] values and ApplicationSet render contracts passed"
