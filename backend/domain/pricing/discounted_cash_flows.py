from decimal import Decimal

from domain.bonds.cash_flow import CashFlow
from domain.shared.rate import Rate
from domain.shared.rounding import round_half_up, truncate


def present_value_fraction(
    cash_flows: list[CashFlow], tir: Rate, flow_rounding_places: int
) -> Decimal:
    """Soma dos fluxos trazidos a valor presente pela TIR, em fração do
    valor de face. `flow_rounding_places` é "Fluxo de Pagamentos Descontados"
    na tabela ANBIMA: A-9 para NTN-F, A-10 para NTN-B (docs/domain/precificacao-anbima.md).
    O fator de desconto em si segue "Exponencial de Dias: T-14", aplicado
    antes da divisão — nunca depois."""
    total = Decimal(0)
    for cf in cash_flows:
        factor = truncate(tir.discount_factor(cf.business_days_to_payment), 14)
        present_value = round_half_up(cf.face_value_fraction / factor, flow_rounding_places)
        total += present_value
    return total


def cotacao_zero_coupon(tir: Rate, business_days: int) -> Decimal:
    """Cotação (base 100) de um título sem cupom (NTN-B Principal, LFT) —
    caso particular de present_value_fraction com um único fluxo, mas
    calculado direto porque não há lista de CashFlow nem arredondamento
    intermediário de fluxo a aplicar (só existe um)."""
    factor = truncate(tir.discount_factor(business_days), 14)
    return truncate(Decimal(100) / factor, 4)  # Cotação: T-4
