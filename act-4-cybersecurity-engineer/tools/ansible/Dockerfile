FROM python:3.12-slim

RUN pip install --no-cache-dir ansible-core==2.19.* \
    && apt-get update \
    && apt-get install -y --no-install-recommends openssh-client rsync \
    && rm -rf /var/lib/apt/lists/* \
    && ansible-galaxy collection install community.general ansible.posix community.docker

WORKDIR /repo/infra/ansible
