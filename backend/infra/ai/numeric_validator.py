"""Extrai valores monetários do texto gerado pela IA e confere contra os
números do payload que o motor determinístico calculou. Qualquer valor
monetário no texto que não bata com nenhum número do payload é tratado
como alucinação — a resposta inteira é descartada por quem orquestra
(ADR-003: a IA nunca tem autoridade sobre número)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

_CURRENCY_RE = re.compile(r"R\$\s*-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?")


def _parse_brl(raw: str) -> Decimal:
    cleaned = raw.replace("R$", "").strip().replace(".", "").replace(",", ".")
    return Decimal(cleaned)


def extract_currency_values(text: str) -> list[Decimal]:
    values = []
    for match in _CURRENCY_RE.finditer(text):
        try:
            values.append(_parse_brl(match.group()))
        except InvalidOperation:
            continue
    return values


def all_values_match_reference(
    found: list[Decimal], reference: list[Decimal], tolerance: Decimal = Decimal("0.02")
) -> bool:
    """Todo valor em `found` precisa estar a `tolerance` de algum valor em
    `reference` — não o contrário (o texto pode mencionar só alguns dos
    números do payload, não precisa citar todos)."""
    return all(any(abs(v - r) <= tolerance for r in reference) for v in found)
