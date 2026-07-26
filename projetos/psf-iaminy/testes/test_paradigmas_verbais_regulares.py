"""Item real do README ("materializar paradigmas regulares e irregulares
de flexão e conjugação") -- estende `_verbo()` (lexico_expansao.py) do
presente/pretérito perfeito parcial para também cobrir pretérito
imperfeito, futuro do presente, presente do subjuntivo, pretérito
imperfeito do subjuntivo, futuro do subjuntivo, pretérito
mais-que-perfeito, futuro do pretérito (condicional), imperativo
afirmativo, infinitivo pessoal e imperativo negativo, cada forma
etiquetada com seu próprio tempo (campo `atributos["tempo"]`, mesma
convenção já usada pelos 11 verbos irregulares em `lexico_base.json`).
Corte deliberadamente estreito: só verbos regulares, só estes 12 tempos
-- verbos irregulares além dos 11 já existentes continuam de fora.

Infinitivo pessoal reaproveita 100% das strings do futuro do subjuntivo
já corrigido (mesma base histórica, leitura adicional, nenhuma forma
nova). Imperativo negativo ("não fales"/"não fale"/"não falemos"/"não
falem") reaproveita 100% do presente do subjuntivo já existente em
`formas`, em toda pessoa -- ao contrário do afirmativo, que usa o
presente indicativo na 2ª singular ("tu"). Nenhum dos dois introduz
vocabulário novo; ambos só tornam explícita, com etiqueta própria, uma
leitura que a língua real já tem.

Achado ao construir o imperativo afirmativo: ele não introduz nenhuma
string nova -- "tu" reaproveita a forma do presente indicativo 3ª
singular, "você"/"nós"/"vocês" reaproveitam o presente do subjuntivo.
Por isso um mapa ingênuo `{forma: entrada}` (como os testes abaixo já
usavam antes desta mudança) perde uma das duas leituras quando a mesma
string carrega tempo/pessoa diferentes -- os testes que precisam de
uma forma ambígua agora filtram por tempo explicitamente, em vez de
assumir forma↔entrada 1:1.
"""
from lingua_portuguesa.tipos import Numero, Pessoa
from lingua_portuguesa.lexico_expansao import entradas_expandidas, _verbo


def _mapa(lema):
    return {e.forma: e for e in entradas_expandidas() if e.lema == lema}


def _por_tempo(infinitivo, forma, tempo):
    """A mesma `forma` pode carregar mais de uma leitura (ex.: imperativo
    reaproveitando subjuntivo) -- escolhe a leitura do tempo pedido."""
    candidatas = [e for e in _verbo(infinitivo, "x") if e.forma == forma and e.atributos.get("tempo") == tempo]
    assert len(candidatas) == 1, f"esperava 1 leitura de {forma!r} em {tempo!r}, achei {len(candidatas)}"
    return candidatas[0]


def test_preterito_imperfeito_verbo_ar_novo_via_geracao():
    # "conversar" só existe via _verbo() (lexico_expansao.py), não no
    # JSON base -- prova que o imperfeito vem da geração, não de dado
    # já pronto.
    formas = _mapa("conversar")
    # 1ª e 3ª singular têm a mesma superfície: eu/ele conversava.
    assert formas["conversava"].pessoa is None
    assert formas["conversava"].numero == Numero.SINGULAR
    assert formas["conversava"].atributos["tempo"] == "pretérito imperfeito"
    assert formas["conversávamos"].pessoa == Pessoa.PRIMEIRA
    assert formas["conversávamos"].numero == Numero.PLURAL
    assert formas["conversavam"].pessoa == Pessoa.TERCEIRA
    assert formas["conversavam"].numero == Numero.PLURAL


def test_futuro_do_presente_mesmo_sufixo_nas_tres_conjugacoes():
    for infinitivo, raiz_futuro in (("estudar", "estudar"), ("comer", "comer"), ("partir", "partir")):
        formas = _verbo(infinitivo, "x")
        por_forma = {f.forma: f for f in formas}
        assert por_forma[raiz_futuro + "ei"].atributos["tempo"] == "futuro do presente"
        assert por_forma[raiz_futuro + "ei"].pessoa == Pessoa.PRIMEIRA
        assert por_forma[raiz_futuro + "ei"].numero == Numero.SINGULAR
        assert por_forma[raiz_futuro + "ão"].pessoa == Pessoa.TERCEIRA
        assert por_forma[raiz_futuro + "ão"].numero == Numero.PLURAL


