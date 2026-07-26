from matematica.divisao import PeriodoDecimal, periodo_da_divisao


def test_divisao_exata_nao_tem_periodo():
    assert periodo_da_divisao(12, 5) is None
    assert periodo_da_divisao(1, 4) is None


def test_dizima_simples_sem_ante_periodo():
    assert periodo_da_divisao(1, 3) == PeriodoDecimal(ante_periodo="", periodo="3", posicao_inicio=0)


def test_dizima_com_ante_periodo():
    # 1/6 = 0,1666... -- o "1" não repete, só o "6" a partir da 2ª casa.
    resultado = periodo_da_divisao(1, 6)
    assert resultado.ante_periodo == "1"
    assert resultado.periodo == "6"
    assert resultado.posicao_inicio == 1


def test_dizima_com_periodo_longo():
    # 1/7 = 0,142857142857... -- período de 6 dígitos, sem ante-período.
    resultado = periodo_da_divisao(1, 7)
    assert resultado.ante_periodo == ""
    assert resultado.periodo == "142857"
    assert resultado.posicao_inicio == 0


def test_busca_e_limitada_pelo_denominador():
    # 1/17 tem período de 16 dígitos -- o máximo possível para denominador
    # 17 (só há 16 restos não nulos: 1..16). Prova que a busca não desiste
    # antes do limite que o próprio denominador garante.
    resultado = periodo_da_divisao(1, 17)
    assert resultado.periodo == "0588235294117647"
    assert len(resultado.periodo) == 16


def test_divisao_por_zero_nao_e_definida():
    import pytest

    with pytest.raises(ValueError):
        periodo_da_divisao(1, 0)
