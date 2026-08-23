"""DTOs de simulação. `SimulationResponse` nunca é construído a partir de
número calculado no frontend nem na camada de IA (Fase 6) — sempre a
partir de `application.simulations.SimulationResult`, que por sua vez só
existe depois de passar pelo motor determinístico (ADR-003)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationCreateRequest(BaseModel):
    bond_series_id: UUID
    purchase_date: date
    amount_invested: Decimal = Field(gt=0, description="Valor investido, em R$")
    reference_date: date | None = Field(
        default=None, description="Data de referência para marcação a mercado; padrão é hoje"
    )


class ScenarioCreateRequest(BaseModel):
    shock_bps: int = Field(
        ge=-200,
        le=200,
        multiple_of=50,
        description="Choque de taxa em bps, de -200 a +200 em passos de 50 (§18 da spec)",
    )


class TaxBreakdownResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gross_gain: Decimal
    iof_amount: Decimal
    ir_amount: Decimal
    net_gain: Decimal


class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bond_series_id: UUID
    bond_type: str
    purchase_date: date
    reference_date: date
    amount_invested: Decimal
    quantity: Decimal
    pu_purchase: Decimal
    pu_reference: Decimal
    gross_value_today: Decimal
    days_held: int
    taxes: TaxBreakdownResponse
    custody_fee_amount: Decimal
    net_value_today: Decimal
    calculation_engine_version: str
