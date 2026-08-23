from datetime import date
from decimal import Decimal

from domain.bonds.bond_series import BondSeries
from domain.bonds.bond_type import BondType
from domain.calendars.anbima import AnbimaCalendar
from domain.pricing.ntnf import price_ntnf
from domain.shared.rate import Rate, RateBasis


def test_price_ntnf_at_par_when_tir_equals_coupon_rate():
    """Identidade: se a TIR de desconto é igual à taxa de cupom do edital e
    os fluxos caem exatamente em múltiplos de 252 du, o PU deve ser
    (dentro da margem de ruído dos truncamentos/arredondamentos oficiais)
    igual ao valor de face — é a definição de precificação "ao par"."""
    calendar = AnbimaCalendar()
    settlement = date(2026, 1, 2)  # sexta, sem feriado

    def add_business_days(start: date, n: int) -> date:
        d = start
        added = 0
        while added < n:
            d = date.fromordinal(d.toordinal() + 1)
            if calendar.is_business_day(d):
                added += 1
        return d

    mid = add_business_days(settlement, 126)
    maturity = add_business_days(settlement, 252)

    bond = BondSeries(
        id="NTNF-PAR",
        bond_type=BondType.NTN_F,
        maturity_date=maturity,
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=(mid, maturity),
    )
    tir = Rate(Decimal("0.10"), RateBasis.NOMINAL)

    pu = price_ntnf(bond, settlement, calendar, tir)

    assert abs(pu.amount - Decimal("1000")) < Decimal("0.05")


def test_price_ntnf_below_par_when_tir_exceeds_coupon():
    calendar = AnbimaCalendar()
    settlement = date(2026, 1, 2)
    maturity = date(2027, 1, 4)
    bond = BondSeries(
        id="NTNF-ABOVE-TIR",
        bond_type=BondType.NTN_F,
        maturity_date=maturity,
        coupon_rate_annual=Decimal("0.10"),
        coupon_dates=(maturity,),
    )
    tir = Rate(Decimal("0.15"), RateBasis.NOMINAL)
    pu = price_ntnf(bond, settlement, calendar, tir)
    assert pu.amount < Decimal("1000")
