from datetime import date

from domain.calendars.anbima import AnbimaCalendar, _easter, national_holidays


def test_easter_matches_known_reference_dates():
    # datas de referência publicamente conhecidas, usadas só para validar
    # o algoritmo de Páscoa em si.
    assert _easter(2024) == date(2024, 3, 31)
    assert _easter(2025) == date(2025, 4, 20)
    assert _easter(2026) == date(2026, 4, 5)


def test_national_holidays_include_fixed_and_movable_dates_2026():
    holidays = national_holidays(2026)
    assert date(2026, 1, 1) in holidays  # confraternização universal
    assert date(2026, 12, 25) in holidays  # natal
    assert date(2026, 2, 16) in holidays  # carnaval (segunda)
    assert date(2026, 4, 3) in holidays  # sexta-feira santa
    assert date(2026, 6, 4) in holidays  # corpus christi
    assert date(2026, 11, 20) in holidays  # consciência negra (a partir de 2024)


def test_consciencia_negra_not_holiday_before_2024():
    assert date(2023, 11, 20) not in national_holidays(2023)


def test_is_business_day_excludes_weekend_and_holiday():
    calendar = AnbimaCalendar()
    assert calendar.is_business_day(date(2026, 1, 2)) is True  # sexta, sem feriado
    assert calendar.is_business_day(date(2026, 1, 3)) is False  # sábado
    assert calendar.is_business_day(date(2026, 1, 1)) is False  # feriado


def test_business_days_between_counts_only_business_days():
    calendar = AnbimaCalendar()
    # sexta 02/01 -> terça 06/01: pula sábado e domingo, conta segunda e terça
    assert calendar.business_days_between(date(2026, 1, 2), date(2026, 1, 6)) == 2


def test_business_days_between_is_negative_when_end_before_start():
    calendar = AnbimaCalendar()
    assert calendar.business_days_between(date(2026, 1, 6), date(2026, 1, 2)) == -2


def test_extra_holidays_are_unioned_with_computed_calendar():
    injected = frozenset({date(2026, 1, 2)})
    calendar = AnbimaCalendar(extra_holidays=injected)
    assert calendar.is_business_day(date(2026, 1, 2)) is False
