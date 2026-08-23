"""`/health` (processo vivo) e `/ready` (dependências respondendo) —
separados de propósito, para o orquestrador de deploy diferenciar
"reiniciar" de "não rotear tráfego ainda" (docs/00-discovery.md §15)."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> JSONResponse:
    from infra.database.base import get_engine
    from sqlalchemy import text

    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(status_code=503, content={"status": "not ready", "detail": str(exc)})
    return JSONResponse(status_code=200, content={"status": "ready"})
