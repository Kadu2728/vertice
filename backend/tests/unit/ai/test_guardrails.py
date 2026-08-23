from infra.ai.guardrails import is_recommendation_seeking


def test_blocks_devo_vender():
    assert is_recommendation_seeking("Devo vender meu título agora?")


def test_blocks_o_que_voce_faria():
    assert is_recommendation_seeking("O que você faria no meu lugar?")


def test_blocks_vale_a_pena():
    assert is_recommendation_seeking("Vale a pena esperar mais um ano?")


def test_blocks_qual_titulo_comprar():
    assert is_recommendation_seeking("Qual título devo comprar para 2030?")


def test_allows_factual_question():
    assert not is_recommendation_seeking("Por que o preço do meu título caiu?")


def test_allows_scenario_question():
    assert not is_recommendation_seeking("Quanto eu receberia se vendesse hoje?")


def test_case_insensitive():
    assert is_recommendation_seeking("DEVO VENDER AGORA?")
