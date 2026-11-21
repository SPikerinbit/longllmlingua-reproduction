#!/usr/bin/env bash
# Usage: ./run_chapter.sh 1
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
CH="${1:?usage: run_chapter.sh 1-6}"
exec "$PY" "$HERE/run_core_demo.py" --chapter "$CH" --no-pause
