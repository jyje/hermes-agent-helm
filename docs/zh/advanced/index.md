---
title: "进阶使用"
description: "配置、集成、运维和扩展 Hermes Agent 部署。"
translation_source:
  path: docs/advanced/index.md
  commit: 4c00dee9830393c8829109453d698bb1eb0ef3f3
---

从 Chart 的基础 `values.yaml` 出发，通过部分覆盖文件调整配置。Hermes 提供各版本的默认值，密钥由环境单独注入。

## 按目标选择

- **配置 Chart：** 了解配置模型、密钥、存储和测试。
- **连接模型：** 提供商页面介绍公开 API 和 GitHub 设备登录流程。
- **连接代理或机器人：** 集成页面介绍 LiteLLM、Discord、Telegram 和受保护的仪表板。
- **协调智能体：** 模式与团队指南介绍密钥管理器、共享存储、协作和团队。

切勿在覆盖文件中提交真实密钥。每个示例均说明所需 Secret，并提供使用占位值的安装命令。

> 本语言版本翻译入门页面，未翻译的章节使用英语。
