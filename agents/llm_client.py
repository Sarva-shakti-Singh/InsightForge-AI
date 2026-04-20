"""Unified LLM wrapper. Supports OpenAI, OpenAI-compatible , or mock mode."""
from __future__ import annotations
import os
from typing import List, Dict, Optional


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LOVABLE_API_KEY")
        self.base_url = os.getenv("AI_BASE_URL")  
        self.model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self._client = None
        if self.api_key:
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except Exception:
                self._client = None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def chat(self, system: str, user: str, temperature: float = 0.4,
             max_tokens: int = 700) -> Optional[str]:
        if not self._client:
            return None
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[LLM error] {e}"