def test_imperfeito_er_e_ir_usa_mesmo_sufixo_ia():
    comer = {f.forma: f for f in _verbo("comer", "x")}
    partir = {f.forma: f for f in _verbo("partir", "x")}
    assert comer["comia"].atributos["tempo"] == "pretérito imperfeito"
    assert partir["partia"].atributos["tempo"] == "pretérito imperfeito"
    assert comer["comíamos"].numero == Numero.PLURAL
    assert partir["partíamos"].numero == Numero.PLURAL


def test_presente_e_preterito_perfeito_continuam_etiquetados_com_tempo():
    # Achado ao estender: antes desta mudança, _verbo() não etiquetava
    # tempo nenhum para presente/pretérito perfeito (só pessoa/número) --
    # agora todos os tempos gerados carregam o mesmo atributo, evitando
    # que presente/perfeito fiquem "sem tempo" enquanto imperfeito/futuro
    # têm.
    formas = {f.forma: f for f in _verbo("estudar", "x")}
    assert formas["estudo"].atributos["tempo"] == "presente"
    assert formas["estudei"].atributos["tempo"] == "pretérito perfeito"
    # "estudar" agora tem DUAS leituras (infinitivo puro E futuro do
    # subjuntivo, mesma string -- ver achado no docstring de `_verbo`) --
    # um mapa ingênuo pega a última, por isso filtra explicitamente pela
    # leitura sem tempo nenhum.
    infinitivo_puro = [f for f in _verbo("estudar", "x") if f.forma == "estudar" and f.atributos == {}]
    assert len(infinitivo_puro) == 1


def test_preterito_perfeito_tem_as_cinco_pessoas():
    # Achado real ao rodar a suite inteira (marco dos 50.000): pretérito
    # perfeito só gerava 1ª/3ª singular ("estudei"/"estudou") -- faltava
    # "tu"/"nós"/"eles" em TODO verbo regular já no léxico, não só nos
    # novos. "nós" reaproveita a mesma string do presente indicativo 1ª
    # plural nas três conjugações (estudamos/comemos/partimos servem pra
    # presente E pretérito perfeito em português real).
    for infinitivo, esperado in [
        ("estudar", {"estudei", "estudaste", "estudou", "estudamos", "estudaram"}),
        ("comer", {"comi", "comeste", "comeu", "comemos", "comeram"}),
        ("partir", {"parti", "partiste", "partiu", "partimos", "partiram"}),
    ]:
        formas = {f.forma for f in _verbo(infinitivo, "x") if f.atributos.get("tempo") == "pretérito perfeito"}
        assert formas == esperado


def test_preterito_perfeito_1a_plural_e_leitura_extra_do_presente():
    # "estudamos" tem DUAS leituras reais (presente indicativo E pretérito
    # perfeito, mesma string) -- nenhuma pode sobrescrever a outra.
    entradas = [f for f in _verbo("estudar", "x") if f.forma == "estudamos"]
    tempos = {f.atributos.get("tempo") for f in entradas}
    assert tempos == {"presente", "pretérito perfeito"}
    assert all(f.pessoa is not None and f.pessoa.value == "primeira" for f in entradas)


def _por_forma_e_tempo(infinitivo, forma, tempo):
    """Localiza a leitura de `forma` com o `tempo` pedido -- algumas
    formas (ex. "estude") têm duas leituras (subjuntivo e imperativo),
    então um mapa ingênuo `{forma: entrada}` perderia uma delas."""
    candidatas = [f for f in _verbo(infinitivo, "x") if f.forma == forma and f.atributos.get("tempo") == tempo]
    assert len(candidatas) == 1, f"esperava 1 leitura de {forma!r} com tempo={tempo!r}, achei {len(candidatas)}"
    return candidatas[0]


