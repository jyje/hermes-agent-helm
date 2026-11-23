---
title: Google Vertex AI
description: GCP のサービス アカウントで Vertex AI の Gemini に接続します。
translation_source:
  path: docs/advanced/providers/google-vertex.md
  commit: 050b421cc602ab29b5116b9e1506df28d0a01dff
---

| 必要なシークレット | オーバーレイ |
| --- | --- |
| GCP サービス アカウントの Secret | `values-google-vertex.yaml` |

## 利用条件

GCP プロジェクトで Vertex AI API を有効にしてください。この例は、Vertex AI ユーザーロールを持つ GCP サービス アカウントの JSON ファイルをマウントします。

この例はグローバル エンドポイントで `google/gemini-3.8-flash` を使います。[Vertex で提供が終了した Gemini 2.5 Flash](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions)の代替です。リージョンやモデルを変更する前に、[モデルとロケーションの対応状況](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash)を確認してください。この例では Gemini Developer API を使いません。

## インストール

```bash
kubectl create namespace hermes-agent
kubectl create secret generic vertex-sa --namespace hermes-agent \
  --from-file=sa.json=/path/to/sa.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string config.vertex.project_id='<your-gcp-project>' --wait
```

名前空間や Secret がすでにある場合は、そのリソースを再利用してください。JSON キーを Helm values に入れたりコミットしたりしないでください。この例は API キーではなくファイルをマウントします。

## 既存リリースの更新

既存リリースでは、デフォルトの `bootstrap.overwrite: false` が PVC 上の `config.yaml` を保持します。Hermes でモデルを変更するか、そのファイルを編集してください。オーバーレイをアップグレードするだけでは保存済みのモデルは変わりません。

## 検証

CI はクラウドのアカウントなしでこのオーバーレイを検証します。オーバーレイ、Hermes イメージ、
ハーネスが変わると、チャートをレンダリングし、ネットワークも認証情報もない状態で固定された
Hermes イメージをローカルのモックに接続して、Vertex のプロジェクト、リージョン、
`google/gemini-3.8-flash` のリクエスト経路と固定の応答を確認します。経路やモデルが違うと
失敗します。具体的な検査とローカルでの実行方法は
[`provider-contract`](https://github.com/jyje/hermes-agent-helm/blob/main/docs/contributing/ci.md#provider-contract)（英語）を参照してください。

これはモックによる検証です。IAM、クォータ、実際の Vertex 推論は検証せず、Secret も Pod では
実行せずマウントされたファイルとして確認するだけです。インストール後は、自分のプロジェクトで
チャットを一度実行してください。

[元の YAML を開く](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## オーバーレイ全体

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```
