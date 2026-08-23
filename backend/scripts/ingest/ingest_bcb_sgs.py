"""Job diário de ingestão de indexadores (BCB/SGS) — Selic diária e IPCA
mensal. Mesmo padrão de ADR-002/§8 do discovery: batch simples, idempotente
por upsert em (indexer, reference_date).

Uso:
    python -m scripts.ingest.ingest_bcb_sgs
"""

from __future__ import annotations

import logging
import sys

from infra.database.base import get_session_factory
from infra.database.repositories import upsert_index_series_point
from infra.external_data.bcb_sgs import (
    IPCA_MONTHLY_VARIATION_SERIES_CODE,
    SELIC_DAILY_SERIES_CODE,
    fetch_series,
    parse_series,
)

logger = logging.getLogger("vertice.ingest.bcb_sgs")

# janela curta o bastante para uma execução diária, larga o bastante para
# cobrir um fim de semana prolongado ou uma falha de execução anterior
_SELIC_LOOKBACK_DAYS = 10
_IPCA_LOOKBACK_MONTHS = 3


def run() -> int:
    total = 0
    session_factory = get_session_factory()
    with session_factory() as session:
        logger.info("baixando série Selic diária (BCB/SGS %d)", SELIC_DAILY_SERIES_CODE)
        selic_raw = fetch_series(SELIC_DAILY_SERIES_CODE, _SELIC_LOOKBACK_DAYS)
        selic_rows = parse_series(selic_raw, indexer="SELIC", unit_period="daily")
        for row in selic_rows:
            upsert_index_series_point(session, row)
        total += len(selic_rows)

        logger.info("baixando série IPCA mensal (BCB/SGS %d)", IPCA_MONTHLY_VARIATION_SERIES_CODE)
        ipca_raw = fetch_series(IPCA_MONTHLY_VARIATION_SERIES_CODE, _IPCA_LOOKBACK_MONTHS)
        ipca_rows = parse_series(ipca_raw, indexer="IPCA", unit_period="monthly")
        for row in ipca_rows:
            upsert_index_series_point(session, row)
        total += len(ipca_rows)

        session.commit()

    logger.info("ingestão de indexadores concluída: %d pontos processados", total)
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        run()
    except Exception:
        logger.exception("falha na ingestão de indexadores BCB/SGS")
        sys.exit(1)
