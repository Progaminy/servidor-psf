import json
from importlib.resources import files

import pytest

from lingua_portuguesa.lexico import Dicionario
from lingua_portuguesa.lexico_expansao import (
    _ADJETIVOS,
    _NOMES,
    _PALAVRAS_FUNCIONAIS,
    _VERBOS,
    _forma_adj,
    _forma_nome,
    _plural_de_conceito_e_seguro,
    _verbo,
    entradas_expandidas,
)
from lingua_portuguesa.tipos import ClasseGramatical, Genero, Numero, Pessoa


def _formas(lema, definicao="x"):
    return {entrada.forma for entrada in _forma_adj(lema, definicao)}


def _formas_nome(lema, genero=Genero.FEMININO, definicao="x"):
    return {entrada.forma for entrada in _forma_nome(lema, genero, definicao)}


def test_adjetivo_terminado_em_al_pluraliza_em_ais():
    # achado real: a versão anterior gerava "reals"/"naturals" (não
    # existem em português) em vez de "reais"/"naturais".
    assert _formas("real") == {"real", "reais"}
    assert _formas("natural") == {"natural", "naturais"}


def test_adjetivo_terminado_em_o_continua_com_quatro_formas():
    assert _formas("claro") == {"claro", "clara", "claros", "claras"}


def test_entradas_expandidas_nao_gera_plural_invalido_em_al():
    entradas = entradas_expandidas()
    formas_adjetivo_real = {
        e.forma for e in entradas if e.classe == ClasseGramatical.ADJETIVO and e.lema == "real"
    }
    assert "reals" not in formas_adjetivo_real
    assert "reais" in formas_adjetivo_real


def test_adjetivo_terminado_em_r_pluraliza_em_es():
    # achado real ao preparar candidato "posterior": SEIS adjetivos já
    # existentes ("modular", "linear", "maior", "anterior", "menor",
    # "regular") geravam "modulars"/"maiors" etc. em vez de "modulares"/
    # "maiores" -- mesma regra "-r"->"-es" que substantivo já tinha
    # (professor->professores), nunca aplicada a adjetivo.
    assert _formas("maior") == {"maior", "maiores"}
    assert _formas("anterior") == {"anterior", "anteriores"}
    assert _formas("regular") == {"regular", "regulares"}


def test_entradas_expandidas_nao_gera_plural_invalido_em_r_adjetivo():
    entradas = entradas_expandidas()
    formas_maior = {e.forma for e in entradas if e.classe == ClasseGramatical.ADJETIVO and e.lema == "maior"}
    assert "maiors" not in formas_maior
    assert "maiores" in formas_maior


def test_adjetivo_terminado_em_dor_flexiona_genero_como_o_a():
    # achado real ao investigar candidato "geradora" (alta frequência no
    # corpus): "gerador" (já no léxico, "elemento gerador") caía na regra
    # genérica de "-r" e só gerava "gerador"/"geradores" -- sem feminino.
    # Diferente de "regular"/"maior" (dois gêneros, invariável), o
    # agentivo "-dor" flexiona como "-o": geradora, geradoras.
    assert _formas("gerador") == {"gerador", "geradora", "geradores", "geradoras"}
    # "-r" comum continua invariável em gênero (achado anterior).
    assert _formas("regular") == {"regular", "regulares"}


def test_adjetivo_terminado_em_sor_flexiona_genero_como_dor():
    # achado real ao adicionar "promissor": caía no "-r" genérico
    # (invariável, mesma classe de "regular") e ficava sem "promissora" --
    # errado, "-sor" é o mesmo sufixo agentivo latino de "-dor" (alomorfe
    # conforme a consoante anterior: emissor/emissora, professor/
    # professora), flexiona em género como "gerador"/"geradora".
    assert _formas("promissor") == {"promissor", "promissora", "promissores", "promissoras"}
    # "-r" comum continua invariável (achado anterior, sem regressão).
    assert _formas("regular") == {"regular", "regulares"}


def test_adjetivo_terminado_em_vel_pluraliza_como_al():
    # achado real: "variável"/"compatível" (já no léxico) geravam
    # "variávels"/"compatívels" -- não existem em português. "-vel"
    # pluraliza igual "-al": cai o "l", entra "is".
    assert _formas("variável") == {"variável", "variáveis"}
    assert _formas("compatível") == {"compatível", "compatíveis"}


def test_adjetivo_terminado_em_m_pluraliza_trocando_por_ns():
    # achado real ao investigar candidato "comuns": "comum" (já no
    # léxico) gerava "comums" -- não existe. Mesma troca "-m"->"-ns" já
    # usada em substantivo (item->itens), agora em adjetivo.
    assert _formas("comum") == {"comum", "comuns"}


def test_substantivo_terminado_em_cao_pluraliza_em_coes():
    # achado real: a versão anterior gerava "intençãos"/"construçãos" (não
    # existem em português) em vez de "intenções"/"construções".
    assert _formas_nome("intenção") == {"intenção", "intenções"}
    assert _formas_nome("construção") == {"construção", "construções"}


