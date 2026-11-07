from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

from .common import ROOT, atomic_json, digest, read_json


class APIError(RuntimeError):
    def __init__(self, message, attempts=0, fatal=False, response_details=None):
        super().__init__(message)
        self.attempts = attempts
        self.fatal = fatal
        self.response_details = response_details or {}


def request_payload(config, prompt):
    return {"model": config["model"], "messages": [{"role": "user", "content": prompt}],
            "temperature": config["temperature"], "max_tokens": config["max_tokens"],
            "thinking": config["thinking"], "stream": False}


def cache_key(config, payload):
    # Credential-independent so rotating a key cannot contaminate reproducibility metadata.
    return digest({"endpoint": config["base_url"], "payload": payload,
                   "expected_model_version": config["expected_model_version"]})


def get_key(config):
    load_dotenv(ROOT / ".env", override=False)
    key = os.environ.get(config["api_key_env"], "").strip()
    if not key or key in ("YOUR_API_KEY", "sk-xxx"):
        raise APIError("Missing DEEPSEEK_API_KEY. Fill .env before running API requests.", fatal=True)
    return key


class DeepSeekClient:
    def __init__(self, config, key, http_client=None):
        self.config = config
        self.key = key
        self.http = http_client or httpx.Client(timeout=config["timeout_seconds"], follow_redirects=False)

    def close(self):
        self.http.close()

    def complete(self, payload):
        started = time.perf_counter()
        attempts = self.config["max_attempts"]
        for attempt in range(1, attempts + 1):
            error = "unknown"
            try:
                response = self.http.post(self.config["base_url"].rstrip("/") + "/chat/completions",
                                          headers={"Authorization": f"Bearer {self.key}"}, json=payload)
                if response.status_code != 200:
                    code = response.status_code
                    retryable = code == 429 or code >= 500
                    # Do not persist error bodies, response headers, or request credentials.
                    if not retryable:
                        raise APIError(f"DeepSeek HTTP {code}", attempt, fatal=code in (401, 402, 403))
                    error = f"DeepSeek HTTP {code}"
                else:
                    body = response.json()
                    choice = body["choices"][0]
                    answer = choice["message"]["content"]
                    details = {"usage": body.get("usage", {}), "response_model": body.get("model"),
                               "response_id": body.get("id"), "system_fingerprint": body.get("system_fingerprint"),
                               "finish_reason": choice.get("finish_reason"),
                               "answer_partial": answer if isinstance(answer, str) else None,
                               "api_seconds": time.perf_counter() - started}
                    if not isinstance(answer, str) or not answer.strip():
                        raise APIError("DeepSeek returned no final answer", attempt, response_details=details)
                    if choice.get("finish_reason") != "stop":
                        raise APIError("Incomplete response (finish_reason != stop); increase max_tokens if needed",
                                       attempt, response_details=details)
                    return {"answer": answer, "usage": body.get("usage", {}),
                            "response_model": body.get("model"), "response_id": body.get("id"),
                            "system_fingerprint": body.get("system_fingerprint"),
                            "finish_reason": choice.get("finish_reason"),
                            "api_seconds": time.perf_counter() - started, "attempts": attempt,
                            "created_at": datetime.now(timezone.utc).isoformat()}
            except (httpx.TimeoutException, httpx.NetworkError):
                error = "DeepSeek network timeout or connection failure"
            except (ValueError, KeyError, IndexError, TypeError):
                raise APIError("Malformed DeepSeek response", attempt) from None
            if attempt < attempts:
                time.sleep(self.config["retry_delay_seconds"] * 2 ** (attempt - 1))
        raise APIError(error, attempts)


def cached_completion(config, payload, client, provenance, cache_dir=None):
    key = cache_key(config, payload)
    path = (cache_dir or ROOT / "cache/api") / f"{key}.json"
    if path.exists():
        saved = read_json(path)
        if saved.get("cache_key") != key or saved.get("payload") != payload:
            raise ValueError("Cache integrity mismatch")
        return saved, True
    if client is None:
        raise APIError("API client required for a cache miss")
    result = client.complete(payload)
    saved = {"cache_key": key, "payload": payload, "endpoint": config["base_url"],
             "provenance": provenance, "result": result}
    # Cache durable success before appending a slot result, so interruption can be resumed safely.
    atomic_json(path, saved)
    return saved, False
