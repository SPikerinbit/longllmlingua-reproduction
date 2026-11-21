"""Stage-two adapter: LLMLingua / LongLLMLingua compression on the pinned reference.

The pinned upstream ``PromptCompressor`` (commit 5a4c78ae, vendored as ``.reference``)
is reused as-is; this module supplies the experiment-side wiring that stage one
needs:

* the library's token counter is replaced by the official answer-model tokenizer so
  every token figure in the project uses one ruler;
* the compression model is loaded with plain ``transformers`` so it can live on the
  NPU device a torch_npu runtime exposes (the library only knows cuda/cpu/mps);
* the library's compression target is a *soft* rate, while the project's main table
  needs a hard budget (same ruler as BM25), so the adapter retries with a tightened
  rate and records both the natural and the enforced result;
* coarse/fine stage outputs are captured for the mechanism trace: per-document
  ranking scores, retained documents, dynamic per-document ratios and the text that
  actually survived.

The restrict statement is handled the way the pinned code handles it: it is
appended inside the document-level condition perplexity only (see
``get_distance_longllmlingua``), never to the prompt handed to the answer model.
The ``restrict`` switch therefore toggles that ranker condition; a documented
difference from the paper's prose is recorded in ``docs/stage2-parameter-map.md``.
"""

from __future__ import annotations

import math
import time

from .llmlingua_pkg import load_prompt_compressor
from .methods import prompt, template

RESTRICT_STATEMENT = "We can get the answer to this question in the given documents."
SOFT_TARGET_MARGIN = 0.98
MIN_RATE = 0.01


class TokenCounterAdapter:
    """Expose the library's ``encode``/``decode`` surface on the stage-one counter."""

    def __init__(self, counter):
        self.counter = counter

    def encode(self, text):
        return self.counter.tokenizer.encode(text).ids

    def decode(self, ids):
        return self.counter.tokenizer.decode(ids)


