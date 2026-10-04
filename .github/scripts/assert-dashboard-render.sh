#!/usr/bin/env bash
# Render-only assertions for the `dashboard` values block (#319, #320, #323).
# No cluster and no secrets, so it is safe for fork PRs. Run it locally with:
#   bash .github/scripts/assert-dashboard-render.sh
set -euo pipefail

chart=charts/hermes-agent
base=(--set-string env.OPENAI_API_KEY=sk-test)
basic=(--set dashboard.enabled=true
  --set-string env.HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
  --set-string env.HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=pw)
ingress=(--set service.enabled=true --set ingress.enabled=true
  --set 'ingress.hosts[0].host=hermes.example.com'
  --set 'ingress.hosts[0].paths[0].path=/' --set 'ingress.hosts[0].paths[0].pathType=Prefix')

render() { helm template t "$chart" "${base[@]}" "$@"; }
container() { yq -e 'select(.kind == "Deployment").spec.template.spec.containers[0]'; }
config() { yq -e 'select(.kind == "ConfigMap").data."config.yaml"' | yq -e "$1" -; }
fail() { echo "::error::dashboard render: $*"; exit 1; }

echo "default render is unchanged while the dashboard is off"
off="$(render)"
printf '%s\n' "$off" | grep -q 'HERMES_DASHBOARD' && fail "HERMES_DASHBOARD rendered with dashboard.enabled=false"
printf '%s\n' "$off" | grep -q 'readinessProbe' && fail "readinessProbe rendered with dashboard.enabled=false"

echo "enabling the dashboard without credentials fails for basic, oauth and oidc"
for provider in basic oauth oidc; do
  if render --set dashboard.enabled=true --set dashboard.auth.provider="$provider" >/dev/null 2>&1; then
    fail "auth.provider=$provider rendered without credentials"
  fi
done

echo "credentials satisfy each provider, and external skips the check"
render "${basic[@]}" >/dev/null
render --set dashboard.enabled=true --set dashboard.auth.provider=oauth \
  --set-string env.HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:1 >/dev/null
render --set dashboard.enabled=true --set dashboard.auth.provider=oidc \
  --set-string env.HERMES_DASHBOARD_OIDC_ISSUER=https://issuer.example \
  --set-string env.HERMES_DASHBOARD_OIDC_CLIENT_ID=client >/dev/null
render --set dashboard.enabled=true --set dashboard.auth.provider=external >/dev/null
echo "oauth and oidc keys under config.dashboard.oauth satisfy the check"
render --set dashboard.enabled=true --set dashboard.auth.provider=oauth \
  --set-string config.dashboard.oauth.client_id=agent:1 >/dev/null
render --set dashboard.enabled=true --set dashboard.auth.provider=oidc \
  --set-string config.dashboard.oauth.self_hosted.issuer=https://issuer.example \
  --set-string config.dashboard.oauth.self_hosted.client_id=client >/dev/null

echo "HERMES_DASHBOARD=1 is set"
render "${basic[@]}" | container \
  | yq -e '.env[] | select(.name == "HERMES_DASHBOARD") | .value == "1"' | grep -q true

echo "public_url is derived from the Ingress host (https only with TLS)"
render "${basic[@]}" "${ingress[@]}" | config '.dashboard.public_url == "http://hermes.example.com"' | grep -q true
render "${basic[@]}" "${ingress[@]}" --set 'ingress.tls[0].secretName=tls' \
  | config '.dashboard.public_url == "https://hermes.example.com"' | grep -q true

echo "an explicit publicUrl and a config.dashboard value win over the derived one"
render "${basic[@]}" "${ingress[@]}" --set-string dashboard.publicUrl=https://explicit.example \
  | config '.dashboard.public_url == "https://explicit.example"' | grep -q true
render "${basic[@]}" "${ingress[@]}" --set-string config.dashboard.public_url=https://cfg.example \
  | config '.dashboard.public_url == "https://cfg.example"' | grep -q true

echo "trustedProxies renders into config.dashboard.trusted_proxies"
render "${basic[@]}" --set 'dashboard.trustedProxies[0]=10.244.0.0/16' \
  | config '.dashboard.trusted_proxies[0] == "10.244.0.0/16"' | grep -q true

echo "readiness probe: default, overridden, disabled"
render "${basic[@]}" | container \
  | yq -e '.readinessProbe.tcpSocket.port == 9119' | grep -q true
render "${basic[@]}" --set probes.readiness.httpGet.path=/x --set probes.readiness.httpGet.port=9119 | container \
  | yq -e '.readinessProbe.httpGet.path == "/x" and (.readinessProbe.tcpSocket == null)' | grep -q true
render "${basic[@]}" --set dashboard.readinessProbe.enabled=false | container \
  | yq -e '.readinessProbe == null' | grep -q true

echo "release notes warn about a missing trusted proxy behind HTTPS only"
notes() { helm install t "$chart" --dry-run=client "${base[@]}" "$@" 2>&1 | sed -n '/^NOTES:/,$p'; }
tls=(--set 'ingress.tls[0].secretName=tls')
notes "${basic[@]}" "${ingress[@]}" "${tls[@]}" | grep -q 'no trusted proxy is set' \
  || fail "no warning for https without a trusted proxy"
notes "${basic[@]}" "${ingress[@]}" "${tls[@]}" --set 'dashboard.trustedProxies[0]=10.244.0.0/16' | grep -q 'no trusted proxy' \
  && fail "warning despite dashboard.trustedProxies"
notes "${basic[@]}" "${ingress[@]}" "${tls[@]}" --set 'config.dashboard.trusted_proxies[0]=10.244.0.0/16' | grep -q 'no trusted proxy' \
  && fail "warning despite config.dashboard.trusted_proxies"
notes "${basic[@]}" "${ingress[@]}" | grep -q 'no trusted proxy' && fail "warning for plain http"
notes | grep -q 'no trusted proxy' && fail "warning while the dashboard is off"

echo "dashboard render assertions passed"