def test_nenhuma_forma_gerada_perde_leitura_por_colisao_de_string():
    # Formas que _parecem_ repetidas (ex. "estuda" é presente indicativo
    # 3ª singular E imperativo "tu") são leituras DIFERENTES, cada uma
    # com seu próprio tempo -- nenhuma pode desaparecer silenciosamente.
    # Total esperado por verbo regular: 25 formas sem repetição de string
    # (presente/perfeito/imperfeito/futuro/subjuntivo/condicional) + 4
    # leituras extra de imperativo que reaproveitam strings já existentes
    # ("tu"=presente 3ª sg, "você"/"nós"/"vocês"=subjuntivo) + 5 formas
    # nominais (gerúndio invariável + particípio em 4 formas de gênero/
    # número, achado real ao medir candidatos de alta frequência do
    # corpus -- "testado"/"passando" eram particípio/gerúndio de verbos
    # já existentes, não lema novo) + 3 formas de pretérito perfeito
    # (achado real ao rodar a suite inteira no marco dos 50.000: só 1ª/3ª
    # singular existiam, faltava 2ª singular "tu" e 3ª plural "eles"
    # -- strings novas, direto em `formas` -- e 1ª plural "nós", que
    # reaproveita a MESMA string do presente indicativo 1ª plural nas
    # três conjugações -- "estudamos"/"comemos"/"partimos" servem pra
    # presente E pretérito perfeito em português real, leitura extra,
    # mesmo mecanismo do imperativo) = 37. Achado real, auditoria
    # sistemática (pretérito imperfeito do subjuntivo e futuro do
    # subjuntivo nunca existiam em NENHUM verbo regular): +4 formas de
    # imperfeito do subjuntivo direto em `formas` (strings novas, sem
    # colisão) + 4 leituras extra de futuro do subjuntivo (1ª/3ª singular
    # reaproveita a string do próprio infinitivo, mesmo mecanismo do
    # imperativo/pretérito 1ª plural; 2ª singular/1ª/3ª plural são
    # strings novas) = 37 + 8 = 45. Mesmo achado, pretérito
    # mais-que-perfeito (conceito 467, "a forma simples... permanece"
    # sem construção nenhuma): +3 formas novas direto em `formas` (1ª/3ª
    # singular ambígua, 2ª singular, 1ª plural) + 1 leitura extra de 3ª
    # plural (reaproveita a MESMA string do pretérito perfeito 3ª plural
    # -- "falaram" serve às duas leituras) = 45 + 4 = 49. Depois, dois
    # tempos que só reetiquetam strings já existentes, sem gerar nenhuma
    # nova: +4 leituras extra de infinitivo pessoal (reaproveita 100% do
    # futuro do subjuntivo já corrigido) + 4 leituras extra de imperativo
    # negativo (reaproveita 100% do presente do subjuntivo já existente,
    # em toda pessoa) = 49 + 8 = 57.
    for infinitivo in ("estudar", "comer", "partir"):
        assert len(_verbo(infinitivo, "x")) == 57


def test_subjuntivo_presente_ambiguo_1a_3a_pessoa_singular():
    # "que eu fale" / "que ele fale" são a mesma forma na língua real --
    # pessoa=None em vez de fingir uma pessoa única, mesmo critério já
    # usado para "quis"/"soube"/"disse" no pretérito dos irregulares.
    for infinitivo, forma_ambigua in (("estudar", "estude"), ("comer", "coma"), ("partir", "parta")):
        entrada = _por_forma_e_tempo(infinitivo, forma_ambigua, "presente do subjuntivo")
        assert entrada.pessoa is None
        assert entrada.numero == Numero.SINGULAR


