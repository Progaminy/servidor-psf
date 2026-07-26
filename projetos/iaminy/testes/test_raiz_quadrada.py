import decimal

import pytest

from matematica.raiz_quadrada import raiz_quadrada_por_digitos


def test_quadrado_perfeito_e_exato():
    r = raiz_quadrada_por_digitos(169, casas=4)
    assert r.exato is True
    assert r.parte_inteira == 13
    assert r.decimal == "13,0000"
    assert r.resto_final == 0


def test_quadrado_perfeito_grande():
    r = raiz_quadrada_por_digitos(1000000, casas=2)
    assert r.exato is True
    assert r.parte_inteira == 1000


def test_zero_e_um_sao_casos_de_fronteira():
    assert raiz_quadrada_por_digitos(0, casas=3).decimal == "0,000"
    assert raiz_quadrada_por_digitos(1, casas=3).decimal == "1,000"


def test_alvo_documentado_como_falho_no_motor_antigo_agora_resolve():
    # `nucleo/reais.py` (Etapa 1085) documenta 13 como alvo que estoura o
    # limite de desempenho do Newton sobre numerais de Church. Este é
    # exatamente o caso do exemplo da hipotenusa (catetos 2 e 3, h²=13).
    r = raiz_quadrada_por_digitos(13, casas=4)
    assert r.exato is False
    assert r.decimal == "3,6055"


@pytest.mark.parametrize("alvo,casas", [
    (2, 10),
    (7, 20),
    (999999999999, 15),
    (12345678901234567890, 25),
])
def test_bate_com_decimal_truncado_para_comparacao_externa(alvo, casas):
    # `decimal` aqui só COMPARA o resultado já construído pelo PSF -- não
    # produz nenhum dígito da resposta (Regra 3: dependência externa só
    # como comparação/validação, nunca como fundamento).
    decimal.getcontext().prec = casas + 20
    r = raiz_quadrada_por_digitos(alvo, casas=casas)
    referencia = decimal.Decimal(alvo).sqrt()
    quantizador = decimal.Decimal("1." + "0" * casas)
    truncado = referencia.quantize(quantizador, rounding=decimal.ROUND_DOWN)
    assert r.decimal.replace(",", ".") == format(truncado, f".{casas}f")


def test_casas_zero_devolve_so_parte_inteira():
    r = raiz_quadrada_por_digitos(170, casas=0)
    assert r.decimal == "13"
    assert r.exato is False


def test_negativo_nao_e_natural():
    with pytest.raises(ValueError):
        raiz_quadrada_por_digitos(-1)


def test_casas_negativas_e_invalido():
    with pytest.raises(ValueError):
        raiz_quadrada_por_digitos(4, casas=-1)


def test_passos_documentam_cada_casa_gerada():
    r = raiz_quadrada_por_digitos(13, casas=2)
    assert len(r.passos) == 1 + 2  # 1 par inteiro (13) + 2 casas decimais
    assert "casa inteira" in r.passos[0]
    assert "casa decimal 1" in r.passos[1]
    assert "casa decimal 2" in r.passos[2]
