#!/usr/bin/env bash
# Interactive six-chapter demo. Press Enter after each chapter.
# Do not print environment values. Do not call the network.
set -euo pipefail
unset HF_TOKEN DEEPSEEK_API_KEY HUGGING_FACE_HUB_TOKEN OPENAI_API_KEY 2>/dev/null || true
HERE="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
if [ -n "${G14_PYTHON:-}" ]; then
  PY="$G14_PYTHON"
elif [ -x /workspace/g14-local-main/venv/bin/python ]; then
  PY=/workspace/g14-local-main/venv/bin/python
else
  PY="$(command -v python3)"
fi
exec "$PY" "$HERE/run_core_demo.py" --all "$@"
