from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class ExplanationRequest(BaseModel):
    simulation_id: UUID
    question: str | None = Field(
        default=None,
        max_length=280,
        description="Pergunta livre sobre a simulação; omitido gera uma explicação geral do resultado",
    )


class ExplanationResponse(BaseModel):
    title: str
    body: str
    warnings: list[str]
