"""Injeção de dependência da API. Em produção, `get_bond_catalog` abre uma
sessão real e devolve o repositório Postgres; em teste, a aplicação
sobrescreve estas funções via `app.dependency_overrides` com fakes em
memória (tests/api/conftest.py) — nenhum teste de API depende de Postgres
estar disponível."""

from __future__ import annotations

import os
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session

from application.simulations.ports import BondCatalogPort
from application.simulations.store import InMemorySimulationStore, SimulationStore
from infra.ai.gemini_client import GeminiClient
from infra.ai.llm_client import LlmClient, UnavailableLlmClient
from infra.ai.rag import LexicalRetriever, load_corpus
from infra.database.base import get_session_factory
from infra.database.bond_catalog_repository import SqlAlchemyBondCatalog

_RAG_CORPUS_DIR = Path(__file__).resolve().parents[2] / "docs" / "domain" / "rag-corpus"


def get_db_session() -> Iterator[Session]:
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_bond_catalog(session: Session = Depends(get_db_session)) -> BondCatalogPort:
    return SqlAlchemyBondCatalog(session)


@lru_cache(maxsize=1)
def _default_simulation_store() -> InMemorySimulationStore:
    # Default de desenvolvimento — ver docstring de InMemorySimulationStore
    # sobre por que isso é aceitável para um dado descartável sem login.
    return InMemorySimulationStore()


def get_simulation_store() -> SimulationStore:
    return _default_simulation_store()


@lru_cache(maxsize=1)
def _default_llm_client() -> LlmClient:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return UnavailableLlmClient()
    return GeminiClient(api_key=api_key)


def get_llm_client() -> LlmClient:
    return _default_llm_client()


@lru_cache(maxsize=1)
def _default_retriever() -> LexicalRetriever:
    return LexicalRetriever(load_corpus(_RAG_CORPUS_DIR))


def get_retriever() -> LexicalRetriever:
    return _default_retriever()
