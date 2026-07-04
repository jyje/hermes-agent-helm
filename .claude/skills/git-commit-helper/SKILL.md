---
name: git-commit-helper
description: Generate descriptive commit messages by analyzing git diffs following the project's specific policy. Use when the user asks for help writing commit messages or reviewing staged changes.
---

# Git Commit Helper

You are an expert software engineer managing git commits. Whenever the user requests a git commit, asks for help with a commit message, or asks to review staged changes, you MUST adhere to the following strict guidelines and workflow.

## 1. Commit Message Format
All commit messages must strictly follow this format:
```
<gitmoji> <type>(<domain>): <title>

<description>
```

### Formatting Rules:
- **Gitmoji**: Must use one of the exactly specified emojis (see mapping below).
- **Type**: Must be lowercase, chosen from the mapping below.
- **Domain**: Must be enclosed in parentheses `()`. Identify the primary component or domain affected (e.g., `(nfs)`, `(open-webui)`). Use lowercase and kebab-case. 
- **Title**: A concise summary of the change in imperative mood. Must start with a lowercase letter directly after the colon and space.
- **Description**: (Optional) Use this to explain "why" the change was made or provide further context.

### Skill-File Changes
`SKILL.md` files define agent behavior, not just documentation — use `fix` (corrections/refinements to an existing skill) or `feat` (new capability/rule added to a skill), never `docs`, for changes to them. Set the domain to `skills/<skill-name>` (e.g. `(skills/git-commit-helper)`) so it reads distinctly from other domains in a repo where skills live alongside other project code. In a repo dedicated entirely to skills (e.g. this one), the bare skill name (e.g. `(git-commit-helper)`) is sufficient since there's no ambiguity.

---

## 2. Gitmoji & Type Mapping
Only use the following approved types and emojis:

| Gitmoji | Type       | Description |
| :------ | :--------- | :---------- |
| 🎉      | `init`     | Initial commit of a project |
| 🔧      | `chore`    | Routine maintenance or minor corrections |
| 🛠️      | `fix`      | Intentional functional configuration changes |
| ✨      | `feat`     | New features |
| ✏️      | `typo`     | Fix a typo |
| 🐛      | `bug`      | Fix a bug |
| ⬆️      | `dep`      | Upgrade dependencies |
| 🔐      | `security` | Add or update secrets |
| 🗑️      | `remove`   | Deprecate or clean up code |
| ♻️      | `refactor` | Refactor code |
| 📄      | `docs`     | Add or update documentation |
| 📝      | `article`  | Add or update articles (content/workload, not project code) |
| 🎨      | `style`    | Improve structure / format |
| ⚡      | `perf`     | Improve performance |
| ✅      | `test`     | Add, update, or pass tests |
| 🔨      | `build`    | Add or update development scripts |
| 🚀      | `release`  | Cut or merge a release (e.g. the release-proposal PR title/merge commit) |

#### Automated / Bot Commits
Commits created entirely by automation (e.g., Dependabot, Renovate) without direct user or agent involvement use a dedicated pairing, kept separate from the manual mapping above:

| Gitmoji | Type | Description |
| :------ | :--- | :---------- |
| 🤖      | `ci` | Added automatically by a bot/automation (e.g., Dependabot), not by direct user intervention |

Configure this pairing directly in the automation tool itself, not by hand-editing bot commits after the fact. For Dependabot, set `commit-message` in `dependabot.yml` for every `package-ecosystem` entry:
```yaml
commit-message:
  prefix: "🤖 ci"
  prefix-development: "🤖 ci"
  include: "scope"
```
This renders as `🤖 ci(deps): bump <package> from X to Y` for production dependencies and `🤖 ci(deps-dev): ...` for development ones (the `(scope)` comes from `include: "scope"`, not from manually typing a domain). Without this config, Dependabot's default has no gitmoji at all, e.g. `build(deps): bump the production-dependencies group with 6 updates` — that default is the bug to fix, not a format to tolerate.

---

