"""DTOs de resposta para o catálogo de títulos — nunca expõem o model
SQLAlchemy diretamente (docs/00-discovery.md §6)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BondSeriesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bond_type: str
    maturity_date: date
    coupon_rate_annual: Decimal | None


class BondQuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quote_date: date
    reference_rate_annual: Decimal
