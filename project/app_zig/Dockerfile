FROM debian:bookworm-slim AS builder

ARG ZIG_VERSION=0.15.2

WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xz-utils \
  && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
  arch="$(dpkg --print-architecture)"; \
  case "${arch}" in \
    amd64)  zig_arch="x86_64-linux" ;; \
    arm64)  zig_arch="aarch64-linux" ;; \
    *) echo "Unsupported arch: ${arch}" >&2; exit 1 ;; \
  esac; \
  url="https://ziglang.org/download/${ZIG_VERSION}/zig-${zig_arch}-${ZIG_VERSION}.tar.xz"; \
  curl -fsSL "${url}" -o /tmp/zig.tar.xz; \
  mkdir -p /opt/zig; \
  tar -xJf /tmp/zig.tar.xz -C /opt/zig --strip-components=1; \
  rm -f /tmp/zig.tar.xz

ENV PATH="/opt/zig:${PATH}"

COPY build.zig ./build.zig
COPY src/ ./src/

RUN zig build -Doptimize=ReleaseSmall


FROM debian:bookworm-slim

WORKDIR /app

RUN groupadd --system --gid 10001 app && \
    useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/app --shell /usr/sbin/nologin app

COPY --from=builder /src/zig-out/bin/devops-info-service /app/devops-info-service

EXPOSE 8080

USER app

CMD ["/app/devops-info-service"]
