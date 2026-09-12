---
title: "Hermes Agent のインストール"
description: "プロバイダーのキーを指定してチャートをインストールし、ワークロードを検証します。"
translation_source:
  path: docs/getting-started/install.md
  commit: 4c00dee9830393c8829109453d698bb1eb0ef3f3
---

## OCI アーティファクトのインストール（推奨）

```bash
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --version <chart-version> --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## Helm リポジトリからインストール

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## 検証

```bash
helm test hermes-agent --namespace hermes-agent
kubectl get pods --namespace hermes-agent
```

Helm テストはチャートの doctor 形式の検査を実行します。標準の OpenAI を使わない場合は、利用するプロバイダーのオーバーレイを選択してください。