def test_substantivo_terminado_em_m_pluraliza_trocando_por_ns():
    # achado real: "item" (já existente) gerava "items" em vez de "itens".
    assert _formas_nome("item", Genero.MASCULINO) == {"item", "itens"}
    assert _formas_nome("som", Genero.MASCULINO) == {"som", "sons"}
    assert _formas_nome("linguagem") == {"linguagem", "linguagens"}


def test_substantivo_terminado_em_r_ou_z_continua_com_es():
    assert _formas_nome("professor", Genero.MASCULINO) == {"professor", "professores"}


def test_entradas_expandidas_nao_gera_plural_invalido_em_cao():
    entradas = entradas_expandidas()
    formas_intencao = {e.forma for e in entradas if e.lema == "intenção"}
    assert "intençãos" not in formas_intencao
    assert "intenções" in formas_intencao


def test_substantivo_terminado_em_al_pluraliza_em_ais():
    # achado real ao adicionar "anel": "vogal"/"radical"/"numeral"/"plural"
    # (já existentes) geravam "vogals"/"radicals"/"numerals"/"plurals" em
    # vez de "vogais"/"radicais"/"numerais"/"plurais" -- "-al" nunca leva
    # acento novo no plural (o ditongo "ai" não é marcado).
    assert _formas_nome("vogal", Genero.FEMININO) == {"vogal", "vogais"}
    assert _formas_nome("radical", Genero.MASCULINO) == {"radical", "radicais"}


def test_substantivo_terminado_em_el_sem_acento_ganha_acento_no_plural():
    # achado real: "anel"/"papel"/"hotel" não têm acento no singular
    # (sílaba tônica é a própria terminação "-el", regra padrão), mas o
    # plural precisa de acento novo porque "e" tônico final antes de "s"
    # é marcado em português: anel->anéis, nunca "anels" nem "aneis".
    assert _formas_nome("anel", Genero.MASCULINO) == {"anel", "anéis"}
    assert _formas_nome("papel", Genero.MASCULINO) == {"papel", "papéis"}


def test_substantivo_terminado_em_el_com_acento_mantem_acento_existente():
    # achado real: "nível" já tem acento marcado (sílaba tônica não é a
    # terminação "-el"), então o plural só cai o "l" e entra "is" sem
    # adicionar acento novo: nível->níveis, nunca "nívels" nem "nivéis".
    assert _formas_nome("nível", Genero.MASCULINO) == {"nível", "níveis"}


def test_entradas_expandidas_nao_gera_plural_invalido_em_el():
    entradas = entradas_expandidas()
    formas_anel = {e.forma for e in entradas if e.lema == "anel"}
    assert "anels" not in formas_anel
    assert "anéis" in formas_anel


def test_substantivo_ao_irregular_usa_excecao_lexical():
    # achado real ao preparar "cão": resto da classe "-ão" (fora de
    # "-ção"/"-são"/"-xão") não tem regra fonética -- "mão"/"pão"/"cão"
    # pluralizam de 3 jeitos diferentes pra terminação igual, só exceção
    # lexical resolve (nunca heurística de sufixo, que erraria as outras
    # classes). "cão"->"cães", nunca "cãos"/"cãoes".
    assert _formas_nome("cão", Genero.MASCULINO) == {"cão", "cães"}


def test_substantivo_terminado_em_ao_solto_pluraliza_em_oes_por_padrao():
    # achado real ao adicionar "padrão"/"razão"/"união" (já no léxico):
    # sem tratamento nenhum pra "-ão" fora de "-ção"/"-são"/"-xão"/exceção
    # lexical, a regra caía no "+s" genérico ("padrãos", "razãos",
    # "uniãos") -- nenhuma existe. "-ões" é o padrão PRODUTIVO da classe
    # (a maioria dos substantivos em "-ão" segue isto), não a exceção --
    # "cão" continua resolvido pela exceção lexical, sem conflito.
    assert _formas_nome("padrão", Genero.MASCULINO) == {"padrão", "padrões"}
    assert _formas_nome("razão", Genero.FEMININO) == {"razão", "razões"}
    assert _formas_nome("união", Genero.FEMININO) == {"união", "uniões"}
    assert _formas_nome("cão", Genero.MASCULINO) == {"cão", "cães"}


def test_entradas_expandidas_nao_gera_plural_invalido_em_ao():
    entradas = entradas_expandidas()
    formas_cao = {e.forma for e in entradas if e.lema == "cão"}
    assert "cãos" not in formas_cao
    assert "cães" in formas_cao


def test_substantivo_terminado_em_sao_ou_xao_pluraliza_em_oes():
    # achado real ao pluralizar "progressão" (dentro de composto): a regra
    # só cobria "-ção", "progressão" termina em "-ssão" e caía no "+s"
    # padrão ("progressãos"). "-ção"/"-são"/"-xão" são a mesma classe
    # produtiva (sufixo derivacional, nunca o "-ão" solto e irregular de
    # "mão"/"pão"), todas trocam "-ão" por "-ões" sem exceção conhecida.
    assert _formas_nome("progressão") == {"progressão", "progressões"}
    assert _formas_nome("profissão") == {"profissão", "profissões"}
    assert _formas_nome("conexão") == {"conexão", "conexões"}


