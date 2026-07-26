import pytest

from nucleo.irracionalidade_raiz_de_dois import (
    ProvaIrracionalidadeRaizDeDois,
    prova_raiz_de_dois_irracional,
    quadrado_e_par_see_base_e_par,
)


def test_lema_paridade_do_quadrado_bate_para_pares_e_impares():
    assert quadrado_e_par_see_base_e_par(0) is True
    assert quadrado_e_par_see_base_e_par(2) is True
    assert quadrado_e_par_see_base_e_par(4) is True
    assert quadrado_e_par_see_base_e_par(1) is True
    assert quadrado_e_par_see_base_e_par(3) is True
    assert quadrado_e_par_see_base_e_par(7) is True


def test_prova_certifica_irracionalidade():
    prova = prova_raiz_de_dois_irracional()
    assert isinstance(prova, ProvaIrracionalidadeRaizDeDois)
    assert prova.lema_paridade_verificado is True
    assert prova.valida is True
    assert "não é racional" in prova.conclusao


def test_prova_aceita_alcance_customizado():
    prova = prova_raiz_de_dois_irracional(alcance_verificacao=8)
    assert prova.alcance_verificacao == 8
    assert prova.valida is True


def test_lema_exige_natural():
    with pytest.raises(ValueError):
        quadrado_e_par_see_base_e_par(-1)
