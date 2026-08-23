"""Fábrica de engine/sessão. Deliberadamente lazy: importar este módulo não
deve exigir DATABASE_URL configurada (testes de parsing/domínio não tocam
banco) — só falha quando algo de fato tenta conectar.

Carrega backend/.env se existir (dotenv) — variável de ambiente real, se já
setada, sempre vence (override=False); .env é só o caminho pra dev local
sem precisar exportar a variável manualmente a cada sessão de terminal."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada")
    return create_engine(database_url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
