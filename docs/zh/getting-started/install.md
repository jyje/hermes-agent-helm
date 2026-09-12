---
title: "安装 Hermes Agent"
description: "使用提供商密钥安装 Chart，再验证工作负载。"
translation_source:
  path: docs/getting-started/install.md
  commit: 4c00dee9830393c8829109453d698bb1eb0ef3f3
---

## 安装 OCI 制品（推荐）

```bash
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --version <chart-version> --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## 或从 Helm 仓库安装

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## 验证

```bash
helm test hermes-agent --namespace hermes-agent
kubectl get pods --namespace hermes-agent
```

Helm 测试执行 Chart 的 doctor 风格检查。如果不使用默认 OpenAI 配置，请选择对应提供商的覆盖文件。
