from datetime import date
from decimal import Decimal

import pytest

from domain.bonds.bond_type import BondType
from infra.external_data.tesouro_direto import UnknownBondTypeLabel, parse_csv

# amostra real, capturada do CSV oficial baixado em 2026-08-21 (Data Base 20/08/2026)
SAMPLE_CSV = (
    "Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;"
    "PU Compra Manha;PU Venda Manha;PU Base Manha\n"
    "Tesouro Prefixado;01/01/2027;20/08/2026;13,48;13,60;955,84;954,99;954,99\n"
    "Tesouro Prefixado com Juros Semestrais;01/01/2027;20/08/2026;13,44;13,56;1002,62;1001,73;1001,73\n"
    "Tesouro IPCA+;15/05/2029;20/08/2026;8,05;8,17;3847,04;3834,59;3834,59\n"
    "Tesouro IPCA+ com Juros Semestrais;15/08/2030;20/08/2026;8,10;8,22;4434,39;4415,85;4415,85\n"
    "Tesouro Selic;01/03/2031;20/08/2026;0,07;0,08;19647,06;19627,98;19627,98\n"
    "Tesouro IGPM+ com Juros Semestrais;01/01/2031;17/02/2005;8,29;8,39;2536,42;2512,14;2511,00\n"
    "Tesouro Educa+;15/12/2030;20/08/2026;7,50;7,60;1000,00;995,00;995,00\n"
)


def test_parses_all_five_mvp_bond_types():
    rows = parse_csv(SAMPLE_CSV)
    bond_types = {row.bond_type for row in rows}
    assert bond_types == {
        BondType.LTN,
        BondType.NTN_F,
        BondType.NTN_B_PRINCIPAL,
        BondType.NTN_B,
        BondType.LFT,
    }


def test_skips_out_of_scope_labels():
    rows = parse_csv(SAMPLE_CSV)
    assert len(rows) == 5  # NTN-C e Educa+ da amostra ficam de fora


def test_converts_rate_from_percentage_to_fraction():
    rows = parse_csv(SAMPLE_CSV)
    ltn_row = next(r for r in rows if r.bond_type == BondType.LTN)
    assert ltn_row.buy_rate_annual == Decimal("0.1348")
    assert ltn_row.sell_rate_annual == Decimal("0.1360")


def test_parses_brazilian_decimal_and_date_format():
    rows = parse_csv(SAMPLE_CSV)
    ltn_row = next(r for r in rows if r.bond_type == BondType.LTN)
    assert ltn_row.buy_pu == Decimal("955.84")
    assert ltn_row.maturity_date == date(2027, 1, 1)
    assert ltn_row.quote_date == date(2026, 8, 20)


def test_unknown_label_raises_instead_of_skipping_silently():
    csv_with_new_label = SAMPLE_CSV.replace("Tesouro Educa+", "Tesouro Novo Produto Misterioso")
    with pytest.raises(UnknownBondTypeLabel):
        parse_csv(csv_with_new_label)
