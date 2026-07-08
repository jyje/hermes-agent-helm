CHART := charts/hermes-agent
CHART_NAME := hermes-agent
NS    := hermes-agent
RELEASE := hermes-agent
VALUES := $(CHART)/values-openai.yaml
OCI_REGISTRY ?= oci://ghcr.io/jyje/hermes-agent-helm

CHART_VERSION = $(shell grep -E '^version:' $(CHART)/Chart.yaml | awk '{print $$2}' | tr -d '"')

.PHONY: docs lint template install test uninstall package push changelog propose help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

docs: ## Regenerate chart README via helm-docs (from README.md.gotmpl)
	helm-docs --chart-search-root=charts --template-files=README.md.gotmpl --badge-style=flat

lint: ## Lint the chart
	helm lint $(CHART) --set env.OPENAI_API_KEY=sk-test

template: ## Render manifests to stdout
	helm template $(RELEASE) $(CHART) --namespace $(NS) --set-string env.OPENAI_API_KEY=sk-test

install: ## Install/upgrade into the cluster (override env.OPENAI_API_KEY=...)
	helm upgrade --install $(RELEASE) $(CHART) --namespace $(NS) --create-namespace \
	  -f $(VALUES) --wait

test: ## Run the Helm install test (doctor-style Job)
	helm test $(RELEASE) --namespace $(NS)
	kubectl logs -n $(NS) -l app.kubernetes.io/component=test --tail=-1

uninstall: ## Remove the release
	helm uninstall $(RELEASE) --namespace $(NS)

package: docs lint ## Package the chart (for future Artifact Hub publishing)
	helm package $(CHART) --destination dist/

push: package ## Push the packaged chart to the OCI registry (GitHub Packages)
	helm push dist/$(CHART_NAME)-*.tgz $(OCI_REGISTRY)

changelog: ## Regenerate CHANGELOG.md (git-cliff) for the current Chart.yaml version
	git cliff --tag v$(CHART_VERSION) -o CHANGELOG.md

propose: ## Dry-run the release proposal locally (collect + AI advice + PR body; no PR)
	@bash .github/scripts/release/collect.sh dist/release
	@python3 .github/scripts/release/advise.py dist/release
	@bump=$$(python3 -c "import json;print(json.load(open('dist/release/advice.json'))['bump'])"); \
	  from=$$(python3 -c "import json;print(json.load(open('dist/release/context.json'))['bump_from'])"); \
	  new=$$(bash .github/scripts/release/semver.sh next $$from $$bump); \
	  printf -- "- (local dry-run: contributors resolved in CI)\n" > dist/release/contributors.md; \
	  echo "=== proposing v$$new (bump=$$bump from $$from) ==="; \
	  bash .github/scripts/release/render-pr-body.sh dist/release $$new dist/release/contributors.md
