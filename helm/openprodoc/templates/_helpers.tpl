{{/*
Expand the name of the chart.
*/}}
{{- define "openprodoc.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "openprodoc.fullname" -}}
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
Create chart name and version as used by the chart label.
*/}}
{{- define "openprodoc.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "openprodoc.labels" -}}
helm.sh/chart: {{ include "openprodoc.chart" . }}
{{ include "openprodoc.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: openprodoc
{{- end }}

{{/*
Selector labels
*/}}
{{- define "openprodoc.selectorLabels" -}}
app.kubernetes.io/name: {{ include "openprodoc.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "openprodoc.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "openprodoc.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Core Engine labels
*/}}
{{- define "openprodoc.coreEngine.labels" -}}
{{ include "openprodoc.labels" . }}
app.kubernetes.io/component: core-engine
{{- end }}

{{/*
Core Engine selector labels
*/}}
{{- define "openprodoc.coreEngine.selectorLabels" -}}
{{ include "openprodoc.selectorLabels" . }}
app.kubernetes.io/component: core-engine
{{- end }}