def _tracking_class(base):
    class Stage2PromptCompressor(base):
        restrict_enabled = True
        restrict_statement = RESTRICT_STATEMENT
        last_rank_results = ()
        last_context_used = ()
        last_dynamic_ratio = ()

        def load_model(self, model_name, device_map="cpu", model_config=None):
            import torch
            from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

            model_config = dict(model_config or {})
            dtype = getattr(torch, model_config.pop("torch_dtype", "float16"))
            attn = model_config.pop("attn_implementation", "eager")
            trust = model_config.pop("trust_remote_code", False)
            config = AutoConfig.from_pretrained(model_name, trust_remote_code=trust)
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust)
            tokenizer.padding_side = "left"
            tokenizer.pad_token_id = config.pad_token_id or tokenizer.eos_token_id
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=dtype, attn_implementation=attn,
                device_map="cpu", low_cpu_mem_usage=True)
            self.tokenizer = tokenizer
            self.device = "cpu"
            self.context_idxs = []
            self.max_position_embeddings = config.max_position_embeddings

        def get_ppl(self, *args, **kwargs):
            # The pinned reference was written when ``past_key_values`` were plain
            # (key, value) tuples.  Transformers >= 4.46 returns a ``Cache`` object and
            # rejects legacy tuples, so the adapter converts in both directions without
            # touching the official file (recorded in the difference table).
            legacy = kwargs.get("past_key_values")
            if legacy is not None and not hasattr(legacy, "to_legacy_cache"):
                from transformers.cache_utils import DynamicCache

                kwargs["past_key_values"] = DynamicCache.from_legacy_cache(
                    tuple((layer[0], layer[1]) for layer in legacy))
            result = super().get_ppl(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                loss, cache = result
                if cache is not None and hasattr(cache, "to_legacy_cache"):
                    return loss, cache.to_legacy_cache()
            return result

        def get_condition_ppl(self, text, question, *args, **kwargs):
            if not self.restrict_enabled:
                suffix = " " + self.restrict_statement
                if isinstance(question, str) and question.endswith(suffix):
                    question = question[:-len(suffix)]
            return super().get_condition_ppl(text, question, *args, **kwargs)

        def get_rank_results(self, *args, **kwargs):
            results = super().get_rank_results(*args, **kwargs)
            self.last_rank_results = list(results)
            return results

        def control_context_budget(self, *args, **kwargs):
            context, ratios, used = super().control_context_budget(*args, **kwargs)
            self.last_context_used = list(used)
            self.last_dynamic_ratio = list(ratios)
            return context, ratios, used

    return Stage2PromptCompressor


def load_compressor(config, counter):
    """Load the pinned compressor on the configured device; returns (compressor, meta)."""
    spec = config["compressor"]
    import torch

    Compressor = _tracking_class(load_prompt_compressor())
    started = time.perf_counter()
    compressor = Compressor(
        model_name=spec["model_path"], device_map="cpu",
        model_config={"torch_dtype": spec["torch_dtype"],
                      "attn_implementation": spec["attn_implementation"]})
    load_seconds = time.perf_counter() - started
    device = spec["device"]
    move_started = time.perf_counter()
    compressor.model.to(device)
    compressor.device = device
    compressor.model.eval()
    compressor.oai_tokenizer = TokenCounterAdapter(counter)
    meta = {"model_path": spec["model_path"], "model_name": spec.get("model_name"),
            "device": device, "torch_dtype": spec["torch_dtype"],
            "attn_implementation": spec["attn_implementation"],
            "load_seconds": load_seconds,
            "move_seconds": time.perf_counter() - move_started,
            "max_position_embeddings": compressor.max_position_embeddings}
    return compressor, meta


def method_spec(config, method):
    try:
        spec = dict(config["methods"][method])
    except KeyError:
        raise ValueError(f"Unknown stage-two method: {method}") from None
    spec.setdefault("kind", "longllmlingua" if method.startswith("longllmlingua") else "llmlingua")
    if spec["kind"] not in ("llmlingua", "longllmlingua"):
        raise ValueError(f"Unknown method kind: {spec['kind']}")
    if float(spec["ratio"]) <= 1:
        raise ValueError("Compression ratio must be greater than 1")
    return spec


def _render_context(documents):
    return [f"Document [{i+1}](Title: {doc['title']}) {doc['text']}"
            for i, doc in enumerate(documents)]


def _strip_question_prefix(text, question):
    for candidate in (question + "\n\n", question + "\n", question):
        if text.startswith(candidate):
            return text[len(candidate):], True
    return text, False


def _call(compressor, config, spec, context, question, rate, target_tokens, counter):
    # k=2 has no direct parameter in the pinned signature; the paper's granular
    # control coefficient is approximated by letting the coarse stage keep twice
    # the fine-grained budget (recorded in the parameter map).
    coarse_target = max(1, int(2 * target_tokens))
    arguments = dict(
        context=context, instruction="", question=question, rate=rate, target_token=-1,
        iterative_size=config["compressor"]["iterative_size"],
        use_sentence_level_filter=False,
        use_context_level_filter=bool(spec["use_context_level_filter"]),
        use_token_level_filter=True,
        context_level_target_token=coarse_target,
        context_budget=config["compressor"]["context_budget"],
        condition_in_question=spec["condition_in_question"],
        reorder_context=spec["reorder_context"],
        dynamic_context_compression_ratio=float(spec["dynamic_context_compression_ratio"]),
        condition_compare=bool(spec["condition_compare"]),
        rank_method=spec["rank_method"],
        concate_question=False,
    )
    started = time.perf_counter()
    result = compressor.compress_prompt(**arguments)
    seconds = time.perf_counter() - started
    ranking = [{"doc_index": int(idx), "score": float(score)}
               for idx, score in compressor.last_rank_results]
    used = [int(idx) for idx in compressor.last_context_used]
    compressed_context, stripped = _strip_question_prefix(result["compressed_prompt"], question)
    return {
        "compressed_context": compressed_context.strip(),
        "question_prefix_stripped": stripped,
        "library_origin_tokens": result["origin_tokens"],
        "library_compressed_tokens": result["compressed_tokens"],
        "library_ratio_label": result["ratio"],
        "library_rate_label": result["rate"],
        "ranking": ranking,
        "used_doc_indices": used,
        "dynamic_ratios": [float(value) for value in compressor.last_dynamic_ratio],
        "seconds": seconds,
    }


def compress_sample(compressor, config, method, sample, counter):
    """Compress one visible sample and return the stage-two prompt plus mechanism trace."""
    spec = method_spec(config, method)
    started = time.perf_counter()
    question = sample["question"]
    documents = sample["documents"]
    compressor.restrict_enabled = bool(spec.get("restrict", False))
    context = _render_context(documents)
    origin_prompt = prompt(question, documents)
    origin_tokens = counter.count(origin_prompt)
    ratio = float(spec["ratio"])
    target_tokens = math.floor(origin_tokens / ratio)
    builder = template()
    mode = config["compressor"]["budget_mode"]
    passes = 1 if mode == "natural" else int(config["compressor"]["max_budget_passes"])
    rate = 1.0 / ratio
    attempts = []
    chosen = None
    for pass_index in range(passes):
        result = _call(compressor, config, spec, context, question, rate, target_tokens, counter)
        final_prompt = builder.format(question=question, search_results=result["compressed_context"])
        full_tokens = counter.count(final_prompt)
        attempt = dict(result, pass_index=pass_index, rate=rate,
                       compressed_tokens=full_tokens,
                       actual_ratio=origin_tokens / full_tokens,
                       budget_satisfied=full_tokens <= target_tokens,
                       final_prompt=final_prompt)
        attempts.append(attempt)
        chosen = attempt
        if mode != "hard" or attempt["budget_satisfied"]:
            break
        tightened = rate * (target_tokens / max(full_tokens, 1)) * SOFT_TARGET_MARGIN
        if tightened >= rate or tightened < MIN_RATE:
            break
        rate = tightened
    chosen = next((a for a in attempts if a["budget_satisfied"]), chosen) if mode == "hard" else attempts[0]
    documents_by_index = {index: doc for index, doc in enumerate(documents)}
    used = chosen["used_doc_indices"]
    trace = {
        "budget_mode": mode,
        "target_tokens": target_tokens,
        "attempts": [{key: value for key, value in attempt.items()
                      if key not in ("final_prompt", "ranking")} for attempt in attempts],
        "document_scores": [
            {"doc_index": item["doc_index"],
             "doc_id": documents_by_index[item["doc_index"]]["id"],
             "score": item["score"], "retained": item["doc_index"] in used}
            for item in chosen["ranking"] if item["doc_index"] in documents_by_index],
        "used_doc_indices": used,
        "used_doc_ids": [documents_by_index[i]["id"] for i in used if i in documents_by_index],
        "dropped_doc_ids": [doc["id"] for i, doc in documents_by_index.items() if i not in used],
        "dynamic_ratios": chosen["dynamic_ratios"],
        "compressed_context_tokens": counter.count(chosen["compressed_context"]),
        "compressed_context_chars": len(chosen["compressed_context"]),
        "compressed_context_preview": chosen["compressed_context"][:400],
        "question_prefix_stripped": chosen["question_prefix_stripped"],
        "restrict_enabled": bool(spec.get("restrict", False)),
        "library_origin_tokens": chosen["library_origin_tokens"],
        "library_compressed_tokens": chosen["library_compressed_tokens"],
        "library_ratio_label": chosen["library_ratio_label"],
        "library_rate_label": chosen["library_rate_label"],
    }
    return {
        "prompt": chosen["final_prompt"],
        "origin_tokens": origin_tokens,
        "compressed_tokens": chosen["compressed_tokens"],
        "actual_ratio": chosen["actual_ratio"],
        "target_ratio": ratio,
        "target_tokens": target_tokens,
        "budget_satisfied": chosen["budget_satisfied"],
        "selected_doc_ids": [documents_by_index[i]["id"] for i in used if i in documents_by_index],
        "truncated_doc_ids": [],
        "ranking": trace["document_scores"],
        "compression_seconds": time.perf_counter() - started,
        "method_version": f"llmlingua-ref-{config['upstream']['llmlingua'][:7]}-{spec['kind']}-v1",
        "trace": trace,
    }
