FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap

WORKDIR /opt/sqlmap
ENTRYPOINT ["python", "sqlmap.py"]
