#!/bin/sh
set -eu

mkdir -p "${OLLAMA_MODELS:-/data/ollama}" "${CLASSSLOTH_DATA_DIR:-/tmp/classsloth}"

# Bind Ollama to localhost only, then point the app at that address.
OLLAMA_HOST=127.0.0.1:11434 ollama serve &

export OLLAMA_HOST=http://127.0.0.1:11434
(
  ready=0
  i=0
  while [ "$i" -lt 30 ]; do
    if curl -sf "${OLLAMA_HOST}/api/tags" >/dev/null; then
      ready=1
      break
    fi
    i=$((i + 1))
    sleep 2
  done
  if [ "$ready" -eq 1 ]; then
    ollama pull "${OLLAMA_MODEL:-gemma3:4b}"
  fi
) &

exec streamlit run app.py \
  --server.port "${PORT:-8501}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
