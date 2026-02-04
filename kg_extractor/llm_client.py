import os
from typing import List

from openai import OpenAI


class LlmClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        resolved_key = api_key or os.getenv("NVIDIA_API_KEY")
        resolved_base_url = base_url or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        resolved_model = model or os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
        if not resolved_key:
            raise ValueError("Missing NVIDIA_API_KEY environment variable or api_key argument.")

        self.client = OpenAI(base_url=resolved_base_url, api_key=resolved_key)
        self.model = resolved_model

    def chat(self, messages: List[dict], temperature: float = 0.2, top_p: float = 0.7, max_tokens: int = 1200) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=False,
        )
        return completion.choices[0].message.content