def test_substantivo_terminado_em_aiz_pluraliza_com_acento_novo():
    # achado real ao adicionar "raiz" (candidato frequente do corpus,
    # termo central em Matemática -- "raiz quadrada"): a regra genérica
    # de "-z" gerava "raizes", sem acento. Certo: "raízes" -- a sílaba
    # tônica muda de "iz" pra "íz" ao pluralizar, e "a"+"í" tônico forma
    # hiato, sempre marcado. Não é regra geral de todo "-z" -- "matriz"/
    # "cicatriz" (sem vogal antes do "i") continuam sem acento.
    assert _formas_nome("raiz") == {"raiz", "raízes"}
    assert _formas_nome("matriz") == {"matriz", "matrizes"}


def test_substantivo_composto_pluraliza_cabeca_e_modificador():
    # achado real: as 15 entradas compostas do léxico ("sílaba tônica",
    # "tempo verbal" etc.) pluralizavam só a ÚLTIMA palavra ("sílaba
    # tônicas", "tempo verbais") porque `_plural_substantivo` tratava o
    # lema inteiro como palavra única -- só o substantivo-cabeça (primeira
    # palavra) concordava de fato. Corrigido: cabeça E modificador(es)
    # concordam em número.
    assert _formas_nome("sílaba tônica") == {"sílaba tônica", "sílabas tônicas"}
    assert _formas_nome("tempo verbal", Genero.MASCULINO) == {"tempo verbal", "tempos verbais"}
    assert _formas_nome("encontro consonantal", Genero.MASCULINO) == {
        "encontro consonantal",
        "encontros consonantais",
    }


def test_entradas_expandidas_nao_gera_plural_composto_so_na_ultima_palavra():
    entradas = entradas_expandidas()
    formas = {e.forma for e in entradas if e.lema == "sílaba tônica"}
    assert "sílaba tônicas" not in formas
    assert "sílabas tônicas" in formas


def test_dicionario_padrao_inclui_adverbios_mente_gerados():
    # Fase 4 do plano de léxico: gerar_adverbios_mente ligado direto ao
    # dicionário vivo (decisão registada em conversa.md -- definição
    # composta a partir de conteúdo humano do adjetivo-raiz não é
    # fabricação em massa). "natural" já é adjetivo do léxico, então
    # "naturalmente" deve existir sem ter sido escrito à mão em _VERBOS
    # nem _NOMES.
    dicionario = Dicionario.padrao()
    assert "naturalmente" in dicionario
    assert "De modo natural" in dicionario.definir("naturalmente")[0]


def test_dicionario_padrao_nao_inclui_advebio_mente_de_gentilico():
    # achado real: "português"->"portuguêsmente" não é palavra --
    # excluído em gerar_adverbios_mente, nunca chega ao dicionário vivo.
    dicionario = Dicionario.padrao()
    assert "portuguêsmente" not in dicionario


def test_verbo_terminado_em_cer_troca_c_por_c_cedilha_antes_de_a_ou_o():
    # achado real ao adicionar "nascer" como candidato do corpus: a versão
    # anterior gerava "nasco"/"nasca" (não existem em português) em vez de
    # "nasço"/"nasça" -- "c" antes de "a"/"o" precisa virar "ç" pra manter
    # o som /s/ em verbos "-cer"/"-cir".
    formas = {e.forma for e in _verbo("nascer", "x")}
    assert "nasço" in formas
    assert "nasça" in formas
    assert "nasco" not in formas
    assert "nasca" not in formas
    # formas que não ficam antes de "a"/"o" continuam sem alteração.
    assert "nasce" in formas
    assert "nasceu" in formas


def test_verbo_medir_troca_d_por_c_cedilha_antes_de_a_ou_o():
    # achado real ao adicionar "medir" como candidato do corpus: a regra
    # genérica de "-ir" gerava "medo"/"meda"/"medas"/"medamos"/"medam" --
    # nenhuma existe, e "medo" ainda colide com a palavra real "medo"
    # (substantivo, susto). Certo: "meço"/"meça"/"meças"/"meçamos"/
    # "meçam". Diferente de "-cer"/"-cir" (regra geral por sufixo), esta
    # troca é de um conjunto FECHADO de verbos ("medir", "pedir") --
    # "dividir"/"decidir" continuam regulares, sem troca nenhuma.
    formas = {e.forma for e in _verbo("medir", "x")}
    assert "meço" in formas and "medo" not in formas
    assert "meça" in formas and "meda" not in formas
    assert "meçamos" in formas and "meçam" in formas
    assert "medamos" not in formas and "medam" not in formas
    # formas que não ficam antes de "a"/"o" continuam sem alteração.
    assert "mede" in formas and "medimos" in formas
    # "-dir" comum não sofre a troca -- é exceção fechada, não regra geral.
    formas_dividir = {e.forma for e in _verbo("dividir", "x")}
    assert "divido" in formas_dividir and "diço" not in formas_dividir


