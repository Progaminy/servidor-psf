import pytest

from nucleo.irracionalidade_raiz_prima import (
    ProvaIrracionalidadeRaizPrima,
    eh_primo_pequeno,
    prova_raiz_prima_irracional,
    primo_divide_quadrado_implica_primo_divide_base,
)


def test_eh_primo_pequeno_reconhece_primos_e_compostos():
    assert eh_primo_pequeno(2) is True
    assert eh_primo_pequeno(3) is True
    assert eh_primo_pequeno(11) is True
    assert eh_primo_pequeno(13) is True
    assert eh_primo_pequeno(1) is False
    assert eh_primo_pequeno(4) is False
    assert eh_primo_pequeno(9) is False


def test_lema_generalizado_bate_para_varios_primos():
    for p in (2, 3, 5, 7):
        for n in range(1, 15):
            assert primo_divide_quadrado_implica_primo_divide_base(p, n) is True


@pytest.mark.parametrize("p", [2, 3, 5, 7, 11, 13])
def test_prova_certifica_irracionalidade_para_varios_primos(p):
    prova = prova_raiz_prima_irracional(p)
    assert isinstance(prova, ProvaIrracionalidadeRaizPrima)
    assert prova.primo == p
    assert prova.lema_verificado is True
    assert prova.valida is True
    assert f"√{p}" in prova.conclusao


def test_prova_recusa_primo_falso():
    with pytest.raises(ValueError):
        prova_raiz_prima_irracional(4)
    with pytest.raises(ValueError):
        prova_raiz_prima_irracional(9)
