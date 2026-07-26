import pytest

from lingua_portuguesa.corretor_ortografico_sessao import corrigir_ortografia
from lingua_portuguesa.normalizacao_pontuacao import normalizar_texto_corrido


@pytest.mark.parametrize(
    "texto",
    (
        "A mercadoria foi reposta na prateleira.",
        "Esta repostagem ficou boa.",
        "A regra foi preposta ao capítulo.",
    ),
)
def test_reposta_nao_e_substituida_como_fragmento_ou_participio(texto):
    resultado = corrigir_ortografia(texto)
    assert resultado.corrigido == texto
    assert resultado.alteracoes == ()


@pytest.mark.parametrize(
    "texto",
    (
        "Quero detetar erros.",
        "Quero fazer isto duma só vez.",
        "Quero maus perguntas.",
        "O orçamento foi aprovado.",
    ),
)
def test_whitelist_abstem_se_de_variantes_e_trocas_semanticas(texto):
    resultado = corrigir_ortografia(texto)
    assert resultado.corrigido == texto
    assert resultado.alteracoes == ()


def test_reposta_so_e_corrigida_em_contexto_inequivoco_de_resposta():
    resultado = corrigir_ortografia("A reposta está correta.")
    assert resultado.corrigido == "A resposta está correta."
    assert tuple((item.antes, item.depois) for item in resultado.alteracoes) == (
        ("reposta", "resposta"),
    )


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    (
        ("aprimure isto.", "aprimore isto."),
        ("Aprimure isto.", "Aprimore isto."),
        ("APRIMURE ISTO.", "APRIMORE ISTO."),
    ),
)
def test_correcao_inequivoca_preserva_caixa(entrada, esperado):
    assert corrigir_ortografia(entrada).corrigido == esperado


def test_correcao_inequivoca_nao_casa_dentro_de_palavra():
    texto = "O identificador reaprimurex deve ficar intacto."
    assert corrigir_ortografia(texto).corrigido == texto


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    (
        ("visite exemplo.com/teste", "Visite exemplo.com/teste."),
        (
            "envie para nome.sobrenome@example.com",
            "Envie para nome.sobrenome@example.com.",
        ),
        ("veja https://example.com/path", "Veja https://example.com/path."),
        ("hora 12:30", "Hora 12:30."),
        ("use a versão 3.14.4 agora", "Use a versão 3.14.4 agora."),
        ("execute /usr/local/bin/python", "Execute /usr/local/bin/python."),
        ("use U.S.A. como sigla", "Use U.S.A. como sigla."),
        ("rode `foo.bar()` agora", "Rode `foo.bar()` agora."),
    ),
)
def test_normalizacao_preserva_trechos_tecnicos(entrada, esperado):
    assert normalizar_texto_corrido(entrada) == esperado


def test_normalizacao_respeita_pontuacao_final_dentro_de_aspas():
    assert normalizar_texto_corrido('ele perguntou "vem?"') == 'Ele perguntou "vem?"'


def test_normalizacao_nao_reescreve_conteudo_entre_aspas():
    entrada = 'ele citou "x ,y ."'
    assert normalizar_texto_corrido(entrada) == 'Ele citou "x ,y ."'