def test_verbo_perder_troca_d_por_c_sem_cedilha_antes_de_a_ou_o():
    # achado real ao adicionar "perder": a regra genérica de "-er" gerava
    # "perdo"/"perda"/"perdas"/"perdamos"/"perdam" -- nenhuma existe.
    # "perder" troca "d"->"c" (sem cedilha, diferente de "medir"/"pedir")
    # antes de "a"/"o": perco, perca, percas, percamos, percam. Conjunto
    # fechado -- "render"/"vender" continuam regulares, sem troca.
    formas = {e.forma for e in _verbo("perder", "x")}
    assert "perco" in formas and "perdo" not in formas
    assert "perca" in formas and "perda" not in formas
    assert "percamos" in formas and "percam" in formas
    assert "perdamos" not in formas and "perdam" not in formas
    assert "perde" in formas and "perdemos" in formas
    formas_vender = {e.forma for e in _verbo("vender", "x")}
    assert "vendo" in formas_vender and "venco" not in formas_vender


def test_verbo_terminado_em_car_ganha_qu_antes_de_e():
    # achado real, grave por afetar verbo já existente em silêncio:
    # "explicar" (já em `_VERBOS`) media contra o dicionário vivo sem
    # "expliquei"/"explique" -- a regra genérica de "-ar" gerava
    # "explicei"/"explique" com "c" antes de "e" (soaria /s/, errado).
    # Auditoria achou 23 verbos "-car" já no léxico com o mesmo buraco.
    formas = {e.forma for e in _verbo("explicar", "x")}
    assert "expliquei" in formas and "explicei" not in formas
    assert "explique" in formas and "explice" not in formas
    assert "expliquemos" in formas and "expliquem" in formas
    # formas que não ficam antes de "e" continuam sem alteração.
    assert "explica" in formas and "explicamos" in formas
    # "-çar" não entra aqui -- gatilho disjunto de `_corrigir_car_com_cedilha`.
    formas_comecar = {e.forma for e in _verbo("começar", "x")}
    assert "comece" in formas_comecar and "comeque" not in formas_comecar


def test_verbo_terminado_em_gar_ganha_gu_antes_de_e():
    # mesma família fonética do achado acima, consoante diferente:
    # "pagar"/"entregar" geravam "pagei"/"pague" com "g" antes de "e"
    # (soaria /ʒ/, errado). 10 verbos "-gar" já no léxico afetados.
    formas = {e.forma for e in _verbo("pagar", "x")}
    assert "paguei" in formas and "pagei" not in formas
    assert "pague" in formas and "page" not in formas
    assert "paguemos" in formas and "paguem" in formas
    assert "paga" in formas and "pagamos" in formas
    # "entregar" tem particípio irregular "entregue" (ver
    # `_PARTICIPIOS_IRREGULARES`) que coincide na escrita com o
    # subjuntivo "entregue" gerado aqui -- as duas leituras convivem na
    # mesma forma, nenhuma apaga a outra (mesmo mecanismo de "foi").
    entradas_entregar = _verbo("entregar", "x")
    tempos_entregue = {e.atributos.get("tempo") for e in entradas_entregar if e.forma == "entregue"}
    assert "presente do subjuntivo" in tempos_entregue
    assert "particípio" in tempos_entregue


def test_verbo_gera_gerundio_invariavel_por_conjugacao():
    # achado real: candidatos de alta frequência do corpus amplo
    # ("passando", "testando") eram gerúndio de verbos já existentes no
    # léxico, não lema novo -- lacuna de geração de paradigma, não de
    # vocabulário.
    assert "falando" in {e.forma for e in _verbo("falar", "x")}
    assert "comendo" in {e.forma for e in _verbo("comer", "x")}
    assert "partindo" in {e.forma for e in _verbo("partir", "x")}


def test_verbo_gera_participio_regular_com_quatro_formas():
    # achado real: "testado", "validado", "implementado", "usado",
    # "aprovado" eram candidatos a lema novo, mas são particípio de verbos
    # já existentes -- particípio regular flexiona como adjetivo.
    formas = {e.forma: (e.genero, e.numero) for e in _verbo("testar", "x") if e.atributos.get("tempo") == "particípio"}
    assert set(formas) == {"testado", "testada", "testados", "testadas"}
    assert formas["testado"] == (Genero.MASCULINO, Numero.SINGULAR)
    assert formas["testada"] == (Genero.FEMININO, Numero.SINGULAR)
    formas_ir = {e.forma for e in _verbo("partir", "x") if e.atributos.get("tempo") == "particípio"}
    assert formas_ir == {"partido", "partida", "partidos", "partidas"}


def test_participio_de_verbo_cer_nao_indevidamente_alterado():
    # particípio de "-cer"/"-cir" termina em "-ido" (vogal "i"), nunca
    # precisa da troca "c"->"ç" (essa só se aplica antes de "a"/"o").
    formas = {e.forma for e in _verbo("nascer", "x") if e.atributos.get("tempo") == "particípio"}
    assert formas == {"nascido", "nascida", "nascidos", "nascidas"}


def test_verbo_terminado_em_uir_troca_u_por_o_com_acento_no_presente():
    # achado real: "construir" (já no léxico) gerava "construe"/"construes"/
    # "construem" pela regra genérica de "-ir" -- não existem em português.
    # Verbo "-uir" perde o "u" final da raiz nessas 3 pessoas do presente.
    formas = {e.forma for e in _verbo("construir", "x") if e.atributos.get("tempo") == "presente"}
    assert formas == {"construo", "constrói", "constróis", "construímos", "constroem"}
    assert "construe" not in formas and "construes" not in formas and "construem" not in formas


