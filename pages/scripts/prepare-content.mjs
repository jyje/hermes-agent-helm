import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../..', import.meta.url));
const site = join(root, 'pages');
const generated = join(site, 'src/content/docs');
const rawRoot = join(site, 'public/source');
// Example pages always live two folders below `docs`, hence this stable import.
const componentImport = "import RawDocumentActions from '../../../../components/RawDocumentActions.astro';";
const quote = (source) => source;

const examples = [
  ['providers', 'openai', 'OpenAI', 'OpenAI API로 가장 빠르게 시작하는 기본 provider 구성', 'OPENAI_API_KEY', 'OpenAI 계정과 API key가 필요합니다. 처음 설치하거나 범용 기준 구성이 필요할 때 선택합니다.', 'OpenAI 모델 ID와 key만 실제 값으로 바꾸면 됩니다.'],
  ['providers', 'anthropic', 'Anthropic', 'Claude를 Hermes Agent의 기본 모델로 사용하는 구성', 'ANTHROPIC_API_KEY', 'Anthropic API key와 사용 가능한 Claude 모델이 필요합니다.', 'provider를 `anthropic`으로 두고 Anthropic key를 Secret으로 주입합니다.'],
  ['providers', 'gemini', 'Google Gemini', 'Google AI Studio Gemini API를 사용하는 구성', 'GOOGLE_API_KEY', 'Google AI Studio API key가 필요합니다.', 'Gemini 모델 ID와 API key를 환경에 맞게 조정합니다.'],
  ['providers', 'google-vertex', 'Google Vertex AI', 'GCP 서비스 계정으로 Vertex AI Gemini에 연결하는 구성', 'GCP service-account Secret', 'Vertex AI User 권한의 GCP 서비스 계정 JSON Secret과 project ID가 필요합니다.', '정적 API key 대신 credential 파일을 mount하므로 Secret 생성 단계를 먼저 수행합니다.'],
  ['providers', 'github-copilot', 'GitHub Copilot', 'Discord를 통해 GitHub OAuth device login을 완료하는 구성', 'DISCORD_BOT_TOKEN', 'Discord bot과 GitHub Copilot 권한이 필요합니다. 영속 볼륨도 활성화해야 로그인 토큰이 재사용됩니다.', '초기 pod 로그 또는 Discord 안내에 나온 device code를 GitHub에서 승인합니다.'],
  ['providers', 'nvidia-nim-and-discord', 'NVIDIA NIM + Discord', 'NVIDIA NIM 모델과 Discord bot을 함께 연결하는 구성', 'NVIDIA_API_KEY, DISCORD_BOT_TOKEN', 'NVIDIA API key, Discord bot token, 채널 및 허용 사용자 ID가 필요합니다.', 'ARM64 클러스터에서도 사용할 수 있는 provider + messenger 조합입니다.'],
  ['providers', 'openrouter', 'OpenRouter', '하나의 OpenRouter key로 다양한 upstream 모델을 선택하는 구성', 'OPENROUTER_API_KEY', 'OpenRouter API key와 선택할 모델 ID가 필요합니다.', '모델 이름은 OpenRouter 카탈로그에 있는 provider/model 형식으로 지정합니다.'],
  ['providers', 'fireworks', 'Fireworks AI', 'Fireworks의 OpenAI-compatible provider를 사용하는 구성', 'FIREWORKS_API_KEY', 'Fireworks API key가 필요합니다.', '지원 모델 목록을 확인한 뒤 `config.model.default`를 바꿉니다.'],
  ['providers', 'deepinfra', 'DeepInfra', 'DeepInfra OpenAI-compatible endpoint에 연결하는 구성', 'DEEPINFRA_API_KEY', 'DeepInfra API key와 해당 endpoint에서 제공하는 모델 ID가 필요합니다.', '모델은 DeepInfra `/v1/openai/models` 목록에서 선택합니다.'],
  ['providers', 'upstage', 'Upstage Solar', 'Upstage Solar provider를 사용하는 구성', 'UPSTAGE_API_KEY', 'Upstage API key가 필요합니다.', 'Solar 모델 ID와 key를 설정합니다.'],
  ['integrations', 'litellm', 'LiteLLM (external)', '네트워크로 도달 가능한 LiteLLM proxy에 연결하는 구성', 'OPENAI_API_KEY', 'LiteLLM의 HTTPS endpoint와 proxy virtual key가 필요합니다.', '클러스터 밖 proxy 또는 Ingress/LoadBalancer로 노출된 proxy에 사용합니다.'],
  ['integrations', 'litellm-k8s', 'LiteLLM (in cluster)', '같은 Kubernetes 클러스터 안의 LiteLLM Service DNS를 사용하는 구성', 'OPENAI_API_KEY', 'LiteLLM Service 이름·namespace·port와 proxy key가 필요합니다.', 'base URL을 Service FQDN으로 맞추면 Ingress와 TLS 없이 통신합니다.'],
  ['integrations', 'anthropic-and-discord', 'Anthropic + Discord', 'Claude provider와 Discord bot을 한 릴리스에 결합한 구성', 'ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN', 'Anthropic API key, Discord bot token, 채널 ID가 필요합니다.', '모델과 messenger 설정을 함께 검증할 때 사용합니다.'],
  ['integrations', 'openai-and-telegram', 'OpenAI + Telegram', 'OpenAI provider와 Telegram bot을 결합한 구성', 'OPENAI_API_KEY, TELEGRAM_BOT_TOKEN', 'OpenAI key와 Telegram bot token이 필요합니다.', 'Telegram 대상 범위를 설정한 뒤 bot과 대화해 연결을 확인합니다.'],
  ['integrations', 'ingress', 'Dashboard Ingress', '민감한 management dashboard를 인증된 Ingress 뒤에 노출하는 구성', 'OPENAI_API_KEY, basic-auth Secret', 'Ingress controller와 사전에 생성한 basic-auth Secret이 필요합니다.', 'dashboard는 API key를 노출할 수 있으므로 authentication과 private network 경계를 반드시 적용합니다.'],
  ['advanced', 'bitwarden', 'Bitwarden Secrets Manager', 'Bitwarden에서 provider key를 시작 시 가져오는 구성', 'BWS_ACCESS_TOKEN', '읽기 권한이 있는 Bitwarden machine account와 bootstrap Kubernetes Secret이 필요합니다.', 'provider key는 Git이나 Kubernetes Secret이 아닌 Bitwarden project에 보관합니다.'],
  ['advanced', 'moa', 'Mixture of Agents', '여러 reference model과 aggregator model을 결합하는 구성', 'OPENROUTER_API_KEY', 'Hermes image v2026.7.1 이상과 각 preset provider의 key가 필요합니다.', 'preset의 reference·aggregator model을 워크로드에 맞게 교체합니다.'],
  ['advanced', 'multi-agent-collab', 'Collaborating pair', '같은 Discord channel에서 @mention으로 협업하는 planner 구성', 'NVIDIA_API_KEY, DISCORD_BOT_TOKEN', '두 bot identity, 공통 channel, 서로의 Discord user ID가 필요합니다.', '이 파일은 planner 절반입니다. builder용 별도 release와 loop-brake 설정을 함께 배포합니다.'],
  ['advanced', 'shared-knowledge', 'Shared knowledge PVC', '여러 agent가 RWX PVC를 공용 지식 저장소로 mount하는 구성', 'Provider key', '미리 생성한 RWX PVC와 uid/gid 10000이 쓸 수 있는 권한이 필요합니다.', '각 agent의 HERMES_HOME은 private PVC로 유지하면서 knowledge claim만 공유합니다.'],
  ['advanced', 'team-leader', 'Team leader', 'Discord thread 기반 leader-orchestrated team의 leader 구성', 'NVIDIA_API_KEY, DISCORD_BOT_TOKEN', 'RWX knowledge claim, leader bot, member bot IDs가 필요합니다.', 'leader는 shared knowledge를 read-write로 mount하고 member에게 명시적으로 작업을 handoff합니다.'],
  ['advanced', 'team-member', 'Team member', 'leader 팀에 참여하는 개별 member release 구성', 'NVIDIA_API_KEY, DISCORD_BOT_TOKEN', '고유한 bot token, fullnameOverride, TEAM_MEMBER_NAME이 필요합니다.', 'member마다 이 파일로 별도 Helm release를 만들고 identity 값을 다르게 설정합니다.'],
];

