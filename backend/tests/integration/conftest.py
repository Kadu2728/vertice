"""Fixtures de integração — exigem Postgres real via TEST_DATABASE_URL.
Sem essa variável, os testes marcados `integration` são pulados (não
falham).

Deliberadamente uma variável SEPARADA de DATABASE_URL: esta fixture roda
`Base.metadata.drop_all(engine)` no teardown de cada teste. Já apontou sem
querer pro banco de desenvolvimento (mesmo valor de DATABASE_URL) e apagou
dado real ingerido do Tesouro Transparente — ver docs/domain/fase-4-status.md.
TEST_DATABASE_URL existir e ser diferente de DATABASE_URL é a garantia de
que isso não se repete."""

import os

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

requires_database = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL não configurada — sem Postgres de teste disponível neste ambiente",
)


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from infra.database.models import Base

    if TEST_DATABASE_URL == os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "TEST_DATABASE_URL igual a DATABASE_URL — recusando rodar para não apagar dado de dev"
        )

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
