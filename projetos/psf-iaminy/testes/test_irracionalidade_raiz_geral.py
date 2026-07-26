import pytest

from nucleo.irracionalidade_raiz_geral import (
    ProvaIrracionalidadeRaizGeral,
    fator_com_valoracao_impar,
    prova_raiz_n_irracional_geral,
    valoracao_p_adica,
)


def test_valoracao_p_adica_conta_a_multiplicidade_certa():
    assert valoracao_p_adica(2, 8) == 3
    assert valoracao_p_adica(2, 16) == 4
    assert valoracao_p_adica(3, 12) == 1
    assert valoracao_p_adica(2, 12) == 2
    assert valoracao_p_adica(5, 7) == 0


def test_valoracao_p_adica_exige_base_prima():
    with pytest.raises(ValueError):
        valoracao_p_adica(4, 8)


@pytest.mark.parametrize(
    "n,fator_esperado,valoracao_esperada",
    [
        (2, 2, 1),
        (6, 2, 1),
        (8, 2, 3),
        (12, 3, 1),
        (18, 2, 1),
        (24, 2, 3),
        (27, 3, 3),
        (32, 2, 5),
        (50, 2, 1),
    ],
)
def test_fator_com_valoracao_impar_acerta_casos_que_a_etapa_anterior_recusava(
    n, fator_esperado, valoracao_esperada
):
    # 8, 16, 24, 32 são exatamente os casos que test_irracionalidade_raiz_composta
    # recusa (nenhum fator de multiplicidade 1) -- esta etapa cobre também eles.
    fator = fator_com_valoracao_impar(n)
    assert fator == fator_esperado
    assert valoracao_p_adica(fator, n) == valoracao_esperada


@pytest.mark.parametrize("n", [1, 4, 9, 16, 25, 36, 49])
def test_fator_com_valoracao_impar_nao_existe_para_quadrados_perfeitos(n):
    assert fator_com_valoracao_impar(n) is None


@pytest.mark.parametrize("n", [2, 3, 5, 6, 7, 8, 10, 12, 18, 20, 24, 27, 32, 50])
def test_prova_certifica_irracionalidade_caso_geral(n):
    prova = prova_raiz_n_irracional_geral(n)
    assert isinstance(prova, ProvaIrracionalidadeRaizGeral)
    assert prova.n == n
    assert prova.valida is True
    assert prova.valoracao_do_fator % 2 == 1
    assert f"√{n}" in prova.conclusao


@pytest.mark.parametrize("n", [1, 4, 9, 16, 25])
def test_prova_recusa_quadrados_perfeitos(n):
    with pytest.raises(ValueError):
        prova_raiz_n_irracional_geral(n)
