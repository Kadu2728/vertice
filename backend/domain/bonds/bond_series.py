from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.bonds.bond_type import ZERO_COUPON_TYPES, BondType


@dataclass(frozen=True, slots=True)
class BondSeries:
    """Uma série específica de título (ex.: NTN-B 15/08/2035). Dados de
    catálogo virão da ingestão (Fase 3) — aqui só o suficiente para o motor
    de pricing operar e ser testado isoladamente."""

    id: str
    bond_type: BondType
    maturity_date: date
    coupon_rate_annual: Decimal | None = None  # taxa do edital: 0.10 (NTN-F), 0.06 (NTN-B)
    coupon_dates: tuple[date, ...] = ()  # datas de pagamento semestral, deve incluir maturity_date

    def __post_init__(self) -> None:
        has_coupon = self.bond_type not in ZERO_COUPON_TYPES
        if has_coupon:
            if self.coupon_rate_annual is None:
                raise ValueError(f"{self.bond_type.value} exige coupon_rate_annual")
            if not self.coupon_dates or self.coupon_dates[-1] != self.maturity_date:
                raise ValueError(
                    f"{self.bond_type.value} exige coupon_dates terminando em maturity_date"
                )
        elif self.coupon_rate_annual is not None or self.coupon_dates:
            raise ValueError(f"{self.bond_type.value} não tem cupom — não informe coupon_*")