def test_verbo_terminado_em_uir_acentua_hiato_no_i_apos_o_u():
    # achado real: "construi"/"construia"/"construimos"/"construido" não
    # existem -- o "i" logo após o "u" da raiz forma hiato tônico e precisa
    # de acento ("construí"/"construía"/"construímos"/"construído").
    entradas = _verbo("construir", "x")
    formas_por_tempo = {}
    for e in entradas:
        formas_por_tempo.setdefault(e.atributos.get("tempo"), set()).add(e.forma)
    assert "construí" in formas_por_tempo["pretérito perfeito"]
    assert "construía" in formas_por_tempo["pretérito imperfeito"]
    assert "construías" in formas_por_tempo["pretérito imperfeito"]
    assert "construíam" in formas_por_tempo["pretérito imperfeito"]
    assert {"construído", "construída", "construídos", "construídas"} == {
        e.forma for e in entradas if e.atributos.get("tempo") == "particípio"
    }


def test_verbo_uir_preterito_perfeito_1a_plural_acentua_hiato():
    # achado real ao corrigir o pretérito perfeito incompleto (marco dos
    # 50.000, suite inteira): a leitura extra de "nós" no pretérito
    # perfeito quase escapou sem `_corrigir_acento_uir`, gerando
    # "construimos" (sem acento) como STRING DIFERENTE do presente
    # indicativo "construímos" -- quebrava o objetivo de serem a mesma
    # forma com duas leituras. Corrigido: as duas leituras têm que
    # compartilhar a mesma string acentuada.
    entradas = _verbo("construir", "x")
    formas_construimos = [e for e in entradas if e.forma in {"construímos", "construimos"}]
    assert {e.forma for e in formas_construimos} == {"construímos"}
    tempos = {e.atributos.get("tempo") for e in formas_construimos}
    assert tempos == {"presente", "pretérito perfeito"}


def test_verbo_terminado_em_uir_nao_acentua_ditongo_iu_nem_gerundio():
    # "-iu" (pretérito perfeito 3ª singular) e "-indo" (gerúndio) são
    # ditongo, não hiato -- continuam sem acento ("construiu",
    # "construindo"), diferente de "construiu" virar "construíu" (errado).
    formas = {e.forma for e in _verbo("construir", "x")}
    assert "construiu" in formas and "construíu" not in formas
    assert "construindo" in formas and "construíndo" not in formas


def test_infinitivo_de_verbo_uir_nao_e_alterado():
    # o próprio infinitivo ("construir") não pode ganhar acento por engano
    # -- só as formas conjugadas com "i" logo após o "u" da raiz mudam.
    formas = {e.forma for e in _verbo("construir", "x") if e.atributos == {}}
    assert formas == {"construir"}


def test_verbo_terminado_em_uir_tu_do_imperativo_usa_a_forma_irregular():
    # imperativo "tu" deriva do presente 3ª singular irregular -- "constrói",
    # nunca "construe".
    imperativos = {e.forma for e in _verbo("construir", "x") if e.atributos.get("tempo") == "imperativo afirmativo"}
    assert "constrói" in imperativos
    assert "construe" not in imperativos


def test_verbo_terminado_em_guir_nao_e_tratado_como_uir_vocalico():
    # achado real, bug introduzido e corrigido na mesma sessão: aplicar a
    # regra vocálica de "-uir" (construir) às cegas em "distinguir" (já no
    # léxico) gerava "distingoem"/"distingói"/"distinguí" -- nenhuma real.
    # "-guir" tem "u" mudo (dígrafo "gu"), nunca vogal em hiato.
    formas = {e.forma for e in _verbo("distinguir", "x")}
    assert "distingue" in formas and "distinguímos" not in formas
    assert "distinguiu" in formas
    assert not any(f.startswith("distingo") and f != "distingo" for f in formas)
    assert "distingói" not in formas and "distingoem" not in formas and "distinguí" not in formas


def test_verbo_terminado_em_guir_perde_u_antes_de_a_ou_o():
    # achado real: "distinguir" gerava "distinguo"/"distingua"/"distinguas"/
    # "distinguamos"/"distinguam" -- o "u" do dígrafo "gu" precisa cair
    # antes de "a"/"o" (senão soaria /gw/, não /g/): "distingo", "distinga".
    formas = {e.forma for e in _verbo("distinguir", "x")}
    assert "distingo" in formas and "distinguo" not in formas
    assert "distinga" in formas and "distingua" not in formas
    assert "distingamos" in formas and "distinguamos" not in formas
    assert "distingam" in formas and "distinguam" not in formas
    # antes de "e"/"i" o "u" continua (som /g/ já preservado sem ele).
    assert "distingue" in formas and "distinguimos" in formas


