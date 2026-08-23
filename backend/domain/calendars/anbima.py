"""Calendário de dias úteis ANBIMA/B3.

Os feriados nacionais são computados algoritmicamente (data fixa + Páscoa
via algoritmo de Meeus/Jones/Butcher para os móveis). Isso cobre o
calendário nacional que fecha o mercado, mas B3/ANBIMA publicam um arquivo
oficial de calendário que é a fonte de verdade final — a ingestão (Fase 3)
deve carregar esse arquivo e passá-lo como `extra_holidays` para
`AnbimaCalendar`, que faz união com o calendário computado em vez de
substituí-lo. Diferença entre os dois é sinal de bug em um dos dois lados,
não algo a ignorar silenciosamente.

Feriado de Consciência Negra (20/11) é feriado nacional a partir de 2024
(Lei 14.759/2023) — tratado condicionalmente por ano de vigência.
"""

from __future__ import annotations

from datetime import date, timedelta


def _easter(year: int) -> date:
    """Domingo de Páscoa (algoritmo de Meeus/Jones/Butcher, calendário
    gregoriano)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def national_holidays(year: int) -> frozenset[date]:
    """Feriados nacionais que fecham o mercado (calendário ANBIMA), para um
    ano civil. Ver módulo docstring sobre a necessidade de validar contra o
    arquivo oficial na ingestão."""
    easter = _easter(year)
    holidays = {
        date(year, 1, 1),  # confraternização universal
        easter - timedelta(days=48),  # carnaval (segunda)
        easter - timedelta(days=47),  # carnaval (terça)
        easter - timedelta(days=2),  # sexta-feira santa
        easter + timedelta(days=60),  # corpus christi
        date(year, 4, 21),  # tiradentes
        date(year, 5, 1),  # dia do trabalho
        date(year, 9, 7),  # independência
        date(year, 10, 12),  # nossa senhora aparecida
        date(year, 11, 2),  # finados
        date(year, 11, 15),  # proclamação da república
        date(year, 12, 25),  # natal
    }
    if year >= 2024:
        holidays.add(date(year, 11, 20))  # consciência negra — Lei 14.759/2023
    return frozenset(holidays)


class AnbimaCalendar:
    """Implementa o Protocol BusinessDayCalendar (domain/shared/business_date.py)."""

    def __init__(self, extra_holidays: frozenset[date] = frozenset()) -> None:
        self._extra_holidays = extra_holidays
        self._year_cache: dict[int, frozenset[date]] = {}

    def _holidays_for_year(self, year: int) -> frozenset[date]:
        if year not in self._year_cache:
            self._year_cache[year] = national_holidays(year) | self._extra_holidays
        return self._year_cache[year]

    def is_business_day(self, day: date) -> bool:
        if day.weekday() >= 5:  # sábado, domingo
            return False
        return day not in self._holidays_for_year(day.year)

    def business_days_between(self, start: date, end: date) -> int:
        """Dias úteis entre start (exclusive) e end (inclusive). Se end < start,
        retorna a contagem negativa (permite calcular prazo já decorrido)."""
        if end == start:
            return 0
        step = 1 if end > start else -1
        count = 0
        cursor = start
        while cursor != end:
            cursor += timedelta(days=step)
            if self.is_business_day(cursor):
                count += step
        return count

    def next_business_day(self, day: date) -> date:
        cursor = day
        while not self.is_business_day(cursor):
            cursor += timedelta(days=1)
        return cursor
