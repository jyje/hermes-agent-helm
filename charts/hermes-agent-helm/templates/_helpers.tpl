{{/*
Expand the name of the chart.
*/}}
{{- define "hermes-agent-helm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified app name.
*/}}
{{- define "hermes-agent-helm.fullname" -}}
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
{{- define "hermes-agent-helm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "hermes-agent-helm.labels" -}}
helm.sh/chart: {{ include "hermes-agent-helm.chart" . }}
{{ include "hermes-agent-helm.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "hermes-agent-helm.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hermes-agent-helm.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service account name.
*/}}
{{- define "hermes-agent-helm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hermes-agent-helm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Headless service name used for StatefulSet governance.
*/}}
{{- define "hermes-agent-helm.headlessServiceName" -}}
{{- printf "%s-headless" (include "hermes-agent-helm.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Main image reference. Falls back to Chart.AppVersion when image.tag is empty.
*/}}
{{- define "hermes-agent-helm.image" -}}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}

{{/*
Test image reference. Falls back to the main image when tests.image fields are empty.
*/}}
{{- define "hermes-agent-helm.testImage" -}}
{{- $repo := .Values.tests.image.repository | default .Values.image.repository }}
{{- $tag := .Values.tests.image.tag | default .Values.image.tag | default .Chart.AppVersion }}
{{- printf "%s:%s" $repo $tag }}
{{- end }}
