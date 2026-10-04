#!/usr/bin/env bash
# dashboard-ingress scenario: reach the management dashboard through a real
# ingress-nginx controller in this scenario's own ephemeral kind cluster and
# check what an operator depends on: the pod only turns Ready once the
# dashboard listens (readiness probe), the auth gate holds, sign-in works,
# and behind a TLS-terminating Ingress the session cookies are `Secure` only
# when the controller is a trusted proxy.
#
# No DNS and no public certificate are needed: the host is a reserved `.test`
# name resolved with `curl --resolve`, the certificate is self-signed, and the
# requests come from a pod inside the cluster so the Host header carries no
# port. Do not use a `*.localhost` host: upstream treats loopback hosts as a
# development setup and never sets `Secure` there, which would hide the very
# behavior this scenario checks. Real DNS and Let's Encrypt issuance are out
# of scope here and are verified by hand on a real cluster.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

INGRESS_NGINX_REF="${INGRESS_NGINX_REF:-controller-v1.15.1}"
HOST="hermes.ci.test"
USER_NAME="admin"
PASSWORD="$(openssl rand -hex 16)"
SESSION_SECRET="$(openssl rand -base64 32)"
echo "::add-mask::$PASSWORD"
echo "::add-mask::$SESSION_SECRET"

diagnostics() {
  echo "::group::diagnostics"
  kubectl get pods,svc,ingress -A -o wide || true
  kubectl -n ingress-nginx logs -l app.kubernetes.io/component=controller --tail=60 || true
  kubectl logs -n "$NS" -l app.kubernetes.io/name=hermes-agent -c hermes-agent --tail=80 || true
  echo "::endgroup::"
}
set -o errtrace
trap diagnostics ERR

echo "[$NS] installing ingress-nginx $INGRESS_NGINX_REF"
kubectl apply -f "https://raw.githubusercontent.com/kubernetes/ingress-nginx/${INGRESS_NGINX_REF}/deploy/static/provider/baremetal/deploy.yaml"
# The admission webhook must be serving before an Ingress can be created, and
# neither the controller's Ready condition nor its Jobs say so reliably (the
# Jobs are removed as soon as they finish, and Ready can precede the webhook
# listener). Ask the webhook itself: a server-side dry-run of an Ingress goes
# through it, so it succeeds only once the webhook answers.
kubectl -n ingress-nginx wait --for=condition=Ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
webhook_ready=false
for _ in $(seq 1 90); do
  if kubectl apply --dry-run=server -f - >/dev/null 2>&1 <<'MANIFEST'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webhook-probe
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: webhook-probe.ci.test
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: webhook-probe
                port:
                  number: 80
MANIFEST
  then webhook_ready=true; break; fi
  sleep 2
done
[ "$webhook_ready" = true ] || { echo "::error::[$NS] ingress-nginx admission webhook never started answering"; exit 1; }
controller_ip="$(kubectl -n ingress-nginx get pod -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].status.podIP}')"
controller_svc="$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.spec.clusterIP}')"
echo "[$NS] controller pod $controller_ip, Service $controller_svc"

kubectl create namespace "$NS" 2>/dev/null || true
tmp="$(mktemp -d)"
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=$HOST" -addext "subjectAltName=DNS:$HOST" \
  -keyout "$tmp/tls.key" -out "$tmp/tls.crt" 2>/dev/null
kubectl -n "$NS" create secret tls dashboard-tls --cert="$tmp/tls.crt" --key="$tmp/tls.key"

echo "[$NS] installing the chart with the dashboard behind the Ingress (readiness probe gates --wait)"
# trustedProxies is the exact controller pod: the dashboard sees the controller,
# not the client, as its peer.
install_release \
  --set dashboard.enabled=true \
  --set "dashboard.trustedProxies[0]=${controller_ip}/32" \
  --set-string env.HERMES_DASHBOARD_BASIC_AUTH_USERNAME="$USER_NAME" \
  --set-string env.HERMES_DASHBOARD_BASIC_AUTH_PASSWORD="$PASSWORD" \
  --set-string env.HERMES_DASHBOARD_BASIC_AUTH_SECRET="$SESSION_SECRET" \
  --set service.enabled=true \
  --set ingress.enabled=true --set ingress.className=nginx \
  --set "ingress.hosts[0].host=$HOST" \
  --set "ingress.hosts[0].paths[0].path=/" --set "ingress.hosts[0].paths[0].pathType=Prefix" \
  --set "ingress.tls[0].secretName=dashboard-tls" --set "ingress.tls[0].hosts[0]=$HOST"

