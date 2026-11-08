FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

ARG KUBESEAL_VERSION=0.41.2
RUN set -eux; \
    case "$(dpkg --print-architecture)" in \
      amd64) arch=amd64 ;; \
      arm64) arch=arm64 ;; \
      *) echo "unsupported architecture: $(dpkg --print-architecture)" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/kubeseal.tar.gz \
      "https://github.com/bitnami/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-${arch}.tar.gz"; \
    tar -xzf /tmp/kubeseal.tar.gz -C /usr/local/bin kubeseal; \
    rm /tmp/kubeseal.tar.gz; \
    chmod +x /usr/local/bin/kubeseal

WORKDIR /repo
ENTRYPOINT ["kubeseal"]
