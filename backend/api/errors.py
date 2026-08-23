"""Erros da API seguem RFC 7807 (application/problem+json): corpo
estruturado com type/title/status/detail, não string solta — o frontend
distingue tipo de erro pelo campo `type`, sem parsear mensagem
(docs/00-discovery.md §6). `type` usa esquema `urn:vertice:error:...` em
vez de uma URL https — o produto não tem um domínio de documentação de
erros publicado, e um `type` que aponta pra uma URL inexistente seria pior
que um URN que não promete resolução."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from application.simulations.service import (
    BondSeriesNotFound,
    BondTypeNotYetSupported,
    QuoteNotFound,
)


def _problem(status: int, type_: str, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={"type": type_, "title": title, "status": status, "detail": detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BondSeriesNotFound)
    async def _bond_series_not_found(request: Request, exc: BondSeriesNotFound) -> JSONResponse:
        return _problem(
            404, "urn:vertice:error:bond-series-not-found", "Série de título não encontrada", str(exc)
        )

    @app.exception_handler(QuoteNotFound)
    async def _quote_not_found(request: Request, exc: QuoteNotFound) -> JSONResponse:
        return _problem(
            404, "urn:vertice:error:quote-not-found", "Cotação não encontrada para a data informada", str(exc)
        )

    @app.exception_handler(BondTypeNotYetSupported)
    async def _bond_type_not_supported(
        request: Request, exc: BondTypeNotYetSupported
    ) -> JSONResponse:
        return _problem(
            501,
            "urn:vertice:error:bond-type-not-yet-supported",
            "Tipo de título ainda não suportado",
            str(exc),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(
            422, "urn:vertice:error:validation-error", "Entrada inválida", str(exc.errors())
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = str(exc.detail)
        return _problem(exc.status_code, "urn:vertice:error:http-error", detail, detail)
