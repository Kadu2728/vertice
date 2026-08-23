"""Porta entre a orquestração e o provedor de LLM. Protocol, não classe
concreta — a mesma razão de sempre neste projeto (ver BondCatalogPort):
testar a camada de explicação inteira sem chamar uma API externa de
verdade, e trocar de provedor sem tocar em `application/explanations`."""

from __future__ import annotations

from typing import Any, Protocol


class LlmClient(Protocol):
    def generate_json(
        self, system_prompt: str, user_prompt: str, response_schema: dict[str, Any] | None = None
    ) -> str:
        """Devolve uma string JSON (esperado: bater com ExplanationOutput).
        `response_schema`, se dado, é repassado ao provedor para restringir
        o formato de saída (nem todo provedor suporta — quem implementa
        decide se ignora). Levanta exceção em qualquer falha — quem chama
        decide o fallback, este cliente não silencia erro."""
        ...


class UnavailableLlmClient:
    """Usado quando não há provedor configurado (ex.: GEMINI_API_KEY
    ausente). Levanta dentro de `generate_json`, não na construção — o
    orquestrador (application/explanations/service.py) já trata qualquer
    exceção daqui caindo no fallback estático. A IA fica indisponível sem
    a API nunca falhar por causa disso (docs/00-discovery.md §25)."""

    def generate_json(
        self, system_prompt: str, user_prompt: str, response_schema: dict[str, Any] | None = None
    ) -> str:
        raise RuntimeError("nenhum provedor de LLM configurado (GEMINI_API_KEY ausente)")


class FakeLlmClient:
    """Usado em teste — devolve uma resposta fixa ou levanta um erro
    configurado, sem rede."""

    def __init__(self, response: str | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def generate_json(
        self, system_prompt: str, user_prompt: str, response_schema: dict[str, Any] | None = None
    ) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        if self._error is not None:
            raise self._error
        if self._response is None:
            raise RuntimeError("FakeLlmClient sem resposta configurada")
        return self._response