def test_verbo_uir_vocalico_nao_struir_fica_regular_sem_troca_de_o():
    # achado real, checado ANTES de generalizar a troca de raiz "ó" (que
    # é certa pra "construir"/"destruir") pra outros candidatos "-uir":
    # "substituir" NÃO troca de raiz -- "substitue"/"substitui" e
    # "substituo"/"substituis"/"substitui"/"substituímos"/"substituem"
    # são as formas certas, nunca "substitóis"/"substitói". A família
    # com troca "ó" é exclusiva de "-struir" (etimologia latina
    # "struere" compartilhada por construir/destruir/instruir).
    formas = {e.forma for e in _verbo("substituir", "x") if e.atributos.get("tempo") == "presente"}
    assert formas == {"substituo", "substituis", "substitui", "substituímos", "substituem"}
    assert "substitói" not in formas and "substitóis" not in formas


def test_verbo_uir_vocalico_presente_3a_e_preterito_1a_sao_distintos():
    # achado real, bug que eu mesmo quase introduzi: a 3ª singular do
    # presente ("substitui", sem acento) e a 1ª singular do pretérito
    # perfeito ("substituí", com acento) usam a MESMA raiz + "i" antes da
    # correção de acento -- se a troca de presente rodasse antes do
    # acento de hiato, as duas colidiriam na mesma chave de dicionário e
    # uma leitura seria perdida. As duas têm que sobreviver, distintas.
    entradas = _verbo("substituir", "x")
    presente_3sg = {
        e.forma for e in entradas
        if e.atributos.get("tempo") == "presente" and e.pessoa == Pessoa.TERCEIRA and e.numero == Numero.SINGULAR
    }
    preterito_1sg = {
        e.forma for e in entradas
        if e.atributos.get("tempo") == "pretérito perfeito" and e.pessoa == Pessoa.PRIMEIRA and e.numero == Numero.SINGULAR
    }
    assert presente_3sg == {"substitui"}
    assert preterito_1sg == {"substituí"}


def test_verbo_terminado_em_zir_perde_vogal_na_3a_singular_presente():
    # achado real ao adicionar "produzir": a regra genérica de "-ir"
    # gerava "produze" (3ª singular do presente) -- não existe, o certo
    # é "produz", sem vogal temática nenhuma. Regra produtiva pra toda a
    # classe "-zir" (reduzir, traduzir, conduzir, induzir, deduzir).
    formas = {e.forma for e in _verbo("produzir", "x")}
    assert "produz" in formas and "produze" not in formas
    # demais pessoas do presente continuam regulares.
    assert "produzo" in formas and "produzes" in formas and "produzimos" in formas


def test_verbo_terminado_em_erir_troca_e_por_i_na_1a_singular_e_subjuntivo():
    # achado real ao adicionar "conferir": a regra genérica de "-ir"
    # gerava "confero"/"confera"/"conferas"/"conferamos"/"conferam" --
    # nenhuma existe. "-erir" (conferir, preferir, referir, sugerir,
    # ferir, gerir, aderir) troca "e"->"i" na 1ª singular do presente e
    # em todo o subjuntivo presente: confiro, confira, confiras,
    # confiramos, confiram.
    formas = {e.forma for e in _verbo("conferir", "x")}
    assert "confiro" in formas and "confero" not in formas
    assert "confira" in formas and "confera" not in formas
    assert "confiras" in formas and "confiramos" in formas and "confiram" in formas
    assert "conferas" not in formas and "conferamos" not in formas and "conferam" not in formas
    # demais pessoas do presente (2ª/3ª singular, plurais) continuam com "e".
    assert "conferes" in formas and "confere" in formas and "conferimos" in formas


def test_verbo_cobrir_troca_o_por_u_na_1a_singular_e_subjuntivo():
    # achado real ao adicionar "cobrir": a regra genérica de "-ir" gerava
    # "cobro"/"cobra"/"cobras"/"cobramos"/"cobram" -- nenhuma existe.
    # "cobrir" (exceção fechada, não sufixo geral) troca "o"->"u" na 1ª
    # singular do presente e em todo o subjuntivo: cubro, cubra, cubras,
    # cubramos, cubram.
    formas = {e.forma for e in _verbo("cobrir", "x")}
    assert "cubro" in formas and "cobro" not in formas
    assert "cubra" in formas and "cobra" not in formas
    assert "cubras" in formas and "cubramos" in formas and "cubram" in formas
    # demais pessoas do presente continuam com "o".
    assert "cobres" in formas and "cobre" in formas and "cobrimos" in formas


def test_verbo_seguir_troca_e_por_i_e_simplifica_gu_ao_mesmo_tempo():
    # achado real ao adicionar "seguir": mesmo depois de `_corrigir_guir`
    # (que já tira o "u" mudo do "gu" antes de "a"/"o") a regra gerava
    # "sego"/"sega"/"segas"/"segamos"/"segam" -- ainda erradas. "seguir"
    # empilha DUAS trocas na mesma forma: "e"->"i" (mesma classe de
    # "-erir") E o "gu"->"g" (mesma classe de "distinguir"), resultando
    # em "sigo"/"siga"/"sigas"/"sigamos"/"sigam" -- nunca "segu"+algo.
    formas = {e.forma for e in _verbo("seguir", "x")}
    assert "sigo" in formas and "sego" not in formas and "seguo" not in formas
    assert "siga" in formas and "sega" not in formas
    assert "sigas" in formas and "sigamos" in formas and "sigam" in formas
    # demais pessoas do presente continuam regulares, com "gu".
    assert "segues" in formas and "segue" in formas and "seguimos" in formas


