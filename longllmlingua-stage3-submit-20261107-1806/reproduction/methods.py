from __future__ import annotations

import math
import re
from functools import lru_cache

from rank_bm25 import BM25Okapi
from tokenizers import Tokenizer

from .common import ROOT


class TokenCounter:
    """Pinned official tokenizer; text tokens exclude provider-side chat framing."""

    def __init__(self, path=None):
        self.tokenizer = Tokenizer.from_file(str(path or ROOT / "data/tokenizer/tokenizer.json"))

    def count(self, text):
        return len(self.tokenizer.encode(text, add_special_tokens=False).ids)


@lru_cache(maxsize=1)
def template():
    return (ROOT / "vendor/lost_in_the_middle/qa.prompt").read_text(encoding="utf-8").rstrip("\n")


def prompt(question, documents):
    formatted = [f"Document [{i+1}](Title: {doc['title']}) {doc['text']}"
                 for i, doc in enumerate(documents)]
    return template().format(question=question, search_results="\n".join(formatted))


def words(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def build_prompt(sample, method, config, counter):
    """Only question and explicitly visible document fields are accepted here."""
    original = prompt(sample["question"], sample["documents"])
    original_tokens = counter.count(original)
    if method == "original":
        return {"prompt": original, "origin_tokens": original_tokens,
                "compressed_tokens": original_tokens, "actual_ratio": 1.0,
                "target_ratio": 1, "target_tokens": original_tokens,
                "selected_doc_ids": [d["id"] for d in sample["documents"]],
                "truncated_doc_ids": [], "method_version": "original-v1"}
    ratio = {"bm25_2x": 2, "bm25_4x": 4}[method]
    budget = math.floor(original_tokens / ratio)
    minimum = counter.count(prompt(sample["question"], []))
    if budget <= minimum:
        raise ValueError("Compression budget cannot fit the fixed instruction and question")
    docs = sample["documents"]
    corpus = [words(d["title"] + " " + d["text"]) or [""] for d in docs]
    bm25 = BM25Okapi(corpus, k1=config["bm25"]["k1"], b=config["bm25"]["b"])
    scores = bm25.get_scores(words(sample["question"]))
    # Stable ID tie-break avoids positional artifacts for equal scores.
    ranked = sorted(range(len(docs)), key=lambda i: (-float(scores[i]), docs[i]["id"]))
    selected = {}
    truncated = []

    def render():
        return prompt(sample["question"], [selected[i] for i in sorted(selected)])

    for i in ranked:
        selected[i] = dict(docs[i])
        if counter.count(render()) <= budget:
            continue
        # Deterministic prefix clipping of the final passage, with the *full* prompt re-counted.
        parts = docs[i]["text"].split()
        lo, hi = 0, len(parts)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            selected[i]["text"] = " ".join(parts[:mid])
            if counter.count(render()) <= budget:
                lo = mid
            else:
                hi = mid - 1
        selected[i]["text"] = " ".join(parts[:lo])
        # Token lengths can be slightly non-monotonic at BPE boundaries: enforce final bound.
        while lo > 0 and counter.count(render()) > budget:
            lo -= 1
            selected[i]["text"] = " ".join(parts[:lo])
        if lo == 0:
            del selected[i]
            continue
        truncated.append(docs[i]["id"])
        break
    if not selected:
        raise ValueError("No nonempty document fits the compression budget")
    compressed = render()
    tokens = counter.count(compressed)
    if tokens > budget:
        raise ValueError("BM25 budget invariant failed")
    return {"prompt": compressed, "origin_tokens": original_tokens,
            "compressed_tokens": tokens, "actual_ratio": original_tokens / tokens,
            "target_ratio": ratio, "target_tokens": budget,
            "selected_doc_ids": [selected[i]["id"] for i in sorted(selected)],
            "truncated_doc_ids": truncated,
            "ranking": [{"doc_id": docs[i]["id"], "score": float(scores[i])} for i in ranked],
            "method_version": "bm25-doc-prefix-v1"}
