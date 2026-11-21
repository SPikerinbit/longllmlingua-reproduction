from scripts.analyze_stage4 import matched_efficiency


def row(method, qid, position=1, status="success", cached=False):
    return {"method": method, "question_id": qid, "position": position,
        "status": status, "cache_hit": cached, "compression_cache_hit": False,
        "compression_seconds": 1.0, "api_seconds": 2.0, "recovery_seconds": .1,
        "total_pipeline_seconds": 3.1, "telemetry": {"peak_allocated_bytes": 1000000000}}


def test_efficiency_uses_common_workload_and_excludes_warmup():
    rows = [row(m, q) for m in ("a", "b") for q in ("warm", "q1", "q2")]
    rows += [row("a", "only-a"), row("b", "only-a", status="failed")]
    result = matched_efficiency(rows, ["a", "b"], ("warm", 1))
    assert result["common_success_samples_before_warmup"] == 3
    assert result["n_per_method"] == 2
    assert result["sample_keys"] == [["q1", 1], ["q2", 1]]
    assert all(r["n"] == 2 for r in result["table"])
    assert all(r["peak_allocated_GB"] == 1 for r in result["table"])


def test_cache_hit_is_not_fresh_efficiency_evidence():
    rows = [row("a", "q"), row("b", "q", cached=True)]
    result = matched_efficiency(rows, ["a", "b"], ("warm", 1))
    assert result["n_per_method"] == 0
    assert all(r["api_seconds_p50"] is None for r in result["table"])


def test_warmup_is_removed_by_identity_not_sorted_position():
    rows = [row(m, q, p) for m in ("a", "b") for q, p in (("z", 1), ("a", 5))]
    result = matched_efficiency(rows, ["a", "b"], ("z", 1))
    assert result["sample_keys"] == [["a", 5]]
