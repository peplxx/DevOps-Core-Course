# LAB02 — Docker Containerization (Python)

This document covers containerizing the Lab 1 FastAPI service (`app_python/`) using Docker best practices and preparing it for publishing to Docker Hub.

---

## 1) Docker Best Practices Applied

### 1.1 Specific base image version

- **What**: `FROM python:3.13-slim`
- **Why it matters**:
  - Pinning a specific major/minor improves **reproducibility** (you don’t accidentally “upgrade” by rebuilding later).
  - `slim` significantly reduces image size vs the full Debian variant, while still being broadly compatible (unlike `alpine`, which can introduce musl/glibc and wheel/build issues).

### 1.2 Run as non-root (mandatory)

- **What**: Create a dedicated `app` user and switch via `USER app`.
- **Why it matters**:
  - If the application is compromised, a non-root user reduces damage (no write access to system paths, lower privilege escalation surface).
  - Many production platforms recommend/require non-root containers.

### 1.3 Minimal copy / least-privilege build context

- **What**:
  - Dockerfile copies only `pyproject.toml`, `uv.lock`, and `app/`.
  - `.dockerignore` excludes `docs/`, `tests/`, `.env`, virtualenvs, caches, VCS data, etc.
- **Why it matters**:
  - Smaller build context → faster builds.
  - Less accidental leakage (e.g., `.env` secrets).
  - Smaller final image → fewer attack surface + faster pull/deploy.

### 1.4 Layer ordering for caching

- **What**:
  - Copy `pyproject.toml` + `uv.lock` and run `uv sync` **before** copying application code.
- **Why it matters**:
  - Dependency install is usually the slowest step.
  - When code changes but dependencies don’t, Docker reuses the cached dependency layer → rebuilds become much faster.

### 1.5 Container-friendly runtime settings

- **What**:
  - `PYTHONUNBUFFERED=1` for immediate logs
  - `PYTHONDONTWRITEBYTECODE=1` to avoid `.pyc` writes
  - Avoid installer caches (`PIP_NO_CACHE_DIR=1`, `UV_NO_CACHE=1`)
- **Why it matters**:
  - Better observability (logs show up immediately).
  - Fewer filesystem writes and less image bloat.

### 1.6 Document the port

- **What**: `EXPOSE 5000`
- **Why it matters**:
  - It’s documentation for humans and tooling about the intended port.
  - (It does not publish the port by itself; `docker run -p ...` does.)

### 1.7 Dockerfile snippet (key parts)

```dockerfile
FROM python:3.13-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.29 /uv /uvx /bin/

RUN groupadd --system --gid 10001 app && \
    useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/app --shell /usr/sbin/nologin app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY app/ ./app/
USER app
CMD ["uv", "run", "-m", "app"]
```

---

## 2) Image Information & Decisions

### 2.1 Base image choice

- **Chosen**: `python:3.13-slim`
- **Reasoning**:
  - Small(er) but still Debian-based → good compatibility with Python packaging.
  - Aligns with the lab’s recommended images and keeps runtime predictable.

### 2.2 Final image size

Paste the output of:

```bash
docker image ls | head
```

**Output:**

```text
# TODO: paste output here
```

### 2.3 Layer structure

Inspect layers with:

```bash
docker history --no-trunc <image:tag>
```

**Notes / assessment:**

- The dependency layer (`uv sync ...`) should be stable across code-only changes.
- The app code layer should be small (only `app/`).

---

## 3) Build & Run Process

### 3.1 Build (local)

Build from the `project/app_python/` directory:

```bash
docker build -t <name>:<tag> .
```

**Terminal output (build):**

```text
# TODO: paste build output here
```

### 3.2 Run container

Run with port publishing:

```bash
docker run --rm -p <host_port>:5000 --name <container_name> <name>:<tag>
```

**Terminal output (container logs):**

```text
# TODO: paste container logs here
```

### 3.3 Test endpoints (from host)

```bash
curl http://localhost:<host_port>/
curl http://localhost:<host_port>/health
```

**Terminal output (curl):**

```text
# TODO: paste curl output here
```

### 3.4 Docker Hub (push / pull)

#### Tagging strategy

- Repository: `<dockerhub_user>/<repo>`
- Tags:
  - `lab02` for the lab submission
  - optionally `latest` for convenience

#### Push

```bash
docker login
docker tag <name>:<tag> <dockerhub_user>/<repo>:<tag>
docker push <dockerhub_user>/<repo>:<tag>
```

**Terminal output (push):**

```text
# TODO: paste push output here
```

#### Docker Hub URL

`https://hub.docker.com/r/<dockerhub_user>/<repo>`

#### Pull and run (verification)

```bash
docker pull <dockerhub_user>/<repo>:<tag>
docker run --rm -p <host_port>:5000 <dockerhub_user>/<repo>:<tag>
```

**Terminal output (pull/run):**

```text
# TODO: paste pull/run output here
```

---

## 4) Technical Analysis

### 4.1 Why this Dockerfile works

- `WORKDIR /app` ensures `python -m app` runs with the expected project layout.
- Installing dependencies before copying code reduces rebuild time due to Docker’s layer cache.
- `USER app` enforces non-root execution at runtime.

### 4.2 What happens if you change layer order?

- If you `COPY app/` **before** installing dependencies, then every code change invalidates the dependency cache.
- That forces Docker to reinstall dependencies on every rebuild → slower iteration and heavier CI usage.

### 4.3 Security considerations implemented

- Non-root container user with a fixed UID/GID.
- `.dockerignore` excludes `.env` and other sensitive local artifacts from the build context.
- Minimal file copy reduces the chance of shipping secrets or unnecessary tooling into production.

### 4.4 How `.dockerignore` improves builds

- Build context size drops, so Docker sends less data to the daemon.
- Fewer invalidations from changing dev-only files (docs, tests, caches) → better caching.

---

## 5) Challenges & Solutions

Document anything that came up during your build/push workflow:

- **Issue**: (e.g., permission errors due to non-root user)
  - **Fix**:
  - **What I learned**:
- **Issue**: (e.g., wrong port mapping)
  - **Fix**:
  - **What I learned**:

