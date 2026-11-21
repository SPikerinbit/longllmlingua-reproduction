from __future__ import annotations

import statistics
import time
from datetime import datetime, timezone

from .api import APIError, DeepSeekClient, cache_key, cached_completion, get_key, request_payload
from .common import (ROOT, append_jsonl, atomic_json, configuration_hash, digest,
                     implementation_hash, read_json, read_jsonl)
from .data import iter_samples, visible_sample
from .evaluation import score, summarize
from .methods import TokenCounter, build_prompt


def _resource_matches(data, expected):
    """Compare a resource digest, tolerating line-ending conversion.

    ``manifests/resources.json`` was recorded on Windows, so text resources carry
    CRLF digests there; a git checkout on Linux stores the same files with LF.
    Accepting the LF<->CRLF equivalents keeps the recorded manifest usable across
    platforms without rewriting provenance data.
    """
    import hashlib

    lf = data.replace(b"\r\n", b"\n")
    for candidate in (data, lf, lf.replace(b"\n", b"\r\n")):
        if hashlib.sha256(candidate).hexdigest() == expected:
            return True
    return False


def verify_resources(config):
    if config["tokenizer"]["revision"] != "314113f8a7dadb388215396ba5fbee2c610a04d6":
        raise ValueError("Tokenizer revision changed: prepare and record a new source before running")
    provenance = read_json(ROOT / "manifests/resources.json")
    # Manifest keys were produced on Windows and use backslashes; normalize them
    # so the same manifest verifies on POSIX checkouts.
    for name, info in provenance["files"].items():
        path = ROOT / name.replace("\\", "/")
        if not _resource_matches(path.read_bytes(), info["sha256"]):
            raise ValueError(f"Resource changed since prepare: {name}")
    if config["upstream"]["lost_in_the_middle"] != provenance["lost_in_the_middle_commit"]:
        raise ValueError("Upstream revision mismatch")
    if config["upstream"]["llmlingua"] != provenance["llmlingua_commit"]:
        raise ValueError("LLMLingua revision mismatch")


def slots(config, counter):
    for qid, position, row in iter_samples(config):
        for method in config["methods"]:
            started = time.perf_counter()
            built = build_prompt(visible_sample(row), method, config, counter)
            yield {"slot_id": f"{qid}:{position}:{method}", "question_id": qid,
                   "position": position, "method": method, "split": config["split"],
                   "answers": row["answers"], "compression_seconds": time.perf_counter() - started,
                   **built}


def plan(config):
    verify_resources(config)
    counter = TokenCounter()
    totals, lengths = {}, []
    for row in slots(config, counter):
        group = totals.setdefault(row["method"], {"slots": 0, "input_text_tokens": 0,
                                                  "output_token_cap": 0, "cache_hits": 0})
        group["slots"] += 1
        group["input_text_tokens"] += row["compressed_tokens"]
        group["output_token_cap"] += config["max_tokens"]
        payload = request_payload(config, row["prompt"])
        group["cache_hits"] += (ROOT / "cache/api" / f"{cache_key(config, payload)}.json").exists()
        lengths.append(row["compressed_tokens"])
    result = {"config_hash": configuration_hash(config), "split": config["split"],
              "provider": config["provider"], "model": config["model"],
              "methods": totals, "max_input_text_tokens": max(lengths),
              "mean_input_text_tokens": statistics.mean(lengths),
              "logical_call_limit": config["max_requests_per_run"],
              "wire_attempt_limit": config["max_requests_per_run"] * config["max_attempts"],
              "token_count_note": config["tokenizer"]["counting"],
              "api_requests_sent": 0}
    atomic_json(ROOT / f"reports/{config['split']}-plan.json", result)
    return result


