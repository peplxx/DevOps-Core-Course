FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=1 \
    UV_NO_DEV=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.29 /uv /uvx /bin/

RUN groupadd --system --gid 10001 app && \
    useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/app --shell /usr/sbin/nologin app


COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project && rm -rf /root/.cache/uv && chown -R app:app /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

COPY app/ ./app/

RUN mkdir -p /data && chown app:app /data

EXPOSE 5000

USER app

CMD ["uv", "run", "-m", "app"]