kubectl run curl -n "$NS" --image=curlimages/curl:8.10.1 --restart=Never --command -- sleep 3600
kubectl wait -n "$NS" --for=condition=Ready pod/curl --timeout=120s

# curl_in <curl args...>: runs curl in the cluster, resolving $HOST to the controller.
curl_in() {
  kubectl exec -n "$NS" curl -- curl -sk -m 20 --resolve "$HOST:443:$controller_svc" "$@"
}
status_of() { curl_in -o /dev/null -w '%{http_code}' "$@"; }
expect() { # expect <label> <actual> <expected>
  if [ "$2" != "$3" ]; then
    echo "::error::[$NS] $1: expected $3, got $2"; return 1
  fi
  echo "[$NS] ok: $1 -> $2"
}
login() { # login <password> <cookie jar in the curl pod>; prints the response headers
  curl_in -D - -o /dev/null -c "$2" -H 'Content-Type: application/json' \
    -d "{\"provider\":\"basic\",\"username\":\"$USER_NAME\",\"password\":\"$1\",\"next\":\"/\"}" \
    "https://$HOST/auth/password-login"
}
cookies() { tr -d '\r' | grep -i '^set-cookie:' || true; }

echo "[$NS] --- the Ingress answers right after Ready (no 502/503 window)"
expect "GET / redirects to sign-in" "$(status_of "https://$HOST/")" 302
curl_in -D - -o /dev/null "https://$HOST/" | tr -d '\r' | grep -i '^location: /login' >/dev/null
expect "unauthenticated GET /api/env is rejected" "$(status_of "https://$HOST/api/env")" 401

echo "[$NS] --- a wrong password is rejected and sets no cookie"
bad="$(login "not-the-password" /tmp/jar-bad)"
if [ "$(printf '%s\n' "$bad" | head -1 | tr -d '\r' | awk '{print $2}')" = 200 ]; then
  echo "::error::[$NS] wrong password was accepted"; exit 1
fi
expect "no cookie for a wrong password" "$(printf '%s\n' "$bad" | cookies | wc -l | tr -d ' ')" 0

echo "[$NS] --- the right password signs in; cookies are Secure behind the trusted TLS proxy"
good="$(login "$PASSWORD" /tmp/jar-good)"
expect "sign-in succeeds" "$(printf '%s\n' "$good" | head -1 | tr -d '\r' | awk '{print $2}')" 200
sess="$(printf '%s\n' "$good" | cookies | grep -i '__Host-hermes_session_at=' || true)"
[ -n "$sess" ] || { echo "::error::[$NS] no __Host- session cookie behind a trusted TLS proxy"; exit 1; }
printf '%s' "$sess" | grep -qi '; *secure' || { echo "::error::[$NS] session cookie is not Secure"; exit 1; }
printf '%s' "$sess" | grep -qi '; *httponly' || { echo "::error::[$NS] session cookie is not HttpOnly"; exit 1; }
expect "authenticated GET /api/env" "$(status_of -b /tmp/jar-good "https://$HOST/api/env")" 200

echo "[$NS] --- control: without a trusted proxy the same sign-in yields non-Secure cookies"
helm upgrade hermes-agent charts/hermes-agent --namespace "$NS" --reuse-values \
  --set bootstrap.overwrite=true --set-json 'dashboard.trustedProxies=[]' --wait --timeout 5m
# The new pod is Ready, but the controller needs a moment to move its upstream
# over from the old pod, during which it answers 502/503/504. Only that window
# is retried; any other status is the real answer.
untrusted=""
for _ in $(seq 1 30); do
  untrusted="$(login "$PASSWORD" /tmp/jar-untrusted)"
  case "$(printf '%s\n' "$untrusted" | head -1 | tr -d '\r' | awk '{print $2}')" in
    502|503|504) sleep 2 ;;
    *) break ;;
  esac
done
expect "sign-in still succeeds" "$(printf '%s\n' "$untrusted" | head -1 | tr -d '\r' | awk '{print $2}')" 200
if printf '%s\n' "$untrusted" | cookies | grep -qi '; *secure'; then
  # Informational: upstream may one day mark the cookie Secure on its own. The
  # chart docs say the opposite today, so flag it for a docs update.
  echo "::warning::[$NS] cookies are Secure without trusted_proxies: update the dashboard docs (#321)"
else
  echo "[$NS] ok: cookies are not Secure without trusted_proxies (the documented reason to set dashboard.trustedProxies)"
fi

echo "[$NS] dashboard-ingress scenario passed"
