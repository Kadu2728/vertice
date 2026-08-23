from __future__ import annotations

from decimal import Decimal, getcontext


def decimal_power(base: Decimal, exponent: Decimal) -> Decimal:
    """base**exponent para expoente fracionário, via identidade
    exp(exponent * ln(base)) — Decimal não implementa potência fracionária
    nativamente. Precisão de contexto ampliada temporariamente para não
    introduzir erro relevante frente à tolerância de R$ 0,01 dos golden
    tests (ver ADR-005)."""
    ctx = getcontext()
    prev_prec = ctx.prec
    ctx.prec = prev_prec + 10
    try:
        result = (exponent * base.ln()).exp()
    finally:
        ctx.prec = prev_prec
    return +result
