# LAB02 — Multi-Stage Docker Build (Zig)

This document covers the Lab 02 bonus task: containerizing the compiled Zig implementation using a **multi-stage Docker build** to keep the final image small and secure.

---

## 1) Multi-stage build strategy

### Stage 1: Builder

- **Purpose**: download a pinned Zig toolchain and compile the binary.
- **Why**: build tools (compiler, headers, curl, etc.) are large and should not ship in production images.

### Stage 2: Runtime

- **Purpose**: run only the compiled `devops-info-service` binary.
- **Why**: smaller image → faster pulls/deployments and reduced attack surface.

---

## 2) Docker Best Practices Applied

- **Pinned Zig version**: `ARG ZIG_VERSION=0.15.2`
- **Multi-stage build**: separates build environment from runtime
- **Non-root runtime**: runs as a dedicated `app` user
- **Minimal copy**: final stage copies only the binary
- **.dockerignore**: excludes build artifacts (`zig-out/`, caches) and docs from build context

---

## 3) Build commands + image sizes

### Build (local)

```bash
docker build -t devops-info-service-zig:lab02 .
```

**Terminal output (build):**

```text
# TODO: paste output here
```

### Image size comparison

```bash
docker image ls | head
docker history --no-trunc devops-info-service-zig:lab02
```

**Output:**

```text
# TODO: paste output here
```

---

## 4) Run + test endpoints

The Zig service listens on port **8080** inside the container.

```bash
docker run --rm -p 8080:8080 --name devops-info-zig devops-info-service-zig:lab02
```

Test:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

**Terminal output (curl):**

```text
# TODO: paste output here
```

---

## 5) Technical analysis (why this works)

- Build stage installs Zig for the container architecture (amd64/arm64) and compiles using `zig build -Doptimize=ReleaseSmall`.
- Runtime stage is Debian slim to maximize compatibility (glibc). Only the binary is copied over.
- Running as non-root reduces the impact of any runtime compromise.

