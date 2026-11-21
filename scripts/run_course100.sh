#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
for config in pilot-ablation efficiency; do
  python scripts/cloud910b.py run --config "configs/cloud/$config.json" 2>&1 | tee "logs/course100-$config.log"
  python scripts/cloud910b.py analyze --config "configs/cloud/$config.json" 2>&1 | tee "logs/course100-$config-analysis.log"
done
python scripts/cloud910b.py export --out stage4-return.tar.gz
