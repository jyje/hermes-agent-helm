{{/*
Expand the name of the chart.
*/}}
{{- define "hermes-agent.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified app name.
*/}}
{{- define "hermes-agent.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart name and version label.
*/}}
{{- define "hermes-agent.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "hermes-agent.labels" -}}
helm.sh/chart: {{ include "hermes-agent.chart" . }}
{{ include "hermes-agent.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "hermes-agent.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hermes-agent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service account name.
*/}}
{{- define "hermes-agent.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hermes-agent.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Headless service name used for StatefulSet governance.
*/}}
{{- define "hermes-agent.headlessServiceName" -}}
{{- printf "%s-headless" (include "hermes-agent.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Main image reference. Falls back to Chart.AppVersion when image.tag is empty.
*/}}
{{- define "hermes-agent.image" -}}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}

{{/*
Test image reference. Falls back to the main image when tests.image fields are empty.
*/}}
{{- define "hermes-agent.testImage" -}}
{{- $repo := .Values.tests.image.repository | default .Values.image.repository }}
{{- $tag := .Values.tests.image.tag | default .Values.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" $repo $tag }}
{{- end }}

{{/*
Set $dict[$key] = $default, but only when $dict doesn't already have that key
- so a chart-computed default (team mode's config.yaml overlay, or any future
one) never clobbers a value the user already set under `config:`. Go maps are
reference types, so mutating $dict here is visible to the caller with no
return value needed. Call as:
  {{- $_ := include "hermes-agent.setConfigDefault" (list $dict "key" $default) -}}
*/}}
{{- define "hermes-agent.setConfigDefault" -}}
{{- $dict := index . 0 -}}
{{- $key := index . 1 -}}
{{- $default := index . 2 -}}
{{- if not (hasKey $dict $key) -}}
  {{- $_ := set $dict $key $default -}}
{{- end -}}
{{- end -}}

{{/*
Logical ports exposed by the chart Service. An empty explicit list keeps the
legacy dashboard-only Service byte-for-byte compatible. Callers may parse this
list for another Kubernetes port shape, such as containerPorts.
*/}}
{{- define "hermes-agent.servicePorts" -}}
{{- if .Values.service.ports }}
{{- range .Values.service.ports }}
- name: {{ .name }}
  port: {{ .port }}
  targetPort: {{ .targetPort | default .port }}
  protocol: {{ .protocol | default "TCP" }}
{{- end }}
{{- else -}}
# Intended for the management dashboard (port 9119). Requires the dashboard
# to be enabled and bound to 0.0.0.0 (--insecure) inside the container.
- name: dashboard
  port: {{ .Values.service.port }}
  targetPort: {{ .Values.service.port }}
  protocol: TCP
{{- end }}
{{- end }}

{{/*
Pod template (metadata + spec), shared by the StatefulSet and Deployment
controllers. Caller is expected to nest this under `template:` with `nindent 4`.
*/}}
{{- define "hermes-agent.podTemplate" -}}
{{- include "hermes-agent.team.validate" . -}}
metadata:
  annotations:
    # Roll pods when config/secret content changes.
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
    {{- if and .Values.team.enabled .Values.team.skill.enabled }}
    # Roll leaders and members when the rendered shared skill changes. Members
    # reference the leader-owned ConfigMap, so hashing only the created resource
    # would leave their existing Pods on the previous in-memory protocol.
    checksum/team-skill: {{ tpl (.Files.Get "files/skills/hermes-team-roster/SKILL.md") . | sha256sum }}
    {{- end }}
    {{- with .Values.podAnnotations }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  labels:
    {{- include "hermes-agent.selectorLabels" . | nindent 4 }}
    {{- with .Values.podLabels }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
spec:
  serviceAccountName: {{ include "hermes-agent.serviceAccountName" . }}
  automountServiceAccountToken: {{ .Values.serviceAccount.automountServiceAccountToken }}
  {{- with .Values.runtimeClassName }}
  runtimeClassName: {{ . | quote }}
  {{- end }}
  {{- with .Values.terminationGracePeriodSeconds }}
  terminationGracePeriodSeconds: {{ . }}
  {{- end }}
  {{- with .Values.imagePullSecrets }}
  imagePullSecrets:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  securityContext:
    {{- toYaml .Values.podSecurityContext | nindent 4 }}
  {{- if or .Values.bootstrap.enabled .Values.auth.deviceFlow.enabled .Values.extraInitContainers (and .Values.team.enabled .Values.team.sharedVolume.permissions.enabled) }}
  initContainers:
    {{- if .Values.bootstrap.enabled }}
    # Seed chart-managed files into HERMES_HOME (the writable volume). Hermes
    # merges config.yaml over its built-in defaults and also writes to its home
    # at runtime, so the ConfigMap is not mounted there read-only.
    - name: seed-config
      image: "{{ include "hermes-agent.image" . }}"
      imagePullPolicy: {{ .Values.image.pullPolicy }}
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      command:
        - sh
        - -c
        - |
          set -eu
          seed() {
            dest="$1"
            source="$2"
            if [ "{{ .Values.bootstrap.overwrite }}" = "true" ] || [ ! -f "$dest" ]; then
              echo "Seeding $dest (overwrite={{ .Values.bootstrap.overwrite }})"
              cp "$source" "$dest"
            else
              echo "Keeping existing $dest (overwrite=false)"
            fi
          }
          seed "{{ .Values.persistence.mountPath }}/config.yaml" /seed/config.yaml
          if [ -f /seed/SOUL.md ]; then
            seed "{{ .Values.persistence.mountPath }}/SOUL.md" /seed/SOUL.md
          fi
      volumeMounts:
        - name: config
          mountPath: /seed
          readOnly: true
        - name: data
          mountPath: {{ .Values.persistence.mountPath }}
    {{- end }}
    {{- if .Values.auth.deviceFlow.enabled }}
    {{- $df := .Values.auth.deviceFlow }}
    {{- $p := index $df.providers $df.provider }}
    {{- if not $p }}{{ fail (printf "auth.deviceFlow.provider %q has no matching entry under auth.deviceFlow.providers" $df.provider) }}{{- end }}
    {{- $flow := $p.flow | default "github" }}
    # Bootstrap the selected provider credential before the agent starts.
    # GitHub writes .env; OpenAI Codex uses Hermes' native auth.json store.
    - name: auth-device-login
      {{- if eq $flow "openai-codex" }}
      image: "{{ include "hermes-agent.image" . }}"
      {{- else }}
      image: "{{ $df.image.repository }}:{{ $df.image.tag }}"
      {{- end }}
      imagePullPolicy: {{ .Values.image.pullPolicy }}
      {{- with $df.securityContext }}
      securityContext:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      command: ["python3", "/login/device_login.py"]
      env:
        - name: HERMES_HOME
          value: {{ .Values.persistence.mountPath | quote }}
        - name: DEVICE_FLOW_KIND
          value: {{ $flow | quote }}
        - name: OAUTH_CLIENT_ID
          value: {{ $p.clientId | default "" | quote }}
        - name: OAUTH_SCOPE
          value: {{ $p.scope | default "read:user" | quote }}
        - name: AUTH_HOST
          value: {{ $p.authHost | default "github.com" | quote }}
        - name: TOKEN_ENV
          value: {{ $p.tokenEnv | default "" | quote }}
        - name: VALIDATE_URL
          value: {{ $p.validateUrl | default "" | quote }}
        - name: OPENAI_CODEX_ISSUER
          value: {{ $p.issuer | default "https://auth.openai.com" | quote }}
        - name: NOTIFY
          value: {{ $df.notify | quote }}
        - name: LOGIN_TIMEOUT_SECONDS
          value: {{ $df.timeoutSeconds | quote }}
        - name: FORCE_RELOGIN
          value: {{ $df.forceRelogin | quote }}
        - name: CHOWN_UID
          value: {{ $df.tokenOwner.uid | quote }}
        - name: CHOWN_GID
          value: {{ $df.tokenOwner.gid | quote }}
        - name: PYTHONUNBUFFERED
          value: "1"
        {{- with .Values.extraEnv }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      envFrom:
        - secretRef:
            name: {{ include "hermes-agent.fullname" . }}-env
        {{- with .Values.extraEnvFrom }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      {{- with $df.resources }}
      resources:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      volumeMounts:
        - name: login-script
          mountPath: /login
          readOnly: true
        - name: data
          mountPath: {{ .Values.persistence.mountPath }}
    {{- end }}
    {{- if and .Values.team.enabled .Values.team.sharedVolume.permissions.enabled }}
    # Optional ownership preparation for a chart-managed RWX knowledge volume.
    - name: init-team-shared
      image: {{ .Values.team.sharedVolume.permissions.image | quote }}
      imagePullPolicy: IfNotPresent
      securityContext:
        {{- toYaml .Values.team.sharedVolume.permissions.securityContext | nindent 8 }}
      command:
        - sh
        - -c
        - chown -R {{ .Values.team.sharedVolume.permissions.uid }}:{{ .Values.team.sharedVolume.permissions.gid }} /team-shared
      volumeMounts:
        - name: team-shared
          mountPath: /team-shared
    {{- end }}
    {{- with .Values.extraInitContainers }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- end }}
  containers:
    - name: hermes-agent
      image: "{{ include "hermes-agent.image" . }}"
      imagePullPolicy: {{ .Values.image.pullPolicy }}
      {{- with .Values.command }}
      command:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.args }}
      args:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- if .Values.service.ports }}
      ports:
        {{- range (include "hermes-agent.servicePorts" . | fromYamlArray) }}
        - name: {{ .name }}
          containerPort: {{ .targetPort | default .port }}
          protocol: {{ .protocol | default "TCP" }}
        {{- end }}
      {{- end }}
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      env:
        - name: HERMES_HOME
          value: {{ .Values.persistence.mountPath | quote }}
        {{- if .Values.apiServer.enabled }}
        - name: API_SERVER_ENABLED
          value: "true"
        - name: API_SERVER_HOST
          value: {{ .Values.apiServer.host | quote }}
        - name: API_SERVER_PORT
          value: {{ .Values.apiServer.port | quote }}
        {{- with .Values.apiServer.corsOrigins }}
        - name: API_SERVER_CORS_ORIGINS
          value: {{ . | quote }}
        {{- end }}
        {{- end }}
        {{- if .Values.webhook.enabled }}
        - name: WEBHOOK_ENABLED
          value: "true"
        - name: WEBHOOK_PORT
          value: {{ .Values.webhook.port | quote }}
        {{- end }}
        {{- if .Values.team.enabled }}
        # Team mode makes explicit body mentions the only bot-to-bot trigger.
        - name: DISCORD_ALLOW_BOTS
          value: "mentions"
        - name: DISCORD_THREAD_REQUIRE_MENTION
          value: "true"
        - name: DISCORD_REPLY_TO_MODE
          value: "off"
        - name: DISCORD_ALLOW_MENTION_REPLIED_USER
          value: "false"
        {{- end }}
        {{- with .Values.extraEnv }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      envFrom:
        - secretRef:
            name: {{ include "hermes-agent.fullname" . }}-env
        {{- with .Values.extraEnvFrom }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      {{- with .Values.probes.startup }}
      startupProbe:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.probes.liveness }}
      livenessProbe:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.probes.readiness }}
      readinessProbe:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      resources:
        {{- toYaml .Values.resources | nindent 8 }}
      volumeMounts:
        - name: data
          mountPath: {{ .Values.persistence.mountPath }}
        {{- if and .Values.team.enabled .Values.team.skill.enabled }}
        - name: team-skill
          mountPath: {{ include "hermes-agent.team.skillMountPath" . }}
          readOnly: true
        {{- end }}
        {{- if and .Values.team.enabled .Values.team.sharedVolume.enabled }}
        - name: team-shared
          mountPath: {{ .Values.team.sharedVolume.mountPath }}
          readOnly: {{ ne .Values.team.role "leader" }}
        {{- end }}
        {{- with .Values.extraVolumeMounts }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
    {{- with .Values.extraContainers }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  volumes:
    {{- if .Values.bootstrap.enabled }}
    - name: config
      configMap:
        name: {{ include "hermes-agent.fullname" . }}-config
    {{- end }}
    {{- if .Values.auth.deviceFlow.enabled }}
    - name: login-script
      configMap:
        name: {{ include "hermes-agent.fullname" . }}-login
        defaultMode: 0555
    {{- end }}
    {{- if .Values.persistence.enabled }}
    {{- if .Values.persistence.existingClaim }}
    - name: data
      persistentVolumeClaim:
        claimName: {{ .Values.persistence.existingClaim | quote }}
    {{- else if eq .Values.controller.type "deployment" }}
    - name: data
      persistentVolumeClaim:
        claimName: {{ include "hermes-agent.fullname" . }}
    {{- end }}
    {{- else }}
    - name: data
      emptyDir: {}
    {{- end }}
    {{- if and .Values.team.enabled .Values.team.skill.enabled }}
    - name: team-skill
      configMap:
        name: {{ include "hermes-agent.team.skillConfigMapName" . }}
    {{- end }}
    {{- if and .Values.team.enabled .Values.team.sharedVolume.enabled }}
    - name: team-shared
      persistentVolumeClaim:
        claimName: {{ include "hermes-agent.team.sharedClaimName" . }}
    {{- end }}
    {{- with .Values.extraVolumes }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- with .Values.nodeSelector }}
  nodeSelector:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.affinity }}
  affinity:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.tolerations }}
  tolerations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
