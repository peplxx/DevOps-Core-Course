# Lab 12 — ConfigMaps & persistent volumes

This document describes how the DevOps Info Service was extended for **externalized configuration** (ConfigMaps) and **durable storage** (PVC) for the visit counter. The canonical evidence workbook (screenshot checklist, verification commands, ConfigMap vs Secret) lives in **[`k8s/CONFIGMAPS.md`](../k8s/CONFIGMAPS.md)**.

Course lab spec: [`labs/lab12.md`](../../labs/lab12.md) (repository root).

---

## Objectives

- Persist a **visit counter** to disk (`/data/visits` by default), increment on `GET /`, expose `GET /visits`.
- Prove persistence **locally** with Docker Compose and a bind-mounted `./data` directory.
- Ship **Helm-managed ConfigMaps**: one built from `files/config.json` via `.Files.Get` and mounted under `/config`; a second with key/value pairs injected through **`envFrom` + `configMapRef`**.
- Provision a **PersistentVolumeClaim** (`ReadWriteOnce`), mount it at `/data`, and verify the counter survives **pod deletion** (not Deployment deletion).
- Document behavior and evidence; contrast **ConfigMap vs Secret** for sensitive data.

---

## Application (Task 1)

| Location | Notes |
|----------|--------|
| [`app_python/app/visits.py`](../app_python/app/visits.py) | File-backed counter; `VISITS_FILE` env overrides path. |
| [`app_python/app/app.py`](../app_python/app/app.py) | `GET /` increments; `GET /visits` returns `{"visits": n}`. |
| [`app_python/docker-compose.yml`](../app_python/docker-compose.yml) | `volumes: ./data:/data`, `VISITS_FILE=/data/visits`. |
| [`app_python/README.md`](../app_python/README.md) | Visit counter and Compose usage. |

---

## Chart overview (after Lab 12)

Chart path: `k8s/devops-info-service/` (run Helm from the **`project/`** directory).

```
k8s/devops-info-service/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── values-vault.yaml
├── files/
│   ├── config.json                 # Embedded into ConfigMap via Helm .Files.Get
│   └── vault-agent-template.tpl   # Lab 11 Vault Agent (optional)
└── templates/
    ├── _helpers.tpl                 # Labels, fullname, containerEnv (HOST, PORT, VISITS_FILE)
    ├── deployment.yaml              # Volumes: ConfigMap + PVC or emptyDir; envFrom Secret + ConfigMap
    ├── configmap.yaml               # …-config (file) and …-env (keys for envFrom)
    ├── pvc.yaml                     # PVC when persistence.enabled
    ├── secrets.yaml                 # Opaque Secret for credentials (Lab 11); required by deployment envFrom
    ├── serviceaccount.yaml
    ├── service.yaml
    ├── NOTES.txt
    └── hooks/
        ├── pre-install-job.yaml
        └── post-install-job.yaml
```

| File | Purpose |
|------|---------|
| `files/config.json` | Non-sensitive app metadata and feature-style flags; rendered into the `…-config` ConfigMap. |
| `templates/configmap.yaml` | **`…-config`**: `config.json` key mounted as `/config/config.json`. **`…-env`**: `APP_ENV`, `LOG_LEVEL`, `APP_NAME` from values. |
| `templates/pvc.yaml` | Claim `…-data` when `persistence.enabled`; size and optional `storageClassName` from values. |
| `templates/deployment.yaml` | `volumeMounts` for `/config` and `/data`; `envFrom` for credentials Secret and env ConfigMap. |

---

## Configuration reference

### `application`

| Value | Default | Purpose |
|-------|---------|---------|
| `application.host` | `0.0.0.0` | `HOST` in container. |
| `application.port` | `5000` | `PORT` (align with probes). |
| `application.name` | `devops-info-service` | `APP_NAME` in the env ConfigMap. |

### `environment` / `logLevel`

| Value | Default | Purpose |
|-------|---------|---------|
| `environment` | `dev` | `APP_ENV` in the env ConfigMap. |
| `logLevel` | `info` | `LOG_LEVEL` in the env ConfigMap. |

### `persistence`

| Value | Default | Purpose |
|-------|---------|---------|
| `persistence.enabled` | `true` | Create PVC and mount it at `/data`; if `false`, use `emptyDir` at `/data`. |
| `persistence.size` | `100Mi` | PVC `resources.requests.storage`. |
| `persistence.storageClass` | `""` | Omit `storageClassName` when empty (cluster default). |

### Replicas and RWO

A **ReadWriteOnce** volume can attach to **one** pod at a time. Default `replicaCount` is `1` while persistence is enabled. For multi-replica installs (for example `values-prod.yaml`), `persistence.enabled` should be `false` unless your storage class supports **ReadWriteMany**.

---

## Task mapping (lab rubric)

| Lab task | What to show |
|----------|----------------|
| **1 — App persistence** | Counter file, `/visits`, Docker Compose volume, README; local restart proof (see [`k8s/CONFIGMAPS.md`](../k8s/CONFIGMAPS.md) §1). |
| **2 — ConfigMaps** | `files/config.json`, `configmap.yaml`, mount under `/config`, `envFrom` for `…-env`; `kubectl exec` for file and `printenv` (see runbook §2). |
| **3 — PVC** | `pvc.yaml`, bound PVC, `/data/visits`; delete **pod** only; counter unchanged (runbook §3). |
| **4 — Documentation** | Evidence in [`k8s/CONFIGMAPS.md`](../k8s/CONFIGMAPS.md); checklist table at end of that file. |
| **Bonus — Hot reload** | ConfigMap update delay, `subPath` limitation, checksum annotation or Reloader / file watch; optional section in runbook. |

---

## Testing & validation (local)

From the `project/` directory (run on your machine):

```bash
cd app_python && uv run pytest tests/ -q

cd ..   # back to project/
helm lint k8s/devops-info-service

helm template lab k8s/devops-info-service \
  -f k8s/devops-info-service/values.yaml \
  -f k8s/devops-info-service/values-dev.yaml
```

Inspect rendered `ConfigMap`, `PersistentVolumeClaim`, and `Deployment` volumes in the template output.

If `kubectl exec … -- cat /config/config.json` fails with **No such file or directory**, the cluster is usually still on an **older Deployment** (before the ConfigMap volume was added) or the ConfigMap has no `config.json` data key. See the troubleshooting block in [`k8s/CONFIGMAPS.md`](../k8s/CONFIGMAPS.md).

---

## Further reading

- Evidence runbook & screenshot list: [`k8s/CONFIGMAPS.md`](../k8s/CONFIGMAPS.md)
- Application README (Compose + `VISITS_FILE`): [`app_python/README.md`](../app_python/README.md)
- Lecture notes: [`lectures/lec12.md`](../../lectures/lec12.md)
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
