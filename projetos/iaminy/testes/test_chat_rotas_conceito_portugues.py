"""Prova fim-a-fim de que uma pergunta conceitual de português ("o que é
um verbo?") passa a ser respondida pelo chat vivo com o conhecimento
puro já documentado -- antes disso, nenhuma rota do chat consultava
`MotorPortugues().conhecimento_portugues`, então a pergunta caía direto
em "não materializado" mesmo com o conceito pronto e testado.
"""
from nucleo.chat_rotas_resolvedores import _responder_conceito_portugues
from nucleo.chat_vivo import responder


def test_responder_conceito_portugues_usa_o_conhecimento_puro():
    resposta = _responder_conceito_portugues("O que é um verbo?")
    assert resposta is not None
    assert resposta.intencao == "conceito_portugues"
    assert resposta.conhecimento_encontrado is True
    assert "ação" in resposta.texto or "estado" in resposta.texto


def test_responder_conceito_portugues_e_none_quando_nao_e_pergunta_conceitual():
    assert _responder_conceito_portugues("Maria correu porque estava atrasada.") is None


def test_chat_vivo_responde_o_que_e_um_verbo_fim_a_fim():
    r = responder("O que é um verbo?")
    assert r.origem == "resolvedor_perguntas_portugues"
    assert "ação" in r.texto or "estado" in r.texto


def test_chat_vivo_responde_o_que_e_um_poema_fim_a_fim():
    r = responder("o que é um poema?")
    assert r.origem == "resolvedor_perguntas_portugues"
    assert "verso" in r.texto or "gênero" in r.texto


def test_chat_vivo_e_honesto_quando_o_conceito_nao_e_exato():
    r = responder("Defina substantivo.")
    assert r.origem == "resolvedor_perguntas_portugues"
    assert r.conhecimento_encontrado is False
    assert "substantivo próprio" in r.texto
