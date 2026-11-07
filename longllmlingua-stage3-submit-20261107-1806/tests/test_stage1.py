import json
from copy import deepcopy

import httpx
import pytest

from reproduction.api import APIError, DeepSeekClient, cache_key, cached_completion, request_payload
from reproduction.common import ROOT, atomic_json, load_config, read_jsonl
from reproduction.data import question_id, visible_sample
from reproduction.evaluation import score, summarize
from reproduction.methods import TokenCounter, build_prompt, prompt


@pytest.fixture
def config():
    value = load_config()
    value["retry_delay_seconds"] = 0
    return value


@pytest.fixture
def sample():
    docs = [{"id": str(i), "title": f"Article {i}",
             "text": ("Paris France capital city. " if i == 7 else "Trees forests rivers mountains. ") * 30,
             "isgold": i == 7, "hasanswer": i == 7, "original_retrieval_index": i, "score": 1}
            for i in range(20)]
    return {"question": "What is the capital of France?", "answers": ["SECRET GOLD ANSWER"], "ctxs": docs}


def test_visible_sample_allowlist(sample):
    visible = visible_sample(sample)
    assert set(visible) == {"question", "documents"}
    assert all(set(d) == {"id", "title", "text"} for d in visible["documents"])
    assert "SECRET GOLD ANSWER" not in prompt(visible["question"], visible["documents"])


def test_question_id_independent_of_document_position(sample):
    other = deepcopy(sample)
    other["ctxs"].reverse()
    assert question_id(other) == question_id(sample)


@pytest.mark.parametrize("method,ratio", [("original", 1), ("bm25_2x", 2), ("bm25_4x", 4)])
def test_real_tokenizer_budget_and_order(sample, config, method, ratio):
    counter = TokenCounter()
    built = build_prompt(visible_sample(sample), method, config, counter)
    assert built["compressed_tokens"] == counter.count(built["prompt"])
    assert built["compressed_tokens"] <= built["target_tokens"]
    assert built["actual_ratio"] >= ratio
    assert list(map(int, built["selected_doc_ids"])) == sorted(map(int, built["selected_doc_ids"]))
    if method != "original":
        assert built["ranking"][0]["doc_id"] == "7"
        assert "7" in built["selected_doc_ids"]


@pytest.mark.parametrize("prediction,answers,expected", [
    ("The answer is PARIS!", ["Paris"], 1),
    ("Wrong\nParis", ["Paris"], 0),
    ("\nParis", ["Paris"], 0),
    ("It was Rontgen.", ["Einstein", "Rontgen"], 1),
    ("New York", ["New-York"], 0),
])
def test_exact_upstream_scoring(prediction, answers, expected):
    assert score(prediction, answers) == expected


def success_response(model="deepseek-flash", answer="Paris", finish="stop"):
    return {"id": "test-response", "model": model, "choices": [
        {"message": {"content": answer}, "finish_reason": finish}],
        "usage": {"prompt_tokens": 90, "completion_tokens": 2}}


def test_api_payload_cache_and_credential_isolation(config, tmp_path):
    calls = []

    def handle(request):
        calls.append(request)
        body = json.loads(request.content)
        assert body["thinking"] == {"type": "disabled"}
        assert body["temperature"] == 0
        assert request.url == "https://api.deepseek.com/chat/completions"
        return httpx.Response(200, json=success_response())

    http = httpx.Client(transport=httpx.MockTransport(handle))
    client = DeepSeekClient(config, "test-secret-never-save", http)
    payload = request_payload(config, "Question?")
    first, hit = cached_completion(config, payload, client, {"test": True}, tmp_path)
    second, hit2 = cached_completion(config, payload, None, {"test": True}, tmp_path)
    assert not hit and hit2 and first == second and len(calls) == 1
    assert "test-secret-never-save" not in next(tmp_path.glob("*.json")).read_text()
    client.close()


def test_cache_changes_with_prompt_model_generation(config):
    original = cache_key(config, request_payload(config, "A"))
    assert original != cache_key(config, request_payload(config, "B"))
    for field, value in (("model", "another"), ("max_tokens", 64), ("temperature", 0.5)):
        changed = deepcopy(config)
        changed[field] = value
        assert original != cache_key(changed, request_payload(changed, "A"))


def test_retry_429_then_success(config):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(429) if len(calls) == 1 else httpx.Response(200, json=success_response())

    client = DeepSeekClient(config, "fake", httpx.Client(transport=httpx.MockTransport(handle)))
    assert client.complete(request_payload(config, "Q"))["attempts"] == 2
    assert len(calls) == 2
    client.close()


