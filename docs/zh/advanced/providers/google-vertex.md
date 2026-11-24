---
title: Google Vertex AI
description: 使用 GCP 服务账号连接 Vertex AI Gemini。
translation_source:
  path: docs/advanced/providers/google-vertex.md
  commit: 050b421cc602ab29b5116b9e1506df28d0a01dff
---

| 所需密钥 | 覆盖文件 |
| --- | --- |
| GCP 服务账号 Secret | `values-google-vertex.yaml` |

## 使用条件

在 GCP 项目中启用 Vertex AI API。此示例挂载具有 Vertex AI User 角色的 GCP 服务账号 JSON 文件。

此示例在全球端点使用 `google/gemini-3.8-flash`，替代[已在 Vertex 停用的 Gemini 2.5 Flash](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions)。选择其他区域或模型前，请检查[模型和区域可用性](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash)。此示例不使用 Gemini Developer API。

## 安装

```bash
kubectl create namespace hermes-agent
kubectl create secret generic vertex-sa --namespace hermes-agent \
  --from-file=sa.json=/path/to/sa.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string config.vertex.project_id='<your-gcp-project>' --wait
```

如果命名空间或 Secret 已存在，请复用。不要将 JSON 密钥写入 Helm values 或提交到仓库。此示例挂载文件，不使用 API 密钥。

## 更新现有版本

对于已安装的版本，默认设置 `bootstrap.overwrite: false` 会保留 PVC 上的 `config.yaml`。请在 Hermes 中更改模型，或编辑该文件。仅升级覆盖文件不会更改已保存的模型。

## 验证

CI 无需云账号即可验证此覆盖文件。当覆盖文件、Hermes 镜像或测试框架变化时，它会渲染 Chart，
并在没有网络和凭据的环境中让固定版本的 Hermes 镜像连接本地 mock，检查 Vertex 的项目、区域、
`google/gemini-3.8-flash` 请求路径以及固定的回复。路径或模型错误会导致失败。具体检查项和本地
运行方法见 [`provider-contract`](https://github.com/jyje/hermes-agent-helm/blob/main/docs/contributing/ci.md#provider-contract)（英文）。

这是 mock 验证。它不检验 IAM、配额或真实的 Vertex 推理，Secret 也只检查了作为已挂载文件，并未在
Pod 中实际运行。安装后，请用你自己的项目发起一次对话。

[打开原始 YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## 完整覆盖文件

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```