def test_subjuntivo_presente_er_ir_usa_mesma_vogal_a():
    comer_amos = _por_forma_e_tempo("comer", "comamos", "presente do subjuntivo")
    partir_amos = _por_forma_e_tempo("partir", "partamos", "presente do subjuntivo")
    assert comer_amos.pessoa == Pessoa.PRIMEIRA
    assert partir_amos.pessoa == Pessoa.PRIMEIRA
    comer_am = _por_forma_e_tempo("comer", "comam", "presente do subjuntivo")
    partir_am = _por_forma_e_tempo("partir", "partam", "presente do subjuntivo")
    assert comer_am.pessoa == Pessoa.TERCEIRA
    assert partir_am.pessoa == Pessoa.TERCEIRA


def test_imperativo_afirmativo_tu_reaproveita_presente_indicativo():
    # "tu" no imperativo é a MESMA string do presente indicativo 3ª
    # singular ("fala"/"come"/"parte") -- leitura adicional, não troca.
    for infinitivo, forma_tu in (("estudar", "estuda"), ("comer", "come"), ("partir", "parte")):
        indicativo = _por_forma_e_tempo(infinitivo, forma_tu, "presente")
        imperativo = _por_forma_e_tempo(infinitivo, forma_tu, "imperativo afirmativo")
        assert indicativo.pessoa == Pessoa.TERCEIRA
        assert imperativo.pessoa == Pessoa.SEGUNDA
        assert imperativo.numero == Numero.SINGULAR


def test_condicional_futuro_do_preterito_mesmo_sufixo_nas_tres_conjugacoes():
    for infinitivo in ("estudar", "comer", "partir"):
        formas = {f.forma: f for f in _verbo(infinitivo, "x")}
        forma_1a3a = formas[infinitivo + "ia"]
        assert forma_1a3a.pessoa is None
        assert forma_1a3a.atributos["tempo"] == "futuro do pretérito"
        assert formas[infinitivo + "íamos"].pessoa == Pessoa.PRIMEIRA
        assert formas[infinitivo + "íamos"].numero == Numero.PLURAL


def test_verbo_air_vocalico_presente_e_preterito_perfeito():
    # Achado real registado em conversa.md ("sair"/"cair" quebravam quase
    # o paradigma inteiro contra o gerador genérico de "-ir") -- raiz
    # "sa"/"ca" precisa reganhar o "i" que a vogal temática genérica
    # apaga, com acento de hiato tônico onde o "i" é sílaba própria (e
    # SEM acento onde "ai" continua ditongo: "saiu", "saindo").
    for infinitivo, esperado_presente, esperado_perfeito in [
        ("sair", {"saio", "sais", "sai", "saímos", "saem"}, {"saí", "saíste", "saiu", "saímos", "saíram"}),
        ("cair", {"caio", "cais", "cai", "caímos", "caem"}, {"caí", "caíste", "caiu", "caímos", "caíram"}),
    ]:
        entradas = _verbo(infinitivo, "x")
        presente = {f.forma for f in entradas if f.atributos.get("tempo") == "presente"}
        perfeito = {f.forma for f in entradas if f.atributos.get("tempo") == "pretérito perfeito"}
        assert presente == esperado_presente
        assert perfeito == esperado_perfeito


def test_verbo_air_vocalico_subjuntivo_sem_acento_diferente_do_imperfeito_acentuado():
    # "saiam" (subjuntivo, ditongo átono) e "saíam" (pretérito imperfeito,
    # hiato tônico) são formas REAIS diferentes -- se a ordem das
    # correções em `_verbo` estivesse errada, uma delas apagaria a outra
    # silenciosamente (mesma classe de bug já pega por
    # `test_nenhuma_forma_gerada_perde_leitura_por_colisao_de_string`).
    entradas = _verbo("sair", "x")
    por_forma_e_tempo = {(f.forma, f.atributos.get("tempo")) for f in entradas}
    assert ("saiam", "presente do subjuntivo") in por_forma_e_tempo
    assert ("saíam", "pretérito imperfeito") in por_forma_e_tempo
    assert "saiam" != "saíam"


def test_verbo_air_vocalico_particip_e_gerundio():
    entradas = _verbo("cair", "x")
    nominais = {f.forma: f.atributos.get("tempo") for f in entradas if f.atributos.get("tempo") in ("gerúndio", "particípio")}
    assert nominais["caindo"] == "gerúndio"
    assert nominais["caído"] == "particípio"
    assert nominais["caída"] == "particípio"
    assert nominais["caídos"] == "particípio"
    assert nominais["caídas"] == "particípio"


