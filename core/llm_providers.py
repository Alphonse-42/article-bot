"""
LLM Provider Abstraction Layer
===============================
Unified interface for multiple LLM backends:
  - Ollama (local, default)
  - OpenAI
  - Anthropic
  - Google Generative AI
"""

import os
import json
import time
from abc import ABC, abstractmethod

import requests
from loguru import logger


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, model: str, temperature: float = 0.3,
                 max_tokens: int = 8192, max_retries: int = 3,
                 retry_delay: int = 5):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @abstractmethod
    def _call(self, system_prompt: str, user_prompt: str) -> str:
        """Provider-specific API call. Must be implemented by subclasses."""
        ...

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a prompt to the LLM and return the response text.
        Includes automatic retry logic for transient failures.
        """
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"LLM call attempt {attempt}/{self.max_retries} "
                            f"[{self.__class__.__name__}:{self.model}]")
                result = self._call(system_prompt, user_prompt)
                logger.success(f"LLM call succeeded ({len(result)} chars)")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)

        raise RuntimeError(
            f"LLM call failed after {self.max_retries} attempts: {last_error}"
        )


# ── Ollama (Local) ───────────────────────────────────────────
class OllamaProvider(BaseLLMProvider):
    """Local LLM via Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip("/")

    def _call(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]


# ── OpenAI ───────────────────────────────────────────────────
class OpenAIProvider(BaseLLMProvider):
    """OpenAI API (GPT-4o, etc.)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("pip install openai")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=api_key)

    def _call(self, system_prompt: str, user_prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content


# ── Anthropic ────────────────────────────────────────────────
class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import anthropic
        except ImportError:
            raise ImportError("pip install anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call(self, system_prompt: str, user_prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.temperature,
        )
        return resp.content[0].text


# ── Google Generative AI ─────────────────────────────────────
class GoogleProvider(BaseLLMProvider):
    """Google Gemini API."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("pip install google-generativeai")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment")
        genai.configure(api_key=api_key)
        self.genai_model = genai.GenerativeModel(
            self.model,
            system_instruction=None,  # set per-call
        )

    def _call(self, system_prompt: str, user_prompt: str) -> str:
        import google.generativeai as genai
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )
        resp = model.generate_content(user_prompt)
        return resp.text


# ── Factory ──────────────────────────────────────────────────
_PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
}


def get_provider(config: dict) -> BaseLLMProvider:
    """
    Instantiate the correct LLM provider from a config dict.

    Expected keys in config["llm"]:
        provider, model, base_url (ollama only),
        temperature, max_tokens, max_retries, retry_delay_seconds
    """
    llm_cfg = config["llm"]
    provider_name = llm_cfg["provider"].lower()

    if provider_name not in _PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Supported: {list(_PROVIDERS.keys())}"
        )

    common_kwargs = {
        "model": llm_cfg["model"],
        "temperature": llm_cfg.get("temperature", 0.3),
        "max_tokens": llm_cfg.get("max_tokens", 8192),
        "max_retries": llm_cfg.get("max_retries", 3),
        "retry_delay": llm_cfg.get("retry_delay_seconds", 5),
    }

    if provider_name == "ollama":
        common_kwargs["base_url"] = llm_cfg.get(
            "base_url",
            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    cls = _PROVIDERS[provider_name]
    return cls(**common_kwargs)
