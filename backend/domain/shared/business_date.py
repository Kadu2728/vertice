from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


class BusinessDayCalendar(Protocol):
    """Contrato que qualquer calendário (ANBIMA, ou um de teste) precisa
    cumprir. BusinessDate depende disso, não de uma implementação concreta —
    é o que permite trocar/injetar calendário em teste sem tocar no motor."""

    def is_business_day(self, day: date) -> bool: ...

    def business_days_between(self, start: date, end: date) -> int:
        """Quantidade de dias úteis entre start (exclusive) e end (inclusive),
        convenção usada no du/252 de mercado brasileiro."""
        ...


@dataclass(frozen=True, slots=True)
class BusinessDate:
    """Data amarrada a um calendário — força toda aritmética de prazo do
    domínio a passar por dias úteis explícitos, nunca por `date2 - date1`."""

    value: date
    calendar: BusinessDayCalendar

    def __post_init__(self) -> None:
        if not self.calendar.is_business_day(self.value):
            # não é erro em si (data de compra pode cair num fim de semana
            # na simulação do usuário), mas quem chama precisa saber disso
            # para decidir se rola para o próximo dia útil ou rejeita.
            pass

    def business_days_until(self, other: "BusinessDate") -> int:
        if self.calendar is not other.calendar:
            raise ValueError("business_days_until exige o mesmo calendário nas duas pontas")
        return self.calendar.business_days_between(self.value, other.value)
