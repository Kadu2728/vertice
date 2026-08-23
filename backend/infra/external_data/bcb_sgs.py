"""Cliente para a API de Séries Temporais do Banco Central (SGS).

Fonte: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados

Códigos usados — verificados por chamada real à API nesta sessão
(2026-08-21), não por memória:
- 11: Taxa de juros - Selic, diária (% ao dia). Ex.: 0,051660 em 21/08/2026.
- 433: IPCA - variação mensal (%). Ex.: 0,07 em 07/2026.

O VNA da LFT precisa do fator diário acumulado da Selic (série 11); o VNA
da NTN-B precisa do IPCA — usamos a variação mensal (série 433) porque o
índice-número IBGE não tem série SGS direta e confiável identificada nesta
pesquisa: a razão IPCA_t/IPCA_0 da fórmula ANBIMA (docs/domain/precificacao-anbima.md)
é matematicamente idêntica ao produto acumulado dos fatores mensais
(1 + variação_i), então a variação mensal é suficiente — só a base
(IPCA_0) é arbitrária e cancela na razão."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

SELIC_DAILY_SERIES_CODE = 11
IPCA_MONTHLY_VARIATION_SERIES_CODE = 433

_FETCH_TIMEOUT_SECONDS = 30
_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/{n}?formato=json"


class UnexpectedSgsResponseShape(ValueError):
    """A resposta da API não tem o formato esperado ([{"data":..,"valor":..}])
    — falha ruidosa em vez de tentar adivinhar o formato novo."""


@dataclass(frozen=True, slots=True)
class IndexSeriesPointRow:
    indexer: str  # "SELIC" | "IPCA"
    unit_period: str  # "daily" | "monthly"
    reference_date: date
    value: Decimal  # percentual do período, ex.: Decimal("0.051660") = 0,05166%


def _parse_point(raw: dict[str, str], indexer: str, unit_period: str) -> IndexSeriesPointRow:
    try:
        reference_date = datetime.strptime(raw["data"], "%d/%m/%Y").date()
        value = Decimal(raw["valor"])
    except (KeyError, ValueError, ArithmeticError) as exc:
        raise UnexpectedSgsResponseShape(f"ponto inesperado na série SGS: {raw!r}") from exc
    return IndexSeriesPointRow(
        indexer=indexer, unit_period=unit_period, reference_date=reference_date, value=value
    )


def parse_series(raw_json: str, indexer: str, unit_period: str) -> list[IndexSeriesPointRow]:
    """Parsing puro — sem rede. `raw_json` é o corpo da resposta da API SGS."""
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise UnexpectedSgsResponseShape("resposta SGS não é JSON válido") from exc
    if not isinstance(payload, list):
        raise UnexpectedSgsResponseShape(f"esperava uma lista, recebeu {type(payload).__name__}")
    return [_parse_point(item, indexer, unit_period) for item in payload]


def fetch_series(series_code: int, last_n: int) -> str:
    """Único ponto que toca a rede. `last_n` limita o volume por chamada —
    evita puxar a série inteira quando só os últimos dias importam para a
    ingestão diária."""
    url = _BASE_URL.format(code=series_code, n=last_n)
    request = urllib.request.Request(url, headers={"User-Agent": "vertice-ingestion/0.1"})
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT_SECONDS) as response:
        content: str = response.read().decode("utf-8")
        return content
