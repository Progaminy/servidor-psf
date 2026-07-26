"""Fecha um achado real de auditoria externa: os 11 verbos irregulares
comuns (ser, estar, ter, fazer, ir, querer, poder, saber, dizer, ver, dar)
só tinham formas do presente em `lexico_base.json` -- por isso "foi"
(pretérito comuníssimo de "ir"/"ser") não estava no dicionário e o
corretor sugeria "oi" no lugar. Este ficheiro prende o pretérito perfeito
das formas mais comuns em texto corrido (3ª pessoa singular/plural, mais
1ª pessoa onde a forma é inequívoca).
"""
from lingua_portuguesa import Dicionario, MotorPortugues
from lingua_portuguesa.corretor import Corretor
from lingua_portuguesa.tipos import Pessoa, Numero


def test_foi_esta_no_dicionario_com_pessoa_e_numero_reais():
    dicionario = Dicionario.padrao()
    leituras = dicionario.buscar("foi")
    assert leituras
    lemas = {leitura.lema for leitura in leituras}
    # "foi" é homógrafo real entre "ir" e "ser" -- as duas leituras devem
    # existir, nenhuma escondida.
    assert lemas == {"ir", "ser"}
    for leitura in leituras:
        assert leitura.pessoa == Pessoa.TERCEIRA
        assert leitura.numero == Numero.SINGULAR


def test_formas_irregulares_centrais_estao_no_dicionario():
    dicionario = Dicionario.padrao()
    formas_esperadas = (
        "fui", "foi", "fomos", "foram",  # ser/ir
        "estive", "esteve", "estivemos", "estiveram",  # estar
        "tive", "teve", "tivemos", "tiveram",  # ter
        "fiz", "fez", "fizemos", "fizeram",  # fazer
        "quis", "quisemos", "quiseram",  # querer
        "pude", "pôde", "pudemos", "puderam",  # poder
        "soube", "soubemos", "souberam",  # saber
        "disse", "dissemos", "disseram",  # dizer
        "vi", "viu", "vimos", "viram",  # ver
        "dei", "deu", "demos", "deram",  # dar
    )
    for forma in formas_esperadas:
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_formas_ambiguas_entre_primeira_e_terceira_pessoa_nao_fingem_pessoa_unica():
    # "quis"/"soube"/"disse" são genuinamente a mesma forma para "eu" e
    # "ele" no pretérito -- o índice deve preservar as duas leituras, sem
    # escolher uma pessoa por acaso nem apagar esse traço gramatical.
    dicionario = Dicionario.padrao()
    for forma, lema in (("quis", "querer"), ("soube", "saber"), ("disse", "dizer")):
        flexoes = {
            (leitura.pessoa, leitura.numero)
            for leitura in dicionario.buscar(forma)
            if leitura.lema == lema
        }
        assert flexoes == {
            (Pessoa.PRIMEIRA, Numero.SINGULAR),
            (Pessoa.TERCEIRA, Numero.SINGULAR),
        }


