# Lab 11 — Kubernetes Secrets & HashiCorp Vault

This document describes how the Lab 10 Helm chart was extended for **secret management**: native Kubernetes Secrets in Helm, optional **Vault Agent Injector** sidecars, and where to record evidence. The canonical step-by-step runbook (commands, Vault bootstrap, policy/role examples, and **screenshot checklist**) lives in **[`k8s/SECRETS.md`](../k8s/SECRETS.md)**.

Course lab spec: [`labs/lab11.md`](../../labs/lab11.md) (repository root).

---

## Objectives

- Create and inspect Kubernetes Secrets (`kubectl`).
- Manage application credentials via Helm (`templates/secrets.yaml`, `values.yaml`) and inject them with **`envFrom` + `secretRef`**.
- Keep non-sensitive environment variables DRY with a **named template** in `_helpers.tpl`.
- Deploy HashiCorp Vault in **dev mode** (learning only), enable **KV v2** and **Kubernetes auth**, and prove **Agent injection** into pods.
- Document trade-offs: Kubernetes Secrets vs Vault, requests vs limits, base64 vs encryption.

---

## Chart overview (after Lab 11)

Chart path: `k8s/devops-info-service/` (run Helm from the **`project/`** directory).

```
k8s/devops-info-service/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── values-vault.yaml              # Overlay: enable Vault injector + custom template
├── files/
│   └── vault-agent-template.tpl   # Vault Agent template (USERNAME/PASSWORD/API_KEY); not Helm syntax
└── templates/
    ├── _helpers.tpl               # fullname, labels, serviceAccountName, containerEnv (DRY)
    ├── deployment.yaml            # envFrom + env; optional Vault annotations; ServiceAccount
    ├── secrets.yaml               # Opaque Secret from credentials.*
    ├── serviceaccount.yaml
    ├── service.yaml
    ├── NOTES.txt
    └── hooks/
        ├── pre-install-job.yaml
        └── post-install-job.yaml
```

| File | Purpose |
|------|---------|
| `templates/secrets.yaml` | `Secret` with `stringData` for `username` / `password` (placeholders in Git). |
| `templates/deployment.yaml` | `envFrom.secretRef` to the chart Secret; `env` from `include "devops-info-service.containerEnv"`; optional Vault annotations. |
| `templates/serviceaccount.yaml` | Dedicated ServiceAccount for pods (Vault **Kubernetes auth** binds roles to this name). |
| `templates/_helpers.tpl` | `devops-info-service.serviceAccountName`, `devops-info-service.containerEnv` (`HOST`, `PORT`). |
| `files/vault-agent-template.tpl` | Custom **Vault Agent** render for `/vault/secrets/config` when `vaultInjector.useCustomTemplate=true`. |
| `values-vault.yaml` | Turns on injector + custom template without editing defaults. |

---

## Configuration reference

### `application` (non-secret env, DRY)

| Value | Default | Purpose |
|-------|---------|---------|
| `application.host` | `0.0.0.0` | Binds the app listener (rendered as `HOST`). |
| `application.port` | `5000` | App port (rendered as `PORT`; keep in sync with probes). |

### `credentials` (Helm Secret)

| Value | Default | Purpose |
|-------|---------|---------|
| `credentials.username` | `changeme-user` | Secret key `username` — override at install time. |
| `credentials.password` | `changeme-password` | Secret key `password` — **never** commit real passwords. |

Use `--set` or a private values file for real installs:

```bash
helm upgrade --install lab-info k8s/devops-info-service \
  -f k8s/devops-info-service/values.yaml \
  -f k8s/devops-info-service/values-dev.yaml \
  --set credentials.username=demo-user \
  --set credentials.password='use-a-strong-secret'
```

### `serviceAccount`

| Value | Default | Purpose |
|-------|---------|---------|
| `serviceAccount.create` | `true` | Create a chart-owned ServiceAccount. |
| `serviceAccount.name` | `""` | If empty and `create=true`, name defaults to release fullname. |

### `vaultInjector`

| Value | Default | Purpose |
|-------|---------|---------|
| `vaultInjector.enabled` | `false` | Add Vault Agent Injector annotations to the pod. |
| `vaultInjector.role` | `devops-info-service` | Vault **Kubernetes auth** role name. |
| `vaultInjector.secretPath` | `secret/data/devops-info/config` | KV v2 path for `agent-inject-secret-config`. |
| `vaultInjector.useCustomTemplate` | `false` | If `true`, also set `agent-inject-template-config` from `files/vault-agent-template.tpl`. |

Enable Vault integration:

```bash
helm upgrade --install lab-info k8s/devops-info-service \
  -f k8s/devops-info-service/values.yaml \
  -f k8s/devops-info-service/values-dev.yaml \
  -f k8s/devops-info-service/values-vault.yaml \
  --set credentials.username=demo-user \
  --set credentials.password='use-a-strong-secret'
```

**Prerequisite:** Vault (with injector) installed in the **same namespace** as the app, KV secret written at `secret/devops-info/config`, Kubernetes auth configured, and a Vault role bound to this chart’s ServiceAccount. Exact commands are in [`k8s/SECRETS.md`](../k8s/SECRETS.md).

---

## Task mapping (lab rubric)

| Lab task | What to show |
|----------|----------------|
| **1 — kubectl Secret** | Create `app-credentials`, `kubectl get secret ... -o yaml`, decode base64; explain encoding vs encryption and etcd encryption (see runbook §1). |
| **2 — Helm Secret** | `secrets.yaml`, `values.yaml`, deployment `envFrom`; `kubectl exec ... env`; `kubectl describe pod` without cleartext; resources in values (see runbook §2–3). |
| **3 — Vault** | Helm install Vault dev + injector; KV + K8s auth + policy + role; pod with sidecar; files under `/vault/secrets` (see runbook §4). |
| **4 — Documentation** | Paste evidence into [`k8s/SECRETS.md`](../k8s/SECRETS.md) or attach screenshots per checklist there. |
| **Bonus** | Custom template file + annotations; Agent refresh / `agent-inject-command` notes; `_helpers.tpl` `containerEnv` + `include` (see runbook §6). |

---

## Testing & validation (local)

From the `project/` directory:

```bash
helm lint k8s/devops-info-service

helm template lab k8s/devops-info-service \
  -f k8s/devops-info-service/values.yaml \
  -f k8s/devops-info-service/values-dev.yaml

# With Vault annotations and custom template (requires chart files/ present)
helm template lab k8s/devops-info-service \
  -f k8s/devops-info-service/values.yaml \
  -f k8s/devops-info-service/values-dev.yaml \
  -f k8s/devops-info-service/values-vault.yaml
```

Inspect rendered `Secret`, `Deployment` annotations, and `ServiceAccount` in the output.

---

## Security notes (production)

- **Do not** use Vault `server.dev.enabled=true` or a logged **root token** in production.
- Prefer **etcd encryption**, strict **RBAC**, and a dedicated secret platform (Vault, cloud secret manager, External Secrets Operator) as required by policy.
- **Base64** in Kubernetes Secret objects is **not** confidentiality; treat API and backup access as sensitive.

---

## Further reading

- Evidence runbook & screenshot list: [`k8s/SECRETS.md`](../k8s/SECRETS.md)
- Lecture notes: [`lectures/lec11.md`](../../lectures/lec11.md)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Vault Helm chart](https://developer.hashicorp.com/vault/docs/platform/k8s/helm)
- [Vault Agent Injector annotations](https://developer.hashicorp.com/vault/docs/platform/k8s/injector/annotations)