def test_verbo_air_vocalico_nenhuma_leitura_perdida_por_colisao():
    for infinitivo in ("sair", "cair"):
        assert len(_verbo(infinitivo, "x")) == 57


def test_preterito_imperfeito_do_subjuntivo_nas_tres_conjugacoes():
    # achado real, auditoria sistemática: "se eu falasse"/"comesse"/
    # "partisse" nunca existiam em NENHUM dos 397+ verbos regulares --
    # lacuna sistémica, não um verbo isolado. 1ª/3ª singular ambíguas
    # (mesmo critério de sempre); "-ássemos"/"-êssemos"/"-íssemos" são
    # sempre proparoxítonas (regra geral de acentuação), levam acento em
    # TODO verbo desta conjugação, sem exceção.
    for infinitivo, esperado in [
        ("estudar", {"estudasse", "estudasses", "estudássemos", "estudassem"}),
        ("comer", {"comesse", "comesses", "comêssemos", "comessem"}),
        ("partir", {"partisse", "partisses", "partíssemos", "partissem"}),
    ]:
        formas = {f.forma for f in _verbo(infinitivo, "x") if f.atributos.get("tempo") == "pretérito imperfeito do subjuntivo"}
        assert formas == esperado
    ambigua = _por_forma_e_tempo("estudar", "estudasse", "pretérito imperfeito do subjuntivo")
    assert ambigua.pessoa is None


def test_futuro_do_subjuntivo_singular_reaproveita_o_infinitivo():
    # achado real: futuro do subjuntivo 1ª/3ª singular é SEMPRE idêntico
    # ao infinitivo ("quando eu FALAR"/"COMER"/"PARTIR") -- leitura
    # adicional pra uma forma que já existe, mesmo mecanismo do
    # imperativo e do pretérito 1ª plural, nunca sobrescreve a leitura
    # pura do infinitivo (ver `test_presente_e_preterito_perfeito_
    # continuam_etiquetados_com_tempo`).
    for infinitivo, esperado in [
        ("estudar", {"estudar", "estudares", "estudarmos", "estudarem"}),
        ("comer", {"comer", "comeres", "comermos", "comerem"}),
        ("partir", {"partir", "partires", "partirmos", "partirem"}),
    ]:
        formas = {f.forma for f in _verbo(infinitivo, "x") if f.atributos.get("tempo") == "futuro do subjuntivo"}
        assert formas == esperado
    ambiguo = _por_forma_e_tempo("estudar", "estudar", "futuro do subjuntivo")
    assert ambiguo.pessoa is None


def test_futuro_do_subjuntivo_hiato_so_fora_da_1a_plural_em_air_e_uir():
    # achado real, conferido contra "sair"/"construir" antes de
    # generalizar: 2ª singular/3ª plural levam acento de hiato tônico
    # ("saíres"/"saírem", "construíres"/"construírem") mas a 1ª plural
    # NÃO ("sairmos"/"construirmos") -- a sílaba tônica aí é o próprio
    # "-ir-" final, não um hiato isolado. Verbo "-guir"/"-quir"
    # (dígrafo "u" mudo, não vocálico) não leva acento nenhum.
    for infinitivo, esperado in [
        ("sair", {"sair", "saíres", "sairmos", "saírem"}),
        ("construir", {"construir", "construíres", "construirmos", "construírem"}),
        ("seguir", {"seguir", "seguires", "seguirmos", "seguirem"}),
    ]:
        formas = {f.forma for f in _verbo(infinitivo, "x") if f.atributos.get("tempo") == "futuro do subjuntivo"}
        assert formas == esperado


