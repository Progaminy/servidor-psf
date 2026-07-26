from lingua_portuguesa import MotorPortugues, OpcoesAnalise
from lingua_portuguesa.avaliacao import avaliar_motor, carregar_corpus
from lingua_portuguesa.corretor import Corretor


def test_corpus_dourado_tem_categorias_variadas_e_ids_unicos():
    casos = carregar_corpus()
    assert len(casos) >= 25
    assert len({caso["id"] for caso in casos}) == len(casos)
    assert any(caso.get("uso_do_se") for caso in casos)
    assert any("ORTOGRAFIA_SUGESTAO" in caso["diagnosticos"] for caso in casos)
    assert any("CONCORDANCIA_VERBO_SUJEITO" in caso["diagnosticos"] for caso in casos)


def test_avaliacao_agregada_protege_metricas_do_pipeline():
    relatorio = avaliar_motor()
    assert relatorio.total_casos >= 25
    assert relatorio.diagnosticos.precisao == 1.0
    assert relatorio.diagnosticos.revocacao == 1.0
    assert relatorio.constituintes.f1 == 1.0
    assert relatorio.acuracia_morfologica == 1.0
    assert relatorio.cobertura_lexical >= 0.95
    assert relatorio.taxa_falso_positivo_textos_corretos == 0.0
    assert relatorio.sugestoes_corretas == relatorio.sugestoes_esperadas
    assert relatorio.falhas == ()


def test_perfil_leve_mantem_gramatica_e_adia_recursos_pesados():
    motor = MotorPortugues(opcoes=OpcoesAnalise.leve())
    assert motor.modelo_ngrama is None
    assert motor.corretor is None

    analise = motor.analisar("Os livros chegou.")
    assert any(d.codigo == "CONCORDANCIA_VERBO_SUJEITO" for d in analise.diagnosticos)
    assert analise.correcao is None
    assert analise.probabilidades_contextuais == ()
    assert analise.codigos_foneticos == ()
    assert "correcao" not in analise.recursos_executados
    assert "ngramas" not in analise.recursos_executados
    assert "fonetica" not in analise.recursos_executados
    assert "cliticos" in analise.recursos_executados
    assert motor.modelo_ngrama is None
    assert motor.corretor is None


def test_revisao_forca_perfil_completo_mesmo_em_motor_leve():
    motor = MotorPortugues(opcoes=OpcoesAnalise.leve())
    revisao = motor.revisar_escrita("voçe veio")
    assert "você" in dict(revisao["sugestoes_ortografia"])["voçe"]
    assert motor.modelo_ngrama is not None
    assert motor.corretor is not None


def test_opcoes_podem_ser_sobrescritas_por_chamada():
    motor = MotorPortugues(opcoes=OpcoesAnalise.leve())
    analise = motor.analisar("A casa existe.", opcoes=OpcoesAnalise.completa())
    assert analise.correcao is not None
    assert analise.probabilidades_contextuais
    assert analise.codigos_foneticos
    assert {"correcao", "ngramas", "fonetica"}.issubset(analise.recursos_executados)


def test_contexto_e_fonetica_desligados_nao_sao_usados_no_ranking():
    corretor = Corretor()
    candidatos = corretor.candidatos_para(
        "protugues", anterior="estudo", usar_contexto=False, usar_fonetica=False
    )
    assert candidatos
    assert all(c.probabilidade_contexto is None for c in candidatos)
    assert all(c.similaridade_fonetica is None for c in candidatos)
    assert all(c.peso_erro is None for c in candidatos)


def test_correcao_sem_contexto_nao_carrega_modelo_ngrama():
    opcoes = OpcoesAnalise(
        corrigir_ortografia=True,
        calcular_contexto=False,
        calcular_fonetica=False,
    )
    motor = MotorPortugues(opcoes=opcoes)
    assert motor.modelo_ngrama is None
    analise = motor.analisar("voçe veio")
    assert analise.correcao is not None
    assert "correcao" in analise.recursos_executados
    assert "ngramas" not in analise.recursos_executados
    assert motor.modelo_ngrama is None
    assert motor.corretor.modelo_ngrama is None


def test_motor_geral_encaminha_perfil_leve():
    from motor.geral import MotorGeralIAMiny

    portugues = MotorPortugues(opcoes=OpcoesAnalise.leve())
    geral = MotorGeralIAMiny(portugues=portugues)
    analise = geral.analisar_portugues("Os livros chegou.", opcoes=OpcoesAnalise.leve())
    assert analise.correcao is None
    assert "correcao" not in analise.recursos_executados
