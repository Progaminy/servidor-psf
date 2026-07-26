from lingua_portuguesa import (
    ClasseGramatical,
    Dicionario,
    EntradaLexical,
    Genero,
    MotorPortugues,
    Numero,
)
from lingua_portuguesa.corretor import Corretor
from lingua_portuguesa.tipos import Pessoa


def _dicionario_ambiguo() -> Dicionario:
    d = Dicionario()
    d.adicionar(EntradaLexical("eu", "eu", ClasseGramatical.PRONOME, numero=Numero.SINGULAR, pessoa=Pessoa.PRIMEIRA))
    d.adicionar(EntradaLexical("banco", "banco", ClasseGramatical.SUBSTANTIVO, genero=Genero.MASCULINO, numero=Numero.SINGULAR))
    d.adicionar(EntradaLexical("bancar", "banco", ClasseGramatical.VERBO, numero=Numero.SINGULAR, pessoa=Pessoa.PRIMEIRA))
    return d


def test_motor_promove_desambiguacao_antes_da_gramatica():
    analise = MotorPortugues(dicionario=_dicionario_ambiguo()).analisar("Eu banco.")
    banco = next(item for item in analise.morfologia if item.token.texto == "banco")
    assert banco.principal.classe is ClasseGramatical.VERBO
    assert len(banco.leituras) == 2
    assert any(d.codigo == "CATEGORIA_INCOMPATIVEL" for d in analise.diagnosticos)


def test_correcao_ortografica_entra_no_resultado_e_na_revisao():
    motor = MotorPortugues()
    analise = motor.analisar("voçe veio")
    diagnostico = next(d for d in analise.diagnosticos if d.codigo == "ORTOGRAFIA_SUGESTAO")
    assert "você" in diagnostico.sugestao
    revisao = motor.revisar_escrita("voçe veio")
    assert dict(revisao["sugestoes_ortografia"])["voçe"][0] == "você"


def test_ngrama_e_fonetica_ficam_expostos_na_analise():
    analise = MotorPortugues().analisar("A casa existe.")
    assert len(analise.probabilidades_contextuais) == 3
    assert dict(analise.codigos_foneticos)["casa"]


def test_clitico_e_uso_do_se_entram_no_pipeline_principal():
    analise = MotorPortugues().analisar("Vendem-se casas.")
    assert tuple(token.texto for token in analise.tokens[:3]) == ("Vendem", "-", "se")
    assert analise.morfologia[0].principal.classe is ClasseGramatical.VERBO
    assert analise.morfologia[2].principal.classe is ClasseGramatical.PRONOME
    assert analise.usos_do_se == ("apassivador",)
    assert ("sujeito_posposto", "casas") in tuple(
        (item.funcao, item.texto) for item in analise.constituintes
    )


def test_vocativo_objeto_sujeito_posposto_e_coordenacao():
    motor = MotorPortugues()
    vocativo = motor.analisar("João, venha aqui!")
    assert ("vocativo", "João") in tuple((c.funcao, c.texto) for c in vocativo.constituintes)
    assert not any(c.funcao == "sujeito" for c in vocativo.constituintes)

    transitiva = motor.analisar("Maria viu João.")
    assert ("objeto_direto", "João") in tuple((c.funcao, c.texto) for c in transitiva.constituintes)

    posposto = motor.analisar("Chegaram os alunos.")
    assert ("sujeito_posposto", "alunos") in tuple((c.funcao, c.texto) for c in posposto.constituintes)

    coordenado = motor.analisar("A Maria e o João chegou.")
    assert any(d.codigo == "CONCORDANCIA_VERBO_SUJEITO" for d in coordenado.diagnosticos)


def test_estados_processavel_e_gramaticalmente_aceitavel_sao_distintos():
    analise = MotorPortugues().analisar("Os livros chegou.")
    assert analise.processavel
    assert analise.valido
    assert not analise.gramaticalmente_aceitavel


def test_candidato_em_contexto_calcula_compatibilidade_gramatical():
    corretor = Corretor()
    tokens = corretor.tokenizador.tokenizar("A menina bonitu chegou.")
    indice = next(i for i, token in enumerate(tokens) if token.texto == "bonitu")
    candidatos = corretor.candidatos_para(
        "bonitu", anterior="menina", contexto=tokens, indice_contexto=indice
    )
    assert candidatos
    assert all(c.compatibilidade_gramatical is not None for c in candidatos)


def test_sujeito_oculto_marca_ausencia_sem_inventar_conteudo():
    motor = MotorPortugues()
    vocativo = motor.analisar("João, venha aqui!")
    assert ("sujeito_oculto", "") in tuple((c.funcao, c.texto) for c in vocativo.constituintes)

    pro_drop = motor.analisar("Chegou.")
    assert ("sujeito_oculto", "") in tuple((c.funcao, c.texto) for c in pro_drop.constituintes)

    impessoal = motor.analisar("Há muitos problemas.")
    assert not any(c.funcao == "sujeito_oculto" for c in impessoal.constituintes)


def test_cadeia_auxiliar_reconhece_nucleo_verbal_e_objeto():
    motor = MotorPortugues()
    progressiva = motor.analisar("Os alunos estão estudando.")
    funcoes = tuple((c.funcao, c.texto) for c in progressiva.constituintes)
    assert ("auxiliar_verbal", "estão") in funcoes
    assert ("sujeito", "Os alunos") in funcoes

    com_objeto = motor.analisar("Maria estava cantando uma canção.")
    funcoes_objeto = tuple((c.funcao, c.texto) for c in com_objeto.constituintes)
    assert ("auxiliar_verbal", "estava") in funcoes_objeto
    assert ("objeto_direto", "canção") in funcoes_objeto


def test_voz_passiva_reconhece_sujeito_paciente_e_agente():
    analise = MotorPortugues().analisar("As cartas foram escritas pelos alunos.")
    funcoes = tuple((c.funcao, c.texto) for c in analise.constituintes)
    assert ("auxiliar_verbal", "foram") in funcoes
    assert ("sujeito_paciente", "As cartas") in funcoes
    assert ("agente_da_passiva", "alunos") in funcoes


def test_multiplas_oracoes_sao_divididas_na_conjuncao_subordinativa():
    motor = MotorPortugues()
    complemento = motor.analisar("Eu quero que você venha.")
    funcoes = tuple((c.funcao, c.texto) for c in complemento.constituintes)
    assert ("sujeito", "Eu") in funcoes
    assert ("sujeito", "você") in funcoes

    causal = motor.analisar("Maria correu porque estava atrasada.")
    funcoes_causal = tuple((c.funcao, c.texto) for c in causal.constituintes)
    assert ("sujeito", "Maria") in funcoes_causal
    assert ("predicativo", "atrasada") in funcoes_causal
    assert ("sujeito_oculto", "") in funcoes_causal
