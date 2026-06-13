# Installing with Helm

Two ways to install `hermes-agent`: **from Git** (this repo) and **from an OCI
registry** (GitHub Packages / `ghcr.io`, the form indexed by Artifact Hub).

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
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# environment-specific (in-cluster LiteLLM)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values.example.yaml \
  --set-string env.OPENAI_API_KEY='sk-<litellm-key>' --wait

helm test hermes-agent -n hermes-agent
```

> Release name `hermes-agent` (== chart name) keeps resources clean
> (`hermes-agent-0`, not `hermes-hermes-agent-0`).

---

## 2. From an OCI registry (GitHub Packages, `ghcr.io`)

Once the chart is published (see "Publishing"), no clone is needed. This is the
form Artifact Hub lists.

```bash
# public chart: no login needed to pull
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/charts/hermes-agent --version 0.1.0 \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# with an env-specific values file (download or keep your own)
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/charts/hermes-agent --version 0.1.0 \
  --namespace hermes-agent --create-namespace \
  -f my-values.yaml --set-string env.OPENAI_API_KEY='sk-...' --wait
```

Inspect before installing:

```bash
helm show values oci://ghcr.io/jyje/charts/hermes-agent --version 0.1.0
helm show readme oci://ghcr.io/jyje/charts/hermes-agent --version 0.1.0
```

If the package is private, log in first:

```bash
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin
```

---

## Secrets (both methods)

Never bake the key into a committed values file. Either `--set-string` it at
install time, or pre-create a Secret and reference it via `extraEnvFrom` (the
later envFrom wins over the chart's placeholder):

```bash
kubectl create namespace hermes-agent
kubectl create secret generic hermes-agent-litellm -n hermes-agent \
  --from-literal=OPENAI_API_KEY='sk-<litellm-key>'

helm upgrade --install hermes-agent oci://ghcr.io/jyje/charts/hermes-agent \
  --version 0.1.0 -n hermes-agent --create-namespace \
  --set 'extraEnvFrom[0].secretRef.name=hermes-agent-litellm'
```

---

## Publishing to GitHub Packages (OCI) for Artifact Hub

> **CI owns the `.tgz` lifecycle.** Bumping `version` in `Chart.yaml` on `main`
> triggers `.github/workflows/release.yml`, which tags `vX.Y.Z`, writes release
> notes (git-cliff), and pushes to `oci://ghcr.io/<owner>/charts` — the package
> is never committed. The commands below are the equivalent manual/local flow.

```bash
# 1) package (also runs docs + lint via the Makefile target)
make package                      # -> dist/hermes-agent-0.1.0.tgz

# 2) login to ghcr (PAT needs write:packages)
echo "$GITHUB_TOKEN" | helm registry login ghcr.io -u jyje --password-stdin

# 3) push as an OCI artifact
helm push dist/hermes-agent-0.1.0.tgz oci://ghcr.io/jyje/charts
#   -> ghcr.io/jyje/charts/hermes-agent:0.1.0

# (Makefile shortcut)
make push
```

Then make the `ghcr.io` package **public** (GitHub → Packages → package
settings) so Artifact Hub and users can pull anonymously.

### Register on Artifact Hub

1. artifacthub.io → Control Panel → Add → **Helm charts** repository.
2. URL: `oci://ghcr.io/jyje/charts/hermes-agent`
3. (Recommended) Verify ownership: push `artifacthub-repo.yml` (in this folder)
   to the same OCI path so Artifact Hub can confirm you own the repo. The
   `artifacthub.io/*` annotations already in `Chart.yaml` populate the listing.

> Chart version vs app version: bump `version` in `Chart.yaml` for chart
> changes; `appVersion` tracks the Hermes image tag (date-based, e.g.
> `v2026.6.5`).
