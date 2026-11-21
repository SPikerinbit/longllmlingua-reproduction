#!/usr/bin/env bash
# Safe desktop demo. Actual run is about 7 seconds; the recorded video is 50 seconds
# because the screen was held for reading. No network, no interaction.
# Does not print environment variable values or secrets.
# Evidence was recorded against already-pushed main bdb11d3. After later
# documentation commits, the current HEAD may be a descendant of that commit.
set -euo pipefail
unset HF_TOKEN DEEPSEEK_API_KEY HUGGING_FACE_HUB_TOKEN OPENAI_API_KEY 2>/dev/null || true

HERE="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
# scripts/ lives at repo root in this checkout
REPO="$(CDPATH= cd -- "$HERE/.." && pwd)"
EXPECTED_EVIDENCE_COMMIT="bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4"
TOK_SHA="c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b"
NQ0_SHA="69a8dd87a45f07fb3ed9b804917a89db975cd6e488682fc838edca029cc3881f"

cd "$REPO"

if command -v python >/dev/null 2>&1 && python -c "import pytest,tokenizers" >/dev/null 2>&1; then
  PY=python
elif python3 -c "import pytest,tokenizers" >/dev/null 2>&1; then
  PY=python3
else
  echo "error: need a Python environment with pytest and tokenizers (see requirements-lock.txt)" >&2
  exit 3
fi

echo "============================================================"
echo "G14 offline evidence demo (not a new model run)"
echo "============================================================"
echo "time:      $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S %Z (Asia/Shanghai)')"
echo "repo:      $REPO"
echo "python:    $PY ($("$PY" -c 'import sys; print(sys.version.split()[0])'))"
echo "HEAD:      $(git rev-parse HEAD)"
echo "evidence:  $EXPECTED_EVIDENCE_COMMIT"
if [ "$(git rev-parse HEAD)" = "$EXPECTED_EVIDENCE_COMMIT" ]; then
  echo "HEAD is the original verification commit."
elif git merge-base --is-ancestor "$EXPECTED_EVIDENCE_COMMIT" HEAD; then
  echo "HEAD is a descendant of the original verification commit; logs still record that commit."
else
  echo "ERROR: current HEAD is not $EXPECTED_EVIDENCE_COMMIT or a descendant of it."
  exit 1
fi
echo "subject:   $(git log -1 --format='%s')"
echo

echo "[1] Pinned public artifacts (sha256 must match manifests/resources.json)"
tok_actual="$("$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$REPO/data/tokenizer/tokenizer.json")"
nq_actual="$("$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$REPO/data/raw/nq-open-20_total_documents_gold_at_0.jsonl.gz")"
echo "tokenizer.json  $tok_actual"
echo "expected        $TOK_SHA"
[ "$tok_actual" = "$TOK_SHA" ] && echo "tokenizer: MATCH" || { echo "tokenizer: MISMATCH"; exit 1; }
echo "nq gold_at_0    $nq_actual"
echo "expected        $NQ0_SHA"
[ "$nq_actual" = "$NQ0_SHA" ] && echo "nq gold_at_0: MATCH" || { echo "nq gold_at_0: MISMATCH"; exit 1; }
echo

echo "[2] Re-run the five tests that failed before data/tokenizer were present"
"$PY" -m pytest -v --tb=line \
  tests/test_stage1.py::test_real_tokenizer_budget_and_order \
  tests/test_stage1.py::test_full_real_data_nested_manifests \
  tests/test_stage1.py::test_runner_interrupt_resume_and_cache_rebuild
echo

echo "[3] Full suite already collected as 77 items on this checkout"
"$PY" -m pytest -q
echo

echo "[4] Published official numbers (from committed JSON; this is not new inference)"
"$PY" - <<PY
import json
from pathlib import Path
root = Path(r"$REPO")
acc = json.loads((root / "reports/smoke-stage2-acceptance.json").read_text())
s1 = json.loads((root / "reports/stage1-supplement/offline-audit.json").read_text())
s3 = json.loads((root / "reports/stage3-main/summary.json").read_text())
print(f"stage2 canonical: {acc['budget_satisfied']}/{acc['slots']}  accepted_run={acc['accepted_run']}")
means = s1["rescore"]["official_mean_score"]
print(f"stage1 official EM (20 questions): original={means['original']} bm25_2x={means['bm25_2x']} bm25_4x={means['bm25_4x']}")
print("stage1 audit api_calls=", s1.get("api_calls"), " mismatches=", s1["rescore"]["mismatches"])
methods = {row["method"]: row for row in s3["methods"]}
print("stage3 CUDA official EM: original={:.1f}% longllmlingua_2x={:.1f}%".format(
    100*methods["original"]["mean_em"], 100*methods["longllmlingua_2x"]["mean_em"]))
print("These figures are committed records. This demo only rechecked them offline.")
PY

echo
echo "Done. No API calls, no weights loaded, no screen was cleared."
echo "Script runtime is about 7 seconds; a 50-second recording may hold this output for reading."