## 3. Workflow Requirements
1. **Analyze changes**: Review staged and unstaged changes to understand the scope and purpose of the work.
2. **Split by concern**: If the changes span multiple semantically distinct concerns (e.g. different `Type`, different `Domain`, or otherwise unrelated purposes), split them into separate commits instead of bundling them into one. Stage and commit each concern individually, each with its own message following this policy. Do not split a single concern across multiple commits just to make diffs smaller.
3. **Review history**: Search the most recent 10 commits in the `git log` to help determine the appropriate `Type` and `Domain`. After identifying a potential `Domain`, search up to 10 recent commits specifically for that domain to ensure consistency and gain context for writing the commit message.
4. **Propose message**: Present the drafted commit message to the user in a markdown code block. If split into multiple commits, present all of them together before proceeding.
5. **Wait for confirmation**: Ask the user if they want to proceed with the proposed commit message(s). Do not proceed with committing or pushing until explicit approval is given.
6. **Commit & Push**:
   - Only execute `git commit` after explicit user approval. Do NOT auto-commit.
   - After committing, ask the user if they want to push to the remote repository.
   - Only execute `git push` after receiving explicit user approval. Do NOT auto-push.

---

## 4. Strict Constraints
- **Agent Autonomy**: You MUST NOT arbitrarily execute commit or push commands before the user approves. All execution must wait for explicit user consent.
- **Language**: The commit message and any detailed explanations of changes MUST be in English only. Do NOT use Korean.
- **Privacy & Security**: NEVER include local paths, sensitive environment variables, or other local/sensitive information in the commit messages or detailed descriptions.
- **No Session Metadata**: NEVER append session infomation or session links. (e.g. `Claude-Session:` lines to commit messages) This is a public repository and session URLs are confidential.

---

## 5. Examples

### Initial commit
```
🎉 init: setup project

Make a Next.js project for UI/UX and a FastAPI project for the AI backend. 
```

### Feature addition (AI/agent)
```
✨ feat(agent): add Deep Agents example with OpenAI-compatible API

Wire up a Deep Agents example that talks to any OpenAI-compatible
endpoint via uv-managed dependencies.
```

### Feature addition (web frontend)
```
✨ feat(vue): initialize Vue frontend and implement 1:1 parity with Next.js chat

Port the existing Next.js chat UI to Vue so both frontends share the
same feature set and API contract.
```

### Intentional functional configuration change
```
🛠️ fix(nfs): rollback health probes and chart rename to fix distroless image compatibility

Revert recent changes including health probes and chart renaming because the
distroless image lacks 'sh' and other shell utilities required for probes.
```

### Routine maintenance
```
🔧 chore(helm): remove deprecated Helm chart versions and clean up configuration files

Remove old chart versions and clean up unused configuration files for homer applications.
```

### Bug fix
```
🐛 bug(open-webui): resolve inconsistencies in git commit policy rule

Fix three bugs in the git commit policy rule:
1. Translate Korean text to English to match the 'Always English' policy
2. Clarify gitmoji mapping conflicts
3. Add missing types to the Type list
```

### Dependency update
```
⬆️ dep(open-webui): update chart to 10.2.1 from 8.10.0

Upgrade open-webui Helm chart to latest version.
```

### Refactoring (web frontend)
```
♻️ refactor(assets): reorganize logos into subdirectories

Group logo images by source/purpose instead of dumping them all into
a single flat assets folder.
```

### Security
```
🔐 security(open-webui): add CORS_ALLOW_ORIGIN environment variable for enhanced security

Configure CORS settings to restrict allowed origins.
```

### Typo fix
```
✏️ typo(docs): fix typo in gitmoji standard reference

Correct "gitmodi" to "gitmoji" in documentation.
```

### Article (content/workload)
```
📝 article(blog): add new post about kubernetes best practices

Add a new blog post discussing kubernetes deployment strategies and best practices.
```

### Documentation
```
📄 docs(chart): add Korean translation of the chart README

Add the Korean README as a twin of the English one so non-English
users get the same install/config guidance.
```

### Build / CI
```
🔨 build(ci): bump ubuntu runner version to 26.04-arm

Move workflows onto the arm runner image to match production hardware
and pick up its faster cold-start time.
```
