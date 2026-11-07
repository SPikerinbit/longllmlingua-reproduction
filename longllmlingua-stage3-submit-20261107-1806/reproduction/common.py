from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSITIONS = (1, 5, 10, 15, 20)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load_config(path=None):
    config = read_json(path or ROOT / "configs/stage1.json")
    if config["base_url"] != "https://api.deepseek.com":
        raise ValueError("This stage-one adapter only sends credentials to https://api.deepseek.com")
    if config["thinking"] != {"type": "disabled"}:
        raise ValueError("Stage one requires non-thinking mode for the agreed token budget")
    if config["split"] not in ("smoke", "pilot", "main"):
        raise ValueError("Unknown split")
    if not config["positions"] or not set(config["positions"]).issubset(POSITIONS):
        raise ValueError("Invalid positions")
    if len(set(config["positions"])) != len(config["positions"]):
        raise ValueError("Duplicate positions")
    methods = config["methods"]
    if not methods or len(set(methods)) != len(methods) or not set(methods).issubset(
            {"original", "bm25_2x", "bm25_4x"}):
        raise ValueError("Invalid stage-one methods")
    for field in ("max_tokens", "max_attempts", "max_requests_per_run", "max_context_tokens"):
        if not isinstance(config[field], int) or config[field] <= 0:
            raise ValueError(f"{field} must be a positive integer")
    return config


def implementation_hash():
    files = sorted((ROOT / "reproduction").glob("*.py"))
    files += sorted((ROOT / "vendor").rglob("*.py"))
    files += sorted((ROOT / "vendor").rglob("*.prompt"))
    return digest({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in files})


def configuration_hash(config):
    return digest({"config": config, "implementation": implementation_hash()})


def append_jsonl(path, row):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if i != len(lines) - 1:
                raise
            # An interrupted trailing write must not invalidate durable earlier rows.
            print("Warning: ignoring interrupted final JSONL line; results can be rebuilt from cache.")
    return rows
