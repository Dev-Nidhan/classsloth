FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl zstd \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x scripts/render_start.sh

ENV OLLAMA_MODELS=/data/ollama \
    OLLAMA_MODEL=gemma3:4b \
    CLASSSLOTH_PUBLIC_DEMO=1 \
    CLASSSLOTH_NUM_CTX=4096 \
    CLASSSLOTH_TIMEZONE=UTC \
    CLASSSLOTH_DATA_DIR=/tmp/classsloth

CMD ["scripts/render_start.sh"]
