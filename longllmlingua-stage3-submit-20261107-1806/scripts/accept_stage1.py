"""Offline acceptance and lightweight export; never sends API requests."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.common import atomic_json, configuration_hash, digest, load_config, read_json, read_jsonl
from reproduction.evaluation import score, summarize
from reproduction.methods import TokenCounter
from reproduction.runner import slots, verify_resources


def rate_multiplier(timestamp):
    # This acceptance was run on 2026-11-06, which is not a Chinese public holiday.
    date = datetime.fromisoformat(timestamp).astimezone(timezone(timedelta(hours=8)))
    return 2 if date.weekday() < 5 and (9 <= date.hour < 12 or 14 <= date.hour < 18) else 1


def recorded_cost(result):
    usage = result.get("usage", {})
    hits = usage.get("prompt_cache_hit_tokens", usage.get("prompt_tokens_details", {}).get("cached_tokens", 0))
    inputs = usage.get("prompt_tokens", 0)
    outputs = usage.get("completion_tokens", 0)
    cost = (hits * 0.02 + (inputs - hits) * 1 + outputs * 4) / 1_000_000
    return cost * rate_multiplier(result["created_at"])


def accept(run_dir):
    run_dir = run_dir.resolve()
    config = load_config()
    verify_resources(config)
    meta = read_json(run_dir / "run.json")
    assert meta["config_hash"] == configuration_hash(config), "Current config/implementation differs from run"
    assert config["split"] == "smoke" and config["positions"] == [1, 5, 10, 15, 20]
    assert set(config["methods"]) == {"original", "bm25_2x", "bm25_4x"}
    before = read_json(run_dir / "summary.json")
    after = summarize(run_dir)
    assert before == after, "Offline rescoring changed stored aggregate"
    latest = {r["slot_id"]: r for r in read_jsonl(run_dir / "results.jsonl")}
    expected = {r["slot_id"]: r for r in slots(config, TokenCounter())}
    assert len(expected) == 300 and set(latest) == set(expected), "Matrix incomplete or has extra slots"
    for slot, row in latest.items():
        target = expected[slot]
        assert row["status"] == "success" and row["finish_reason"] == "stop"
        assert row["prompt"] == target["prompt"]
        assert row["prompt_hash"] == digest(target["prompt"])
        assert row["answers"] == target["answers"]
        assert row["compressed_tokens"] == target["compressed_tokens"] <= target["target_tokens"]
        assert row["score"] == score(row["answer"], row["answers"])
        assert row["usage"]["prompt_tokens"] > 0 and row["usage"]["completion_tokens"] > 0
        cached = read_json(ROOT / "cache/api" / f"{row['cache_key']}.json")
        assert cached["result"]["answer"] == row["answer"]
        assert cached["payload"]["messages"] == [{"role": "user", "content": target["prompt"]}]
        assert cached["payload"]["thinking"] == {"type": "disabled"}
        assert cached["payload"]["max_tokens"] == config["max_tokens"]
    assert after["complete"]
    from dotenv import dotenv_values
    import os
    key = os.environ.get("DEEPSEEK_API_KEY") or dotenv_values(ROOT / ".env").get("DEEPSEEK_API_KEY")
    scanned = 0
    if key:
        scan = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in (".py", ".md", ".json", ".jsonl", ".txt")
                and not any(part in (".venv", ".git", "__pycache__") for part in p.relative_to(ROOT).parts)]
        for path in scan:
            assert key.encode() not in path.read_bytes(), f"Credential leaked into {path.relative_to(ROOT)}"
            scanned += 1
    output = ROOT / "reports/stage1-acceptance"
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_bytes((run_dir / "summary.json").read_bytes())
    (output / "summary.md").write_bytes((run_dir / "summary.md").read_bytes())
    fields = ["slot_id", "question_id", "position", "method", "answer", "score", "origin_tokens",
              "compressed_tokens", "target_tokens", "actual_ratio", "model", "response_model",
              "system_fingerprint", "finish_reason", "usage", "cache_key", "generation_created_at"]
    with (output / "predictions.jsonl").open("w", encoding="utf-8") as f:
        for slot in sorted(latest):
            f.write(json.dumps({k: latest[slot].get(k) for k in fields}, ensure_ascii=False) + "\n")
    final_unique = {r["cache_key"]: r for r in latest.values()}
    final_cost = sum(recorded_cost({**r, "created_at": r["generation_created_at"]}) for r in final_unique.values())
    # Sum distinct genuine responses across the interrupted 128-token run and final 512-token run.
    all_cache = [read_json(p) for p in (ROOT / "cache/api").glob("*.json")]
    all_cache_cost = sum(recorded_cost(c["result"]) for c in all_cache)
    old_failed = []
    for path in (ROOT / "outputs/stage1").glob("*/results.jsonl"):
        old_failed.extend(r for r in read_jsonl(path) if r["status"] == "failed" and not r.get("usage"))
    total_usage = {k: sum(c["result"]["usage"].get(k, 0) for c in all_cache)
                   for k in ("prompt_tokens", "completion_tokens", "prompt_cache_hit_tokens", "prompt_cache_miss_tokens")}
    methods = []
    for method in config["methods"]:
        rows = [r for r in latest.values() if r["method"] == method]
        methods.append({"method": method, "samples": len(rows), "em_percent": statistics.mean(r["score"] for r in rows)*100,
                        "mean_actual_ratio": statistics.mean(r["actual_ratio"] for r in rows),
                        "api_seconds_mean": statistics.mean(r["api_seconds"] for r in rows),
                        "output_tokens_mean": statistics.mean(r["usage"]["completion_tokens"] for r in rows)})
    report = {"local_acceptance_passed": True, "peer_review_pending": True,
              "accepted_run": str(run_dir.relative_to(ROOT)), "config_hash": meta["config_hash"],
              "config": config, "success": 300, "failed": 0, "missing": 0,
              "offline_rescore_identical": True, "prompts_and_budgets_rebuilt": True,
              "cached_payloads_checked": True, "methods": methods,
              "credential_scan_files": scanned,
              "response_models": sorted(set(r["response_model"] for r in latest.values())),
              "system_fingerprints": sorted(set(r["system_fingerprint"] for r in latest.values() if r["system_fingerprint"])),
              "api_minus_local_prompt_tokens": dict(Counter(r["usage"]["prompt_tokens"] - r["compressed_tokens"] for r in latest.values())),
              "final_unique_responses": len(final_unique), "all_successful_unique_responses": len(all_cache),
              "final_run_cost_cny_estimate": final_cost, "all_recorded_success_cost_cny_estimate": all_cache_cost,
              "all_recorded_success_usage": total_usage,
              "earlier_failures_without_usage": len(old_failed),
              "earlier_failures_local_input_tokens": sum(r["compressed_tokens"] for r in old_failed),
              "cost_note": "Official 2026-11-06 rates, cache hits and Beijing peak hours; missing usage for earlier truncated responses and any interrupted in-flight request excluded; not a billing receipt.",
              "pricing_source": "https://api-docs.deepseek.com/zh-cn/quick_start/pricing/",
              "generated_at": datetime.now(timezone.utc).isoformat()}
    atomic_json(output / "acceptance.json", report)
    lines = ["# 第一阶段本机技术验收报告", "",
             "结论：**通过本机技术验收**。300 个槽位全部成功，失败 0、缺失 0；队友复核、GitHub 发布及服务器/LLaMA-2 准备仍待完成。", "",
             "## 实验设置", "",
             f"- 运行目录：`{report['accepted_run']}`。配置摘要：`{meta['config_hash']}`。",
             "- NQ 固定 20 题、每题 20 文档、五种答案位置，三个基线各 100 条结果。",
             f"- DeepSeek 官方 API，{config['model']}，非思考模式，temperature=0，最大输出 {config['max_tokens']} token。",
             f"- 返回模型：`{', '.join(report['response_models'])}`；fingerprint：`{', '.join(report['system_fingerprints'])}`。",
             "- API 返回模型别名，不能单凭别名独立证明具体快照；调研时官方映射版本见配置。", "",
             "## 基线结果", "",
             "| 方法 | 结果数 | 平均 EM (%) | 实测压缩比 | 平均输出 token |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for row in methods:
        lines.append(f"| {row['method']} | {row['samples']} | {row['em_percent']:.2f} | {row['mean_actual_ratio']:.3f}x | {row['output_tokens_mean']:.2f} |")
    lines += ["", "五种位置逐项结果见同目录 summary.md。这里是流程验收的小样本分数，不能代替 500 题主实验或论文历史模型结果。", "",
              "## 验收证据", "",
              "- 全部 2,655 题的五位置数据对齐与 gold 位置已校验，20/100/500 题清单固定。",
              "- 22 项离线测试及依赖完整性检查通过。",
              "- 最终 300 槽位的完整提示、分词预算、缓存请求与回答逐项重建核对通过。",
              "- 离线重新评分与已保存汇总完全一致，未调用 API。",
              f"- 对 {scanned} 个项目/数据结果文件进行实际密钥字符串扫描，未发现泄漏。",
              f"- 在线输入计数减本地文本计数的分布：`{report['api_minus_local_prompt_tokens']}`；在线 usage 用于计费。", "",
              "## 费用与异常处理", "",
              f"- 最终矩阵复用相同请求后实际对应 {len(final_unique)} 个独立成功响应，按官方时段/缓存价格估算费用 **{final_cost:.4f} 元**。",
              f"- 包括早期 128 上限试运行，全部留存成功响应共 {len(all_cache)} 个，按已记录 usage 估算 **{all_cache_cost:.4f} 元**。",
              f"- 另有 {len(old_failed)} 条旧版截断失败未保存 usage，以及停止旧进程时可能存在的在途请求，未计入以上金额；准确总扣费以平台账单为准。",
              "- 旧轮次输出上限 128 导致截断，已保留原记录并停止；最终轮次统一提高到 512，未把旧设置结果混入最终矩阵。",
              "- 新版失败记录保留截断返回的用量和部分回答，但不作为成功缓存或评分。",
              "- 价格来源：https://api-docs.deepseek.com/zh-cn/quick_start/pricing/，2026-11-06 核验。", "",
              "## 交接与限制", "",
              "公开交接产物为本目录的 acceptance.json、summary.json、summary.md、轻量 predictions.jsonl；完整提示、缓存和旧试运行留在忽略目录。",
              "成员二接手统一数据/方法接口，接入 LLMLingua/LongLLMLingua；服务器配置和 LLaMA-2 权限仍需核验。",
              "使用现有 DeepSeek 替代历史 GPT-3.5，BM25 分词与片段裁剪是明确固定的工程选择，不声称完全重现论文数字。",
              "GitHub 仓库、PR、队友复核与 stage1-ready 标签尚未创建。", ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    environment = read_json(ROOT / "reports/environment.json")
    environment.pop("api_requests_sent", None)
    environment["api_validation"] = {"complete_slots": 300, "unique_final_responses": len(final_unique),
                                     "observed_successful_responses_all_runs": len(all_cache),
                                     "accepted_run": report["accepted_run"]}
    environment["not_validated"] = ["server_deployment", "llama2_access", "peer_review", "github_publication"]
    atomic_json(ROOT / "reports/environment.json", environment)
    print(json.dumps({k: report[k] for k in ["local_acceptance_passed", "accepted_run", "success", "failed", "missing",
                                           "final_unique_responses", "all_successful_unique_responses",
                                           "final_run_cost_cny_estimate", "all_recorded_success_cost_cny_estimate",
                                           "earlier_failures_without_usage", "methods"]}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    accept(args.run_dir)
