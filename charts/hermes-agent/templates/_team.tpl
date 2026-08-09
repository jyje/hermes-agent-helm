{{/* Validate the cross-field invariants that JSON Schema cannot express. */}}
{{- define "hermes-agent.team.validate" -}}
{{- if .Values.team.enabled -}}
  {{- $teamName := required "team.name is required when team.enabled=true" .Values.team.name -}}
  {{- $identity := required "team.identity is required when team.enabled=true" .Values.team.identity -}}
  {{- $leaderName := required "team.leader.name is required when team.enabled=true" .Values.team.leader.name -}}
  {{- $leaderMention := required "team.leader.mentionEnv is required when team.enabled=true" .Values.team.leader.mentionEnv -}}
  {{- if lt (len .Values.team.members) 1 -}}
    {{- fail "team.members must contain at least one member when team.enabled=true" -}}
  {{- end -}}
  {{- if not .Values.team.sharedVolume.enabled -}}
    {{- fail "team.sharedVolume.enabled must be true when team.enabled=true" -}}
  {{- end -}}
  {{- if not .Values.team.skill.enabled -}}
    {{- fail "team.skill.enabled must be true when team.enabled=true" -}}
  {{- end -}}
  {{- if and (eq .Values.team.role "member") .Values.team.skill.create -}}
    {{- fail "only a team leader release may set team.skill.create=true" -}}
  {{- end -}}
  {{- if eq .Values.team.sharedVolume.mountPath .Values.persistence.mountPath -}}
    {{- fail "team.sharedVolume.mountPath must differ from persistence.mountPath" -}}
  {{- end -}}
  {{- if and (eq .Values.team.role "member") .Values.team.sharedVolume.create -}}
    {{- fail "only a team leader release may set team.sharedVolume.create=true" -}}
  {{- end -}}
  {{- if and .Values.team.sharedVolume.permissions.enabled (ne .Values.team.role "leader") -}}
    {{- fail "team.sharedVolume.permissions.enabled is supported only for the leader" -}}
  {{- end -}}

  {{- $names := dict $leaderName true -}}
  {{- $mentions := dict $leaderMention true -}}
  {{- $identityIsMember := false -}}
  {{- range .Values.team.members -}}
    {{- if hasKey $names .name -}}
      {{- fail (printf "team member name %q is duplicated or matches the leader" .name) -}}
    {{- end -}}
    {{- $_ := set $names .name true -}}
    {{- if hasKey $mentions .mentionEnv -}}
      {{- fail (printf "team mention environment variable %q is duplicated" .mentionEnv) -}}
    {{- end -}}
    {{- $_ := set $mentions .mentionEnv true -}}
    {{- if eq .name $identity -}}
      {{- $identityIsMember = true -}}
    {{- end -}}
  {{- end -}}
  {{- if and (eq .Values.team.role "leader") (ne $identity $leaderName) -}}
    {{- fail "team.identity must equal team.leader.name for a leader release" -}}
  {{- end -}}
  {{- if and (eq .Values.team.role "member") (not $identityIsMember) -}}
    {{- fail "team.identity must match one team.members entry for a member release" -}}
  {{- end -}}

  {{- $agent := default (dict) (get .Values.config "agent") -}}
  {{- $disabled := default (list) (get $agent "disabled_toolsets") -}}
  {{- if has "skills" $disabled -}}
    {{- fail "team mode requires the skills toolset; remove skills from config.agent.disabled_toolsets" -}}
  {{- end -}}

  {{- $reserved := list "DISCORD_ALLOW_BOTS" "DISCORD_THREAD_REQUIRE_MENTION" "DISCORD_REPLY_TO_MODE" "DISCORD_ALLOW_MENTION_REPLIED_USER" -}}
  {{- range .Values.extraEnv -}}
    {{- if has .name $reserved -}}
      {{- fail (printf "%s is managed by team mode; remove it from extraEnv" .name) -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "hermes-agent.team.skillName" -}}
{{- .Values.team.skill.name | default (printf "%s-roster" .Values.team.name) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hermes-agent.team.skillConfigMapName" -}}
{{- .Values.team.skill.configMapName | default (printf "%s-skill" .Values.team.name) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hermes-agent.team.sharedClaimName" -}}
{{- .Values.team.sharedVolume.claimName | default (printf "%s-knowledge" .Values.team.name) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hermes-agent.team.skillMountPath" -}}
{{- printf "%s/skills/%s" (.Values.persistence.mountPath | trimSuffix "/") (include "hermes-agent.team.skillName" .) -}}
{{- end -}}

{{/* Minimal always-on identity and routing context. The full protocol stays in the skill. */}}
{{- define "hermes-agent.team.environmentHint" -}}
You are {{ .Values.team.identity | quote }}, the {{ upper .Values.team.role }} of Hermes team {{ .Values.team.name | quote }}.
Load and follow /{{ include "hermes-agent.team.skillName" . }} for every team roster, member-status, delegation, handoff, review, or synthesis request.
The configured leader is {{ .Values.team.leader.name | quote }} with exact Discord mention {{ printf "<@${%s}>" .Values.team.leader.mentionEnv }}.
{{- if eq .Values.team.role "leader" }}
Configured members and their exact Discord mentions:
{{- range .Values.team.members }}
- {{ .name }}: {{ printf "<@${%s}>" .mentionEnv }} - {{ .role }}
{{- end }}
Only explicit Discord messages following the team skill are cross-agent handoffs.
{{- else }}
Accept team work only from the configured leader and return the complete result to that leader according to the team skill.
{{- end }}
Discord's typing indicator is display state, not authoritative evidence that a member is online or working.
Durable accepted team knowledge is mounted at {{ .Values.team.sharedVolume.mountPath }}; it is not a task queue or completion signal.
{{- end -}}

{{/* Merge team-safe conversation settings and identity context into config.yaml. */}}
{{- define "hermes-agent.effectiveConfig" -}}
{{- include "hermes-agent.team.validate" . -}}
{{- $config := deepCopy .Values.config -}}
{{- if .Values.team.enabled -}}
  {{- $_ := set $config "group_sessions_per_user" false -}}
  {{- $discord := deepCopy (default (dict) (get $config "discord")) -}}
  {{- $_ := set $discord "thread_require_mention" true -}}
  {{- $_ := set $discord "history_backfill" true -}}
  {{- if not (hasKey $discord "history_backfill_limit") -}}
    {{- $_ := set $discord "history_backfill_limit" 50 -}}
  {{- end -}}
  {{- $allowMentions := deepCopy (default (dict) (get $discord "allow_mentions")) -}}
  {{- $_ := set $allowMentions "everyone" false -}}
  {{- $_ := set $allowMentions "roles" false -}}
  {{- $_ := set $allowMentions "users" true -}}
  {{- $_ := set $allowMentions "replied_user" false -}}
  {{- $_ := set $discord "allow_mentions" $allowMentions -}}
  {{- $_ := set $config "discord" $discord -}}

  {{- $agent := deepCopy (default (dict) (get $config "agent")) -}}
  {{- $existingHint := default "" (get $agent "environment_hint") -}}
  {{- $teamHint := include "hermes-agent.team.environmentHint" . -}}
  {{- if $existingHint -}}
    {{- $_ := set $agent "environment_hint" (printf "%s\n\n%s" ($existingHint | trim) ($teamHint | trim)) -}}
  {{- else -}}
    {{- $_ := set $agent "environment_hint" ($teamHint | trim) -}}
  {{- end -}}
  {{- $_ := set $config "agent" $agent -}}
{{- end -}}
{{- toYaml $config -}}
{{- end -}}

{{- define "hermes-agent.team.skillContent" -}}
---
name: {{ include "hermes-agent.team.skillName" . }}
description: Manage the {{ .Values.team.name }} Hermes team roster, leader and member responsibilities, member status, Discord handoffs, reviews, and shared knowledge. Use for any team, member, roster, online-status, delegation, handoff, or collaboration request.
---

# {{ .Values.team.name }} team protocol

Your identity and assigned role come from the runtime environment hint. Follow
only the workflow matching that role. This one shared skill is mounted by every
configured team release.

## Roster

| Name | Team role | Capabilities |
|---|---|---|
| {{ .Values.team.leader.name }} | Leader | Task decomposition, assignment, review, and final synthesis |
{{- range .Values.team.members }}
| {{ .name }} | {{ .role | replace "|" "\\|" }} | {{ if .capabilities }}{{ join ", " .capabilities }}{{ else }}Not specified{{ end }} |
{{- end }}

The roster states who is configured. It does not prove runtime availability.
Never infer that a member is online, idle, or working from Discord's typing
indicator. Treat only an explicit team `TASK`, `RESULT`, or `BLOCKED` message
as authoritative workflow state.

## Shared knowledge

The shared volume is mounted at `{{ .Values.team.sharedVolume.mountPath }}`.
The leader is its curator and may write durable, reviewed, reusable knowledge.
Members receive a read-only mount and may consult it as background.
Never use the volume for live assignments, queues, locks, progress, completion
markers, or result handoffs. Discord messages must contain all context required
to perform and review a task.

## Leader workflow

1. Acknowledge the human request briefly, then decompose it.
2. Choose exactly one suitable member. Send one message containing that
   member's exact mention, complete context, one concrete task, observable
   acceptance criteria, and this final marker:

   `[TEAM run=<short-id> step=<n> TASK]`

3. Wait for that member's matching `RESULT` or `BLOCKED` response. Do not infer
   progress from typing state and do not mention another member while waiting.
4. Review the result. Request one concrete revision from the same member when
   needed, or hand the accepted result and full context to the next member.
5. Preserve the run id and increment the step. Never exceed
   **{{ .Values.team.protocol.maxHandoffs }}** member handoffs. Escalate to the
   human without a member mention when the limit would be exceeded.
6. When the goal is complete, provide the human-facing synthesis with no member
   mention. A no-mention final response terminates the workflow.

Never mention two members at once. Never emit filler containing a member
mention. Do not use `delegate_task` as a substitute for assigning a configured
team member: it creates an anonymous child, not one of the rostered agents.

## Member workflow

1. Act only on a leader message containing your exact mention and a
   `[TEAM ... TASK]` marker.
2. Perform the visible task against its acceptance criteria. Do not delegate to
   another configured member and do not use the shared volume as a message bus.
3. Return exactly one complete response to the leader. Include evidence,
   assumptions, and caveats, then finish with the matching marker:

   `[TEAM run=<same-id> step=<same-n> RESULT]`

4. If blocked, return one precise question and the same metadata with
   `BLOCKED`. Mention the leader exactly once and never mention another member.
{{- with .Values.team.skill.extraInstructions }}

## Deployment-specific instructions

{{ . }}
{{- end }}
{{- end -}}
