<!-- translation_source: README.md @ 4c00dee9830393c8829109453d698bb1eb0ef3f3 -->

<div align="center" markdown="1">

# jyje/hermes-agent-helm

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

👩🏻‍💻 在 Kubernetes 上运行 Hermes Agent - 使用 Codex/Copilot 登录，轻量运行智能体团队。

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · [日本語](README-ja.md) · [简体中文](README-zh.md)

**🚀 [Hermes 团队](docs/advanced/teams/index.md)** · [Chart 文档](charts/hermes-agent/README-zh.md) · [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) · [AGENTS](AGENTS.md)

---

**如果本项目对你有帮助，请点亮 ⭐，让更多人发现它。**

</div>

## 概述

> 简体中文版翻译入门页面。未翻译的章节使用英语。本译文尚未经中文母语维护者审核，欢迎提出修正建议。

![Flow of Hermes Agent](https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm-flow.png)

只需一次 `helm install`，即可在 Kubernetes 上运行 [Hermes Agent](https://github.com/NousResearch/hermes-agent)。支持 Hermes 可用的所有 LLM 提供商，可在小型单节点上运行，并经过实际运行验证。同一集群中的多个实例也可以组成 [**Hermes 团队**](docs/advanced/teams/reference.md)。这是一个**社区维护的 Chart**，并非 Nous Research 的官方发行版。

## 快速开始

1. **OCI（推荐）**：直接从镜像仓库安装，无需执行 `helm repo add`。

    ```bash
    helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

2. **Helm 仓库**：项目也在 GitHub Pages 上发布 Helm 仓库，添加一次后即可按名称安装。

    ```bash
    helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
    helm repo update
    helm install hermes-agent hermes-agent/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

如需固定版本，可使用 `--version` 指定某个[已发布的 Chart 版本](https://github.com/jyje/hermes-agent-helm/releases)。

如需从本仓库源码安装，例如尝试尚未发布的更改，请参阅下方的[开发](#开发)。

## 为什么使用此 Chart

- **通过 `values.yaml` 配置 Hermes 支持的提供商。** Hermes 本身通过环境变量支持 `openai-api`、`anthropic`、`gemini`、`openrouter`、`nvidia`、`deepseek` 以及 [LiteLLM](https://github.com/BerriAI/litellm) 等 OpenAI 兼容端点。此 Chart 通过 `values.yaml` 暴露这些配置，并提供可修改的各提供商示例，不在模板中固定提供商。
- **以聊天为中心的网关与账户登录。** 提供 Discord 或 Telegram 机器人令牌后，Chart 会启动 Hermes 的出站网关，并由 Kubernetes 管理其生命周期。对于 **GitHub Copilot** 和 **OpenAI Codex**，可选的设备登录初始化功能会将一次性链接和验证码发送到 Discord 主频道或日志，然后将可刷新的凭据保存到 `HERMES_HOME`。批准一次后，正常的 Pod 重启会复用已保存的登录状态。
- **从轻量配置扩展到生产环境。** 默认适用于家庭实验室、单节点和边缘集群：一个副本、适量的资源请求和较小的 PVC。通过增加资源进行纵向扩展。Hermes 是单实例个人智能体，拥有独立的 `HERMES_HOME`、网关和记忆。需要更多智能体时，运行多个独立管理的实例，将它们组成**团队**，通过共同的网关频道共享上下文。参阅 [Hermes 团队](docs/advanced/teams/reference.md)。
- **端到端验证。** CI 在临时 **kind** 集群中安装 Chart，运行随附的测试 Job（`hermes doctor`）。当仓库中的 `NVIDIA_API_KEY` secret 可用时，还会向 NVIDIA NIM 执行真实的 **`hermes chat` 往返调用**。Discord 线程中的领导者团队也完成了真实的人类 → 领导者 → 两个成员 → 领导者流程。Telegram 团队编排另行验证。

<div align="center">
  <img src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/demos/team-k9s-pods.png" alt="在 k9s 中查看 kind 集群上的 Hermes 团队 august、may 和 march"/>
  <p><em>部署证据：领导者 <code>august</code> 和成员 <code>may</code>/<code>march</code> 在 kind 中作为独立 release 运行。此截图本身不能证明多轮提及协作有效；最新状态请参阅 <a href="docs/advanced/teams/reference.md">Hermes 团队</a>。</em></p>
</div>

完整的资源说明、配置模型以及包含消息平台集成的各提供商安装示例，请参阅 [Chart README](charts/hermes-agent/README-zh.md)。

## 生产环境检查清单

以下功能均未默认启用，默认配置保持轻量。每一项都需要主动开启，并列出了验证依据，便于你自行判断是否满足运行要求。

| 关注点 | 方法 | 验证依据 |
|---|---|---|
| Pod Security Standards | `-f charts/hermes-agent/values-hardened.yaml` | kind 加固场景（PSS `restricted`） |
| 出站流量控制 | `networkPolicy.enabled=true` | CI 检查渲染后的策略 |
| 内核隔离 | `runtimeClassName: gvisor` 或其他沙箱运行时 | 取决于集群，仅有文档说明 |
| 密钥管理 | [Bitwarden 示例](charts/hermes-agent/values-bitwarden.yaml)或 [SealedSecret 指南](examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord) | Bitwarden：CI 的 values 示例冒烟测试；SealedSecret：仅有文档说明 |
| 升级安全 | `bootstrap.overwrite=false` 保留运行时编辑 | 已有行为说明，尚未经 CI 验证（[#235](https://github.com/jyje/hermes-agent-helm/issues/235)） |

## 完整安装

### OCI（推荐）

```bash
# render the chart and check its templates before installing
helm template hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# install with the generic defaults (set your provider key)
# release name == chart name keeps resources clean (hermes-agent-0, not hermes-agent-hermes-agent-0)
helm upgrade --install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

### Helm 仓库

```bash
# add the Helm Repository and fetch the latest chart index
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update

# render the chart and check its templates before installing
helm template hermes-agent hermes-agent/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# install with the generic defaults (set your provider key)
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

完整的 values 表、各提供商以及 Discord/Telegram、LiteLLM 的 `values-*.yaml` 示例，请参阅 [Chart README](charts/hermes-agent/README-zh.md)。复制原始 YAML 后通过 `-f` 传入即可。另有 [ArgoCD 示例](examples/argocd/)。

## 自动化

本仓库提供三项与 Chart 用户相关的自动化功能：

- **跟踪上游。** 定时任务每六小时检查新 Hermes 镜像，并创建更新 `appVersion` 的拉取请求。它不会自行发布版本，更新仍须经过与其他 Chart 更改相同的审核和 Changesets 流程。
- **签名发布。** 发布时生成 cosign 签名的 OCI 制品以及 Helm 仓库索引。
- **发布后验证。** 每次发布后，CI 从 OCI 安装已发布制品，验证签名并执行 Chart 自身的测试套件。

所有工作流、触发条件及其关系均记录在 [CI 指南](docs/contributing/ci.md)中。

## 开发

创建 PR 前，克隆仓库并从本地 Chart 路径安装，以验证修改：

```bash
git clone https://github.com/jyje/hermes-agent-helm.git
cd hermes-agent-helm

# render & lint
make template
make lint

# install from the local chart source
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1

# or start from a ready-made example (provider, Discord/Telegram, LiteLLM, ...)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' --wait
```

分支模型、发布流程及其他本地检查（`make docs` / `make test`）见 [CONTRIBUTING.md](CONTRIBUTING.md)，Chart 设计原则见 [AGENTS.md](AGENTS.md)。

## 路线图

此 Chart 专注于部署和管理**一个**智能体。目前可以通过 ArgoCD ApplicationSet 组建团队来扩展；基于 CRD 的 Operator 是尚未启动的长期候选方向。参阅[路线图](docs/about/roadmap.md)。

## 参与贡献

欢迎提交 Issue、PR 和想法。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，了解分支模型、本地检查和发布流程。所有合并的贡献都会在更新日志与发行说明中署名。

感谢所有贡献代码以及为项目点亮星标的朋友 ⭐

<a href="https://github.com/jyje/hermes-agent-helm/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jyje/hermes-agent-helm" alt="Contributors" />
</a>

---

> Banner © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
