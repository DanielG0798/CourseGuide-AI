"""Thin abstraction over the LLM API so the model can be swapped without changing agent code."""
from __future__ import annotations

import os
from typing import Any

from openai import AsyncOpenAI, OpenAI

from .config import model_client_config


class ModelClient:
    """A simple client for the configured BYOM/NRP/OpenAI-compatible endpoint."""

    def __init__(self, config: dict | None = None):
        self.cfg = config or model_client_config()
        self.provider = self.cfg.get("provider", "byom")
        self._sync_client: OpenAI | None = None
        self._async_client: AsyncOpenAI | None = None

    def _client_kwargs(self) -> dict[str, Any]:
        kwargs = {
            "api_key": self.cfg.get("api_key") or os.getenv("BYOM_API_KEY", "missing-key"),
            "base_url": self.cfg.get("base_url"),
        }
        return kwargs

    def _sync(self) -> OpenAI:
        if self._sync_client is None:
            self._sync_client = OpenAI(**self._client_kwargs())
        return self._sync_client

    def _async(self) -> AsyncOpenAI:
        if self._async_client is None:
            self._async_client = AsyncOpenAI(**self._client_kwargs())
        return self._async_client

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.3, **kwargs) -> str:
        """Send a chat completion request and return the assistant message content."""
        response = self._sync().chat.completions.create(
            model=self.cfg["model"],
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def achat(
        self, messages: list[dict[str, str]], temperature: float = 0.3, **kwargs
    ) -> str:
        """Async version of chat."""
        response = await self._async().chat.completions.create(
            model=self.cfg["model"],
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""