def test_preterito_mais_que_perfeito_nas_tres_conjugacoes():
    # achado real: conceito 467 do conhecimento puro já registava
    # "quando cheguei, ele já partira" como exemplo, e a nota "a forma
    # simples... permanece" -- mas nenhum verbo regular tinha essa forma
    # construída. 1ª/3ª singular ambígua ("falara" = eu falara ou ele
    # falara); 3ª plural é a MESMA string do pretérito perfeito
    # ("falaram" serve às duas leituras).
    for infinitivo, esperado in [
        ("estudar", {"estudara", "estudaras", "estudáramos", "estudaram"}),
        ("comer", {"comera", "comeras", "comêramos", "comeram"}),
        ("partir", {"partira", "partiras", "partíramos", "partiram"}),
    ]:
        formas = {f.forma for f in _verbo(infinitivo, "x") if f.atributos.get("tempo") == "pretérito mais-que-perfeito"}
        assert formas == esperado
    ambigua = _por_forma_e_tempo("estudar", "estudara", "pretérito mais-que-perfeito")
    assert ambigua.pessoa is None
    perfeito = _por_forma_e_tempo("estudar", "estudaram", "pretérito perfeito")
    mqp = _por_forma_e_tempo("estudar", "estudaram", "pretérito mais-que-perfeito")
    assert perfeito.pessoa == mqp.pessoa == Pessoa.TERCEIRA


def test_preterito_mais_que_perfeito_air_vocalico_mantem_acento_do_perfeito():
    # a 3ª plural do mais-que-perfeito precisa reaproveitar EXATAMENTE a
    # mesma grafia acentuada já usada pelo pretérito perfeito ("saíram"),
    # nunca uma versão sem acento gerada à parte.
    formas = {f.forma for f in _verbo("sair", "x") if f.atributos.get("tempo") == "pretérito mais-que-perfeito"}
    assert formas == {"saíra", "saíras", "saíramos", "saíram"}


def test_infinitivo_pessoal_reaproveita_exatamente_o_futuro_do_subjuntivo():
    # "para eu/tu/ele FALAR/FALARES/FALAR" -- mesma base histórica do
    # futuro do subjuntivo, mesmas 4 strings, só etiqueta diferente.
    for infinitivo in ("estudar", "comer", "partir", "sair", "construir"):
        entradas = _verbo(infinitivo, "x")
        futuro_subj = {f.forma for f in entradas if f.atributos.get("tempo") == "futuro do subjuntivo"}
        inf_pessoal = {f.forma for f in entradas if f.atributos.get("tempo") == "infinitivo pessoal"}
        assert inf_pessoal == futuro_subj
    ambiguo = _por_forma_e_tempo("estudar", "estudar", "infinitivo pessoal")
    assert ambiguo.pessoa is None
    plural = _por_forma_e_tempo("comer", "comermos", "infinitivo pessoal")
    assert plural.pessoa == Pessoa.PRIMEIRA
    assert plural.numero == Numero.PLURAL


def test_imperativo_negativo_reaproveita_subjuntivo_em_toda_pessoa():
    # "não fales"/"não fale"/"não falemos"/"não falem" -- ao contrário do
    # afirmativo, a 2ª singular ("tu") também vem do subjuntivo, não do
    # presente indicativo.
    for infinitivo, esperado in [
        ("estudar", {"estude", "estudes", "estudemos", "estudem"}),
        ("comer", {"coma", "comas", "comamos", "comam"}),
        ("partir", {"parta", "partas", "partamos", "partam"}),
    ]:
        entradas = _verbo(infinitivo, "x")
        negativo = {f.forma for f in entradas if f.atributos.get("tempo") == "imperativo negativo"}
        assert negativo == esperado
    tu_negativo = _por_forma_e_tempo("estudar", "estudes", "imperativo negativo")
    assert tu_negativo.pessoa == Pessoa.SEGUNDA
    assert tu_negativo.numero == Numero.SINGULAR
    ambiguo = _por_forma_e_tempo("comer", "coma", "imperativo negativo")
    assert ambiguo.pessoa is None


def test_estrutura_do_portugues_continua_sem_lacuna_apos_a_extensao():
    from lingua_portuguesa import MotorPortugues

    motor = MotorPortugues()
    auditoria = motor.auditar_estrutura_portugues()
    assert len(auditoria.nomes_duplicados) == 0
    assert len(auditoria.dependencias_ausentes) == 0
