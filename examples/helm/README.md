# Installing with Helm

Two ways to install `hermes-agent-helm`: **from Git** (this repo) and **from an
OCI registry** (GitHub Packages / `ghcr.io`, the form indexed by Artifact Hub).

In every case, keep the API key out of the manifests — pass it at install time
or inject it from a pre-created Secret (see "Secrets").

---

## 1. From Git (local checkout)

Use the chart directly from a clone of this repo. Best for development and for
trying changes before publishing.

```bash
git clone https://github.com/jyje/hermes-helm
cd hermes-helm

# generic defaults (real OpenAI)
helm upgrade --install hermes-agent-helm ./charts/hermes-agent-helm \
  --namespace hermes-agent-helm --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# environment-specific (in-cluster LiteLLM)
helm upgrade --install hermes-agent-helm ./charts/hermes-agent-helm \
  --namespace hermes-agent-helm --create-namespace \
  -f charts/hermes-agent-helm/values.example.yaml \
  --set-string env.OPENAI_API_KEY='sk-<litellm-key>' --wait

helm test hermes-agent-helm -n hermes-agent-helm
```

> Release name `hermes-agent-helm` (== chart name) keeps resources clean
> (`hermes-agent-helm-0`, not `hermes-agent-helm-hermes-agent-helm-0`).

---

## 2. From an OCI registry (GitHub Packages, `ghcr.io`)

Once the chart is published (see "Publishing"), no clone is needed. This is the
form Artifact Hub lists.

```bash
# public chart: no login needed to pull
helm upgrade --install hermes-agent-helm \
  oci://ghcr.io/jyje/hermes-agent-helm --version 0.1.0 \
  --namespace hermes-agent-helm --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# with an env-specific values file (download or keep your own)
helm upgrade --install hermes-agent-helm \
  oci://ghcr.io/jyje/hermes-agent-helm --version 0.1.0 \
  --namespace hermes-agent-helm --create-namespace \
  -f my-values.yaml --set-string env.OPENAI_API_KEY='sk-...' --wait
```

Inspect before installing:

```bash
helm show values oci://ghcr.io/jyje/hermes-agent-helm --version 0.1.0
helm show readme oci://ghcr.io/jyje/hermes-agent-helm --version 0.1.0
```

If the package is private, log in first:

```bash
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin
```

---

## Upgrading an existing release across a chart rename

If you installed an earlier version of this chart under its old name (e.g.
`hermes-agent`) and are upgrading in place to `hermes-agent-helm`, a plain
`helm upgrade` can fail or — worse — create a **second, empty StatefulSet +
PVC** alongside your existing one. This happens because two things derive from
the chart name (`Chart.Name`):

1. **`fullname`** — if your release name doesn't already contain the new chart
   name, Helm computes `<release>-<chart>` (e.g. `hermes-agent-hermes-agent-helm`)
   instead of reusing the existing `<release>` name, so it creates brand-new
   resources (including a fresh, empty PVC) rather than upgrading the old ones.
2. **`volumeClaimTemplates[].metadata.labels["helm.sh/chart"]`** — this label
   includes the chart name+version and is part of a StatefulSet's *immutable*
   `volumeClaimTemplates`, so Kubernetes rejects the upgrade outright once the
   chart name changes.

Fix both by pinning the original name and recreating (not deleting) the
StatefulSet:

```bash
# 1) keep fullname/selectors stable (replace with YOUR existing release name)
RELEASE=hermes-agent
NS=hermes-agent

# 2) drop the StatefulSet object only — Pod and PVC (and your data) are kept
kubectl delete sts "$RELEASE" -n "$NS" --cascade=orphan

# 3) upgrade to the renamed chart, pinning nameOverride to the old name
helm upgrade --install "$RELEASE" ./charts/hermes-agent-helm -n "$NS" \
  -f charts/hermes-agent-helm/values.example.yaml \
  --set nameOverride="$RELEASE" \
  --set-string env.OPENAI_API_KEY='sk-<litellm-key>'

# 4) the Pod restarts once (new chart's StatefulSet adopts the old PVC); verify
kubectl rollout status statefulset/"$RELEASE" -n "$NS"
helm test "$RELEASE" -n "$NS"
```

Verified end-to-end on jyje's cluster: `hermes-agent-0` kept its original
`data-hermes-agent-0` PVC, `helm test` passed, and a live chat round-trip
through the in-cluster LiteLLM proxy returned a reply.

> If you don't need to preserve the existing release name/resources, skip
> `nameOverride` and just `helm uninstall` + reinstall fresh with the new chart
> name instead.

---

## Secrets (both methods)

Never bake the key into a committed values file. Either `--set-string` it at
install time, or pre-create a Secret and reference it via `extraEnvFrom` (the
later envFrom wins over the chart's placeholder):

```bash
kubectl create namespace hermes-agent-helm
kubectl create secret generic hermes-agent-helm-litellm -n hermes-agent-helm \
  --from-literal=OPENAI_API_KEY='sk-<litellm-key>'

helm upgrade --install hermes-agent-helm oci://ghcr.io/jyje/hermes-agent-helm \
  --version 0.1.0 -n hermes-agent-helm --create-namespace \
  --set 'extraEnvFrom[0].secretRef.name=hermes-agent-helm-litellm'
```

---

## Publishing to GitHub Packages (OCI) for Artifact Hub

> **CI owns the `.tgz` lifecycle.** Bumping `version` in `Chart.yaml` on `main`
> triggers `.github/workflows/release.yml`, which tags `vX.Y.Z`, writes release
> notes (git-cliff), and pushes to `oci://ghcr.io/<owner>` — the package
> is never committed. The commands below are the equivalent manual/local flow.

```bash
# 1) package (also runs docs + lint via the Makefile target)
make package                      # -> dist/hermes-agent-helm-0.1.0.tgz

# 2) login to ghcr (PAT needs write:packages)
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin

# 3) push as an OCI artifact
helm push dist/hermes-agent-helm-0.1.0.tgz oci://ghcr.io/jyje
#   -> ghcr.io/jyje/hermes-agent-helm:0.1.0

# (Makefile shortcut)
make push
```

Then make the `ghcr.io` package **public** (GitHub → Packages → package
settings) so Artifact Hub and users can pull anonymously.

### Register on Artifact Hub

1. artifacthub.io → Control Panel → Add → **Helm charts** repository.
2. URL: `oci://ghcr.io/jyje/hermes-agent-helm`
3. (Recommended) Verify ownership: push `artifacthub-repo.yml` (in this folder)
   to the same OCI path so Artifact Hub can confirm you own the repo. The
   `artifacthub.io/*` annotations already in `Chart.yaml` populate the listing.

> Chart version vs app version: bump `version` in `Chart.yaml` for chart
> changes; `appVersion` tracks the Hermes image tag (date-based, e.g.
> `v2026.6.5`).
