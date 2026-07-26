"""Expansão interna do léxico português do PSF-IAminy.

Não é um dicionário externo importado. É uma semente grande, auditável e
extensível, escrita em código simples para o motor reconhecer pedidos naturais,
termos de estudo, linguagem técnica, matemática e conversa humana.
"""
from __future__ import annotations

from .tipos import ClasseGramatical, EntradaLexical, Genero, Numero, Pessoa
from .conhecimento_puro import ALIASES_CONCEITOS_PORTUGUES, CONCEITOS_PORTUGUES_PURO


_VOGAIS_ACENTUADAS = "áéíóúâêôãõà"

# Achado real ao preparar "cão" como candidato: a classe "-ão" fora de
# "-ção"/"-são"/"-xão" não tem regra fonética confiável -- "mão"->"mãos",
# "pão"->"pães", "cão"->"cães" são três padrões diferentes pra terminação
# igual, só memorização lexical resolve. Lista pequena e explícita (nunca
# heurística de sufixo, que erraria as outras duas classes): só entra
# palavra que o léxico realmente precisa, uma de cada vez, conferida.
_PLURAIS_AO_IRREGULARES: dict[str, str] = {"cão": "cães", "mão": "mãos", "pão": "pães"}


def _plural_substantivo(lema: str) -> str:
    """Achado real ao adicionar candidatos do corpus ("intenção",
    "construção", "validação" já existentes geravam "intençãos" etc., forma
    que não existe em português): substantivo terminado em "-ção" pluraliza
    em "-ções" (nunca "+s") -- sub-padrão de "-ão" quase sem exceção. O
    restante da classe "-ão" (mão -> mãos, pão -> pães, irmão -> irmãos) é
    genuinamente irregular e fica de fora por ora, não coberto às cegas.

    Segundo achado real, mesmo padrão de erro ("item" já existente gerava
    "items"): substantivo terminado em "-m" pluraliza trocando "m" por
    "ns" (item -> itens, som -> sons, linguagem -> linguagens, contagem ->
    contagens), nunca "+s".

    Terceiro achado real, encontrado ao adicionar "anel" como candidato:
    substantivo terminado em "-l" já tinha SEIS palavras erradas no léxico
    antes desta correção ("nível"->"nívels", "vogal"->"vogals", "radical"->
    "radicals", "numeral"->"numerals", "plural"->"plurals", "anel"->
    "anels") porque a função não tratava "-l" nenhuma, só caía no "+s"
    padrão. "-al" pluraliza em "-ais" sempre (vogal->vogais, radical->
    radicais, nunca leva acento novo -- o ditongo "ai" não marca em
    português). "-el" depende de onde já está o acento no lema: se o lema
    JÁ tem uma vogal acentuada em outra sílaba (ex.: "nível", acento em
    "í"), a sílaba tônica não muda ao pluralizar, então só cai o "l" e
    entra "is" (nível->níveis, o "í" já existente carrega o plural). Se o
    lema NÃO tem acento nenhum (ex.: "anel", "papel", "hotel" -- sílaba
    tônica é a própria "-el" final, regra padrão pra terminação em "l"),
    pluralizar exige acento NOVO porque "e" tônico final antes de "s" leva
    acento em português (anel->anéis, papel->papéis, hotel->hotéis). "-ol"/
    "-ul"/"-il" (farol->faróis, azul->azuis, fácil->fáceis vs. funil->
    funis, mesma família mas com sub-regras próprias) ficam de fora por
    ora -- nenhuma palavra do léxico usa essas terminações ainda, não
    coberto às cegas.

    Quarto achado real, encontrado ao pluralizar "progressão" dentro de
    um composto ("progressão temática"): a regra só cobria "-ção", mas
    "progressão" termina em "-ssão", não "-ção" -- caía no "+s" padrão e
    virava "progressãos". "-ção"/"-são"/"-xão" são a mesma classe
    produtiva (sufixo derivacional real, não o "-ão" solto e irregular de
    "mão"/"pão"/"irmão" já excluído acima): todas trocam "-ão" final por
    "-ões" sem exceção conhecida (nação->nações, profissão->profissões,
    conexão->conexões). Generalizado pra cobrir as três.

    Quinto achado real, ao adicionar "raiz" como candidato do corpus
    (frequência alta -- "raiz quadrada"/"raízes de uma equação" são termos
    centrais em Matemática): a regra genérica de "-z" gerava "raizes",
    sem acento -- errado. "raiz" pluraliza com acento NOVO em "í"
    (raiz->raízes) porque a sílaba tônica muda de "iz" (final) pra "íz"
    (agora penúltima) ao entrar "-es", e "a"+"í" tônico forma hiato, que
    é sempre marcado em português (mesma regra geral de acento de hiato
    já usada pra verbos "-uir", agora vista num substantivo). Não é regra
    geral de todo "-z" (matriz->matrizes, cicatriz->cicatrizes continuam
    sem acento -- ali "i" não segue outra vogal, não há hiato).

    Sexto achado real, ao preparar "cão": resto da classe "-ão" (fora de
    "-ção"/"-são"/"-xão") não tem regra fonética única -- "cão"/"mão"/
    "pão" são genuinamente irregulares, resolvidos por exceção lexical
    explícita (ver `_PLURAIS_AO_IRREGULARES`), conferida palavra por
    palavra, nunca por adivinhação de sufixo.

    Sétimo achado real, ao adicionar "padrão"/"razão"/"união" (já no
    léxico, geravam "padrãos"/"razãos"/"uniãos" -- a regra caía direto no
    "+s" genérico por não ter nenhum tratamento pra "-ão" solto): "-ões"
    é o padrão PRODUTIVO/majoritário pra substantivo terminado em "-ão"
    (nação, botão, cordão, feijão e a maioria da classe), não a exceção
    -- vira o fallback depois do dicionário de exceções (que continua
    resolvendo os poucos casos genuinamente diferentes, tipo "cão")."""
    if lema in _PLURAIS_AO_IRREGULARES:
        return _PLURAIS_AO_IRREGULARES[lema]
    if lema.endswith(("ção", "são", "xão")):
        return lema[:-2] + "ões"
    if lema.endswith("m"):
        return lema[:-1] + "ns"
    if lema.endswith("aiz"):
        return lema[:-2] + "ízes"
    if lema.endswith(("r", "z")):
        return lema + "es"
    if lema.endswith("il"):
        # Achado real ao adicionar "perfil": a regra genérica de "-l" caía
        # no "+s" ("perfils", que não existe). Substantivo terminado em
        # "-il" tônico (perfil, funil, barril, fuzil) troca "l" por "s"
        # (sem acento novo, diferente de "-el"): perfil->perfis,
        # funil->funis. Não cobre "-il" átono de adjetivo (fácil->fáceis,
        # difícil->difíceis) -- essa família tem sub-regra própria em
        # `_forma_adj`, nenhum substantivo do léxico usa esse padrão ainda.
        return lema[:-1] + "s"
    if lema.endswith("al"):
        return lema[:-1] + "is"
    if lema.endswith("el"):
        if any(vogal in lema for vogal in _VOGAIS_ACENTUADAS):
            return lema[:-1] + "is"
        return lema[:-2] + "éis"
    if lema.endswith("ol"):
        if any(vogal in lema for vogal in _VOGAIS_ACENTUADAS):
            return lema[:-1] + "is"
        return lema[:-2] + "óis"
    if lema.endswith("ul"):
        return lema[:-1] + "is"
    if lema.endswith("ão"):
        return lema[:-2] + "ões"
    return lema + "s"



def _pluralizar_modificador(palavra: str) -> str:
    """Pluraliza um adjetivo que já está na forma de gênero certa dentro
    de um nome composto (ex.: "tônica" em "sílaba tônica") -- não precisa
    gerar as 4 formas de `_forma_adj` (o gênero já está fixado pelo
    substantivo-cabeça), só concordar em número com as mesmas regras
    produtivas já usadas em `_forma_adj`/`_plural_substantivo`."""
    if palavra.endswith(("al", "vel", "ul")):
        return palavra[:-1] + "is"
    if palavra.endswith("el"):
        if any(vogal in palavra for vogal in _VOGAIS_ACENTUADAS):
            return palavra[:-1] + "is"
        return palavra[:-2] + "éis"
    if palavra.endswith("r"):
        return palavra + "es"
    if palavra.endswith("z"):
        return palavra + "es"
    if palavra.endswith("s"):
        return palavra
    return palavra + "s"


def _plural_composto(lema: str) -> str:
    """Achado real ao medir os compostos já existentes ("sílaba tônica",
    "tempo verbal", "encontro consonantal" etc.): `_plural_substantivo`
    aplicado ao lema inteiro só flexionava a ÚLTIMA palavra ("sílaba
    tônicas", "encontro consonantais") -- as 15 entradas compostas do
    léxico estavam TODAS erradas, porque só o substantivo-cabeça (a
    primeira palavra) concorda em número real, e o(s) modificador(es)
    seguintes precisam concordar também ("sílabas tônicas", "tempos
    verbais"), não só o final da frase inteira."""
    cabeca, *modificadores = lema.split(" ")
    partes = [_plural_substantivo(cabeca)] + [_pluralizar_modificador(m) for m in modificadores]
    return " ".join(partes)


def _forma_nome(lema: str, genero: Genero, definicao: str) -> list[EntradaLexical]:
    entradas = [
        EntradaLexical(lema, lema, ClasseGramatical.SUBSTANTIVO, (definicao,), genero, Numero.SINGULAR)
    ]
    if not lema.endswith("s"):
        plural = _plural_composto(lema) if " " in lema else _plural_substantivo(lema)
        entradas.append(
            EntradaLexical(lema, plural, ClasseGramatical.SUBSTANTIVO, (definicao,), genero, Numero.PLURAL)
        )
    return entradas


def _forma_adj(lema: str, definicao: str) -> list[EntradaLexical]:
    """Regra achada quebrada ao adicionar candidatos reais do corpus ("real",
    "natural" já existentes geravam plural "reals"/"naturals", formas que não
    existem em português): adjetivo terminado em "-al" pluraliza em "-ais"
    (real -> reais, natural -> naturais, nominal -> nominais), nunca "+s".
    A terminação "-el" distingue lemas já acentuados dos não acentuados
    (móvel -> móveis; fiel -> fiéis); "-ul" segue a troca de "l" por "is".

    Segundo achado real, encontrado ao preparar candidato "posterior":
    SEIS adjetivos terminados em "-r" já existentes ("modular", "linear",
    "maior", "anterior", "menor", "regular") geravam plural errado
    ("modulars", "maiors" etc.) porque a função nunca tratou "-r" -- caía
    no "+s" padrão. Mesma regra que `_plural_substantivo` já usa pra
    substantivo (professor->professores): "-r" pluraliza em "-es"
    (modular->modulares, maior->maiores, anterior->anteriores).

    Terceiro achado real, ao investigar candidato "geradora" (freq. alta
    no corpus): "gerador" (já no léxico como adjetivo, "elemento
    gerador"/"conjunto gerador") caía na regra genérica de "-r" e só
    gerava "gerador"/"geradores" -- sem a forma feminina. Diferente dos
    "-r" comuns (regular/maior/anterior, que são de dois gêneros,
    INVARIÁVEIS), adjetivo agentivo em "-dor" flexiona em gênero como os
    terminados em "-o": geradora, geradoras.

    Quarto achado real, ao preparar candidato "possível": "variável" e
    "compatível" (já no léxico) geravam "variávels"/"compatívels" --
    não existem em português. Adjetivo terminado em "-vel" pluraliza
    igual ao "-al" (mesma troca "cai o 'l', entra 'is'"): variável ->
    variáveis, possível -> possíveis, nunca "+s".

    Quinto achado real, ao investigar candidato "comuns": "comum" (já no
    léxico) gerava "comums" -- não existe. Mesma troca "-m"->"-ns" que
    `_plural_substantivo` já usa pra substantivo (item->itens), nunca
    aplicada a adjetivo.

    Sexto achado real, ao preparar candidato "capaz": nenhuma regra tratava
    "-z" -- caía no "+s" genérico ("capazs", que não existe). "feliz" já
    no léxico escapava disto por vir pronto do JSON (`lexico_base.json`),
    não desta função -- mas qualquer "-z" novo entrando por aqui quebraria.
    Mesma família do "-r" (também some o "s" cru, ganha "-es"): capaz ->
    capazes, feliz -> felizes, veloz -> velozes.

    Sétimo achado real, ao adicionar "promissor": caiu no "-r" genérico
    (INVARIÁVEL, mesma classe de "regular"/"maior") e ficou sem "promissora"
    -- errado, "promissor" é agentivo como "gerador" (mesmo sufixo latino
    "-tor"/"-sor"/"-dor", só o alomorfe muda conforme a consoante anterior:
    emissor/emissora, professor/professora), não um "-r" comum. "-sor"
    entra no mesmo braço de "-dor" -- confirmado que nenhum outro "-sor" já
    no léxico é invariável (não há contraexemplo ainda medido)."""
    formas: list[tuple[str, Genero, Numero]]
    if lema.endswith("o"):
        formas = [
            (lema, Genero.MASCULINO, Numero.SINGULAR),
            (lema[:-1] + "a", Genero.FEMININO, Numero.SINGULAR),
            (lema[:-1] + "os", Genero.MASCULINO, Numero.PLURAL),
            (lema[:-1] + "as", Genero.FEMININO, Numero.PLURAL),
        ]
    elif lema.endswith(("dor", "sor")):
        formas = [
            (lema, Genero.MASCULINO, Numero.SINGULAR),
            (lema + "a", Genero.FEMININO, Numero.SINGULAR),
            (lema + "es", Genero.MASCULINO, Numero.PLURAL),
            (lema + "as", Genero.FEMININO, Numero.PLURAL),
        ]
    else:
        if lema.endswith(("al", "vel", "ul")):
            # Nono achado real, ao preparar candidato "azul": "-ul" caía
            # no "+s" genérico ("azuls", que não existe). Mesma troca de
            # "-al" (cai o "l", entra "is"): azul->azuis.
            plural = lema[:-1] + "is"
        elif lema.endswith("el"):
            # Décimo achado real: "fiel" caía no "+s" genérico ("fiels").
            # Sem acento anterior, o plural recebe "éis"; com acento já
            # marcado, conserva-o e apenas troca "l" por "is".
            plural = (
                lema[:-1] + "is"
                if any(vogal in lema for vogal in _VOGAIS_ACENTUADAS)
                else lema[:-2] + "éis"
            )
        elif lema.endswith("il"):
            # Oitavo achado real, ao preparar candidato "útil": nenhuma
            # regra tratava "-il" -- caía no "+s" genérico ("útils", que
            # não existe). Adjetivo terminado em "-il" ÁTONO troca "-il"
            # por "-eis" (útil->úteis, fácil->fáceis). O padrão tônico,
            # tipo "civil"->"civis", não ocorre no léxico atual.
            plural = lema[:-2] + "eis"
        elif lema.endswith("m"):
            plural = lema[:-1] + "ns"
        elif lema.endswith(("r", "z")):
            plural = lema + "es"
        elif lema.endswith("s"):
            plural = lema
        else:
            plural = lema + "s"
        # Adjetivos sem flexão de género continuam precisando de duas
        # leituras de número. Se a superfície for invariável ("simples"),
        # ambas são preservadas em vez de colapsadas num conjunto de formas.
        formas = [
            (lema, Genero.COMUM, Numero.SINGULAR),
            (plural, Genero.COMUM, Numero.PLURAL),
        ]
    return [
        EntradaLexical(
            lema,
            forma,
            ClasseGramatical.ADJETIVO,
            (definicao,),
            genero,
            numero,
        )
        for forma, genero, numero in sorted(
            formas,
            key=lambda item: (item[0], item[1].value, item[2].value),
        )
    ]


def _corrigir_ortografia_raiz(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao adicionar "nascer" como candidato do corpus: verbo
    terminado em "-cer"/"-cir" gerava "nasco"/"nasca" em vez de
    "nasço"/"nasça" -- português preserva o som de "c" (=/s/) trocando por
    "ç" sempre que a próxima vogal é "a" ou "o" (senão "c" soaria /k/).
    Mesma disciplina já usada para os plurais em "-al"/"-ção"."""
    if not infinitivo.endswith(("cer", "cir")):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("a", "o"):
            forma = raiz[:-1] + "ç" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_car_com_cedilha(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao medir "começar" (já no léxico): infinitivo terminado
    em "-çar" tem raiz já com cedilha ("começ"), correta antes de "a"/"o"
    ("começo"/"começa") mas ERRADA antes de "e"/"i" (subjuntivo "começe",
    pretérito perfeito 1sg "começei") -- cedilha nunca aparece antes de
    "e"/"i" em português (o "c" simples já soa /s/ ali, sem precisar do
    sinal). Caso inverso de `_corrigir_ortografia_raiz` (c->ç antes de
    "a"/"o"): aqui é ç->c antes de "e"/"i"."""
    if not infinitivo.endswith("çar"):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("e", "i"):
            forma = raiz[:-1] + "c" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_car_com_qu(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real, grave por afetar verbo já existente em silêncio: medi
    "explicar" (já em `_VERBOS` havia sessões) contra o dicionário vivo e
    "expliquei"/"explique"/"expliquemos"/"expliquem" não existiam --
    a regra genérica de "-ar" gera "explicei"/"explique" com "c" antes de
    "e", que soaria /s/ em vez de /k/. Verbo terminado em "-car" (não
    "-çar", ver `_corrigir_car_com_cedilha`, gatilho disjunto) troca
    "c"->"qu" antes de "e" -- mesma família fonética de `_corrigir_
    ortografia_raiz` (c->ç antes de a/o) e `_corrigir_guir` (some "u"
    mudo antes de a/o), aqui é o inverso: GANHA "u" mudo antes de "e" pra
    preservar o som /k/. Auditoria rápida achou 23 verbos já no léxico
    com este mesmo buraco (marcar, aplicar, trocar, ficar, colocar
    etc.) -- corrigido pra todos de uma vez, não só pro que achei
    primeiro."""
    if not infinitivo.endswith("car") or infinitivo.endswith("çar"):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] == "e":
            forma = raiz[:-1] + "qu" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_gar_com_gu(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Mesma família fonética de `_corrigir_car_com_qu`, consoante
    diferente: verbo terminado em "-gar" (pagar, entregar, jogar, chegar,
    ligar, negar, apagar) gera "pagei"/"pague" com "g" antes de "e" na
    regra genérica -- soaria /ʒ/ em vez de /g/. Ganha "u" mudo antes de
    "e": paguei, pague, paguemos, paguem. Achado na mesma auditoria que
    achou o buraco de "-car" -- 10 verbos já no léxico afetados (negar,
    ligar, chegar, apagar, investigar, legar, carregar, entre outros)."""
    if not infinitivo.endswith("gar"):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] == "e":
            forma = raiz[:-1] + "gu" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_ger_gir_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao investigar candidato "dirigir": a regra genérica
    gerava "dirigo"/"dirigamos" -- não existem em português. Verbo
    terminado em "-ger"/"-gir" (dirigir, fingir, exigir, surgir, eleger,
    proteger) troca "g"->"j" na raiz sempre que a próxima vogal é "a" ou
    "o" (senão "g" soaria /g/ em vez de /ʒ/) -- mesmo gatilho de
    `_corrigir_ortografia_raiz` (c->ç), troca de letra diferente. As
    demais pessoas (diriges/dirige/dirigimos/dirigem, já com "e"/"i"
    depois do "g") continuam regulares, sem troca -- não é sufixo "-guir"
    (seguir, distinguir: "gu" é dígrafo com "u" mudo, regra própria já
    em `_corrigir_guir`, disjunta desta)."""
    if not infinitivo.endswith(("ger", "gir")):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("a", "o"):
            forma = raiz[:-1] + "j" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


# Achado real ao adicionar "medir" como candidato do corpus: a regra
# genérica de "-ir" gerava "medo"/"meda"/"medas"/"medamos"/"medam" -- não
# só não existem em português como "medo" colide com a palavra real
# "medo" (substantivo, "medo" = susto). O certo é "meço"/"meça"/"meças"/
# "meçamos"/"meçam". Diferente de "-cer"/"-cir" (regra produtiva, vale
# pra QUALQUER verbo com essa terminação), esta troca "d"->"ç" NÃO é
# geral pra "-dir" (dividir->divido, decidir->decido continuam
# regulares) -- é irregularidade fechada de um punhado de verbos
# específicos ("medir", "pedir"), por isso o conjunto é enumerado, nunca
# por sufixo.
_VERBOS_DIR_COM_ALTERNANCIA = frozenset({"medir", "pedir"})

# Achado real ao adicionar "escrever": particípio irregular não segue
# "-ado"/"-ido" nenhum, é exceção lexical fechada (um punhado de verbos
# comuns), nunca sufixo -- só a forma masculina singular precisa ficar
# registada aqui, o resto do paradigma (feminino/plural) é regular a
# partir dela (ver uso em `_verbo`).
_PARTICIPIOS_IRREGULARES: dict[str, str] = {
    "escrever": "escrito",
    "descrever": "descrito",
    "abrir": "aberto",
    "cobrir": "coberto",
    "ganhar": "ganho",
    # Achado real (conversa.md): mais 6 verbos comuns com particípio
    # irregular ÚNICO (não duplo -- diferente de "aceitar", que tem
    # "aceitado"/"aceito" os dois válidos e por isso fica de fora daqui).
    # Conferido contra o oráculo hunspell (só diagnóstico) + conhecimento
    # próprio: nenhuma forma regular ("pagado"/"entregado"/"morrido"/
    # "gastado"/"prendido"/"suspendido") é palavra real.
    "pagar": "pago",
    "entregar": "entregue",
    "morrer": "morto",
    "gastar": "gasto",
    "prender": "preso",
    "suspender": "suspenso",
    # Achado real (conversa.md): "reabrir" ficou de fora junto de "obter"
    # como pendente -- composto de "abrir", herda o mesmo particípio
    # irregular com o prefixo colado (reaberto, não "reabrido").
    "reabrir": "reaberto",
}


def _corrigir_dir_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_VERBOS_DIR_COM_ALTERNANCIA`: troca "d"->"ç" na raiz antes de
    "a"/"o", mesmo gatilho de `_corrigir_ortografia_raiz` (c->ç), conjunto
    fechado em vez de sufixo porque a maioria dos "-dir" é regular."""
    if infinitivo not in _VERBOS_DIR_COM_ALTERNANCIA:
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("a", "o"):
            forma = raiz[:-1] + "ç" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


# Achado real ao adicionar "perder": a regra genérica de "-er" gerava
# "perdo"/"perda"/"perdas"/"perdamos"/"perdam" -- não existem em
# português. Conjunto fechado (não sufixo geral -- "render"/"vender" não
# trocam): "perder" troca "d"->"c" (sem cedilha, diferente de
# "-dir"/"_corrigir_dir_alternancia") antes de "a"/"o": perco, perca,
# percas, percamos, percam.
_VERBOS_DER_COM_ALTERNANCIA = frozenset({"perder"})


def _corrigir_der_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_VERBOS_DER_COM_ALTERNANCIA`."""
    if infinitivo not in _VERBOS_DER_COM_ALTERNANCIA:
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("a", "o"):
            forma = raiz[:-1] + "c" + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_zir(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao adicionar "produzir": a regra genérica de "-ir"
    gerava "produze" (3ª singular do presente) -- não existe, o certo é
    "produz", sem vogal temática nenhuma. Verbos "-zir" (produzir,
    reduzir, traduzir, conduzir, induzir, deduzir) perdem o "e" final
    nessa única forma -- regra produtiva pra toda a classe, sem exceção
    conhecida (diferente de "dizer", que é "-zer" e já vem irregular
    completo do JSON)."""
    if not infinitivo.endswith("zir"):
        return formas
    forma_errada = raiz + "e"
    if forma_errada not in formas:
        return formas
    corrigidas = dict(formas)
    corrigidas[raiz] = corrigidas.pop(forma_errada)
    return corrigidas


_VERBOS_ERIR_COM_ALTERNANCIA_E_I = ("erir",)


def _corrigir_erir_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao adicionar "conferir": a regra genérica de "-ir"
    gerava "confero"/"confera"/"conferas"/"conferamos"/"conferam" -- não
    existem em português. Verbo terminado em "-erir" (conferir, preferir,
    referir, sugerir, ferir, gerir, aderir, digerir) troca o "e" da raiz
    por "i" na 1ª singular do presente e em TODO o subjuntivo presente
    (confiro, confira, confiras, confiramos, confiram) -- regra produtiva
    pra toda a classe. As demais pessoas do presente (conferes/confere/
    conferimos/conferem) continuam regulares, sem troca."""
    if not infinitivo.endswith(_VERBOS_ERIR_COM_ALTERNANCIA_E_I):
        return formas
    raiz_com_i = raiz[:-2] + "ir"
    substituicoes = {
        raiz + "o": raiz_com_i + "o",
        raiz + "a": raiz_com_i + "a",
        raiz + "as": raiz_com_i + "as",
        raiz + "amos": raiz_com_i + "amos",
        raiz + "am": raiz_com_i + "am",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in formas.items()}


# Achado real ao adicionar "cobrir": a regra genérica de "-ir" gerava
# "cobro"/"cobra"/"cobras"/"cobramos"/"cobram" -- não existem em
# português. Fechado (não sufixo geral: "abrir" não troca, "cobre" ->
# não vira "cubre"), mesma disciplina de `_VERBOS_DIR_COM_ALTERNANCIA`.
_VERBOS_O_U_ALTERNANCIA = frozenset({"cobrir", "descobrir"})

# Achado real ao adicionar "seguir": mesmo depois de `_corrigir_guir`
# (que já tira o "u" mudo do dígrafo "gu" antes de "a"/"o") a regra
# gerava "sego"/"sega"/"segas"/"segamos"/"segam" -- ainda erradas. Além
# do "gu"->"g", "seguir" (e compostos) troca "e"->"i" na 1ª singular do
# presente e em todo o subjuntivo, empilhando as duas trocas na mesma
# forma: sigo, siga, sigas, sigamos, sigam (nunca "sego"/"segu"+algo).
_VERBOS_EGUIR_ALTERNANCIA = frozenset({"seguir", "conseguir", "perseguir", "prosseguir"})


def _corrigir_eguir_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_VERBOS_EGUIR_ALTERNANCIA`: raiz termina em "egu" (seguir ->
    "segu"); a forma corrigida troca esse "egu" final por "ig" (segu ->
    sig, consegu -> consig), aplicada só onde `_corrigir_guir` também se
    aplicaria (1ª singular presente + todo o subjuntivo)."""
    if infinitivo not in _VERBOS_EGUIR_ALTERNANCIA:
        return formas
    raiz_com_i = raiz[:-3] + "ig"
    substituicoes = {
        raiz + "o": raiz_com_i + "o",
        raiz + "a": raiz_com_i + "a",
        raiz + "as": raiz_com_i + "as",
        raiz + "amos": raiz_com_i + "amos",
        raiz + "am": raiz_com_i + "am",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in formas.items()}


def _corrigir_ear_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao adicionar "nomear": a regra genérica de "-ar" gerava
    "nomeo"/"nomea"/"nomeas"/"nomeam" (presente) e "nomee"/"nomees"/
    "nomeem" (subjuntivo) -- nenhuma existe. Verbo terminado em "-ear"
    (nomear, passear, folhear, bloquear, recear -- classe produtiva, sem
    exceção conhecida) insere "i" antes da vogal temática em toda pessoa
    ONDE ESSA SÍLABA É TÔNICA: presente 1ª/2ª/3ª singular e 3ª plural
    (nomeio, nomeias, nomeia, nomeiam) e o mesmo no subjuntivo (nomeie,
    nomeies, nomeiem). A 1ª pessoa do plural, nas duas formas
    (nomeamos/nomeemos), é tônica no próprio sufixo -- continua sem "i",
    diferente da alternância "-erir"/"o-u" (que é troca categórica de
    vogal, vale pra TODO o subjuntivo; aqui é inserção condicionada à
    sílaba tônica, então "-amos"/"-emos" ficam de fora)."""
    if not infinitivo.endswith("ear"):
        return formas
    substituicoes = {
        raiz + "o": raiz + "io",
        raiz + "as": raiz + "ias",
        raiz + "a": raiz + "ia",
        raiz + "am": raiz + "iam",
        raiz + "e": raiz + "ie",
        raiz + "es": raiz + "ies",
        raiz + "em": raiz + "iem",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in formas.items()}


def _corrigir_o_u_alternancia(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_VERBOS_O_U_ALTERNANCIA`: troca "o"->"u" na raiz na 1ª
    singular do presente e em todo o subjuntivo presente (cubro, cubra,
    cubras, cubramos, cubram) -- mesmo gatilho de `_corrigir_erir_alternancia`
    (e->i), troca de vogal diferente."""
    if infinitivo not in _VERBOS_O_U_ALTERNANCIA:
        return formas
    # troca o último "o" da raiz por "u" (cobr -> cubr): o "o" tônico não
    # é necessariamente a última letra, então a troca é pela direita.
    raiz_com_u = raiz[::-1].replace("o", "u", 1)[::-1]
    if raiz == raiz_com_u:
        return formas
    substituicoes = {
        raiz + "o": raiz_com_u + "o",
        raiz + "a": raiz_com_u + "a",
        raiz + "as": raiz_com_u + "as",
        raiz + "amos": raiz_com_u + "amos",
        raiz + "am": raiz_com_u + "am",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in formas.items()}


# Achado real ao adicionar "reunir" (já no léxico, "reúne" era candidato
# frequente): a regra genérica de "-ir" gerava "reune"/"reuno"/"reunem"
# sem acento -- errados. Diferente do hiato de "-uir" (entre a raiz e o
# sufixo), aqui é o prefixo "re-" que cria hiato tônico dentro da própria
# raiz ("re-ú-ne"), marcado só nas pessoas onde a sílaba da raiz é
# tônica (1ª/2ª/3ª singular e 3ª plural, presente e subjuntivo) -- NUNCA
# em 1ª plural ("reunimos"/"reunamos"), onde a sílaba tônica é o próprio
# sufixo. Fechado por palavra (não sufixo geral: "punir" não faz isto).
_VERBOS_ACENTO_HIATO_INTERNO: dict[str, str] = {"reunir": "reún"}


def _corrigir_acento_hiato_interno(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_VERBOS_ACENTO_HIATO_INTERNO`."""
    raiz_acentuada = _VERBOS_ACENTO_HIATO_INTERNO.get(infinitivo)
    if raiz_acentuada is None:
        return formas
    substituicoes = {
        raiz + "o": raiz_acentuada + "o",
        raiz + "es": raiz_acentuada + "es",
        raiz + "e": raiz_acentuada + "e",
        raiz + "em": raiz_acentuada + "em",
        raiz + "a": raiz_acentuada + "a",
        raiz + "as": raiz_acentuada + "as",
        raiz + "am": raiz_acentuada + "am",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in formas.items()}


def _corrigir_guir(formas: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao medir "distinguir" (já no léxico) contra o gerador
    regular de "-ir": produzia "distinguo"/"distingua"/"distinguas"/
    "distinguamos"/"distinguam" -- nenhuma existe em português. Verbo
    terminado em "-guir" (distinguir, seguir, conseguir, perseguir,
    prosseguir, extinguir) marca o som /g/ com um "u" mudo antes de
    "e"/"i" ("distingue", "distinguimos", sem mudança) mas PERDE esse "u"
    antes de "a"/"o" -- senão soaria /gw/ em vez de /g/: "distingo",
    "distinga". Mesma disciplina de `_corrigir_ortografia_raiz`
    (c->ç antes de "a"/"o"), troca diferente, mesmo gatilho."""
    if not infinitivo.endswith("guir"):
        return formas
    corrigidas = {}
    for forma, dado in formas.items():
        if forma.startswith(raiz) and forma[len(raiz):len(raiz) + 1] in ("a", "o"):
            forma = raiz[:-1] + forma[len(raiz):]
        corrigidas[forma] = dado
    return corrigidas


def _e_verbo_uir_vocalico(infinitivo: str) -> bool:
    """"-uir" só é a classe vocálica (precisa de acento de hiato -- ver
    `_corrigir_acento_uir`) quando o "u" não faz parte do dígrafo "gu"/
    "qu" (distinguir, seguir, conseguir, extinguir -- aí o "u" é mudo, só
    marca o som /g/ antes de "i", e o verbo NÃO muda de raiz nem ganha
    acento de hiato). Achado real ao medir "distinguir" (já no léxico): a
    regra vocálica aplicada às cegas gerava "distingoem"/"distingói"/
    "distinguí", nenhuma delas real. Vale para TODO "-uir" vocálico
    (construir, substituir, atribuir, possuir, distribuir, diminuir,
    concluir, incluir) -- diferente da troca de raiz "ó" (ver
    `_e_verbo_struir_com_o_o`), que é mais restrita."""
    return infinitivo.endswith("uir") and not infinitivo.endswith(("guir", "quir"))


def _e_verbo_struir_com_o_o(infinitivo: str) -> bool:
    """A troca de raiz "u"->"ó" no presente ("constrÓi", "destrÓi") NÃO é
    regra geral de todo "-uir" vocálico -- achado ao verificar com
    cuidado antes de generalizar de "construir" pra outros candidatos
    ("substituir" na lista de candidatos frequentes): "substituir",
    "atribuir", "distribuir", "possuir", "diminuir", "concluir",
    "incluir" são regulares no presente (substituo/substituis/substitui/
    substituímos/substituem, SEM "ó"), só precisando do acento de hiato
    (`_corrigir_acento_uir`, que é geral). A troca de raiz é exclusiva da
    família etimológica "-struir" (construir, destruir, instruir, e
    prefixados como "reconstruir") -- todas do latim "struere", mesma
    irregularidade historicamente compartilhada."""
    return infinitivo.endswith("struir")


def _corrigir_presente_uir(mapa: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real ao medir "construir" (já no léxico) contra o gerador
    regular de "-ir": produzia "construe"/"construes"/"construem" -- não
    existem em português. Dois casos reais, não só um:

    1) Família "-struir" (construir, destruir, instruir, reconstruir --
       ver `_e_verbo_struir_com_o_o"): perde o "u" final da raiz e ganha
       "ó" em 3 pessoas do presente: "constrÓi"/"constrÓis"/"constroem".

    2) Achado ao verificar "substituir" antes de generalizar o caso 1 pra
       ele (candidato frequente do corpus): "-uir" vocálico que NÃO é
       "-struir" (substituir, atribuir, distribuir, possuir, diminuir,
       concluir, incluir) NÃO troca de raiz, mas também não é "-e"/"-es"
       genérico de "-ir" -- é "substitui"/"substituis" (raiz + "i"/"is"
       direto, sem vogal temática "e"), porque o "u" da raiz já ocupa o
       lugar da vogal temática. "-em" (3ª plural, "substituem") já sai
       certo pela regra genérica, sem mudança.

    As demais pessoas do presente (1ª singular "-o", 1ª plural "-ímos" --
    ver `_corrigir_acento_uir`) e todo o subjuntivo já saem regulares nos
    dois casos, sem mudança de raiz."""
    if _e_verbo_struir_com_o_o(infinitivo):
        raiz_sem_u = raiz[:-1]
        substituicoes = {
            raiz + "es": raiz_sem_u + "óis",
            raiz + "e": raiz_sem_u + "ói",
            raiz + "em": raiz_sem_u + "oem",
        }
    elif _e_verbo_uir_vocalico(infinitivo):
        substituicoes = {
            raiz + "es": raiz + "is",
            raiz + "e": raiz + "i",
        }
    else:
        return mapa
    return {substituicoes.get(forma, forma): dado for forma, dado in mapa.items()}


def _corrigir_acento_uir(mapa: dict, raiz: str, infinitivo: str) -> dict:
    """Achado real, mesma medição de "construir": o "i" logo após o "u"
    final da raiz de um verbo "-uir" forma hiato tônico e precisa de
    acento -- "construi"/"construia"/"construimos"/"construido" não
    existem em português, o certo é "construí"/"construía"/
    "construímos"/"construído". Exceção real: "-iu" (pretérito perfeito
    3ª singular, "construiu") e "-indo" (gerúndio, "construindo") são
    ditongo, não hiato, e ficam sem acento. Ver `_e_verbo_uir_vocalico`
    para a exceção real de "-guir"/"-quir" (distinguir, seguir -- "u"
    mudo do dígrafo "gu", nunca vogal em hiato)."""
    if not _e_verbo_uir_vocalico(infinitivo):
        return mapa
    prefixo = raiz + "i"
    corrigidas = {}
    for forma, dado in mapa.items():
        if (
            forma != infinitivo
            and forma.startswith(prefixo)
            and not forma.startswith(prefixo + "u")
            and not forma.startswith(prefixo + "ndo")
        ):
            forma = raiz + "í" + forma[len(prefixo):]
        corrigidas[forma] = dado
    return corrigidas


def _e_verbo_air_vocalico(infinitivo: str) -> bool:
    """Achado real ao investigar "sair"/"cair" como candidatos (registado
    em `conversa.md` como "quebra muito mais que o esperado" antes de ser
    entendido): verbo terminado em "-air" (sair, cair, trair, atrair,
    contrair, distrair, extrair, retrair, abstrair, subtrair) tem raiz
    terminada em vogal "a" que forma hiato tônico com o "i" da vogal
    temática -- parecido com "-uir" (`_e_verbo_uir_vocalico`), mas não
    idêntico: "-air" também precisa inserir "i" na 1ª singular do
    presente ("saio", não "sao"), o que "-uir" não precisa ("construo"
    já sai certo). Diferente de "-guir"/"-quir" (sem digrafo "g"/"q" com
    "u" mudo aqui), não há exceção de dígrafo a excluir."""
    return infinitivo.endswith("air")


def _corrigir_acento_air(mapa: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_e_verbo_air_vocalico`. Mesma estrutura de
    `_corrigir_acento_uir` (hiato "a-í" em vez de "u-í"): qualquer forma
    que começe com raiz+"i" ganha acento no "i" (raiz+"í"), exceto
    pretérito perfeito 3ª singular ("saiu", ditongo, não hiato) e
    gerúndio ("saindo", idem) -- os dois únicos casos onde "ai" seguido
    de vogal continua ditongo em vez de virar hiato. Isto já resolve
    sozinho presente 1ª plural ("saímos"), pretérito perfeito 1ª/2ª
    singular e 3ª plural ("saí"/"saíste"/"saíram") e todo o pretérito
    imperfeito ("saía"/"saías"/"saíam") -- só falta o presente do
    indicativo (`_corrigir_presente_air`) e o subjuntivo
    (`_corrigir_subjuntivo_air`), que não nascem com "i" nenhum na forma
    bruta genérica de "-ir" (então não são achados por este prefixo)."""
    if not _e_verbo_air_vocalico(infinitivo):
        return mapa
    prefixo = raiz + "i"
    corrigidas = {}
    for forma, dado in mapa.items():
        if (
            forma != infinitivo
            and forma.startswith(prefixo)
            and not forma.startswith(prefixo + "u")
            and not forma.startswith(prefixo + "ndo")
        ):
            forma = raiz + "í" + forma[len(prefixo):]
        corrigidas[forma] = dado
    return corrigidas


def _corrigir_subjuntivo_air(mapa: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_e_verbo_air_vocalico`: a regra genérica de "-ir" gera
    "saa"/"saas"/"saamos"/"saam" pro subjuntivo presente -- não existem.
    O certo insere "i" antes da vogal temática, SEM acento ("saia",
    "saias", "saiamos", "saiam") -- diferente do indicativo (mesma
    sílaba "ai" no subjuntivo é ditongo átono, não hiato tônico, por
    isso não leva acento; "saiam" (subjuntivo) e "saíam" (pretérito
    imperfeito) são formas REAIS diferentes que continuam distintas
    porque este acerto roda DEPOIS de `_corrigir_acento_air` já ter
    reservado "saiam" com acento pro imperfeito)."""
    if not _e_verbo_air_vocalico(infinitivo):
        return mapa
    substituicoes = {
        raiz + "a": raiz + "ia",
        raiz + "as": raiz + "ias",
        raiz + "amos": raiz + "iamos",
        raiz + "am": raiz + "iam",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in mapa.items()}


def _corrigir_presente_air(mapa: dict, raiz: str, infinitivo: str) -> dict:
    """Ver `_e_verbo_air_vocalico`: a regra genérica de "-ir" gera
    "sao"/"saes"/"sae" pro presente do indicativo -- não existem. O
    certo insere "i": "saio"/"sais"/"sai". Tem que rodar DEPOIS de
    `_corrigir_acento_air`: antes dela, "sai" já pertencia ao pretérito
    perfeito 1ª singular (raiz+"i"); só depois que essa leitura vira
    "saí" (acentuada) é que "sae"->"sai" (3ª singular do presente) pode
    ocupar a forma sem colidir e apagar a outra leitura silenciosamente
    -- mesma disciplina já documentada em `_verbo` pra `_corrigir_acento_uir`
    antes de `_corrigir_presente_uir`."""
    if not _e_verbo_air_vocalico(infinitivo):
        return mapa
    substituicoes = {
        raiz + "o": raiz + "io",
        raiz + "es": raiz + "is",
        raiz + "e": raiz + "i",
    }
    return {substituicoes.get(forma, forma): dado for forma, dado in mapa.items()}


def _verbo(infinitivo: str, definicao: str) -> list[EntradaLexical]:
    """Gera as formas do presente, pretérito perfeito, pretérito
    imperfeito, futuro do presente, presente do subjuntivo, pretérito
    imperfeito do subjuntivo, futuro do subjuntivo, pretérito
    mais-que-perfeito, futuro do pretérito (condicional), imperativo
    afirmativo, gerúndio e particípio, cada uma já etiquetada com sua
    própria pessoa/número/tempo -- validação em pequena escala da
    "geração real de paradigma" (Fase 2 do plano de corretor), antes de
    crescer para um motor de geração morfológica completo (Fase 3). Só
    verbos regulares -- os 11 irregulares comuns continuam vindo do JSON
    (`lexico_base.json`), não desta geração.

    Achado real, auditoria sistemática (autor pediu "resolva muita coisa
    no léxico"): pretérito imperfeito do subjuntivo ("se eu falasse"),
    futuro do subjuntivo ("quando eu falar") e pretérito mais-que-perfeito
    ("quando cheguei, ele já falara" -- conceito 467 do conhecimento puro,
    que já registava "a forma simples... permanece" sem construção
    nenhuma) nunca existiam em NENHUM dos 397+ verbos regulares gerados
    por esta função -- lacuna sistémica, não um verbo isolado. Imperfeito
    do subjuntivo e mais-que-perfeito (exceto 3ª plural) entram direto em
    `formas` (sufixo "-sse"/"-esse"/"-isse" e "-ra"/"-era"/"-ira" nunca
    aparecem em nenhum outro tempo) e por isso já herdam de graça todas
    as correções ortográficas que rodam sobre `formas` (c/qu, g/gu, ç/c,
    g/j, hiato de "-uir"/"-air" etc.), sem precisar de nenhuma regra nova.
    Futuro do subjuntivo (1ª/3ª singular) e mais-que-perfeito (3ª plural)
    são SEMPRE idênticos a uma forma que já existe -- o infinitivo
    ("quando eu FALAR") e o pretérito perfeito 3ª plural ("eles falaram"
    = falaram ontem OU já tinham falado antes), respectivamente -- não
    podem entrar em `formas` (apagariam a leitura já lá), viram leitura
    adicional como o imperativo. O hiato de "-uir"/"-air" no futuro do
    subjuntivo (só na 2ª singular/3ª plural, nunca na 1ª plural --
    "saíres"/"saírem" mas "sairmos") é tratado à mão, não pelas funções
    genéricas de hiato (que confundiriam "sairmos" com as formas que
    devem levar acento).

    Achado real ao revisar os candidatos de maior frequência do corpus
    amplo (Fase 5 do plano de léxico): "testado", "validado",
    "implementado", "usado", "aprovado", "passando" apareciam como
    candidatos a LEMA NOVO, mas são particípio/gerúndio de verbos que já
    existem no léxico ("testar", "validar", "implementar" etc.) --
    lacuna real na geração de paradigma, não vocabulário faltando. Gerúndio
    é invariável (-ando/-endo/-indo); particípio regular flexiona como
    adjetivo (masculino/feminino, singular/plural) -- particípios
    irregulares (aberto, feito, dito, escrito, posto, visto, pago, gasto,
    ganho) ficam fora, mesmo critério dos 11 irregulares do resto desta
    função.

    Achado real ao construir o imperativo afirmativo: ele não introduz
    NENHUMA string nova. "tu" é o presente do indicativo 2ª singular sem
    o "s" final (mesma string que o presente indicativo 3ª singular já
    usa -- "fala" serve às duas); "você"/"nós"/"vocês" repetem
    exatamente o presente do subjuntivo. Por isso as entradas de
    imperativo abaixo não entram no dicionário `formas` (que é indexado
    por string e sobrescreveria a leitura já existente) -- entram como
    leituras adicionais para formas que já existem, aproveitando que
    `Dicionario` já guarda múltiplas leituras por forma (o mesmo
    mecanismo que já resolve "foi" entre "ir"/"ser"). Sem "eu" (não se
    comanda a si mesmo) nem "vós" (arcaico, já fora de escopo em todo o
    resto deste módulo). Imperativo negativo fica de fora: usa sempre o
    subjuntivo em TODAS as pessoas (incluindo "tu"), regra diferente do
    afirmativo -- próximo corte, não este."""
    raiz = infinitivo[:-2]
    formas: dict[str, tuple[Pessoa | None, Numero | None, str | None]] = {
        infinitivo: (None, None, None)
    }
    if infinitivo.endswith("ar"):
        formas.update(
            {
                raiz + "o": (Pessoa.PRIMEIRA, Numero.SINGULAR, "presente"),
                raiz + "as": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente"),
                raiz + "a": (Pessoa.TERCEIRA, Numero.SINGULAR, "presente"),
                raiz + "amos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente"),
                raiz + "am": (Pessoa.TERCEIRA, Numero.PLURAL, "presente"),
                raiz + "ei": (Pessoa.PRIMEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "aste": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "ou": (Pessoa.TERCEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "aram": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito perfeito"),
                # A mesma superfície serve à 1ª e à 3ª pessoa singular
                # ("eu falava" / "ele falava"); pessoa=None preserva a
                # leitura sincrética sem inventar uma preferência.
                raiz + "ava": (None, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "avas": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "ávamos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito"),
                raiz + "avam": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito"),
                # Subjuntivo presente troca a vogal temática para "e" nos
                # -ar. 1ª e 3ª singular são a mesma forma na língua real
                # ("que eu fale" / "que ele fale") -- pessoa=None em vez
                # de fingir uma pessoa única, mesmo critério já usado
                # para "quis"/"soube"/"disse" no pretérito dos irregulares.
                raiz + "e": (None, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "es": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "emos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente do subjuntivo"),
                raiz + "em": (Pessoa.TERCEIRA, Numero.PLURAL, "presente do subjuntivo"),
                # Pretérito imperfeito do subjuntivo: nasce do pretérito
                # perfeito 3ª plural (raiz+"aram") tirando "-ram" e trocando
                # por "-sse". 1ª/3ª singular ambíguas, mesmo critério de
                # sempre. "-ássemos" é sempre proparoxítona (regra geral de
                # acentuação, não hiato) -- leva acento em TODO verbo desta
                # conjugação, sem exceção.
                raiz + "asse": (None, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "asses": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "ássemos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                raiz + "assem": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                # Pretérito mais-que-perfeito simples (conceito 467 do
                # conhecimento puro, "a forma simples e a composta diferem
                # em frequência e registro" -- registo, não fingido: ainda
                # não tinha construção nenhuma). Nasce do mesmo radical do
                # pretérito perfeito 3ª plural, trocando "-ram" por "-ra"/
                # "-ras"/"-ramos"/"-ram" -- a 3ª plural é IDÊNTICA à do
                # pretérito perfeito ("falaram" serve às duas leituras),
                # por isso fica de fora daqui (ver `entradas_mqp_3pl`
                # abaixo, mesmo mecanismo do imperativo/pretérito 1ª
                # plural: leitura adicional pra forma que já existe).
                raiz + "ara": (None, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "aras": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "áramos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito mais-que-perfeito"),
            }
        )
    elif infinitivo.endswith("er"):
        formas.update(
            {
                raiz + "o": (Pessoa.PRIMEIRA, Numero.SINGULAR, "presente"),
                raiz + "es": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente"),
                raiz + "e": (Pessoa.TERCEIRA, Numero.SINGULAR, "presente"),
                raiz + "emos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente"),
                raiz + "em": (Pessoa.TERCEIRA, Numero.PLURAL, "presente"),
                raiz + "i": (Pessoa.PRIMEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "este": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "eu": (Pessoa.TERCEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "eram": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito perfeito"),
                raiz + "ia": (None, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "ias": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "íamos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito"),
                raiz + "iam": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito"),
                # Subjuntivo presente troca a vogal temática para "a" nos
                # -er/-ir (mesma vogal para os dois). 1ª/3ª singular
                # ambíguas -- mesmo critério do bloco -ar acima.
                raiz + "a": (None, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "as": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "amos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente do subjuntivo"),
                raiz + "am": (Pessoa.TERCEIRA, Numero.PLURAL, "presente do subjuntivo"),
                raiz + "esse": (None, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "esses": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "êssemos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                raiz + "essem": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                raiz + "era": (None, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "eras": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "êramos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito mais-que-perfeito"),
            }
        )
    elif infinitivo.endswith("ir"):
        formas.update(
            {
                raiz + "o": (Pessoa.PRIMEIRA, Numero.SINGULAR, "presente"),
                raiz + "es": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente"),
                raiz + "e": (Pessoa.TERCEIRA, Numero.SINGULAR, "presente"),
                raiz + "imos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente"),
                raiz + "em": (Pessoa.TERCEIRA, Numero.PLURAL, "presente"),
                raiz + "i": (Pessoa.PRIMEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "iste": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "iu": (Pessoa.TERCEIRA, Numero.SINGULAR, "pretérito perfeito"),
                raiz + "iram": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito perfeito"),
                raiz + "ia": (None, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "ias": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito"),
                raiz + "íamos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito"),
                raiz + "iam": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito"),
                raiz + "a": (None, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "as": (Pessoa.SEGUNDA, Numero.SINGULAR, "presente do subjuntivo"),
                raiz + "amos": (Pessoa.PRIMEIRA, Numero.PLURAL, "presente do subjuntivo"),
                raiz + "am": (Pessoa.TERCEIRA, Numero.PLURAL, "presente do subjuntivo"),
                raiz + "isse": (None, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "isses": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito imperfeito do subjuntivo"),
                raiz + "íssemos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                raiz + "issem": (Pessoa.TERCEIRA, Numero.PLURAL, "pretérito imperfeito do subjuntivo"),
                raiz + "ira": (None, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "iras": (Pessoa.SEGUNDA, Numero.SINGULAR, "pretérito mais-que-perfeito"),
                raiz + "íramos": (Pessoa.PRIMEIRA, Numero.PLURAL, "pretérito mais-que-perfeito"),
            }
        )
    formas = _corrigir_ortografia_raiz(formas, raiz, infinitivo)
    formas = _corrigir_car_com_cedilha(formas, raiz, infinitivo)
    formas = _corrigir_car_com_qu(formas, raiz, infinitivo)
    formas = _corrigir_gar_com_gu(formas, raiz, infinitivo)
    formas = _corrigir_ger_gir_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_ear_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_dir_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_der_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_zir(formas, raiz, infinitivo)
    formas = _corrigir_erir_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_o_u_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_acento_hiato_interno(formas, raiz, infinitivo)
    # "eguir" tem que vir ANTES de "guir": os dois mexem exatamente nas
    # mesmas chaves (raiz+"o"/"a"/"as"/"amos"/"am") -- "eguir" já resolve
    # o "gu" junto com o "e"->"i" (sigo, não "segu"+algo), então "guir"
    # rodando depois não encontra mais nada pra trocar nessas formas.
    formas = _corrigir_eguir_alternancia(formas, raiz, infinitivo)
    formas = _corrigir_guir(formas, raiz, infinitivo)
    # Acento de hiato tem que vir ANTES da troca de presente: "substitui"
    # (pretérito perfeito 1sg, raiz+"i") vira "substituí" aqui -- se a
    # troca de presente rodasse primeiro, a 3ª singular do presente
    # (também raiz+"i" depois da troca) colidiria com essa mesma chave
    # ainda sem acento e uma das duas leituras seria perdida no dict.
    formas = _corrigir_acento_uir(formas, raiz, infinitivo)
    formas = _corrigir_presente_uir(formas, raiz, infinitivo)
    # "-air" vocálico (sair/cair/trair...): acento tem que vir ANTES do
    # subjuntivo, que por sua vez vem ANTES do presente -- mesma disciplina
    # documentada em `_corrigir_presente_air`: sem essa ordem, "sae"->"sai"
    # (presente) ou "saa"->"saia" (subjuntivo) colidiriam com formas que
    # ainda não tinham sido acentuadas/deslocadas.
    formas = _corrigir_acento_air(formas, raiz, infinitivo)
    formas = _corrigir_subjuntivo_air(formas, raiz, infinitivo)
    formas = _corrigir_presente_air(formas, raiz, infinitivo)
    # Imperativo afirmativo: "tu" tira o "s" final do presente indicativo
    # 2ª singular; "você"/"nós"/"vocês" repetem o presente do subjuntivo
    # (mesma pessoa morfológica) -- ver achado completo no docstring.
    if infinitivo.endswith("ar"):
        imperativo = {
            raiz + "a": (Pessoa.SEGUNDA, Numero.SINGULAR),
            raiz + "e": (None, Numero.SINGULAR),
            raiz + "emos": (Pessoa.PRIMEIRA, Numero.PLURAL),
            raiz + "em": (Pessoa.TERCEIRA, Numero.PLURAL),
        }
    else:
        # -er e -ir compartilham a mesma derivação de imperativo, assim
        # como já compartilham a mesma vogal temática do subjuntivo.
        imperativo = {
            raiz + "e": (Pessoa.SEGUNDA, Numero.SINGULAR),
            raiz + "a": (None, Numero.SINGULAR),
            raiz + "amos": (Pessoa.PRIMEIRA, Numero.PLURAL),
            raiz + "am": (Pessoa.TERCEIRA, Numero.PLURAL),
        }
    imperativo = _corrigir_ortografia_raiz(imperativo, raiz, infinitivo)
    imperativo = _corrigir_car_com_cedilha(imperativo, raiz, infinitivo)
    imperativo = _corrigir_car_com_qu(imperativo, raiz, infinitivo)
    imperativo = _corrigir_gar_com_gu(imperativo, raiz, infinitivo)
    imperativo = _corrigir_ger_gir_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_ear_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_dir_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_der_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_zir(imperativo, raiz, infinitivo)
    imperativo = _corrigir_erir_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_o_u_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_acento_hiato_interno(imperativo, raiz, infinitivo)
    imperativo = _corrigir_eguir_alternancia(imperativo, raiz, infinitivo)
    imperativo = _corrigir_guir(imperativo, raiz, infinitivo)
    imperativo = _corrigir_presente_uir(imperativo, raiz, infinitivo)
    # "-air" vocálico: sem acento aqui (diferente do bloco principal) --
    # as formas brutas do imperativo (raiz+"e"/"a"/"amos"/"am") nunca
    # começam com raiz+"i", então `_corrigir_acento_air` nunca teria nada
    # pra acentuar antes destas duas rodarem, e rodar depois acentuaria
    # errado "saiamos"/"saiam" (imperativo = mesma forma do subjuntivo,
    # que é átono, sem acento).
    imperativo = _corrigir_subjuntivo_air(imperativo, raiz, infinitivo)
    imperativo = _corrigir_presente_air(imperativo, raiz, infinitivo)
    entradas_imperativo = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": "imperativo afirmativo"},
        )
        for forma, (pessoa, numero) in sorted(imperativo.items())
    ]
    # Achado real ao rodar a suite inteira (marco dos 50.000, autor pediu
    # "só testes"): pretérito perfeito só tinha 1ª/3ª singular -- faltava
    # 2ª singular ("tu"), 1ª plural ("nós") e 3ª plural ("eles") em TODO
    # verbo regular gerado por esta função (achado que afeta todos os
    # verbos já no léxico, não só os novos). "tu"/"eles" são strings novas
    # (raiz+"aste"/"este"/"iste", raiz+"aram"/"eram"/"iram"), já entraram
    # direto no `formas` acima. "nós" é a MESMA string do presente do
    # indicativo 1ª plural nas três conjugações (estudamos/comemos/
    # partimos servem pra presente E pretérito perfeito em português real)
    # -- não pode entrar em `formas` (sobrescreveria a leitura já lá),
    # mesmo mecanismo já usado pro imperativo: leitura adicional pra forma
    # que já existe.
    if infinitivo.endswith("ar"):
        preterito_1pl = {raiz + "amos": (Pessoa.PRIMEIRA, Numero.PLURAL)}
    else:
        sufixo_1pl = "emos" if infinitivo.endswith("er") else "imos"
        preterito_1pl = {raiz + sufixo_1pl: (Pessoa.PRIMEIRA, Numero.PLURAL)}
    preterito_1pl = _corrigir_ortografia_raiz(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_dir_alternancia(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_zir(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_erir_alternancia(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_o_u_alternancia(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_acento_hiato_interno(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_guir(preterito_1pl, raiz, infinitivo)
    # Acento de hiato ANTES da troca de presente -uir, mesma ordem e mesmo
    # motivo já documentados acima pro bloco principal: "construimos"
    # (achado real, quase escapou nesta mesma correção) precisa virar
    # "construímos" -- é a MESMA forma do presente indicativo 1ª plural,
    # que já passa por esta função; sem ela aqui as duas leituras
    # ficariam com strings DIFERENTES, quebrando o objetivo de serem a
    # mesma forma com duas leituras.
    preterito_1pl = _corrigir_acento_uir(preterito_1pl, raiz, infinitivo)
    preterito_1pl = _corrigir_presente_uir(preterito_1pl, raiz, infinitivo)
    # "-air" vocálico: mesmo achado do "-uir" logo acima -- "saimos" (1ª
    # plural, MESMA forma do presente indicativo) precisa virar "saímos"
    # aqui também, senão as duas leituras divergem em string.
    preterito_1pl = _corrigir_acento_air(preterito_1pl, raiz, infinitivo)
    entradas_preterito_1pl = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": "pretérito perfeito"},
        )
        for forma, (pessoa, numero) in sorted(preterito_1pl.items())
    ]
    # Pretérito mais-que-perfeito 3ª plural: MESMA string do pretérito
    # perfeito 3ª plural nas três conjugações ("falaram" serve às duas
    # leituras, "eles falaram" = falaram ontem OU já tinham falado antes)
    # -- mesmo mecanismo de leitura adicional já usado acima pra "nós" do
    # pretérito perfeito, aplicado ao mesmo tipo de colisão.
    if infinitivo.endswith("ar"):
        mqp_3pl = {raiz + "aram": (Pessoa.TERCEIRA, Numero.PLURAL)}
    else:
        sufixo_3pl = "eram" if infinitivo.endswith("er") else "iram"
        mqp_3pl = {raiz + sufixo_3pl: (Pessoa.TERCEIRA, Numero.PLURAL)}
    mqp_3pl = _corrigir_ortografia_raiz(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_dir_alternancia(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_zir(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_erir_alternancia(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_o_u_alternancia(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_acento_hiato_interno(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_guir(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_acento_uir(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_presente_uir(mqp_3pl, raiz, infinitivo)
    mqp_3pl = _corrigir_acento_air(mqp_3pl, raiz, infinitivo)
    entradas_mqp_3pl = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": "pretérito mais-que-perfeito"},
        )
        for forma, (pessoa, numero) in sorted(mqp_3pl.items())
    ]
    # Futuro do presente e futuro do pretérito (condicional): infinitivo
    # inteiro + sufixo, igual nas três conjugações -- não depende da
    # raiz, ao contrário dos tempos acima. 1ª/3ª singular do condicional
    # também são a mesma forma ("eu falaria" / "ele falaria").
    formas.update(
        {
            infinitivo + "ei": (Pessoa.PRIMEIRA, Numero.SINGULAR, "futuro do presente"),
            infinitivo + "ás": (Pessoa.SEGUNDA, Numero.SINGULAR, "futuro do presente"),
            infinitivo + "á": (Pessoa.TERCEIRA, Numero.SINGULAR, "futuro do presente"),
            infinitivo + "emos": (Pessoa.PRIMEIRA, Numero.PLURAL, "futuro do presente"),
            infinitivo + "ão": (Pessoa.TERCEIRA, Numero.PLURAL, "futuro do presente"),
            infinitivo + "ia": (None, Numero.SINGULAR, "futuro do pretérito"),
            infinitivo + "ias": (Pessoa.SEGUNDA, Numero.SINGULAR, "futuro do pretérito"),
            infinitivo + "íamos": (Pessoa.PRIMEIRA, Numero.PLURAL, "futuro do pretérito"),
            infinitivo + "iam": (Pessoa.TERCEIRA, Numero.PLURAL, "futuro do pretérito"),
        }
    )
    # Gerúndio (invariável) e particípio regular (flexiona como adjetivo):
    # ver achado completo no docstring.
    if infinitivo.endswith("ar"):
        gerundio, sufixo_part = raiz + "ando", "ado"
    elif infinitivo.endswith("er"):
        gerundio, sufixo_part = raiz + "endo", "ido"
    else:
        gerundio, sufixo_part = raiz + "indo", "ido"
    if infinitivo in _PARTICIPIOS_IRREGULARES:
        # Achado real ao adicionar "escrever" (candidato frequente, "escrito"
        # nunca existiu): particípio irregular não segue "-ado"/"-ido" nenhum
        # ("escrito", não "escrevido") -- mas, uma vez trocada a forma
        # masculina singular, o resto do paradigma (feminino, plural) É
        # regular ("-o"->"-a"/"-os"/"-as", igual a qualquer adjetivo em "-o").
        # Mesma disciplina de exceção enumerada, nunca sufixo (só um punhado
        # de verbos comuns tem particípio irregular).
        masc_sing = _PARTICIPIOS_IRREGULARES[infinitivo]
        raiz_part = masc_sing[:-1]
        formas_particípio = {
            masc_sing: (Genero.MASCULINO, Numero.SINGULAR, "particípio"),
            raiz_part + "a": (Genero.FEMININO, Numero.SINGULAR, "particípio"),
            masc_sing + "s": (Genero.MASCULINO, Numero.PLURAL, "particípio"),
            raiz_part + "as": (Genero.FEMININO, Numero.PLURAL, "particípio"),
        }
        nominais = {gerundio: (None, None, "gerúndio"), **formas_particípio}
    else:
        nominais = _corrigir_ortografia_raiz(
            {
                gerundio: (None, None, "gerúndio"),
                raiz + sufixo_part: (Genero.MASCULINO, Numero.SINGULAR, "particípio"),
                raiz + sufixo_part[:-1] + "a": (Genero.FEMININO, Numero.SINGULAR, "particípio"),
                raiz + sufixo_part + "s": (Genero.MASCULINO, Numero.PLURAL, "particípio"),
                raiz + sufixo_part[:-1] + "as": (Genero.FEMININO, Numero.PLURAL, "particípio"),
            },
            raiz, infinitivo,
        )
        nominais = _corrigir_acento_uir(nominais, raiz, infinitivo)
        # "-air" vocálico: particípio "saido"/"saida"->"saído"/"saída"
        # (hiato tônico, mesmo motivo do "-uir"); gerúndio "saindo" fica
        # de fora por ser ditongo, já tratado pela exceção dentro da
        # própria função.
        nominais = _corrigir_acento_air(nominais, raiz, infinitivo)
    entradas_nominais = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            genero=genero, numero=numero,
            atributos={"tempo": tempo},
        )
        for forma, (genero, numero, tempo) in sorted(nominais.items())
    ]
    # Futuro do subjuntivo: nasce do pretérito perfeito 3ª plural tirando
    # "-ram" e trocando por "-r"/"-res"/"-rmos"/"-rem" -- 1ª/3ª singular são
    # SEMPRE a própria forma do infinitivo ("quando eu FALAR"/"COMER"/
    # "PARTIR"), por isso não pode entrar em `formas` (sobrescreveria a
    # leitura do infinitivo) -- mesmo mecanismo já usado pro imperativo e
    # pro pretérito 1ª plural: leitura adicional pra uma forma que já existe.
    if infinitivo.endswith("ar"):
        futuro_subjuntivo = {
            infinitivo: (None, Numero.SINGULAR),
            raiz + "ares": (Pessoa.SEGUNDA, Numero.SINGULAR),
            raiz + "armos": (Pessoa.PRIMEIRA, Numero.PLURAL),
            raiz + "arem": (Pessoa.TERCEIRA, Numero.PLURAL),
        }
    elif infinitivo.endswith("er"):
        futuro_subjuntivo = {
            infinitivo: (None, Numero.SINGULAR),
            raiz + "eres": (Pessoa.SEGUNDA, Numero.SINGULAR),
            raiz + "ermos": (Pessoa.PRIMEIRA, Numero.PLURAL),
            raiz + "erem": (Pessoa.TERCEIRA, Numero.PLURAL),
        }
    else:
        futuro_subjuntivo = {
            infinitivo: (None, Numero.SINGULAR),
            raiz + "ires": (Pessoa.SEGUNDA, Numero.SINGULAR),
            raiz + "irmos": (Pessoa.PRIMEIRA, Numero.PLURAL),
            raiz + "irem": (Pessoa.TERCEIRA, Numero.PLURAL),
        }
    futuro_subjuntivo = _corrigir_ortografia_raiz(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_car_com_cedilha(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_car_com_qu(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_gar_com_gu(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_ger_gir_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_ear_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_dir_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_der_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_zir(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_erir_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_o_u_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_acento_hiato_interno(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_eguir_alternancia(futuro_subjuntivo, raiz, infinitivo)
    futuro_subjuntivo = _corrigir_guir(futuro_subjuntivo, raiz, infinitivo)
    # Hiato tônico só em "-uir"/"-air" vocálico (sair/construir...), e só
    # na 2ª singular/3ª plural ("saíres"/"saírem") -- a 1ª plural
    # ("sairmos") NÃO leva acento: a sílaba tônica aí é o próprio "-ir-"
    # final (mesmo padrão de "cantarmos"/"comermos"), não um hiato
    # isolado, diferente do que acontece nas outras pessoas. Tratado à
    # mão aqui (não pelas funções `_corrigir_acento_uir`/`_corrigir_
    # acento_air`, que dispensariam "sairmos" incorretamente por
    # casarem no mesmo prefixo raiz+"i") -- conferido contra "sair"/
    # "construir" antes de generalizar: quando eu sair, quando tu
    # saíres, quando nós sairmos, quando eles saírem.
    if _e_verbo_uir_vocalico(infinitivo) or _e_verbo_air_vocalico(infinitivo):
        acentuadas = {}
        for forma, dado in futuro_subjuntivo.items():
            if forma == raiz + "ires":
                forma = raiz + "íres"
            elif forma == raiz + "irem":
                forma = raiz + "írem"
            acentuadas[forma] = dado
        futuro_subjuntivo = acentuadas
    entradas_futuro_subjuntivo = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": "futuro do subjuntivo"},
        )
        for forma, (pessoa, numero) in sorted(futuro_subjuntivo.items())
    ]
    # Infinitivo pessoal (conceito 365, "para estudarmos"): em verbo
    # regular tem exatamente a MESMA grafia do futuro do subjuntivo em
    # TODA pessoa (achado real: não é coincidência de um caso, é regra --
    # as duas construções descendem da mesma base histórica). Reaproveita
    # o dicionário `futuro_subjuntivo` já corrigido (hiato de "-uir"/
    # "-air" incluído) em vez de derivar de novo -- mesmo dado, tempo
    # diferente, leitura adicional.
    entradas_infinitivo_pessoal = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": "infinitivo pessoal"},
        )
        for forma, (pessoa, numero) in sorted(futuro_subjuntivo.items())
    ]
    # Imperativo negativo ("não fales", "não fale", "não falemos", "não
    # falem"): ao contrário do afirmativo, usa o presente do subjuntivo
    # em TODA pessoa, incluindo "tu" (que no afirmativo vem do presente
    # indicativo) -- por isso não é mistura nenhuma, é só reetiquetar as
    # 4 formas do subjuntivo presente que já estão em `formas`, sem
    # derivar nem uma letra nova.
    entradas_imperativo_negativo = [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=dado[0], numero=dado[1],
            atributos={"tempo": "imperativo negativo"},
        )
        for forma, dado in sorted(formas.items())
        if dado[2] == "presente do subjuntivo"
    ]
    return [
        EntradaLexical(
            infinitivo, forma, ClasseGramatical.VERBO, (definicao,),
            pessoa=pessoa, numero=numero,
            atributos={"tempo": tempo} if tempo else {},
        )
        for forma, (pessoa, numero, tempo) in sorted(formas.items())
    ] + entradas_imperativo + entradas_nominais + entradas_preterito_1pl + entradas_futuro_subjuntivo + entradas_mqp_3pl + entradas_infinitivo_pessoal + entradas_imperativo_negativo


_PALAVRAS_FUNCIONAIS: tuple[EntradaLexical, ...] = (
    # Achado real ao investigar os candidatos mais frequentes do corpus
    # amplo (Fase 3/4 do plano de léxico): o léxico nunca teve cobertura de
    # classe fechada (pronome/preposição/conjunção/determinante) -- só
    # vocabulário técnico/de conteúdo. Este bloco começa a fechar essa
    # lacuna real, palavra por palavra, curada à mão -- não é lista
    # exaustiva de toda a gramática fechada do português, é o núcleo mais
    # frequente na prosa que o próprio projeto já escreveu.
    #
    # Palavra polissêmica (classe muda com o uso) ganha mais de uma
    # entrada com a MESMA forma -- nunca uma classe única forçada. Ex.:
    # "que" é conjunção integrante ("sei que vens") e pronome relativo
    # ("o livro que li"); "mesmo" é adjetivo ("o mesmo carro"), pronome
    # intensificador ("eu mesmo") e advérbio ("mesmo assim").
    #
    # Preposições (invariáveis) -- "até"/"com"/"desde"/"para"/"sem"/"sobre"
    # já existiam em lexico_base.json (lemas próprios); não duplicados aqui.
    EntradaLexical("a", "a", ClasseGramatical.PREPOSICAO, ("Introduz destino, distância, modo ou complemento; distinto do artigo/pronome \"a\".",)),
    EntradaLexical("contra", "contra", ClasseGramatical.PREPOSICAO, ("Marca oposição ou direção contrária.",)),
    EntradaLexical("entre", "entre", ClasseGramatical.PREPOSICAO, ("Marca posição intermédia entre dois ou mais termos.",)),
    EntradaLexical("perante", "perante", ClasseGramatical.PREPOSICAO, ("Marca presença de alguém diante de outro termo.",)),
    EntradaLexical("por", "por", ClasseGramatical.PREPOSICAO, ("Marca causa, meio, troca ou trajeto.",)),
    EntradaLexical("sob", "sob", ClasseGramatical.PREPOSICAO, ("Marca posição abaixo de algo.",)),
    # Conjunções -- "e"/"mas"/"portanto"/"porque"/"se"/"quando"/"então" já
    # existiam em lexico_base.json; não duplicados aqui.
    EntradaLexical("ou", "ou", ClasseGramatical.CONJUNCAO, ("Liga termos apresentando alternativa (alternativa).",)),
    EntradaLexical("pois", "pois", ClasseGramatical.CONJUNCAO, ("Liga orações indicando causa ou conclusão.",)),
    EntradaLexical("porém", "porém", ClasseGramatical.CONJUNCAO, ("Liga orações opondo uma ideia à anterior (adversativa).",)),
    EntradaLexical("contudo", "contudo", ClasseGramatical.CONJUNCAO, ("Liga orações opondo uma ideia à anterior (adversativa).",)),
    EntradaLexical("entretanto", "entretanto", ClasseGramatical.CONJUNCAO, ("Liga orações opondo uma ideia à anterior (adversativa).",)),
    EntradaLexical("logo", "logo", ClasseGramatical.CONJUNCAO, ("Liga orações indicando consequência (conclusiva).",)),
    EntradaLexical("caso", "caso", ClasseGramatical.CONJUNCAO, ("Liga orações indicando condição.",)),
    EntradaLexical("embora", "embora", ClasseGramatical.CONJUNCAO, ("Liga orações indicando concessão.",)),
    EntradaLexical("que", "que", ClasseGramatical.CONJUNCAO, ("Liga oração subordinada ao verbo da principal (\"sei que vens\").",)),
    EntradaLexical("que", "que", ClasseGramatical.PRONOME, ("Retoma um termo anterior dentro da oração seguinte (\"o livro que li\").",)),
    EntradaLexical("quem", "quem", ClasseGramatical.PRONOME, ("Retoma pessoa já referida, ou introduz pergunta sobre pessoa.",)),
    EntradaLexical("qual", "qual", ClasseGramatical.PRONOME, ("Retoma termo já referido, ou introduz pergunta de escolha.",), numero=Numero.SINGULAR),
    EntradaLexical("qual", "quais", ClasseGramatical.PRONOME, ("Retoma termo já referido, ou introduz pergunta de escolha.",), numero=Numero.PLURAL),
    EntradaLexical("quanto", "quanto", ClasseGramatical.PRONOME, ("Introduz pergunta ou referência de quantidade.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("quanto", "quanta", ClasseGramatical.PRONOME, ("Introduz pergunta ou referência de quantidade.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("quanto", "quantos", ClasseGramatical.PRONOME, ("Introduz pergunta ou referência de quantidade.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("quanto", "quantas", ClasseGramatical.PRONOME, ("Introduz pergunta ou referência de quantidade.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    # Pronomes pessoais retos -- "eu"/"tu"/"ele"/"ela"/"eles"/"elas"/"nós"
    # já existiam em lexico_base.json; só "vós" faltava.
    EntradaLexical("vós", "vós", ClasseGramatical.PRONOME, ("2ª pessoa do plural, com quem se fala.",), numero=Numero.PLURAL, pessoa=Pessoa.SEGUNDA),
    # Pronomes possessivos (só forma de base masculino/feminino singular) --
    # "meu"/"minha" já existiam em lexico_base.json.
    EntradaLexical("teu", "teu", ClasseGramatical.PRONOME, ("Indica posse pertencente à 2ª pessoa do singular.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("tua", "tua", ClasseGramatical.PRONOME, ("Indica posse pertencente à 2ª pessoa do singular.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("seu", "seu", ClasseGramatical.PRONOME, ("Indica posse pertencente à 3ª pessoa (ou a \"você\").",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("sua", "sua", ClasseGramatical.PRONOME, ("Indica posse pertencente à 3ª pessoa (ou a \"você\").",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("nosso", "nosso", ClasseGramatical.PRONOME, ("Indica posse pertencente à 1ª pessoa do plural.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("nossa", "nossa", ClasseGramatical.PRONOME, ("Indica posse pertencente à 1ª pessoa do plural.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    # Plurais dos possessivos (achado real: o lote anterior só tinha o
    # singular -- "teus"/"seus"/"nossas" etc. ficavam de fora do léxico).
    EntradaLexical("teu", "teus", ClasseGramatical.PRONOME, ("Indica posse pertencente à 2ª pessoa do singular.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("teu", "tuas", ClasseGramatical.PRONOME, ("Indica posse pertencente à 2ª pessoa do singular.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("seu", "seus", ClasseGramatical.PRONOME, ("Indica posse pertencente à 3ª pessoa (ou a \"você\").",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("seu", "suas", ClasseGramatical.PRONOME, ("Indica posse pertencente à 3ª pessoa (ou a \"você\").",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("nosso", "nossos", ClasseGramatical.PRONOME, ("Indica posse pertencente à 1ª pessoa do plural.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("nosso", "nossas", ClasseGramatical.PRONOME, ("Indica posse pertencente à 1ª pessoa do plural.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    # Pronomes demonstrativos
    EntradaLexical("este", "este", ClasseGramatical.PRONOME, ("Indica algo próximo de quem fala.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("esta", "esta", ClasseGramatical.PRONOME, ("Indica algo próximo de quem fala.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("este", "estes", ClasseGramatical.PRONOME, ("Indica algo próximo de quem fala.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("este", "estas", ClasseGramatical.PRONOME, ("Indica algo próximo de quem fala.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("esse", "esse", ClasseGramatical.PRONOME, ("Indica algo próximo de com quem se fala.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("essa", "essa", ClasseGramatical.PRONOME, ("Indica algo próximo de com quem se fala.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("esse", "esses", ClasseGramatical.PRONOME, ("Indica algo próximo de com quem se fala.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("esse", "essas", ClasseGramatical.PRONOME, ("Indica algo próximo de com quem se fala.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("aquele", "aquele", ClasseGramatical.PRONOME, ("Indica algo distante de quem fala e de com quem se fala.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("aquela", "aquela", ClasseGramatical.PRONOME, ("Indica algo distante de quem fala e de com quem se fala.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("aquele", "aqueles", ClasseGramatical.PRONOME, ("Indica algo distante de quem fala e de com quem se fala.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("aquele", "aquelas", ClasseGramatical.PRONOME, ("Indica algo distante de quem fala e de com quem se fala.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    # "aquilo" já existia em lexico_base.json.
    # Pronomes/determinantes indefinidos
    EntradaLexical("algum", "algum", ClasseGramatical.PRONOME, ("Indica quantidade ou identidade não especificada, de forma afirmativa.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("algum", "alguma", ClasseGramatical.PRONOME, ("Indica quantidade ou identidade não especificada, de forma afirmativa.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("algum", "alguns", ClasseGramatical.PRONOME, ("Indica quantidade ou identidade não especificada, de forma afirmativa.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("algum", "algumas", ClasseGramatical.PRONOME, ("Indica quantidade ou identidade não especificada, de forma afirmativa.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("nenhum", "nenhum", ClasseGramatical.PRONOME, ("Indica ausência de quantidade ou identidade.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("nenhum", "nenhuma", ClasseGramatical.PRONOME, ("Indica ausência de quantidade ou identidade.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("todo", "todo", ClasseGramatical.PRONOME, ("Indica totalidade ou generalidade (\"todo dia\"); também adjetivo (\"o dia todo\").",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("todo", "toda", ClasseGramatical.PRONOME, ("Indica totalidade ou generalidade.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("todo", "todos", ClasseGramatical.PRONOME, ("Indica totalidade ou generalidade, incluindo todos os elementos de um grupo.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("todo", "todas", ClasseGramatical.PRONOME, ("Indica totalidade ou generalidade, incluindo todos os elementos de um grupo.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("cada", "cada", ClasseGramatical.PRONOME, ("Indica cada elemento tratado individualmente dentro de um conjunto.",)),
    EntradaLexical("tal", "tal", ClasseGramatical.PRONOME, ("Indica identidade não especificada, retomando ou introduzindo algo já referido (\"tal pessoa\").",)),
    EntradaLexical("ambos", "ambos", ClasseGramatical.PRONOME, ("Indica os dois elementos de um par, sem exceção.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("ambos", "ambas", ClasseGramatical.PRONOME, ("Indica os dois elementos de um par, sem exceção.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("muito", "muita", ClasseGramatical.PRONOME, ("Indica grande quantidade (\"muita gente\") -- distinto do advérbio invariável \"muito\" (\"muito bom\").",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("muito", "muitos", ClasseGramatical.PRONOME, ("Indica grande quantidade (\"muitos livros\").",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("muito", "muitas", ClasseGramatical.PRONOME, ("Indica grande quantidade (\"muitas pessoas\").",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("outro", "outro", ClasseGramatical.PRONOME, ("Indica identidade distinta da já referida.",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("outro", "outra", ClasseGramatical.PRONOME, ("Indica identidade distinta da já referida.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("outro", "outros", ClasseGramatical.PRONOME, ("Indica identidade distinta da já referida.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("outro", "outras", ClasseGramatical.PRONOME, ("Indica identidade distinta da já referida.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("mesmo", "mesmo", ClasseGramatical.ADJETIVO, ("Indica identidade com algo já referido (\"o mesmo carro\").",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("mesmo", "mesma", ClasseGramatical.ADJETIVO, ("Indica identidade com algo já referido.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("mesmo", "mesmos", ClasseGramatical.ADJETIVO, ("Indica identidade com algo já referido.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("mesmo", "mesmas", ClasseGramatical.ADJETIVO, ("Indica identidade com algo já referido.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("mesmo", "mesmo", ClasseGramatical.PRONOME, ("Reforça a identidade do sujeito (\"eu mesmo fiz\").",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("mesmo", "mesma", ClasseGramatical.PRONOME, ("Reforça a identidade do sujeito.",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("mesmo", "mesmos", ClasseGramatical.PRONOME, ("Reforça a identidade do sujeito.",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("mesmo", "mesmas", ClasseGramatical.PRONOME, ("Reforça a identidade do sujeito.",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("mesmo", "mesmo", ClasseGramatical.ADVERBIO, ("Reforça uma afirmação (\"mesmo assim\").",)),
    EntradaLexical("tudo", "tudo", ClasseGramatical.PRONOME, ("Indica a totalidade das coisas, sem nome próprio.",)),
    EntradaLexical("nada", "nada", ClasseGramatical.PRONOME, ("Indica ausência total de coisa.",)),
    EntradaLexical("alguém", "alguém", ClasseGramatical.PRONOME, ("Indica uma pessoa não identificada.",)),
    EntradaLexical("ninguém", "ninguém", ClasseGramatical.PRONOME, ("Indica ausência de qualquer pessoa.",)),
    # Advérbios de uso muito frequente (função gramatical, não conteúdo) --
    # "muito"/"pouco"/"sempre"/"nunca"/"já"/"ainda"/"também"/"não"/"agora"/
    # "bem"/"mal"/"aqui"/"ali" já existiam em lexico_base.json.
    EntradaLexical("mais", "mais", ClasseGramatical.ADVERBIO, ("Marca grau superior numa comparação.",)),
    EntradaLexical("menos", "menos", ClasseGramatical.ADVERBIO, ("Marca grau inferior numa comparação.",)),
    EntradaLexical("só", "só", ClasseGramatical.ADVERBIO, ("Marca exclusividade (\"só isso\").",)),
    EntradaLexical("apenas", "apenas", ClasseGramatical.ADVERBIO, ("Marca exclusividade ou restrição.",)),
    EntradaLexical("antes", "antes", ClasseGramatical.ADVERBIO, ("Marca momento anterior de referência.",)),
    EntradaLexical("depois", "depois", ClasseGramatical.ADVERBIO, ("Marca momento posterior de referência.",)),
    EntradaLexical("onde", "onde", ClasseGramatical.PRONOME, ("Retoma ou pergunta sobre lugar.",)),
    EntradaLexical("como", "como", ClasseGramatical.CONJUNCAO, ("Introduz comparação (\"forte como um touro\").",)),
    EntradaLexical("como", "como", ClasseGramatical.ADVERBIO, ("Introduz pergunta sobre modo (\"como você está\").",)),
    EntradaLexical("dentro", "dentro", ClasseGramatical.ADVERBIO, ("Marca posição interna em relação a um limite.",)),
    EntradaLexical("nem", "nem", ClasseGramatical.CONJUNCAO, ("Liga termos negando ambos (\"nem um nem outro\").",)),
    EntradaLexical("qualquer", "qualquer", ClasseGramatical.PRONOME, ("Indica identidade não específica entre várias possibilidades.",)),
    EntradaLexical("algo", "algo", ClasseGramatical.PRONOME, ("Indica uma coisa não especificada, indeterminada (\"algo aconteceu\").",)),
    EntradaLexical("cujo", "cujo", ClasseGramatical.PRONOME, ("Indica posse ligando um termo ao que o precede (\"o autor cujo livro li\").",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("cujo", "cuja", ClasseGramatical.PRONOME, ("Indica posse ligando um termo ao que o precede (\"o autor cujo livro li\").",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("cujo", "cujos", ClasseGramatical.PRONOME, ("Indica posse ligando um termo ao que o precede (\"o autor cujo livro li\").",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("cujo", "cujas", ClasseGramatical.PRONOME, ("Indica posse ligando um termo ao que o precede (\"o autor cujo livro li\").",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("ontem", "ontem", ClasseGramatical.ADVERBIO, ("Marca o dia anterior ao dia presente da fala.",)),
    EntradaLexical("acima", "acima", ClasseGramatical.ADVERBIO, ("Marca posição superior em relação a uma referência.",)),
    EntradaLexical("hoje", "hoje", ClasseGramatical.ADVERBIO, ("Marca o dia presente da fala.",)),
    EntradaLexical("sim", "sim", ClasseGramatical.ADVERBIO, ("Advérbio de afirmação, resposta positiva.",)),
    EntradaLexical("trás", "trás", ClasseGramatical.ADVERBIO, ("Marca posição ou direção posterior (\"para trás\").",)),
    EntradaLexical("amanhã", "amanhã", ClasseGramatical.ADVERBIO, ("Marca o dia seguinte ao dia presente da fala.",)),
    EntradaLexical("cedo", "cedo", ClasseGramatical.ADVERBIO, ("Marca um momento antes do esperado ou no início do período.",)),
    EntradaLexical("assim", "assim", ClasseGramatical.ADVERBIO, ("Indica o modo já referido ou mostrado (\"faça assim\").",)),
    EntradaLexical("somente", "somente", ClasseGramatical.ADVERBIO, ("Marca exclusividade ou restrição (\"somente isso\").",)),
    EntradaLexical("abaixo", "abaixo", ClasseGramatical.ADVERBIO, ("Marca posição inferior em relação a uma referência.",)),
    EntradaLexical("durante", "durante", ClasseGramatical.PREPOSICAO, ("Marca o período em que algo ocorre (\"durante a aula\").",)),
    EntradaLexical("diante", "diante", ClasseGramatical.ADVERBIO, ("Marca posição à frente, geralmente seguido de \"de\" (\"diante de um problema\").",)),
    EntradaLexical("longe", "longe", ClasseGramatical.ADVERBIO, ("Marca grande distância em relação a uma referência.",)),
    EntradaLexical("fora", "fora", ClasseGramatical.ADVERBIO, ("Marca posição externa em relação a um limite.",)),
    EntradaLexical("além", "além", ClasseGramatical.ADVERBIO, ("Marca ponto ou ideia adicional, mais adiante do já dito (\"além disso\").",)),
    EntradaLexical("quase", "quase", ClasseGramatical.ADVERBIO, ("Marca proximidade sem atingir o total ou o exato (\"quase certo\").",)),
    EntradaLexical("segundo", "segundo", ClasseGramatical.NUMERAL, ("Indica a posição imediatamente após a primeira numa ordem.",), genero=Genero.MASCULINO),
    EntradaLexical("segundo", "segunda", ClasseGramatical.NUMERAL, ("Indica a posição imediatamente após a primeira numa ordem.",), genero=Genero.FEMININO),
    EntradaLexical("segundo", "segundo", ClasseGramatical.PREPOSICAO, ("Indica a fonte ou o critério de uma afirmação (\"segundo o autor\").",)),
    EntradaLexical("após", "após", ClasseGramatical.PREPOSICAO, ("Marca momento posterior a outro (\"após o almoço\").",)),
    EntradaLexical("conforme", "conforme", ClasseGramatical.PREPOSICAO, ("Indica critério ou fonte de acordo (\"conforme o combinado\").",)),
    EntradaLexical("conforme", "conforme", ClasseGramatical.CONJUNCAO, ("Introduz oração de acordo com o que se afirma (\"faça conforme eu disser\").",)),
    # Contrações (preposição + artigo/pronome, fundidas na escrita) --
    # "dos"/"pela"/"nesta"/"pelo"/"numa" estavam entre os candidatos mais
    # frequentes do corpus amplo; completadas aqui com as formas irmãs
    # óbvias da mesma família, não uma lista inventada à parte. "do"/"da"/
    # "no"/"na" (singular) já existiam em lexico_base.json como formas dos
    # lemas "de"/"em" -- só os plurais "dos"/"das"/"nos"/"nas" faltavam.
    EntradaLexical("dos", "dos", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"os\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("das", "das", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"as\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("nos", "nos", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"os\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("nas", "nas", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"as\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("ao", "ao", ClasseGramatical.PREPOSICAO, ("Contração de \"a\" + \"o\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("à", "à", ClasseGramatical.PREPOSICAO, ("Contração de \"a\" + \"a\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("aos", "aos", ClasseGramatical.PREPOSICAO, ("Contração de \"a\" + \"os\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("às", "às", ClasseGramatical.PREPOSICAO, ("Contração de \"a\" + \"as\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("pelo", "pelo", ClasseGramatical.PREPOSICAO, ("Contração de \"por\" + \"o\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("pela", "pela", ClasseGramatical.PREPOSICAO, ("Contração de \"por\" + \"a\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("pelos", "pelos", ClasseGramatical.PREPOSICAO, ("Contração de \"por\" + \"os\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("pelas", "pelas", ClasseGramatical.PREPOSICAO, ("Contração de \"por\" + \"as\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("num", "num", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"um\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("numa", "numa", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"uma\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("nuns", "nuns", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"uns\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("numas", "numas", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"umas\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("neste", "neste", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"este\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("nesta", "nesta", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"esta\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("nestes", "nestes", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"estes\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("nestas", "nestas", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"estas\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("nesse", "nesse", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"esse\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("nessa", "nessa", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"essa\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("desse", "desse", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"esse\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("dessa", "dessa", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"essa\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("deste", "deste", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"este\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("desta", "desta", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"esta\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("daquele", "daquele", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"aquele\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("daquela", "daquela", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"aquela\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("naquele", "naquele", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"aquele\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("naquela", "naquela", ClasseGramatical.PREPOSICAO, ("Contração de \"em\" + \"aquela\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("dele", "dele", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"ele\".",), genero=Genero.MASCULINO, numero=Numero.SINGULAR),
    EntradaLexical("dela", "dela", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"ela\".",), genero=Genero.FEMININO, numero=Numero.SINGULAR),
    EntradaLexical("deles", "deles", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"eles\".",), genero=Genero.MASCULINO, numero=Numero.PLURAL),
    EntradaLexical("delas", "delas", ClasseGramatical.PREPOSICAO, ("Contração de \"de\" + \"elas\".",), genero=Genero.FEMININO, numero=Numero.PLURAL),
    EntradaLexical("tanto", "tanto", ClasseGramatical.ADVERBIO, ("Indica grande quantidade ou intensidade, muitas vezes usado em comparação (\"tanto... quanto\").",)),
    EntradaLexical("através", "através", ClasseGramatical.ADVERBIO, ("Indica passagem de um lado a outro, ou meio pelo qual algo se realiza (\"através de\").",)),
)


_NOMES: tuple[tuple[str, Genero, str], ...] = (
    ("motor", Genero.MASCULINO, "Parte do sistema que executa uma responsabilidade específica."),
    ("conversa", Genero.FEMININO, "Troca de mensagens com continuidade e contexto."),
    ("pedido", Genero.MASCULINO, "Aquilo que uma pessoa solicita em linguagem natural."),
    ("intenção", Genero.FEMININO, "Sentido prático por trás de uma frase ou comando."),
    ("contexto", Genero.MASCULINO, "Informação anterior que ajuda a entender o próximo pedido."),
    ("aula", Genero.FEMININO, "Explicação organizada para ensinar um conceito a uma pessoa."),
    ("professor", Genero.MASCULINO, "Pessoa ou papel que transforma conhecimento em aprendizagem."),
    ("aluno", Genero.MASCULINO, "Pessoa que aprende, pratica e avança por etapas."),
    ("exemplo", Genero.MASCULINO, "Caso concreto usado para tornar uma ideia visível."),
    ("exercício", Genero.MASCULINO, "Tarefa curta usada para testar e fixar aprendizagem."),
    ("resumo", Genero.MASCULINO, "Versão curta que conserva a ideia principal."),
    ("fronteira", Genero.FEMININO, "Limite atual entre o que já foi construído e o que ainda precisa ser construído."),
    ("conceito", Genero.MASCULINO, "Unidade de entendimento que pode ser definida, usada e testada."),
    ("conhecimento", Genero.MASCULINO, "Conjunto de conceitos, relações e métodos já construídos."),
    ("construção", Genero.FEMININO, "Processo de formar uma ideia a partir de partes anteriores."),
    ("validação", Genero.FEMININO, "Teste usado para confirmar se uma construção funciona."),
    ("prova", Genero.FEMININO, "Caminho controlado que mostra por que uma afirmação se sustenta."),
    ("fórmula", Genero.FEMININO, "Expressão simbólica que só pode entrar como resultado ou validação, não como fundamento pronto."),
    ("matemática", Genero.FEMININO, "Construção de objetos, relações, operações, estruturas e provas."),
    ("infinito", Genero.MASCULINO, "Abertura sem último nível; no PSF é tratado por regra de continuidade, não por lista pronta."),
    ("número", Genero.MASCULINO, "Marca de quantidade ou posição construída por distinção e repetição."),
    ("operação", Genero.FEMININO, "Transformação controlada aplicada a objetos."),
    ("relação", Genero.FEMININO, "Ligação reconhecida entre objetos ou estados."),
    ("estrutura", Genero.FEMININO, "Organização estável de objetos, relações e operações."),
    ("modelo", Genero.MASCULINO, "Representação usada para testar uma teoria ou construção."),
    ("teoria", Genero.FEMININO, "Sistema organizado de conceitos, regras e consequências."),
    ("algoritmo", Genero.MASCULINO, "Sequência finita de passos para resolver uma tarefa."),
    ("função", Genero.FEMININO, "Relação que associa cada entrada permitida a uma saída determinada."),
    ("sequência", Genero.FEMININO, "Objetos postos em ordem por uma regra."),
    ("conjunto", Genero.MASCULINO, "Coleção de objetos tratados como uma unidade."),
    ("grafo", Genero.MASCULINO, "Estrutura formada por vértices e ligações."),
    ("matriz", Genero.FEMININO, "Arranjo retangular de valores usado para representar transformações ou dados."),
    ("vetor", Genero.MASCULINO, "Objeto com componentes ordenadas ou direção estrutural."),
    ("português", Genero.MASCULINO, "Língua usada pelo motor para conversar, explicar e ensinar."),
    ("dicionário", Genero.MASCULINO, "Índice de palavras, formas, classes gramaticais e definições."),
    ("palavra", Genero.FEMININO, "Forma linguística com som, grafia e significado possível."),
    ("frase", Genero.FEMININO, "Unidade de texto com sentido comunicável."),
    ("texto", Genero.MASCULINO, "Sequência organizada de frases com intenção."),
    ("gramática", Genero.FEMININO, "Regras de organização das palavras e frases."),
    ("vocabulário", Genero.MASCULINO, "Conjunto de palavras reconhecidas por uma pessoa ou sistema."),
    ("sinónimo", Genero.MASCULINO, "Palavra de sentido próximo de outra."),
    ("antónimo", Genero.MASCULINO, "Palavra de sentido oposto a outra."),
    ("fluidez", Genero.FEMININO, "Qualidade de uma conversa que mantém continuidade, naturalidade e ritmo."),
    ("clareza", Genero.FEMININO, "Qualidade de uma explicação fácil de seguir."),
    ("dificuldade", Genero.FEMININO, "Grau de esforço necessário para entender ou resolver algo."),
    ("futuro", Genero.MASCULINO, "Parte ainda não construída do trilho de conhecimento."),
    ("lacuna", Genero.FEMININO, "Ponto que falta construir, testar ou documentar."),
    ("hipótese", Genero.FEMININO, "Ideia provisória que precisa ser testada."),
    ("observação", Genero.FEMININO, "Dado ou facto percebido antes da conclusão."),
    ("regra", Genero.FEMININO, "Condição estável que orienta uma construção ou decisão."),
    ("etapa", Genero.FEMININO, "Nível numerado de construção do conhecimento PSF."),
    ("nível", Genero.MASCULINO, "Posição de avanço dentro de uma sequência de aprendizagem."),

    ("diferença", Genero.FEMININO, "Separação mínima que permite reconhecer que uma ocorrência não é outra."),
    ("som", Genero.MASCULINO, "Ocorrência audível ou abstrata que pode iniciar a fala antes da palavra."),
    ("pausa", Genero.FEMININO, "Corte ou intervalo que separa sons, palavras, frases e intenções."),
    ("marca", Genero.FEMININO, "Sinal visível que conserva uma diferença na escrita."),
    ("grafema", Genero.MASCULINO, "Unidade escrita: letra, acento, algarismo, espaço ou pontuação."),
    ("letra", Genero.FEMININO, "Grafema usado para representar som ou parte da forma escrita de uma palavra."),
    ("vogal", Genero.FEMININO, "Unidade sonora/gráfica que pode sustentar núcleo de sílaba."),
    ("consoante", Genero.FEMININO, "Unidade sonora/gráfica que se articula com vogal ou combinação."),
    ("sílaba", Genero.FEMININO, "Agrupamento pronunciável de sons ou grafemas dentro de uma palavra."),
    ("dígrafo", Genero.MASCULINO, "Combinação de duas letras tratada como uma unidade funcional."),
    ("acento", Genero.MASCULINO, "Marca gráfica que altera ou orienta a leitura de uma letra."),
    ("cedilha", Genero.FEMININO, "Marca gráfica usada sob a letra c para indicar som específico em português."),
    ("lema", Genero.MASCULINO, "Forma-base usada para reunir variantes de uma palavra."),
    ("sentido", Genero.MASCULINO, "Função interpretável que nasce da relação entre palavra, contexto e construção."),
    ("oração", Genero.FEMININO, "Construção frasal organizada em torno de verbo ou estrutura equivalente."),
    ("sujeito", Genero.MASCULINO, "Parte que ocupa o ponto de referência daquilo que se declara."),
    ("predicado", Genero.MASCULINO, "Parte que declara algo sobre o sujeito ou organiza o acontecimento verbal."),
    ("pontuação", Genero.FEMININO, "Conjunto de marcas que regula pausa, limite e intenção na escrita."),
    ("espaço", Genero.MASCULINO, "Marca vazia que separa palavras e blocos escritos."),
    ("encontro vocálico", Genero.MASCULINO, "Sequência de vogais observada dentro de uma palavra."),
    ("encontro consonantal", Genero.MASCULINO, "Sequência de consoantes observada dentro de uma palavra."),
    ("tonicidade", Genero.FEMININO, "Diferença de força entre sílabas de uma palavra."),
    ("sílaba tônica", Genero.FEMININO, "Sílaba que recebe maior força relativa dentro da palavra."),
    ("morfema", Genero.MASCULINO, "Parte mínima de palavra com função ou sentido."),
    ("radical", Genero.MASCULINO, "Parte que conserva o núcleo de família de uma palavra."),
    ("prefixo", Genero.MASCULINO, "Morfema colocado antes do radical."),
    ("sufixo", Genero.MASCULINO, "Morfema colocado depois do radical."),
    ("flexão", Genero.FEMININO, "Variação formal de palavra por gênero, número, pessoa, tempo ou modo."),
    ("gênero", Genero.MASCULINO, "Traço de concordância que organiza masculino, feminino ou comum."),
    ("número gramatical", Genero.MASCULINO, "Traço que distingue singular e plural na construção linguística."),
    ("pessoa gramatical", Genero.FEMININO, "Traço que organiza quem fala, com quem se fala e de quem se fala."),
    ("nome", Genero.MASCULINO, "Palavra que aponta para entidade, coisa, ideia, lugar ou conceito."),
    ("substantivo", Genero.MASCULINO, "Classe de palavra que nomeia entidade, coisa, ideia, lugar ou conceito."),
    ("verbo", Genero.MASCULINO, "Classe de palavra que organiza ação, estado, existência, ocorrência ou ligação."),
    ("adjetivo", Genero.MASCULINO, "Classe de palavra que atribui característica a um nome."),
    ("pronome", Genero.MASCULINO, "Classe de palavra que retoma, aponta ou substitui referência."),
    ("determinante", Genero.MASCULINO, "Classe de palavra que acompanha nome e limita referência."),
    ("advérbio", Genero.MASCULINO, "Classe de palavra que modifica verbo, adjetivo, outro advérbio ou frase."),
    ("concordância", Genero.FEMININO, "Ajuste formal entre palavras relacionadas."),
    ("parágrafo", Genero.MASCULINO, "Bloco de texto que agrupa frases em torno de continuidade local."),
    ("coerência", Genero.FEMININO, "Continuidade de sentido entre partes do texto."),
    ("coesão", Genero.FEMININO, "Ligação visível entre partes do texto."),
    ("funcionamento", Genero.MASCULINO, "Caminho interno pelo qual uma construção opera do mínimo até uma forma viva."),
    ("enunciado", Genero.MASCULINO, "Unidade comunicativa dita ou escrita numa situação."),
    ("referência", Genero.FEMININO, "Ligação entre palavra ou expressão e aquilo para que aponta."),
    ("referente", Genero.MASCULINO, "Alvo textual ou situacional construído pela referência."),
    ("campo", Genero.MASCULINO, "Agrupamento ou zona de relação entre elementos."),
    ("campo semântico", Genero.MASCULINO, "Agrupamento de palavras por proximidade de sentido."),
    ("polissemia", Genero.FEMININO, "Possibilidade de uma palavra ter sentidos diferentes conforme o contexto."),
    ("sinonímia", Genero.FEMININO, "Proximidade de sentido entre palavras em certo contexto."),
    ("antonímia", Genero.FEMININO, "Oposição de sentido entre palavras ou expressões."),
    ("conectivo", Genero.MASCULINO, "Palavra ou expressão que liga partes do texto."),
    ("retomada", Genero.FEMININO, "Retorno a um referente já construído no texto."),
    ("elipse", Genero.FEMININO, "Ausência controlada de parte recuperável pela construção."),
    ("inferência", Genero.FEMININO, "Sentido obtido pela relação entre o dito e o implicado."),
    ("período", Genero.MASCULINO, "Unidade formada por uma ou mais orações e limitada por pontuação final."),
    ("coordenação", Genero.FEMININO, "Ligação de unidades de mesmo nível funcional."),
    ("subordinação", Genero.FEMININO, "Ligação em que uma unidade depende de outra."),
    ("termo", Genero.MASCULINO, "Parte funcional de uma oração ou frase."),
    ("núcleo", Genero.MASCULINO, "Parte central de um termo ou construção."),
    ("complemento", Genero.MASCULINO, "Termo que completa sentido de nome, verbo ou construção."),
    ("adjunto", Genero.MASCULINO, "Termo que acrescenta informação sem completar exigência central."),
    ("transitividade", Genero.FEMININO, "Modo como um verbo pede ou dispensa complemento."),
    ("regência", Genero.FEMININO, "Relação de exigência ou orientação entre palavras."),
    ("colocação", Genero.FEMININO, "Posição relativa de palavras na frase."),
    ("norma", Genero.FEMININO, "Regularidade aceita para uso controlado da língua."),
    ("uso", Genero.MASCULINO, "Prática concreta de aplicar a língua numa situação."),
    ("variação", Genero.FEMININO, "Diferença de uso conforme pessoa, lugar, tempo ou situação."),
    ("variação linguística", Genero.FEMININO, "Diferença de uso entre comunidades, lugares, tempos e situações."),
    ("registro", Genero.MASCULINO, "Ajuste de linguagem conforme situação e formalidade."),
    ("fala", Genero.FEMININO, "Realização oral ou concreta da língua em uso."),
    ("escrita", Genero.FEMININO, "Realização gráfica da língua por marcas organizadas."),
    ("emissor", Genero.MASCULINO, "Participante que produz um enunciado."),
    ("receptor", Genero.MASCULINO, "Participante que recebe ou interpreta um enunciado."),
    ("modalidade", Genero.FEMININO, "Orientação do enunciado quanto a afirmar, negar, perguntar, ordenar ou avaliar."),
    ("afirmação", Genero.FEMININO, "Modalidade que apresenta algo como posto ou sustentado."),
    ("negação", Genero.FEMININO, "Marca de recusa, ausência, oposição ou cancelamento de uma afirmação possível."),
    ("interrogação", Genero.FEMININO, "Modalidade que busca informação, confirmação ou escolha."),
    ("exclamação", Genero.FEMININO, "Modalidade que aumenta força expressiva, surpresa, emoção ou ênfase."),
    ("tempo verbal", Genero.MASCULINO, "Traço verbal que situa ocorrência em relação a antes, agora, depois ou referência interna."),
    ("aspecto verbal", Genero.MASCULINO, "Modo de observar a ocorrência como concluída, em curso, repetida, habitual ou iniciada."),
    ("modo verbal", Genero.MASCULINO, "Orientação do verbo quanto a certeza, hipótese, desejo, ordem ou condição."),
    ("voz verbal", Genero.FEMININO, "Organização que mostra como sujeito e predicado se relacionam com a ação."),
    ("preposição", Genero.FEMININO, "Palavra relacional que aproxima termos e orienta dependência de sentido."),
    ("conjunção", Genero.FEMININO, "Palavra relacional que liga termos ou orações."),
    ("interjeição", Genero.FEMININO, "Palavra ou emissão que manifesta reação, chamado, dor, surpresa ou contacto comunicativo."),
    ("numeral", Genero.MASCULINO, "Classe que introduz contagem, ordem, fração ou multiplicação na língua."),
    ("artigo", Genero.MASCULINO, "Determinante que apresenta nome como definido, indefinido ou introduzido na referência."),
    ("locução", Genero.FEMININO, "Combinação estável de palavras que funciona como unidade de classe ou função."),
    ("perífrase verbal", Genero.FEMININO, "Locução em que verbos combinados expressam tempo, aspecto, modalidade ou ação composta."),
    ("discurso direto", Genero.MASCULINO, "Modo textual que apresenta fala ou pensamento como enunciado preservado."),
    ("discurso indireto", Genero.MASCULINO, "Modo textual que reconstrói fala ou pensamento dentro de outra enunciação."),
    ("tema", Genero.MASCULINO, "Aquilo sobre que um texto, parágrafo ou enunciado se organiza."),
    ("progressão temática", Genero.FEMININO, "Avanço controlado do tema ao longo do texto."),
    ("ambiguidade", Genero.FEMININO, "Abertura de mais de uma leitura possível para uma forma, frase ou texto."),
    ("pragmática", Genero.FEMININO, "Observação do sentido em uso, considerando intenção, contexto, participantes e efeito."),
    ("estilo", Genero.MASCULINO, "Modo recorrente de escolher palavras, ritmo, ordem, tom e construção textual."),
    ("revisão", Genero.FEMININO, "Retorno controlado ao texto para verificar coerência, coesão, norma, clareza e intenção."),
    ("interpretação", Genero.FEMININO, "Construção de sentido a partir de texto, contexto, relações e inferências limitadas."),
    # Lote extraído do corpus amplo (Fase 3/4 do plano de léxico), palavras de
    # alta frequência na prosa já autoral do projeto, ainda ausentes do
    # léxico antes desta entrada.
    ("consulta", Genero.FEMININO, "Ato de perguntar ou verificar informação já registrada."),
    ("dependência", Genero.FEMININO, "Aquilo de que um conceito ou construção precisa para existir."),
    ("forma", Genero.FEMININO, "Aspecto ou configuração que algo assume."),
    ("ocorrência", Genero.FEMININO, "Caso concreto em que algo acontece ou aparece."),
    ("definição", Genero.FEMININO, "Enunciado que fixa o sentido preciso de um conceito."),
    ("domínio", Genero.MASCULINO, "Área ou conjunto sobre o qual uma construção ou regra se aplica."),
    ("análise", Genero.FEMININO, "Exame que separa um todo nas suas partes para entender a construção."),
    ("linguística", Genero.FEMININO, "Área que estuda a estrutura e o funcionamento da língua."),
    ("bloco", Genero.MASCULINO, "Conjunto de partes tratadas como unidade dentro de uma organização maior."),
    ("posição", Genero.FEMININO, "Lugar que um elemento ocupa dentro de uma ordem ou estrutura."),
    ("fluxo", Genero.MASCULINO, "Caminho contínuo que avança de um conceito para o seguinte sem saltos."),
    ("unidade", Genero.FEMININO, "Elemento tratado como um todo dentro de uma contagem ou estrutura."),
    ("projeto", Genero.MASCULINO, "Empreendimento organizado com objetivo e construção definidos."),
    ("limite", Genero.MASCULINO, "Ponto além do qual uma construção ou regra deixa de valer."),
    ("base", Genero.FEMININO, "Fundamento sobre o qual uma construção se apoia."),
    ("igualdade", Genero.FEMININO, "Relação entre dois valores ou formas que são exatamente o mesmo."),
    ("busca", Genero.FEMININO, "Percurso controlado para encontrar um elemento ou caminho."),
    ("grau", Genero.MASCULINO, "Nível ou medida numa escala ordenada."),
    ("implementação", Genero.FEMININO, "Construção concreta em código de uma ideia já especificada."),
    # Segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("raiz", Genero.FEMININO, "Origem ou fundamento de onde algo nasce."),
    ("lógica", Genero.FEMININO, "Disciplina que estuda a validade do raciocínio."),
    ("classe", Genero.FEMININO, "Categoria que agrupa elementos com propriedade comum."),
    ("pessoa", Genero.FEMININO, "Indivíduo humano, ou categoria gramatical que marca quem fala."),
    ("valor", Genero.MASCULINO, "Quantidade ou grandeza atribuída a algo."),
    ("zero", Genero.MASCULINO, "Ausência de quantidade; ponto de partida da contagem."),
    ("modo", Genero.MASCULINO, "Maneira como algo acontece ou é feito."),
    ("verdade", Genero.FEMININO, "Aquilo que corresponde exatamente ao que é."),
    ("ponte", Genero.FEMININO, "Ligação explícita entre um conceito novo e outro já construído."),
    ("erro", Genero.MASCULINO, "Desvio entre o esperado e o que aconteceu de fato."),
    ("autor", Genero.MASCULINO, "Pessoa que cria ou constrói uma obra ou ideia."),
    ("parte", Genero.FEMININO, "Porção de um todo maior."),
    ("objeto", Genero.MASCULINO, "Aquilo sobre que uma ação ou pensamento recai."),
    ("mudança", Genero.FEMININO, "Passagem de um estado para outro diferente."),
    ("produto", Genero.MASCULINO, "Resultado de uma construção ou operação."),
    ("lei", Genero.FEMININO, "Regra permanente que rege um domínio."),
    ("expressão", Genero.FEMININO, "Forma que representa um valor ou ideia."),
    ("item", Genero.MASCULINO, "Elemento individual dentro de uma lista ou conjunto."),
    ("linguagem", Genero.FEMININO, "Sistema usado para comunicar ou representar sentido."),
    ("padrão", Genero.MASCULINO, "Forma recorrente que se repete de modo reconhecível."),
    ("passo", Genero.MASCULINO, "Etapa individual dentro de uma construção maior."),
    ("distinção", Genero.FEMININO, "Marca que separa dois conceitos próximos."),
    ("voz", Genero.FEMININO, "Som produzido pela fala, ou organização gramatical sujeito-ação."),
    ("vez", Genero.FEMININO, "Ocasião ou repetição contada de um evento."),
    ("fechamento", Genero.MASCULINO, "Conclusão que fecha uma construção ou etapa."),
    ("equivalência", Genero.FEMININO, "Relação em que dois elementos valem exatamente o mesmo."),
    ("grupo", Genero.MASCULINO, "Conjunto de elementos tratados como unidade."),
    # Terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("variedade", Genero.FEMININO, "Conjunto de formas ou versões diferentes dentro de uma mesma categoria."),
    ("caminho", Genero.MASCULINO, "Percurso ou sequência de passos até um destino."),
    ("informação", Genero.FEMININO, "Conteúdo que reduz incerteza sobre algo."),
    ("lista", Genero.FEMININO, "Sequência ordenada de elementos."),
    ("auditoria", Genero.FEMININO, "Verificação sistemática que confere se algo está correto ou completo."),
    ("aritmética", Genero.FEMININO, "Ramo que trata de números e das operações entre eles."),
    ("corpo", Genero.MASCULINO, "Conjunto principal de um texto ou estrutura, sem as partes periféricas."),
    ("condição", Genero.FEMININO, "Circunstância que precisa se cumprir para algo acontecer."),
    ("contagem", Genero.FEMININO, "Ato de determinar quantos elementos existem num conjunto."),
    ("conteúdo", Genero.MASCULINO, "Aquilo que está contido dentro de uma forma ou estrutura."),
    ("realização", Genero.FEMININO, "Ato de tornar concreto algo que antes era só ideia."),
    ("catálogo", Genero.MASCULINO, "Lista organizada que inventaria itens de um conjunto."),
    ("ligação", Genero.FEMININO, "Conexão estabelecida entre duas partes ou conceitos."),
    ("propriedade", Genero.FEMININO, "Característica que pertence a um objeto ou estrutura."),
    ("elemento", Genero.MASCULINO, "Unidade individual que compõe um conjunto maior."),
    ("ausência", Genero.FEMININO, "Estado de não estar presente."),
    ("módulo", Genero.MASCULINO, "Parte independente que compõe um sistema maior."),
    ("alvo", Genero.MASCULINO, "Aquilo que se pretende atingir ou identificar."),
    ("ação", Genero.FEMININO, "Ato realizado por alguém ou algo."),
    # Quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("caso", Genero.MASCULINO, "Ocorrência particular usada como exemplo ou instância."),
    ("narrativa", Genero.FEMININO, "Relato organizado de acontecimentos."),
    ("repetição", Genero.FEMININO, "Ocorrência de novo do mesmo elemento ou padrão."),
    ("organização", Genero.FEMININO, "Disposição ordenada de partes dentro de um todo."),
    ("participante", Genero.MASCULINO, "Pessoa ou elemento que toma parte numa situação ou interação."),
    ("avaliação", Genero.FEMININO, "Julgamento sobre o valor, a qualidade ou a correção de algo."),
    ("documento", Genero.MASCULINO, "Registro escrito que preserva informação ou conhecimento."),
    ("grafia", Genero.FEMININO, "Modo como uma palavra é escrita."),
    ("código", Genero.MASCULINO, "Sistema de instruções escrito para ser executado por um sistema."),
    ("marcador", Genero.MASCULINO, "Elemento que assinala ou identifica uma posição ou categoria."),
    ("conclusão", Genero.FEMININO, "Ideia final alcançada a partir do que veio antes."),
    ("decisão", Genero.FEMININO, "Escolha feita entre alternativas possíveis."),
    ("continuidade", Genero.FEMININO, "Manutenção de uma ligação sem interrupção ao longo do tempo."),
    ("tipo", Genero.MASCULINO, "Categoria que agrupa elementos com característica comum."),
    ("plano", Genero.MASCULINO, "Conjunto organizado de passos para alcançar um objetivo."),
    # Quinto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("discurso", Genero.MASCULINO, "Uso organizado da língua numa situação real de comunicação."),
    ("pretérito", Genero.MASCULINO, "Tempo verbal que situa a ocorrência antes do momento de referência."),
    ("linha", Genero.FEMININO, "Sequência contínua de texto, marca ou elementos numa direção."),
    ("fonte", Genero.FEMININO, "Origem de onde algo vem ou é obtido."),
    ("produção", Genero.FEMININO, "Ato de gerar ou construir algo a partir de partes ou processo."),
    ("razão", Genero.FEMININO, "Motivo que explica ou justifica algo."),
    ("dado", Genero.MASCULINO, "Informação básica usada como ponto de partida para análise ou construção."),
    ("plural", Genero.MASCULINO, "Forma que indica mais de um elemento."),
    ("par", Genero.MASCULINO, "Conjunto de dois elementos associados."),
    # Sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("criança", Genero.FEMININO, "Ser humano na primeira fase da vida, antes da idade adulta."),
    ("autoridade", Genero.FEMININO, "Poder reconhecido para decidir ou validar algo dentro de um domínio."),
    ("efeito", Genero.MASCULINO, "Consequência produzida por uma causa."),
    ("fato", Genero.MASCULINO, "Acontecimento real, verificável, distinto de opinião ou suposição."),
    ("achado", Genero.MASCULINO, "Descoberta feita ao investigar ou testar algo."),
    ("constituinte", Genero.MASCULINO, "Elemento que entra na composição de uma estrutura maior."),
    ("agente", Genero.MASCULINO, "Quem ou o que realiza uma ação."),
    # Sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("área", Genero.FEMININO, "Domínio ou extensão dentro do qual algo se aplica ou existe."),
    # Oitavo lote do corpus amplo (Fase 3/4, corte seguinte). Sentido
    # escolhido para palavra polissêmica (ex.: "anel") segue o mesmo
    # critério já usado em "corpo"/"classe"/"grau" neste ficheiro: sentido
    # geral do dicionário, não o técnico específico que motivou a
    # frequência alta neste corpus matemático -- léxico de uso comum, a
    # camada técnica por ETAPA fica noutro lugar.
    ("teorema", Genero.MASCULINO, "Proposição demonstrada a partir de axiomas ou de outros teoremas já provados."),
    ("cálculo", Genero.MASCULINO, "Processo de determinar um valor ou resultado a partir de dados conhecidos, seguindo regras definidas."),
    ("equação", Genero.FEMININO, "Igualdade entre duas expressões que contém pelo menos uma incógnita a determinar."),
    ("rima", Genero.FEMININO, "Semelhança de som entre finais de palavras, frequente no fim de versos."),
    ("completude", Genero.FEMININO, "Estado ou qualidade do que está completo, sem parte ou elemento faltando."),
    ("triângulo", Genero.MASCULINO, "Polígono de três lados e três ângulos."),
    ("trigonometria", Genero.FEMININO, "Ramo da matemática que estuda as relações entre os ângulos e os lados de um triângulo."),
    ("anel", Genero.MASCULINO, "Peça circular, geralmente usada como adorno ou símbolo, vestida num dedo."),
    ("simetria", Genero.FEMININO, "Correspondência exata entre as partes de algo em relação a um eixo, ponto ou plano central."),
    ("categoria", Genero.FEMININO, "Classe em que se agrupam elementos que compartilham uma característica comum."),
    ("contraste", Genero.MASCULINO, "Diferença acentuada entre dois elementos colocados lado a lado."),
    ("identidade", Genero.FEMININO, "Conjunto de características que tornam algo exatamente aquilo que é, e não outra coisa."),
    ("quadrado", Genero.MASCULINO, "Polígono de quatro lados iguais e quatro ângulos retos."),
    ("intervalo", Genero.MASCULINO, "Espaço ou distância entre dois pontos, momentos ou valores."),
    # Nono lote do corpus amplo (Fase 3/4, corte seguinte).
    ("aresta", Genero.FEMININO, "Segmento que liga dois vértices num grafo, ou lado de um polígono."),
    ("geometria", Genero.FEMININO, "Ramo da matemática que estuda forma, tamanho e posição das figuras."),
    ("convenção", Genero.FEMININO, "Acordo aceito por um grupo sobre como fazer ou representar algo."),
    ("operador", Genero.MASCULINO, "Símbolo ou função que atua sobre um ou mais valores para produzir um resultado."),
    ("redução", Genero.FEMININO, "Ato de tornar algo menor ou mais simples."),
    ("mapa", Genero.MASCULINO, "Representação visual de um espaço, estrutura ou relação entre elementos."),
    ("entrada", Genero.FEMININO, "Valor ou dado que um processo recebe para começar a operar."),
    # Décimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("rede", Genero.FEMININO, "Conjunto de pontos ligados por conexões, formando uma estrutura interligada."),
    ("ato", Genero.MASCULINO, "Ação realizada num momento determinado."),
    ("aproximação", Genero.FEMININO, "Valor ou resultado que chega perto do exato sem ser idêntico a ele."),
    # Décimo primeiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("fase", Genero.FEMININO, "Etapa distinta dentro de um processo maior."),
    ("lugar", Genero.MASCULINO, "Posição ou ponto ocupado num espaço ou numa ordem."),
    ("sinal", Genero.MASCULINO, "Marca ou símbolo que indica algo além de si mesmo."),
    ("sistema", Genero.MASCULINO, "Conjunto de partes organizadas que funcionam de forma interligada."),
    ("substituição", Genero.FEMININO, "Ato de colocar algo no lugar de outra coisa."),
    ("acentuação", Genero.FEMININO, "Marcação da sílaba tônica ou do acento gráfico de uma palavra."),
    # Décimo lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("léxico", Genero.MASCULINO, "Conjunto de palavras conhecidas por um sistema ou falante."),
    ("capacidade", Genero.FEMININO, "Medida do que algo pode conter, suportar ou realizar."),
    ("corte", Genero.MASCULINO, "Ação de dividir ou separar algo com um instrumento ou critério."),
    ("foco", Genero.MASCULINO, "Ponto central de atenção ou de convergência."),
    ("origem", Genero.FEMININO, "Ponto ou momento em que algo começa a existir."),
    ("porta", Genero.FEMININO, "Estrutura móvel que fecha ou abre a entrada de um espaço."),
    ("aspecto", Genero.MASCULINO, "Característica particular pela qual algo pode ser observado."),
    ("história", Genero.FEMININO, "Relato de acontecimentos reais ou sequência de fatos ao longo do tempo."),
    ("fundamento", Genero.MASCULINO, "Base sobre a qual algo se apoia ou se justifica."),
    ("máquina", Genero.FEMININO, "Sistema construído para executar uma tarefa de forma automática."),
    ("primo", Genero.MASCULINO, "Número inteiro maior que 1 que só é divisível por 1 e por ele mesmo."),
    # Décimo primeiro lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("escolha", Genero.FEMININO, "Ato de selecionar uma opção entre várias possíveis."),
    ("sucessor", Genero.MASCULINO, "Aquele ou aquilo que vem logo depois na ordem ou sequência."),
    ("círculo", Genero.MASCULINO, "Figura plana formada por todos os pontos a uma mesma distância de um centro."),
    ("ângulo", Genero.MASCULINO, "Abertura formada por dois segmentos ou retas que partem de um mesmo ponto."),
    ("vértice", Genero.MASCULINO, "Ponto onde dois ou mais lados ou arestas se encontram."),
    ("via", Genero.FEMININO, "Caminho ou meio pelo qual algo passa ou se realiza."),
    ("inventário", Genero.MASCULINO, "Lista detalhada dos elementos que compõem um conjunto."),
    ("medida", Genero.FEMININO, "Valor obtido ao comparar uma grandeza com uma unidade de referência."),
    ("topologia", Genero.FEMININO, "Ramo da matemática que estuda propriedades que se mantêm sob deformação contínua."),
    # Décimo segundo lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("cardinalidade", Genero.FEMININO, "Quantidade de elementos que um conjunto possui."),
    ("corrente", Genero.FEMININO, "Fluxo contínuo de algo que se desloca numa direção."),
    ("fita", Genero.FEMININO, "Tira longa e estreita de material flexível, usada para prender, medir ou registrar."),
    ("fonética", Genero.FEMININO, "Ramo que estuda os sons da fala e como são produzidos."),
    ("formação", Genero.FEMININO, "Processo pelo qual algo se constitui ou toma forma."),
    ("reconstrução", Genero.FEMININO, "Ato de construir novamente algo a partir dos seus fundamentos."),
    ("tabela", Genero.FEMININO, "Estrutura que organiza dados em linhas e colunas."),
    ("traço", Genero.MASCULINO, "Marca ou linha que representa uma característica ou limite."),
    # Décimo terceiro lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("cadeia", Genero.FEMININO, "Sequência de elementos ligados uns aos outros."),
    ("coeficiente", Genero.MASCULINO, "Número que multiplica uma variável ou termo numa expressão."),
    ("coloração", Genero.FEMININO, "Cor ou conjunto de cores que algo apresenta."),
    ("consequência", Genero.FEMININO, "Aquilo que resulta diretamente de uma causa ou ação."),
    ("correção", Genero.FEMININO, "Ajuste que torna algo certo depois de identificado um erro."),
    ("distância", Genero.FEMININO, "Extensão do espaço entre dois pontos."),
    ("ficheiro", Genero.MASCULINO, "Unidade de dados armazenada com um nome, guardada num sistema."),
    ("potência", Genero.FEMININO, "Resultado de multiplicar um número por ele mesmo repetidamente; capacidade de produzir efeito."),
    # Décimo quarto lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    # "cão" fica de fora por ora: plural "-ão"->"-ães" é a classe irregular
    # já documentada em `_plural_substantivo` (mão/pão/irmão), sem regra
    # segura ainda -- não adiciono às cegas ("cãos" seria gerado, errado).
    ("separação", Genero.FEMININO, "Ato de colocar partes ou elementos fora de contacto uns dos outros."),
    ("transformação", Genero.FEMININO, "Mudança na forma, natureza ou estado de algo."),
    ("alternância", Genero.FEMININO, "Sucessão regular entre dois ou mais elementos diferentes."),
    ("classificação", Genero.FEMININO, "Organização de elementos em categorias segundo um critério."),
    ("extensão", Genero.FEMININO, "Medida do quanto algo se estende no espaço ou no tempo."),
    ("intensidade", Genero.FEMININO, "Grau de força ou energia com que algo se manifesta."),
    ("início", Genero.MASCULINO, "Ponto em que algo começa."),
    ("corpus", Genero.MASCULINO, "Conjunto organizado de textos reunidos para estudo ou análise."),
    # Décimo quinto lote de nomes: "cão" resolvido com exceção lexical em
    # `_PLURAIS_AO_IRREGULARES`, deixa de ficar de fora.
    ("cão", Genero.MASCULINO, "Mamífero doméstico da família dos canídeos, companheiro comum do ser humano."),
    # Décimo sexto lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("memória", Genero.FEMININO, "Capacidade de guardar e recuperar informação já vivida ou aprendida."),
    ("pronúncia", Genero.FEMININO, "Modo como os sons de uma palavra são produzidos ao falar."),
    ("árvore", Genero.FEMININO, "Planta de caule lenhoso e ramificado, ou estrutura hierárquica em forma de galhos."),
    ("currículo", Genero.MASCULINO, "Conjunto organizado de conteúdos e etapas que formam um percurso de ensino."),
    ("desenvolvimento", Genero.MASCULINO, "Processo de crescimento ou avanço de algo ao longo do tempo."),
    ("papel", Genero.MASCULINO, "Material fino usado para escrever ou imprimir; função ou parte desempenhada por algo ou alguém."),
    ("lado", Genero.MASCULINO, "Parte de algo situada numa direção em relação a um centro ou eixo."),
    ("ataque", Genero.MASCULINO, "Ação de investir contra algo ou alguém para causar dano ou tomar iniciativa."),
    # Décimo sétimo lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("união", Genero.FEMININO, "Ato de juntar duas ou mais partes num só conjunto."),
    ("agrupamento", Genero.MASCULINO, "Conjunto de elementos reunidos por uma característica comum."),
    ("entidade", Genero.FEMININO, "Aquilo que existe como unidade própria e distinta."),
    ("execução", Genero.FEMININO, "Ato de realizar ou levar a cabo algo já planeado."),
    # Décimo oitavo lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("pureza", Genero.FEMININO, "Estado do que não está misturado com nada estranho a si."),
    ("símbolo", Genero.MASCULINO, "Sinal que representa algo além de si mesmo por convenção ou associação."),
    ("biblioteca", Genero.FEMININO, "Coleção organizada de obras ou recursos reunidos para consulta."),
    # Décimo nono lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("imagem", Genero.FEMININO, "Representação visual de algo, ou impressão que se forma sobre alguém ou algo."),
    ("meio", Genero.MASCULINO, "Ponto ou parte central de algo, ou aquilo que serve para alcançar um fim."),
    # Vigésimo lote de nomes do corpus amplo (Fase 3/4, corte seguinte).
    ("contacto", Genero.MASCULINO, "Situação em que duas coisas se tocam ou entram em relação direta."),
    ("conversão", Genero.FEMININO, "Mudança de uma forma, valor ou sistema para outro equivalente."),
    ("força", Genero.FEMININO, "Capacidade de produzir movimento, resistência ou efeito sobre algo."),
    ("interseção", Genero.FEMININO, "Ponto ou região onde dois ou mais elementos se cruzam."),
    ("investigação", Genero.FEMININO, "Processo sistemático de busca por conhecimento ou resposta a uma pergunta."),
    ("método", Genero.MASCULINO, "Caminho ordenado de passos seguido para alcançar um resultado."),
    ("peça", Genero.FEMININO, "Parte que compõe um todo maior, ou objeto individual dentro de um conjunto."),
    ("reta", Genero.FEMININO, "Linha que se estende infinitamente em duas direções sem curvar."),
    # Vigésimo primeiro lote de nomes do corpus amplo (Fase 3/4, corte
    # seguinte) -- lote maior, mesmo padrão de definição autorada à mão,
    # a pedido do autor pra medir se aumenta o ritmo real sem perder
    # qualidade.
    ("música", Genero.FEMININO, "Arte de organizar sons e silêncios no tempo, segundo ritmo, melodia e harmonia."),
    ("qualidade", Genero.FEMININO, "Característica que define como algo é, boa ou má."),
    ("regularidade", Genero.FEMININO, "Propriedade do que segue sempre o mesmo padrão, sem variar."),
    ("comunidade", Genero.FEMININO, "Grupo de pessoas que compartilham um espaço, interesse ou característica comum."),
    ("crescimento", Genero.MASCULINO, "Aumento gradual em tamanho, quantidade ou desenvolvimento."),
    ("desvio", Genero.MASCULINO, "Afastamento em relação a um caminho, padrão ou valor esperado."),
    ("dígito", Genero.MASCULINO, "Símbolo usado para representar um número dentro de um sistema de numeração."),
    ("finalidade", Genero.FEMININO, "Objetivo para o qual algo é feito ou existe."),
    ("generalização", Genero.FEMININO, "Extensão de uma conclusão ou regra para além dos casos originalmente observados."),
    ("seleção", Genero.FEMININO, "Ato de escolher um ou mais elementos dentro de um conjunto maior."),
    ("sessão", Genero.FEMININO, "Período de tempo dedicado a uma atividade específica, com início e fim definidos."),
    ("tópico", Genero.MASCULINO, "Assunto específico tratado dentro de um texto ou discussão."),
    ("assimilação", Genero.FEMININO, "Processo pelo qual um som, ideia ou elemento se torna semelhante a outro próximo."),
    ("aquisição", Genero.FEMININO, "Ato de passar a ter ou dominar algo que antes não se tinha."),
    ("apresentação", Genero.FEMININO, "Ato de mostrar ou expor algo a alguém pela primeira vez."),
    ("camada", Genero.FEMININO, "Nível ou faixa sobreposta a outras dentro de uma estrutura."),
    ("ramo", Genero.MASCULINO, "Parte que se divide a partir de um tronco comum, real ou de conhecimento."),
    ("encontro", Genero.MASCULINO, "Momento em que duas ou mais coisas ou pessoas se juntam num mesmo ponto."),
    # Achado real ao auditar o lote anterior (pergunta direta do autor sobre
    # lote maior): "objetivo" só tinha a leitura ADJETIVO, mas o uso mais
    # comum no dia a dia é SUBSTANTIVO ("qual é o seu objetivo?") -- gap de
    # completude real, corrigido com segunda leitura (mesmo padrão de dupla
    # classe já usado por "substantivo"/"quadrado").
    ("objetivo", Genero.MASCULINO, "Resultado que se pretende alcançar através de uma ação ou esforço."),
    # Vigésimo segundo lote de nomes do corpus amplo (Fase 3/4, corte
    # seguinte) -- lote pequeno de novo, cada sentido conferido com
    # cuidado antes de escolher (lição do "objetivo" no lote anterior).
    ("alteração", Genero.FEMININO, "Mudança que se faz em algo já existente."),
    ("contraparte", Genero.FEMININO, "Pessoa ou elemento que corresponde ao outro lado de uma relação ou acordo."),
    # Vigésimo terceiro lote de nomes do corpus amplo (Fase 3/4, corte
    # seguinte) -- lote grande autorizado pelo autor (massa só pra
    # vocabulário puro, teste no fim, nunca pra regra do motor).
    ("verificação", Genero.FEMININO, "Ato de conferir se algo é verdadeiro, correto ou está conforme o esperado."),
    ("abertura", Genero.FEMININO, "Espaço ou passagem que permite entrada, saída ou início de algo."),
    ("figura", Genero.FEMININO, "Forma visível de algo, ou representação gráfica de uma ideia ou objeto."),
    ("necessidade", Genero.FEMININO, "Aquilo que é preciso ter ou fazer para que algo exista ou funcione."),
    ("transição", Genero.FEMININO, "Passagem de um estado, fase ou lugar para outro."),
    ("arco", Genero.MASCULINO, "Curva contínua entre dois pontos, ou estrutura curva que sustenta um peso."),
    ("assunto", Genero.MASCULINO, "Aquilo sobre que se fala, escreve ou pensa."),
    ("circunstância", Genero.FEMININO, "Condição ou fato que acompanha e influencia uma situação."),
    ("disciplina", Genero.FEMININO, "Área organizada de conhecimento ou estudo; ou comportamento regrado e controlado."),
    ("falta", Genero.FEMININO, "Ausência de algo que deveria estar presente."),
    ("tamanho", Genero.MASCULINO, "Medida das dimensões de algo."),
    ("trecho", Genero.MASCULINO, "Parte contínua e delimitada de um todo maior, como um texto ou caminho."),
    ("volume", Genero.MASCULINO, "Quantidade de espaço ocupado por algo em três dimensões, ou intensidade de um som."),
    ("direção", Genero.FEMININO, "Sentido para o qual algo se orienta ou se move."),
    ("fator", Genero.MASCULINO, "Elemento que contribui para produzir um resultado ou efeito."),
    ("interface", Genero.FEMININO, "Ponto de contacto onde dois sistemas ou partes se comunicam."),
    ("pilha", Genero.FEMININO, "Conjunto de objetos colocados uns sobre os outros; dispositivo que armazena energia elétrica."),
    # Vigésimo sexto lote de nomes do corpus amplo (modo rápido, sem
    # rodar suíte a cada corte -- autorizado pelo autor; palavra
    # confirmada ausente e definição própria continuam obrigatórias).
    ("falha", Genero.FEMININO, "Erro ou defeito que impede algo de funcionar como deveria."),
    ("conflito", Genero.MASCULINO, "Situação de choque entre elementos, ideias ou interesses opostos."),
    ("competência", Genero.FEMININO, "Capacidade de realizar bem uma tarefa determinada."),
    ("frequência", Genero.FEMININO, "Número de vezes que algo ocorre num intervalo dado."),
    ("interação", Genero.FEMININO, "Ação recíproca entre duas ou mais partes."),
    ("semelhança", Genero.FEMININO, "Qualidade do que se parece com outra coisa em algum aspecto."),
    ("índice", Genero.MASCULINO, "Número ou marca que indica a posição ou o valor de algo dentro de um conjunto."),
    ("bloqueio", Genero.MASCULINO, "Ato de impedir a passagem ou o avanço de algo."),
    ("centro", Genero.MASCULINO, "Ponto igualmente distante de todos os pontos de uma figura ou espaço."),
    ("distribuição", Genero.FEMININO, "Modo como algo é repartido entre várias partes ou elementos."),
    ("espécie", Genero.FEMININO, "Categoria que agrupa seres ou coisas com características comuns."),
    ("identificação", Genero.FEMININO, "Ato de reconhecer algo ou alguém como sendo o que é."),
    ("regressão", Genero.FEMININO, "Retorno a um estado anterior, ou relação estatística entre variáveis."),
    ("perífrase", Genero.FEMININO, "Construção que usa várias palavras para exprimir o que uma só poderia dizer."),
    # Vigésimo nono lote de nomes do corpus amplo (modo rápido).
    ("restrição", Genero.FEMININO, "Condição que limita o alcance ou a aplicação de algo."),
    ("tratamento", Genero.MASCULINO, "Modo como algo ou alguém é cuidado, processado ou abordado."),
    ("unicidade", Genero.FEMININO, "Propriedade do que é único, sem outro igual possível."),
    ("adequação", Genero.FEMININO, "Qualidade do que se ajusta corretamente a uma situação ou exigência."),
    ("contraexemplo", Genero.MASCULINO, "Caso concreto que mostra que uma afirmação geral é falsa."),
    ("empréstimo", Genero.MASCULINO, "Ato de ceder algo por tempo determinado, com expectativa de devolução."),
    ("interlocutor", Genero.MASCULINO, "Pessoa com quem se fala numa conversa ou troca de ideias."),
    ("mar", Genero.MASCULINO, "Grande extensão de água salgada que cobre parte da superfície terrestre."),
    ("passagem", Genero.FEMININO, "Caminho ou espaço por onde se passa de um lugar a outro."),
    ("proximidade", Genero.FEMININO, "Qualidade do que está perto no espaço, no tempo ou na relação."),
    ("água", Genero.FEMININO, "Líquido incolor e essencial à vida, formado por hidrogénio e oxigénio."),
    ("atalho", Genero.MASCULINO, "Caminho mais curto que o percurso normal para chegar a um lugar."),
    ("centralidade", Genero.FEMININO, "Medida de quão central um elemento é dentro de uma rede ou estrutura."),
    ("comprimento", Genero.MASCULINO, "Medida da maior dimensão de algo, de uma ponta a outra."),
    # Trigésimo primeiro lote de nomes do corpus amplo (modo rápido).
    ("fim", Genero.MASCULINO, "Ponto em que algo termina, ou objetivo para o qual algo se faz."),
    ("precisão", Genero.FEMININO, "Grau de exatidão com que algo é medido ou expresso."),
    ("expansão", Genero.FEMININO, "Ato de tornar algo maior ou mais amplo."),
    ("decomposição", Genero.FEMININO, "Separação de um todo nas partes que o compõem."),
    ("terminação", Genero.FEMININO, "Parte final de uma palavra ou construção."),
    ("quantificador", Genero.MASCULINO, "Palavra que indica quantidade de forma precisa ou vaga."),
    ("retângulo", Genero.MASCULINO, "Quadrilátero com quatro ângulos retos e lados opostos iguais."),
    ("variância", Genero.FEMININO, "Medida de quanto os valores de um conjunto se afastam da média."),
    ("inequação", Genero.FEMININO, "Relação matemática que compara duas expressões por desigualdade."),
    # Trigésimo terceiro lote de nomes do corpus amplo (modo rápido).
    ("versão", Genero.FEMININO, "Forma particular em que algo se apresenta, entre várias possíveis."),
    ("acontecimento", Genero.MASCULINO, "Fato que ocorre num momento determinado."),
    ("ambiente", Genero.MASCULINO, "Conjunto de condições que rodeiam e envolvem algo ou alguém."),
    ("anterioridade", Genero.FEMININO, "Qualidade do que vem antes no tempo em relação a outra coisa."),
    ("ciclo", Genero.MASCULINO, "Sequência de eventos que se repete sempre na mesma ordem."),
    ("compatibilidade", Genero.FEMININO, "Capacidade de duas ou mais coisas existirem ou funcionarem juntas sem conflito."),
    ("compreensão", Genero.FEMININO, "Capacidade de entender o sentido de algo."),
    ("confiança", Genero.FEMININO, "Crença de que algo ou alguém é verdadeiro ou seguro."),
    ("deslocamento", Genero.MASCULINO, "Mudança de posição de um ponto a outro."),
    # Trigésimo quarto lote de nomes do corpus amplo (modo rápido).
    ("grandeza", Genero.FEMININO, "Quantidade que pode ser medida e expressa por um número."),
    ("expoente", Genero.MASCULINO, "Número que indica quantas vezes uma base se multiplica por si mesma."),
    ("irregularidade", Genero.FEMININO, "Desvio em relação a um padrão ou regra esperada."),
    ("produtividade", Genero.FEMININO, "Capacidade de produzir resultado em relação ao esforço ou tempo investido."),
    ("profundidade", Genero.FEMININO, "Distância medida de cima para baixo, ou grau de complexidade de algo."),
    ("recorrência", Genero.FEMININO, "Repetição de algo ao longo do tempo, ou definição em termos de si mesma."),
    ("contradição", Genero.FEMININO, "Afirmação que nega outra, tornando as duas incompatíveis ao mesmo tempo."),
    ("eliminação", Genero.FEMININO, "Ato de remover algo de um conjunto ou processo."),
    ("discriminante", Genero.MASCULINO, "Valor que determina a natureza das soluções de uma equação."),
    ("homomorfismo", Genero.MASCULINO, "Função entre estruturas que preserva as suas operações."),
    ("certeza", Genero.FEMININO, "Estado de saber algo sem dúvida possível."),
    ("peso", Genero.MASCULINO, "Força com que um corpo é atraído pela gravidade; ou importância relativa de algo."),
    ("ponta", Genero.FEMININO, "Extremidade estreita ou aguda de algo."),
    ("propósito", Genero.MASCULINO, "Intenção com que algo é feito."),
    # Trigésimo quinto lote de nomes do corpus amplo (modo rápido).
    ("representação", Genero.FEMININO, "Forma que expressa ou substitui algo, tornando-o presente de outro modo."),
    ("transcrição", Genero.FEMININO, "Passagem de um registo para outra forma escrita, mantendo o conteúdo."),
    ("verificador", Genero.MASCULINO, "Aquilo ou aquele que confere se algo está correto."),
    ("ajuste", Genero.MASCULINO, "Pequena mudança feita para corrigir ou adaptar algo."),
    ("cabeçalho", Genero.MASCULINO, "Parte inicial de um texto ou documento, que identifica o que segue."),
    ("carro", Genero.MASCULINO, "Veículo com rodas usado para transportar pessoas ou cargas."),
    ("componente", Genero.MASCULINO, "Elemento que faz parte de um conjunto maior."),
    ("metro", Genero.MASCULINO, "Unidade de medida de comprimento no sistema internacional."),
    ("lote", Genero.MASCULINO, "Conjunto de itens tratados ou entregues de uma vez."),
    ("prosa", Genero.FEMININO, "Forma de escrita corrida, sem estrutura de verso."),
    ("falante", Genero.MASCULINO, "Pessoa que fala uma língua determinada."),
    ("fatorial", Genero.MASCULINO, "Produto de todos os números inteiros positivos até um dado número."),
    ("pertencimento", Genero.MASCULINO, "Relação de fazer parte de um conjunto ou grupo."),
    ("arredondamento", Genero.MASCULINO, "Ajuste de um número para o valor mais próximo dentro de uma precisão dada."),
    # Trigésimo sexto lote de nomes do corpus amplo (modo rápido).
    ("dúvida", Genero.FEMININO, "Estado de não ter certeza sobre algo."),
    ("honestidade", Genero.FEMININO, "Qualidade de quem age e fala com verdade, sem enganar."),
    ("monografia", Genero.FEMININO, "Texto que trata em profundidade um único assunto."),
    ("nota", Genero.FEMININO, "Registo curto de uma informação, ou valor atribuído a uma avaliação."),
    ("média", Genero.FEMININO, "Valor obtido ao somar um conjunto de números e dividir pela quantidade deles."),
    ("isomorfismo", Genero.MASCULINO, "Correspondência que preserva a estrutura entre dois objetos matemáticos."),
    ("encadeamento", Genero.MASCULINO, "Ligação sequencial entre elementos, cada um dependendo do anterior."),
    ("macroestrutura", Genero.FEMININO, "Organização geral e ampla de um texto ou sistema."),
    ("cor", Genero.FEMININO, "Sensação visual produzida pela luz refletida num objeto."),
    ("facto", Genero.MASCULINO, "Acontecimento real e verificável."),
    # Trigésimo sétimo lote de nomes do corpus amplo (modo rápido).
    ("potenciação", Genero.FEMININO, "Operação que multiplica um número por ele mesmo um número determinado de vezes."),
    ("reconhecimento", Genero.MASCULINO, "Ato de identificar algo como já conhecido ou válido."),
    ("subjuntivo", Genero.MASCULINO, "Modo verbal que expressa dúvida, desejo ou hipótese."),
    ("teclado", Genero.MASCULINO, "Conjunto de teclas usado para introduzir dados ou tocar um instrumento."),
    ("universalidade", Genero.FEMININO, "Qualidade do que se aplica a todos os casos, sem exceção."),
    ("adaptação", Genero.FEMININO, "Ajuste feito para que algo passe a servir a uma nova condição."),
    ("alternativa", Genero.FEMININO, "Opção que pode substituir outra numa escolha."),
    ("associatividade", Genero.FEMININO, "Propriedade de uma operação em que o agrupamento dos termos não altera o resultado."),
    ("logaritmo", Genero.MASCULINO, "Expoente ao qual uma base fixa deve ser elevada para produzir um número dado."),
    ("emparelhamento", Genero.MASCULINO, "Associação de elementos de dois conjuntos em pares correspondentes."),
    # Trigésimo oitavo lote de nomes do corpus amplo (modo rápido).
    ("comportamento", Genero.MASCULINO, "Modo como algo ou alguém age em determinada situação."),
    ("convergência", Genero.FEMININO, "Aproximação progressiva de valores ou elementos até um mesmo ponto."),
    ("crítica", Genero.FEMININO, "Julgamento que aponta qualidades ou falhas de algo."),
    ("denominador", Genero.MASCULINO, "Número que indica em quantas partes um todo foi dividido, numa fração."),
    ("escala", Genero.FEMININO, "Sequência ordenada de valores usada para medir ou comparar algo."),
    ("janela", Genero.FEMININO, "Abertura numa parede que permite entrada de luz e ar."),
    ("obra", Genero.FEMININO, "Produto do trabalho criativo ou construtivo de alguém."),
    ("perda", Genero.FEMININO, "Ato de deixar de ter algo que antes se possuía."),
    ("poesia", Genero.FEMININO, "Forma de expressão que usa ritmo, sonoridade e imagem para construir sentido."),
    ("prática", Genero.FEMININO, "Aplicação real de um conhecimento ou habilidade."),
    ("região", Genero.FEMININO, "Parte delimitada de um espaço maior."),
    ("legado", Genero.MASCULINO, "Aquilo que é deixado por alguém ou algo anterior, para quem vem depois."),
    ("falácia", Genero.FEMININO, "Raciocínio que parece válido mas contém um erro lógico."),
    ("planaridade", Genero.FEMININO, "Propriedade de um grafo que pode ser desenhado sem arestas se cruzarem."),
    ("polinômio", Genero.MASCULINO, "Expressão formada pela soma de termos com potências de uma variável."),
    # Quadragésimo primeiro lote de nomes do corpus amplo (modo rápido).
    ("jeito", Genero.MASCULINO, "Modo próprio de fazer ou de ser de algo ou alguém."),
    ("silêncio", Genero.MASCULINO, "Ausência de som."),
    ("validade", Genero.FEMININO, "Qualidade do que é reconhecido como correto ou aceite dentro de certas regras."),
    ("acréscimo", Genero.MASCULINO, "Quantidade que se soma a algo já existente."),
    ("banco", Genero.MASCULINO, "Instituição que guarda e movimenta dinheiro; ou assento comprido."),
    ("conferência", Genero.FEMININO, "Reunião em que se discute ou apresenta um tema perante um público."),
    ("configuração", Genero.FEMININO, "Modo como as partes de algo estão dispostas ou ajustadas."),
    ("rodada", Genero.FEMININO, "Cada repetição completa dentro de uma sequência de turnos."),
    ("troca", Genero.FEMININO, "Ato de dar uma coisa e receber outra em seu lugar."),
    # Quadragésimo segundo lote de nomes do corpus amplo (modo rápido).
    ("confusão", Genero.FEMININO, "Estado em que elementos se misturam sem ordem clara, dificultando distinção."),
    ("cópia", Genero.FEMININO, "Reprodução que repete exatamente um original."),
    ("desejo", Genero.MASCULINO, "Vontade de obter ou realizar algo."),
    ("formato", Genero.MASCULINO, "Modo específico como algo é organizado ou apresentado."),
    ("homem", Genero.MASCULINO, "Ser humano adulto do sexo masculino."),
    ("hora", Genero.FEMININO, "Unidade de tempo equivalente a sessenta minutos."),
    ("localização", Genero.FEMININO, "Determinação do lugar exato onde algo se encontra."),
    ("exceção", Genero.FEMININO, "Caso que foge da regra geral."),
    ("chat", Genero.MASCULINO, "Conversa em tempo real por mensagens escritas, geralmente numa interface digital."),
    # Quadragésimo terceiro lote de nomes do corpus amplo (modo rápido).
    ("normalização", Genero.FEMININO, "Ajuste de algo a um padrão comum."),
    ("notação", Genero.FEMININO, "Sistema de símbolos usado para representar algo de forma precisa."),
    ("proporção", Genero.FEMININO, "Relação constante entre duas quantidades."),
    ("rastreabilidade", Genero.FEMININO, "Capacidade de seguir a origem e o percurso de algo até à sua fonte."),
    ("recorte", Genero.MASCULINO, "Parte separada de um todo maior, geralmente cortada."),
    ("repertório", Genero.MASCULINO, "Conjunto de elementos disponíveis para uso numa área ou atividade."),
    ("pedra", Genero.FEMININO, "Material sólido e duro, formado naturalmente a partir de minerais."),
    ("testemunha", Genero.FEMININO, "Pessoa que presenciou um facto e pode relatá-lo."),
    ("recurso", Genero.MASCULINO, "Meio disponível para alcançar um objetivo ou resolver uma necessidade."),
    ("coda", Genero.FEMININO, "Consoante ou consoantes que fecham uma sílaba depois da vogal central."),
    ("seno", Genero.MASCULINO, "Razão entre o cateto oposto e a hipotenusa num triângulo retângulo."),
    ("cosseno", Genero.MASCULINO, "Razão entre o cateto adjacente e a hipotenusa num triângulo retângulo."),
    ("favor", Genero.MASCULINO, "Ajuda ou gentileza feita a alguém."),
    ("monossílabo", Genero.MASCULINO, "Palavra formada por uma única sílaba."),
    ("paridade", Genero.FEMININO, "Propriedade de um número ser par ou ímpar."),
    ("amostra", Genero.FEMININO, "Parte de um conjunto usada para representar o todo numa análise."),
    ("aparelho", Genero.MASCULINO, "Dispositivo construído para executar uma função específica."),
    ("folha", Genero.FEMININO, "Parte fina e achatada de uma planta, ou pedaço de papel."),
    ("mente", Genero.FEMININO, "Capacidade de pensar, raciocinar e ter consciência."),
    # Quadragésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("estrela", Genero.FEMININO, "Corpo celeste que produz luz própria através de reações nucleares."),
    ("fruta", Genero.FEMININO, "Parte comestível e geralmente doce de uma planta, desenvolvida a partir da flor."),
    ("coisa", Genero.FEMININO, "Objeto, entidade ou assunto indeterminado, referido sem se nomear especificamente."),
    ("momento", Genero.MASCULINO, "Instante ou ocasião determinada no tempo."),
    ("animal", Genero.MASCULINO, "Ser vivo capaz de se mover e que se alimenta de matéria orgânica."),
    ("interior", Genero.MASCULINO, "Parte de dentro de algo, oposta à superfície ou à borda."),
    ("custo", Genero.MASCULINO, "Valor ou esforço necessário para obter ou realizar algo."),
    ("esquerda", Genero.FEMININO, "Lado do corpo ou do espaço oposto ao lado direito."),
    ("direita", Genero.FEMININO, "Lado do corpo ou do espaço oposto ao lado esquerdo."),
    ("fragmento", Genero.MASCULINO, "Parte pequena e separada de algo que originalmente era maior ou inteiro."),
    ("largura", Genero.FEMININO, "Medida de um lado a outro, perpendicular ao comprimento."),
    ("julgamento", Genero.MASCULINO, "Ato de julgar ou avaliar algo, formando uma opinião ou decisão."),
    ("integridade", Genero.FEMININO, "Qualidade do que está completo, ou de quem age de forma honesta e coerente."),
    ("orientação", Genero.FEMININO, "Indicação de direção ou rumo a seguir."),
    ("percurso", Genero.MASCULINO, "Caminho ou trajeto percorrido de um ponto a outro."),
    ("posse", Genero.FEMININO, "Ato ou direito de ter algo sob controlo próprio."),
    ("presença", Genero.FEMININO, "Facto de estar presente, fisicamente ou não, num determinado lugar ou momento."),
    ("princípio", Genero.MASCULINO, "Início de algo, ou regra fundamental que serve de base a um raciocínio."),
    ("visão", Genero.FEMININO, "Capacidade de ver, ou modo de perceber e interpretar algo."),
    ("vizinho", Genero.MASCULINO, "Pessoa que mora perto de outra, ou que está próxima no espaço."),
    ("aceitação", Genero.FEMININO, "Ato de aceitar algo ou alguém."),
    ("algarismo", Genero.MASCULINO, "Símbolo usado para representar um número."),
    ("cavidade", Genero.FEMININO, "Espaço vazio no interior de algo."),
    ("comentário", Genero.MASCULINO, "Observação ou opinião feita sobre algo."),
    ("contorno", Genero.MASCULINO, "Linha que delimita a forma exterior de algo."),
    ("correlação", Genero.FEMININO, "Relação em que a variação de uma coisa está associada à variação de outra."),
    ("correspondência", Genero.FEMININO, "Relação de equivalência entre coisas, ou troca de mensagens escritas entre pessoas."),
    ("corretor", Genero.MASCULINO, "Aquele ou aquilo que identifica e corrige erros."),
    ("destaque", Genero.MASCULINO, "Realce dado a algo para chamar a atenção sobre ele."),
    ("dimensão", Genero.FEMININO, "Medida de extensão de algo numa determinada direção."),
    ("disposição", Genero.FEMININO, "Modo como algo está arranjado, ou vontade de fazer algo."),
    ("documentação", Genero.FEMININO, "Conjunto de documentos reunidos sobre um assunto."),
    ("instituição", Genero.FEMININO, "Organização criada e estabelecida com um propósito determinado."),
    ("instrumento", Genero.MASCULINO, "Objeto construído ou usado para realizar uma tarefa específica."),
    ("inversão", Genero.FEMININO, "Ato de inverter, trocando a ordem ou o sentido de algo."),
    ("maturidade", Genero.FEMININO, "Estado de quem ou do que atingiu pleno desenvolvimento."),
    ("omissão", Genero.FEMININO, "Ausência de algo que deveria estar presente; ato de não fazer o que era esperado."),
    ("oráculo", Genero.MASCULINO, "Fonte considerada capaz de dar respostas ou previsões fiáveis."),
    ("polígono", Genero.MASCULINO, "Figura plana fechada, formada por segmentos de reta."),
    ("prioridade", Genero.FEMININO, "Aquilo que deve ser tratado ou considerado antes do resto."),
    ("sobreposição", Genero.FEMININO, "Ato de colocar algo por cima de outra coisa, ocupando parcialmente o mesmo espaço."),
    ("superioridade", Genero.FEMININO, "Qualidade de quem ou do que é superior a outra coisa."),
    ("subconjunto", Genero.MASCULINO, "Conjunto cujos elementos pertencem todos a outro conjunto maior."),
    ("posto", Genero.MASCULINO, "Local ou posição ocupada para desempenhar uma função."),
    ("porcentagem", Genero.FEMININO, "Proporção expressa em partes de cem."),
    ("mecânica", Genero.FEMININO, "Ramo da física que estuda o movimento e as forças que o causam."),
    ("planejamento", Genero.MASCULINO, "Ato de planejar, organizando etapas para atingir um objetivo."),
    ("café", Genero.MASCULINO, "Bebida feita a partir dos grãos torrados da planta do mesmo nome."),
    ("cobertura", Genero.FEMININO, "Camada que recobre algo, ou alcance de um serviço ou seguro."),
    ("massa", Genero.FEMININO, "Quantidade de matéria de um corpo, ou mistura densa de ingredientes."),
    ("semigrupo", Genero.MASCULINO, "Conjunto com uma operação associativa, sem exigir elemento neutro."),
    # Quadragésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    ("mensagem", Genero.FEMININO, "Conteúdo comunicado de um emissor para um recetor, através de um meio."),
    ("mesa", Genero.FEMININO, "Móvel com uma superfície plana e elevada, apoiada em pernas."),
    ("membro", Genero.MASCULINO, "Parte que integra um conjunto, grupo ou corpo maior."),
    ("pensamento", Genero.MASCULINO, "Atividade ou produto da mente ao processar ideias."),
    ("respeito", Genero.MASCULINO, "Consideração e atenção dadas a algo ou alguém pelo seu valor."),
    ("satisfação", Genero.FEMININO, "Sentimento de contentamento por algo ter correspondido ao esperado."),
    ("transferência", Genero.FEMININO, "Ato de passar algo de um lugar, pessoa ou estado para outro."),
    ("turma", Genero.FEMININO, "Grupo de pessoas reunidas para uma mesma atividade, geralmente de ensino."),
    ("turno", Genero.MASCULINO, "Período de tempo destinado a uma atividade, dentro de uma sequência organizada."),
    ("candidato", Genero.MASCULINO, "Pessoa ou coisa que se apresenta ou é considerada para ocupar uma posição."),
    ("centena", Genero.FEMININO, "Conjunto de cem unidades."),
    ("cima", Genero.FEMININO, "Parte ou posição mais alta de algo."),
    ("cuidado", Genero.MASCULINO, "Atenção e precaução tomadas para evitar erro ou dano."),
    ("destino", Genero.MASCULINO, "Lugar para onde alguém ou algo se dirige, ou rumo que os acontecimentos tomam."),
    ("ferramenta", Genero.FEMININO, "Objeto ou meio utilizado para realizar uma tarefa."),
    ("geração", Genero.FEMININO, "Ato de gerar algo, ou conjunto de pessoas nascidas numa mesma época."),
    ("maneira", Genero.FEMININO, "Modo específico como algo é feito ou acontece."),
    ("margem", Genero.FEMININO, "Espaço ou faixa lateral que delimita algo, ou diferença tolerada."),
    ("melhoria", Genero.FEMININO, "Mudança que torna algo melhor do que estava antes."),
    ("minuto", Genero.MASCULINO, "Unidade de tempo equivalente a sessenta segundos."),
    ("movimento", Genero.MASCULINO, "Mudança de posição de algo no espaço ao longo do tempo."),
    ("parábola", Genero.FEMININO, "Curva plana formada pelos pontos equidistantes de um foco e de uma reta; narrativa alegórica com ensinamento moral."),
    ("pasta", Genero.FEMININO, "Recipiente ou invólucro usado para guardar e organizar documentos ou ficheiros."),
    ("pato", Genero.MASCULINO, "Ave aquática de bico achatado, comum em lagos e rios."),
    ("processamento", Genero.MASCULINO, "Ato de processar; conjunto de operações realizadas sobre algo para o transformar."),
    ("retorno", Genero.MASCULINO, "Ato de voltar a um ponto de partida, ou resultado devolvido por um processo."),
    ("rótulo", Genero.MASCULINO, "Etiqueta ou nome usado para identificar e classificar algo."),
    ("série", Genero.FEMININO, "Sucessão ordenada de elementos relacionados entre si."),
    ("sucessão", Genero.FEMININO, "Sequência de elementos que se seguem uns aos outros numa ordem."),
    ("tarefa", Genero.FEMININO, "Trabalho ou atividade que deve ser realizada."),
    ("vizinhança", Genero.FEMININO, "Área ou conjunto de elementos próximos de um ponto de referência."),
    ("acesso", Genero.MASCULINO, "Possibilidade ou meio de chegar a um lugar, recurso ou informação."),
    ("beleza", Genero.FEMININO, "Qualidade daquilo que agrada esteticamente."),
    ("capital", Genero.FEMININO, "Cidade principal de um país ou região, onde está sediado o governo."),
    ("capítulo", Genero.MASCULINO, "Cada uma das partes em que se divide um livro ou texto mais extenso."),
    ("companhia", Genero.FEMININO, "Presença de alguém que acompanha, ou empresa organizada para uma atividade económica."),
    ("conselho", Genero.MASCULINO, "Sugestão dada a alguém sobre o que fazer, ou grupo reunido para deliberar."),
    ("convite", Genero.MASCULINO, "Pedido feito a alguém para participar de algo."),
    ("data", Genero.FEMININO, "Indicação do dia, mês e ano em que algo ocorre ou ocorreu."),
    ("desempenho", Genero.MASCULINO, "Modo como algo ou alguém realiza uma tarefa, medido pelo resultado."),
    # Quadragésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    ("relato", Genero.MASCULINO, "Narração de um facto ou acontecimento."),
    ("risco", Genero.MASCULINO, "Possibilidade de que algo negativo aconteça."),
    ("rota", Genero.FEMININO, "Caminho definido para ir de um lugar a outro."),
    ("senhor", Genero.MASCULINO, "Forma de tratamento respeitoso dirigida a um homem, ou homem adulto."),
    ("semana", Genero.FEMININO, "Período de sete dias consecutivos."),
    ("suporte", Genero.MASCULINO, "Estrutura ou meio que sustenta ou auxilia algo."),
    ("totalidade", Genero.FEMININO, "Conjunto de todas as partes de algo, sem exceção."),
    ("treino", Genero.MASCULINO, "Prática repetida de uma atividade para desenvolver uma capacidade."),
    ("universo", Genero.MASCULINO, "Conjunto de tudo o que existe, ou domínio total considerado numa análise."),
    ("alcance", Genero.MASCULINO, "Distância ou extensão até onde algo consegue chegar ou atuar."),
    ("chuva", Genero.FEMININO, "Água que cai da atmosfera em forma de gotas."),
    ("curso", Genero.MASCULINO, "Sequência organizada de conteúdo destinada a ensinar algo, ou percurso de um rio."),
    ("desenho", Genero.MASCULINO, "Representação gráfica feita por meio de linhas e traços."),
    ("envio", Genero.MASCULINO, "Ato de mandar algo para um destino."),
    ("experiência", Genero.FEMININO, "Vivência ou conhecimento adquirido pela prática."),
    ("hierarquia", Genero.FEMININO, "Organização de elementos por níveis de importância ou autoridade."),
    ("importância", Genero.FEMININO, "Qualidade do que tem valor ou relevância significativa."),
    ("legenda", Genero.FEMININO, "Texto explicativo que acompanha uma imagem, gráfico ou vídeo."),
    ("limpeza", Genero.FEMININO, "Ato de tornar algo limpo, livre de sujidade."),
    ("manual", Genero.MASCULINO, "Livro ou documento que explica como usar ou fazer algo."),
    ("rigor", Genero.MASCULINO, "Exatidão e precisão aplicadas com severidade."),
    ("roteiro", Genero.MASCULINO, "Sequência planeada de passos ou de cenas a seguir."),
    ("sala", Genero.FEMININO, "Divisão de uma casa ou edifício destinada a uma atividade específica."),
    ("quilo", Genero.MASCULINO, "Unidade de massa equivalente a mil gramas."),
    # Quadragésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    # "lápis" ficou de fora deliberadamente: `_plural_substantivo` ainda
    # não distingue "-s" final átono invariável (lápis/ônibus/vírus) de
    # "-s" tônico que ganha "-es" (mês->meses, gás->gases, país->países)
    # -- regra fechada por palavra, não sufixo, ainda por escrever com
    # cuidado (mesma classe de "sair"/"cair" antes desta sessão).
    ("correio", Genero.MASCULINO, "Sistema ou serviço usado para enviar e receber cartas e encomendas."),
    ("coleção", Genero.FEMININO, "Conjunto de objetos reunidos por um critério comum."),
    ("confirmação", Genero.FEMININO, "Ato de confirmar, tornando certo algo que estava em dúvida."),
    ("dente", Genero.MASCULINO, "Estrutura dura na boca usada para morder e mastigar."),
    ("duração", Genero.FEMININO, "Tempo que algo leva a acontecer ou a existir."),
    ("estudante", Genero.COMUM, "Pessoa que estuda, geralmente numa instituição de ensino."),
    ("expectativa", Genero.FEMININO, "Previsão ou esperança sobre o que vai acontecer."),
    ("grama", Genero.MASCULINO, "Unidade de massa do sistema métrico, base do quilograma."),
    ("maioria", Genero.FEMININO, "Parte maior de um conjunto, mais de metade do total."),
    ("moral", Genero.FEMININO, "Conjunto de princípios que orientam o que é considerado certo ou errado."),
    ("obstáculo", Genero.MASCULINO, "Aquilo que dificulta ou impede a passagem ou o progresso."),
    ("prato", Genero.MASCULINO, "Utensílio raso onde se serve comida, ou refeição preparada."),
    ("progresso", Genero.MASCULINO, "Avanço em direção a um estado melhor ou mais desenvolvido."),
    ("roupa", Genero.FEMININO, "Peça ou conjunto de peças usadas para vestir o corpo."),
    ("chave", Genero.FEMININO, "Objeto usado para abrir ou fechar uma fechadura, ou elemento que dá acesso a algo."),
    ("comando", Genero.MASCULINO, "Ordem dada para que algo seja executado."),
    ("declaração", Genero.FEMININO, "Ato de declarar algo, tornando-o publicamente conhecido."),
    ("autonomia", Genero.FEMININO, "Capacidade de agir ou decidir por si mesmo, sem depender de outros."),
    ("diamante", Genero.MASCULINO, "Mineral extremamente duro, formado por carbono cristalizado, usado em joalharia."),
    # Quadragésimo oitavo lote do corpus amplo (modo massa, meta 50.000).
    ("acordo", Genero.MASCULINO, "Entendimento comum alcançado entre duas ou mais partes."),
    ("altura", Genero.FEMININO, "Medida de uma extremidade a outra na vertical."),
    ("amor", Genero.MASCULINO, "Sentimento profundo de afeto ou dedicação por alguém ou algo."),
    ("arranjo", Genero.MASCULINO, "Disposição organizada de elementos, ou combinação acordada entre partes."),
    ("aprendizagem", Genero.FEMININO, "Processo de adquirir conhecimento ou habilidade."),
    ("bateria", Genero.FEMININO, "Dispositivo que armazena e fornece energia elétrica, ou conjunto de instrumentos de percussão."),
    ("cidade", Genero.FEMININO, "Área urbana com grande concentração de população e infraestrutura."),
    ("circunferência", Genero.FEMININO, "Linha curva fechada cujos pontos estão todos à mesma distância de um centro."),
    ("comunicação", Genero.FEMININO, "Ato de transmitir informação entre um emissor e um recetor."),
    ("coração", Genero.MASCULINO, "Órgão que bombeia sangue pelo corpo, ou centro simbólico dos sentimentos."),
    ("esquema", Genero.MASCULINO, "Representação simplificada da estrutura ou organização de algo."),
    ("influência", Genero.FEMININO, "Capacidade de afetar ou orientar o comportamento ou pensamento de algo ou alguém."),
    ("matéria", Genero.FEMININO, "Substância que constitui os corpos físicos, ou assunto tratado."),
    ("rato", Genero.MASCULINO, "Pequeno roedor de cauda longa, ou dispositivo apontador de computador."),
    ("estabilidade", Genero.FEMININO, "Qualidade do que se mantém firme e sem grandes variações."),
    ("excelência", Genero.FEMININO, "Qualidade do que é notavelmente superior."),
    ("independência", Genero.FEMININO, "Estado de quem ou do que não depende de outro para existir ou agir."),
    ("possibilidade", Genero.FEMININO, "Qualidade do que pode acontecer, existir ou ser feito."),
    ("porquê", Genero.MASCULINO, "Motivo ou razão de algo."),
    ("axioma", Genero.MASCULINO, "Afirmação aceita como ponto de partida, sem precisar de prova."),
    ("status", Genero.MASCULINO, "Situação ou posição de algo ou alguém num dado momento."),
    # Quadragésimo nono lote do corpus amplo (modo massa, meta 50.000).
    ("arquivo", Genero.MASCULINO, "Conjunto organizado de documentos ou dados guardados para consulta futura."),
    ("atividade", Genero.FEMININO, "Ação ou conjunto de ações realizadas com um propósito."),
    ("coluna", Genero.FEMININO, "Elemento vertical que sustenta uma estrutura, ou disposição vertical de dados numa tabela."),
    ("complexidade", Genero.FEMININO, "Qualidade do que é complexo, com muitas partes relacionadas entre si."),
    ("consciência", Genero.FEMININO, "Capacidade de perceber e ter noção de si mesmo e do que se passa em redor."),
    ("edição", Genero.FEMININO, "Ato de editar um texto, ou versão publicada de uma obra."),
    ("faixa", Genero.FEMININO, "Tira estreita e comprida, ou intervalo delimitado de valores."),
    ("género", Genero.MASCULINO, "Categoria que agrupa elementos com características comuns."),
    ("infraestrutura", Genero.FEMININO, "Conjunto de estruturas de base necessárias para o funcionamento de algo."),
    ("instância", Genero.FEMININO, "Nível ou órgão com autoridade para decidir, ou ocorrência concreta de algo mais geral."),
    ("leitor", Genero.MASCULINO, "Pessoa que lê, ou dispositivo que lê informação de um suporte."),
    ("manga", Genero.FEMININO, "Parte da roupa que cobre o braço, ou fruta tropical doce e suculenta."),
    ("mecanismo", Genero.MASCULINO, "Conjunto de peças ou processos que funcionam juntos para produzir um efeito."),
    ("mestria", Genero.FEMININO, "Grande domínio ou habilidade numa área."),
    ("morfologia", Genero.FEMININO, "Estudo da forma e estrutura das palavras, ou forma de um organismo."),
    ("motivo", Genero.MASCULINO, "Razão que leva alguém a agir de determinada forma."),
    ("painel", Genero.MASCULINO, "Superfície plana usada para exibir informação, ou grupo de pessoas reunidas para debater um tema."),
    ("política", Genero.FEMININO, "Conjunto de ações e decisões relativas à organização de uma sociedade."),
    ("proposta", Genero.FEMININO, "Ideia ou plano apresentado para ser considerado ou aceite."),
    ("receita", Genero.FEMININO, "Conjunto de instruções para preparar algo, ou dinheiro recebido."),
    ("tensão", Genero.FEMININO, "Estado de esforço ou pressão, física ou emocional."),
    ("terminal", Genero.MASCULINO, "Ponto final de uma linha ou rede, ou interface de acesso a um sistema."),
    ("conectividade", Genero.FEMININO, "Propriedade de estar ligado, ou grau de ligação entre elementos."),
    ("inferioridade", Genero.FEMININO, "Estado de estar abaixo de outro em grau, valor ou posição."),
    ("lábio", Genero.MASCULINO, "Cada uma das duas bordas móveis da boca."),
    # Quinquagésimo lote do corpus amplo (modo massa, meta 50.000).
    ("botão", Genero.MASCULINO, "Peça pequena usada para acionar um mecanismo, ou para prender roupa."),
    ("emoção", Genero.FEMININO, "Reação afetiva intensa provocada por um estímulo ou situação."),
    ("modificação", Genero.FEMININO, "Ato de modificar, alterando características de algo."),
    ("atribuição", Genero.FEMININO, "Ato de atribuir algo a alguém, ou responsabilidade designada."),
    ("suíte", Genero.FEMININO, "Conjunto de peças relacionadas, como cómodos ou músicas, formando um todo."),
    ("ênfase", Genero.FEMININO, "Destaque dado a algo para reforçar a sua importância."),
    ("cota", Genero.FEMININO, "Parte ou limite atribuído a alguém dentro de um total."),
    ("iteração", Genero.FEMININO, "Repetição de um processo, cada vez usando o resultado da etapa anterior."),
    ("interferência", Genero.FEMININO, "Ação que perturba ou se sobrepõe a algo em curso."),
    ("fusão", Genero.FEMININO, "União de duas ou mais coisas que se tornam uma só."),
    # Quinquagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    ("armada", Genero.FEMININO, "Conjunto organizado de forças militares, especialmente navais."),
    ("característica", Genero.FEMININO, "Traço que distingue e identifica algo ou alguém."),
    ("continuação", Genero.FEMININO, "Parte que segue e dá seguimento a algo já iniciado."),
    ("determinação", Genero.FEMININO, "Firmeza de vontade para alcançar um objetivo, ou ato de determinar algo."),
    ("justificativa", Genero.FEMININO, "Razão apresentada para explicar ou defender uma ação."),
    ("concessão", Genero.FEMININO, "Ato de ceder algo, ou permissão dada."),
    ("estrangeirismo", Genero.MASCULINO, "Palavra ou expressão de outra língua usada dentro de outra."),
    ("medição", Genero.FEMININO, "Ato de medir algo, determinando a sua grandeza."),
    ("auditor", Genero.MASCULINO, "Pessoa que examina e verifica formalmente contas ou processos."),
    ("encaixe", Genero.MASCULINO, "Ajuste entre duas peças que se completam ou combinam."),
    ("assento", Genero.MASCULINO, "Superfície ou móvel destinado a sentar."),
    ("associação", Genero.FEMININO, "União de pessoas ou entidades com um objetivo comum."),
    ("marcação", Genero.FEMININO, "Ato de assinalar algo de forma visível ou registada."),
    ("proeminência", Genero.FEMININO, "Qualidade do que se destaca em relação ao que está à volta."),
    ("avó", Genero.FEMININO, "Mãe do pai ou da mãe de alguém."),
    ("avô", Genero.MASCULINO, "Pai do pai ou da mãe de alguém."),
    ("decidibilidade", Genero.FEMININO, "Propriedade de um problema para o qual existe um procedimento que sempre termina com resposta sim ou não."),
    ("derivada", Genero.FEMININO, "Taxa de variação instantânea de uma função em relação a uma variável."),
    # Quinquagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    ("fingimento", Genero.MASCULINO, "Ato de fingir, simulando algo que não é real."),
    ("rejeição", Genero.FEMININO, "Ato de rejeitar algo ou alguém."),
    ("suspensão", Genero.FEMININO, "Ato de suspender algo temporariamente."),
    ("anotação", Genero.FEMININO, "Nota escrita feita sobre algo, geralmente breve."),
    ("participação", Genero.FEMININO, "Ato de participar em algo."),
    ("diminuição", Genero.FEMININO, "Ato de tornar algo menor em quantidade ou intensidade."),
    ("elaboração", Genero.FEMININO, "Ato de elaborar algo, desenvolvendo-o com cuidado."),
    ("encerramento", Genero.MASCULINO, "Ato de encerrar ou terminar algo."),
    ("exigência", Genero.FEMININO, "Aquilo que é exigido; requisito imposto."),
    ("isolamento", Genero.MASCULINO, "Estado de estar separado ou afastado do resto."),
    ("previsão", Genero.FEMININO, "Ato de prever o que vai acontecer."),
    ("proibição", Genero.FEMININO, "Ato de proibir algo, impedindo que aconteça."),
    ("cancelamento", Genero.MASCULINO, "Ato de cancelar algo, tornando-o sem efeito."),
    ("consistência", Genero.FEMININO, "Qualidade do que é consistente, sem contradições."),
    ("acessibilidade", Genero.FEMININO, "Qualidade do que é acessível."),
    # achado real: "mão" (candidato de alta frequência, palavra
    # fundamental) nunca existiu -- plural irregular já resolvido em
    # `_PLURAIS_AO_IRREGULARES`.
    ("mão", Genero.FEMININO, "Parte do corpo humano na extremidade do braço, usada para segurar e manipular."),
    ("paralelismo", Genero.MASCULINO, "Relação entre elementos que seguem a mesma estrutura ou direção."),
    # Quinquagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("evolução", Genero.FEMININO, "Processo de transformação gradual ao longo do tempo."),
    ("incerteza", Genero.FEMININO, "Estado de não se saber algo com certeza."),
    ("indução", Genero.FEMININO, "Raciocínio que parte de casos particulares para uma conclusão geral."),
    ("interrupção", Genero.FEMININO, "Ato de interromper algo em curso."),
    ("intervenção", Genero.FEMININO, "Ato de intervir numa situação."),
    ("juntura", Genero.FEMININO, "Ponto onde duas partes se unem."),
    ("noção", Genero.FEMININO, "Ideia geral ou conhecimento básico sobre algo."),
    ("ordenação", Genero.FEMININO, "Ato de ordenar, colocando elementos numa sequência determinada."),
    ("partição", Genero.FEMININO, "Divisão de um todo em partes."),
    ("parêntese", Genero.MASCULINO, "Sinal gráfico usado para isolar uma parte do texto ou de uma expressão."),
    ("perceção", Genero.FEMININO, "Capacidade de captar e interpretar informação através dos sentidos."),
    ("reação", Genero.FEMININO, "Resposta provocada por um estímulo ou ação."),
    ("resíduo", Genero.MASCULINO, "Parte que resta depois de um processo, ou resto de uma divisão."),
    ("simplificação", Genero.FEMININO, "Ato de tornar algo mais simples."),
    ("sincronização", Genero.FEMININO, "Ato de fazer com que dois ou mais processos aconteçam ao mesmo tempo ou de forma coordenada."),
    ("transporte", Genero.MASCULINO, "Ato de levar algo ou alguém de um lugar para outro."),
    ("atenção", Genero.FEMININO, "Concentração da mente sobre algo específico."),
    ("atributo", Genero.MASCULINO, "Característica ou propriedade associada a algo."),
    ("anexo", Genero.MASCULINO, "Documento ou ficheiro juntado a outro como complemento."),
    ("cansaço", Genero.MASCULINO, "Estado de fadiga física ou mental."),
    ("criação", Genero.FEMININO, "Ato de criar algo novo."),
    ("diversidade", Genero.FEMININO, "Qualidade do que apresenta variedade."),
    ("dilema", Genero.MASCULINO, "Situação em que é preciso escolher entre duas opções, ambas com consequências difíceis."),
    ("educação", Genero.FEMININO, "Processo de formação e desenvolvimento de conhecimentos e valores."),
    ("camisa", Genero.FEMININO, "Peça de vestuário que cobre a parte superior do corpo, com mangas e botões."),
    ("autocarro", Genero.MASCULINO, "Veículo grande usado para transportar várias pessoas em rotas fixas."),
    ("automóvel", Genero.MASCULINO, "Veículo motorizado usado para transporte em estradas."),
    # Quinquagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    ("dízima", Genero.FEMININO, "Representação decimal com um bloco de algarismos que se repete indefinidamente."),
    ("emissão", Genero.FEMININO, "Ato de emitir algo, lançando-o para fora ou tornando-o público."),
    ("preservação", Genero.FEMININO, "Ato de preservar, mantendo algo em bom estado ou intacto."),
    ("solidez", Genero.FEMININO, "Qualidade do que é sólido, firme e resistente."),
    ("sonoridade", Genero.FEMININO, "Qualidade do que produz som, ou capacidade de soar bem."),
    ("subgrupo", Genero.MASCULINO, "Subconjunto de um grupo que forma, ele próprio, um grupo com a mesma operação."),
    ("valência", Genero.FEMININO, "Número de elementos que um verbo ou átomo exige para se combinar."),
    ("guarda-chuva", Genero.MASCULINO, "Objeto usado para proteger da chuva, formado por uma haste e um tecido que se abre."),
    # Quinquagésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    # Achado real no caminho: `_plural_substantivo` não tratava "-il"
    # tônico ("perfils", errado) -- corrigido (ver função, perfil->perfis).
    # "país" fica de fora por ora, mesmo motivo de "lápis": "-s" tônico
    # que ganha "-es" (país->países) é exceção fechada, não sufixo geral.
    ("edifício", Genero.MASCULINO, "Construção com paredes e cobertura, destinada a habitação ou outra atividade."),
    ("esclarecimento", Genero.MASCULINO, "Explicação que torna algo mais claro."),
    ("esforço", Genero.MASCULINO, "Aplicação de energia física ou mental para alcançar algo."),
    ("excesso", Genero.MASCULINO, "Quantidade que ultrapassa o que é normal ou necessário."),
    ("fachada", Genero.FEMININO, "Parte externa e frontal de um edifício."),
    ("facilidade", Genero.FEMININO, "Qualidade do que é fácil, ou capacidade de fazer algo sem dificuldade."),
    ("felicidade", Genero.FEMININO, "Estado de bem-estar e satisfação profunda."),
    ("fila", Genero.FEMININO, "Sequência de pessoas ou coisas dispostas uma atrás da outra."),
    ("filtro", Genero.MASCULINO, "Dispositivo ou processo que retém certos elementos e deixa passar outros."),
    ("frente", Genero.FEMININO, "Parte dianteira de algo, ou linha de confronto."),
    ("impacto", Genero.MASCULINO, "Efeito produzido por um choque ou por uma ação sobre algo."),
    ("instante", Genero.MASCULINO, "Período de tempo muito curto."),
    ("manhã", Genero.FEMININO, "Primeira parte do dia, entre o amanhecer e o meio-dia."),
    ("natureza", Genero.FEMININO, "Conjunto de tudo o que existe sem intervenção humana, ou essência de algo."),
    ("orgulho", Genero.MASCULINO, "Sentimento de satisfação por um mérito próprio ou de alguém próximo."),
    ("perfil", Genero.MASCULINO, "Contorno lateral de algo, ou conjunto de características que definem alguém."),
    ("recursão", Genero.FEMININO, "Processo em que algo se define ou se repete em termos de si mesmo."),
    ("reunião", Genero.FEMININO, "Encontro de pessoas para tratar de um assunto."),
    ("segurança", Genero.FEMININO, "Estado de estar protegido de perigo ou risco."),
    ("sentimento", Genero.MASCULINO, "Estado afetivo provocado por uma emoção."),
    ("surpresa", Genero.FEMININO, "Sensação causada por algo inesperado."),
    ("bisseção", Genero.FEMININO, "Divisão de algo em duas partes iguais, ou método que reduz um intervalo pela metade a cada passo."),
    ("autovalor", Genero.MASCULINO, "Escalar que, ao multiplicar um vetor próprio de uma transformação, reproduz o efeito dessa transformação."),
    # Quinquagésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    ("paragem", Genero.FEMININO, "Ato de parar, ou local onde algo para."),
    ("poeta", Genero.MASCULINO, "Pessoa que escreve poesia."),
    ("potencial", Genero.MASCULINO, "Capacidade que existe mas ainda não foi realizada."),
    ("sede", Genero.FEMININO, "Local principal onde uma organização está estabelecida, ou sensação de precisar de beber água."),
    ("sexo", Genero.MASCULINO, "Conjunto de características biológicas que distinguem macho de fêmea."),
    ("território", Genero.MASCULINO, "Extensão de terra sob o controlo de uma entidade."),
    ("tolerância", Genero.FEMININO, "Capacidade de aceitar ou suportar algo diferente do esperado."),
    ("velocidade", Genero.FEMININO, "Medida de quão rápido algo se move."),
    ("viagem", Genero.FEMININO, "Deslocação de um lugar para outro, geralmente distante."),
    ("biografia", Genero.FEMININO, "Relato da vida de uma pessoa."),
    ("anatomia", Genero.FEMININO, "Estudo da estrutura dos seres vivos."),
    ("sociologia", Genero.FEMININO, "Estudo científico da sociedade e das relações sociais."),
    ("quarto", Genero.MASCULINO, "Divisão de uma casa destinada a dormir, ou quarta parte de algo."),
    # Quinquagésimo oitavo lote do corpus amplo (modo massa, meta 50.000).
    ("diagrama", Genero.MASCULINO, "Representação gráfica que mostra relações entre elementos."),
    ("energia", Genero.FEMININO, "Capacidade de realizar trabalho ou provocar mudança."),
    ("estratégia", Genero.FEMININO, "Plano organizado para alcançar um objetivo."),
    ("exame", Genero.MASCULINO, "Avaliação formal do conhecimento ou do estado de algo."),
    ("flor", Genero.FEMININO, "Parte da planta responsável pela reprodução, geralmente colorida."),
    ("gatilho", Genero.MASCULINO, "Peça que aciona um mecanismo, ou evento que desencadeia outro."),
    ("gesto", Genero.MASCULINO, "Movimento do corpo, geralmente da mão, que expressa algo."),
    ("hipotenusa", Genero.FEMININO, "Lado oposto ao ângulo reto num triângulo retângulo, o maior dos três lados."),
    ("jargão", Genero.MASCULINO, "Vocabulário próprio de um grupo ou área de atividade."),
    ("liberdade", Genero.FEMININO, "Capacidade de agir sem restrições impostas por outros."),
    ("orçamento", Genero.MASCULINO, "Estimativa dos recursos financeiros necessários ou disponíveis."),
    ("perpendicular", Genero.FEMININO, "Linha ou plano que forma um ângulo reto com outro."),
    ("porção", Genero.FEMININO, "Parte de um todo."),
    ("raciocínio", Genero.MASCULINO, "Processo mental de encadear ideias para chegar a uma conclusão."),
    ("recipiente", Genero.MASCULINO, "Objeto usado para conter algo."),
    ("redação", Genero.FEMININO, "Ato de redigir um texto, ou o texto resultante."),
    ("régua", Genero.FEMININO, "Instrumento reto usado para medir ou traçar linhas."),
    ("servidor", Genero.MASCULINO, "Pessoa ou programa que presta um serviço a outros."),
    ("soneto", Genero.MASCULINO, "Poema de forma fixa com catorze versos."),
    ("sugestão", Genero.FEMININO, "Ideia proposta para consideração."),
    ("tentativa", Genero.FEMININO, "Ato de tentar fazer algo."),
    ("época", Genero.FEMININO, "Período determinado de tempo, marcado por características próprias."),
    ("computabilidade", Genero.FEMININO, "Propriedade de um problema para o qual existe um algoritmo que o resolve."),
    ("coprimo", Genero.MASCULINO, "Número que não compartilha nenhum divisor comum com outro além de um."),
    # Quinquagésimo nono lote do corpus amplo (modo massa, meta 50.000).
    ("graça", Genero.FEMININO, "Qualidade de ser agradável ou engraçado, ou favor concedido gratuitamente."),
    ("menção", Genero.FEMININO, "Referência breve a algo ou alguém."),
    ("milênio", Genero.MASCULINO, "Período de mil anos."),
    ("obrigação", Genero.FEMININO, "Dever que alguém tem de cumprir."),
    ("permutação", Genero.FEMININO, "Rearranjo dos elementos de um conjunto numa ordem diferente."),
    ("programação", Genero.FEMININO, "Ato de programar, organizando etapas ou instruções."),
    ("proposição", Genero.FEMININO, "Afirmação que pode ser considerada verdadeira ou falsa."),
    ("topo", Genero.MASCULINO, "Ponto mais alto de algo."),
    ("aldeia", Genero.FEMININO, "Povoação pequena, geralmente rural."),
    ("anúncio", Genero.MASCULINO, "Comunicação pública que informa ou promove algo."),
    ("afeto", Genero.MASCULINO, "Sentimento de carinho ou ligação emocional por alguém."),
    ("andamento", Genero.MASCULINO, "Ritmo ou progresso de algo em curso."),
    ("divergência", Genero.FEMININO, "Afastamento progressivo entre valores, sem tender a um limite comum."),
    ("modificador", Genero.MASCULINO, "Termo que altera ou qualifica o sentido de outro elemento numa frase."),
    ("monóide", Genero.MASCULINO, "Conjunto com uma operação associativa e um elemento neutro."),
    ("perpendicularidade", Genero.FEMININO, "Propriedade de duas retas ou planos que se cruzam formando ângulo reto."),
    # Sexagésimo lote do corpus amplo (modo massa, meta 50.000).
    ("atitude", Genero.FEMININO, "Modo de agir ou reagir perante uma situação."),
    ("buraco", Genero.MASCULINO, "Abertura ou cavidade num corpo sólido."),
    ("cardume", Genero.MASCULINO, "Grupo de peixes que se movem juntos."),
    ("caderno", Genero.MASCULINO, "Conjunto de folhas de papel unidas, usado para escrever."),
    ("caneta", Genero.FEMININO, "Instrumento usado para escrever com tinta."),
    ("borda", Genero.FEMININO, "Linha ou faixa que delimita a extremidade de algo."),
    ("bola", Genero.FEMININO, "Objeto redondo usado em jogos ou desportos."),
    ("banana", Genero.FEMININO, "Fruta alongada e curva, de casca amarela quando madura."),
    ("açúcar", Genero.MASCULINO, "Substância doce cristalina extraída de plantas como a cana ou a beterraba."),
    ("cartaz", Genero.MASCULINO, "Folha grande afixada em público para anunciar ou divulgar algo."),
    ("câmara", Genero.FEMININO, "Compartimento ou órgão colegiado, ou dispositivo para captar imagens."),
    ("cena", Genero.FEMININO, "Parte de uma peça, filme ou situação observada."),
    ("cone", Genero.MASCULINO, "Sólido geométrico com base circular que se estreita até um ponto."),
    ("confronto", Genero.MASCULINO, "Situação de oposição direta entre partes."),
    ("consenso", Genero.MASCULINO, "Acordo geral entre várias pessoas ou partes."),
    ("conquista", Genero.FEMININO, "Ato de conquistar algo, ou aquilo que foi conquistado."),
    ("copo", Genero.MASCULINO, "Recipiente usado para beber líquidos."),
    ("costume", Genero.MASCULINO, "Hábito adquirido por repetição, próprio de uma pessoa ou cultura."),
    ("curiosidade", Genero.FEMININO, "Desejo de saber ou conhecer algo."),
    ("curva", Genero.FEMININO, "Linha que se desvia gradualmente de uma direção reta."),
    ("defeito", Genero.MASCULINO, "Imperfeição ou falha em algo."),
    ("degrau", Genero.MASCULINO, "Cada um dos planos de uma escada, usado para subir ou descer."),
    ("desigualdade", Genero.FEMININO, "Falta de igualdade entre duas ou mais coisas."),
    ("descoberta", Genero.FEMININO, "Ato de descobrir algo novo, ou aquilo que foi descoberto."),
    ("cientista", Genero.COMUM, "Pessoa dedicada ao estudo científico de forma sistemática."),
    # Sexagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    ("diagnóstico", Genero.MASCULINO, "Identificação de um problema a partir da análise dos seus sintomas ou sinais."),
    ("detalhe", Genero.MASCULINO, "Parte pequena e específica de algo."),
    ("doce", Genero.MASCULINO, "Alimento com sabor açucarado."),
    ("drama", Genero.MASCULINO, "Obra ou situação marcada por conflito e tensão emocional."),
    ("dívida", Genero.FEMININO, "Quantia que se deve pagar a alguém."),
    ("dúzia", Genero.FEMININO, "Conjunto de doze unidades."),
    ("editor", Genero.MASCULINO, "Pessoa ou programa que prepara um texto ou conteúdo para publicação."),
    ("eficiência", Genero.FEMININO, "Capacidade de produzir um resultado com o mínimo de recursos ou esforço."),
    ("empresa", Genero.FEMININO, "Organização criada para desenvolver uma atividade económica."),
    ("engano", Genero.MASCULINO, "Erro cometido por falta de atenção ou informação incorreta."),
    ("equilíbrio", Genero.MASCULINO, "Estado de estabilidade entre forças ou elementos opostos."),
    ("esfera", Genero.FEMININO, "Sólido geométrico cujos pontos estão todos à mesma distância do centro."),
    ("estatuto", Genero.MASCULINO, "Conjunto de regras que definem a organização e o funcionamento de algo, ou situação legal de alguém."),
    ("etiqueta", Genero.FEMININO, "Pequena peça com informação afixada a um objeto, ou conjunto de normas de comportamento."),
    ("filosofia", Genero.FEMININO, "Estudo racional das questões fundamentais da existência, do conhecimento e da ética."),
    ("fogo", Genero.MASCULINO, "Combustão que produz luz e calor."),
    ("foto", Genero.FEMININO, "Imagem captada por uma câmara."),
    ("fotografia", Genero.FEMININO, "Técnica ou imagem obtida pela captação de luz num suporte sensível."),
    ("fundo", Genero.MASCULINO, "Parte mais profunda ou inferior de algo, ou reserva de recursos financeiros."),
    ("gado", Genero.MASCULINO, "Conjunto de animais criados para produção, geralmente bovinos."),
    ("gelo", Genero.MASCULINO, "Água no estado sólido, obtida por congelamento."),
    ("gestão", Genero.FEMININO, "Ato de gerir, administrando recursos e processos."),
    ("guerra", Genero.FEMININO, "Conflito armado entre grupos ou nações."),
    ("guitarra", Genero.FEMININO, "Instrumento musical de cordas, tocado com os dedos ou uma palheta."),
    ("hospedeiro", Genero.MASCULINO, "Organismo ou entidade que acolhe outro, ou pessoa que recebe visitantes."),
    ("humor", Genero.MASCULINO, "Disposição de espírito, ou capacidade de provocar riso."),
    ("infância", Genero.FEMININO, "Período inicial da vida humana, entre o nascimento e a adolescência."),
    ("pão", Genero.MASCULINO, "Alimento feito de farinha, água e fermento, assado no forno."),
    ("reflexividade", Genero.FEMININO, "Propriedade de uma relação em que todo elemento se relaciona consigo mesmo."),
    ("ressonância", Genero.FEMININO, "Fenómeno em que uma vibração se amplia ao encontrar frequência compatível."),
    ("separador", Genero.MASCULINO, "Elemento que marca o limite entre duas partes distintas."),
    ("apassivador", Genero.MASCULINO, "Elemento que transforma uma construção ativa em passiva."),
    # Sexagésimo segundo lote do corpus amplo (modo massa, meta 50.000).
    ("medo", Genero.MASCULINO, "Sensação de receio perante um perigo real ou imaginado."),
    ("mentira", Genero.FEMININO, "Afirmação que se sabe não ser verdadeira, feita com intenção de enganar."),
    ("moda", Genero.FEMININO, "Conjunto de tendências dominantes numa época, especialmente no vestuário."),
    ("moeda", Genero.FEMININO, "Peça de metal usada como meio de pagamento."),
    ("moradia", Genero.FEMININO, "Local onde alguém vive; habitação."),
    ("motivação", Genero.FEMININO, "Razão que impulsiona alguém a agir."),
    ("nariz", Genero.MASCULINO, "Órgão do rosto usado para respirar e sentir cheiros."),
    ("nascimento", Genero.MASCULINO, "Ato de nascer, início da existência de um ser."),
    ("nuvem", Genero.FEMININO, "Massa visível de partículas de água suspensa na atmosfera."),
    ("onda", Genero.FEMININO, "Perturbação que se propaga através de um meio, ou movimento oscilante na superfície da água."),
    ("parede", Genero.FEMININO, "Estrutura vertical que delimita ou sustenta um espaço."),
    ("parâmetro", Genero.MASCULINO, "Valor ou variável que define ou limita as condições de um sistema ou função."),
    ("passatempo", Genero.MASCULINO, "Atividade feita para ocupar o tempo livre com prazer."),
    ("peixe", Genero.MASCULINO, "Animal aquático que respira por guelras e se desloca por barbatanas."),
    ("periferia", Genero.FEMININO, "Zona que fica à volta de um centro, geralmente mais afastada."),
    ("permanência", Genero.FEMININO, "Ato de permanecer; duração de uma presença num lugar."),
    ("permissão", Genero.FEMININO, "Autorização para fazer algo."),
    ("pico", Genero.MASCULINO, "Ponto mais alto de algo, ou momento de maior intensidade."),
    ("planalto", Genero.MASCULINO, "Extensão de terreno plano situada a grande altitude."),
    ("planta", Genero.FEMININO, "Ser vivo do reino vegetal, ou representação gráfica de uma construção."),
    ("porto", Genero.MASCULINO, "Local à beira-mar ou de um rio onde os navios atracam."),
    ("prejuízo", Genero.MASCULINO, "Perda ou dano causado a alguém."),
    ("prefácio", Genero.MASCULINO, "Texto introdutório que antecede o corpo principal de uma obra."),
    ("programa", Genero.MASCULINO, "Conjunto organizado de atividades ou instruções com um objetivo definido."),
    ("protagonista", Genero.COMUM, "Personagem principal de uma história, ou pessoa central de um acontecimento."),
    ("quadro", Genero.MASCULINO, "Superfície usada para escrever ou desenhar, ou obra de pintura."),
    ("questão", Genero.FEMININO, "Assunto que precisa de resposta ou solução, ou pergunta formulada."),
    ("quilograma", Genero.MASCULINO, "Unidade de massa do sistema internacional, equivalente a mil gramas."),
    ("rascunho", Genero.MASCULINO, "Versão inicial e não definitiva de um texto ou trabalho."),
    ("realidade", Genero.FEMININO, "Conjunto do que existe de facto, independentemente da perceção."),
    # Lote F (sessão contínua, corpus amplo, meta 50.000).
    ("crivo", Genero.MASCULINO, "Instrumento ou processo usado para separar ou selecionar elementos segundo um critério."),
    ("tríade", Genero.FEMININO, "Conjunto de três elementos relacionados entre si."),
    ("dedução", Genero.FEMININO, "Conclusão obtida a partir de premissas, por raciocínio lógico."),
    ("vibração", Genero.FEMININO, "Movimento oscilatório repetido em torno de uma posição de equilíbrio."),
    ("fricção", Genero.FEMININO, "Resistência ao movimento entre duas superfícies em contacto."),
    ("analogia", Genero.FEMININO, "Semelhança entre coisas diferentes que permite comparar uma pela outra."),
    ("coincidência", Genero.FEMININO, "Ocorrência simultânea ou concordante de factos sem ligação causal aparente."),
    # Sexagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    ("tradição", Genero.FEMININO, "Costume ou prática transmitida ao longo do tempo entre gerações."),
    ("trajetória", Genero.FEMININO, "Caminho percorrido por algo em movimento, ou percurso de vida."),
    ("táxi", Genero.MASCULINO, "Veículo automóvel usado para transportar passageiros mediante pagamento."),
    ("utilizador", Genero.MASCULINO, "Pessoa que usa um serviço, sistema ou produto."),
    ("vaca", Genero.FEMININO, "Fêmea do gado bovino, criada para produção de leite ou carne."),
    ("vento", Genero.MASCULINO, "Movimento do ar na atmosfera."),
    ("vínculo", Genero.MASCULINO, "Ligação que une duas coisas ou pessoas."),
    ("ícone", Genero.MASCULINO, "Imagem que representa simbolicamente algo, ou pessoa muito admirada e representativa."),
    ("átomo", Genero.MASCULINO, "Menor partícula de um elemento químico que mantém as suas propriedades."),
    ("acidente", Genero.MASCULINO, "Acontecimento imprevisto que causa dano."),
    ("alegria", Genero.FEMININO, "Sentimento de contentamento e satisfação."),
    ("amizade", Genero.FEMININO, "Relação de afeto e confiança entre pessoas."),
    ("amplitude", Genero.FEMININO, "Extensão ou grandeza de uma variação."),
    ("armazém", Genero.MASCULINO, "Local destinado a guardar mercadorias ou produtos."),
    ("arquitetura", Genero.FEMININO, "Arte e técnica de projetar e construir edifícios, ou estrutura organizacional de um sistema."),
    ("astronomia", Genero.FEMININO, "Ciência que estuda os astros e o universo."),
    ("cama", Genero.FEMININO, "Móvel usado para dormir."),
    ("cavalo", Genero.MASCULINO, "Animal quadrúpede usado para transporte ou desporto equestre."),
    ("chão", Genero.MASCULINO, "Superfície sobre a qual se anda; solo."),
    ("cilindro", Genero.MASCULINO, "Sólido geométrico com duas bases circulares paralelas unidas por uma superfície curva."),
    ("ciência", Genero.FEMININO, "Conhecimento obtido de forma sistemática através da observação e experimentação."),
    ("clima", Genero.MASCULINO, "Conjunto das condições atmosféricas típicas de uma região ao longo do tempo."),
    # Lote F2 (sessão contínua, corpus amplo, meta 50.000).
    ("espírito", Genero.MASCULINO, "Princípio imaterial associado ao pensamento e à consciência, ou disposição de ânimo."),
    ("criptografia", Genero.FEMININO, "Técnica de codificar informação para que só seja lida por quem tem a chave certa."),
    ("discussão", Genero.FEMININO, "Troca de argumentos entre pessoas sobre um assunto."),
    ("assinatura", Genero.FEMININO, "Nome escrito à mão que identifica o autor de um documento, ou subscrição de um serviço."),
    ("fonologia", Genero.FEMININO, "Estudo do sistema de sons de uma língua e das suas funções."),
    ("planeamento", Genero.MASCULINO, "Ato de organizar antecipadamente as etapas necessárias para atingir um objetivo."),
    ("interpretador", Genero.MASCULINO, "Programa que executa instruções de outro programa, traduzindo-as passo a passo."),
    ("buscador", Genero.MASCULINO, "Sistema ou programa que procura informação de acordo com um critério dado."),
    ("observador", Genero.MASCULINO, "Pessoa ou sistema que regista o que acontece sem intervir diretamente."),
    ("controlador", Genero.MASCULINO, "Elemento que regula ou supervisiona o funcionamento de um sistema."),
    ("detector", Genero.MASCULINO, "Dispositivo ou processo que identifica a presença de algo."),
    ("navegador", Genero.MASCULINO, "Programa usado para aceder e percorrer páginas na internet, ou pessoa que navega."),
    # Sexagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("disco", Genero.MASCULINO, "Objeto plano e circular, ou suporte usado para armazenar dados ou som."),
    ("dissertação", Genero.FEMININO, "Trabalho académico extenso sobre um tema específico."),
    ("dossiê", Genero.MASCULINO, "Conjunto de documentos organizados sobre um assunto."),
    ("engenharia", Genero.FEMININO, "Aplicação de conhecimentos científicos para projetar e construir soluções técnicas."),
    ("entropia", Genero.FEMININO, "Medida do grau de desordem ou incerteza de um sistema."),
    ("escada", Genero.FEMININO, "Estrutura com degraus usada para subir ou descer entre níveis."),
    ("esperança", Genero.FEMININO, "Sentimento de expectativa positiva quanto ao futuro."),
    ("espinha", Genero.FEMININO, "Estrutura óssea alongada, ou osso fino de peixe."),
    ("esquecimento", Genero.MASCULINO, "Estado de não se lembrar de algo."),
    ("fábula", Genero.FEMININO, "Narrativa curta com ensinamento moral, geralmente com animais como personagens."),
    ("gente", Genero.FEMININO, "Conjunto de pessoas, ou forma coloquial de referir pessoas em geral."),
    ("genética", Genero.FEMININO, "Ramo da biologia que estuda a hereditariedade e a variação dos seres vivos."),
    ("descarte", Genero.MASCULINO, "Ato de descartar algo, eliminando-o por não ser mais necessário."),
    ("despacho", Genero.MASCULINO, "Decisão ou ordem emitida por uma autoridade, ou ato de despachar algo."),
    ("determinismo", Genero.MASCULINO, "Doutrina segundo a qual todo acontecimento é determinado por causas anteriores."),
    ("disponibilidade", Genero.FEMININO, "Qualidade do que está disponível para uso."),
    # Sexagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    ("lixo", Genero.MASCULINO, "Material descartado como inútil ou sem valor."),
    ("medicina", Genero.FEMININO, "Ciência e prática de prevenir, diagnosticar e tratar doenças."),
    ("mercado", Genero.MASCULINO, "Local ou sistema onde se compram e vendem bens ou serviços."),
    ("meta", Genero.FEMININO, "Objetivo que se pretende alcançar."),
    ("mito", Genero.MASCULINO, "Narrativa tradicional com valor simbólico, ou crença amplamente aceite sem prova."),
    ("modernismo", Genero.MASCULINO, "Movimento artístico e cultural que rompe com as formas tradicionais."),
    ("muro", Genero.MASCULINO, "Estrutura vertical construída para delimitar ou proteger um espaço."),
    ("nervo", Genero.MASCULINO, "Estrutura do corpo que transmite impulsos entre o cérebro e as outras partes."),
    ("novela", Genero.FEMININO, "Obra narrativa mais curta que um romance, ou série televisiva de ficção com episódios."),
    ("paleta", Genero.FEMININO, "Superfície onde se misturam tintas, ou conjunto de cores usadas numa obra."),
    ("passeio", Genero.MASCULINO, "Caminhada feita por lazer, ou faixa lateral de uma rua destinada aos peões."),
    ("pedaço", Genero.MASCULINO, "Parte separada de um todo maior."),
    ("penalidade", Genero.FEMININO, "Punição imposta por não cumprir uma regra."),
    ("perímetro", Genero.MASCULINO, "Medida do contorno de uma figura plana."),
    ("pneu", Genero.MASCULINO, "Peça de borracha que envolve a roda de um veículo."),
    ("praia", Genero.FEMININO, "Faixa de terra à beira-mar coberta de areia."),
    ("queda", Genero.FEMININO, "Ato de cair."),
    ("raio", Genero.MASCULINO, "Segmento que une o centro de uma circunferência a um ponto da sua borda, ou descarga elétrica atmosférica."),
    ("reclamação", Genero.FEMININO, "Manifestação de descontentamento sobre algo."),
    ("recuperação", Genero.FEMININO, "Ato de recuperar algo que se tinha perdido."),
    ("relevância", Genero.FEMININO, "Qualidade do que é relevante, importante para o contexto."),
    ("relógio", Genero.MASCULINO, "Instrumento usado para medir e indicar o tempo."),
    ("repositório", Genero.MASCULINO, "Local onde se armazena e organiza um conjunto de dados ou ficheiros."),
    # Lote F3 (sessão contínua, corpus amplo, meta 50.000).
    ("resolução", Genero.FEMININO, "Ato de resolver algo, ou decisão tomada sobre um assunto."),
    ("exploração", Genero.FEMININO, "Ato de explorar, investigando ou aproveitando algo em profundidade."),
    ("colisão", Genero.FEMININO, "Choque entre dois ou mais corpos ou elementos."),
    ("desempate", Genero.MASCULINO, "Ato ou critério que decide um vencedor quando há empate."),
    ("cabeça", Genero.FEMININO, "Parte superior do corpo humano ou animal, onde está o cérebro, ou parte inicial de algo."),
    ("caixa", Genero.FEMININO, "Recipiente usado para guardar ou transportar objetos."),
    ("canal", Genero.MASCULINO, "Percurso por onde algo é conduzido ou transmitido, ou via de comunicação."),
    ("eixo", Genero.MASCULINO, "Linha em torno da qual algo gira ou se organiza, ou reta de referência num sistema de coordenadas."),
    ("piso", Genero.MASCULINO, "Superfície sobre a qual se anda, ou cada nível de um edifício."),
    ("rua", Genero.FEMININO, "Via pública numa povoação, ladeada por edifícios."),
    ("tarde", Genero.FEMININO, "Período do dia entre o meio-dia e o anoitecer."),
    ("espelho", Genero.MASCULINO, "Superfície que reflete a imagem de quem ou do que está à sua frente."),
    # Sexagésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    ("sucesso", Genero.MASCULINO, "Resultado positivo alcançado após um esforço."),
    ("superfície", Genero.FEMININO, "Parte exterior e visível de algo, ou extensão de área."),
    ("sustentabilidade", Genero.FEMININO, "Capacidade de se manter ao longo do tempo sem esgotar os recursos."),
    ("teatro", Genero.MASCULINO, "Arte de representar histórias diante de uma audiência, ou edifício onde isso acontece."),
    ("tecla", Genero.FEMININO, "Peça que se pressiona para acionar um mecanismo, como num teclado."),
    ("tela", Genero.FEMININO, "Superfície onde se projeta uma imagem, ou tecido usado em pintura."),
    ("teto", Genero.MASCULINO, "Parte superior de uma divisão que a cobre, ou limite máximo de algo."),
    ("tonelada", Genero.FEMININO, "Unidade de massa equivalente a mil quilogramas."),
    ("transparência", Genero.FEMININO, "Qualidade do que deixa passar a luz e ver através, ou clareza de intenções."),
    ("urgência", Genero.FEMININO, "Necessidade de agir rapidamente."),
    ("veracidade", Genero.FEMININO, "Qualidade do que é verdadeiro."),
    ("votação", Genero.FEMININO, "Ato de votar para decidir algo coletivamente."),
    ("áudio", Genero.MASCULINO, "Som gravado ou transmitido eletronicamente."),
    ("multiplicidade", Genero.FEMININO, "Quantidade de vezes que um mesmo elemento ou fator se repete."),
    ("irracionalidade", Genero.FEMININO, "Propriedade de um número que não pode ser escrito como razão entre dois inteiros."),
    ("simultaneidade", Genero.FEMININO, "Qualidade do que ocorre ao mesmo tempo que outra coisa."),
    ("sinalefa", Genero.FEMININO, "Fusão de duas vogais em sílabas vizinhas quando uma palavra termina e a seguinte começa em vogal."),
    ("truncamento", Genero.MASCULINO, "Ato de cortar uma parte de algo antes do seu fim natural."),
    ("autovetor", Genero.MASCULINO, "Vetor não nulo que, ao ser transformado por uma matriz, muda apenas de escala."),
    ("prima", Genero.FEMININO, "Filha de um tio ou tia em relação a outra pessoa da mesma geração."),
    # Expansão de substantivos técnicos e gerais em português.
    ("controle", Genero.MASCULINO, "Mecanismo ou ação de regular e verificar o funcionamento de um sistema."),
    ("pacote", Genero.MASCULINO, "Conjunto de módulos, arquivos ou dados agrupados como unidade."),
    ("serviço", Genero.MASCULINO, "Processo ou funcionalidade oferecida por um componente a outro."),
    ("relatório", Genero.MASCULINO, "Documento que apresenta a análise de dados ou resultados."),
    ("ponto", Genero.MASCULINO, "Posição exata num espaço, sequência ou estrutura."),
    ("gargalo", Genero.MASCULINO, "Ponto de restrição que limita o fluxo ou o desempenho de um sistema."),
    ("escopo", Genero.MASCULINO, "Alcance ou limite de validade de uma variável, regra ou projeto."),
    ("saída", Genero.FEMININO, "Resultado produzido por uma função, algoritmo ou processo."),
    ("barramento", Genero.MASCULINO, "Canal ou via de comunicação que liga múltiplos componentes."),
    ("ponteiro", Genero.MASCULINO, "Variável ou referência que indica o endereço de memória de um elemento."),
    ("requisito", Genero.MASCULINO, "Condição ou capacidade necessária que um sistema deve satisfazer."),
    ("fluxograma", Genero.MASCULINO, "Diagrama que representa graficamente as etapas de um processo."),
    ("protocolo", Genero.MASCULINO, "Conjunto de regras que governam a troca de dados entre sistemas."),
    ("cliente", Genero.MASCULINO, "Componente ou programa que solicita serviços a um servidor."),
    ("compilação", Genero.FEMININO, "Processo de tradução de código fonte em linguagem executável."),
    ("notificação", Genero.FEMININO, "Mensagem enviada para alertar sobre um evento ou mudança de estado."),
    ("transação", Genero.FEMININO, "Sequência de operações tratada como uma unidade indivisível."),
    ("título", Genero.MASCULINO, "Nome ou identificação de um documento, seção ou trabalho."),
    ("depuração", Genero.FEMININO, "Processo de localizar e corrigir erros num programa."),
    ("diretório", Genero.MASCULINO, "Estrutura organizadora que contém arquivos e outros diretórios num sistema de arquivos."),
    ("rastreamento", Genero.MASCULINO, "Acompanhamento do percurso ou execução de um processo."),
    ("agendamento", Genero.MASCULINO, "Organização temporal da execução de tarefas ou processos."),
    ("mapeamento", Genero.MASCULINO, "Associação sistemática entre elementos de dois conjuntos ou domínios."),
    ("barreira", Genero.FEMININO, "Ponto de sincronização ou restrição num fluxo de execução."),
    ("redirecionamento", Genero.MASCULINO, "Alteração do destino normal de um fluxo de dados ou chamada."),
    ("redimensionamento", Genero.MASCULINO, "Alteração do tamanho ou capacidade de uma estrutura de dados ou imagem."),
    ("vetorização", Genero.FEMININO, "Conversão de operações para execução paralela sobre vetores de dados."),
    ("serialização", Genero.FEMININO, "Conversão de um objeto ou estrutura de dados num formato transmissível ou armazenável."),
    ("desserialização", Genero.FEMININO, "Reconstrução de um objeto a partir de um formato serializado."),
    ("otimização", Genero.FEMININO, "Ajuste de um sistema ou algoritmo para melhorar a sua eficiência."),
    # Expansão com 30 novos substantivos técnicos e gramaticais.
    ("aplicação", Genero.FEMININO, "Programa ou sistema construído para realizar tarefas específicas para um utilizador ou processo."),
    ("critério", Genero.MASCULINO, "Regra ou padrão usado para julgar, classificar ou tomar uma decisão."),
    ("identificador", Genero.MASCULINO, "Nome ou símbolo único usado para referenciar uma entidade, variável ou função numa estrutura ou código."),
    ("variável", Genero.FEMININO, "Símbolo ou espaço de armazenamento que representa um valor sujeito a alteração durante a execução ou análise."),
    ("abstração", Genero.FEMININO, "Processo de simplificação que oculta detalhes complexos para focar nos aspetos essenciais."),
    ("alocação", Genero.FEMININO, "Ato de reservar ou atribuir recursos, como memória ou espaço, para um uso determinado."),
    ("argumento", Genero.MASCULINO, "Valor fornecido a uma função ou comando para orientar o seu processamento."),
    ("automação", Genero.FEMININO, "Uso de sistemas ou processos automáticos para realizar tarefas sem intervenção humana direta."),
    ("caractere", Genero.MASCULINO, "Símbolo individual de escrita, como uma letra, número ou sinal de pontuação."),
    ("compilador", Genero.MASCULINO, "Programa que traduz código-fonte escrito numa linguagem de alto nível para linguagem de máquina ou código executável."),
    ("concorrência", Genero.FEMININO, "Execução simultânea ou intercalada de múltiplas tarefas num sistema."),
    ("constante", Genero.FEMININO, "Valor fixo que não se altera durante a execução de um algoritmo ou processo."),
    ("construtor", Genero.MASCULINO, "Método especial responsável por inicializar uma nova instância de uma classe."),
    ("especificação", Genero.FEMININO, "Descrição detalhada e precisa dos requisitos, comportamento ou estrutura de um sistema."),
    ("executável", Genero.MASCULINO, "Arquivo ou programa preparado para ser diretamente executado por um sistema operacional."),
    ("herança", Genero.FEMININO, "Mecanismo pelo qual uma classe deriva propriedades e comportamentos de outra classe."),
    ("indexação", Genero.FEMININO, "Organização de dados através de índices para acelerar a busca e o acesso."),
    ("inicialização", Genero.FEMININO, "Ato de definir o estado ou valor inicial de uma variável, componente ou sistema."),
    ("instrução", Genero.FEMININO, "Comando ou operação individual executada por um processador ou programa."),
    ("invariante", Genero.FEMININO, "Condição ou propriedade que permanece verdadeira durante toda a execução de um processo."),
    ("metadado", Genero.MASCULINO, "Dado estruturado que fornece informação descritiva sobre outros dados."),
    ("morfossintaxe", Genero.FEMININO, "Estudo conjunto da estrutura interna das palavras e do seu papel na frase."),
    ("operando", Genero.MASCULINO, "Valor ou entidade sobre a qual um operador atua numa expressão."),
    ("polimorfismo", Genero.MASCULINO, "Capacidade de objetos de diferentes classes responderem à mesma mensagem ou chamada de métodos."),
    ("recursividade", Genero.FEMININO, "Propriedade de uma função ou processo que chama a si mesmo para resolver subproblemas."),
    ("registrador", Genero.MASCULINO, "Pequena memória interna de alta velocidade num processador usada para armazenar dados temporários."),
    ("requisição", Genero.FEMININO, "Solicitação formal enviada por um cliente a um servidor para obter um recurso ou serviço."),
    ("semântica", Genero.FEMININO, "Ramo da linguística e da computação que estuda o significado das palavras, frases ou expressões."),
    ("sintaxe", Genero.FEMININO, "Conjunto de regras que governa a estrutura e a combinação correta dos símbolos numa linguagem."),
    ("tipagem", Genero.FEMININO, "Sistema de regras que define como os tipos de dados são atribuídos e validados num programa."),
)


_ADJETIVOS: tuple[tuple[str, str], ...] = (
    ("fluido", "Que corre com naturalidade e continuidade."),
    ("natural", "Próximo do modo como uma pessoa fala ou pensa."),
    ("humano", "Explicado para uma pessoa real, com chão, exemplo e ritmo."),
    ("técnico", "Relacionado a método, sistema, ciência ou construção especializada."),
    ("perfeito", "Completo para o objetivo definido, sem lacuna essencial naquele contexto."),
    ("amplo", "Grande em alcance e variedade."),
    ("grande", "De tamanho, alcance ou quantidade elevados."),
    ("infinito", "Sem último elemento dentro da regra de continuação."),
    ("real", "Tratado com honestidade operacional e não apenas como palavra bonita."),
    ("futuro", "Ainda por construir, testar ou integrar."),
    ("construído", "Já formado por etapas anteriores e documentado."),
    ("pendente", "Ainda em falta ou à espera de construção."),
    ("claro", "Fácil de perceber."),
    ("simples", "Reduzido ao essencial sem perder verdade."),
    ("profundo", "Que vai até fundamentos e consequências."),
    ("aberto", "Preparado para continuar além do estado atual."),
    ("finito", "Com limite definido e manipulável."),
    ("simbólico", "Expresso por sinais, letras ou fórmulas."),
    ("conceitual", "Baseado no conceito antes da fórmula."),
    ("lexical", "Relacionado à palavra como unidade reconhecida."),
    ("morfologico", "Relacionado à forma interna das palavras."),
    ("morfológico", "Relacionado à forma interna das palavras."),
    ("sintático", "Relacionado à organização das palavras na frase."),
    ("semântico", "Relacionado ao sentido construído."),
    ("gramatical", "Relacionado ao funcionamento organizado da língua."),
    ("tônico", "Que recebe força relativa maior na palavra."),
    ("comunicativo", "Relacionado à intenção ou ato de comunicar."),
    ("referencial", "Relacionado à referência ou ao alvo indicado."),
    ("polissêmico", "Que admite mais de um sentido conforme contexto."),
    ("sinonímico", "Relacionado à proximidade de sentido."),
    ("antonímico", "Relacionado à oposição de sentido."),
    ("coordenado", "Ligado em mesmo nível funcional."),
    ("subordinado", "Dependente de outra unidade na construção."),
    ("normativo", "Relacionado à norma de uso controlado."),
    ("variável", "Que pode mudar conforme uso, situação ou relação."),
    ("formal", "Adequado a contexto de maior controlo ou cerimónia."),
    ("informal", "Adequado a contexto familiar ou espontâneo."),
    ("afirmativo", "Relacionado a afirmação ou declaração sustentada."),
    ("negativo", "Relacionado a negação ou cancelamento de uma afirmação possível."),
    ("interrogativo", "Relacionado a pergunta ou busca de informação."),
    ("exclamativo", "Relacionado a força expressiva ou exclamação."),
    ("pragmático", "Relacionado ao sentido em uso e ao contexto comunicativo."),
    ("estilístico", "Relacionado ao modo de expressão de um texto."),
    ("interpretativo", "Relacionado à construção de sentido com limites claros."),
    # Lote extraído do corpus amplo (Fase 3/4 do plano de léxico).
    ("mínimo", "O menor valor ou caso ainda válido dentro de uma regra."),
    ("verbal", "Relacionado ao verbo ou à fala."),
    ("compatível", "Que pode coexistir ou funcionar junto sem conflito."),
    ("operacional", "Que já funciona de verdade, não só em teoria."),
    ("nominal", "Relacionado ao nome ou substantivo."),
    ("adverbial", "Relacionado ao advérbio ou à sua função."),
    ("puro", "Construído desde o fundamento, sem atalho nem fórmula pronta importada."),
    # Segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("inicial", "Que está no começo de algo."),
    ("final", "Que está no fim de algo."),
    ("explícito", "Dito de forma clara e direta, sem ficar implícito."),
    ("geral", "Que se aplica ao conjunto todo, não a um caso só."),
    ("primeiro", "Que ocupa a posição inicial numa ordem."),
    ("próprio", "Que pertence especificamente a algo ou alguém."),
    ("direto", "Que vai ao ponto sem desvio ou intermediário."),
    ("gráfico", "Relacionado à representação visual ou escrita."),
    ("próximo", "Que está perto no espaço, tempo ou relação."),
    ("comum", "Que é compartilhado ou frequente."),
    ("externo", "Que vem ou está fora de um limite dado."),
    ("necessário", "Que é preciso para que algo aconteça ou exista."),
    ("textual", "Relacionado ao texto como unidade organizada."),
    ("permitido", "Que tem autorização para acontecer ou ser usado."),
    ("proibido", "Que não tem autorização para acontecer ou ser usado."),
    # Terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("diferente", "Que não é igual a outra coisa comparada."),
    ("parcial", "Que cobre só uma parte, não o todo."),
    ("exato", "Que corresponde precisamente ao esperado, sem erro."),
    ("linguístico", "Relacionado à língua ou ao seu estudo."),
    ("ordenado", "Que segue uma sequência ou critério de organização."),
    ("modular", "Que pode ser dividido em partes independentes e combináveis."),
    ("booleano", "Relacionado a valores lógicos de verdadeiro ou falso."),
    ("linear", "Que segue uma progressão direta, sem ramificação."),
    ("maior", "Que tem tamanho, grau ou quantidade acima de outro na comparação."),
    ("principal", "Que tem mais importância entre os elementos comparados."),
    ("racional", "Que pode ser expresso como razão entre dois números inteiros, ou que segue raciocínio lógico."),
    ("anterior", "Que vem antes na ordem ou no tempo."),
    ("automático", "Que acontece sem intervenção manual repetida."),
    ("histórico", "Relacionado a fatos ou período já ocorridos."),
    ("ortográfico", "Relacionado às regras de escrita correta das palavras."),
    # Quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("abstrato", "Que não tem existência física concreta, tratado por conceito."),
    ("temporal", "Relacionado ao tempo ou à sua passagem."),
    ("universal", "Que se aplica a todos os casos dentro do seu domínio, sem exceção conhecida."),
    ("honesto", "Que não esconde nem finge o que realmente é ou sabe."),
    ("menor", "Que tem tamanho, grau ou quantidade abaixo de outro na comparação."),
    ("sonoro", "Que produz ou envolve som."),
    ("único", "Que não tem outro igual dentro do conjunto considerado."),
    ("interno", "Que está ou vem de dentro de um limite dado."),
    ("indireto", "Que passa por um intermediário em vez de ir direto ao ponto."),
    # Quinto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("pronto", "Que já está preparado ou concluído para uso ou apresentação."),
    ("funcional", "Que cumpre de verdade a função a que se destina."),
    ("limitado", "Que tem alcance restrito, não total."),
    ("nativo", "Que já nasce construído dentro do sistema, sem depender de fonte externa."),
    ("regular", "Que segue um padrão previsível, sem exceção."),
    ("social", "Relacionado à convivência ou organização entre pessoas."),
    # Sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("central", "Que ocupa a posição principal ou mais importante."),
    # Sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("fonológico", "Relacionado ao sistema de sons de uma língua."),
    ("binário", "Que tem ou usa apenas dois valores ou estados possíveis."),
    ("diferencial", "Que marca ou introduz uma diferença em relação ao padrão."),
    ("silábico", "Relacionado à sílaba."),
    ("original", "Que é a fonte primeira, não cópia nem derivação de outra coisa."),
    ("posterior", "Que vem depois na ordem ou no tempo."),
    ("relativo", "Que depende de outro elemento para ter sentido ou valor completo."),
    ("avançado", "Que está num estágio adiantado de desenvolvimento ou complexidade."),
    ("composto", "Que é formado pela junção de duas ou mais partes."),
    ("pessoal", "Que pertence ou diz respeito a uma pessoa específica."),
    ("estrutural", "Relacionado à estrutura ou organização interna de algo."),
    ("literal", "Que segue exatamente o sentido próprio das palavras, sem figura."),
    ("local", "Que pertence ou está limitado a um lugar específico."),
    ("geométrico", "Relacionado à geometria ou às suas formas."),
    ("simétrico", "Que tem simetria entre suas partes."),
    # Oitavo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("gerador", "Que gera ou produz algo."),
    ("integral", "Que abrange o todo, sem faltar nenhuma parte."),
    ("inteiro", "Que está completo, sem estar dividido em partes."),
    # Nono lote do corpus amplo (Fase 3/4, corte seguinte).
    ("possível", "Que pode acontecer, existir ou ser feito."),
    ("consonantal", "Relacionado a consoante ou formado por consoantes."),
    ("matemático", "Relacionado à matemática ou construído por seus métodos."),
    # Décimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("livre", "Que não está preso, limitado ou condicionado por algo."),
    # Décimo primeiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("inverso", "Que ocupa posição, direção ou ordem oposta a outro."),
    ("oral", "Relativo à fala, feito pela boca em vez de escrito."),
    # Décimo segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("condicional", "Que depende de uma condição para se realizar ou ser válido."),
    ("estável", "Que se mantém firme, sem variar ou se romper."),
    # Décimo terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("exponencial", "Que cresce ou decresce multiplicando-se por um fator fixo a cada etapa."),
    ("predicativo", "Que atribui uma qualidade ou estado ao sujeito através do verbo."),
    ("existente", "Que existe ou está presente de fato."),
    # Décimo quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("reflexivo", "Que volta sobre o próprio sujeito que o pratica."),
    ("contextual", "Que depende do contexto em que ocorre."),
    ("supremo", "Que está no grau mais alto, acima de todos os outros."),
    # Décimo quinto lote do corpus amplo (Fase 3/4, corte seguinte).
    # "substantivo" e "quadrado" já existem como substantivo em `_NOMES`
    # -- aqui ganham a leitura ADJETIVO real (dupla classe, mesmo padrão
    # já usado por "segundo" NUMERAL/PREPOSICAO): "função substantiva",
    # "número quadrado"/"raiz quadrada" usam a palavra como adjetivo.
    ("substantivo", "Relativo ao substantivo, ou que funciona como um."),
    ("adjetivo", "Relativo ao adjetivo, ou que funciona como um (\"oração adjetiva\")."),
    ("quadrado", "Que tem quatro lados iguais, ou que resulta de multiplicar um número por si mesmo."),
    ("antigo", "Que existe ou aconteceu há muito tempo."),
    ("clássico", "Que segue um modelo consagrado, tomado como referência."),
    ("concreto", "Que existe de forma real e palpável, não abstrata."),
    # Décimo sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("positivo", "Que afirma, favorece ou tem valor maior que zero."),
    ("narrativo", "Relativo à narrativa ou ao ato de narrar."),
    ("temático", "Relacionado a um tema específico."),
    # Décimo sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("primitivo", "Que existe desde a origem, sem depender de construção anterior."),
    # Décimo oitavo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("vetorial", "Relativo a vetor, ou que é representado por grandeza com direção e sentido."),
    ("relevante", "Que tem importância real para o caso em questão."),
    ("básico", "Que forma o fundamento sobre o qual o resto se apoia."),
    ("absoluto", "Que vale por si mesmo, sem depender de comparação ou condição."),
    ("exaustivo", "Que cobre todos os casos possíveis, sem deixar nenhum de fora."),
    ("explicativo", "Que serve para tornar algo mais claro ou compreensível."),
    # Décimo nono lote do corpus amplo (Fase 3/4, corte seguinte).
    ("suficiente", "Que é bastante para satisfazer uma necessidade ou condição."),
    ("dependente", "Que precisa de outra coisa para existir, funcionar ou ter sentido."),
    ("verificável", "Que pode ser conferido e confirmado como verdadeiro ou falso."),
    ("relacional", "Relativo à relação entre elementos, ou que se baseia nela."),
    ("pronominal", "Relativo ao pronome, ou que funciona como um."),
    ("preposicional", "Relativo à preposição, ou introduzido por uma."),
    # Vigésimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("decimal", "Relativo ao sistema de contagem em base dez."),
    ("impessoal", "Que não se refere a uma pessoa específica, ou não expressa sujeito determinado."),
    ("oracional", "Relativo à oração gramatical."),
    # Vigésimo primeiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("transitivo", "Que exige complemento para completar seu sentido."),
    ("vocálico", "Relativo à vogal, ou formado por vogal."),
    ("nasal", "Relativo ao nariz, ou produzido com passagem de ar pelo nariz."),
    ("objetivo", "Que existe independente de opinião pessoal, baseado em fatos."),
    ("comparativo", "Que estabelece comparação entre dois ou mais elementos."),
    ("passivo", "Que recebe a ação em vez de praticá-la; que não reage ou intervém."),
    # Vigésimo terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("quadrático", "Que envolve o quadrado de uma quantidade, como em uma equação de grau dois."),
    # Vigésimo quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("seguinte", "Que vem logo depois na ordem ou sequência."),
    ("reticulado", "Que tem forma de rede, com linhas cruzadas formando uma grade."),
    # Vigésimo quinto lote do corpus amplo (Fase 3/4, corte seguinte) --
    # lote grande autorizado, massa só pra vocabulário puro.
    ("auxiliar", "Que ajuda ou serve de apoio a outra coisa principal."),
    ("complexo", "Que é formado por muitas partes relacionadas entre si, difícil de separar ou entender de uma vez."),
    ("consistente", "Que se mantém coerente e sem contradição ao longo do tempo ou da construção."),
    ("convencional", "Que segue um acordo ou costume aceito por um grupo."),
    ("discursivo", "Relativo ao discurso, ou que se desenvolve através dele."),
    ("regional", "Relativo a uma região específica."),
    ("superlativo", "Que expressa o grau mais alto de uma qualidade."),
    ("vivo", "Que está com vida, ou que mantém atividade e energia."),
    ("forte", "Que tem grande capacidade, resistência ou intensidade."),
    ("independente", "Que não depende de outra coisa para existir ou funcionar."),
    ("terceiro", "Que ocupa a posição depois do segundo numa ordem."),
    ("causal", "Relativo à causa, ou que indica relação de causa e efeito."),
    ("analítico", "Que procede por análise, separando um todo nas suas partes."),
    # Vigésimo sétimo lote do corpus amplo (modo rápido).
    ("visível", "Que pode ser visto."),
    ("constante", "Que não muda ao longo do tempo ou do processo."),
    ("equivalente", "Que tem o mesmo valor, efeito ou importância que outra coisa."),
    ("escalar", "Que tem só magnitude, sem direção nem sentido."),
    ("global", "Que abrange o todo, sem se limitar a uma parte."),
    ("igual", "Que tem exatamente o mesmo valor ou característica que outro."),
    ("neutro", "Que não toma partido nem pende para nenhum dos lados."),
    ("indeterminado", "Que não tem valor ou limite fixado com precisão."),
    ("aumentativo", "Que indica tamanho maior do que o normal."),
    ("diminutivo", "Que indica tamanho menor do que o normal, ou tom afetivo."),
    ("existencial", "Relativo à existência."),
    # Trigésimo lote do corpus amplo (modo rápido).
    ("literário", "Relativo à literatura."),
    ("semelhante", "Que se parece com outra coisa em algum aspecto."),
    ("coletivo", "Que pertence ou diz respeito a um grupo, não a um indivíduo só."),
    ("espacial", "Relativo ao espaço."),
    ("informacional", "Relativo à informação."),
    ("indefinido", "Que não tem limite ou valor determinado com precisão."),
    ("documentado", "Que está registado e comprovado por documento."),
    ("reto", "Que segue sempre a mesma direção, sem curvar; ângulo de noventa graus."),
    # Trigésimo segundo lote do corpus amplo (modo rápido).
    ("obrigatório", "Que tem de ser cumprido ou feito, sem escolha."),
    ("especial", "Que se distingue do comum por alguma característica própria."),
    ("unitário", "Relativo à unidade, ou que tem valor igual a um."),
    ("expressivo", "Que comunica com força e clareza um sentido ou sentimento."),
    ("multiplicativo", "Relativo à multiplicação, ou que atua multiplicando."),
    ("longo", "Que tem grande extensão no espaço ou no tempo."),
    ("poético", "Relativo à poesia."),
    ("espectral", "Relativo ao espectro, conjunto de componentes decompostos de algo."),
    # Trigésimo terceiro lote do corpus amplo (modo rápido).
    ("argumentativo", "Que apresenta razões para defender uma posição."),
    ("curto", "Que tem pouca extensão no espaço ou no tempo."),
    ("alto", "Que tem grande altura ou está numa posição elevada."),
    ("contínuo", "Que não tem interrupção, mantendo-se ligado ao longo do tempo ou espaço."),
    # Trigésimo quarto lote do corpus amplo (modo rápido).
    ("nulo", "Que tem valor zero, ou que não produz efeito nenhum."),
    ("singular", "Que é único ou fora do comum; ou que indica um só elemento."),
    ("visual", "Relativo à visão."),
    ("oculto", "Que está escondido, fora de vista direta."),
    ("disponível", "Que está livre e pronto para ser usado."),
    ("escolar", "Relativo à escola."),
    ("distinto", "Que é diferente de outro, claramente separável."),
    ("específico", "Que se refere a um caso particular, não ao geral."),
    # Trigésimo quinto lote do corpus amplo (modo rápido).
    ("falso", "Que não corresponde à verdade."),
    ("proposicional", "Relativo a proposições, unidades lógicas que podem ser verdadeiras ou falsas."),
    # Trigésimo sexto lote do corpus amplo (modo rápido).
    ("oblíquo", "Que não é reto nem perpendicular, inclinado em relação a uma referência."),
    ("cruzado", "Que atravessa outro elemento em ângulo, formando um X."),
    ("figurado", "Que é usado num sentido diferente do literal, por comparação ou imagem."),
    ("imperfeito", "Que tem falhas, não está completo ou acabado."),
    # Trigésimo sétimo lote do corpus amplo (modo rápido).
    ("observável", "Que pode ser observado."),
    ("paciente", "Que suporta espera ou dificuldade sem se alterar."),
    ("recíproco", "Que se aplica igualmente entre as duas partes envolvidas."),
    ("sintético", "Que resume o essencial em poucos elementos; produzido artificialmente."),
    ("ausente", "Que não está presente."),
    ("bipartido", "Dividido em duas partes distintas."),
    # Achado real ao investigar candidatos ("átona", "algébricas"):
    # "átono"/"algébrico" nunca existiram como lemas.
    ("átono", "Que não recebe o acento tônico numa palavra."),
    ("algébrico", "Relacionado à álgebra ou expresso por suas operações."),
    # Trigésimo oitavo lote do corpus amplo (modo rápido).
    ("material", "Que tem existência física, palpável."),
    ("individual", "Que se refere a um só elemento, não a um grupo."),
    ("irregular", "Que não segue o padrão ou a regra esperada."),
    ("clítico", "Que se apoia foneticamente na palavra vizinha, sem acento próprio."),
    ("genuíno", "Que é verdadeiro e autêntico, sem imitação."),
    # Quadragésimo primeiro lote do corpus amplo (modo rápido).
    ("situacional", "Relativo a uma situação específica."),
    ("tradicional", "Que segue costumes transmitidos ao longo do tempo."),
    ("arbitrário", "Que depende só da vontade de quem decide, sem critério fixo."),
    ("científico", "Relativo à ciência ou construído pelos seus métodos."),
    ("cardinal", "Que indica quantidade exata; ou que é fundamental, principal."),
    ("conceptual", "Relativo a conceitos, ou construído a partir deles."),
    ("vazio", "Que não contém nada dentro."),
    ("sagrado", "Que é tratado com respeito absoluto, acima de qualquer questionamento."),
    # Quadragésimo segundo lote do corpus amplo (modo rápido).
    ("máximo", "Que é o maior possível dentro de um conjunto ou condição."),
    ("frio", "Que tem temperatura baixa."),
    ("estranho", "Que foge do habitual, difícil de explicar ou reconhecer."),
    ("discreto", "Que não chama atenção; ou que assume valores separados, não contínuos."),
    ("informativo", "Que transmite informação útil."),
    ("euclidiano", "Relativo à geometria de Euclides, baseada nos seus postulados clássicos."),
    # Quadragésimo terceiro lote do corpus amplo (modo rápido).
    ("oficial", "Que é reconhecido e aprovado por uma autoridade."),
    ("médio", "Que fica entre dois extremos, nem grande nem pequeno."),
    ("recorrente", "Que se repete com frequência."),
    ("válido", "Que cumpre as condições exigidas para ter valor ou efeito."),
    ("sozinho", "Que está sem companhia de outros."),
    # Achado real ao investigar candidato "plana": "plano" já existe como
    # substantivo, mas falta a leitura ADJETIVO ("geometria plana",
    # "figura plana") -- mesmo padrão de "substantivo"/"quadrado".
    ("plano", "Que se estende numa superfície sem elevações ou curvas."),
    ("prosódico", "Relativo à prosódia, ao ritmo e à entoação da fala."),
    ("subordinativo", "Que liga uma oração a outra da qual ela depende gramaticalmente."),
    # Quadragésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("crescente", "Que está a crescer ou a aumentar."),
    ("decrescente", "Que está a diminuir ou a decrescer."),
    ("digital", "Relativo a dígitos, dedos, ou à representação da informação em valores discretos."),
    ("dramático", "Relativo a drama, ou que causa forte impressão emocional."),
    ("inferior", "Que está abaixo de outra coisa em posição, quantidade ou qualidade."),
    ("superior", "Que está acima de outra coisa em posição, quantidade ou qualidade."),
    ("nuclear", "Relativo ao núcleo, especialmente o núcleo do átomo."),
    ("ordinal", "Que indica a posição de algo numa sequência ordenada."),
    ("proporcional", "Que mantém a mesma razão entre grandezas relacionadas."),
    ("sequencial", "Que segue uma ordem ou sequência determinada."),
    ("predominante", "Que predomina; que prevalece sobre o resto."),
    ("ponderado", "Que age com cautela e equilíbrio, avaliando bem antes de decidir."),
    ("computacional", "Relativo à computação."),
    ("agudo", "Que termina em ponta fina; intenso; que tem acento tónico na última sílaba."),
    ("cansado", "Que sente cansaço; sem energia para continuar."),
    ("demonstrativo", "Que indica ou aponta algo, situando-o em relação a quem fala."),
    ("derivacional", "Relativo à derivação, ao processo de formar palavras novas a partir de outras."),
    ("fonador", "Relativo aos órgãos que produzem os sons da fala."),
    ("junto", "Que está próximo ou em conjunto com outro elemento."),
    ("deliberado", "Que é feito de propósito, com intenção clara."),
    ("frequente", "Que ocorre muitas vezes, com regularidade."),
    ("ínfimo", "Que é o menor valor possível dentro de um conjunto, ou muito pequeno."),
    # Quadragésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    # "capaz" verificado à mão contra `_forma_adj` corrigido nesta sessão
    # (achado real do "-z", ver docstring da função) antes de entrar.
    ("previsível", "Que se pode prever com antecedência."),
    ("uniforme", "Que mantém sempre a mesma forma, ritmo ou característica."),
    ("consciente", "Que tem noção de si mesmo ou do que se passa ao seu redor."),
    ("fundamental", "Que serve de base essencial para algo."),
    ("irracional", "Que não pode ser expresso como razão entre dois números inteiros; que foge à lógica."),
    ("nacional", "Relativo a uma nação inteira."),
    ("opcional", "Que pode ser escolhido ou não, sem ser obrigatório."),
    ("permanente", "Que dura sem interrupção ou mudança ao longo do tempo."),
    ("pobre", "Que tem poucos recursos ou meios."),
    ("procedural", "Relativo a um procedimento, ou organizado em etapas sequenciais."),
    ("acessível", "Que se pode alcançar ou usar com facilidade."),
    ("capaz", "Que tem capacidade ou aptidão para fazer algo."),
    # Quadragésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    ("acidental", "Que acontece por acaso, sem intenção."),
    ("secundário", "Que vem depois do principal em importância ou ordem."),
    ("sólido", "Que tem forma própria e resiste a mudanças de forma; consistente."),
    ("genérico", "Que se aplica a um conjunto amplo, sem especificar detalhes."),
    ("gradual", "Que acontece aos poucos, em etapas."),
    ("imediato", "Que acontece logo, sem demora."),
    ("impossível", "Que não pode acontecer ou ser realizado."),
    ("maduro", "Que atingiu pleno desenvolvimento."),
    ("privado", "Que pertence a um indivíduo, não é de acesso público."),
    ("trivial", "Que é simples, sem complicação ou importância especial."),
    ("cultural", "Relativo à cultura de um grupo ou sociedade."),
    # Quadragésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    ("profissional", "Relativo a uma profissão, ou que exerce uma atividade com competência."),
    ("particular", "Que pertence ou diz respeito a uma pessoa ou caso específico, não geral."),
    ("orgulhoso", "Que sente ou demonstra orgulho."),
    ("extenso", "Que se estende por uma grande área ou duração."),
    ("didático", "Que tem como objetivo ensinar de forma clara."),
    ("aleatório", "Que depende do acaso, sem padrão previsível."),
    ("idêntico", "Exatamente igual a outra coisa."),
    ("geográfico", "Relativo à geografia, ao espaço físico da Terra."),
    ("lógico", "Relativo à lógica, ou que segue um raciocínio coerente."),
    # Quadragésimo oitavo lote do corpus amplo (modo massa, meta 50.000).
    ("verdadeiro", "Que corresponde à realidade dos factos."),
    ("abundante", "Que existe em grande quantidade."),
    ("caro", "Que custa muito dinheiro, ou muito estimado."),
    ("grave", "Que tem consequências sérias, ou que tem acento tónico na penúltima sílaba."),
    ("essencial", "Que é indispensável, que constitui a parte mais importante de algo."),
    ("institucional", "Relativo a uma instituição."),
    ("implícito", "Que está subentendido, sem ser dito diretamente."),
    ("cronológico", "Organizado segundo a ordem em que os factos aconteceram."),
    ("direito", "Que segue uma linha reta sem desvios, ou que corresponde à justiça e à lei."),
    ("compreensível", "Que se pode entender com facilidade."),
    ("contável", "Que se pode contar, elemento a elemento."),
    ("auditável", "Que se pode examinar e verificar formalmente."),
    ("pronunciável", "Que se pode pronunciar."),
    ("computável", "Que pode ser calculado por um procedimento finito e determinado."),
    ("possessivo", "Que indica posse ou pertença."),
    ("ativo", "Que age ou pratica a ação, em vez de recebê-la."),
    ("adjetival", "Relativo ao adjetivo, ou que funciona como um."),
    ("argumental", "Relativo ao argumento de um verbo ou de uma função."),
    ("autoral", "Relativo ao autor ou à autoria de uma obra."),
    ("reconhecível", "Que pode ser reconhecido ou identificado com facilidade."),
    ("recuperável", "Que pode ser recuperado depois de perdido ou danificado."),
    ("alfabético", "Que segue a ordem das letras do alfabeto."),
    ("contrário", "Que se opõe ou está em direção oposta a algo."),
    ("dinâmico", "Que envolve movimento ou mudança constante, em vez de ficar parado."),
    ("estético", "Relativo à beleza ou à apreciação do que é belo."),
    # Quadragésimo nono lote do corpus amplo (modo massa, meta 50.000).
    ("físico", "Relativo ao corpo, ou à física como ciência."),
    ("infeliz", "Que não é feliz."),
    ("normal", "Que segue o padrão habitual, sem nada de anómalo."),
    ("elementar", "Que é básico, simples, na sua forma mais fundamental."),
    ("teatral", "Relativo ao teatro, ou exageradamente dramático."),
    ("unipessoal", "Que envolve ou pertence a uma só pessoa."),
    # Quinquagésimo lote do corpus amplo (modo massa, meta 50.000).
    ("anômalo", "Que se desvia do padrão normal; irregular."),
    ("incompleto", "Que não está completo, ao qual falta uma parte."),
    ("comutativo", "Que produz o mesmo resultado independentemente da ordem dos elementos envolvidos."),
    ("melhor", "Que tem mais qualidade ou valor em comparação com outro."),
    ("prefixal", "Relativo ao prefixo, ao elemento colocado antes da raiz de uma palavra."),
    ("sufixal", "Relativo ao sufixo, ao elemento colocado depois da raiz de uma palavra."),
    ("surdo", "Que não ouve, ou (som) produzido sem vibração das cordas vocais."),
    ("provisório", "Que dura só até ser substituído por algo definitivo."),
    ("subjetivo", "Que depende do ponto de vista pessoal, não de fatos objetivos."),
    # Quinquagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    ("animado", "Que tem energia e entusiasmo; que tem vida."),
    ("binomial", "Relativo a uma expressão com dois termos."),
    ("decidível", "Que pode ser decidido por um procedimento finito e determinado."),
    ("definitivo", "Que não vai mudar; final."),
    ("circular", "Que tem forma de círculo, ou que gira em torno de algo."),
    ("cego", "Que não pode ver, privado do sentido da visão."),
    ("eletrónico", "Relativo à eletrónica, que funciona por meio de circuitos elétricos."),
    ("estruturado", "Que tem uma estrutura organizada e definida."),
    # achado real: "vizinho" já existia só como substantivo (sem plural
    # gerado); ganha aqui a leitura ADJETIVO completa ("casa vizinha"),
    # mesmo padrão de dupla classe já usado em "substantivo"/"quadrado".
    ("vizinho", "Que está perto ou ao lado de outro."),
    ("vário", "Que existe em número ou variedade maior que um."),
    ("baixo", "Que tem pouca altura, ou está em posição inferior."),
    ("derivado", "Que se origina ou é formado a partir de outra coisa."),
    # Quinquagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    ("paralelo", "Que mantém sempre a mesma distância de outra linha, sem nunca se cruzar."),
    ("lírico", "Relativo à poesia que expressa sentimentos pessoais."),
    ("modal", "Relativo ao modo, à forma como algo é expresso ou é possível."),
    ("composicional", "Que resulta da composição de partes mais simples."),
    ("assertivo", "Que afirma algo com firmeza e segurança."),
    ("identificável", "Que se pode identificar."),
    # Quinquagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("ambíguo", "Que pode ter mais de uma interpretação ou sentido."),
    ("audível", "Que se pode ouvir."),
    ("construtivo", "Que contribui de forma positiva para melhorar algo."),
    ("declarativo", "Que declara ou afirma algo diretamente."),
    ("distintivo", "Que serve para distinguir algo de outra coisa."),
    ("cartesiano", "Relativo ao sistema de coordenadas de Descartes, ou ao pensamento lógico e metódico."),
    # achado real: "múltiplo" já existia só como substantivo (sem plural
    # gerado); ganha aqui a leitura ADJETIVO ("razões múltiplas").
    ("múltiplo", "Que existe em várias unidades ou ocorrências."),
    ("canónico", "Que segue o modelo ou a forma aceita como referência."),
    ("parentético", "Que está inserido entre parênteses ou marcas equivalentes, como explicação à parte."),
    ("pleonástico", "Que repete desnecessariamente uma ideia já expressa."),
    # Achado real (auditoria de paradigma, não vocabulário novo): estes 4
    # já existiam em `lexico_base.json` com uma forma só, sem plural nem
    # feminino gerado -- "restritas"/"pública"/"promissores" etc. não
    # existiam no dicionário vivo, confirmado rodando antes desta linha.
    ("coerente", "Que não contradiz os conceitos já aceites."),
    ("restrito", "Que exige permissão ou reconhecimento antes de ser revelado."),
    ("público", "Que pode ser usado sem restrição especial."),
    ("promissor", "Que gerou ferramenta, método ou avanço aplicável."),
    # Quinquagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    ("sistemático", "Que segue um sistema, organizado de forma metódica e regular."),
    ("pedagógico", "Relativo à pedagogia, ao ensino e à forma de transmitir conhecimento."),
    # achado real: "total" já existia só como substantivo; ganha aqui a
    # leitura ADJETIVO ("quantidade total"), o que já resolve
    # "totalmente" de graça via a regra "-mente" ligada ao dicionário.
    ("total", "Que abrange tudo, sem exceção ou parte de fora."),
    ("vocabular", "Relativo ao vocabulário, ao conjunto de palavras de uma língua."),
    # achado real: "repetido" só existia como particípio (VERBO); ganha
    # aqui a leitura ADJETIVO ("um erro repetido"), o que já resolve
    # "repetidamente" de graça via a regra "-mente" ligada ao dicionário.
    ("repetido", "Que ocorre ou é feito mais de uma vez."),
    ("articulatório", "Relativo à articulação dos sons da fala pelo aparelho fonador."),
    ("aditivo", "Que se soma a outra coisa, acrescentando algo."),
    # Quinquagésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    ("psicológico", "Relativo à psicologia, à mente e ao comportamento."),
    ("topológico", "Relativo à topologia, ao estudo das propriedades que se mantêm sob deformação contínua."),
    ("amostral", "Relativo a uma amostra, ao conjunto reduzido usado para representar um todo."),
    ("aplicável", "Que se pode aplicar."),
    ("autónomo", "Que age por si mesmo, sem depender de outros."),
    ("removível", "Que se pode remover."),
    ("solúvel", "Que se pode dissolver."),
    ("residual", "Que resta depois de um processo, em pequena quantidade."),
    # Quinquagésimo oitavo lote do corpus amplo (modo massa, meta 50.000).
    # Achado real no caminho: `_forma_adj` não tratava "-il" átono
    # ("útils", errado) -- corrigido (útil->úteis, mesma família de
    # fácil/hábil/dócil, ver docstring da função).
    ("cíclico", "Que se repete em ciclos."),
    ("filosófico", "Relativo à filosofia."),
    ("incompatível", "Que não pode coexistir ou funcionar junto com outra coisa."),
    ("provável", "Que tem grande chance de acontecer."),
    ("robusto", "Que é forte e resistente."),
    ("dual", "Que tem correspondência simétrica com outro conceito, trocando papéis."),
    ("triangular", "Que tem forma de triângulo."),
    ("útil", "Que serve para alguma coisa; que tem utilidade."),
    # Quinquagésimo nono lote do corpus amplo (modo massa, meta 50.000).
    ("seguro", "Que está livre de perigo, ou que tem confiança."),
    ("silencioso", "Que não produz som, ou que está em silêncio."),
    ("superficial", "Que está ou fica apenas na superfície, sem profundidade."),
    ("angular", "Relativo a um ângulo."),
    ("agrícola", "Relativo à agricultura, ao cultivo da terra."),
    ("amoroso", "Relativo ao amor, ou que demonstra amor."),
    ("administrativo", "Relativo à administração."),
    ("académico", "Relativo à academia, ao ensino superior ou à investigação."),
    ("flexional", "Relativo à flexão, à mudança de forma de uma palavra para marcar género, número, tempo ou pessoa."),
    # Sexagésimo lote do corpus amplo (modo massa, meta 50.000). Achado
    # real no caminho: `_forma_adj` não tratava "-ul" ("azuls", errado) --
    # corrigido (azul->azuis, mesma troca de "-al", ver docstring).
    ("atómico", "Relativo ao átomo."),
    ("biológico", "Relativo à biologia, aos seres vivos."),
    ("azul", "Que tem a cor do céu limpo ou do mar."),
    ("belo", "Que tem beleza; agradável à vista."),
    ("branco", "Que tem a cor da neve ou do leite; ausência de cor."),
    ("colorido", "Que tem cor, ou várias cores."),
    ("crítico", "Relativo à crítica, ou que representa um ponto decisivo."),
    # Sexagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    # "espanhol"/"francês" ficam de fora por ora: precisam de acento novo
    # ("-ol"->"óis", "-ês"->"eses") que `_forma_adj` ainda não trata --
    # mesma disciplina de registar como pendente em vez de adivinhar.
    ("diagonal", "Que atravessa de um canto a outro, sem ser paralelo aos lados."),
    ("direcional", "Relativo a uma direção específica."),
    ("eficaz", "Que produz o efeito desejado."),
    ("educativo", "Que tem como propósito ensinar."),
    ("efetivo", "Que produz realmente o efeito esperado; real."),
    ("enorme", "Que tem tamanho muito grande."),
    ("exclusivo", "Que pertence ou está reservado a um único elemento ou grupo."),
    ("favorável", "Que é propício ou vantajoso."),
    ("fiel", "Que se mantém firme e leal a um compromisso, pessoa ou ideia."),
    ("feminino", "Relativo ao género gramaticalmente distinto do masculino, ou próprio da mulher."),
    ("pontual", "Que ocorre num ponto específico, sem se estender."),
    ("tradutório", "Relativo à tradução de um texto ou linguagem para outra."),
    ("coordenativo", "Que liga elementos do mesmo nível sintático, sem subordinação."),
    ("concessivo", "Que expressa uma concessão, admitindo um facto apesar de outro."),
    ("consecutivo", "Que expressa consequência ou vem em sequência imediata."),
    ("regressivo", "Que volta ou tende a voltar a um estado anterior."),
    ("restritivo", "Que limita ou reduz o alcance de algo."),
    ("produtivo", "Que produz resultado com eficiência, ou gera bastante."),
    ("qualificativo", "Que atribui uma qualidade a algo."),
    ("assindético", "Que liga orações ou termos sem conjunção."),
    ("sindético", "Que liga orações ou termos por meio de conjunção."),
    ("restante", "Que sobra depois de retirada uma parte."),
    # Sexagésimo segundo lote do corpus amplo (modo massa, meta 50.000).
    ("moderno", "Que pertence ou é próprio do tempo atual."),
    ("minúsculo", "Que é muito pequeno."),
    ("molhado", "Que está coberto ou impregnado de água ou outro líquido."),
    ("populacional", "Relativo a uma população."),
    ("popular", "Que é próprio ou apreciado pelo povo em geral."),
    ("presencial", "Que exige a presença física, feito em pessoa."),
    ("preto", "Que tem a cor mais escura possível; ausência de luz refletida."),
    ("recente", "Que aconteceu há pouco tempo."),
    ("prático", "Que é voltado para a ação e a utilidade, em vez da teoria."),
    # Lote F (sessão contínua, corpus amplo, meta 50.000).
    ("ímpar", "Que não é divisível por dois."),
    ("último", "Que vem depois de todos os outros, sem mais nenhum a seguir."),
    ("estreito", "Que tem pouca largura."),
    ("rico", "Que possui muitos bens ou recursos em abundância."),
    ("oposto", "Que está do lado contrário, ou que se contrapõe a outra coisa."),
    ("quente", "Que tem temperatura elevada."),
    # Sexagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    ("vertical", "Que segue a direção de cima para baixo, perpendicular ao horizonte."),
    ("triste", "Que sente ou expressa tristeza."),
    ("típico", "Que é característico ou representativo de algo."),
    ("ótimo", "Que é excelente, o melhor possível."),
    ("artificial", "Que é produzido pelo ser humano, não natural."),
    ("brasileiro", "Relativo ao Brasil."),
    ("barato", "Que custa pouco dinheiro."),
    # Lote F2 (sessão contínua, corpus amplo, meta 50.000).
    ("grego", "Relativo à Grécia, ou próprio da sua língua e cultura."),
    ("trigonométrico", "Relativo à trigonometria."),
    ("polinomial", "Relativo a um polinómio."),
    ("posicional", "Relativo à posição, cujo valor depende do lugar que ocupa."),
    ("fracionário", "Que é expresso em fração, ou que representa uma parte de um todo."),
    ("numérico", "Relativo aos números, ou expresso por eles."),
    ("impróprio", "Que não é adequado, ou que foge à forma habitual esperada."),
    ("hipotético", "Que se baseia numa hipótese, ainda não confirmado."),
    ("incorreto", "Que contém um erro; que não está certo."),
    ("executável", "Que pode ser executado ou posto em prática."),
    ("imutável", "Que não pode ser alterado depois de criado."),
    # Sexagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("denso", "Que tem grande quantidade de matéria ou elementos num espaço reduzido."),
    ("desumano", "Que não demonstra características humanas de compaixão; cruel."),
    ("dorsal", "Relativo às costas ou à parte de trás de algo."),
    ("dourado", "Que tem a cor do ouro."),
    ("durável", "Que dura muito tempo, resistente ao desgaste."),
    ("eficiente", "Que produz um bom resultado com o mínimo de recursos."),
    ("emocional", "Relativo às emoções."),
    ("estrangeiro", "Que vem de outro país; que não é nativo do lugar."),
    ("estático", "Que não se move ou não muda; parado."),
    ("financeiro", "Relativo ao dinheiro e à sua gestão."),
    # Sexagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    ("mental", "Relativo à mente."),
    ("obtuso", "Que tem ângulo maior que noventa graus, ou pouco perspicaz."),
    ("multidisciplinar", "Que envolve várias disciplinas ou áreas de conhecimento."),
    ("percentual", "Relativo a uma percentagem."),
    ("pentagonal", "Relativo a um pentágono, com cinco lados."),
    ("planeado", "Que foi previamente planeado."),
    ("poderoso", "Que tem muito poder ou força."),
    ("prévio", "Que acontece ou existe antes de outra coisa."),
    ("recursivo", "Que se define ou se aplica repetidamente em termos de si mesmo."),
    ("redundante", "Que repete desnecessariamente algo já dito ou existente."),
    # Lote F3 (sessão contínua, corpus amplo, meta 50.000).
    ("divisível", "Que pode ser dividido, sem resto, por outro número."),
    ("experimental", "Que se baseia em experiência ou ensaio, ainda em prova."),
    ("degenerado", "Que perdeu as propriedades típicas do caso geral, reduzindo-se a um caso especial."),
    ("pleno", "Que está completo, sem faltar nada."),
    ("bruto", "Que ainda não foi refinado ou tratado, ou que é medido sem descontar nada."),
    ("decorativo", "Que serve para decorar, sem função essencial."),
    ("consultável", "Que pode ser consultado."),
    ("determinístico", "Que segue sempre o mesmo resultado a partir das mesmas condições, sem acaso envolvido."),
    ("categórico", "Que é afirmado sem condição ou exceção; taxativo."),
    ("quotidiano", "Que acontece todos os dias; próprio do dia a dia."),
    # Sexagésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    ("tardio", "Que acontece mais tarde do que o esperado."),
    ("temporário", "Que dura apenas por um certo tempo, não permanente."),
    ("teórico", "Relativo à teoria, baseado em princípios gerais e não na prática."),
    ("tolerante", "Que aceita ou suporta opiniões e comportamentos diferentes dos seus."),
    ("transversal", "Que atravessa de um lado a outro, cruzando uma direção principal."),
    ("usual", "Que é comum, habitual."),
    ("óbvio", "Que é evidente, fácil de perceber."),
    ("completivo", "Que completa o sentido de outro termo, geralmente um verbo ou nome."),
    ("conformativo", "Que expressa conformidade com aquilo que se afirma."),
    ("adversativo", "Que expressa oposição ou contraste entre duas ideias."),
    ("adnominal", "Que se liga diretamente a um nome, modificando-o."),
    ("toante", "Que rima apenas nas vogais, sem exigir igualdade nas consoantes."),
    # Achado real ao investigar a falha do predicativo em oração causal
    # ("Maria correu porque estava atrasada."): "atrasado" nunca tinha
    # entrado no léxico, então "atrasada" caía em DESCONHECIDA e a
    # gramática não achava nenhuma leitura ADJETIVO pra marcar o
    # predicativo -- não era bug de gramática, era lacuna de léxico.
    ("atrasado", "Que chegou ou aconteceu depois da hora ou do prazo previsto."),
    # Expansão de adjetivos técnicos e gerais em português.
    ("completo", "Que tem todas as suas partes e elementos, não faltando nada."),
    ("extensível", "Que pode ser estendido ou expandido para incluir novos recursos."),
    ("farto", "Que existe em grande quantidade ou abundância."),
    ("firme", "Que se mantém estável, constante e seguro."),
    ("fixo", "Que não muda de posição, valor ou estado."),
    ("isolado", "Que se encontra separado ou desligado de outros elementos."),
    ("novo", "Que foi criado ou introduzido recentemente."),
    ("flexível", "Que pode ser adaptado ou modificado facilmente."),
    ("síncrono", "Que ocorre ao mesmo tempo ou com sincronismo de fases."),
    ("assíncrono", "Que não ocorre ao mesmo tempo, funcionando de forma independente."),
    ("híbrido", "Que combina elementos ou tecnologias de origens diferentes."),
    ("otimizado", "Que foi ajustado para obter o melhor desempenho possível."),
    ("reutilizável", "Que pode ser usado novamente em diferentes contextos."),
    ("portável", "Que pode ser executado ou transferido para diferentes ambientes sem alteração."),
    ("reverso", "Que tem direção ou ordem oposta à habitual."),
    ("compacto", "Que ocupa pouco espaço ou reúne muita informação de forma concentrada."),
    ("intacto", "Que se conserva no estado original, sem sofrer alteração ou dano."),
    ("remoto", "Que se situa ou opera à distância, de forma não local."),
    ("rápido", "Que se move ou executa tarefas em pouco tempo."),
    ("lento", "Que se move ou executa tarefas com velocidade reduzida."),
    ("nítido", "Que é claro, bem definido e fácil de perceber."),
    ("opaco", "Que não deixa passar a luz ou que esconde os detalhes internos."),
    ("invisível", "Que não pode ser visto ou percebido diretamente."),
    ("interativo", "Que permite a interação direta entre o utilizador e o sistema."),
    ("escalável", "Que pode expandir a sua capacidade para lidar com maior volume de trabalho."),
    ("configurável", "Que permite ajustar os seus parâmetros e opções de funcionamento."),
    ("integrado", "Que funciona de forma conjunta e harmoniosa com outros componentes."),
    ("assimétrico", "Que não possui simetria ou proporção igual em ambos os lados."),
    ("periódico", "Que ocorre ou se repete em intervalos de tempo regulares."),
    ("estatístico", "Relativo à estatística, à coleta e análise de dados numéricos."),
    # Lote de expansão de adjetivos regulares técnicos e gerais.
    ("adequado", "Que é apropriado, conveniente ou satisfatório para determinado fim."),
    ("aplicado", "Que se põe em prática ou é voltado a um uso específico."),
    ("assintótico", "Relativo a assíntota, ou ao comportamento no limite de uma função ou algoritmo."),
    ("atribuível", "Que pode ser atribuído a uma causa, origem ou entidade."),
    ("concorrente", "Que acontece ou executa ao mesmo tempo que outro."),
    ("configurado", "Que teve os seus parâmetros ajustados para um fim específico."),
    ("correto", "Que está em conformidade com a verdade, a regra ou a norma."),
    ("declarado", "Que foi afirmado ou especificado de modo explícito."),
    ("desejado", "Que é almejado ou esperado num determinado processo ou resultado."),
    ("diferenciado", "Que possui características próprias que o distinguem dos demais."),
    ("distribuído", "Que se encontra repartido por múltiplos nós ou locais."),
    ("escalonado", "Que está disposto em etapas, níveis ou graus sucessivos."),
    ("esperado", "Que se prevê que aconteça ou que constitui o resultado previsto."),
    ("estendível", "Que permite extensão ou expansão de suas funcionalidades."),
    ("estruturante", "Que serve de base ou fundação para a organização de algo."),
    ("hierárquico", "Organizado em níveis de dependência ou autoridade."),
    ("indexado", "Que se encontra registrado ou organizado por índices para consulta rápida."),
    ("indutivo", "Que procede por indução, do particular para o geral."),
    ("intermediário", "Que se situa entre dois pontos, fases ou valores."),
    ("invariante", "Que não sofre alteração sob determinadas transformações."),
    ("iterativo", "Que procede por repetições sucessivas de um ciclo de operações."),
    ("mapeado", "Que teve suas correspondências ou localizações estabelecidas."),
    ("mensurável", "Que pode ser medido ou quantificado."),
    ("modificado", "Que sofreu alteração na sua forma, estado ou conteúdo."),
    ("monotônico", "Que mantém uma tendência constante de crescimento ou decrescimento."),
    ("multidimensional", "Que possui ou envolve múltiplas dimensões."),
    ("ordenável", "Que possui critérios que permitem a sua ordenação."),
    ("parametrizado", "Cujos atributos ou comportamentos são definidos por parâmetros."),
    ("persistente", "Que se mantém ao longo do tempo ou após o encerramento de uma sessão."),
    ("preditivo", "Que serve para prever comportamentos ou resultados futuros."),
)


_VERBOS: tuple[tuple[str, str], ...] = (
    ("conversar", "Trocar mensagens com contexto e continuidade."),
    ("entender", "Captar a intenção e o conteúdo de um pedido."),
    ("explicar", "Tornar uma ideia clara para outra pessoa."),
    ("ensinar", "Organizar conhecimento em caminho de aprendizagem."),
    ("aprender", "Transformar explicação e prática em domínio."),
    ("construir", "Formar algo a partir de partes anteriores."),
    ("reconstruir", "Refazer uma ideia desde o fundamento."),
    ("validar", "Testar se uma construção funciona."),
    ("melhorar", "Remover falhas e aumentar qualidade."),
    ("aprimorar", "Ajustar e elevar o nível de um sistema ou ideia."),
    ("desmontar", "Separar uma ideia em partes menores."),
    ("resumir", "Dizer o essencial em menos palavras."),
    ("exemplificar", "Mostrar uma ideia por caso concreto."),
    ("praticar", "Treinar por exercícios."),
    ("continuar", "Avançar a partir do ponto atual."),
    ("perguntar", "Solicitar informação, aula, exemplo ou ação."),
    ("responder", "Devolver uma resposta ao pedido recebido."),
    ("comparar", "Ver semelhanças, diferenças e consequências."),
    ("testar", "Submeter uma ideia a casos para verificar estabilidade."),
    ("formalizar", "Dar forma precisa a uma construção."),
    ("flexionar", "Variar uma palavra por gênero, número, pessoa, tempo ou modo."),
    ("concordar", "Ajustar palavras relacionadas dentro da construção."),
    ("acentuar", "Marcar graficamente uma palavra quando a construção exigir."),
    ("pontuar", "Inserir marcas que regulam limite, pausa e intenção."),
    ("segmentar", "Separar uma forma em partes menores para análise."),
    ("relacionar", "Ligar partes da construção por função ou sentido."),
    ("referir", "Apontar para um alvo textual ou situacional."),
    ("retomar", "Voltar a um referente já construído."),
    ("inferir", "Obter sentido por relação entre o dito e o implicado."),
    ("coordenar", "Ligar unidades de mesmo nível funcional."),
    ("subordinar", "Ligar uma unidade a outra da qual depende."),
    ("complementar", "Completar sentido de uma construção."),
    ("reger", "Orientar ou exigir uma relação gramatical."),
    ("variar", "Mudar forma ou uso conforme condição."),
    ("registrar", "Ajustar ou fixar uma forma de linguagem em certo contexto."),
    ("afirmar", "Apresentar algo como sustentado ou posto."),
    ("negar", "Marcar recusa, ausência ou cancelamento de uma afirmação possível."),
    ("interrogar", "Construir pergunta ou busca de informação."),
    ("exclamar", "Marcar força expressiva, surpresa ou emoção."),
    ("interpretar", "Construir sentido a partir de texto, contexto e relações limitadas."),
    ("revisar", "Retornar ao texto para verificar e melhorar coerência, coesão, norma e clareza."),
    # Lote extraído do corpus amplo (Fase 3/4 do plano de léxico).
    ("permitir", "Dar possibilidade ou abertura para algo acontecer ou ser feito."),
    ("reconhecer", "Identificar algo como já conhecido ou válido."),
    ("confundir", "Tratar por engano uma coisa como se fosse outra."),
    ("verificar", "Conferir se algo é verdadeiro ou está correto."),
    ("ligar", "Estabelecer conexão entre duas partes ou conceitos."),
    ("organizar", "Dispor partes numa ordem clara e funcional."),
    ("distinguir", "Perceber e marcar a diferença entre duas coisas."),
    # Segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("existir", "Ter presença real dentro de um domínio."),
    ("pertencer", "Fazer parte de um conjunto ou categoria."),
    ("precisar", "Ter necessidade de algo para continuar."),
    ("apresentar", "Mostrar algo pela primeira vez a alguém."),
    ("implementar", "Construir em código uma ideia já especificada."),
    ("exigir", "Pedir como condição necessária."),
    ("usar", "Empregar algo para um fim."),
    ("depender", "Precisar de outra coisa para existir ou funcionar."),
    # Terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("significar", "Ter determinado sentido ou valor."),
    ("expressar", "Tornar visível ou comunicável um sentido ou sentimento."),
    ("partir", "Sair de um ponto de origem em direção a outro."),
    ("fingir", "Simular algo que não é real ou verdadeiro."),
    ("materializar", "Tornar concreto algo que antes era só ideia ou possibilidade."),
    ("nascer", "Passar a existir a partir de uma origem."),
    ("dever", "Ter obrigação de fazer algo."),
    # Quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("separar", "Colocar partes distintas fora de contacto ou de um mesmo grupo."),
    ("criar", "Fazer existir algo que antes não existia."),
    ("chegar", "Alcançar um destino ou ponto de referência."),
    ("fechar", "Encerrar ou concluir algo que estava aberto ou em curso."),
    ("aprovar", "Confirmar que algo está correto ou aceitável."),
    # Sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("corrigir", "Ajustar algo para remover erro ou falha."),
    # Sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("ficar", "Permanecer num estado ou lugar."),
    ("aparecer", "Passar a ser visível ou perceptível."),
    # Oitavo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("passar", "Mover-se de um ponto a outro, ou decorrer no tempo."),
    # Nono lote do corpus amplo (Fase 3/4, corte seguinte).
    ("impedir", "Fazer com que algo não aconteça ou não seja possível."),
    ("servir", "Ser útil ou adequado para um fim."),
    ("marcar", "Assinalar ou determinar algo de forma visível."),
    # Décimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("aproximar", "Tornar mais próximo ou chegar perto de um valor exato."),
    ("representar", "Apresentar algo por meio de um símbolo, imagem ou substituto."),
    # Achado real: "recriar", "generalizar", "multiplicar" e "dividir" já
    # existiam em `lexico_base.json`, mas só com a forma "infinitivo" --
    # nenhuma conjugação, mesmo sendo verbos regulares. Trazidos pra cá
    # pra ganhar o paradigma completo (a leitura duplicada do infinitivo
    # que sobra no JSON é inofensiva, mesmo caso já tolerado por
    # "construir"/"validar"/"testar"). "subtrair" fica de fora por ora --
    # é irregular ("-air": subtraio/subtrais/subtraímos), a regra
    # genérica de "-ir" geraria formas erradas, mesma classe de cuidado
    # já usada para "-uir"/"-guir".
    ("recriar", "Construir novamente por fundamentos próprios, sem copiar como dogma."),
    ("generalizar", "Estender uma construção para mais casos mantendo a regra."),
    ("multiplicar", "Repetir uma adição de grupos iguais."),
    ("dividir", "Repartir ou procurar quantas vezes uma parte cabe no todo."),
    # Décimo primeiro lote do corpus amplo (Fase 3/4, corte seguinte).
    # "substituir" verificado com cuidado: NÃO é da família "-struir" (ver
    # achado em `_e_verbo_struir_com_o_o`) -- fica regular no presente,
    # sem troca "ó".
    ("substituir", "Colocar algo no lugar de outra coisa."),
    ("analisar", "Examinar as partes de algo para entender sua estrutura ou sentido."),
    # Décimo segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("controlar", "Verificar e ajustar algo para que siga dentro do esperado."),
    ("fixar", "Tornar algo estável ou definido num lugar ou valor."),
    ("mostrar", "Tornar algo visível ou perceptível para alguém."),
    # Décimo terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("observar", "Olhar ou acompanhar algo com atenção para entender ou registrar."),
    ("ocorrer", "Acontecer ou se manifestar num determinado momento."),
    ("crescer", "Aumentar em tamanho, quantidade ou desenvolvimento."),
    # Décimo quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("medir", "Determinar a extensão, quantidade ou grau de algo."),
    ("repetir", "Fazer ou dizer novamente algo já feito ou dito antes."),
    # Décimo quinto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("aceitar", "Concordar em receber ou reconhecer algo como válido."),
    # Décimo sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    # "conter"/"manter" ficam de fora por ora: compostos de "ter", herdam a
    # mesma irregularidade (contenho/contém/contêm, não "conto"/"contem"
    # que a regra genérica de "-er" geraria) -- mesma classe de cuidado já
    # usada para "vir"/"subtrair".
    ("transformar", "Mudar a forma, natureza ou estado de algo."),
    ("garantir", "Assegurar que algo vai acontecer ou se manter verdadeiro."),
    # Décimo sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("definir", "Estabelecer com precisão o sentido ou os limites de algo."),
    ("reduzir", "Tornar menor em tamanho, quantidade ou intensidade."),
    # Décimo oitavo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("aplicar", "Colocar algo em uso prático sobre um caso concreto."),
    ("produzir", "Fazer existir ou gerar algo através de um processo."),
    ("conferir", "Verificar se algo está certo comparando com uma referência."),
    # Décimo nono lote do corpus amplo (Fase 3/4, corte seguinte).
    ("apoiar", "Dar sustentação ou suporte a algo ou alguém."),
    ("localizar", "Determinar ou encontrar a posição exata de algo."),
    ("declarar", "Afirmar algo de forma clara e explícita."),
    # Vigésimo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("citar", "Mencionar ou referir algo como exemplo ou apoio."),
    ("preservar", "Manter algo protegido de dano ou alteração ao longo do tempo."),
    ("sustentar", "Manter algo firme, apoiado ou verdadeiro ao longo do tempo."),
    ("receber", "Passar a ter algo que vem de outra origem."),
    # Vigésimo primeiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("inventar", "Criar algo que não existia antes, a partir de ideia própria."),
    ("tratar", "Lidar com algo ou alguém de determinada maneira."),
    ("adicionar", "Juntar algo a outra coisa já existente."),
    ("devolver", "Entregar de volta algo que foi recebido ou emprestado."),
    ("confirmar", "Tornar certo algo que antes era incerto ou proposto."),
    # Vigésimo segundo lote do corpus amplo (Fase 3/4, corte seguinte).
    ("formar", "Dar origem ou constituir algo através de suas partes."),
    # Vigésimo terceiro lote do corpus amplo (Fase 3/4, corte seguinte).
    ("apagar", "Fazer desaparecer algo que estava registado ou visível."),
    ("acrescentar", "Juntar algo a mais ao que já existe."),
    # Vigésimo quarto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("mudar", "Passar de um estado, lugar ou forma para outro diferente."),
    # Vigésimo quinto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("cobrir", "Colocar algo sobre outra coisa para proteger ou esconder."),
    ("reunir", "Juntar pessoas ou coisas num mesmo lugar ou grupo."),
    ("restar", "Continuar a existir depois que o resto foi retirado ou usado."),
    # Vigésimo sexto lote do corpus amplo (Fase 3/4, corte seguinte).
    ("escolher", "Selecionar uma opção entre várias possíveis."),
    ("funcionar", "Operar ou executar a função para a qual foi feito."),
    # Vigésimo sétimo lote do corpus amplo (Fase 3/4, corte seguinte).
    # "escrever"/"abrir" verificados com cuidado antes de entrar: têm
    # particípio irregular ("escrito"/"aberto", não "escrevido"/"abrido")
    # -- ver `_PARTICIPIOS_IRREGULARES`. Regulares em tudo o resto.
    ("escrever", "Representar palavras através de sinais gráficos."),
    ("abrir", "Tornar algo acessível, retirando o que fechava a passagem."),
    # Vigésimo oitavo lote do corpus amplo (modo rápido).
    ("classificar", "Organizar elementos em categorias segundo um critério."),
    ("começar", "Dar início a algo."),
    ("fornecer", "Dar ou disponibilizar algo que é necessário."),
    ("identificar", "Reconhecer algo ou alguém como sendo o que é."),
    ("integrar", "Juntar partes para formar um todo coerente."),
    ("modificar", "Mudar uma característica de algo, sem alterar sua natureza total."),
    # Vigésimo nono lote do corpus amplo (modo rápido).
    ("orientar", "Indicar a direção ou o caminho correto a seguir."),
    ("atribuir", "Dar ou associar uma característica, valor ou responsabilidade a algo."),
    ("situar", "Colocar algo numa posição ou contexto determinado."),
    ("permanecer", "Continuar a existir ou a estar num mesmo estado ou lugar."),
    # Trigésimo quarto lote do corpus amplo (modo rápido).
    ("compreender", "Entender o sentido de algo."),
    ("decidir", "Escolher entre alternativas, encerrando uma dúvida ou hesitação."),
    ("conservar", "Manter algo no seu estado original, sem deixar que se estrague."),
    # Trigésimo quinto lote do corpus amplo (modo rápido).
    ("alterar", "Mudar uma característica de algo."),
    ("introduzir", "Fazer entrar algo pela primeira vez num lugar ou contexto."),
    ("possuir", "Ter algo como propriedade ou característica própria."),
    ("tornar", "Fazer passar a ser de outro jeito."),
    ("contrastar", "Mostrar diferença acentuada ao ser colocado ao lado de outra coisa."),
    # Achado real: "estudar" já existia em `lexico_base.json`, mas só com
    # presente (5 formas) -- verbo totalmente regular, sem irregularidade
    # nenhuma, trazido pra cá pra ganhar o paradigma completo.
    ("estudar", "Aplicar atenção à aprendizagem de algo."),
    # Trigésimo sexto lote do corpus amplo (modo rápido).
    ("deixar", "Permitir que algo aconteça, ou abandonar algo num lugar."),
    # Trigésimo sétimo lote do corpus amplo (modo rápido).
    ("descrever", "Representar por palavras as características de algo."),
    ("estabelecer", "Fixar ou determinar algo de forma definitiva."),
    ("nomear", "Dar um nome a algo ou alguém."),
    ("apontar", "Indicar algo com o dedo ou por outro meio direto."),
    # Trigésimo oitavo lote do corpus amplo (modo rápido).
    # "ganhar" verificado antes: particípio irregular "ganho", regular no
    # resto -- ver `_PARTICIPIOS_IRREGULARES`.
    ("ganhar", "Obter algo como resultado de esforço, disputa ou sorte."),
    ("associar", "Ligar mentalmente uma coisa a outra."),
    # Trigésimo nono lote do corpus amplo (modo rápido).
    ("terminar", "Chegar ao fim, ou levar algo ao fim."),
    ("selecionar", "Escolher um ou mais elementos entre vários possíveis."),
    # Quadragésimo lote do corpus amplo (modo rápido).
    ("investigar", "Procurar de forma sistemática para descobrir a verdade sobre algo."),
    ("considerar", "Ponderar sobre algo antes de formar uma opinião ou decisão."),
    ("importar", "Trazer algo de fora, ou ter valor/relevância para alguém."),
    ("legar", "Deixar algo para quem vem depois."),
    ("reaproveitar", "Usar de novo algo que já existia, em vez de descartar."),
    ("esconder", "Colocar algo fora de vista, para que não seja encontrado."),
    # Quadragésimo segundo lote do corpus amplo (modo rápido).
    ("completar", "Tornar algo inteiro, acrescentando o que faltava."),
    ("informar", "Dar conhecimento de algo a alguém."),
    ("delimitar", "Marcar os limites exatos de algo."),
    ("implicar", "Ter como consequência necessária, ou envolver algo noutra coisa."),
    # Achado real ao investigar candidatos de alta frequência: todos
    # regulares, verificados antes de entrar (nenhum "-air"/"-erir"/
    # "-uir" escondido).
    ("entrar", "Passar para dentro de um lugar ou situação."),
    ("gerar", "Fazer existir algo a partir de um processo ou regra."),
    ("ocupar", "Preencher um espaço, lugar ou posição."),
    ("voltar", "Retornar a um lugar, estado ou ponto anterior."),
    ("ampliar", "Tornar maior em tamanho, alcance ou importância."),
    ("bastar", "Ser suficiente para um propósito."),
    ("esperar", "Aguardar que algo aconteça, ou ter expectativa sobre algo."),
    ("provar", "Demonstrar a verdade de algo através de evidência ou raciocínio."),
    ("chover", "Cair água da atmosfera em forma de gotas."),
    ("incluir", "Fazer com que algo passe a fazer parte de um conjunto."),
    # "seguir" verificado com cuidado antes de entrar: precisa da troca
    # empilhada "e"->"i" + "gu"->"g" -- ver `_VERBOS_EGUIR_ALTERNANCIA`.
    ("seguir", "Ir atrás de algo ou alguém, ou continuar um caminho já iniciado."),
    # Achado real registado em conversa.md: "sair"/"cair" ("-air"
    # vocálico) ficaram de fora até `_verbo()` ganhar `_corrigir_acento_air`/
    # `_corrigir_subjuntivo_air`/`_corrigir_presente_air` (ver essas três
    # funções) -- paradigma inteiro conferido à mão (37 formas cada, sem
    # colisão) antes de entrar.
    ("sair", "Deixar de estar dentro de um lugar, passando para fora dele."),
    ("cair", "Ir de cima para baixo por ação da gravidade, perdendo o apoio ou equilíbrio."),
    ("conhecer", "Ter contacto ou saber sobre algo ou alguém através da experiência."),
    ("rodar", "Girar em torno de um eixo, ou executar um programa/processo."),
    ("correr", "Mover-se rapidamente usando as pernas, ou decorrer no tempo."),
    ("encontrar", "Achar algo ou alguém, ou coincidir num mesmo ponto."),
    ("agrupar", "Reunir elementos numa mesma categoria ou conjunto."),
    ("admitir", "Aceitar como verdadeiro ou permitido, ou deixar entrar."),
    ("rejeitar", "Recusar aceitar algo ou alguém."),
    # Quadragésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    # Todos verificados regulares antes de entrar (nenhum "-air"/"-erir"/
    # "-uir"/"-guir"/"-cer"/"-cir"/"-zir" escondido); "pedir" já tem
    # alternância conhecida e tratada em `_VERBOS_DIR_COM_ALTERNANCIA`.
    ("cantar", "Produzir sons melódicos com a voz, seguindo uma melodia."),
    ("isolar", "Separar algo ou alguém do resto, deixando-o à parte."),
    ("pedir", "Solicitar que alguém dê ou faça algo."),
    ("assumir", "Tomar para si uma responsabilidade, posição ou compromisso."),
    ("limitar", "Estabelecer um limite para algo, restringindo a sua extensão."),
    ("quebrar", "Partir algo em pedaços por aplicação de força."),
    ("coincidir", "Acontecer ao mesmo tempo que outra coisa, ou ser exatamente igual a ela."),
    ("combinar", "Juntar duas ou mais coisas de forma organizada, ou chegar a um acordo."),
    ("evitar", "Agir de modo a que algo não aconteça."),
    ("expandir", "Tornar maior em tamanho, alcance ou volume."),
    ("determinar", "Estabelecer com precisão o que algo é ou deve ser."),
    ("planejar", "Organizar antecipadamente as etapas necessárias para atingir um objetivo."),
    # Achado real: "falar" já existia em `lexico_base.json`, mas só com
    # presente (5 formas) -- verbo regular, sem irregularidade nenhuma,
    # trazido pra cá pra ganhar o paradigma completo.
    ("falar", "Comunicar por meio da voz ou de palavras."),
    ("faltar", "Não estar presente quando esperado, ou ser insuficiente."),
    ("certificar", "Confirmar formalmente que algo é verdadeiro ou cumpre um requisito."),
    # Quadragésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    # Todos verificados regulares antes de entrar; "inserir" já tem
    # alternância conhecida ("-erir") e "concluir"/"distribuir" já são
    # "-uir" vocálico não-"struir" -- os dois já cobertos pelas correções
    # existentes. Deliberadamente fora desta leva: "renomear" ("-ear" tem
    # irregularidade própria -- "renomeio", não "renomeo" -- ainda sem
    # correção nenhuma) e "restringir"/"caber" (alternância "g"->"j" e
    # irregularidade fechada, respetivamente, nenhuma tratada ainda).
    ("realizar", "Tornar real algo que estava apenas planeado ou imaginado."),
    ("vender", "Trocar algo que se possui por dinheiro."),
    ("arrastar", "Puxar algo pelo chão, movendo-o sem o levantar."),
    ("chamar", "Dizer o nome de alguém para lhe pedir atenção, ou dar um nome a algo."),
    ("andar", "Mover-se de um lugar para outro dando passos."),
    ("adaptar", "Ajustar algo a uma nova condição ou necessidade."),
    ("adivinhar", "Descobrir algo sem ter informação direta, por intuição ou dedução."),
    ("trabalhar", "Realizar uma atividade com esforço, geralmente em troca de sustento."),
    ("envolver", "Rodear algo por todos os lados, ou fazer parte ativa de uma situação."),
    ("executar", "Pôr em prática uma ação, ordem ou plano."),
    ("soar", "Produzir ou fazer ouvir um som."),
    ("inserir", "Colocar algo dentro de outra coisa, incluindo-o nela."),
    ("concluir", "Chegar ao fim de algo, ou tirar uma conclusão a partir de premissas."),
    ("distribuir", "Repartir algo entre várias partes ou pessoas."),
    # Quadragésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    ("trocar", "Substituir algo por outra coisa, ou dar e receber mutuamente."),
    ("avaliar", "Determinar o valor, a qualidade ou o estado de algo."),
    ("detectar", "Perceber ou identificar a presença de algo."),
    ("ordenar", "Colocar em ordem, ou dar uma instrução para que algo seja feito."),
    ("achar", "Encontrar algo, ou ter uma opinião sobre algo."),
    ("acompanhar", "Ir junto com alguém, ou seguir de perto a evolução de algo."),
    ("comunicar", "Transmitir uma informação a alguém."),
    ("copiar", "Reproduzir algo de forma igual ao original."),
    ("indicar", "Apontar ou mostrar algo, sugerindo um caminho ou escolha."),
    ("narrar", "Contar um acontecimento, real ou imaginado."),
    ("perceber", "Captar algo através dos sentidos ou da razão."),
    ("posicionar", "Colocar algo ou alguém numa posição determinada."),
    ("preparar", "Organizar previamente o que é necessário para algo acontecer."),
    ("procurar", "Fazer um esforço para encontrar algo."),
    ("eliminar", "Fazer desaparecer algo, retirando-o por completo."),
    ("examinar", "Observar algo com atenção para o avaliar ou entender."),
    ("levantar", "Erguer algo do chão ou de uma posição mais baixa."),
    ("carregar", "Transportar algo, geralmente com peso, ou fornecer energia a algo."),
    # Quadragésimo oitavo lote do corpus amplo (modo massa, meta 50.000).
    ("checar", "Verificar se algo está correto ou conforme o esperado."),
    ("diferenciar", "Estabelecer ou reconhecer a diferença entre duas ou mais coisas."),
    ("duplicar", "Tornar algo o dobro do que era, ou criar uma cópia exata de algo."),
    ("remover", "Retirar algo do lugar onde estava."),
    ("misturar", "Juntar duas ou mais substâncias ou elementos, combinando-os."),
    # Quinquagésimo lote do corpus amplo (modo massa, meta 50.000). "-çar"
    # e "-ear" verificados: "recomeçar"/"mapear" testados à mão contra as
    # correções `_corrigir_car_com_cedilha`/`_corrigir_ear_alternancia`
    # antes de entrar.
    ("recomeçar", "Começar de novo algo que tinha sido interrompido."),
    ("mapear", "Representar de forma organizada a estrutura ou disposição de algo."),
    ("aprofundar", "Tornar mais profundo o estudo ou o conhecimento sobre algo."),
    ("antecipar", "Fazer ou prever algo antes do tempo esperado."),
    ("aumentar", "Tornar maior em quantidade, tamanho ou intensidade."),
    ("caracterizar", "Descrever as características próprias de algo, distinguindo-o do resto."),
    ("colocar", "Pôr algo num determinado lugar."),
    ("exprimir", "Manifestar por palavras, gestos ou sinais aquilo que se sente ou pensa."),
    ("incorporar", "Juntar algo a um todo, passando a fazer parte dele."),
    # Quinquagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    ("arriscar", "Expor algo ou alguém a um perigo ou possível perda, na esperança de um ganho."),
    ("exercer", "Praticar uma atividade, função ou influência."),
    ("especializar", "Concentrar-se ou tornar específico num domínio restrito."),
    ("imitar", "Reproduzir o comportamento, a forma ou o som de algo ou alguém."),
    # Quinquagésimo segundo lote do corpus amplo (modo massa, meta
    # 50.000). Achado real: "-ger"/"-gir" (dirigir, fingir, exigir, eleger)
    # trocavam "g" por nada nenhuma vez -- 1ª singular do presente e todo
    # o subjuntivo geravam "dirigo"/"dirigamos" em vez de "dirijo"/
    # "dirijamos". Nova função `_corrigir_ger_gir_alternancia` (g->j antes
    # de "a"/"o", mesmo gatilho de c->ç), verificada à mão contra
    # "dirigir"/"fingir"/"eleger" antes de entrar -- "fingir"/"exigir" já
    # estavam no léxico e ganharam a forma certa retroativamente, sem
    # precisar tocar nas suas entradas.
    ("dirigir", "Conduzir um veículo, ou orientar e comandar uma atividade ou pessoas."),
    ("divergir", "Seguir direções diferentes a partir de um ponto comum, ou discordar de algo."),
    ("surgir", "Aparecer de forma repentina ou passar a existir."),
    ("proteger", "Defender algo ou alguém de um perigo ou dano."),
    # Achado real: "calcular" já existia em `lexico_base.json`, mas só
    # com presente (5 formas) -- verbo regular, trazido pra cá pra ganhar
    # o paradigma completo.
    ("calcular", "Determinar um valor através de operações matemáticas."),
    # Quinquagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    ("adotar", "Passar a ter ou seguir algo como próprio, ou assumir a criação de alguém."),
    ("corresponder", "Estar de acordo ou em equivalência com algo, ou responder a uma comunicação."),
    ("parecer", "Dar a impressão de ser, sem se ter certeza plena."),
    ("perder", "Deixar de ter algo que se possuía, ou não conseguir vencer."),
    ("virar", "Mudar de direção, posição ou estado."),
    ("iniciar", "Dar começo a algo."),
    # Quinquagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    ("beber", "Ingerir um líquido."),
    ("comprar", "Adquirir algo em troca de dinheiro."),
    ("criticar", "Avaliar algo apontando os seus defeitos ou qualidades."),
    ("deduzir", "Chegar a uma conclusão a partir de premissas, ou subtrair uma quantia de um total."),
    ("avançar", "Mover-se para a frente, ou progredir numa direção."),
    ("documentar", "Registar informação de forma organizada, ou comprovar algo com documentos."),
    ("atacar", "Agir de forma agressiva contra algo ou alguém."),
    # Achado real (auditoria de paradigma, não vocabulário novo): estes 7
    # já existiam em `lexico_base.json` com "presente" só, de antes de
    # `_verbo()` existir -- "comi"/"comeu"/"comia"/"comendo" etc. não
    # existiam no dicionário vivo, só "come". Mesmo resgate já feito pra
    # "recriar"/"multiplicar"/"dividir"/"calcular", confirmado rodando
    # (`d.buscar("comi")` devolvia vazio antes desta linha).
    ("comer", "Ingerir alimento."),
    ("pensar", "Formar ideias na mente; refletir."),
    ("gostar", "Sentir agrado ou preferência por algo."),
    ("ajudar", "Prestar auxílio a alguém."),
    ("resolver", "Encontrar a solução de um problema ou exercício."),
    ("contar", "Enumerar unidades para determinar uma quantidade."),
    ("somar", "Juntar quantidades para obter um total."),
    # Quinquagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    # "restringir"/"bloquear" testados à mão contra `_corrigir_ger_gir_
    # alternancia`/`_corrigir_ear_alternancia` antes de entrar.
    ("restringir", "Limitar o alcance ou a extensão de algo."),
    ("bloquear", "Impedir a passagem ou o funcionamento de algo."),
    # Verbos com particípio irregular único, ver `_PARTICIPIOS_IRREGULARES`
    # (registado em conversa.md, conferido contra oráculo hunspell antes
    # de entrar: nenhuma forma regular em "-ado"/"-ido" é palavra real).
    ("pagar", "Entregar valor devido em troca de algo."),
    ("entregar", "Fazer chegar algo às mãos de outra pessoa."),
    ("morrer", "Deixar de estar vivo."),
    ("gastar", "Usar ou consumir um recurso, sobretudo dinheiro ou tempo."),
    ("prender", "Segurar algo no lugar, ou privar alguém de liberdade."),
    ("suspender", "Interromper temporariamente algo, ou pendurar no ar."),
    ("bater", "Dar pancadas repetidas em algo, ou colidir com força."),
    # Quinquagésimo sétimo lote do corpus amplo (modo massa, meta 50.000).
    # "sugerir" já é "-erir" conhecido (`_VERBOS_ERIR_COM_ALTERNANCIA_E_I`);
    # "redigir"/"reforçar" testados à mão contra "-gir"/"-çar" antes de
    # entrar.
    ("refletir", "Pensar cuidadosamente sobre algo, ou devolver luz/imagem numa superfície."),
    ("sugerir", "Propor uma ideia a alguém, de forma indireta."),
    ("redigir", "Escrever um texto de forma organizada."),
    ("buscar", "Ir à procura de algo, tentando encontrá-lo."),
    ("recuperar", "Voltar a ter algo que se tinha perdido."),
    ("reforçar", "Tornar algo mais forte ou mais resistente."),
    # Quinquagésimo nono lote do corpus amplo (modo massa, meta 50.000).
    # "agir" testado à mão contra `_corrigir_ger_gir_alternancia` (raiz
    # curta "ag", ajo/ages/age/agimos/agem, confirmado sem regressão).
    ("justificar", "Apresentar uma razão que explica ou defende algo."),
    ("olhar", "Dirigir a vista para algo ou alguém."),
    ("mover", "Fazer com que algo mude de posição."),
    ("tentar", "Fazer um esforço para conseguir algo, sem garantia de êxito."),
    ("tirar", "Retirar algo de um lugar, ou obter algo a partir de outra coisa."),
    ("agir", "Praticar uma ação; comportar-se de determinada forma."),
    ("derivar", "Obter uma expressão a partir de outra por regras, ou vir a partir de uma origem."),
    ("estabilizar", "Tornar algo firme e constante, sem variação."),
    ("parar", "Deixar de se mover ou de continuar uma ação."),
    # Sexagésimo lote do corpus amplo (modo massa, meta 50.000).
    ("desenvolver", "Fazer crescer ou evoluir algo, tornando-o mais completo."),
    ("desejar", "Ter vontade de obter ou alcançar algo."),
    ("cortar", "Dividir algo em partes usando um instrumento afiado."),
    ("clarificar", "Tornar algo mais claro ou compreensível."),
    ("caminhar", "Andar a pé de um lugar para outro."),
    ("atualizar", "Tornar algo conforme o estado mais recente."),
    ("atuar", "Agir sobre algo, ou desempenhar um papel."),
    ("bancar", "Assumir o custo ou a responsabilidade de algo, ou desempenhar um papel de forma deliberada."),
    # Sexagésimo primeiro lote do corpus amplo (modo massa, meta 50.000).
    # "gerir" já é "-erir" conhecido (`_VERBOS_ERIR_COM_ALTERNANCIA_E_I`),
    # testado à mão (giro/geres/gere/gerimos/gerem) antes de entrar.
    ("gerir", "Administrar recursos, processos ou uma organização."),
    ("girar", "Mover-se em torno de um eixo ou ponto central."),
    ("guardar", "Colocar algo num lugar seguro para o conservar, ou manter na memória."),
    ("hesitar", "Ficar indeciso antes de agir ou decidir."),
    ("fundir", "Transformar em líquido pelo calor, ou juntar duas ou mais coisas numa só."),
    ("digitar", "Introduzir texto por meio de um teclado."),
    ("explicitar", "Tornar algo explícito, dizendo-o de forma clara e direta."),
    ("fabricar", "Produzir algo, geralmente em série, a partir de matéria-prima."),
    ("formular", "Expressar algo de forma precisa e organizada, ou criar uma fórmula."),
    ("estender", "Alongar algo no espaço ou no tempo, tornando-o mais extenso."),
    ("registar", "Anotar ou gravar algo formalmente para consulta futura."),
    ("encaixar", "Ajustar uma peça ou elemento dentro de outro, de forma exata."),
    ("truncar", "Cortar uma parte de algo, encurtando-o antes do fim natural."),
    ("saltar", "Impulsionar o corpo para fora do chão, ou passar por cima de algo."),
    # Sexagésimo segundo lote do corpus amplo (modo massa, meta 50.000).
    # "obedecer" já é "-cer" conhecido (obedeço/obedece), testado à mão.
    ("mexer", "Fazer um movimento, ou tocar em algo alterando a sua posição."),
    ("morar", "Ter residência habitual num lugar."),
    ("nadar", "Deslocar-se na água movendo o corpo."),
    ("obedecer", "Cumprir uma ordem ou seguir uma regra imposta por outro."),
    ("processar", "Submeter algo a uma sequência de operações, ou mover uma ação judicial contra alguém."),
    ("qualificar", "Atribuir uma qualidade ou classificação a algo ou alguém."),
    ("questionar", "Colocar uma questão, pondo algo em dúvida."),
    ("recolher", "Juntar e retirar algo que estava disperso ou deixado num lugar."),
    ("recorrer", "Voltar a usar algo, ou pedir uma nova apreciação de uma decisão."),
    ("reformular", "Formular de novo, de forma diferente ou melhorada."),
    # Lote F (sessão contínua, corpus amplo, meta 50.000). "conseguir"
    # confirmado "-guir" conhecido (consigo/consegue/consiga), testado à
    # mão contra `_corrigir_guir` antes de entrar.
    ("evocar", "Trazer à memória ou à mente algo passado ou ausente."),
    ("inverter", "Trocar a ordem, o sentido ou a posição de algo pelo seu oposto."),
    ("sobrar", "Restar depois de usada ou retirada uma parte."),
    ("ajustar", "Adaptar algo para que fique na medida ou na posição certa."),
    ("participar", "Tomar parte em algo, ou dar a conhecer algo a alguém."),
    ("solicitar", "Pedir algo de forma formal."),
    ("acontecer", "Ocorrer ou suceder no tempo."),
    ("renomear", "Dar um novo nome a algo que já tinha um."),
    ("telefonar", "Comunicar por telefone."),
    ("sentar", "Colocar-se ou colocar alguém numa posição de assento."),
    ("vencer", "Ganhar uma disputa ou competição, ou chegar ao fim de um prazo."),
    ("conseguir", "Alcançar um objetivo através de esforço ou capacidade."),
    # Sexagésimo terceiro lote do corpus amplo (modo massa, meta 50.000).
    # "traduzir" já é "-zir" conhecido (traduz, não "traduze"); "alcançar"
    # testado à mão contra `_corrigir_car_com_cedilha` antes de entrar.
    ("traduzir", "Passar um texto ou uma fala de uma língua para outra."),
    ("arredondar", "Ajustar um valor para o número inteiro ou casa decimal mais próxima, ou dar forma redonda a algo."),
    ("atravessar", "Passar de um lado ao outro de algo."),
    ("avisar", "Dar conhecimento antecipado de algo a alguém."),
    ("captar", "Receber ou apreender algo, como um sinal, uma imagem ou uma ideia."),
    ("casar", "Unir-se a alguém em matrimónio, ou combinar bem com outra coisa."),
    ("alcançar", "Chegar a um ponto, objetivo ou nível pretendido."),
    # Lote F2 (sessão contínua, corpus amplo, meta 50.000). "diferir"
    # confirmado "-erir" conhecido (difiro/difira), testado à mão.
    ("diferir", "Ser diferente de outra coisa, ou adiar algo para depois."),
    ("costumar", "Ter por hábito fazer algo."),
    ("concentrar", "Reunir num só ponto, ou focar a atenção em algo."),
    ("argumentar", "Apresentar razões a favor ou contra uma ideia."),
    ("decorar", "Memorizar algo repetindo-o, sem necessariamente compreender, ou embelezar um espaço."),
    ("levar", "Transportar algo de um lugar para outro, ou durar um certo tempo."),
    ("influenciar", "Produzir um efeito sobre o comportamento, a opinião ou o estado de algo ou alguém."),
    # Sexagésimo quarto lote do corpus amplo (modo massa, meta 50.000).
    # "descobrir" já é o-u conhecido (`_VERBOS_O_U_ALTERNANCIA`); "ferir"/
    # "emergir" já são "-erir"/"-gir" conhecidos, testados à mão.
    ("descobrir", "Encontrar ou perceber algo que antes era desconhecido."),
    ("editar", "Preparar um texto ou conteúdo para publicação, corrigindo e ajustando-o."),
    ("encolher", "Tornar-se ou tornar algo mais pequeno."),
    ("enumerar", "Mencionar um a um os elementos de um conjunto."),
    ("estruturar", "Organizar algo segundo uma estrutura definida."),
    ("falsificar", "Fazer uma cópia ou versão fraudulenta de algo, fazendo-a passar por verdadeira."),
    ("fatorar", "Decompor um número ou expressão num produto de fatores."),
    ("filtrar", "Separar elementos de uma mistura ou conjunto segundo um critério."),
    ("focar", "Dirigir a atenção ou o esforço para um ponto específico."),
    ("ferir", "Causar uma lesão física, ou magoar emocionalmente."),
    ("emergir", "Sair de dentro de um meio para a superfície, ou surgir de forma gradual."),
    # Sexagésimo quinto lote do corpus amplo (modo massa, meta 50.000).
    # "obter"/"reabrir" ficam de fora por ora: "obter" é composto
    # irregular de "ter" (obtenho, não "obto"); "reabrir" herdaria o
    # particípio irregular de "abrir" ("reaberto"), ainda não registado.
    ("listar", "Organizar elementos numa lista."),
    ("navegar", "Deslocar-se por água usando uma embarcação, ou percorrer páginas e conteúdos digitais."),
    ("ocultar", "Esconder algo, impedindo que seja visto ou percebido."),
    ("operar", "Fazer funcionar algo, ou realizar uma intervenção cirúrgica."),
    ("otimizar", "Tornar algo o mais eficiente possível."),
    ("pegar", "Segurar algo com a mão, ou apanhar algo."),
    ("permutar", "Trocar a posição ou o lugar de elementos entre si."),
    ("propagar", "Difundir algo, fazendo-o chegar a um alcance cada vez maior."),
    ("redefinir", "Definir de novo, de forma diferente da anterior."),
    ("regenerar", "Fazer nascer de novo algo que se tinha degradado ou perdido."),
    ("reordenar", "Colocar de novo em ordem, segundo um novo critério."),
    ("ratificar", "Confirmar formalmente e tornar válido algo já acordado."),
    # Lote F3 (sessão contínua, corpus amplo, meta 50.000). "rastrear"/
    # "forçar" testados à mão contra `_corrigir_ear_alternancia`/
    # `_corrigir_car_com_cedilha` antes de entrar.
    ("rastrear", "Seguir o percurso ou a origem de algo, acompanhando os seus passos."),
    ("forçar", "Obrigar algo ou alguém a fazer ou a ceder, usando força ou pressão."),
    ("clicar", "Pressionar um botão do rato ou de um dispositivo para selecionar ou ativar algo."),
    ("consultar", "Procurar informação junto de uma fonte, ou pedir a opinião de alguém."),
    ("facilitar", "Tornar mais fácil algo que seria difícil."),
    ("falhar", "Não conseguir alcançar o resultado pretendido."),
    ("desenhar", "Representar uma forma através de linhas e traços."),
    ("limpar", "Retirar sujidade ou elementos indesejados de algo."),
    ("migrar", "Mudar de um lugar, sistema ou estado para outro."),
    ("ignorar", "Não dar atenção a algo, propositadamente ou por desconhecimento."),
    ("prometer", "Comprometer-se a cumprir algo no futuro."),
    ("desistir", "Deixar de continuar uma ação ou tentativa."),
    ("sincronizar", "Fazer com que duas ou mais coisas ocorram ou fiquem coerentes ao mesmo tempo."),
    # Sexagésimo sexto lote do corpus amplo (modo massa, meta 50.000).
    ("tapar", "Cobrir algo, impedindo o acesso ou a passagem."),
    ("tomar", "Segurar ou apoderar-se de algo, ou ingerir um alimento ou bebida."),
    ("transmitir", "Fazer passar algo de um lugar, pessoa ou meio para outro."),
    ("transportar", "Levar algo ou alguém de um lugar para outro."),
    ("treinar", "Praticar repetidamente uma atividade para melhorar o desempenho."),
    ("ultrapassar", "Passar à frente de algo ou alguém, ou exceder um limite."),
    ("viver", "Estar vivo, ou passar a vida de determinada forma."),
    ("visitar", "Ir a um lugar ou a alguém por um período limitado."),
    # "obter" foi resolvido em `lexico_base.json` (composto irregular de
    # "ter", não passa por `_verbo()`). "reabrir" entra aqui com o
    # particípio irregular já registado em `_PARTICIPIOS_IRREGULARES`
    # ("reaberto").
    ("reabrir", "Abrir de novo algo que estava fechado."),
    # Achado real: o comentário perto de "recriar"/"generalizar" (acima)
    # excluía "subtrair" por ser "-air" e a regra genérica de "-ir" gerar
    # forma errada -- verdade QUANDO foi escrito, mas `_corrigir_acento_air`
    # já existe e já está testado em "sair"/"cair" (ver achado logo abaixo).
    # Conferido à mão antes de entrar: `_verbo("subtrair", ...)` gera
    # subtraio/subtrais/subtrai/subtraímos/subtraem, subtraí/subtraiu/
    # subtraímos/subtraíram, subtraindo, subtraído -- mesmo padrão de
    # "sair"/"cair", nenhuma forma fabricada errada. Termo central deste
    # projeto (matemática) que só tinha o infinitivo até agora.
    ("subtrair", "Retirar uma quantidade de outra quando isso é controlado."),
    # Sexagésimo sétimo lote do corpus amplo (modo massa, aceleração de vocabulário).
    ("articular", "Unir partes de forma flexível ou pronunciar com clareza."),
    ("assegurar", "Dar certeza ou garantir algo."),
    ("assimilar", "Absorver e compreender nova informação."),
    ("caracterizar", "Descrever os traços distintivos de algo."),
    ("categorizar", "Classificar em categorias definidas."),
    ("comprovar", "Demonstrar a verdade de algo por provas."),
    ("coordenar", "Organizar elementos para atuarem em harmonia."),
    ("diferenciar", "Distinguir diferenças entre coisas ou conceitos."),
    ("documentar", "Registrar em documentos a evidência de algo."),
    ("equacionar", "Formular um problema sob a forma de equação."),
    ("esclarecer", "Tornar claro ou compreensível um assunto."),
    ("especificar", "Indicar com precisão os detalhes de algo."),
    ("estabelecer", "Fixar, instituir ou determinar uma regra ou princípio."),
    ("formular", "Expressar algo de modo estruturado ou rigoroso."),
    ("fortalecer", "Tornar forte ou mais resistente."),
    ("fundamentar", "Basear um argumento em razões ou princípios sólidos."),
    ("ilustrar", "Esclarecer algo por meio de exemplos ou imagens."),
    ("incorporar", "Incluir ou integrar num todo já existente."),
    ("inspecionar", "Examinar atentamente para verificar a conformidade."),
    ("inventariar", "Fazer um levantamento detalhado de itens ou conceitos."),
    ("justificar", "Apresentar razões válidas para defender uma posição."),
    ("manifestar", "Tornar público ou visível um pensamento ou estado."),
    ("materializar", "Dar forma concreta a uma ideia ou conceito."),
    ("modelar", "Criar uma representação simplificada de um fenômeno."),
    ("normalizar", "Tornar conforme uma norma ou padrão prévio."),
    ("objetivar", "Definir com clareza um objetivo ou meta."),
    ("padronizar", "Uniformizar procedimentos ou representações."),
    ("ponderar", "Examinar com cuidado os prós e contras de algo."),
    ("preservar", "Manter intacto sem perda ou alteração."),
    ("processar", "Submeter dados a uma sequência de transformações."),
    ("questionar", "Colocar em dúvida ou pedir esclarecimentos sobre algo."),
    ("raciocinar", "Usar a razão para deduzir ou inferir conclusões."),
    ("refinar", "Aprimorar detalhes para tornar algo mais preciso."),
    ("reformular", "Formular de novo com correções ou ajustes."),
    ("relacionar", "Estabelecer ligação lógica entre dois ou mais elementos."),
    ("resumir", "Sintetizar as ideias principais de um conteúdo."),
    ("sintetizar", "Combinar elementos para formar um todo coerente."),
    ("sumarizar", "Apresentar em um resumo conciso."),
    ("sustentar", "Manter ou defender uma tese com argumentos."),
    ("valorizar", "Atribuir valor ou reconhecer a importância de algo."),
    ("visualizar", "Formar uma representação visual de um conceito."),
    # Sexagésimo oitavo lote do corpus amplo (modo massa, expansão de verbos regulares -ar).
    ("abrigar", "Dar ou receber abrigo, proteção ou refúgio."),
    ("acelerar", "Aumentar a velocidade ou a rapidez de algo."),
    ("acumular", "Juntar ou reunir coisas em quantidade ao longo do tempo."),
    ("admirar", "Olhar ou contemplar com apreço, respeito ou espanto."),
    ("afetar", "Causar efeito ou impacto sobre algo ou alguém."),
    ("armar", "Equipar com armas, ou montar uma estrutura ou mecanismo."),
    ("armazenar", "Guardar ou conservar algo num local próprio para uso futuro."),
    ("assinar", "Escrever o próprio nome em documento, ou subscrever algo."),
    ("conectar", "Ligar ou interligar partes ou sistemas entre si."),
    ("demonstrar", "Mostrar claramente a verdade de algo por provas ou razões."),
    ("denominar", "Dar um nome ou título a algo ou alguém."),
    ("destacar", "Dar relevo ou importância a algo, tornando-o bem visível."),
    ("divulgar", "Tornar público ou amplamente conhecido."),
    ("dominar", "Exercer controlo ou ter conhecimento profundo sobre algo."),
    ("elevar", "Mover para uma posição mais alta, ou aumentar o nível de algo."),
    ("enfrentar", "Fazer frente a um desafio, problema ou perigo."),
    ("alimentar", "Fornecer alimento ou sustento a algo ou alguém."),
    ("alugar", "Ceder ou tomar o uso de um bem mediante pagamento."),
    ("ameaçar", "Manifestar intenção de fazer mal ou causar dano."),
    ("anotar", "Registrar por escrito uma nota ou lembrete."),
    ("anular", "Tornar nulo ou sem efeito um ato ou decisão."),
    ("aproveitar", "Utilizar algo de maneira proveitosa ou frutuosa."),
    ("arrancar", "Tirar ou puxar com força de um lugar."),
    ("arrecadar", "Recolher ou juntar valores ou fundos."),
    ("arrendar", "Ceder o uso de um imóvel ou terreno mediante aluguel."),
    ("atrapalhar", "Causar embaraço ou perturbação no andamento de algo."),
    ("atrasar", "Fazer demorar ou chegar depois do horário previsto."),
    ("ausentar", "Afastar-se ou retirar-se de um determinado local."),
    ("auxiliar", "Prestar ajuda ou colaboração a alguém."),
    ("balançar", "Mover-se alternadamente de um lado para o outro."),
    ("camuflar", "Disfarçar ou esconder algo na paisagem ou ambiente."),
    ("cancelar", "Interromper ou anular a validade de um compromisso ou ato."),
    ("capturar", "Prender ou tomar a posse de algo ou alguém."),
    ("colaborar", "Trabalhar em conjunto com outros para um fim comum."),
    ("compensar", "Dar uma contrapartida equilibrada por uma perda ou esforço."),
    ("complicar", "Tornar difícil ou complexo o entendimento de algo."),
    ("comportar", "Portar-se de determinada maneira ou ter capacidade para conter."),
    ("conciliar", "Harmonizar ou pôr em acordo partes ou ideias distintas."),
    ("condenar", "Declarar culpado ou impor uma pena a alguém."),
    ("congelar", "Passar ao estado sólido por efeito do frio intenso."),
    # Lote de 30 verbos regulares terminados em -er e -ir.
    ("ceder", "Dar ou transferir algo a outrem, ou deixar de resistir."),
    ("combater", "Lutar contra algo ou alguém, buscando vencer ou conter."),
    ("conceder", "Dar, permitir ou outorgar algo a alguém."),
    ("contender", "Disputar ou competir com alguém por uma razão ou objetivo."),
    ("defender", "Proteger contra ataque, perigo ou acusação."),
    ("eleger", "Escolher alguém por votação ou preferência."),
    ("pretender", "Tencionar ou ter como intenção alcançar algo."),
    ("proceder", "Agir de determinada maneira, ou ter fundamento."),
    ("promover", "Impulsionar ou favorecer o desenvolvimento de algo."),
    ("atingir", "Alcançar um ponto, meta ou objetivo."),
    ("conduzir", "Guiar, dirigir ou levar algo ou alguém a um destino."),
    ("consistir", "Ter como base, matéria ou essência fundamental."),
    ("insistir", "Manter-se firme numa opinião, pedido ou intenção."),
    ("resistir", "Opor força contrária ou suportar a ação de algo."),
    ("persistir", "Continuar com determinação num propósito ou estado."),
    ("assistir", "Estar presente para ver ou prestar ajuda a alguém."),
    ("discutir", "Debater um assunto apresentando razões ou opiniões."),
    ("cumprir", "Executar uma obrigação, promessa ou tarefa."),
    ("suprir", "Fornecer o que falta para completar algo."),
    ("punir", "Aplicar uma pena ou castigo a quem cometeu uma falta."),
    ("consumir", "Usar ou gastar um recurso até ao fim."),
    ("exibir", "Mostrar publicamente algo com orgulho ou destaque."),
    ("inibir", "Dificultar ou impedir a manifestação de uma ação ou comportamento."),
    ("emitir", "Enviar, lançar ou expressar um sinal, som ou documento."),
    ("omitir", "Deixar de dizer, incluir ou fazer algo."),
    ("comprometer", "Assumir uma obrigação formal ou colocar algo em risco."),
    ("submeter", "Apresentar algo à apreciação ou sujeitar-se a uma autoridade."),
    ("remeter", "Enviar algo para um destinatário ou referir-se a outro ponto."),
    ("atender", "Prestar atenção a alguém ou satisfazer um pedido."),
    ("ofender", "Causar dano moral ou desrespeitar alguém."),
    # Lote de 25 verbos regulares terminados em -er.
    ("acolher", "Receber ou dar abrigo a alguém com atenção ou afeto."),
    ("acometer", "Atacar, investir com ímpeto ou ser acometido por algo."),
    ("anteceder", "Ocorrer ou vir antes de algo no tempo ou na ordem."),
    ("aquecer", "Tornar ou ficar quente ou mais aquecido."),
    ("absorver", "Aspirar, beber ou incorporar uma substância ou informação."),
    ("carecer", "Ter falta de algo ou necessitar de alguma coisa."),
    ("decorrer", "Passar o tempo ou suceder como consequência."),
    ("dissolver", "Fazer passar um sólido a líquido ou desfazer uma união."),
    ("incorrer", "Cair em falta, erro, pena ou responsabilidade."),
    ("interromper", "Cessar ou suspender temporariamente uma ação ou processo."),
    ("merecer", "Ser digno de receber algo por suas qualidades ou ações."),
    ("morder", "Pressionar ou cortar com os dentes."),
    ("percorrer", "Atravessar ou andar ao longo de uma extensão."),
    ("abastecer", "Fornecer o necessário para o funcionamento ou consumo."),
    ("acender", "Fazer começar a arder ou ligar uma fonte de luz."),
    ("agradecer", "Manifestar gratidão por um benefício recebido."),
    ("arrefecer", "Tornar-se ou fazer ficar frio ou menos quente."),
    ("concorrer", "Competir com outros por um objetivo ou disputar algo."),
    ("convencer", "Levar alguém a aceitar ou reconhecer uma verdade."),
    ("converter", "Transformar algo ou alguém de um estado ou crença para outro."),
    ("descer", "Mover-se de um ponto mais alto para um mais baixo."),
    ("emagrecer", "Perder peso corporal ou tornar-se mais magro."),
    ("enlouquecer", "Tornar-se ou fazer alguém ficar louco."),
    ("enriquecer", "Tornar-se ou fazer ficar rico, ou tornar mais abundante."),
    ("esquecer", "Deixar de ter na memória ou perder de vista uma lembrança."),
)




_PALAVRAS_INVARIAVEIS_EM_COMPOSTO = frozenset({
    "de", "em", "por", "com", "para", "entre", "sem", "sob", "sobre",
    "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "e", "ou", "a", "o", "os", "as", "ao", "à",
    "não", "mais", "menos", "só", "apenas",
})


def _plural_de_conceito_e_seguro(nome: str) -> bool:
    """Achado real ao investigar candidatos de alta frequência ("leituras",
    "critérios", "eventos"): os 1141 conceitos de `conhecimento_puro.py`
    que não têm entrada manual em `_NOMES` nunca ganhavam plural nenhum --
    só a forma singular era registada (nem "-s" simples). Gerar o plural
    em massa é seguro aqui porque a regra (`_plural_substantivo`/
    `_plural_composto`) já é a mesma testada em toda a `_forma_nome` --
    não é palavra nova, é a MESMA palavra ganhando a forma que já faltava.

    Ressalva real, encontrada medindo antes de aplicar às cegas: nomes
    compostos com preposição/artigo ("adjunto adverbial de tempo") ou com
    "não" ("símbolo não alfabético") ou com sigla/nome próprio em
    maiúscula ("reconstrução linguística PSF") NÃO seguem o padrão
    "substantivo + adjetivo(s)" que `_plural_composto` sabe tratar --
    aplicar geraria "des tempos"/"nãos alfabéticos"/"PSFs", que não
    existem. Ficam de fora, sem plural gerado, em vez de arriscar forma
    fabricada errada."""
    if nome.endswith("s"):
        return False
    if " " not in nome:
        return True
    for modificador in nome.split(" ")[1:]:
        if modificador in _PALAVRAS_INVARIAVEIS_EM_COMPOSTO:
            return False
        if not modificador.isalpha() or not modificador.islower():
            return False
    return True


def entradas_expandidas() -> tuple[EntradaLexical, ...]:
    entradas: list[EntradaLexical] = []
    lemas_manuais: set[str] = set()
    for lema, genero, definicao in _NOMES:
        lemas_manuais.add(lema.casefold())
        entradas.extend(_forma_nome(lema, genero, definicao))
    for lema, definicao in _ADJETIVOS:
        entradas.extend(_forma_adj(lema, definicao))
    for infinitivo, definicao in _VERBOS:
        entradas.extend(_verbo(infinitivo, definicao))
    entradas.extend(_PALAVRAS_FUNCIONAIS)

    # Todo conceito puro precisa ser consultável no léxico interno. Conceitos já
    # materializados manualmente não são duplicados; os demais entram como
    # substantivos técnicos, sem género inventado e sem dependência externa.
    conceitos_por_nome = {conceito.nome.casefold(): conceito for conceito in CONCEITOS_PORTUGUES_PURO}
    for conceito in CONCEITOS_PORTUGUES_PURO:
        if conceito.nome.casefold() in lemas_manuais:
            continue
        atributos_conceito = {"tema_consulta_psf": conceito.tema_consulta, "ordem_psf": conceito.ordem, "camada_psf": conceito.camada}
        entradas.append(
            EntradaLexical(
                lema=conceito.nome,
                forma=conceito.nome,
                classe=ClasseGramatical.SUBSTANTIVO,
                definicoes=(conceito.construcao,),
                atributos=atributos_conceito,
            )
        )
        if _plural_de_conceito_e_seguro(conceito.nome):
            plural = _plural_composto(conceito.nome) if " " in conceito.nome else _plural_substantivo(conceito.nome)
            entradas.append(
                EntradaLexical(
                    lema=conceito.nome,
                    forma=plural,
                    classe=ClasseGramatical.SUBSTANTIVO,
                    definicoes=(conceito.construcao,),
                    numero=Numero.PLURAL,
                    atributos=atributos_conceito,
                )
            )

    # Termos equivalentes são formas de acesso, não conceitos duplicados.
    for alias, alvo in ALIASES_CONCEITOS_PORTUGUES.items():
        conceito = conceitos_por_nome[alvo.casefold()]
        entradas.append(
            EntradaLexical(
                lema=alias,
                forma=alias,
                classe=ClasseGramatical.SUBSTANTIVO,
                definicoes=(f"Termo equivalente a {conceito.nome}: {conceito.construcao}",),
                atributos={"alias_psf": conceito.nome, "ordem_psf": conceito.ordem},
            )
        )
    return tuple(entradas)