async function output(path, content) { await mkdir(dirname(path), { recursive: true }); await writeFile(path, content); }
async function sourceCopy(source, destination) { await mkdir(dirname(destination), { recursive: true }); await cp(source, destination); }

async function sourcePage({ source, outputPath, title, description }) {
  const rawPath = `/hermes-agent-helm/source/${relative(root, source)}`;
  await sourceCopy(source, join(rawRoot, relative(root, source)));
  const content = await readFile(source, 'utf8');
  await output(join(generated, outputPath), `---\ntitle: ${title}\ndescription: ${description}\n---\n\n<div class="raw-document-actions" data-raw-path="${rawPath}">\n  <a href="${rawPath}">Open raw Markdown</a>\n  <button type="button" data-copy-source>Copy source</button>\n</div>\n\n${content}`);
}

async function main() {
  // The generated source set can add or remove pages between runs. Clear
  // Astro's ignored content caches so deleted generated files never linger.
  await rm(join(site, '.astro'), { recursive: true, force: true });
  await rm(join(site, 'node_modules/.astro'), { recursive: true, force: true });
  await rm(generated, { recursive: true, force: true });
  await rm(rawRoot, { recursive: true, force: true });
  await output(join(generated, 'index.mdx'), `---\ntitle: Hermes Agent on Kubernetes\ndescription: Deploy a persistent, provider-agnostic Hermes Agent with Helm.\ntemplate: splash\n---\n\n<div className="hero">\n\n# Your agent runs where your workloads run.\n\nDeploy Hermes Agent as a lightweight Deployment or StatefulSet. Pick an example, add your secret, and keep the agent’s working state on a PVC.\n\n[Install Hermes Agent](/hermes-agent-helm/getting-started/install/) [Choose an example](/hermes-agent-helm/examples/)\n\n</div>\n\n## Start with a known shape\n\n- **One model, no messenger** — begin with [OpenAI](/hermes-agent-helm/examples/providers/openai/), Anthropic, Gemini, or another provider overlay.\n- **One bot, one channel** — use a Discord or Telegram example when the agent should receive messages.\n- **Several agents** — use the collaboration and team overlays only after the individual bot flow works.\n\n## What this chart owns\n\nThe chart creates the Kubernetes workload, its configuration ConfigMap, its Secret, optional persistent storage, and opt-in dashboard Service/Ingress. Hermes runs commands in its pod; no Docker socket or inbound API is required.\n\n## Read the source in the form you need\n\nEvery guide links to its original Markdown or YAML and offers a copy action. The full machine-readable map is available at [llms.txt](/hermes-agent-helm/llms.txt).`);
  await sourceCopy(join(site, 'content/index.mdx'), join(generated, 'index.mdx'));
  await output(join(generated, 'getting-started/index.md'), `---\ntitle: Getting Started\ndescription: Install Hermes Agent, then choose a values overlay for your provider and integration.\nsidebar:\n  label: Getting Started\n  order: 0\n---\n\nStart with the [installation guide](/hermes-agent-helm/getting-started/install/), then choose the values overlay that matches your provider and integration.`);
  await output(join(generated, 'getting-started/install.md'), `---\ntitle: Install Hermes Agent\ndescription: Install the chart with a provider key, then verify the rendered workload.\n---\n\n## Install from the Helm repository\n\n\`\`\`bash\nhelm repo add hermes-agent https://jyje.github.io/hermes-agent-helm\nhelm repo update\nhelm upgrade --install hermes-agent hermes-agent/hermes-agent \\\n  --namespace hermes-agent --create-namespace \\\n  --set-string env.OPENAI_API_KEY='sk-...' --wait\n\`\`\`\n\n## Or install the OCI artifact\n\n\`\`\`bash\nhelm upgrade --install hermes-agent \\\n  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \\\n  --version <chart-version> --namespace hermes-agent --create-namespace \\\n  --set-string env.OPENAI_API_KEY='sk-...' --wait\n\`\`\`\n\n## Verify\n\n\`\`\`bash\nhelm test hermes-agent --namespace hermes-agent\nkubectl get pods --namespace hermes-agent\n\`\`\`\n\nThe Helm test performs the chart's doctor-style check. Pick a provider overlay next when the generic OpenAI default is not your target.`);
  await output(join(generated, 'examples/index.md'), `---\ntitle: Choose a values example\ndescription: Start from a runnable overlay, then replace only its dummy credentials and environment-specific identifiers.\n---\n\nEvery example is an overlay for \`charts/hermes-agent/values.yaml\`. It is deliberately partial: Hermes adds its version-specific defaults and your environment injects secrets separately.\n\n## Pick by outcome\n\n- **Connect a model:** provider pages cover public APIs and the GitHub device-login flow.\n- **Connect a proxy or bot:** integration pages cover LiteLLM, Discord, Telegram, and the protected dashboard.\n- **Coordinate agents:** advanced pages cover secrets managers, shared storage, collaboration, and teams.\n\nNever commit real keys into an overlay. Each example documents the required Secret and an install command with placeholder values.`);
  await output(join(generated, 'guides/configuration.md'), `---\ntitle: Configuration model\ndescription: Understand how config.yaml, environment variables, Secrets, and the persistent Hermes home work together.\n---\n\n## Precedence\n\nHermes merges partial chart configuration with its built-in version-specific defaults. The effective precedence is **CLI > config.yaml > environment > built-in defaults**. The chart therefore does not attempt to reproduce the complete upstream configuration.\n\n## Why configuration is seeded\n\nThe chart seeds \`config.yaml\` into \`$HERMES_HOME\` with an init container. It is not mounted read-only: Hermes writes runtime state in its home directory. Set \`bootstrap.overwrite: true\` to reseed on each rollout, or keep the default seed-if-absent behavior to preserve edits.\n\n## Controller choice\n\nUse a Deployment for the normal single-agent case. Use a StatefulSet when stable pod identity matters to your workload. Neither mode creates a Namespace; choose it through Helm's \`--namespace\` flag.`);
  await output(join(generated, 'guides/secrets-and-storage.md'), `---\ntitle: Secrets and persistence\ndescription: Supply credentials safely and preserve Hermes state without turning the values file into a secret store.\n---\n\n## Credentials\n\nThe chart uses \`envFrom\` to make the chart-managed Secret available to Hermes. Environment variables win over \`config.yaml\`, so provider credentials belong in \`env\` or \`extraEnvFrom\`, not in a checked-in \`.env\` file.\n\nFor production, create a Secret outside Helm and reference it with \`extraEnvFrom\`; the Bitwarden example documents an alternative bootstrap pattern.\n\n## Persistent home\n\nThe default persistent volume is intentionally modest. It stores config, login state, sessions, and agent memory. Scale its size or storage class through values. Shared agent knowledge is a separate concern: use an RWX volume only when multiple agents genuinely need the same writable directory.`);
  await output(join(generated, 'guides/operations.md'), `---\ntitle: Operations and testing\ndescription: Render safely, validate the chart, and understand the gateway lifecycle.\n---\n\n## Local validation\n\n\`\`\`bash\nmake docs\nmake lint\nmake template\n\`\`\`\n\n## Runtime validation\n\nRun \`helm test <release> --namespace <namespace>\` after installation. For provider end-to-end checks, configure \`tests.chat.enabled\` deliberately; it is not required for normal installation.\n\n## Gateway behavior\n\n\`hermes gateway run\` is an outbound messenger process and the upstream image is s6-supervised. Leave the image entrypoint intact. The optional management dashboard on port 9119 is sensitive and should only be exposed behind authentication.`);
  await output(join(generated, 'reference/values.md'), `---\ntitle: Chart values\ndescription: Generated Helm values reference and the maintained source chart README.\n---\n\nThe complete Helm values table is generated by \`helm-docs\` and remains in the chart README so package consumers and this site describe the same chart.\n\n[Open the generated chart reference](/hermes-agent-helm/reference/chart-readme/)\n\n[View raw values.yaml](/hermes-agent-helm/source/charts/hermes-agent/values.yaml)`);
  await output(join(generated, 'reference/helm-repository.md'), `---\ntitle: Helm repository index\ndescription: The machine-readable Helm repository index and published chart packages.\n---\n\nThe documentation site and Helm repository share GitHub Pages without overwriting one another. Helm clients use this index; you can inspect it directly or add the repository with the command below.\n\n\`\`\`bash\nhelm repo add hermes-agent https://jyje.github.io/hermes-agent-helm\nhelm repo update\n\`\`\`\n\n[Open index.yaml](/hermes-agent-helm/index.yaml)`);
  await output(join(generated, 'reference/source-documents.md'), `---\ntitle: Source documents\ndescription: The original repository Markdown, available as rendered pages and raw files.\n---\n\n- [Repository README](/hermes-agent-helm/reference/repository-readme/)\n- [Chart README and generated values table](/hermes-agent-helm/reference/chart-readme/)\n- [Helm installation guide](/hermes-agent-helm/reference/helm-installation/)\n- [ArgoCD guide](/hermes-agent-helm/reference/argocd/)\n- [Local development guide](/hermes-agent-helm/reference/local-development/)\n- [CI guide](/hermes-agent-helm/reference/ci/)\n- [Teams guide](/hermes-agent-helm/reference/teams/)\n- [Collaboration guide](/hermes-agent-helm/reference/collaboration/)\n- [Roadmap](/hermes-agent-helm/reference/roadmap/)`);

  await output(join(generated, 'examples/providers/index.md'), `---\ntitle: Provider examples\ndescription: Values overlays for connecting Hermes Agent to a model provider.\nsidebar:\n  label: Providers\n  order: 0\n---\n\nChoose the provider whose API credentials and model catalog you plan to use.`);
  await output(join(generated, 'examples/integrations/index.md'), `---\ntitle: Integration examples\ndescription: Values overlays for proxies, messaging platforms, and the optional dashboard.\nsidebar:\n  label: Integrations\n  order: 0\n---\n\nChoose an integration after the underlying provider connection is working.`);
  await output(join(generated, 'examples/advanced/index.md'), `---\ntitle: Advanced examples\ndescription: Values overlays for secret managers, collaboration, shared storage, and teams.\nsidebar:\n  label: Advanced\n  order: 0\n---\n\nUse these examples after validating the individual provider and messenger flow.`);
  await output(join(generated, 'guides/index.md'), `---\ntitle: Guides\ndescription: Configuration, storage, and operating guidance for the chart.\nsidebar:\n  label: Guides\n  order: 0\n---\n\nThese guides explain how chart values and Hermes runtime behavior fit together.`);
  await output(join(generated, 'reference/index.md'), `---\ntitle: Reference\ndescription: Generated values, repository metadata, and source documentation.\nsidebar:\n  label: Reference\n  order: 0\n---\n\nUse this section for the complete chart reference and original project documents.`);

  const examplesIndexPath = join(generated, 'examples/index.md');
  await writeFile(examplesIndexPath, (await readFile(examplesIndexPath, 'utf8')).replace('---\n', '---\nsidebar:\n  label: Examples\n  order: 0\n'));

  const directoryOrders = new Map([
    ['getting-started/index.md', 10],
    ['examples/index.md', 20],
    ['guides/index.md', 30],
    ['reference/index.md', 40],
    ['examples/providers/index.md', 10],
    ['examples/integrations/index.md', 20],
    ['examples/advanced/index.md', 30],
  ]);
  for (const [relativePath, order] of directoryOrders) {
    const pagePath = join(generated, relativePath);
    const page = await readFile(pagePath, 'utf8');
    await writeFile(
      pagePath,
      page.replace(
        /\n  order: 0\n/,
        '\n  order: ' + order + "\n  attrs:\n    data-sidebar-order: '" + order + "'\n",
      ),
    );
  }

  for (const [group, slug, title, description, secret, requirements, customize] of examples) {
    const source = join(root, 'charts/hermes-agent', `values-${slug}.yaml`);
    const rawPath = `/hermes-agent-helm/source/charts/hermes-agent/values-${slug}.yaml`;
    const yaml = await readFile(source, 'utf8');
    await sourceCopy(source, join(rawRoot, 'charts/hermes-agent', `values-${slug}.yaml`));
    await output(join(generated, 'examples', group, `${slug}.mdx`), `---\ntitle: ${title}\ndescription: ${description}\n---\n\n${componentImport}\n\n<div className="example-meta">\n  <div><strong>Required secret</strong>${secret}</div>\n  <div><strong>Overlay</strong>values-${slug}.yaml</div>\n</div>\n\n## When to use it\n\n${requirements}\n\n## Install\n\n\`\`\`bash\nhelm upgrade --install hermes-agent ./charts/hermes-agent \\\n  --namespace hermes-agent --create-namespace \\\n  -f charts/hermes-agent/values-${slug}.yaml \\\n  --set-string env.${secret.split(',')[0].replaceAll(' ', '_')}='<real-value>' --wait\n\`\`\`\n\nWhen the example requires more than one credential, pass every listed value with \`--set-string\` or use \`extraEnvFrom\` to reference an existing Secret.\n\n## Adapt before deploying\n\n${customize}\n\n<RawDocumentActions rawPath="${rawPath}" label="Open raw values YAML" />\n\n## Complete overlay\n\n\`\`\`yaml title="charts/hermes-agent/values-${slug}.yaml"\n${quote(yaml)}\n\`\`\``);
  }

  const documents = [
    ['README.md', 'reference/repository-readme.md', 'Repository README', 'The project overview and development entry points.'],
    ['charts/hermes-agent/README.md', 'reference/chart-readme.md', 'Chart README', 'The maintained chart documentation and generated values table.'],
    ['examples/helm/README.md', 'reference/helm-installation.md', 'Helm installation guide', 'Local, OCI, upgrade, and publishing instructions.'],
    ['examples/argocd/README.md', 'reference/argocd.md', 'ArgoCD guide', 'GitOps deployment examples and Secret patterns.'],
    ['docs/local-dev.md', 'reference/local-development.md', 'Local development guide', 'Local Kubernetes and development workflows.'],
    ['docs/ci.md', 'reference/ci.md', 'CI guide', 'Continuous validation and release checks.'],
    ['docs/devops-roadmap.md', 'reference/devops-roadmap.md', 'DevOps roadmap', 'Operational improvement roadmap.'],
    ['docs/roadmap.md', 'reference/roadmap.md', 'Roadmap', 'Project roadmap and release readiness.'],
    ['CONTRIBUTING.md', 'reference/contributing.md', 'Contributing', 'Contribution guidelines.'],
    ['SECURITY.md', 'reference/security.md', 'Security policy', 'Security disclosure policy.'],
    ['docs/teams.md', 'reference/teams.md', 'Hermes teams', 'Leader-and-member team workflow.'],
    ['docs/collaboration.md', 'reference/collaboration.md', 'Hermes collaboration', 'Pair collaboration and handoff protocol.'],
    ['README-ko.md', 'ko/reference/repository-readme.md', '프로젝트 README', '프로젝트 개요의 한국어 원문입니다.'],
    ['charts/hermes-agent/README-ko.md', 'ko/reference/chart-readme.md', '차트 README', '차트 문서의 한국어 원문입니다.'],
    ['docs/teams-ko.md', 'ko/reference/teams.md', 'Hermes 팀', '팀 운영 문서의 한국어 원문입니다.'],
    ['docs/collaboration-ko.md', 'ko/reference/collaboration.md', 'Hermes 협업', '협업 문서의 한국어 원문입니다.'],
    ['docs/roadmap-ko.md', 'ko/reference/roadmap.md', '로드맵', '프로젝트 로드맵의 한국어 원문입니다.'],
    ['SECURITY-ko.md', 'ko/reference/security.md', '보안 정책', '보안 정책의 한국어 원문입니다.'],
  ];
  for (const [sourcePath, outputPath, title, description] of documents) await sourcePage({ source: join(root, sourcePath), outputPath, title, description });

  const list = ['# Hermes Agent Helm documentation', '', '> Machine-readable map of the published documentation.', '', '## Core guides', '', '- [Install](https://jyje.github.io/hermes-agent-helm/getting-started/install/): Install and verify Hermes Agent.', '- [Examples](https://jyje.github.io/hermes-agent-helm/examples/): Choose a ready-made values overlay.', '- [Configuration](https://jyje.github.io/hermes-agent-helm/guides/configuration/): Configuration precedence and persistence.', '- [Chart reference](https://jyje.github.io/hermes-agent-helm/reference/chart-readme/): Full maintained chart README and values table.', '', '## Values examples', '', ...examples.map(([, slug, title, description]) => `- [${title}](https://jyje.github.io/hermes-agent-helm/examples/${examples.find((entry) => entry[1] === slug)[0]}/${slug}/): ${description}`), ''].join('\n');
  await output(join(site, 'public/llms.txt'), list);
  await output(join(site, 'public/llms-full.txt'), list);
}

main().catch((error) => { console.error(error); process.exit(1); });
