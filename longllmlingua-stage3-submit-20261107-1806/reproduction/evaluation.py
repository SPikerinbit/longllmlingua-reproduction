from __future__ import annotations

import importlib.util
from collections import defaultdict

from .common import ROOT, atomic_json, read_jsonl


def score(answer, answers):
    path = ROOT / "vendor/lost_in_the_middle/metrics.py"
    spec = importlib.util.spec_from_file_location("upstream_nq_metrics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Exactly the upstream evaluate_qa_responses.py pre-processing.
    return module.best_subspan_em(answer.split("\n")[0].strip(), answers)


def summarize(run_dir):
    from .common import read_json
    meta = read_json(run_dir / "run.json")
    latest = {}
    for row in read_jsonl(run_dir / "results.jsonl"):
        latest[row["slot_id"]] = row
    groups = defaultdict(list)
    for row in latest.values():
        groups[(row["method"], row["position"])].append(row)
    expected = len(meta["question_ids"])
    summary = []
    for method in meta["config"]["methods"]:
        for position in meta["config"]["positions"]:
            rows = groups[(method, position)]
            ok = [r for r in rows if r["status"] == "success"]
            for row in ok:
                row["score"] = score(row["answer"], row["answers"])
            summary.append({"method": method, "position": position, "expected": expected,
                            "success": len(ok), "failed": len(rows) - len(ok),
                            "missing": expected - len(rows),
                            "best_subspan_em": sum(r["score"] for r in ok) / len(ok) if ok else None,
                            "mean_actual_ratio": sum(r["actual_ratio"] for r in ok) / len(ok) if ok else None,
                            "api_input_tokens": sum(r.get("usage", {}).get("prompt_tokens", 0) for r in ok),
                            "api_output_tokens": sum(r.get("usage", {}).get("completion_tokens", 0) for r in ok)})
    complete = all(r["success"] == r["expected"] for r in summary)
    atomic_json(run_dir / "summary.json", {"complete": complete, "groups": summary})
    text = ["# Stage-one baseline results", "", f"Complete matrix: **{complete}**", "",
            "Scores use successful records only; inspect failed/missing columns before comparing.", "",
            "| Method | Position | Expected | Success | Failed | Missing | EM (%) | Actual ratio |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in summary:
        em = f"{r['best_subspan_em'] * 100:.2f}" if r["success"] else "pending"
        ratio = f"{r['mean_actual_ratio']:.2f}" if r["success"] else "pending"
        text.append(f"| {r['method']} | {r['position']} | {r['expected']} | {r['success']} | "
                    f"{r['failed']} | {r['missing']} | {em} | {ratio} |")
    (run_dir / "summary.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    return {"complete": complete, "groups": summary}
