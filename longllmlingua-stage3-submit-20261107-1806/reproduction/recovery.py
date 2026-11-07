"""Token-level subsequence recovery (LongLLMLingua, paper Algorithm 1).

The paper applies recovery to the LLM *response* after question answering, using
the same tokenizer as the compression model (LLaMA-2).  This reproduction pins the
answer model's official DeepSeek tokenizer instead, as recorded in the stage-two
difference table: the response, the original prompt, and the compressed prompt are
all split with the same tokenizer so the subsequence relations stay exact.

The upstream reference implementation of ``PromptCompressor.recover`` works on
whitespace-separated words of the LLaMA tokenizer; this module follows the paper's
token-level definition directly.
"""

from __future__ import annotations

import time
from bisect import bisect_right


def _ids(counter, text: str) -> list[int]:
    return counter.tokenizer.encode(text, add_special_tokens=False).ids


def _positions(ids: list[int]) -> dict[int, list[int]]:
    index: dict[int, list[int]] = {}
    for position, token in enumerate(ids):
        index.setdefault(token, []).append(position)
    return index


def _shortest_span(positions: dict[int, list[int]], key: list[int]):
    """Shortest contiguous span of the original tokens containing ``key`` in order."""
    best = None
    for start in positions.get(key[0], ()):
        cursor = start
        for token in key[1:]:
            candidates = positions.get(token)
            if not candidates:
                start = None
                break
            offset = bisect_right(candidates, cursor)
            if offset >= len(candidates):
                start = None
                break
            cursor = candidates[offset]
        if start is None:
            continue
        length = cursor - start + 1
        if best is None or length < best[0]:
            best = (length, start, cursor + 1)
    return None if best is None else (best[1], best[2])


def recover_answer(original_prompt: str, compressed_prompt: str, response: str,
                   counter) -> tuple[str, dict]:
    """Return ``(recovered_response, stats)`` implementing paper Algorithm 1.

    Unmatched response tokens are kept verbatim.  When nothing matches, the original
    response string is returned unchanged so recovery can never introduce noise.
    """
    started = time.perf_counter()
    original_ids = _ids(counter, original_prompt)
    compressed_ids = _ids(counter, compressed_prompt)
    response_ids = _ids(counter, response)
    stats = {
        "response_tokens": len(response_ids),
        "original_prompt_tokens": len(original_ids),
        "compressed_prompt_tokens": len(compressed_ids),
        "matched_spans": 0,
        "matched_response_tokens": 0,
        "recovered_tokens": 0,
        "changed": False,
        "seconds": 0.0,
    }
    if not response_ids or not compressed_ids or not original_ids:
        stats["seconds"] = time.perf_counter() - started
        return response, stats

    compressed_positions = _positions(compressed_ids)
    original_positions = _positions(original_ids)
    output: list[int] = []
    left = 0
    total = len(response_ids)
    while left < total:
        longest = 0
        for start in compressed_positions.get(response_ids[left], ()):
            length = 0
            while (left + length < total and start + length < len(compressed_ids)
                   and response_ids[left + length] == compressed_ids[start + length]):
                length += 1
            longest = max(longest, length)
        if longest:
            key = response_ids[left:left + longest]
            span = _shortest_span(original_positions, key)
            if span is not None:
                output.extend(original_ids[span[0]:span[1]])
                stats["matched_spans"] += 1
                stats["matched_response_tokens"] += longest
                left += longest
                continue
            output.extend(key)
            left += longest
            continue
        output.append(response_ids[left])
        left += 1

    recovered = counter.tokenizer.decode(output)
    stats["recovered_tokens"] = len(output)
    stats["changed"] = recovered != response
    if stats["matched_spans"] == 0:
        recovered = response
        stats["changed"] = False
    stats["seconds"] = time.perf_counter() - started
    return recovered, stats
