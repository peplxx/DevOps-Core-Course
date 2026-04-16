# Lab 12 — ConfigMaps and persistent volumes

Overview, chart layout, and values reference: **[`docs/LAB12.md`](../docs/LAB12.md)**.

This document summarizes application changes, Helm resources, and the evidence to attach for grading (terminal output screenshots or pasted logs).

## 1. Application changes

### Visit counter

- Each `GET /` increments an integer stored in a text file (default `/data/visits`, configurable with env `VISITS_FILE`).
- Writes use a temporary file plus rename for an atomic update; a `threading.Lock` guards read-modify-write under concurrent requests.
- `GET /visits` returns `{"visits": <n>}` without incrementing the counter.

### Local Docker evidence

1. From `app_python/`: `docker compose up --build`
2. Call `/` several times, then `curl -s http://localhost:5000/visits`
3. Show `cat ./data/visits` matching the counter
4. `docker compose restart` and call `/visits` again to show the value survived

*(Paste terminal output or screenshots here.)*

---

## 2. ConfigMap implementation

### Chart layout

| Path | Role |
|------|------|
| `k8s/devops-info-service/files/config.json` | Source file embedded into the file-based ConfigMap via Helm `.Files.Get` |
| `k8s/devops-info-service/templates/configmap.yaml` | `…-config` (file data) and `…-env` (key/value for `envFrom`) |

### `config.json` (mounted at `/config/config.json`)

The chart ships JSON with application name, environment label, and feature-style flags. Inspect the live file in the cluster after install.

### Mount as files

The Deployment mounts the `…-config` ConfigMap as a volume at `/config` (read-only). Kubernetes exposes keys as files, so the payload appears as `/config/config.json`.

### Environment variables

The `…-env` ConfigMap holds keys such as `APP_ENV`, `LOG_LEVEL`, and `APP_NAME` (from `values.yaml`). The Deployment uses `envFrom` with `configMapRef` so every key becomes an environment variable in the container (in addition to credentials from the Secret).

### Verification commands

```bash
kubectl get configmap -l app.kubernetes.io/instance=<release-name>
kubectl exec deploy/<release-name>-devops-info-service -- cat /config/config.json
kubectl exec deploy/<release-name>-devops-info-service -- printenv | grep -E '^(APP_ENV|LOG_LEVEL|APP_NAME)='
```

*(Attach `kubectl get configmap,pvc` output, `cat /config/config.json`, and filtered `printenv` as required by the lab.)*

### Troubleshooting: `cat: /config/config.json: No such file or directory`

That almost always means the **running pod spec** does not match the Lab 12 chart (no `app-config` volume, or the ConfigMap has no `config.json` key).

1. **Confirm the Deployment mounts the ConfigMap**

   ```bash
   kubectl get deploy lab-info-devops-info-service -o yaml | grep -A3 'name: app-config'
   ```

   You should see a `volumes` entry `name: app-config` with `configMap.name: …-config` and a `volumeMounts` entry with `mountPath: /config`. If these are missing, upgrade the release from the chart that contains `templates/configmap.yaml`, `files/config.json`, and the updated `templates/deployment.yaml`:

   ```bash
   # from the project/ directory, chart path as you use it locally
   helm upgrade --install lab-info ./k8s/devops-info-service --wait
   ```

2. **Confirm the ConfigMap has the file key**

   ```bash
   kubectl get configmap lab-info-devops-info-service-config -o jsonpath='{.data}' | head -c 200
   kubectl get configmap lab-info-devops-info-service-config -o yaml
   ```

   Under `data:` you must see a key **`config.json`**. If `data:` is empty or the object is missing, the chart was not rendered with `files/config.json` on disk (wrong directory, old packaged chart without `files/`, or a fork without that file).

3. **List the mount inside the pod**

   ```bash
   kubectl exec deploy/lab-info-devops-info-service -- ls -la /config
   ```

   You should see `config.json` (often along with `..data` symlinks used by the kubelet). If `/config` itself is missing, the volume is not mounted on that pod template.

---

## 3. Persistent volume

### PVC

- Template: `templates/pvc.yaml` (created when `persistence.enabled` is true).
- Size: `values.persistence.size` (default `100Mi`).
- Access mode: `ReadWriteOnce` (single writer; chart default `replicaCount` is `1` while persistence is on).
- `storageClassName` is set only when `persistence.storageClass` is non-empty; otherwise the cluster default storage class is used (typical on Minikube).

### Mount

The Deployment mounts the PVC (or `emptyDir` if `persistence.enabled: false`) at `/data`. The app writes `VISITS_FILE=/data/visits` via Helm `containerEnv`.

### Persistence test (required evidence)

1. Note current count: `kubectl exec <pod> -- cat /data/visits` or `curl` via Service/ingress to `/visits`.
2. Delete only the pod: `kubectl delete pod <pod-name>`.
3. Wait for the Deployment to recreate the pod; repeat the read — the count must match.

*(Capture before value, the delete command + output, and after value.)*

---

## 4. ConfigMap vs Secret

| Use ConfigMap for | Use Secret for |
|-------------------|----------------|
| Non-sensitive config (flags, URLs, log levels, JSON app settings) | Passwords, API keys, TLS material, database credentials |
| Plaintext in etcd (still restrict RBAC) | Opaque or typed Secret objects; prefer encryption at rest + external secret managers for production |

ConfigMaps are not a confidentiality mechanism; they only separate configuration from the image.

---

## Bonus (optional): hot reload

If you complete the bonus: document kubelet sync delay after `kubectl edit configmap`, why `subPath` does not receive updates, your chosen reload approach (checksum annotation on the pod template, file watch, or Reloader), and show one successful reload.

---

## Screenshot and output checklist (Task 4)

| # | What to capture |
|---|-----------------|
| 1 | `kubectl get configmap,pvc` (wide output is fine) |
| 2 | `kubectl exec … -- cat /config/config.json` |
| 3 | `kubectl exec … -- printenv` filtered to injected ConfigMap keys (`APP_ENV`, `LOG_LEVEL`, `APP_NAME`, or similar) |
| 4 | Persistence: `/visits` or `cat /data/visits` **before** deleting the pod |
| 5 | `kubectl delete pod <name>` and confirmation |
| 6 | Same check **after** the new pod is ready — count unchanged |
| 7 | Docker Compose: `cat ./data/visits` after restarts (Task 1 evidence) |
