"""Porta (Protocol) entre a aplicação e o catálogo de títulos/cotações.

Existe para inversão de dependência real, não decorativa: permite testar a
API inteira (roteamento, validação, contrato de erro) com um catálogo falso
em memória, sem precisar de um Postgres — que este ambiente de
desenvolvimento não tem (ver docs/domain/fase-3-status.md). A implementação
real (SQLAlchemy) mora em infra/database e satisfaz o mesmo Protocol."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from domain.bonds.bond_type import BondType
from domain.shared.money import Money


@dataclass(frozen=True, slots=True)
class BondSeriesRecord:
    id: UUID
    bond_type: BondType
    maturity_date: date
    coupon_rate_annual: Decimal | None
    coupon_dates: tuple[date, ...]


@dataclass(frozen=True, slots=True)
class MarketQuoteRecord:
    quote_date: date
    reference_rate_annual: Decimal


class BondCatalogPort(Protocol):
    def list_bond_series(self) -> list[BondSeriesRecord]: ...

    def get_bond_series(self, bond_series_id: UUID) -> BondSeriesRecord | None: ...

    def get_quote(self, bond_series_id: UUID, quote_date: date) -> MarketQuoteRecord | None: ...

    def list_quotes(self, bond_series_id: UUID, limit: int) -> list[MarketQuoteRecord]: ...

    def get_vna(self, bond_type: BondType, reference_date: date) -> Money | None: ...
