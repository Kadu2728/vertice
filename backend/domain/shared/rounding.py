"""Truncamento e arredondamento explícitos por convenção ANBIMA (ver
docs/domain/precificacao-anbima.md, tabela "T" = truncado, "A" = arredondado
por variável). Deliberadamente separado de Money/Rate: esses objetos de
valor não conhecem a convenção de nenhum domínio específico — quem decide
"esta variável trunca em 6, aquela arredonda em 5" é o código de pricing/
indexers que sabe qual variável está calculando, não o objeto de valor."""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal


def truncate(value: Decimal, places: int) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_DOWN)


def round_half_up(value: Decimal, places: int) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)
