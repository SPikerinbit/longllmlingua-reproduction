#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs outputs/cloud/efficiency-final-session
if [ -f outputs/cloud/environment.json ] && [ ! -f outputs/cloud/efficiency-final-session/environment-before-check.json ]; then
  cp outputs/cloud/environment.json outputs/cloud/efficiency-final-session/environment-before-check.json
fi
python scripts/cloud910b.py check
cp outputs/cloud/environment.json outputs/cloud/efficiency-final-session/environment-current.json
npu-smi info > outputs/cloud/efficiency-final-session/npu-smi.txt
python - <<'PY'
import importlib.metadata as m
import json
from pathlib import Path
versions = {d.metadata['Name']: d.version for d in m.distributions() if d.metadata['Name']}
Path('outputs/cloud/efficiency-final-session/package-versions.json').write_text(json.dumps(versions,indent=2))
PY
python scripts/cloud910b.py run --config configs/cloud/efficiency-final.json 2>&1 | tee logs/efficiency-final.log
python scripts/cloud910b.py analyze --config configs/cloud/efficiency-final.json 2>&1 | tee logs/efficiency-final-analysis.log
python scripts/cloud910b.py export --out /home/ma-user/work/stage4-final-return.tar.gz
