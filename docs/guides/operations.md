---
title: Operations and testing
description: Render safely, validate the chart, and understand the gateway lifecycle.
---

## Local validation

```bash
make docs
make lint
make template
```

## Runtime validation

Run `helm test <release> --namespace <namespace>` after installation. For provider end-to-end checks, configure `tests.chat.enabled` deliberately; it is not required for normal installation.

## Gateway behavior

`hermes gateway run` is an outbound messenger process and the upstream image is s6-supervised. Leave the image entrypoint intact. The optional management dashboard on port 9119 is sensitive and should only be exposed behind authentication.