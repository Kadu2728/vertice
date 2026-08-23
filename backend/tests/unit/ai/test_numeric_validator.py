from decimal import Decimal

from infra.ai.numeric_validator import all_values_match_reference, extract_currency_values


def test_extracts_single_value():
    assert extract_currency_values("O valor líquido é R$ 1.252,85 hoje.") == [Decimal("1252.85")]


def test_extracts_multiple_values():
    text = "Você investiu R$ 1.000,00 e hoje tem R$ 1.252,85."
    assert extract_currency_values(text) == [Decimal("1000.00"), Decimal("1252.85")]


def test_extracts_negative_value():
    assert extract_currency_values("O IR foi de R$ -54,54.") == [Decimal("-54.54")]


def test_no_currency_returns_empty():
    assert extract_currency_values("Seu título vence em 2029.") == []


def test_matches_within_tolerance():
    found = [Decimal("1252.85")]
    reference = [Decimal("1252.86")]
    assert all_values_match_reference(found, reference, tolerance=Decimal("0.02"))


def test_rejects_value_outside_tolerance():
    found = [Decimal("1300.00")]
    reference = [Decimal("1252.85")]
    assert not all_values_match_reference(found, reference)


def test_rejects_hallucinated_extra_number():
    # texto menciona um valor que não existe em lugar nenhum do payload
    found = [Decimal("1252.85"), Decimal("9999.99")]
    reference = [Decimal("1252.85"), Decimal("1000.00")]
    assert not all_values_match_reference(found, reference)


def test_empty_found_always_matches():
    assert all_values_match_reference([], [Decimal("1252.85")])
