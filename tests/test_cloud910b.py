"""Offline launcher checks; no torch stack or real API used."""
import json
import sys
from types import SimpleNamespace
from scripts import cloud910b as cloud


def exercise(monkeypatch, tmp_path, benchmark):
    events = []
    npu = SimpleNamespace(synchronize=lambda: events.append("sync"),
        reset_peak_memory_stats=lambda: events.append("reset"),
        max_memory_allocated=lambda: 123, max_memory_reserved=lambda: 456)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(npu=npu))
    monkeypatch.setitem(sys.modules, "torch_npu", SimpleNamespace())
    monkeypatch.setattr(cloud, "ROOT", tmp_path)
    config = {"compressor": {"device": "npu:0", "model_revision": "fixed"},
              "benchmark_no_cache": benchmark, "experiment_phase": "efficiency"}
    monkeypatch.setattr(cloud.stage3, "load_stage3_config", lambda p: config)
    monkeypatch.setattr(cloud.methods, "TokenCounter", lambda: object())
    monkeypatch.setattr(cloud.data, "iter_samples", lambda c: iter([("q", 1, {})]))
    monkeypatch.setattr(cloud.data, "visible_sample", lambda x: x)
    monkeypatch.setattr(cloud.compression, "load_compressor", lambda *a: (object(), {}))
    monkeypatch.setattr(cloud.compression, "compress_sample", lambda *a: {"prompt": "test"})
    monkeypatch.setattr(cloud, "environment", lambda: {"offline_test": True})
    monkeypatch.setattr(cloud.stage3, "summarize", lambda p: {"complete": True})
    from reproduction import stage2
    monkeypatch.setattr(stage2, "_compression_key", lambda *a: "key")
    original_cache = cloud.api.cached_completion
    def engine(c, limit=None):
        directory = tmp_path / "run"
        if benchmark:
            result, hit, key = stage2._compress_cached(None, c, "m", {}, None)
            assert not hit and key == "key"
            client = SimpleNamespace(complete=lambda p: {"answer": "fresh"})
            monkeypatch.setattr(cloud.api, "cache_key", lambda *a: "qa")
            saved, hit = cloud.api.cached_completion({}, {}, client, {})
            assert not hit and saved["result"]["answer"] == "fresh"
        else:
            cloud.compression.compress_sample()
        cloud.common.append_jsonl(directory / "results.jsonl", {
            "kind": "longllmlingua", "compression_cache_hit": False, "cache_hit": False})
        return directory, 1
    monkeypatch.setattr(cloud.stage3, "run", engine)
    assert cloud.run("config.json", None) == 0
    row = json.loads((tmp_path / "run/results.jsonl").read_text())
    assert row["telemetry"]["peak_allocated_bytes"] == 123
    assert row["telemetry"]["compression_measured"]
    assert "reset" in events and events.count("sync") >= 3
    assert cloud.api.cached_completion is original_cache


def test_warmed_compression_is_synchronized_and_metered(monkeypatch, tmp_path):
    exercise(monkeypatch, tmp_path, False)


def test_efficiency_bypasses_both_local_caches(monkeypatch, tmp_path):
    exercise(monkeypatch, tmp_path, True)
