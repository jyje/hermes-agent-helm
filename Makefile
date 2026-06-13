CHART := charts/hermes-agent-helm
CHART_NAME := hermes-agent-helm
NS    := hermes-agent-helm
RELEASE := hermes-agent-helm
VALUES := $(CHART)/values.example.yaml
OCI_REGISTRY ?= oci://ghcr.io/jyje

CHART_VERSION = $(shell grep -E '^version:' $(CHART)/Chart.yaml | awk '{print $$2}' | tr -d '"')

.PHONY: docs lint template install test uninstall package push changelog help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

docs: ## Regenerate chart README via helm-docs (from README.md.gotmpl)
	helm-docs --chart-search-root=charts --template-files=README.md.gotmpl

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
