---
title: GitHub Copilot
description: 通过 Discord 或 Telegram 完成 GitHub Copilot 设备登录。
translation_source:
  path: docs/advanced/providers/github-copilot.md
  commit: 8e2ddc80214e950127133e680a3534f8eea28dac
---

| 所需密钥 | 覆盖文件 |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-github-copilot.yaml` |
| `TELEGRAM_BOT_TOKEN`（同时设置 `auth.deviceFlow.notify: telegram`） | `values-github-copilot.yaml` 加上下方的覆盖设置 |

## 使用条件

需要 Discord 或 Telegram 机器人以及 GitHub Copilot 使用权限。还需要持久存储，以便重复使用登录令牌。

从 Hermes v0.23.0 起，`copilot` 提供商迁移到了
[GitHub Copilot Labs 插件](https://github.com/NousResearch/hermes-labs-plugins/pull/34)。
如果配置档案选择了 Copilot，Hermes 会自动安装插件。如果限制了出站流量，
除了允许访问 Copilot API，还要确保首次启动时可以访问插件目录和 GitHub 上的插件源代码。

保留 `config.model.provider: copilot`。Chart 的设备登录仍将 `COPILOT_GITHUB_TOKEN`
写入 Hermes 卷，插件仍读取同一个键。如果只在另一台机器上通过 GitHub 或 Copilot CLI 登录，
插件无法使用那台机器上的凭据。请改用 Chart 的设备登录。

## 安装

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-github-copilot.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

如果示例需要多项凭据，请通过 `--set-string` 传入所有列出的值，或使用 `extraEnvFrom` 引用现有的 Secret。

## 部署时的配置

在 GitHub 上批准 Pod 首次启动日志或 Discord 提示中显示的设备代码。

## 后续启动

令牌保存在持久卷中的 `HERMES_HOME/.env`。下次启动时，初始化容器会通过
`https://api.github.com/user` 检查令牌。如果令牌仍有效，则跳过登录。
如果验证端点返回 HTTP 401 或 403，初始化容器会重新发起设备登录。此检查不受 Copilot 套餐影响。
Chart 1.18.0 及更早版本使用 `copilot_internal/v2/token` 进行检查。该端点对 Copilot Free
账号的有效令牌也会返回 403，导致每次重启都要求新的设备代码
（[#349](https://github.com/jyje/hermes-agent-helm/issues/349)）。如果覆盖 `validateUrl`，
请使用对有效令牌返回 200、仅在需要重新登录时返回 401 或 403 的端点。

## 使用 Telegram 代替 Discord

设置 `auth.deviceFlow.notify: telegram`，并提供 `TELEGRAM_BOT_TOKEN`、
`TELEGRAM_HOME_CHANNEL` 和 `TELEGRAM_ALLOWED_USERS`，替换 Discord 的对应设置。
设备代码会发送到 Telegram 聊天。设置 `readyNotify.enabled: true` 后，智能体就绪时也会在同一个聊天中发送通知。
使用 Copilot Free 账号实测时，登录成功，收到了就绪通知，并通过 `gpt-4o` 得到了回复。
可用模型取决于 GitHub 套餐。

[打开原始 YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## 完整覆盖文件

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```
