# Lab 13 — GitOps with ArgoCD

This document describes the GitOps implementation for the DevOps Info Service using **ArgoCD 2.13+**. All ArgoCD Application manifests live in [`k8s/argocd/`](../k8s/argocd/).

Course lab spec: [`labs/lab13.md`](../../labs/lab13.md) (repository root).

---

## Objectives

- Install ArgoCD via Helm and access the management UI and CLI.
- Deploy the `devops-info-service` Helm chart through an ArgoCD Application manifest.
- Implement multi-environment deployment (`dev` / `prod`) with different sync policies.
- Observe and document ArgoCD self-healing and configuration drift detection.
- (Bonus) Replace individual Application manifests with an ApplicationSet.

---

## ArgoCD Setup

### Installation

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

kubectl create namespace argocd
helm install argocd argo/argo-cd --namespace argocd

kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server \
  -n argocd --timeout=300s
```

### UI Access

```bash
# Terminal 1 — keep running
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Terminal 2 — retrieve password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

Open **https://localhost:8080**, login as `admin` with the retrieved password.

### CLI

```bash
brew install argocd   # macOS

argocd login localhost:8080 --insecure \
  --username admin \
  --password $(kubectl -n argocd get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d)

argocd app list
```

---

## Manifests Overview

```
k8s/argocd/
├── application.yaml          # default namespace — manual sync  (Task 2)
├── application-dev.yaml      # dev namespace    — auto-sync     (Task 3)
├── application-prod.yaml     # prod namespace   — manual sync   (Task 3)
└── applicationset.yaml       # List generator for dev + prod    (Bonus)
```

All manifests point at the same Helm chart (`project/k8s/devops-info-service`) on branch `feat/lab13`.

### Key design decisions

| Decision | Reason |
|----------|--------|
| Explicit `helm.releaseName` (`app`, `dev`, `prod`) | Avoids double-name collision from `{appName}-{chartName}` default |
| `values.yaml` always listed first in `valueFiles` | Dev/prod override files only contain deltas; base file provides required keys (`credentials`, `application`, `securityContext`, `strategy`) |
| `RespectIgnoreDifferences=true` in every `syncPolicy` | Helm hook Jobs (`hook-delete-policy: hook-succeeded`) delete themselves after success; without this option ArgoCD would flag the missing Jobs as OutOfSync on the next reconcile |

---

## Application Deployment (Task 2)

```bash
# Apply and sync
kubectl apply -f k8s/argocd/application.yaml
argocd app sync devops-info-service

# Verify
argocd app get devops-info-service
kubectl get pods -n default
```

### GitOps workflow test

Make a change to `values.yaml` (e.g. `replicaCount: 2`), commit and push. ArgoCD polls Git every **3 minutes** and will show the app as **OutOfSync**. Sync manually to apply:

```bash
argocd app diff devops-info-service
argocd app sync devops-info-service
```

---

## Multi-Environment Deployment (Task 3)

### Environment configuration differences

| Setting | `values.yaml` | `values-dev.yaml` | `values-prod.yaml` |
|---------|--------------|-------------------|--------------------|
| Replicas | 3 | 1 | 5 |
| CPU limit | 200m | 100m | 500m |
| Memory limit | 256Mi | 128Mi | 512Mi |
| Service type | NodePort | NodePort | LoadBalancer |
| Image tag | latest | latest | 1.0.0 |

> **Note:** `LoadBalancer` in `values-prod.yaml` will show `EXTERNAL-IP: <pending>` on a local cluster. The app is still reachable via the assigned NodePort.

### Sync policy rationale

| Environment | Policy | Why |
|-------------|--------|-----|
| dev | `automated` + `selfHeal: true` + `prune: true` | Continuous delivery — every Git push auto-deploys |
| prod | Manual | Every production change is a deliberate human action: audit trail, controlled rollout timing, rollback planning |

### Deploy

```bash
kubectl create namespace dev
kubectl create namespace prod

kubectl apply -f k8s/argocd/application-dev.yaml
kubectl apply -f k8s/argocd/application-prod.yaml

# dev auto-syncs; prod needs a manual trigger
argocd app sync devops-info-service-prod

kubectl get pods -n dev
kubectl get pods -n prod
argocd app list
```

---

## Self-Healing (Task 4)

The dev application has `selfHeal: true`. Any manual change to cluster state is reverted within ~30 seconds.

### Manual scale test

```bash
# Scale to 5 — drifts from Git-defined 1 replica
kubectl scale deployment dev-devops-info-service -n dev --replicas=5

# Watch ArgoCD revert it
kubectl get pods -n dev -w
```

### Pod deletion test

```bash
kubectl delete pod -n dev -l app.kubernetes.io/instance=dev
kubectl get pods -n dev -w
```

This is **Kubernetes ReplicaSet healing** (immediate pod recreation), not ArgoCD. ArgoCD self-healing only fires when the Deployment *spec* drifts from Git.

### Configuration drift test

```bash
kubectl label deployment dev-devops-info-service -n dev test-label=manual-drift
argocd app diff devops-info-service-dev   # shows the label as live drift
# selfHeal reverts within ~30s
```

### Sync behaviour summary

| Trigger | Handler | Latency |
|---------|---------|---------|
| Git change + `automated` policy | ArgoCD | ~3 min poll (or instant with webhook) |
| Manual `argocd app sync` | ArgoCD | Immediate |
| Pod crash / deletion | Kubernetes ReplicaSet | Immediate |
| Manual cluster change + `selfHeal` | ArgoCD | ~30 s |

---

## Bonus — ApplicationSet

`k8s/argocd/applicationset.yaml` uses the **List generator** to produce `devops-info-service-dev` and `devops-info-service-prod` from a single template.

```bash
# Remove individual env apps; ApplicationSet recreates them
argocd app delete devops-info-service-dev --yes
argocd app delete devops-info-service-prod --yes

kubectl apply -f k8s/argocd/applicationset.yaml
argocd app list
```

### Generator comparison

| Generator | Best for |
|-----------|----------|
| List | Fixed, explicitly named environments |
| Git (directory) | Auto-discovery of apps from folder structure |
| Cluster | Multi-cluster fleet deployments |
| Matrix | Cartesian product of two generators (e.g. env × cluster) |

### ApplicationSet vs individual Applications

| | Individual Applications | ApplicationSet |
|-|------------------------|----------------|
| Adding an environment | New YAML file | One extra list element |
| Consistency | Each file can drift independently | Single template enforces uniformity |
| Conditional sync policy | Easy per-file | Requires two separate ApplicationSets or a Matrix generator workaround |

---

## Task mapping

| Lab task | Points | Manifests / commands |
|----------|--------|----------------------|
| ArgoCD installation & setup | 2 pts | `helm install argocd`, port-forward, CLI login |
| Application deployment | 3 pts | `k8s/argocd/application.yaml`, initial sync, GitOps drift test |
| Multi-environment deployment | 3 pts | `application-dev.yaml`, `application-prod.yaml`, `dev`/`prod` namespaces |
| Self-healing & documentation | 2 pts | Scale test, pod deletion test, drift test |
| Bonus — ApplicationSet | 2.5 pts | `k8s/argocd/applicationset.yaml` |

---

## Further reading

- ArgoCD manifests: [`k8s/argocd/`](../k8s/argocd/)
- Helm chart: [`k8s/devops-info-service/`](../k8s/devops-info-service/)
- Lecture notes: [`lectures/lec13.md`](../../lectures/lec13.md)
- [ArgoCD documentation](https://argo-cd.readthedocs.io/)
- [Automated sync policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [ApplicationSet](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/)
