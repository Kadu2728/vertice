"""Aplicação FastAPI — monta rotas, CORS, headers de segurança e
tratamento de erro RFC 7807 (ver docs/00-discovery.md §6/§12)."""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.v1.routes import bonds, explanations, health, simulations

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title="VÉRTICE API",
        description="Simulação e explicação de marcação a mercado de títulos públicos brasileiros.",
        version="0.1.0",
    )

    allowed_origins = [
        origin.strip()
        for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(bonds.router, prefix="/api/v1")
    app.include_router(simulations.router, prefix="/api/v1")
    app.include_router(explanations.router, prefix="/api/v1")

    return app


app = create_app()