@pytest.mark.parametrize("status", [401, 402, 403])
def test_auth_or_balance_errors_not_retried(config, status):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(status, text="sensitive upstream error should not be persisted")

    client = DeepSeekClient(config, "fake", httpx.Client(transport=httpx.MockTransport(handle)))
    with pytest.raises(APIError) as exc:
        client.complete(request_payload(config, "Q"))
    assert exc.value.fatal and len(calls) == 1
    assert "sensitive" not in str(exc.value)
    client.close()


def test_failed_or_truncated_response_never_cached(config, tmp_path):
    client = DeepSeekClient(config, "fake", httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=success_response(finish="length")))))
    with pytest.raises(APIError) as exc:
        cached_completion(config, request_payload(config, "Q"), client, {}, tmp_path)
    assert not list(tmp_path.glob("*.json"))
    assert exc.value.response_details["finish_reason"] == "length"
    assert exc.value.response_details["usage"]["completion_tokens"] == 2
    client.close()


def test_summary_includes_missing_and_rescores(config, tmp_path):
    config["methods"] = ["original"]
    config["positions"] = [1]
    atomic_json(tmp_path / "run.json", {"config": config, "question_ids": ["a", "b", "c"]})
    rows = [{"slot_id": "a", "status": "failed", "method": "original", "position": 1},
            {"slot_id": "a", "status": "success", "method": "original", "position": 1,
             "answer": "Paris", "answers": ["Paris"], "score": 0, "actual_ratio": 1},
            {"slot_id": "b", "status": "failed", "method": "original", "position": 1}]
    (tmp_path / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    result = summarize(tmp_path)
    row = result["groups"][0]
    assert not result["complete"]
    assert (row["success"], row["failed"], row["missing"], row["best_subspan_em"]) == (1, 1, 1, 1)


def test_interrupted_final_result_line(tmp_path):
    path = tmp_path / "results.jsonl"
    path.write_text('{"status": "success"}\n{"status":')
    assert read_jsonl(path) == [{"status": "success"}]


def test_full_real_data_nested_manifests():
    from reproduction.data import load_position, document_set
    smoke = json.loads((ROOT / "manifests/smoke.json").read_text())
    pilot = json.loads((ROOT / "manifests/pilot.json").read_text())
    main = json.loads((ROOT / "manifests/main.json").read_text())
    assert smoke["question_ids"] == pilot["question_ids"][:20] == main["question_ids"][:20]
    assert pilot["question_ids"] == main["question_ids"][:100]
    assert len(main["question_ids"]) == 500
    canonical = load_position(1)
    for pos in (5, 10, 15, 20):
        other = load_position(pos)
        assert set(other) == set(canonical)
        for qid in smoke["question_ids"]:
            assert document_set(other[qid]) == document_set(canonical[qid])


def test_missing_document_id_uses_content_without_gold(sample):
    from reproduction.data import document_id
    document = sample["ctxs"][0]
    document.pop("id")
    before = document_id(document)
    document["isgold"] = not document["isgold"]
    assert before == document_id(document)


def test_runner_interrupt_resume_and_cache_rebuild(config, sample, tmp_path, monkeypatch):
    import reproduction.api as api_module
    import reproduction.runner as runner
    config["methods"] = ["original"]
    config["positions"] = [1]
    config["request_interval_seconds"] = 0
    manifest = {"question_ids": ["a", "b"], "source_commit": config["upstream"]["lost_in_the_middle"]}
    atomic_json(tmp_path / "manifests/smoke.json", manifest)
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(api_module, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "verify_resources", lambda config: None)
    monkeypatch.setattr(runner, "get_key", lambda config: "fake-offline-test-key")
    changed = deepcopy(sample)
    changed["question"] = "A second distinct question?"
    monkeypatch.setattr(runner, "iter_samples", lambda config: iter([("a", 1, sample), ("b", 1, changed)]))
    calls = []

    class OfflineClient:
        def __init__(self, *args):
            pass

        def complete(self, payload):
            calls.append(payload)
            return {"answer": "Paris", "usage": {"prompt_tokens": 10, "completion_tokens": 1},
                    "response_model": "OFFLINE-TEST", "response_id": "fake", "system_fingerprint": None,
                    "finish_reason": "stop", "api_seconds": 0.1, "attempts": 1, "created_at": "offline-test"}

        def close(self):
            pass

    monkeypatch.setattr(runner, "DeepSeekClient", OfflineClient)
    directory, complete = runner.run(config, limit=1)
    assert not complete and len(calls) == 1
    directory, complete = runner.run(config, limit=1)
    assert complete and len(calls) == 2
    # Lose the result log after the successful cache write: rebuild without new calls.
    (directory / "results.jsonl").unlink()
    _, complete = runner.run(config, limit=1)
    assert complete and len(calls) == 2
    assert all(row["cache_hit"] for row in read_jsonl(directory / "results.jsonl"))
