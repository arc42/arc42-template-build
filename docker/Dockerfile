# Simplified for PoC - only EN, DE support needed initially

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    # Essential tools
    curl wget git make zip \
    # Ruby for Asciidoctor
    ruby ruby-dev build-essential \
    # Python for orchestrator
    python3 python3-pip \
    # Pandoc for DOCX
    pandoc \
    # Basic fonts (EN/DE don't need special fonts)
    fonts-liberation fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Asciidoctor
RUN gem install asciidoctor:2.0.20 asciidoctor-pdf:2.3.10

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
