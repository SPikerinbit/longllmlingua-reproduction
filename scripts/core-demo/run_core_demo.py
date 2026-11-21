#!/usr/bin/env python3
"""Core-evidence demo for a 60-second (sped-up) recording.

Live CPU work: official BM25 compression + first-line best_subspan_em.
Does not call the QA API, does not load LLaMA/LongLLMLingua weights,
and does not invent missing stage-2/3/4 caches. Existing DeepSeek
answers are scored as already-saved records, not as new calls.

This is not a full rerun of the course experiments.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
DEFAULT_REPO = Path("/workspace/g14-local-main/repo")
KNOWN_MAIN = "aa11a2c85e131d0aadc7990c7fa6a1a03bd8ad9f"
WIDTH = 86

QID = "ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc"
QID_POS = 1
BOUND_QID = "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5"
BOUND_POS = 10

# Do not leak env values; just drop keys so nothing is sent.
for _k in ("DEEPSEEK_API_KEY", "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "OPENAI_API_KEY"):
    os.environ.pop(_k, None)


def now_cst():
    # Box clock is Asia/Shanghai.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def epoch():
    return time.time()


def wrap(text, width=WIDTH):
    text = re.sub(r"\s+", " ", text).strip()
    lines = []
    while text:
        if len(text) <= width:
            lines.append(text)
            break
        cut = text.rfind(" ", 0, width)
        if cut < width // 2:
            cut = width
        lines.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    return lines


def say(text=""):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def rule(title=""):
    if title:
        pad = WIDTH - len(title) - 2
        left = pad // 2
        say("=" * left + " " + title + " " + "=" * (pad - left))
    else:
        say("=" * WIDTH)


def box_kv(rows):
    if not rows:
        return
    w = max(len(k) for k, _ in rows)
    for k, v in rows:
        say(f"  {k.ljust(w)}  {v}")


def excerpt_source(path: Path, start: int, end: int):
    """1-based inclusive line range, live from the current checkout."""
    lines = path.read_text(encoding="utf-8").splitlines()
    say(f"  [excerpt] {path.as_posix()}:{start}-{end}")
    for i in range(start, end + 1):
        if 1 <= i <= len(lines):
            say(f"  {i:>4}| {lines[i-1]}")


def short_id(qid: str) -> str:
    return qid[:12] + "…"


class MarkerLog:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._start = {}
        if not path.exists():
            path.write_text(
                "chapter\tevent\ttime_cst\tepoch\telapsed_s\n", encoding="utf-8"
            )

    def _write(self, chapter, event, elapsed=""):
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(f"{chapter}\t{event}\t{now_cst()}\t{epoch():.3f}\t{elapsed}\n")

    def start(self, chapter):
        self._start[chapter] = epoch()
        self._write(chapter, "START")
        rule(f"CHAPTER {chapter}/6")

    def end(self, chapter):
        elapsed = epoch() - self._start[chapter]
        self._write(chapter, "END", f"{elapsed:.3f}")
        say(f"  -- chapter {chapter} elapsed {elapsed:.2f}s (Asia/Shanghai {now_cst()}) --")
        say()
        return elapsed


def find_repo(explicit: Path | None) -> Path:
    if explicit:
        return explicit.resolve()
    env = os.environ.get("G14_REPO")
    if env:
        return Path(env).resolve()
    # Prefer the checkout that contains this script (scripts/core-demo/...).
    here = DEMO_ROOT
    for cand in [here, *here.parents]:
        if (cand / "reproduction" / "methods.py").is_file():
            return cand
    if DEFAULT_REPO.is_dir():
        return DEFAULT_REPO
    raise SystemExit("cannot locate the repository; pass --repo")


def git_head(repo: Path) -> str:
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def load_predictions(repo: Path):
    path = repo / "reports/stage1-acceptance/predictions.jsonl"
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[(row["question_id"], row["position"], row["method"])] = row
    return out, path


def docs_from_prompt(prompt_text: str):
    chunks = re.split(r"\n(?=Document \[\d+\]\(Title: )", prompt_text)
    found = []
    for chunk in chunks:
        m = re.match(
            r"Document \[(\d+)\]\(Title: ([^)]*)\) (.*)$",
            chunk,
            flags=re.S,
        )
        if not m:
            continue
        body = m.group(3)
        body = re.split(r"\n+Question:", body, maxsplit=1)[0].strip()
        found.append({"n": int(m.group(1)), "title": m.group(2), "text": body})
    return found


def preflight(repo: Path):
    needed = [
        repo / "configs/stage1.json",
        repo / "data/tokenizer/tokenizer.json",
        repo / "data/raw/nq-open-20_total_documents_gold_at_0.jsonl.gz",
        repo / "data/raw/nq-open-20_total_documents_gold_at_9.jsonl.gz",
        repo / "reports/stage1-acceptance/predictions.jsonl",
        repo / "reports/stage3-main/summary.json",
        repo / "reports/stage3-main/stats.json",
        repo / "reports/stage4-ablation-efficiency/RESULTS.md",
        repo / "reproduction/methods.py",
        repo / "reproduction/compression.py",
    ]
    missing = [str(p) for p in needed if not p.is_file()]
    if missing:
        raise SystemExit(
            "missing required local files (run official prepare in the repo if data/tokenizer are absent):\n  "
            + "\n  ".join(missing)
        )


def chapter1(ctx):
    repo = ctx["repo"]
    cfg1 = ctx["cfg1"]
    say("This recording is a walkable evidence chain, not a live rerun of the")
    say("full 3500-slot experiments. No QA API. No compression-model weights.")
    say()
    head = git_head(repo)
    box_kv([
        ("time", f"{now_cst()} Asia/Shanghai"),
        ("repo", str(repo)),
        ("HEAD", head),
        ("known main", KNOWN_MAIN + ("  (current or ancestor is fine)" if head != KNOWN_MAIN else "")),
        ("entry", "python -m reproduction   /  python -m reproduction.stage3"),
        ("API this run", "0"),
    ])
    say()
    say("Locked setup (excerpt from configs/stage1.json and committed stage-3 run):")
    box_kv([
        ("seed", str(cfg1["seed"])),
        ("positions", "1, 5, 10, 15, 20  (gold index 0,4,9,14,19)"),
        ("split", "smoke=20 questions; course main/ablation uses pilot=100"),
        ("stage-1 methods", ", ".join(cfg1["methods"])),
        ("stage-3 methods", "7: original, BM25 2x/4x, LLMLingua 2x/4x, Long 2x/4x"),
        ("QA record", f"{cfg1['model']}, temperature={cfg1['temperature']}, max_tokens={cfg1['max_tokens']}, thinking disabled"),
        ("tokenizer", f"{cfg1['tokenizer']['repo']}  rev {cfg1['tokenizer']['revision'][:12]}…"),
        ("upstream data", f"lost-in-the-middle {cfg1['upstream']['lost_in_the_middle'][:12]}…"),
        ("note", "default configs/stage3.json has split=main; the saved run is split=pilot"),
    ])
    say()
    say("How a slot is built (visible fields only, then the official method):")
    excerpt_source(repo / "reproduction/runner.py", 48, 56)


def chapter2(ctx):
    row = ctx["row"]
    vis = ctx["vis"]
    gold_i = ctx["gold_i"]
    gold = row["ctxs"][gold_i]
    say(f"Real smoke question  (first ID in manifests/smoke.json)")
    box_kv([
        ("question_id", QID),
        ("question", vis["question"]),
        ("position", f"{QID_POS}   (this file is gold_at_0; gold document is ctxs[{gold_i}])"),
        ("n documents", f"{len(vis['documents'])} visible / {len(row['ctxs'])} raw"),
        ("reference answers", " ; ".join(row["answers"])),
        ("source", "official NQ 20-document jsonl via reproduction.data.load_position"),
    ])
    say()
    say("Visible-field isolation  (reproduction/data.py visible_sample):")
    excerpt_source(ctx["repo"] / "reproduction/data.py", 158, 162)
    raw_doc_keys = sorted(row["ctxs"][0].keys())
    vis_doc_keys = sorted(vis["documents"][0].keys())
    box_kv([
        ("raw row keys", ", ".join(sorted(row.keys()))),
        ("raw ctx keys", ", ".join(raw_doc_keys)),
        ("visible doc keys", ", ".join(vis_doc_keys)),
        ("answers in visible?", str("answers" in vis)),
        ("isgold/hasanswer in visible docs?", str(any(("isgold" in d or "hasanswer" in d) for d in vis["documents"]))),
        ("gold flags (raw only)", f"ctxs[{gold_i}] isgold={gold.get('isgold')} hasanswer={gold.get('hasanswer')}"),
    ])
    say()
    say("Gold document excerpt (raw text, not a rewrite):")
    say(f"  title: {gold['title']}")
    for line in wrap(gold["text"][:240], WIDTH - 4):
        say(f"  {line}")
    say("  …")
    say()
    say("The method never receives answers or gold flags. Those stay in the raw row")
    say("for checking and scoring only.")


def chapter3(ctx):
    repo = ctx["repo"]
    vis = ctx["vis"]
    built = ctx["built"]
    gold_id = ctx["gold_id"]
    timings = ctx["compress_timings"]
    say("Live CPU call: reproduction.methods.build_prompt  (BM25Okapi, official tokenizer).")
    say("This is not LLMLingua/LongLLMLingua. Those need the LLaMA-2-7B compressor,")
    say("which is not loaded here.")
    say()
    excerpt_source(repo / "reproduction/methods.py", 48, 58)
    say()
    say("Running build_prompt now for original, bm25_2x, bm25_4x …")
    if ctx["built"] is None:
        built = {}
        timings = {}
        for method in ("original", "bm25_2x", "bm25_4x"):
            t0 = time.perf_counter()
            built[method] = ctx["build_prompt"](ctx["vis"], method, ctx["cfg1"], ctx["counter"])
            timings[method] = time.perf_counter() - t0
            say(f"  {method} finished in {timings[method]:.3f}s")
        ctx["built"] = built
        ctx["compress_timings"] = timings
        persist_artifacts(ctx)
    say()
    say(f"{'method':<10} {'origin':>7} {'comp':>7} {'budget':>7} {'ratio':>7} {'#docs':>5}  gold kept  time")
    say("-" * WIDTH)
    for method in ("original", "bm25_2x", "bm25_4x"):
        b = built[method]
        kept = gold_id in b["selected_doc_ids"]
        st = ctx["preds"][(QID, QID_POS, method)]
        match = (
            b["origin_tokens"] == st["origin_tokens"]
            and b["compressed_tokens"] == st["compressed_tokens"]
            and b["target_tokens"] == st["target_tokens"]
        )
        say(
            f"{method:<10} {b['origin_tokens']:7d} {b['compressed_tokens']:7d} "
            f"{b['target_tokens']:7d} {b['actual_ratio']:7.3f} {len(b['selected_doc_ids']):5d}  "
            f"{'yes' if kept else 'NO '}      {timings[method]:.3f}s"
        )
        if not match:
            say(f"  WARNING: live tokens differ from stored predictions for {method}")
    say()
    say("Live token counts match reports/stage1-acceptance/predictions.jsonl for this slot.")
    say(f"  total BM25+original build time: {sum(timings.values()):.3f}s   API calls: 0")
    b4 = built["bm25_4x"]
    rank = [r["doc_id"] for r in b4["ranking"]]
    gold_rank = rank.index(gold_id) + 1 if gold_id in rank else None
    say(f"  gold doc id (prefix): {gold_id[:16]}…   BM25 rank among 20: {gold_rank}")
    say(f"  4x selected {len(b4['selected_doc_ids'])} docs; truncated {b4['truncated_doc_ids']}; gold kept? no")
    say()
    say("4x compressed prompt excerpt (actual render, first kept document):")
    docs = docs_from_prompt(b4["prompt"])
    if docs:
        d0 = docs[0]
        say(f"  Document [{d0['n']}]  title: {d0['title']}")
        for line in wrap(d0["text"][:220], WIDTH - 4):
            say(f"  {line}")
        say("  …")
    say()
    say("Official LongLLMLingua is wired here (not executed in this demo):")
    excerpt_source(repo / "reproduction/compression.py", 170, 188)
    say()
    say("Parameter map (excerpt): coarse rank_method=longllmlingua; fine condition_compare=True;")
    say("dynamic δτ=0.3; main comparison reorder_context=original (off); k=2 is not a")
    say("valid mapping on the pinned library path. See docs/stage2-parameter-map.md.")


def chapter4(ctx):
    repo = ctx["repo"]
    preds = ctx["preds"]
    say("Scorer: first line only, upstream best_subspan_em. Saved DeepSeek answers")
    say("are re-scored; this is not a new model call.")
    excerpt_source(repo / "reproduction/evaluation.py", 9, 15)
    say()

    def show_slot(label, qid, pos, method, note):
        st = preds[(qid, pos, method)]
        from reproduction.data import load_position
        answers = load_position(pos)[qid]["answers"]
        t0 = time.perf_counter()
        live = ctx["score"](st["answer"], answers)
        dt = time.perf_counter() - t0
        first = st["answer"].split("\n")[0].strip()
        joined = " ".join(st["answer"].split())
        joined_score = ctx["score"](joined, answers)
        say(f"{label}  {short_id(qid)}  pos={pos}  {method}")
        box_kv([
            ("slot_id", st["slot_id"]),
            ("saved score", str(st["score"])),
            ("live first-line score", f"{live}   ({dt*1000:.1f} ms, API=0)"),
            ("if whole answer is joined to one line", str(joined_score)),
            ("reference", " ; ".join(answers)),
            ("origin/comp/target", f"{st['origin_tokens']} / {st['compressed_tokens']} / {st['target_tokens']}"),
            ("record time", st["generation_created_at"] + "  (saved run, not this demo)"),
            ("note", note),
        ])
        say("  first line:")
        for line in wrap(first, WIDTH - 4):
            say(f"    {line}")
        say()

    show_slot(
        "A. S1-01",
        QID, 1, "original",
        "same question, uncompressed; official EM=1",
    )
    show_slot(
        "B. S1-03",
        QID, 1, "bm25_4x",
        "same question after live 4x (gold dropped); official EM=0",
    )
    show_slot(
        "C. S1-08  (boundary)",
        BOUND_QID, 10, "bm25_2x",
        "first line denies the title, but still contains 'Los Lonely Boys' → official EM=1",
    )
    show_slot(
        "D. S1-10  (metric boundary)",
        BOUND_QID, 5, "original",
        "reference is not in the first line; joining newlines would flip 0→1. Official metric stays first-line.",
    )
    say("Stage-1 smoke has a complete 300-slot predictions.jsonl (20×5×3). The 13 written")
    say("cases are a subset of those slots. Stage-2/3/4 full results.jsonl are not on this machine.")


def chapter5(ctx):
    repo = ctx["repo"]
    summary = json.loads((repo / "reports/stage3-main/summary.json").read_text(encoding="utf-8"))
    stats = json.loads((repo / "reports/stage3-main/stats.json").read_text(encoding="utf-8"))
    coverage = json.loads((repo / "reports/stage3-main/coverage.json").read_text(encoding="utf-8"))
    run = json.loads((repo / "reports/stage3-main/run.json").read_text(encoding="utf-8"))
    say("Committed CUDA main comparison — read from reports/stage3-main/, not re-inferred.")
    box_kv([
        ("run_id", run.get("run_id", "")),
        ("split", f"{coverage['split']}  ({coverage['questions']} questions × 5 positions × 7 methods)"),
        ("slots", f"{coverage['success']}/{coverage['expected_slots']} success, failed={coverage['failed']}, missing={coverage['missing']}"),
        ("note", "configs/stage3.json split=main is not this run; inspect run.json"),
    ])
    say()
    say(f"{'method':<22} {'EM %':>6}  {'ratio':>6}  budget")
    say("-" * WIDTH)
    # budget satisfied may live on methods or must be derived from a known field
    methods = {m["method"]: m for m in summary["methods"]}
    for m in summary["methods"]:
        em = 100.0 * m["mean_em"]
        ratio = m["mean_actual_ratio"]
        budget = m.get("budget_satisfied_rate")
        if budget is None:
            budget = m.get("mean_budget_satisfied")
        budget_s = "—" if budget is None else f"{budget:.3f}"
        say(f"{m['method']:<22} {em:6.1f}  {ratio:6.2f}x  {budget_s}")
    # 18/500 from long 4x if rate present; else from registry-known field in summary groups
    long4 = methods["longllmlingua_4x"]
    rate = long4.get("budget_satisfied_rate")
    if rate is None:
        # try groups
        groups = summary.get("groups") or []
        cells = [g for g in groups if g.get("method") == "longllmlingua_4x" and "budget_satisfied" in g]
        if cells:
            # average or overall
            if "budget_satisfied" in long4:
                rate = long4["budget_satisfied"]
    # official accepted figure: 0.964 × 500 = 18 misses. Prefer file.
    if rate is None and "budget_satisfied" in long4:
        rate = long4["budget_satisfied"]
    say()
    rate = methods["longllmlingua_4x"]["budget_satisfied_rate"]
    met = int(round(rate * 500))
    say(f"  longllmlingua_4x budget_satisfied_rate={rate} → {met}/500 met, {500-met}/500 miss the hard budget.")
    say("  Success slots remain 500. 4x is therefore not a strict equal-budget comparison.")
    say()
    say("Paired question-level bootstrap vs original  (n=100, 2000 resamples, seed 42):")
    say(f"{'method':<22} {'Δ':>7}  95% CI")
    say("-" * WIDTH)
    for row in stats["comparisons"]:
        if row["method"] not in ("bm25_2x", "llmlingua_2x", "longllmlingua_2x", "longllmlingua_4x"):
            continue
        mean = row["mean"]
        lo, hi = row["ci_low"], row["ci_high"]
        say(f"{row['method']:<22} {100*mean:+6.1f}pp  [{100*lo:+5.1f}, {100*hi:+5.1f}]")
    say()
    say("Long 2x minus original is −1.4 pp, interval [−6.2, +3.0] crosses 0.")
    say("That interval is not proof of equivalence. All figures are saved records.")


def chapter6(ctx):
    repo = ctx["repo"]
    import csv
    rows = list(csv.DictReader((repo / "reports/stage4-ablation-efficiency/ablation.csv").open(encoding="utf-8")))
    say("Committed NPU ablation (same 100 questions, 2x) — reports/stage4-ablation-efficiency/.")
    say("These are saved official means, not a new 910B run.")
    # keep 6-7 rows max: original, full, no_coarse, no_dynamic, no_recovery maybe reorder
    keep = {
        "original",
        "longllmlingua_2x",
        "longllmlingua_2x_no_coarse",
        "longllmlingua_2x_no_dynamic",
        "longllmlingua_2x_reorder",
        "longllmlingua_2x_no_recovery",
    }
    say(f"{'method':<32} {'EM %':>6}  {'Δ pp':>7}  95% CI")
    say("-" * WIDTH)
    shown = 0
    for r in rows:
        if r["method"] not in keep:
            continue
        em = float(r["em_percent"])
        delta = r.get("delta_pp") or r.get("delta") or ""
        lo = r.get("ci95_low") or r.get("ci_low") or ""
        hi = r.get("ci95_high") or r.get("ci_high") or ""
        # try common column names
        cols = {k.lower(): k for k in r}
        def pick(*names):
            for n in names:
                if n in r and r[n] not in ("", None):
                    return r[n]
                for c in r:
                    if c.lower() == n:
                        return r[c]
            return ""
        delta = pick("delta_pp", "difference_pp", "delta")
        lo = pick("ci_low_pp", "ci95_low", "ci_low")
        hi = pick("ci_high_pp", "ci95_high", "ci_high")
        def fmt(x):
            if x in ("", None):
                return "—"
            try:
                return f"{float(x):.1f}"
            except ValueError:
                return str(x)
        say(f"{r['method']:<32} {em:6.1f}  {fmt(delta):>7}  [{fmt(lo)}, {fmt(hi)}]")
        shown += 1
    say(f"  ({shown} of {len(rows)} rows shown; full table stays in the committed CSV.)")
    # If columns didn't map well, also print raw header once
    if rows and shown:
        pass
    say()
    # efficiency two lines
    import csv as csvmod
    erows = list(csvmod.DictReader((repo / "reports/stage4-ablation-efficiency/efficiency.csv").open(encoding="utf-8")))
    want = {"original", "longllmlingua_2x"}
    say("Independent efficiency batch (smoke 20×5, cache bypass), p50 / p95 seconds:")
    for r in erows:
        if r.get("method") not in want:
            continue
        p50 = float(r["total_pipeline_seconds_p50"])
        p95 = float(r["total_pipeline_seconds_p95"])
        hbm = r.get("peak_allocated_GB") or "—"
        if hbm not in ("", "—"):
            hbm = f"{float(hbm):.2f}"
        else:
            hbm = "—"
        say(f"  {r['method']:<22} p50={p50:.2f}s  p95={p95:.2f}s  peak allocated GB={hbm}")
    say("  Compression reduced prompt tokens; it did not reduce end-to-end latency in this batch.")
    say("  Stage-4 CANN version was not recorded. Stage-2 smoke CANN 8.5.2 must not be copied here.")
    say()
    say("Offline test chain (short; not the experiment):")
    say("  official prepare → python -m pytest   collected 77, all passed")
    say("  2026-11-21 17:46:58–17:47:02 Asia/Shanghai, exit 0, API=0")
    say("  logs: reports/local-verification/  (junit-full.xml, data-tokenizer-sha256.txt)")
    say("  recheck: bash reports/local-verification/recheck.sh")
    # tiny collect-only, not the full suite
    say()
    say("Collect-only reminder (no test body rerun as the main act):")
    t0 = time.perf_counter()
    import subprocess
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(repo),
            text=True,
            stderr=subprocess.STDOUT,
        )
        dt = time.perf_counter() - t0
        lines = [ln for ln in out.splitlines() if ln.strip()]
        file_lines = [ln for ln in lines if ln.startswith("tests/")]
        total = 0
        for ln in file_lines:
            try:
                total += int(ln.rsplit(":", 1)[1].strip())
            except ValueError:
                pass
        # Short index only (tests are the last beat, not the main act).
        for ln in file_lines[:3]:
            say(f"  {ln}")
        if len(file_lines) > 3:
            say(f"  … {len(file_lines)-3} more files …")
        say(f"  collected {total} items  ({len(file_lines)} files, collect-only {dt:.2f}s)")
    except Exception as exc:
        say(f"  collect-only skipped: {exc}")
    say()
    say("What this 1-minute tape is not: a real-time rerun of CUDA/NPU inference,")
    say("and not a substitute for the committed results or the full course package.")


def persist_artifacts(ctx):
    out = DEMO_ROOT / "artifacts"
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": "g14-core-demo-live-bm25",
        "api_calls": 0,
        "time_cst": now_cst(),
        "question_id": QID,
        "position": QID_POS,
        "question": ctx["vis"]["question"],
        "gold_id": ctx["gold_id"],
        "gold_title": ctx["row"]["ctxs"][ctx["gold_i"]]["title"],
        "compress_seconds": ctx["compress_timings"],
        "methods": {},
    }
    for method, b in ctx["built"].items():
        payload["methods"][method] = {
            "origin_tokens": b["origin_tokens"],
            "compressed_tokens": b["compressed_tokens"],
            "target_tokens": b["target_tokens"],
            "actual_ratio": b["actual_ratio"],
            "selected_doc_ids": b["selected_doc_ids"],
            "truncated_doc_ids": b.get("truncated_doc_ids", []),
            "gold_kept": ctx["gold_id"] in b["selected_doc_ids"],
        }
        if method != "original" and "ranking" in b:
            payload["methods"][method]["ranking_top5"] = b["ranking"][:5]
            rank = [r["doc_id"] for r in b["ranking"]]
            payload["methods"][method]["gold_rank"] = rank.index(ctx["gold_id"]) + 1 if ctx["gold_id"] in rank else None
    (out / "live-bm25-ef848352-pos1.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # short excerpts only
    excerpt = {
        "gold_title": ctx["row"]["ctxs"][ctx["gold_i"]]["title"],
        "gold_text_prefix": ctx["row"]["ctxs"][ctx["gold_i"]]["text"][:400],
        "bm25_4x_first_kept": docs_from_prompt(ctx["built"]["bm25_4x"]["prompt"])[:1],
    }
    # do not store full 20-doc prompts
    if excerpt["bm25_4x_first_kept"]:
        excerpt["bm25_4x_first_kept"][0]["text"] = excerpt["bm25_4x_first_kept"][0]["text"][:400]
    (out / "excerpts-ef848352-pos1.json").write_text(
        json.dumps(excerpt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build_context(repo: Path):
    sys.path.insert(0, str(repo))
    from reproduction.common import read_json
    from reproduction.data import document_id, load_position, visible_sample
    from reproduction.evaluation import score
    from reproduction.methods import TokenCounter, build_prompt

    cfg1 = read_json(repo / "configs/stage1.json")
    preds, pred_path = load_predictions(repo)
    row = load_position(QID_POS)[QID]
    vis = visible_sample(row)
    gold_i = next(i for i, d in enumerate(row["ctxs"]) if d.get("isgold"))
    gold_id = document_id(row["ctxs"][gold_i])
    counter = TokenCounter()
    return {
        "repo": repo,
        "cfg1": cfg1,
        "preds": preds,
        "pred_path": pred_path,
        "row": row,
        "vis": vis,
        "gold_i": gold_i,
        "gold_id": gold_id,
        "built": None,
        "compress_timings": None,
        "score": score,
        "counter": counter,
        "build_prompt": build_prompt,
    }


def maybe_pause(args, chapter, nxt):
    if args.no_pause:
        return
    if args.chapter:
        return
    prompt = f"[chapter {chapter} done] Enter = next chapter"
    if nxt:
        prompt += f" {nxt}"
    else:
        prompt += " (end)"
    prompt += "   q = quit  "
    try:
        got = input(prompt)
    except EOFError:
        return
    if got.strip().lower() in {"q", "quit"}:
        raise SystemExit(0)


def main():
    parser = argparse.ArgumentParser(description="G14 core-evidence demo (CPU, API=0)")
    parser.add_argument("--repo", type=Path, default=None)
    parser.add_argument("--chapter", type=int, choices=range(1, 7), help="run one chapter only")
    parser.add_argument("--all", action="store_true", help="run all six chapters")
    parser.add_argument("--no-pause", action="store_true", help="do not wait for Enter (for rehearsal)")
    args = parser.parse_args()
    if not args.chapter and not args.all:
        args.all = True

    repo = find_repo(args.repo)
    os.chdir(repo)
    preflight(repo)

    markers = MarkerLog(DEMO_ROOT / "logs/markers.tsv")
    t_all = epoch()
    rule("G14 core evidence demo")
    say("CPU only. Official BM25 + official first-line scorer will run live.")
    say("LongLLMLingua weights are not loaded. Saved EM tables are not new inference.")
    say()

    ctx = build_context(repo)
    chapters = {
        1: ("Entry, calls, locked config", chapter1),
        2: ("Real sample and visible-field isolation", chapter2),
        3: ("Live BM25 compression and token budget", chapter3),
        4: ("Saved DeepSeek answers and live scoring", chapter4),
        5: ("CUDA main comparison (committed)", chapter5),
        6: ("NPU ablation/efficiency and test index", chapter6),
    }
    order = [args.chapter] if args.chapter else [1, 2, 3, 4, 5, 6]
    elapsed = {}
    for i, ch in enumerate(order):
        title, fn = chapters[ch]
        markers.start(ch)
        say(title)
        say()
        fn(ctx)
        elapsed[ch] = markers.end(ch)
        nxt = order[i + 1] if i + 1 < len(order) else None
        if i + 1 < len(order):
            maybe_pause(args, ch, nxt)
    total = epoch() - t_all
    say("=" * WIDTH)
    say(f"done  chapters={order}  wall={total:.2f}s  API=0  artifacts={DEMO_ROOT / 'artifacts'}")
    say(f"markers: {DEMO_ROOT / 'logs/markers.tsv'}")
    (DEMO_ROOT / "logs/last-run.json").write_text(
        json.dumps(
            {
                "time_cst": now_cst(),
                "repo": str(repo),
                "head": git_head(repo),
                "chapters": order,
                "elapsed_s": elapsed,
                "wall_s": total,
                "api_calls": 0,
                "compress_seconds": ctx["compress_timings"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
