"""Saída estruturada da IA — só campos de texto. Nenhum campo numérico:
torna alucinação numérica estruturalmente impossível de virar "verdade"
sem passar pelo validador (docs/00-discovery.md §20)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExplanationOutput(BaseModel):
    title: str = Field(description="Título curto, sentence case, sem emoji")
    body: str = Field(description="Explicação em linguagem natural, 2 a 4 frases")
    warnings: list[str] = Field(default_factory=list, description="Avisos relevantes, se houver")
