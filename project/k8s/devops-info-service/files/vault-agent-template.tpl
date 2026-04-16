{{- with secret "secret/data/devops-info/config" -}}
USERNAME={{ .Data.data.username }}
PASSWORD={{ .Data.data.password }}
API_KEY={{ .Data.data.api_key }}
{{- end -}}
