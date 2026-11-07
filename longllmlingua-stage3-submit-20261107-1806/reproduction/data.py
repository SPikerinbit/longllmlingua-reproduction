from __future__ import annotations

import gzip
import hashlib
import json
import random
import time
import unicodedata
from pathlib import Path

import httpx

from .common import ROOT, POSITIONS, atomic_json, digest, read_json

UPSTREAM = "29b8a6d042ce29abccee3db1a73171a107d7e6af"
LLMLINGUA = "5a4c78ae18ab17a98cf997e8259354e546081d64"
TOKENIZER_REV = "314113f8a7dadb388215396ba5fbee2c610a04d6"
RAW = ROOT / "data/raw"


def download(url, path, expected_blob=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        temp = path.with_suffix(path.suffix + ".part")
        for attempt in range(3):
            try:
                with httpx.stream("GET", url, follow_redirects=True, timeout=120) as response:
                    response.raise_for_status()
                    with temp.open("wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                temp.replace(path)
                break
            except (httpx.HTTPError, OSError):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    content = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if expected_blob and blob != expected_blob:
        raise ValueError(f"Integrity mismatch: {path.name}; remove it and prepare again")
    return {"url": url, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
            "git_blob_sha1": blob}


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def question_id(row):
    return digest({"question": normalized(row["question"]),
                   "answers": sorted(set(normalized(a) for a in row["answers"]))})


def raw_path(position):
    return RAW / f"nq-open-20_total_documents_gold_at_{position - 1}.jsonl.gz"


def load_position(position):
    rows = {}
    with gzip.open(raw_path(position), "rt", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            qid = question_id(item)
            if qid in rows:
                raise ValueError(f"Duplicate question ID in position {position}: {qid}")
            docs = item["ctxs"]
            gold = [i + 1 for i, d in enumerate(docs) if d.get("isgold")]
            if len(docs) != 20 or gold != [position]:
                raise ValueError(f"Invalid document count or gold position: {qid}, {gold}")
            if not item["question"].strip() or not item["answers"]:
                raise ValueError(f"Empty question or answers: {qid}")
            rows[qid] = item
    return rows


def document_set(row):
    return sorted(digest({"id": document_id(d), "title": d["title"], "text": d["text"]})
                  for d in row["ctxs"])


def document_id(document):
    # Upstream gold passages do not always carry a retrieval ID.
    return str(document["id"]) if document.get("id") is not None else digest(
        {"title": document["title"], "text": document["text"]})


def prepare():
    """Download only data, pinned source references, and tokenizer (no weights)."""
    url = f"https://api.github.com/repos/nelson-liu/lost-in-the-middle/git/trees/{UPSTREAM}?recursive=1"
    response = httpx.get(url, timeout=60)
    response.raise_for_status()
    tree = {item["path"]: item for item in response.json()["tree"]}
    provenance = {"lost_in_the_middle_commit": UPSTREAM, "llmlingua_commit": LLMLINGUA,
                  "files": {}}
    files = {}
    for position in POSITIONS:
        source = f"qa_data/20_total_documents/{raw_path(position).name}"
        files[source] = raw_path(position)
    for source, name in {
        "LICENSE": "LICENSE",
        "src/lost_in_the_middle/metrics.py": "metrics.py",
        "src/lost_in_the_middle/prompts/qa.prompt": "qa.prompt",
        "src/lost_in_the_middle/prompting.py": "prompting.py.reference",
        "scripts/evaluate_qa_responses.py": "evaluate_qa_responses.py.reference",
    }.items():
        files[source] = ROOT / "vendor/lost_in_the_middle" / name
    for source, path in files.items():
        print(f"Preparing {path.name}", flush=True)
        source_url = f"https://raw.githubusercontent.com/nelson-liu/lost-in-the-middle/{UPSTREAM}/{source}"
        provenance["files"][str(path.relative_to(ROOT))] = download(source_url, path, tree[source]["sha"])
    for name in ("LICENSE", "README.md", "DOCUMENT.md", "setup.py", "llmlingua/prompt_compressor.py"):
        source_url = f"https://raw.githubusercontent.com/microsoft/LLMLingua/{LLMLINGUA}/{name}"
        path = ROOT / "vendor/llmlingua_reference" / (name + ".reference" if name.endswith(".py") else name)
        provenance["files"][str(path.relative_to(ROOT))] = download(source_url, path)
    token_url = f"https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/{TOKENIZER_REV}/tokenizer.json"
    path = ROOT / "data/tokenizer/tokenizer.json"
    print("Preparing official DeepSeek tokenizer (no model weights)", flush=True)
    provenance["files"][str(path.relative_to(ROOT))] = download(token_url, path)
    license_url = f"https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/{TOKENIZER_REV}/LICENSE"
    path = ROOT / "vendor/deepseek_tokenizer/LICENSE"
    provenance["files"][str(path.relative_to(ROOT))] = download(license_url, path)
    atomic_json(ROOT / "manifests/resources.json", provenance)
    build_manifests()


def build_manifests():
    canonical = load_position(1)
    reference = {qid: document_set(row) for qid, row in canonical.items()}
    for position in POSITIONS[1:]:
        rows = load_position(position)
        if set(rows) != set(canonical):
            raise ValueError(f"Question sets differ at position {position}")
        for qid, row in rows.items():
            if document_set(row) != reference[qid] or row["question"] != canonical[qid]["question"]:
                raise ValueError(f"Question or documents differ across positions: {qid}")
        del rows
    ids = sorted(canonical)
    random.Random(42).shuffle(ids)
    if len(ids) < 500:
        raise ValueError("Fewer than 500 aligned questions")
    for split, size in (("smoke", 20), ("pilot", 100), ("main", 500)):
        atomic_json(ROOT / f"manifests/{split}.json", {
            "split": split, "seed": 42, "source_commit": UPSTREAM,
            "population": len(ids), "question_ids": ids[:size],
            "selection": "sorted stable IDs, random.Random(42).shuffle, nested prefixes",
        })
    atomic_json(ROOT / "reports/data-validation.json", {
        "questions_per_position": len(ids), "positions": list(POSITIONS),
        "documents_per_question": 20, "all_question_sets_match": True,
        "all_document_sets_match": True, "gold_positions_verified": True,
        "duplicate_ids": 0, "seed": 42, "source_commit": UPSTREAM,
    })
    print(f"Validated {len(ids)} questions x 5 positions; nested 20/100/500 manifests ready.", flush=True)


def visible_sample(row):
    # Explicit allowlist is the boundary: upstream retrieval scores, answers and gold flags stay out.
    return {"question": row["question"], "documents": [
        {"id": document_id(d), "title": d["title"], "text": d["text"]}
        for d in row["ctxs"]]}


def iter_samples(config):
    manifest = read_json(ROOT / f"manifests/{config['split']}.json")
    if manifest["source_commit"] != config["upstream"]["lost_in_the_middle"]:
        raise ValueError("Manifest and configured upstream revisions differ")
    for position in config["positions"]:
        rows = load_position(position)
        for qid in manifest["question_ids"]:
            yield qid, position, rows[qid]