def test_ter_tem_preterito_imperfeito_no_dicionario():
    # achado real: "tinha" (freq. alta no corpus, "ter" existente só com
    # presente/pretérito perfeito) não estava no léxico -- imperfeito de
    # "ter" faltava inteiro.
    dicionario = Dicionario.padrao()
    for forma in ("tinha", "tinhas", "tínhamos", "tinham"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_ser_e_estar_tem_imperfeito_e_ser_tem_condicional():
    # achado real: "estava" e "seria" (candidatos de alta frequência) não
    # existiam -- "ser"/"estar" só tinham presente/pretérito perfeito.
    dicionario = Dicionario.padrao()
    formas_esperadas = (
        "era", "eras", "éramos", "eram",  # ser, imperfeito
        "seria", "serias", "seríamos", "seriam",  # ser, condicional
        "estava", "estavas", "estávamos", "estavam",  # estar, imperfeito
    )
    for forma in formas_esperadas:
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_dizer_e_fazer_tem_participio_irregular():
    # achado real ao investigar candidatos ("dito", "feita"): "dizer"/
    # "fazer" só tinham presente/pretérito perfeito -- particípio
    # irregular ("dito"/"feito", não "dizido"/"fazido") nunca existia.
    dicionario = Dicionario.padrao()
    for forma in ("dito", "dita", "ditos", "ditas", "feito", "feita", "feitos", "feitas"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_ser_e_vir_tem_presente_do_subjuntivo():
    # achado real: "seja"/"venha" (candidatos de alta frequência,
    # extremamente comuns -- "seja como for", "venha comigo") não
    # existiam -- "ser"/"vir" nunca tiveram subjuntivo nenhum registado.
    dicionario = Dicionario.padrao()
    for forma in ("seja", "sejas", "sejamos", "sejam", "venha", "venhas", "venhamos", "venham"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    # 1ª/3ª singular são ambíguas na língua real -- pessoa=None, não uma
    # pessoa fingida (mesmo critério já usado no pretérito de "quis"/
    # "soube"/"disse").
    (leitura_seja,) = dicionario.buscar("seja")
    assert leitura_seja.pessoa is None


def test_por_tem_presente_preterito_e_subjuntivo():
    # achado real: "pôr" ficou de fora por ora quando "sair"/"cair"
    # (-air vocálico) foram fechados, registado em conversa.md como
    # "irregularíssimo, não seguir o mesmo cuidado apressado" -- fechado
    # agora com o mesmo cuidado já usado pra "ser"/"vir": raiz suplectiva
    # "pu-"/"pon-"/"põ-", nenhuma delas vem de "pôr" por regra mecânica
    # nenhuma, mesmo critério dos outros irregulares comuns do JSON.
    dicionario = Dicionario.padrao()
    for forma in ("ponho", "põe", "pomos", "põem", "pus", "pôs", "pusemos", "puseram",
                  "ponha", "ponhas", "ponhamos", "ponham"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    # 1ª/3ª singular do subjuntivo são ambíguas na língua real --
    # pessoa=None, mesmo critério já usado pra "seja"/"tenha".
    (leitura_ponha,) = dicionario.buscar("ponha")
    assert leitura_ponha.pessoa is None


def test_compostos_de_por_herdam_irregularidade_completa():
    # mesma herança de "conter"/"manter" com "ter": "compor"/"decompor"/
    # "expor"/"propor"/"supor" são compostos de "pôr" e herdam TODA a
    # irregularidade (componho/compõe/compõem, não "compo"/"compora" que
    # a regra genérica de "-or" geraria) -- registado em conversa.md como
    # próximo passo depois de "pôr" fechado.
    dicionario = Dicionario.padrao()
    for prefixo in ("com", "decom", "ex", "pro", "su"):
        for forma in ("ponho", "põe", "pus", "pôs", "ponha"):
            forma_composta = prefixo + forma
            assert forma_composta in dicionario, f"{forma_composta!r} deveria estar no dicionário"


def test_caber_trazer_valer_irregulares_comuns_ausentes_ate_agora():
    # achado real: "caber"/"trazer"/"valer" (verbos comuns, cotidianos)
    # nunca existiam no léxico -- nenhuma forma, nem presente. Fechados
    # com o mesmo cuidado de "ser"/"vir"/"pôr": "caibo"/"trago"/"valho"
    # (1sg presente irregular), "coube"/"trouxe" (pretérito totalmente
    # suplectivo, ambíguo 1ª/3ª singular -- as DUAS pessoas ficam
    # registadas na mesma forma, mesmo critério de "soube"), "caiba"/
    # "traga"/"valha" (subjuntivo de raiz irregular). "valer" é caso
    # misto: só presente e subjuntivo são irregulares, o pretérito é
    # regular (vali/valeu/valemos/valeram) e entrou completo também.
    dicionario = Dicionario.padrao()
    for forma in ("caibo", "cabe", "coube", "coubemos", "couberam", "caiba", "caibas"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    for forma in ("trago", "traz", "trouxe", "trouxemos", "trouxeram", "traga"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    for forma in ("valho", "vale", "vali", "valeu", "valemos", "valeram", "valha"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    # "coube"/"trouxe" ambíguos entre 1ª e 3ª singular -- as duas leituras
    # reais convivem, nenhuma apaga a outra (mesmo mecanismo de "soube").
    pessoas_coube = {l.pessoa for l in dicionario.buscar("coube") if l.lema == "caber"}
    assert pessoas_coube == {Pessoa.PRIMEIRA, Pessoa.TERCEIRA}
    pessoas_trouxe = {l.pessoa for l in dicionario.buscar("trouxe") if l.lema == "trazer"}
    assert pessoas_trouxe == {Pessoa.PRIMEIRA, Pessoa.TERCEIRA}
    # "valemos" ambíguo entre presente E pretérito perfeito (mesma string,
    # mesmo mecanismo já usado pra "estudamos"/"lemos").
    tempos_valemos = {l.atributos.get("tempo") for l in dicionario.buscar("valemos") if l.lema == "valer"}
    assert tempos_valemos == {"presente", "pretérito perfeito"}


def test_ler_tem_preterito_perfeito_completo():
    # achado real: "leu" (candidato frequente) não existia -- "ler" só
    # tinha presente. "lemos" tem DUAS leituras reais (presente E
    # pretérito perfeito, mesma string), nenhuma pode sobrescrever a
    # outra -- mesmo mecanismo já usado para "estudamos".
    dicionario = Dicionario.padrao()
    for forma in ("li", "leu", "lemos", "leram"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    tempos_lemos = {l.atributos.get("tempo") for l in dicionario.buscar("lemos") if l.lema == "ler"}
    assert tempos_lemos == {"presente", "pretérito perfeito"}


def test_ter_conter_manter_tem_gerundio():
    # achado real: "mantendo" (candidato persistente de alta frequência)
    # não existia -- "ter"/"conter"/"manter" nunca tiveram gerúndio
    # registado, apesar de ser totalmente regular na forma (ter+"endo").
    dicionario = Dicionario.padrao()
    for forma in ("tendo", "contendo", "mantendo"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_ser_tem_gerundio():
    # achado real: "sendo" (candidato de alta frequência) não existia --
    # "ser" nunca teve gerúndio registado, apesar de regular na forma.
    assert "sendo" in Dicionario.padrao()


def test_conter_e_manter_herdam_irregularidade_completa_de_ter():
    # achado real ao investigar "contém"/"mantendo" como candidatos:
    # "conter"/"manter" são compostos de "ter" e herdam TODA a
    # irregularidade (contenho/contém/contêm, mantenho/mantém/mantêm,
    # nunca "conto"/"contem" que a regra genérica de "-er" geraria) --
    # mesma classe de cuidado já usada para "vir"/"subtrair"/"conferir".
    dicionario = Dicionario.padrao()
    formas_esperadas = (
        "contenho", "contém", "contemos", "contêm",
        "contive", "conteve", "contivemos", "contiveram",
        "continha", "continhas", "contínhamos", "continham",
        "mantenho", "mantém", "mantemos", "mantêm",
        "mantive", "manteve", "mantivemos", "mantiveram",
        "mantinha", "mantinhas", "mantínhamos", "mantinham",
    )
    for forma in formas_esperadas:
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_deter_reter_convir_intervir_provir_sobrevir_herdam_irregularidade_de_ter_e_vir():
    # achado real ao auditar o inventário de "acento diferencial" (conceito
    # 438): a família de compostos de "ter"/"vir" que marcam a 3ª pessoa do
    # plural com acento diferencial do circunflexo só tinha metade
    # construída (conter/manter/obter, mas não deter/reter, nem nenhum
    # composto de "vir" -- convir/intervir/provir/sobrevir). Mesma herança
    # 100% mecânica já usada por "conter"/"manter": prefixo + cada forma da
    # base, com uma única exceção real -- a 3ª singular do presente ganha
    # acento agudo que a base monossílaba não tinha ("tem"->"detém",
    # "vem"->"convém"), porque o prefixo transforma monossílabo em oxítona
    # terminada em "-em" (ver `lingua_portuguesa/acentuacao_grafica.py`,
    # que decide exatamente essa regra); a 3ª plural já vinha acentuada na
    # base e só concatena ("têm"->"detêm", "vêm"->"convêm").
    dicionario = Dicionario.padrao()
    formas_esperadas = (
        "detenho", "detém", "detemos", "detêm",
        "detive", "deteve", "detivemos", "detiveram", "detido",
        "retenho", "retém", "retemos", "retêm",
        "retive", "reteve", "retivemos", "retiveram", "retido",
        "convenho", "convém", "convimos", "convêm",
        "convim", "conveio", "conviemos", "convieram", "convindo",
        "intervenho", "intervém", "intervimos", "intervêm",
        "intervim", "interveio", "interviemos", "intervieram", "intervindo",
        "provenho", "provém", "provimos", "provêm",
        "provim", "proveio", "proviemos", "provieram", "provindo",
        "sobrevenho", "sobrevém", "sobrevimos", "sobrevêm",
        "sobrevim", "sobreveio", "sobrevieram", "sobrevindo",
    )
    for forma in formas_esperadas:
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"


def test_corretor_nao_confunde_foi_com_interjeicao_oi():
    resultado = Corretor().corrigir_texto("Ele foi a escola.")
    sugestoes = dict(resultado.sugestoes_ortografia)
    assert "foi" not in sugestoes


def test_concordancia_verbal_pega_discordancia_real_com_viram():
    motor = MotorPortugues()
    analise = motor.analisar("O menino viram a casa.")
    codigos = [d.codigo for d in analise.diagnosticos]
    assert "CONCORDANCIA_VERBO_SUJEITO" in codigos


def test_haver_tem_subjuntivo_presente_e_futuro_gerundio_e_participio():
    # achado real: "houver" (futuro do subjuntivo -- "se houver problema",
    # "quando houver tempo") é candidato de alta frequência no próprio
    # corpus interno do projeto (9 ocorrências em README/PLANO/RELATÓRIO)
    # e não existia -- "haver" só tinha infinitivo + presente do
    # indicativo (hei/há/havemos/hão) desde que foi "adicionado do zero".
    dicionario = Dicionario.padrao()
    for forma in ("haja", "hajam", "houver", "houvermos", "houverem", "havendo", "havido"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    # 1ª/3ª singular são ambíguas na língua real -- pessoa=None, mesmo
    # critério já usado pra "seja"/"tenha"/"ponha".
    (leitura_haja,) = dicionario.buscar("haja")
    assert leitura_haja.pessoa is None
    (leitura_houver,) = dicionario.buscar("houver")
    assert leitura_houver.pessoa is None


def test_poder_tem_subjuntivo_presente_gerundio_e_preterito_imperfeito():
    # achado real: "podendo" (gerúndio) também é candidato de alta
    # frequência no corpus interno e não existia -- "poder" só tinha
    # presente e pretérito perfeito.
    dicionario = Dicionario.padrao()
    for forma in ("possa", "possamos", "possam", "podendo", "podia", "podíamos", "podiam"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    (leitura_possa,) = dicionario.buscar("possa")
    assert leitura_possa.pessoa is None
    (leitura_podia,) = dicionario.buscar("podia")
    assert leitura_podia.pessoa is None


def test_auditoria_paradigmas_irregulares_fecha_buracos_reais():
    # achado real, auditoria sistemática: comparando os 27 verbos que só
    # existem escritos à mão em `lexico_base.json` (não passam por
    # `_verbo()`) contra o paradigma esperado (presente, pretérito
    # perfeito/imperfeito, presente do subjuntivo, gerúndio, particípio),
    # a maioria tinha buracos reais -- alguns eram só presente+pretérito,
    # nunca ganharam subjuntivo/imperfeito/gerúndio/particípio. Fechado
    # tudo de uma vez, cada forma conferida à mão contra a conjugação real
    # (incluindo achados de homógrafo genuíno, ex.: "vendo" já existia como
    # presente de "vender" e agora também é gerúndio de "ver" -- as duas
    # leituras convivem, nenhuma apaga a outra).
    dicionario = Dicionario.padrao()
    esperadas = (
        "tenha", "tido", "esteja", "estando", "estado",
        "contido", "contenha", "obtido", "obtenha", "mantido", "mantenha",
        "fazendo", "faça", "fazia", "indo", "ido", "vá", "vás", "ia",
        "houve", "houveste", "houvemos", "houveram", "havia",
        "leia", "lia", "ouvi", "ouviu", "ouvimos", "ouviram", "ouvindo",
        "ouvido", "ouça", "ouvia", "podido",
        "querendo", "querido", "querida", "queira", "queria",
        "sabendo", "sabido", "saiba", "sabia",
        "trazendo", "trazido", "trazia", "valendo", "valido", "valia",
        "cabendo", "cabido", "cabia",
        "dando", "dê", "dês", "deem", "demos", "dava",
        "dizendo", "diga", "dizia",
        "vendo", "visto", "vista", "veja", "via",
        "vindo", "vinha",
        "pondo", "posto", "posta", "punha",
        "compondo", "composto", "compunha",
        "decompondo", "decomposto", "expondo", "exposto",
        "propondo", "proposto", "supondo", "suposto",
    )
    for forma in esperadas:
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    # Homógrafos genuínos: a forma nova convive com a leitura já existente
    # de outro lema, nenhuma sobrescreve a outra.
    leituras_vendo = {(l.lema, l.classe.value) for l in dicionario.buscar("vendo")}
    assert ("vender", "verbo") in leituras_vendo
    assert ("ver", "verbo") in leituras_vendo
    leituras_via = {(l.lema, l.classe.value) for l in dicionario.buscar("via")}
    assert ("via", "substantivo") in leituras_via
    assert ("ver", "verbo") in leituras_via
    leituras_posto = {(l.lema, l.classe.value) for l in dicionario.buscar("posto")}
    assert ("posto", "substantivo") in leituras_posto
    assert ("pôr", "verbo") in leituras_posto
    # "vindo" é gerúndio E particípio de "vir" ao mesmo tempo -- duas
    # leituras verbais distintas para a mesma forma, não uma sobrescrita.
    tempos_vindo = {l.atributos.get("tempo") for l in dicionario.buscar("vindo") if l.lema == "vir"}
    assert tempos_vindo == {"gerúndio", "particípio"}


def test_participios_de_verbos_irregulares_flexionam_genero_e_numero():
    # achado real, registado como pendência da rodada anterior: "tido",
    # "contido", "obtido", "mantido", "cabido", "trazido", "valido",
    # "sabido", "podido" e "havido" só existiam na forma masculina
    # singular -- diferente de "feito"/"dito"/"lido"/"dado", que já
    # flexionavam em género e número desde antes. Mesma regra regular de
    # particípio (-ido -> -ida/-idos/-idas) aplicada nos 10, cada forma
    # nova conferida contra colisão real antes de entrar ("valida"/
    # "validas" já existiam como presente de "validar" -- segunda
    # leitura, não sobrescrita).
    dicionario = Dicionario.padrao()
    pares = (
        ("tido", "tida", "tidos", "tidas"),
        ("contido", "contida", "contidos", "contidas"),
        ("obtido", "obtida", "obtidos", "obtidas"),
        ("mantido", "mantida", "mantidos", "mantidas"),
        ("cabido", "cabida", "cabidos", "cabidas"),
        ("trazido", "trazida", "trazidos", "trazidas"),
        ("valido", "valida", "validos", "validas"),
        ("sabido", "sabida", "sabidos", "sabidas"),
        ("podido", "podida", "podidos", "podidas"),
        ("havido", "havida", "havidos", "havidas"),
    )
    for m_sg, f_sg, m_pl, f_pl in pares:
        for forma in (m_sg, f_sg, m_pl, f_pl):
            assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
    leituras_valida = {
        (l.lema, l.atributos.get("tempo")) for l in dicionario.buscar("valida")
    }
    assert ("valer", "particípio") in leituras_valida
    assert ("validar", "presente") in leituras_valida


def test_ir_tem_segunda_leitura_de_subjuntivo_para_vamos_e_vao():
    # achado real, registado como pendência da rodada anterior: "vamos"/
    # "vão" já existiam só como presente do indicativo -- mas são também
    # a forma do presente do subjuntivo de "ir" (mesma grafia, ambiguidade
    # real da língua, mesmo padrão já usado pra "demos"/"ouvimos"/
    # "vindo"). Adicionadas como segunda leitura, sem apagar a primeira.
    dicionario = Dicionario.padrao()
    tempos_vamos = {l.atributos.get("tempo") for l in dicionario.buscar("vamos") if l.lema == "ir"}
    assert tempos_vamos == {"presente", "presente do subjuntivo"}
    tempos_vao = {l.atributos.get("tempo") for l in dicionario.buscar("vão") if l.lema == "ir"}
    assert tempos_vao == {"presente", "presente do subjuntivo"}


def test_subtrair_tem_paradigma_completo_como_sair_e_cair():
    # achado real: comentário antigo excluía "subtrair" de `_VERBOS` por
    # ser "-air" (mesma família de "sair"/"cair") -- verdade quando foi
    # escrito, mas `_corrigir_acento_air` já existe e já está testado
    # nesses dois verbos. "subtrair" é termo central deste projeto
    # (matemática) e só tinha o infinitivo até agora.
    dicionario = Dicionario.padrao()
    for forma in ("subtraio", "subtrai", "subtraímos", "subtraem",
                  "subtraí", "subtraiu", "subtraíram", "subtraindo", "subtraído"):
        assert forma in dicionario, f"{forma!r} deveria estar no dicionário"
