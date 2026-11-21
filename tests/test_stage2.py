"""Stage-two tests: config contract, compression budget adapter, recovery, reporting.

These run on the CPU-only stage-one environment: nothing here loads the 7B model or
calls the API.  The adapter tests use a synthetic compressor so the budget/retry and
question-prefix behaviour is exercised without torch.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from reproduction import common, compression, recovery
from reproduction.stage2 import load_stage2_config, summarize

ROOT = common.ROOT


def _config():
    return load_stage2_config(ROOT / "configs/stage2.json")


def test_stage2_config_accepts_pinned_matrix():
    config = _config()
    assert config["split"] == "smoke"
    assert set(config["methods"]) == {"llmlingua_2x", "llmlingua_4x",
                                      "longllmlingua_2x", "longllmlingua_4x"}
    assert config["methods"]["longllmlingua_2x"]["recovery"] is True
    assert config["methods"]["llmlingua_2x"]["recovery"] is False
    assert config["compressor"]["iterative_size"] == 200


@pytest.mark.parametrize("mutate", [
    lambda config: config["methods"].__setitem__(
        "llmlingua_2x", dict(config["methods"]["llmlingua_2x"], ratio=1.0)),
    lambda config: config["compressor"].__setitem__("budget_mode", "loose"),
    lambda config: config["upstream"].__setitem__("llmlingua", "0" * 40),
    lambda config: config.__setitem__("thinking", {"type": "enabled"}),
    lambda config: config["methods"]["longllmlingua_2x"].__setitem__("restrict", "yes"),
])
def test_stage2_config_rejects_contract_violations(tmp_path, mutate):
    config = json.loads((ROOT / "configs/stage2.json").read_text(encoding="utf-8"))
    mutate(config)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError):
        load_stage2_config(path)


class _FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return SimpleNamespace(ids=[ord(char) for char in text])

    def decode(self, ids):
        return "".join(chr(value) for value in ids)


class _FakeCounter:
    def __init__(self):
        self.tokenizer = _FakeTokenizer()

    def count(self, text):
        return len(text)


class _FakeCompressor:
    """Length-proportional stand-in for the pinned compressor's soft target."""

    def __init__(self):
        self.last_rank_results = [(0, 0.2), (1, 0.9)]
        self.last_context_used = [0]
        self.last_dynamic_ratio = [0.1, 0.2]
        self.restrict_enabled = True
        self.calls = []

    def compress_prompt(self, context, question, rate, **kwargs):
        self.calls.append(rate)
        joined = "\n\n".join(context)
        keep = max(1, int(rate * len(joined)))
        compressed = joined[:keep]
        return {"compressed_prompt": question + "\n\n" + compressed,
                "origin_tokens": len(joined), "compressed_tokens": keep,
                "ratio": "2.0x", "rate": "50.0%"}


def _sample():
    documents = [{"id": f"doc{i}", "title": f"Title {i}", "text": "word " * 200}
                 for i in range(2)]
    return {"question": "Who wrote it?", "documents": documents}


def test_hard_budget_retries_until_full_prompt_fits():
    config = _config()
    config["compressor"]["budget_mode"] = "hard"
    config["compressor"]["max_budget_passes"] = 4
    compressor = _FakeCompressor()
    result = compression.compress_sample(
        compressor, config, "longllmlingua_2x", _sample(), _FakeCounter())
    assert result["budget_satisfied"] is True
    assert result["compressed_tokens"] <= result["target_tokens"]
    assert len(result["trace"]["attempts"]) >= 2
    assert result["actual_ratio"] >= result["target_ratio"]
    assert result["trace"]["question_prefix_stripped"] is True
    assert result["trace"]["restrict_enabled"] is True
    assert result["trace"]["used_doc_ids"] == ["doc0"]
    assert result["trace"]["dropped_doc_ids"] == ["doc1"]


def test_natural_mode_keeps_single_attempt_even_when_over_budget():
    config = _config()
    config["compressor"]["budget_mode"] = "natural"
    compressor = _FakeCompressor()
    result = compression.compress_sample(
        compressor, config, "llmlingua_2x", _sample(), _FakeCounter())
    assert len(result["trace"]["attempts"]) == 1
    assert result["budget_satisfied"] is False
    assert len(compressor.calls) == 1


def test_recovery_restores_original_span_into_response():
    counter = _FakeCounter()
    original = "alpha beta gamma delta"
    compressed = "alpha gamma"
    response = "alpha gamma epsilon"
    recovered, stats = recovery.recover_answer(original, compressed, response, counter)
    # The compressed span "alpha gamma" is widened back to "alpha beta gamma"; the
    # trailing response text must survive untouched.
    assert recovered == "alpha beta gamma epsilon"
    assert stats["matched_spans"] >= 1
    assert stats["matched_response_tokens"] >= len("alpha gamma")
    assert stats["changed"] is True


def test_recovery_without_overlap_returns_response_unchanged():
    counter = _FakeCounter()
    recovered, stats = recovery.recover_answer(
        "alpha beta", "alpha beta", "zzz", counter)
    assert recovered == "zzz"
    assert stats["changed"] is False
    assert stats["matched_spans"] == 0


def test_summarize_reports_before_and_after_recovery(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    row = {"slot_id": "q1:1:longllmlingua_2x", "question_id": "q1", "position": 1,
           "split": "smoke", "stage": 2, "method": "longllmlingua_2x",
           "status": "success", "score": 1, "score_before_recovery": 0,
           "score_after_recovery": 1, "actual_ratio": 2.1,
           "budget_satisfied": True, "compression_seconds": 3.0,
           "recovery_stats": {"changed": True},
           "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
    (run_dir / "results.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    meta = {"run_id": "run", "split": "smoke", "question_ids": ["q1"],
            "config": {"methods": {"longllmlingua_2x": {}},
                       "positions": [1],
                       "compressor": {"budget_mode": "hard"}},
            "compressor": {"model_name": "fake", "device": "cpu"}}
    (run_dir / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    report = summarize(run_dir)
    group = report["groups"][0]
    assert report["complete"] is True
    assert group["best_subspan_em_before_recovery"] == 0
    assert group["best_subspan_em_after_recovery"] == 1
    assert group["recovery_changed_rate"] == 1
