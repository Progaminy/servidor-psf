import pytest

from matematica.pitagoras import hipotenusa


def test_terno_pitagorico_classico_e_exato():
    r = hipotenusa(3, 4, casas=4)
    assert r.exata is True
    assert r.soma_quadrados == 25
    assert r.raiz.parte_inteira == 5


def test_catetos_2_e_3_correspondem_ao_exemplo_original():
    # Exemplo que motivou a Etapa 1089: catetos 2 e 3, h²=13, h≈3,6055 --
    # exatamente o alvo que a Etapa 1085 documentava como travado.
    r = hipotenusa(2, 3, casas=4)
    assert r.exata is False
    assert r.soma_quadrados == 13
    assert r.decimal == "3,6055"


def test_passos_contam_a_historia_completa():
    r = hipotenusa(2, 3, casas=4)
    assert len(r.passos) == 3
    assert "h² = a² + b²" in r.passos[0]
    assert "4 + 9 = 13" in r.passos[1]
    assert "3,6055" in r.passos[2]


def test_catetos_devem_ser_positivos():
    with pytest.raises(ValueError):
        hipotenusa(0, 3)
    with pytest.raises(ValueError):
        hipotenusa(3, -1)


def test_sem_pedir_conferencia_o_resultado_nunca_depende_do_cao_de_caca():
    # Regra 17: o campo só existe quando pedido; por omissão fica None e
    # nenhum outro campo é afetado pela presença/ausência do cão de caça.
    r = hipotenusa(2, 3, casas=4)
    assert r.conferencia_cao_de_caca is None
    assert r.decimal == "3,6055"


def test_conferencia_com_calculadora_nunca_muda_o_resultado_psf():
    # Regra 17: o cão de caça (projeto externo, `cao_de_caca/`, fora do
    # git) é só um conferidor opcional -- presente ou ausente, `decimal`
    # e `exata` continuam vindo exclusivamente da construção PSF
    # (Etapa 1089). `conferencia_cao_de_caca` é None quando o cão de
    # caça está indisponível nesta máquina, ou True/False quando ele
    # roda e a comparação é feita -- nunca um terceiro valor.
    sem_conferencia = hipotenusa(2, 3, casas=4)
    com_conferencia = hipotenusa(2, 3, casas=4, conferir_com_calculadora=True)
    assert com_conferencia.decimal == sem_conferencia.decimal == "3,6055"
    assert com_conferencia.exata == sem_conferencia.exata
    assert com_conferencia.conferencia_cao_de_caca in (None, True, False)


def test_conferencia_bate_com_o_cao_de_caca_quando_disponivel():
    from matematica.pitagoras import _CAMINHO_CAO_DE_CACA

    if not _CAMINHO_CAO_DE_CACA.is_dir():
        pytest.skip("cao_de_caca/PSF-Calculadora não está presente nesta máquina")
    r = hipotenusa(2, 3, casas=4, conferir_com_calculadora=True)
    assert r.conferencia_cao_de_caca is True