def run(config, limit=None):
    # Fail before any experiment work or network call when the key is absent.
    key = get_key(config)
    verify_resources(config)
    if limit is not None and limit <= 0:
        raise ValueError("--limit must be positive")
    config_hash = configuration_hash(config)
    manifest = read_json(ROOT / f"manifests/{config['split']}.json")
    run_id = digest({"config_hash": config_hash, "manifest": manifest})[:20]
    run_dir = ROOT / "outputs/stage1" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    # Atomic lock prevents accidentally running two processes against the same log/cache.
    lock = run_dir / ".running"
    try:
        lock_fd = lock.open("x")
    except FileExistsError:
        raise ValueError(f"Run already active: {run_dir}. If interrupted, remove .running after confirming no process is active.") from None
    client = None
    try:
        meta = {"run_id": run_id, "config_hash": config_hash, "config": config,
                "implementation_hash": implementation_hash(), "question_ids": manifest["question_ids"],
                "manifest": manifest, "created_at": datetime.now(timezone.utc).isoformat()}
        if not (run_dir / "run.json").exists():
            atomic_json(run_dir / "run.json", meta)
        result_path = run_dir / "results.jsonl"
        existing = read_jsonl(result_path)
        # Repair a partial final line before appending; durable rows are preserved.
        if result_path.exists() and result_path.read_bytes() and not result_path.read_bytes().endswith(b"\n"):
            import json
            result_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in existing), encoding="utf-8")
        completed = {r["slot_id"] for r in existing if r["status"] == "success"}
        counter = TokenCounter()
        client = DeepSeekClient(config, key)
        request_budget = min(limit or config["max_requests_per_run"], config["max_requests_per_run"])
        requests = 0
        for row in slots(config, counter):
            if row["slot_id"] in completed:
                continue
            payload = request_payload(config, row["prompt"])
            ck = cache_key(config, payload)
            cached = (ROOT / "cache/api" / f"{ck}.json").exists()
            if not cached and requests >= request_budget:
                break
            started = time.perf_counter()
            fatal = False
            try:
                if row["compressed_tokens"] + config["max_tokens"] > config["max_context_tokens"]:
                    raise APIError("Configured context guard exceeded; inspect prompt length before retry")
                saved, hit = cached_completion(config, payload, client, {
                    "implementation_hash": meta["implementation_hash"], "config_hash": config_hash})
                result = saved["result"]
                if not hit:
                    requests += 1
                row.update(status="success", answer=result["answer"],
                           answer_before_recovery=result["answer"], answer_after_recovery=result["answer"],
                           recovery_seconds=0, recovery_enabled=False, usage=result["usage"],
                           score=score(result["answer"], row["answers"]),
                           response_model=result["response_model"],
                           system_fingerprint=result["system_fingerprint"],
                           response_id=result["response_id"], finish_reason=result["finish_reason"],
                           api_seconds=result["api_seconds"], attempts=result["attempts"],
                           cache_hit=hit, generation_created_at=result["created_at"],
                           cache_source_provenance=saved["provenance"])
            except APIError as exc:
                # Requests is a logical-call budget; attempts records wire retries separately.
                if exc.attempts:
                    requests += 1
                row.update(status="failed", error=str(exc), attempts=exc.attempts, cache_hit=False)
                row.update(exc.response_details)
                fatal = exc.fatal
            row.update(cache_key=ck, prompt_hash=digest(row["prompt"]), config_hash=config_hash,
                       expected_model_version=config["expected_model_version"], model=config["model"],
                       endpoint=config["base_url"], upstream=config["upstream"],
                       tokenizer=config["tokenizer"],
                       observed_seconds=time.perf_counter() - started,
                       total_pipeline_seconds=row["compression_seconds"] + time.perf_counter() - started,
                       timestamp=datetime.now(timezone.utc).isoformat())
            append_jsonl(result_path, row)
            print(f"{row['status']}: {row['method']} position={row['position']} requests={requests}/{request_budget}", flush=True)
            if fatal:
                break
            if not row["cache_hit"]:
                time.sleep(config["request_interval_seconds"])
        summary = summarize(run_dir)
        print(f"Results: {run_dir}; complete={summary['complete']}", flush=True)
        return run_dir, summary["complete"]
    finally:
        if client:
            client.close()
        lock_fd.close()
        lock.unlink(missing_ok=True)
