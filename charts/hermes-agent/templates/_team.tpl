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

{{/*
Merge team-safe conversation settings and identity context into config.yaml.
The discord/group_sessions_per_user defaults below only fill in a key the
user hasn't already set under `config:` (see hermes-agent.setConfigDefault) -
an existing team install that never touched these keys renders byte-identical
config.yaml; anyone who wants different team-mode Discord behavior can now
set it themselves. agent.environment_hint is exempt: it's generated from the
team roster (team.members/team.leader/team.identity), not a static default,
so it always merges rather than only filling a gap.
*/}}
{{- define "hermes-agent.effectiveConfig" -}}
{{- include "hermes-agent.team.validate" . -}}
{{- $config := deepCopy .Values.config -}}
{{- if .Values.team.enabled -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $config "group_sessions_per_user" false) -}}
  {{- $discord := deepCopy (default (dict) (get $config "discord")) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $discord "thread_require_mention" true) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $discord "history_backfill" true) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $discord "history_backfill_limit" 50) -}}
  {{- $allowMentions := deepCopy (default (dict) (get $discord "allow_mentions")) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $allowMentions "everyone" false) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $allowMentions "roles" false) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $allowMentions "users" true) -}}
  {{- $_ := include "hermes-agent.setConfigDefault" (list $allowMentions "replied_user" false) -}}
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
