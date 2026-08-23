"""Dados e fakes compartilhados entre conftest.py e os módulos de teste.

Deliberadamente FORA de conftest.py: pytest importa conftest.py através do
próprio mecanismo de plugin (não um `import` comum), o que pode criar uma
segunda instância do módulo quando um arquivo de teste faz
`from tests.http_api.conftest import X` — e então uma constante gerada
dinamicamente (como um UUID) diverge entre as duas instâncias. Um módulo
comum, importado normalmente pelos dois lados, não tem esse problema."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from application.simulations.ports import BondSeriesRecord, MarketQuoteRecord
from domain.bonds.bond_type import BondType

LTN_ID = uuid4()
PURCHASE_DATE = date(2026, 1, 2)
REFERENCE_DATE = date(2027, 1, 4)
MATURITY = date(2028, 1, 1)


@dataclass
class FakeCatalog:
    series: dict[UUID, BondSeriesRecord] = field(default_factory=dict)
    quotes: dict[tuple[UUID, date], MarketQuoteRecord] = field(default_factory=dict)

    def list_bond_series(self) -> list[BondSeriesRecord]:
        return list(self.series.values())

    def get_bond_series(self, bond_series_id: UUID) -> BondSeriesRecord | None:
        return self.series.get(bond_series_id)

    def get_quote(self, bond_series_id: UUID, quote_date: date) -> MarketQuoteRecord | None:
        return self.quotes.get((bond_series_id, quote_date))

    def list_quotes(self, bond_series_id: UUID, limit: int) -> list[MarketQuoteRecord]:
        matches = [q for (bid, _), q in self.quotes.items() if bid == bond_series_id]
        return sorted(matches, key=lambda q: q.quote_date, reverse=True)[:limit]

    def get_vna(self, bond_type: BondType, reference_date: date):
        return None


def build_fake_catalog() -> FakeCatalog:
    return FakeCatalog(
        series={
            LTN_ID: BondSeriesRecord(
                id=LTN_ID,
                bond_type=BondType.LTN,
                maturity_date=MATURITY,
                coupon_rate_annual=None,
                coupon_dates=(),
            )
        },
        quotes={
            (LTN_ID, PURCHASE_DATE): MarketQuoteRecord(PURCHASE_DATE, Decimal("0.10")),
            (LTN_ID, REFERENCE_DATE): MarketQuoteRecord(REFERENCE_DATE, Decimal("0.10")),
        },
    )
