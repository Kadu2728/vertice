"""Persistência de simulações — Protocol + implementação em memória para
teste/dev. A implementação real (Postgres, tabela `simulations`) mora em
infra/database e nunca rodou contra um banco de verdade neste ambiente
(sem Postgres disponível — ver docs/domain/fase-3-status.md)."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from application.simulations.service import SimulationResult


class SimulationStore(Protocol):
    def save(self, simulation_id: UUID, result: SimulationResult) -> None: ...

    def get(self, simulation_id: UUID) -> SimulationResult | None: ...


class InMemorySimulationStore:
    """Usada como default de desenvolvimento e em testes de API — não
    sobrevive a um restart do processo, o que é aceitável para uma
    simulação sem login (dado descartável) até a Fase 3 conectar
    infra/database de verdade nesta porta."""

    def __init__(self) -> None:
        self._data: dict[UUID, SimulationResult] = {}

    def save(self, simulation_id: UUID, result: SimulationResult) -> None:
        self._data[simulation_id] = result

    def get(self, simulation_id: UUID) -> SimulationResult | None:
        return self._data.get(simulation_id)
