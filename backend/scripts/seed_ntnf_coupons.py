"""Preenche coupon_rate_annual e bond_coupon_dates para as séries NTN-F já
ingeridas. Gap conhecido da Fase 3: o CSV do Tesouro Transparente não traz
a taxa de cupom nem o calendário de pagamento — só preço e taxa de retorno.
10% a.a. é a convenção de mercado padrão para todas as séries de NTN-F em
oferta (mesma usada nos golden tests, ver docs/domain/golden-tests-status.md).

Uso único de desenvolvimento — não é um job de ingestão recorrente.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select

from domain.bonds.bond_type import BondType
from infra.database.base import get_session_factory
from infra.database.models import BondCouponDateModel, BondSeriesModel

NTNF_COUPON_RATE = "0.10"


def semiannual_dates_back_to(maturity: date, floor_year: int) -> list[date]:
    dates = []
    cursor = maturity
    while cursor.year > floor_year:
        dates.append(cursor)
        month = cursor.month - 6
        year = cursor.year
        if month <= 0:
            month += 12
            year -= 1
        cursor = cursor.replace(year=year, month=month)
    return dates


def run() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        series_list = session.scalars(
            select(BondSeriesModel).where(BondSeriesModel.bond_type == BondType.NTN_F.value)
        ).all()
        for series in series_list:
            series.coupon_rate_annual = NTNF_COUPON_RATE
            for payment_date in semiannual_dates_back_to(series.maturity_date, 2020):
                exists = session.scalar(
                    select(BondCouponDateModel).where(
                        BondCouponDateModel.bond_series_id == series.id,
                        BondCouponDateModel.payment_date == payment_date,
                    )
                )
                if not exists:
                    session.add(
                        BondCouponDateModel(bond_series_id=series.id, payment_date=payment_date)
                    )
        session.commit()
        print(f"NTN-F atualizadas: {len(series_list)}")


if __name__ == "__main__":
    run()