def test_verbo_terminado_em_ear_insere_i_nas_pessoas_tonicas():
    # achado real ao adicionar "nomear": a regra genérica de "-ar" gerava
    # "nomeo"/"nomea"/"nomeas"/"nomeam" (presente) e "nomee"/"nomees"/
    # "nomeem" (subjuntivo) -- nenhuma existe. "-ear" (nomear, passear,
    # folhear, bloquear, recear) insere "i" nas pessoas tônicas: nomeio,
    # nomeias, nomeia, nomeiam / nomeie, nomeies, nomeiem.
    formas = {e.forma for e in _verbo("nomear", "x")}
    assert {"nomeio", "nomeias", "nomeia", "nomeiam"} <= formas
    assert {"nomeo", "nomea", "nomeas", "nomeam"}.isdisjoint(formas)
    assert {"nomeie", "nomeies", "nomeiem"} <= formas
    assert {"nomee", "nomees", "nomeem"}.isdisjoint(formas)
    # 1ª plural (indicativo E subjuntivo) fica sem "i" -- tônica no sufixo.
    assert "nomeamos" in formas and "nomeemos" in formas
    assert "nomeiamos" not in formas and "nomeiemos" not in formas


def test_verbo_com_particip_irregular_nao_usa_regra_ado_ido():
    # achado real ao adicionar "escrever"/"abrir": particípio irregular
    # ("escrito", "aberto") não segue "-ido"/"-ado" nenhum -- se a regra
    # genérica rodasse, geraria "escrevido"/"abrido", que não existem.
    formas_escrever = {e.forma for e in _verbo("escrever", "x") if e.atributos.get("tempo") == "particípio"}
    assert formas_escrever == {"escrito", "escrita", "escritos", "escritas"}
    formas_abrir = {e.forma for e in _verbo("abrir", "x") if e.atributos.get("tempo") == "particípio"}
    assert formas_abrir == {"aberto", "aberta", "abertos", "abertas"}
    # gerúndio continua regular nos dois (o irregular é só o particípio).
    assert "escrevendo" in {e.forma for e in _verbo("escrever", "x")}
    assert "abrindo" in {e.forma for e in _verbo("abrir", "x")}


def test_verbo_reunir_acentua_hiato_interno_so_nas_pessoas_tonicas():
    # achado real ao investigar candidato "reúne": a regra genérica de
    # "-ir" gerava "reune"/"reuno"/"reunem", sem acento -- errados. O
    # prefixo "re-" cria hiato tônico dentro da raiz ("re-ú-ne"), marcado
    # só onde a sílaba da raiz é tônica (singular + 3ª plural), nunca em
    # 1ª plural ("reunimos"/"reunamos", tônica no sufixo).
    formas = {e.forma for e in _verbo("reunir", "x")}
    assert {"reúno", "reúnes", "reúne", "reúnem"} <= formas
    assert {"reuno", "reune", "reunem"}.isdisjoint(formas)
    assert {"reúna", "reúnas", "reúnam"} <= formas
    # 1ª plural NUNCA leva acento -- sílaba tônica é o sufixo, não a raiz.
    assert "reunimos" in formas and "reunamos" in formas
    assert "reúnimos" not in formas and "reúnamos" not in formas


def _dicionario_base_sem_palavras_funcionais() -> Dicionario:
    """Léxico vivo (JSON + nomes/adjetivos/verbos), sem `_PALAVRAS_FUNCIONAIS`
    -- baseline real para achar colisão, não um dicionário vazio."""
    caminho = files("lingua_portuguesa.dados").joinpath("lexico_base.json")
    with caminho.open("r", encoding="utf-8") as arquivo:
        base = Dicionario._de_dados(json.load(arquivo))
    for lema, genero, definicao in _NOMES:
        for entrada in _forma_nome(lema, genero, definicao):
            base.adicionar(entrada)
    for lema, definicao in _ADJETIVOS:
        for entrada in _forma_adj(lema, definicao):
            base.adicionar(entrada)
    for infinitivo, definicao in _VERBOS:
        for entrada in _verbo(infinitivo, definicao):
            base.adicionar(entrada)
    return base


def test_palavras_funcionais_nao_duplicam_lexico_ja_existente():
    # achado real: um primeiro lote incluiu "eu"/"e"/"muito"/"do"/"com" etc.
    # que já existiam em lexico_base.json com a mesma classe -- removidos.
    # Este teste vira o guarda permanente contra repetir o mesmo erro.
    base = _dicionario_base_sem_palavras_funcionais()
    colisoes = [
        (entrada.forma, entrada.classe.value)
        for entrada in _PALAVRAS_FUNCIONAIS
        if any(existente.classe == entrada.classe for existente in base.buscar(entrada.forma))
    ]
    assert colisoes == []


