#!/bin/sh
# Offline evidence only. Does not call DeepSeek or Cursor.
set -eu
cd "$(dirname "$0")/.."
python -m pytest \
  tests/test_stage4_results.py \
  tests/test_cloud910b.py \
  tests/test_stage3.py \
  tests/test_stage4_recovery_analysis.py \
  tests/test_final_delivery.py \
  tests/test_stage1_supplement.py -q
if [ -f data/tokenizer/tokenizer.json ] && [ -f data/raw/nq-open-20_total_documents_gold_at_0.jsonl.gz ]; then
  python scripts/audit_stage1_offline.py --raw-dir data/raw
else
  echo "DATA_ABSENT: pinned NQ gz and tokenizer are not in the worktree."
  echo "Rescore of the committed predictions uses reports/stage1-supplement/smoke-labels.json."
fi
if [ ! -f reports/cursor_dialogue/trial/replies.jsonl ]; then
  echo "CURSOR_DIALOGUE: no replies. The feasibility gate is not passed."
fi
