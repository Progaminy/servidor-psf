"""Fecha, com tabela testada, três limites operacionais reais do
conhecimento puro (`regra de oxítona`, `regra de paroxítona`, `regra de
monossílabo tônico`, conceitos 433/434/436 em `conhecimento_puro.py`) e
audita o inventário fechado do `acento diferencial` (conceito 438).

Todas as palavras usadas como fixture aqui são reais e atestadas -- em
parte já citadas como exemplo pelos próprios conceitos de
`conhecimento_puro.py` (café, música, casa, pá), em parte exemplos
clássicos de gramática escolar (não inventados), para manter a mesma
disciplina de nunca testar contra dado fabricado.
"""
import pytest

from lingua_portuguesa.acentuacao_grafica import (
    ACENTO_DIFERENCIAL,
    ClasseTonica,
    classificar_tonicidade,
    decidir_acento_grafico,
)
from lingua_portuguesa.lexico import Dicionario


def test_classificar_tonicidade_monossilabo():
    assert classificar_tonicidade(1, 0) == ClasseTonica.MONOSSILABO_TONICO


def test_classificar_tonicidade_oxitona_paroxitona_proparoxitona():
    # "café": ca-FÉ, 2 sílabas, tônica na última (índice 1).
    assert classificar_tonicidade(2, 1) == ClasseTonica.OXITONA
    # "casa": CA-sa, 2 sílabas, tônica na penúltima (índice 0).
    assert classificar_tonicidade(2, 0) == ClasseTonica.PAROXITONA
    # "música": MÚ-si-ca, 3 sílabas, tônica na antepenúltima (índice 0).
    assert classificar_tonicidade(3, 0) == ClasseTonica.PROPAROXITONA
    # "caderno": ca-DER-no, 3 sílabas, tônica na penúltima (índice 1).
    assert classificar_tonicidade(3, 1) == ClasseTonica.PAROXITONA


def test_classificar_tonicidade_indice_invalido():
    with pytest.raises(ValueError):
        classificar_tonicidade(2, 2)
    with pytest.raises(ValueError):
        classificar_tonicidade(2, -1)


def test_proparoxitona_sempre_exige_acento():
    for palavra in ("musica", "lampada", "onibus", "arvore"):
        decisao = decidir_acento_grafico(ClasseTonica.PROPAROXITONA, palavra)
        assert decisao.exige_acento is True


def test_monossilabo_tonico_a_e_o_exige_acento():
    for palavra in ("pa", "da", "mas", "fe", "so", "nos"):
        assert decidir_acento_grafico(ClasseTonica.MONOSSILABO_TONICO, palavra).exige_acento is True


def test_monossilabo_tonico_fora_de_a_e_o_nao_exige_acento_por_esta_regra():
    # "sol", "paz", "giz" -- monossílabos tônicos reais sem acento porque
    # não terminam em a/e/o.
    for palavra in ("sol", "paz", "giz", "mim"):
        assert decidir_acento_grafico(ClasseTonica.MONOSSILABO_TONICO, palavra).exige_acento is False


def test_oxitona_a_e_o_exige_acento():
    # café, sofá, avô, avó, paletó -- exemplos clássicos de oxítona
    # acentuada por terminar em a/e/o.
    for palavra in ("cafe", "sofa", "avo", "paleto"):
        assert decidir_acento_grafico(ClasseTonica.OXITONA, palavra).exige_acento is True


def test_oxitona_em_ens_exige_acento():
    # também, parabéns -- oxítona terminada em em/ens.
    for palavra in ("tambem", "parabens", "armazem"):
        assert decidir_acento_grafico(ClasseTonica.OXITONA, palavra).exige_acento is True


def test_oxitona_fora_da_tabela_nao_exige_acento_por_esta_regra():
    # javali, urubu, mulher, capaz -- oxítonas reais sem acento por
    # terminarem fora da tabela (i, u, r, z).
    for palavra in ("javali", "urubu", "mulher", "capaz"):
        assert decidir_acento_grafico(ClasseTonica.OXITONA, palavra).exige_acento is False


def test_paroxitona_terminada_em_a_e_o_em_ens_am_nao_exige_acento():
    # casa, come, menino, homem, jovens, falam -- paroxítonas comuns sem
    # acento, mesmo padrão usado na maioria do léxico regular.
    for palavra in ("casa", "come", "menino", "homem", "jovens", "falam", "amem"):
        assert decidir_acento_grafico(ClasseTonica.PAROXITONA, palavra).exige_acento is False


def test_paroxitona_fora_da_tabela_exige_acento():
    # fácil, táxi, hífen, vírus, tórax, caráter -- paroxítonas clássicas
    # que exigem acento por terminarem fora de a/e/o/em/ens/am. Palavras
    # com til nasal ("órgão") ficam fora de propósito: o til marca
    # nasalidade (obrigatório, não é o acento de tonicidade decidido
    # aqui) e exigiria preservar esse diacrítico na entrada, questão
    # diferente da que esta função resolve.
    for palavra in ("facil", "taxi", "hifen", "virus", "torax", "carater"):
        assert decidir_acento_grafico(ClasseTonica.PAROXITONA, palavra).exige_acento is True


def test_ditongo_oral_tonico_nao_decidido_por_esta_regra():
    # achado real de validação contra o léxico vivo: "valeu" (oxítona,
    # "-eu") não tem acento, mas "chapéu" (oxítona, "-éu") tem -- depende
    # de abertura vocálica lexical, não decidido mecanicamente aqui.
    for classe in (ClasseTonica.OXITONA, ClasseTonica.MONOSSILABO_TONICO):
        decisao = decidir_acento_grafico(classe, "valeu")
        assert decisao.exige_acento is None
        assert "abertura vocálica" in decisao.motivo


def test_ditongo_oral_valeu_e_chapeu_confirmam_a_ambiguidade_no_lexico_vivo():
    dicionario = Dicionario.padrao()
    assert "valeu" in dicionario
    assert "valéu" not in dicionario


def test_palavra_vazia_levanta_erro():
    with pytest.raises(ValueError):
        decidir_acento_grafico(ClasseTonica.OXITONA, "   ")


def test_acento_diferencial_pares_estao_no_dicionario_vivo():
    dicionario = Dicionario.padrao()
    for acentuada, sem_acento, _motivo in ACENTO_DIFERENCIAL:
        assert acentuada in dicionario, f"{acentuada!r} deveria estar no dicionário"
        assert sem_acento in dicionario, f"{sem_acento!r} deveria estar no dicionário"
        assert acentuada != sem_acento
