"""Cliente para "Taxas dos Títulos Ofertados pelo Tesouro Direto" —
Tesouro Transparente. Download e parsing separados deliberadamente: parsing
é puro (testável sem rede), download é a única parte que toca a internet.

Fonte: https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
Verificado por download real em 2026-08-21 (14,4 MB, ~175 mil linhas,
atualizado diariamente segundo o portal)."""

from __future__ import annotations

import csv
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

from domain.bonds.bond_type import BondType

TESOURO_DIRETO_CSV_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"
)

_FETCH_TIMEOUT_SECONDS = 30

_TYPE_LABEL_TO_BOND_TYPE: dict[str, BondType] = {
    "Tesouro Prefixado": BondType.LTN,
    "Tesouro Prefixado com Juros Semestrais": BondType.NTN_F,
    "Tesouro IPCA+": BondType.NTN_B_PRINCIPAL,
    "Tesouro IPCA+ com Juros Semestrais": BondType.NTN_B,
    "Tesouro Selic": BondType.LFT,
}

# Fora do escopo do MVP (§39 do prompt do projeto) — ignorados
# explicitamente por nome, não por fallback silencioso.
_OUT_OF_SCOPE_LABELS = frozenset(
    {
        "Tesouro IGPM+ com Juros Semestrais",  # NTN-C
        "Tesouro Educa+",
        "Tesouro Renda+ Aposentadoria Extra",
    }
)


class UnknownBondTypeLabel(ValueError):
    """O CSV trouxe um rótulo de título não mapeado e não listado como fora
    de escopo — sinal de que o Tesouro mudou o arquivo; a ingestão deve
    falhar de forma ruidosa aqui, não pular a linha silenciosamente
    (docs/00-discovery.md §8: "validação de schema explícita, falha ruidosa
    em vez de upsert de dado inválido")."""


@dataclass(frozen=True, slots=True)
class TesouroDiretoQuoteRow:
    bond_type: BondType
    maturity_date: date
    quote_date: date
    buy_rate_annual: Decimal
    sell_rate_annual: Decimal
    buy_pu: Decimal
    sell_pu: Decimal
    base_pu: Decimal


def _parse_brazilian_decimal(raw: str) -> Decimal:
    try:
        return Decimal(raw.strip().replace(".", "").replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"valor decimal inválido no CSV do Tesouro Direto: {raw!r}") from exc


def _parse_brazilian_date(raw: str) -> date:
    return datetime.strptime(raw.strip(), "%d/%m/%Y").date()


def parse_csv(content: str) -> list[TesouroDiretoQuoteRow]:
    """Parsing puro — sem rede, sem banco. Levanta UnknownBondTypeLabel se
    encontrar um tipo de título não reconhecido."""
    reader = csv.DictReader(StringIO(content), delimiter=";")
    rows: list[TesouroDiretoQuoteRow] = []
    for raw_row in reader:
        label = raw_row["Tipo Titulo"].strip()
        if label in _OUT_OF_SCOPE_LABELS:
            continue
        bond_type = _TYPE_LABEL_TO_BOND_TYPE.get(label)
        if bond_type is None:
            raise UnknownBondTypeLabel(label)
        rows.append(
            TesouroDiretoQuoteRow(
                bond_type=bond_type,
                maturity_date=_parse_brazilian_date(raw_row["Data Vencimento"]),
                quote_date=_parse_brazilian_date(raw_row["Data Base"]),
                buy_rate_annual=_parse_brazilian_decimal(raw_row["Taxa Compra Manha"]) / 100,
                sell_rate_annual=_parse_brazilian_decimal(raw_row["Taxa Venda Manha"]) / 100,
                buy_pu=_parse_brazilian_decimal(raw_row["PU Compra Manha"]),
                sell_pu=_parse_brazilian_decimal(raw_row["PU Venda Manha"]),
                base_pu=_parse_brazilian_decimal(raw_row["PU Base Manha"]),
            )
        )
    return rows


class IngestionValidationError(ValueError):
    """Falha de validação pós-parsing (contagem, cobertura de tipos) — sinal
    de que a fonte mudou de formato ou o arquivo veio truncado. Deve
    interromper a ingestão, não seguir com dado suspeito."""


def latest_quote_date(rows: list[TesouroDiretoQuoteRow]) -> date:
    if not rows:
        raise IngestionValidationError("nenhuma linha para determinar a última Data Base")
    return max(row.quote_date for row in rows)


def filter_by_quote_date(
    rows: list[TesouroDiretoQuoteRow], quote_date: date
) -> list[TesouroDiretoQuoteRow]:
    """A ingestão diária processa só a Data Base mais recente — o arquivo
    traz o histórico completo (~20 anos), reprocessar tudo todo dia seria
    custoso sem necessidade, já que Data Base passada não muda retroativamente."""
    return [row for row in rows if row.quote_date == quote_date]


# Menor que qualquer volume diário observado no arquivo real (dezenas de
# séries ativas por dia) — limiar propositalmente conservador para pegar
# arquivo truncado/corrompido sem gerar falso positivo em dia normal.
MIN_EXPECTED_ROWS_PER_DAY = 20


def validate_daily_batch(rows: list[TesouroDiretoQuoteRow]) -> None:
    """Validação pós-ingestão (docs/00-discovery.md §8): contagem mínima e
    cobertura dos 5 tipos do MVP. Levanta em vez de logar e seguir —
    upsert de lote suspeito é pior do que não ingerir."""
    if len(rows) < MIN_EXPECTED_ROWS_PER_DAY:
        raise IngestionValidationError(
            f"apenas {len(rows)} cotações no lote diário — abaixo do mínimo esperado "
            f"({MIN_EXPECTED_ROWS_PER_DAY}); investigar antes de repetir a ingestão"
        )
    covered_types = {row.bond_type for row in rows}
    missing = set(BondType) - covered_types
    if missing:
        raise IngestionValidationError(
            f"tipos de título ausentes no lote diário: {sorted(t.value for t in missing)}"
        )


def fetch_csv() -> str:
    """Único ponto que toca a rede. Timeout curto e host fixo (proteção
    SSRF básica — ver docs/00-discovery.md §12)."""
    request = urllib.request.Request(
        TESOURO_DIRETO_CSV_URL, headers={"User-Agent": "vertice-ingestion/0.1"}
    )
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT_SECONDS) as response:
        content: str = response.read().decode("utf-8")
        return content
