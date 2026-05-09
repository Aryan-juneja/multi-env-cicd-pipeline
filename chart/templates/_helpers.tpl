{{/*
Resource name = the Helm release name. So `helm install myapp ...` produces
resources named "myapp".
*/}}
{{- define "myapp.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Common labels applied to every resource. Includes selector labels.
*/}}
{{- define "myapp.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels. Must be a stable subset of labels — Deployment selectors
are immutable after creation, so anything templated in here that varies
between deploys would block upgrades.
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
