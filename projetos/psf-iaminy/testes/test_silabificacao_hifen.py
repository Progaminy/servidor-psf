# -*- coding: utf-8 -*-
"""Testes para o módulo de Divisão Silábica e Hifenização do PSF-IAminy."""
from lingua_portuguesa.silabificacao_hifen import (
    decidir_hifen_prefixo,
    dividir_silabas,
    eh_consoante,
    eh_vogal,
)


def test_eh_vogal_e_consoante():
    assert eh_vogal("a")
    assert eh_vogal("é")
    assert eh_vogal("U")
    assert not eh_vogal("b")

    assert eh_consoante("b")
    assert eh_consoante("z")
    assert not eh_consoante("a")


def test_dividir_silabas_simples():
    assert dividir_silabas("casa") == ("ca", "sa")
    assert dividir_silabas("brasil") == ("bra", "sil")
    assert dividir_silabas("janela") == ("ja", "ne", "la")


def test_dividir_silabas_digrafos():
    assert dividir_silabas("cachorro") == ("ca", "chor", "ro")
    assert dividir_silabas("pássaro") == ("pás", "sa", "ro")
    assert dividir_silabas("telha") == ("te", "lha")
    assert dividir_silabas("ninho") == ("ni", "nho")


def test_dividir_silabas_hiatos_e_ditongos():
    assert dividir_silabas("caixa") == ("cai", "xa")
    assert dividir_silabas("saúde") == ("sa", "ú", "de")
    assert dividir_silabas("baú") == ("ba", "ú")
    assert dividir_silabas("poeta") == ("po", "e", "ta")


def test_decidir_hifen_prefixo_base_com_h():
    res = decidir_hifen_prefixo("anti", "higiênico")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "anti-higiênico"

    res = decidir_hifen_prefixo("super", "homem")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "super-homem"


def test_decidir_hifen_prefixo_vogais_iguais():
    res = decidir_hifen_prefixo("micro", "onda")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "micro-onda"

    res = decidir_hifen_prefixo("anti", "inflamatório")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "anti-inflamatório"


def test_decidir_hifen_prefixo_vogais_diferentes():
    res = decidir_hifen_prefixo("auto", "escola")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "autoescola"

    res = decidir_hifen_prefixo("semi", "analfabeto")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "semianalfabeto"


def test_decidir_hifen_prefixo_dobra_r_s():
    res = decidir_hifen_prefixo("mini", "saia")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "minissaia"

    res = decidir_hifen_prefixo("auto", "resposta")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "autorresposta"


def test_decidir_hifen_prefixo_consoantes_iguais():
    res = decidir_hifen_prefixo("inter", "relação")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "inter-relação"

    res = decidir_hifen_prefixo("super", "resistente")
    assert res["usa_hifen"] is True
    assert res["resultado"] == "super-resistente"


def test_decidir_hifen_prefixo_consoante_vogal_ou_diferente():
    res = decidir_hifen_prefixo("super", "interessante")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "superinteressante"

    res = decidir_hifen_prefixo("sub", "categoria")
    assert res["usa_hifen"] is False
    assert res["resultado"] == "subcategoria"
