from ensino.resolvedor_perguntas_portugues import resolver_pergunta_conceito


def test_pergunta_o_que_e_verbo_usa_o_conceito_puro_documentado():
    r = resolver_pergunta_conceito("O que é um verbo?")
    assert r.resolvida is True
    assert r.termo == "verbo"
    assert "ação" in r.resposta or "estado" in r.resposta


def test_pergunta_com_termo_composto_e_artigo_feminino():
    r = resolver_pergunta_conceito("o que é uma rima consoante?")
    assert r.resolvida is True
    assert r.termo == "rima consoante"


def test_defina_tambem_e_reconhecido_como_gatilho():
    r = resolver_pergunta_conceito("Defina poema.")
    assert r.resolvida is True
    assert r.termo == "poema"


def test_plural_cai_para_singular_quando_singular_existe():
    r = resolver_pergunta_conceito("O que são pronomes?")
    assert r.resolvida is True
    assert r.termo == "pronome"


def test_resposta_inclui_construcao_funcao_e_exemplo_nunca_so_a_construcao():
    r = resolver_pergunta_conceito("explique métrica")
    assert r.resolvida is True
    assert "Exemplo:" in r.resposta


def test_termo_sem_conceito_exato_mas_com_relacionados_nao_finge_resposta():
    # "substantivo" sozinho não existe como conceito-base (só os subtipos:
    # substantivo próprio, comum, concreto...) -- lacuna real de conteúdo,
    # não bug de rota: honesto, sugere os relacionados, não inventa.
    r = resolver_pergunta_conceito("Defina substantivo.")
    assert r.resolvida is False
    assert r.resposta is None
    assert "substantivo próprio" in r.raciocinio


def test_termo_totalmente_desconhecido_e_honesto():
    r = resolver_pergunta_conceito("o que é xilofonia magnética inexistente?")
    assert r.resolvida is False
    assert "não invento" in r.raciocinio


def test_frase_sem_gatilho_nao_e_reconhecida():
    r = resolver_pergunta_conceito("Maria correu porque estava atrasada.")
    assert r.resolvida is False
    assert r.termo is None
