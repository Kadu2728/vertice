"""Job diário de ingestão do Tesouro Direto — chamado pelo GitHub Actions
(ADR-002: sem fila, batch simples). Idempotente: reexecutar no mesmo dia
não duplica nem diverge, porque o upsert é por chave natural.

Uso:
    python -m scripts.ingest.ingest_tesouro_direto                  # só o dia mais recente
    python -m scripts.ingest.ingest_tesouro_direto --backfill       # histórico completo (uso único)
    python -m scripts.ingest.ingest_tesouro_direto --date 2025-01-02 # uma Data Base específica
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime

from infra.database.base import get_session_factory
from infra.database.repositories import upsert_bond_market_quote, upsert_bond_series
from infra.external_data.tesouro_direto import (
    fetch_csv,
    filter_by_quote_date,
    latest_quote_date,
    parse_csv,
    validate_daily_batch,
)

logger = logging.getLogger("vertice.ingest.tesouro_direto")


def run(backfill: bool = False, target_date: date | None = None) -> int:
    logger.info("baixando CSV do Tesouro Transparente")
    content = fetch_csv()
    all_rows = parse_csv(content)
    logger.info("linhas parseadas no arquivo completo: %d", len(all_rows))

    if backfill:
        rows = all_rows
    else:
        effective_date = target_date or latest_quote_date(all_rows)
        rows = filter_by_quote_date(all_rows, effective_date)
        validate_daily_batch(rows)
        logger.info("Data Base do dia: %s — %d cotações", effective_date, len(rows))

    session_factory = get_session_factory()
    with session_factory() as session:
        for row in rows:
            series = upsert_bond_series(session, row)
            upsert_bond_market_quote(session, series.id, row)
        session.commit()

    logger.info("ingestão concluída: %d cotações processadas", len(rows))
    return len(rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--backfill", action="store_true")
    parser.add_argument("--date", type=str, default=None, help="Data Base específica (YYYY-MM-DD)")
    args = parser.parse_args()
    parsed_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else None
    try:
        run(backfill=args.backfill, target_date=parsed_date)
        if not args.backfill and parsed_date is None:
            # TEMPORÁRIO — backfill pontual da Data Base fixa que o frontend
            # usa como PURCHASE_DATE (simulator.tsx), ausente no banco de
            # produção recém-criado. Remover depois de confirmar em prod.
            run(backfill=False, target_date=date(2025, 1, 2))
    except Exception:
        logger.exception("falha na ingestão do Tesouro Direto")
        sys.exit(1)
