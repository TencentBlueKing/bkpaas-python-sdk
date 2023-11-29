{{/*
Expand the name of the chart.
*/}}
{{- define "bk-demo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "bk-demo.fullname" -}}
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
Create a default name prefix for the resources which truncate at 32 chars.
*/}}
{{- define "bk-demo.name-prefix" -}}
{{- include "bk-demo.fullname" . | trunc 32 | trimSuffix "-" -}}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "bk-demo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "bk-demo.labels" -}}
app.kubernetes.io/name: {{ include "bk-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ include "bk-demo.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "bk-demo.selector-labels" -}}
app.kubernetes.io/name: {{ include "bk-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create a job name with default prefix and release revision.
*/}}
{{- define "bk-demo.job-name" -}}
{{- $root := first . -}}
{{- $name := last . -}}
{{- include "bk-demo.name-prefix" $root }}-{{ $name }}-{{ $root.Release.Revision }}
{{- end }}