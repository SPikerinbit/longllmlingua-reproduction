#!/usr/bin/env bash
# Portable recheck of the full offline pytest suite. Not a new model run.
# Run from anywhere; paths are resolved relative to this file.
# Does not print environment variable values. Does not add tests.
set -euo pipefail
unset HF_TOKEN DEEPSEEK_API_KEY HUGGING_FACE_HUB_TOKEN OPENAI_API_KEY 2>/dev/null || true

HERE="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$HERE/../.." && pwd)"
cd "$ROOT"

if [ ! -f tests/test_stage1.py ] || [ ! -f manifests/resources.json ]; then
  echo "error: cannot locate repository root from $HERE" >&2
  exit 1
fi

echo "repo: $ROOT"
echo "HEAD: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "time: $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S %Z (Asia/Shanghai)')"
echo "This recheck is offline. It is not model inference."

if [ ! -f data/tokenizer/tokenizer.json ] || [ ! -f data/raw/nq-open-20_total_documents_gold_at_0.jsonl.gz ]; then
  echo "error: official data/tokenizer not present. From the repo root run: python -m reproduction prepare" >&2
  exit 2
fi

# Prefer the current interpreter if it already has pytest; otherwise python3.
if command -v python >/dev/null 2>&1 && python -c "import pytest,tokenizers" >/dev/null 2>&1; then
  PY=python
elif python3 -c "import pytest,tokenizers" >/dev/null 2>&1; then
  PY=python3
else
  echo "error: need a Python environment with pytest and tokenizers (see requirements-lock.txt)" >&2
  exit 3
fi

"$PY" -c "import sys; print('python:', sys.version.split()[0])"
"$PY" -c "import tokenizers; print('tokenizers:', tokenizers.__version__)"
"$PY" -m pytest -q --tb=line --junitxml="$HERE/recheck-junit.xml"
