import pytest

from nucleo.irracionalidade_raiz_composta import (
    ProvaIrracionalidadeRaizComposta,
    fator_multiplicidade_um,
    prova_raiz_n_irracional,
)


@pytest.mark.parametrize(
    "n,fator_esperado",
    [
        (6, 2),
        (10, 2),
        (12, 3),
        (14, 2),
        (15, 3),
        (18, 2),
        (20, 5),
        (21, 3),
        (24, 3),
    ],
)
def test_fator_multiplicidade_um_acha_o_fator_certo(n, fator_esperado):
    assert fator_multiplicidade_um(n) == fator_esperado


@pytest.mark.parametrize("n", [1, 4, 8, 9, 16])
def test_fator_multiplicidade_um_nao_existe_para_quadrados_e_potencias_puras(n):
    # 4=2², 9=3² (quadrados perfeitos); 8=2³, 16=2⁴ (nenhum primo com mult. 1).
    assert fator_multiplicidade_um(n) is None


@pytest.mark.parametrize("n", [6, 10, 12, 14, 15, 18, 20, 21, 24])
def test_prova_certifica_irracionalidade_para_compostos_cobertos(n):
    prova = prova_raiz_n_irracional(n)
    assert isinstance(prova, ProvaIrracionalidadeRaizComposta)
    assert prova.n == n
    assert prova.lema_verificado is True
    assert prova.valida is True
    assert f"√{n}" in prova.conclusao


@pytest.mark.parametrize("n", [1, 4, 8, 9, 16])
def test_prova_recusa_n_fora_do_alcance_deste_argumento(n):
    with pytest.raises(ValueError):
        prova_raiz_n_irracional(n)
