ARG IMAGE=python:3
FROM --platform=amd64 mcr.microsoft.com/devcontainers/${IMAGE}

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client \
     && apt-get update && apt-get install -y xdg-utils \
     && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://aka.ms/install-azd.sh | bash
