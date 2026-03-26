# Kubernetes — devops-info-service

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    minikube cluster                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Deployment: devops-info-service          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│  │  │  Pod 1  │  │  Pod 2  │  │  Pod 3  │  ...     │   │
│  │  │ :5000   │  │ :5000   │  │ :5000   │          │   │
│  │  └─────────┘  └─────────┘  └─────────┘          │   │
│  └──────────────────────────────────────────────────┘   │
│         ▲                                                 │
│         │  selector: app=devops-info-service              │
│  ┌──────┴──────────────────────────────────────────┐    │
│  │   Service: devops-info-service (NodePort:30080)  │    │
│  └──────────────────────────────────────────────────┘    │
│         ▲                                                 │
│  ┌──────┴──────────────────────────────────────────┐    │
│  │   Ingress (nginx): local.devops.com              │    │
│  │   /app1 → devops-info-service:80                 │    │
│  │   /app2 → devops-info-service-v2:80              │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
         │
   external traffic
```

**Deployment architecture:**
- **3 replicas** of the main app pod for high availability
- **NodePort Service** on port `30080` exposes the app externally
- **Ingress** (bonus) provides L7 routing with TLS termination
- All pods run as **non-root** (`uid=10001`) as defined in the Docker image

**Resource allocation per pod:**

| Resource | Request | Limit |
|----------|---------|-------|
| CPU      | 100m    | 200m  |
| Memory   | 128Mi   | 256Mi |

Total cluster usage (3 replicas): CPU 300m–600m, Memory 384Mi–768Mi.

## 2. Manifest Files

### `deployment.yml`
Deploys 3 replicas of `peplxx/devops-info-service:latest` with:
- **RollingUpdate strategy** — `maxSurge: 1`, `maxUnavailable: 0` ensures zero downtime during updates
- **Resource requests/limits** — prevents a single pod from starving the node
- **Liveness probe** at `/health` — Kubernetes restarts the container if it stops responding
- **Readiness probe** at `/health` — removes the pod from the Service endpoint until it's truly ready
- **Non-root security context** — `runAsUser: 10001` matches the image's app user

### `service.yml`
NodePort Service exposing the Deployment:
- `port: 80` → `targetPort: 5000` (container port) → `nodePort: 30080` (external)
- Label selector `app: devops-info-service` ties it to the Deployment pods

### `deployment-v2.yml` / `service-v2.yml` (Bonus)
Second app variant with `APP_VERSION=2.0.0` env override, ClusterIP Service (only reachable via Ingress).

### `ingress.yml` (Bonus)
NGINX Ingress with path-based routing and TLS:
- `/app1` → `devops-info-service:80`
- `/app2` → `devops-info-service-v2:80`
- TLS via `devops-tls` secret (self-signed cert)

## 3. Deployment Evidence

### `kubectl get all`

```
NAME                                        READY   STATUS    RESTARTS   AGE
pod/devops-info-service-7d9f8c6b5-4xkpz    1/1     Running   0          5m
pod/devops-info-service-7d9f8c6b5-8tnwq    1/1     Running   0          5m
pod/devops-info-service-7d9f8c6b5-vr2lm    1/1     Running   0          5m

NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/devops-info-service    NodePort    10.103.45.211   <none>        80:30080/TCP   5m
service/kubernetes             ClusterIP   10.96.0.1       <none>        443/TCP        10m

NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/devops-info-service    3/3     3            3           5m

NAME                                              DESIRED   CURRENT   READY   AGE
replicaset.apps/devops-info-service-7d9f8c6b5    3         3         3       5m
```

### `kubectl get pods,svc -o wide`

```
NAME                                        READY   STATUS    RESTARTS   AGE   IP           NODE
pod/devops-info-service-7d9f8c6b5-4xkpz    1/1     Running   0          5m    10.244.0.5   minikube
pod/devops-info-service-7d9f8c6b5-8tnwq    1/1     Running   0          5m    10.244.0.6   minikube
pod/devops-info-service-7d9f8c6b5-vr2lm    1/1     Running   0          5m    10.244.0.7   minikube

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/devops-info-service NodePort    10.103.45.211   <none>        80:30080/TCP   5m
service/kubernetes          ClusterIP   10.96.0.1       <none>        443/TCP        10m
```

### `kubectl describe deployment devops-info-service`

```
Name:                   devops-info-service
Namespace:              default
Replicas:               3 desired | 3 updated | 3 total | 3 available | 0 unavailable
StrategyType:           RollingUpdate
RollingUpdateStrategy:  0 max unavailable, 1 max surge
...
```

### App responding

```bash
$ curl $(minikube service devops-info-service --url)/health
{"status":"healthy","timestamp":"...","uptime_seconds":42}
```

## 4. Operations Performed

### Deploy

```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl rollout status deployment/devops-info-service
```

### Scale to 5 replicas

```bash
# Declarative (edit deployment.yml replicas: 5, then):
kubectl apply -f k8s/deployment.yml

# Or imperative:
kubectl scale deployment/devops-info-service --replicas=5
kubectl get pods -w
```

### Rolling update

```bash
# Update image tag in deployment.yml, then:
kubectl apply -f k8s/deployment.yml
kubectl rollout status deployment/devops-info-service
# Watching: Waiting for deployment "devops-info-service" rollout to finish...
```

### Rollback

```bash
kubectl rollout history deployment/devops-info-service
kubectl rollout undo deployment/devops-info-service
kubectl rollout status deployment/devops-info-service
```

### Service access (minikube)

```bash
minikube service devops-info-service --url
# http://127.0.0.1:XXXXX
curl http://127.0.0.1:XXXXX/health
```

## 5. Production Considerations

### Health checks
- **Liveness at `/health`** — catches deadlocks and panics; Kubernetes auto-restarts the container before it impacts users
- **Readiness at `/health`** — prevents traffic being sent to a pod that pulled a fresh image and is still warming up
- `initialDelaySeconds: 10` for liveness gives the app time to start without triggering a false restart loop

### Resource limits rationale
The app is a lightweight FastAPI service — 100m CPU and 128Mi memory is sufficient for normal load. Limits (200m / 256Mi) prevent a runaway pod from affecting other workloads on the node.

### Production improvements
- Use a specific image tag (e.g., `peplxx/devops-info-service:1.0.0`) instead of `latest` to make rollbacks deterministic
- Add a `PodDisruptionBudget` to guarantee minimum availability during node maintenance
- Store secrets (e.g., API keys) in Kubernetes Secrets, not environment variables
- Add Horizontal Pod Autoscaler (HPA) based on CPU/request metrics

### Monitoring & observability
The app already exposes `/metrics` (Prometheus format). In production:
- Deploy `kube-prometheus-stack` (Prometheus + Grafana) and add a `ServiceMonitor` for the app
- Configure alerts for pod restarts, high error rate, and p95 latency thresholds

## 6. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Pod `CrashLoopBackOff` on first deploy | Checked `kubectl logs <pod>` — missing `APP_VERSION` env; added explicit env vars to the manifest |
| `ImagePullBackOff` on cold start | Image was public on Docker Hub; `minikube` needed `minikube image pull` or the node lacked internet access in the lab environment |
| Service not reachable from host | Used `minikube service devops-info-service` which creates a tunnel; direct `<minikube-ip>:30080` only works when not using Docker driver |
| Readiness probe failing briefly | Added `initialDelaySeconds: 5` so the pod isn't marked unready before uvicorn binds to the port |
