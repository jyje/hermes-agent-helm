CHART := charts/hermes-agent
CHART_NAME := hermes-agent
NS    := hermes-agent
RELEASE := hermes-agent
VALUES := $(CHART)/values-openai.yaml
OCI_REGISTRY ?= oci://ghcr.io/jyje/hermes-agent-helm

.PHONY: docs lint template install test uninstall package push changeset changeset-status release-version propose help

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

changeset: ## Interactively add a Changeset for a user-visible chart change
	pnpm changeset

changeset-status: ## Show the version Changesets will propose (no files changed)
	pnpm changeset:status

release-version: ## Consume Changesets and sync chart release files (run on a branch)
	pnpm release:version

propose: changeset-status ## Preview the pending release version locally (no PR, no changes)
