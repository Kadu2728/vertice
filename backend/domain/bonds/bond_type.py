from enum import Enum


class BondType(str, Enum):
    """Os 5 tipos suportados — ver docs/00-discovery.md §6."""

    LTN = "LTN"
    NTN_F = "NTN-F"
    NTN_B = "NTN-B"
    NTN_B_PRINCIPAL = "NTN-B Principal"
    LFT = "LFT"


# Títulos sem cupom: um único fluxo de principal no vencimento.
ZERO_COUPON_TYPES = frozenset({BondType.LTN, BondType.LFT, BondType.NTN_B_PRINCIPAL})
