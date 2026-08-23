"""Implementação real (Gemini) do LlmClient. Escrita contra a API real do
SDK `google-genai` (verificada nesta sessão: `genai.Client(...).models.
generate_content(...)`, `types.GenerateContentConfig` com `system_instruction`
e `response_json_schema`), mas **nunca chamada com uma API key de verdade**
— sem GEMINI_API_KEY configurada neste ambiente. Estruturalmente correta,
não validada ao vivo. Mesma ressalva transparente já usada para o
repositório Postgres antes de haver banco (ver docs/domain/fase-4-status.md).

Modelo default `gemini-1.5-flash`: se a API rejeitar por descontinuação,
o erro sobe como exceção normal (generate_json não engole erro) — quem
orquestra cai no fallback estático, e o modelo precisa ser atualizado
depois de confirmar com o Google qual Flash está disponível."""

from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_json(
        self, system_prompt: str, user_prompt: str, response_schema: dict[str, Any] | None = None
    ) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_json_schema=response_schema,
        )
        response = self._client.models.generate_content(
            model=self._model, contents=user_prompt, config=config
        )
        if not response.text:
            raise RuntimeError("Gemini devolveu resposta vazia")
        return response.text