def test_palavras_funcionais_sem_duplicata_interna():
    chaves = [(entrada.forma, entrada.classe) for entrada in _PALAVRAS_FUNCIONAIS]
    assert len(chaves) == len(set(chaves))


def test_palavras_funcionais_nao_tem_lema_e_forma_trocados():
    # achado real: um lote de plurais/gênero (teus/tuas/estas/mesma/toda...)
    # foi escrito com EntradaLexical(forma, lema, ...) em vez de
    # EntradaLexical(lema, forma, ...) -- a forma inflectida virava "lema"
    # e o radical base virava "forma", quebrando a busca real ("tuas" não
    # existia no dicionário, "teu" aparecia com forma="teu" quatro vezes).
    # Nenhuma entrada aqui deve ter `forma` mais longa que `lema` sem que
    # `forma` comece pelo prefixo do próprio `lema` OU seja igual a ele --
    # sinal simples e real de troca de argumento.
    # "teu"/"tua" e "seu"/"sua" são exceções genuínas (não compartilham
    # prefixo -- "e" vs "u" na 2ª letra), diferente de este/esta, esse/essa,
    # aquele/aquela (esses sim compartilham prefixo).
    excecoes_irregulares = {
        ("teu", "tua"), ("teu", "tuas"),
        ("seu", "sua"), ("seu", "suas"),
    }
    suspeitas = [
        e for e in _PALAVRAS_FUNCIONAIS
        if e.forma != e.lema
        and not e.forma.startswith(e.lema[:3])
        and (e.lema, e.forma) not in excecoes_irregulares
    ]
    assert suspeitas == []


@pytest.mark.parametrize(
    "forma",
    ["teus", "tuas", "seus", "suas", "nossos", "nossas", "estes", "estas",
     "esses", "essas", "aqueles", "aquelas", "alguma", "alguns", "algumas",
     "nenhuma", "toda", "todos", "todas", "outra", "outros", "outras",
     "mesma", "mesmos", "mesmas", "quais", "quanta", "quantos", "quantas"],
)
def test_forma_flexionada_de_palavra_funcional_esta_no_dicionario(forma):
    assert forma in Dicionario.padrao()


def test_palavra_polissemica_mantem_mais_de_uma_classe():
    dicionario = Dicionario.padrao()
    classes_que = {entrada.classe for entrada in dicionario.buscar("que")}
    assert ClasseGramatical.CONJUNCAO in classes_que
    assert ClasseGramatical.PRONOME in classes_que

    classes_mesmo = {entrada.classe for entrada in dicionario.buscar("mesmo")}
    assert {ClasseGramatical.ADJETIVO, ClasseGramatical.PRONOME, ClasseGramatical.ADVERBIO} <= classes_mesmo


def test_contracao_plural_nova_esta_no_dicionario_vivo():
    dicionario = Dicionario.padrao()
    for forma in ("dos", "das", "nos", "nas", "pelo", "pela", "numa", "nesta"):
        assert forma in dicionario


def test_conceito_puro_ganha_plural_gerado_pela_mesma_regra():
    # achado real ao investigar candidatos de alta frequência ("leituras",
    # "critérios", "eventos"): os conceitos de `conhecimento_puro.py` sem
    # entrada manual em `_NOMES` nunca ganhavam plural nenhum -- só a
    # forma singular era registada. Corrigido em massa, reaproveitando a
    # MESMA regra já testada (`_plural_substantivo`/`_plural_composto`),
    # não uma palavra nova.
    entradas = entradas_expandidas()
    formas = {e.forma for e in entradas}
    assert "leituras" in formas
    assert "critérios" in formas
    assert "eventos" in formas
    assert "sonoridades fonológicas" in formas


def test_plural_de_conceito_e_seguro_recusa_composto_com_preposicao_ou_nao():
    # achado real ao medir antes de aplicar em massa: "adjunto adverbial
    # de tempo" (preposição), "símbolo não alfabético" ("não" invariável)
    # e "reconstrução linguística PSF" (sigla maiúscula) quebrariam com a
    # regra de composto ("des tempos"/"nãos alfabéticos"/"PSFs") -- ficam
    # de fora, sem plural gerado, em vez de arriscar forma fabricada.
    assert not _plural_de_conceito_e_seguro("adjunto adverbial de tempo")
    assert not _plural_de_conceito_e_seguro("símbolo não alfabético")
    assert not _plural_de_conceito_e_seguro("reconstrução linguística PSF")
    # os casos simples (substantivo + adjetivo, sem função gramatical no
    # meio) continuam seguros.
    assert _plural_de_conceito_e_seguro("sonoridade fonológica")
    assert _plural_de_conceito_e_seguro("contexto")


def test_entradas_expandidas_nao_gera_plural_arriscado_de_conceito():
    entradas = entradas_expandidas()
    formas = {e.forma for e in entradas}
    assert "des tempos" not in formas
    assert "nãos alfabéticos" not in formas
    assert "PSFs" not in formas


def test_plural_substantivo_ol_ul():
    from lingua_portuguesa.lexico_expansao import _plural_substantivo
    assert _plural_substantivo("farol") == "faróis"
    assert _plural_substantivo("anzol") == "anzóis"
    assert _plural_substantivo("azul") == "azuis"

