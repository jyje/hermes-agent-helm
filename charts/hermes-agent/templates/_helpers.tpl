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
Pod template (metadata + spec), shared by the StatefulSet and Deployment
controllers. Caller is expected to nest this under `template:` with `nindent 4`.
*/}}
{{- define "hermes-agent.podTemplate" -}}
metadata:
  annotations:
    # Roll pods when config/secret content changes.
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
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
  {{- with .Values.imagePullSecrets }}
  imagePullSecrets:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  securityContext:
    {{- toYaml .Values.podSecurityContext | nindent 4 }}
  {{- if or .Values.bootstrap.enabled .Values.auth.deviceFlow.enabled }}
  initContainers:
    {{- if .Values.bootstrap.enabled }}
    # Seed the partial config.yaml into HERMES_HOME (the writable volume) so
    # Hermes merges it over its built-in defaults. Hermes also writes to its
    # home at runtime, so config is not mounted read-only.
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
          dest="{{ .Values.persistence.mountPath }}/config.yaml"
          if [ "{{ .Values.bootstrap.overwrite }}" = "true" ] || [ ! -f "$dest" ]; then
            echo "Seeding $dest (overwrite={{ .Values.bootstrap.overwrite }})"
            cp /seed/config.yaml "$dest"
          else
            echo "Keeping existing $dest (overwrite=false)"
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
    # Bootstrap the selected provider's credential via the OAuth device flow
    # before the agent starts. Idempotent: skips if a valid token already
    # exists on the volume. Runs as the Hermes runtime uid so the token file it
    # writes to $HERMES_HOME/.env is readable by the agent.
    - name: auth-device-login
      image: "{{ $df.image.repository }}:{{ $df.image.tag }}"
      imagePullPolicy: {{ .Values.image.pullPolicy }}
      command: ["python3", "/login/device_login.py"]
      env:
        - name: HERMES_HOME
          value: {{ .Values.persistence.mountPath | quote }}
        - name: OAUTH_CLIENT_ID
          value: {{ $p.clientId | quote }}
        - name: OAUTH_SCOPE
          value: {{ $p.scope | default "read:user" | quote }}
        - name: AUTH_HOST
          value: {{ $p.authHost | default "github.com" | quote }}
        - name: TOKEN_ENV
          value: {{ $p.tokenEnv | quote }}
        - name: VALIDATE_URL
          value: {{ $p.validateUrl | default "" | quote }}
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
      securityContext:
        {{- toYaml .Values.securityContext | nindent 8 }}
      env:
        - name: HERMES_HOME
          value: {{ .Values.persistence.mountPath | quote }}
        {{- with .Values.extraEnv }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      envFrom:
        - secretRef:
            name: {{ include "hermes-agent.fullname" . }}-env
        {{- with .Values.extraEnvFrom }}
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
    {{- if eq .Values.controller.type "deployment" }}
    - name: data
      persistentVolumeClaim:
        claimName: {{ include "hermes-agent.fullname" . }}
    {{- end }}
    {{- else }}
    - name: data
      emptyDir: {}
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
