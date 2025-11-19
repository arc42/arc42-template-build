# Stage 1: Base tools with comprehensive font support
FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
# Ensure Asciidoctor PDF uses our fonts
ENV RUBYOPT="-Eutf-8"

# Install system dependencies and ALL required fonts
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl wget git make zip unzip \
    # Ruby for Asciidoctor
    ruby ruby-dev build-essential \
    # Python for orchestrator
    python3.11 python3-pip python3-venv \
    # Pandoc for format conversions
    pandoc \
    # Font management tools
    fontconfig \
    # ============ COMPREHENSIVE FONT INSTALLATION ============ \
    # Core Latin fonts (EN, DE, CZ base support)
    fonts-liberation \
    fonts-dejavu-core \
    fonts-liberation2 \
    # Noto fonts - Google's comprehensive Unicode font family
    fonts-noto-core \
    # Basic Latin + extensions
    fonts-noto-ui-core \
    # UI variants with better screen rendering
    fonts-noto-extra \
    # Additional scripts
    # CJK (Chinese, Japanese, Korean) fonts
    fonts-noto-cjk \
    # Main CJK fonts
    fonts-noto-cjk-extra \
    # Additional CJK variants
    # Specific Chinese fonts (ZH)
    fonts-wqy-microhei \
    # WenQuanYi Chinese font
    fonts-wqy-zenhei \
    # Alternative Chinese font
    # Cyrillic fonts (RU, UKR)
    fonts-noto \
    # Includes Cyrillic
    # Czech specific (CZ) - Latin Extended-A
    fonts-freefont-ttf \
    # Good Czech support
    # Monospace fonts for code blocks
    fonts-noto-mono \
    # Noto Mono for all scripts
    fonts-firacode \
    # Programming font with ligatures
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Update font cache
    && fc-cache -f -v

# Install Asciidoctor and extensions with specific versions
RUN gem install asciidoctor:2.0.20 \
    asciidoctor-pdf:2.3.10 \
    asciidoctor-diagram:2.2.14
    # Note: asciidoctor-confluence removed - gem not available/working

# Copy custom PDF themes and fonts (if any)
# This allows adding commercial or special fonts not in Ubuntu repos
COPY docker/custom-fonts/ /usr/share/fonts/truetype/custom/
COPY docker/pdf-themes/ /opt/arc42/pdf-themes/

# Rebuild font cache with custom fonts
RUN fc-cache -f -v && \
    # Verify critical fonts are installed
    fc-list | grep -i noto > /tmp/font-check.txt && \
    echo "Installed Noto fonts:" && cat /tmp/font-check.txt

# Stage 2: Python environment
FROM base AS python-env

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM python-env AS app

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY tests/ /app/tests/
COPY pytest.ini /app/pytest.ini

# Set Python path to find the module
ENV PYTHONPATH=/app

# Create directories for templates and outputs
RUN mkdir -p /workspace /workspace/build /workspace/dist /workspace/logs

# Set working directory
WORKDIR /workspace

# Entry point
ENTRYPOINT ["python3", "-m", "src.arc42_builder"]
CMD ["--help"]