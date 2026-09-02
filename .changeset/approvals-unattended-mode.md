---
"@jyje/hermes-agent-helm": patch
---

Documentation(approvals): Cover unattended_mode and protected instruction files

Add `approvals.unattended_mode` (new upstream between v2026.8.27 and
v2026.8.31) and `single_query_mode` to the README's "Unattended approvals"
section next to `cron_mode`, and explain which surfaces each of the three
"nobody can answer" switches governs: `unattended_mode` is the one that
applies to sessions arriving through the chart's `apiServer` / `webhook`
listeners, and it denies dangerous commands outright by default. Note that
writes to the agent's own instruction files always require approval with no
yolo bypass. English and Korean READMEs updated together.
