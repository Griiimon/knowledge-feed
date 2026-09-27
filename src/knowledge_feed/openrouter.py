from __future__ import annotations
import json, os, time
from urllib import request, error


class OpenRouterError(RuntimeError): pass


class OpenRouterClient:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 30, retries: int = 3):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key: raise OpenRouterError("OPENROUTER_API_KEY is required")
        self.model, self.timeout, self.retries = model or os.getenv("OPENROUTER_MODEL", "openrouter/free"), timeout, retries
    def chat(self, prompt: str, max_tokens: int = 1600) -> str:
        payload = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}).encode()
        for attempt in range(self.retries + 1):
            req = request.Request(self.endpoint, payload, {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            try:
                with request.urlopen(req, timeout=self.timeout) as response: data = json.loads(response.read())
                content = data["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise ValueError("response did not include assistant message content")
                return content
            except (error.HTTPError, error.URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
                transient = not isinstance(exc, error.HTTPError) or exc.code == 429 or 500 <= exc.code < 600
                if not transient or attempt == self.retries: raise OpenRouterError(f"OpenRouter request failed after {attempt + 1} attempts: {exc}") from exc
                time.sleep(2 ** attempt)
        raise AssertionError("unreachable")
