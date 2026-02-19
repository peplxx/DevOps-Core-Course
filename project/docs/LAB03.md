## Overview

This lab adds **unit tests** and a **CI/CD pipeline** for the Python service.

- **Testing framework**: `pytest`
  - **Why**: concise assertions, fixtures (FastAPI `TestClient`), and strong ecosystem.
- **What is tested**:
  - `GET /`: response JSON schema/required fields and basic type/contract checks.
  - `GET /health`: response JSON schema/required fields and basic type/contract checks.
  - Error cases: `GET` unknown path returns custom `404` JSON; `POST /health` returns `405`.

## How to run tests locally

From repo root:

```bash
cd project/app_python
uv sync --dev
uv run pytest
```

Or:

```bash
cd project/app_python
make install
make test
```

## CI workflow

- **Workflow file**: `.github/workflows/python-ci.yml`
- **Triggers**:
  - `push` to `master`
  - `pull_request` targeting `master`
  - **Path filter**: only when `project/app_python/**` or the workflow file changes
- **Stages**:
  - **Lint + tests**: ruff + pytest (matrix: Python 3.11, 3.12)
  - **Security scan**: Snyk dependency scan (only on `master` pushes)
  - **Docker build & push**: handled by the existing workflow `.github/workflows/docker-release.yml` (runs on `v*` tags)

## Required GitHub Secrets

Add these repository secrets for the CI workflow:

- **`DOCKERHUB_USERNAME`**: your Docker Hub username
- **`DOCKERHUB_TOKEN`**: Docker Hub access token (not your password)
- **`SNYK_TOKEN`**: Snyk API token (optional but required to enable Snyk step)

## Versioning strategy (SemVer)

Chosen strategy: **Semantic Versioning (SemVer)** using git tags `vMAJOR.MINOR.PATCH`.

Why SemVer fits here:
- It’s a service with explicit releases; tags map cleanly to Docker image versions.
- It produces predictable Docker tags for rollbacks.

Docker image tags produced by CI:
- On `v1.2.3` tag: `v1.2.3` and `latest` (see `.github/workflows/docker-release.yml`)

## CI best practices applied

- **Dependency caching**: uv cache persisted via `astral-sh/setup-uv`.
- **Matrix testing**: validates on multiple Python versions (3.11/3.12).
- **Concurrency control**: cancels outdated in-progress runs for the same branch/ref.
- **Job dependencies**: Docker publish job runs only if lint/tests succeed.
- **Least privilege**: workflow defaults to read-only `contents` permissions.

## Snyk integration

- **Secret required**: `SNYK_TOKEN` (GitHub Actions secret)
- **Command**: `uv export ... -> snyk test --file=requirements-ci.txt --package-manager=pip`
- **Notes**:
  - Runs only on `push` to `master` (so secrets aren’t required on PRs).

## Workflow evidence (fill after pushing)

- **Successful workflow run**: `<paste GitHub Actions run link here>`
- **Docker Hub image**: `<paste Docker Hub repo link here>`
- **Local tests output**:

```text
4 passed in 0.01s
```

