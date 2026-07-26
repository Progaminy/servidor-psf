import unicodedata

from lingua_portuguesa import MotorPortugues, OpcoesAnalise
from lingua_portuguesa.tokenizacao import Tokenizador


def test_nfc_e_nfd_produzem_a_mesma_analise_lexical_com_offsets_originais():
    motor = MotorPortugues(opcoes=OpcoesAnalise.leve())
    nfc = "A ação não é fácil."
    nfd = unicodedata.normalize("NFD", nfc)

    analise_nfc = motor.analisar(nfc)
    analise_nfd = motor.analisar(nfd)

    assert tuple(token.normalizado for token in analise_nfd.tokens) == tuple(
        token.normalizado for token in analise_nfc.tokens
    )
    assert tuple(item.principal.classe for item in analise_nfd.morfologia) == tuple(
        item.principal.classe for item in analise_nfc.morfologia
    )
    assert all(
        nfd[token.inicio : token.fim] == token.texto
        for token in analise_nfd.tokens
    )


def test_tokenizador_nao_apaga_underscore_e_separa_numero_malformado():
    tokens = Tokenizador().tokenizar("foo_bar 1,2,3")
    assert tuple(token.texto for token in tokens) == (
        "foo",
        "_",
        "bar",
        "1,2",
        ",",
        "3",
    )


def test_apostrofo_tipografico_permanece_na_palavra():
    tokens = Tokenizador().tokenizar("d’água")
    assert len(tokens) == 1
    assert tokens[0].texto == "d’água"


def test_casefold_expansivo_nao_fabrica_digrafo_com_offset_invalido():
    analise = MotorPortugues(opcoes=OpcoesAnalise.leve()).analisar("ß.")
    digrafos = tuple(
        item for item in analise.fluxo.combinacoes if item.tipo == "digrafo"
    )
    assert digrafos == ()
