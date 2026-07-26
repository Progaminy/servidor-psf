"""Regras gramaticais pequenas, compostas e substituíveis."""
from __future__ import annotations

from typing import Protocol

from .tipos import (
    AnaliseToken,
    ClasseGramatical,
    Constituinte,
    Diagnostico,
    Genero,
    Numero,
    Pessoa,
)


class RegraGramatical(Protocol):
    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        ...


def _leitura_de_classe(analise: AnaliseToken, classe: ClasseGramatical):
    """Devolve a leitura da classe somente quando ela já foi selecionada.

    A desambiguação promove a leitura escolhida para ``principal``. As regras
    sintáticas não podem voltar a procurar uma classe nas alternativas, pois
    isso ressuscita leituras rejeitadas pelo contexto (por exemplo, ``casas``
    substantivo como forma do verbo ``casar``).
    """
    if not analise.leituras or analise.principal.classe != classe:
        return None
    return analise.principal


def _qualquer_leitura_de_classe(analise: AnaliseToken, classe: ClasseGramatical):
    """Busca uma alternativa sem a promover, para diagnosticar ambiguidade."""
    return next((leitura for leitura in analise.leituras if leitura.classe == classe), None)


def _leituras_da_classe_selecionada(
    analise: AnaliseToken, classe: ClasseGramatical
) -> tuple:
    """Conserva alternativas flexionais da mesma classe selecionada.

    Formas sincréticas como ``disse`` e ``quis`` possuem leituras verbais de
    1.ª e 3.ª pessoa. Consultá-las não reabre uma ambiguidade de classe: só
    permite escolher a flexão compatível da forma verbal já selecionada.
    """
    if _leitura_de_classe(analise, classe) is None:
        return ()
    return tuple(leitura for leitura in analise.leituras if leitura.classe == classe)


def _discordancias(esquerda, direita) -> list[str]:
    campos: list[str] = []
    if (
        esquerda.genero in {Genero.MASCULINO, Genero.FEMININO}
        and direita.genero in {Genero.MASCULINO, Genero.FEMININO}
        and esquerda.genero != direita.genero
    ):
        campos.append("género")
    if esquerda.numero is not None and direita.numero is not None and esquerda.numero != direita.numero:
        campos.append("número")
    return campos


class RegraConcordanciaDeterminanteNome:
    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        resultados: list[Diagnostico] = []
        for esquerda, direita in zip(analises, analises[1:]):
            det = _leitura_de_classe(esquerda, ClasseGramatical.DETERMINANTE)
            nome = _leitura_de_classe(direita, ClasseGramatical.SUBSTANTIVO)
            if det is None or nome is None:
                continue
            campos = _discordancias(det, nome)
            if campos:
                resultados.append(
                    Diagnostico(
                        codigo="CONCORDANCIA_DET_NOME",
                        mensagem=f"Possível discordância de {' e '.join(campos)} entre "
                        f"“{esquerda.token.texto}” e “{direita.token.texto}”.",
                        inicio=esquerda.token.inicio,
                        fim=direita.token.fim,
                        sugestao="Faça o determinante concordar com o substantivo.",
                    )
                )
        return tuple(resultados)


_PRONOMES_DE_TRATAMENTO = frozenset({"você", "vocês"})


def _discordancias_verbais(sujeito, verbo) -> list[str]:
    """Achado real ao investigar por que "você veio" (frase correta) disparava
    falso positivo de discordância: "você"/"vocês" são pronomes de
    TRATAMENTO -- referem-se à 2ª pessoa (quem ouve), mas a norma do
    português sempre flexiona o verbo na 3ª pessoa ("você veio", nunca
    "você vieste"). Não é exceção regional nem erro comum, é a única
    concordância gramaticalmente correta para este pronome -- por isso a
    pessoa do sujeito usada na comparação vira 3ª quando o núcleo é um
    destes pronomes, mesmo que o dado lexical registe pessoa=segunda
    (correto para outros usos, como geração de conjugação de "tu")."""
    campos: list[str] = []
    if sujeito.numero is not None and verbo.numero is not None and sujeito.numero != verbo.numero:
        campos.append("número")
    pessoa_sujeito = sujeito.pessoa
    if sujeito.lema in _PRONOMES_DE_TRATAMENTO:
        pessoa_sujeito = Pessoa.TERCEIRA
    if pessoa_sujeito is not None and verbo.pessoa is not None and pessoa_sujeito != verbo.pessoa:
        campos.append("pessoa")
    return campos


def _nucleo_do_sujeito(candidatos: list[AnaliseToken]):
    for item in candidatos:
        leitura = _leitura_de_classe(item, ClasseGramatical.SUBSTANTIVO)
        if leitura is None:
            leitura = _leitura_de_classe(item, ClasseGramatical.PRONOME)
        if leitura is not None:
            return leitura
    return None


def _sujeito_coordenado(candidatos: list[AnaliseToken]) -> bool:
    nominais = sum(
        1
        for item in candidatos
        if _leitura_de_classe(item, ClasseGramatical.SUBSTANTIVO) is not None
        or _leitura_de_classe(item, ClasseGramatical.PRONOME) is not None
    )
    return nominais >= 2 and any(item.token.normalizado == "e" for item in candidatos)


def _juntar_tokens(itens: list[AnaliseToken]) -> str:
    texto = ""
    for item in itens:
        atual = item.token.texto
        if not texto or atual == "-" or texto.endswith("-"):
            texto += atual
        else:
            texto += " " + atual
    return texto


class RegraConcordanciaVerboSujeito:
    """Concordância de número e pessoa entre o núcleo do sujeito e o verbo.

    Ao contrário de determinante/nome e nome/adjetivo, sujeito e verbo não
    são sempre adjacentes ("Os livros antigos chegou") -- por isso esta
    regra segmenta por frase e localiza os dois membros do par, em vez de
    comparar pares consecutivos.
    """

    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        resultados: list[Diagnostico] = []
        for segmento in _segmentos_frase(analises):
            indice_verbo = next(
                (
                    i
                    for i, analise in enumerate(segmento)
                    if _leitura_de_classe(analise, ClasseGramatical.VERBO) is not None
                ),
                None,
            )
            if indice_verbo is None:
                continue
            verbos = _leituras_da_classe_selecionada(
                segmento[indice_verbo], ClasseGramatical.VERBO
            )
            candidatos_sujeito = [
                item for item in segmento[:indice_verbo]
                if item.token.texto.strip() and item.token.texto not in ",;:"
            ]
            if not candidatos_sujeito:
                continue
            nucleo = _nucleo_do_sujeito(candidatos_sujeito)
            if nucleo is None:
                continue
            sujeito_coordenado = _sujeito_coordenado(candidatos_sujeito)
            discordancias_possiveis: list[list[str]] = []
            for verbo in verbos:
                campos_candidatos = _discordancias_verbais(nucleo, verbo)
                if sujeito_coordenado:
                    campos_candidatos = [
                        campo for campo in campos_candidatos if campo != "número"
                    ]
                    if verbo.numero == Numero.SINGULAR:
                        campos_candidatos.append("número")
                discordancias_possiveis.append(campos_candidatos)

            # Basta uma leitura flexional compatível da forma verbal. Quando
            # nenhuma serve, relata a alternativa que diverge em menos traços.
            campos = min(discordancias_possiveis, key=len, default=[])
            if campos:
                sujeito_texto = _juntar_tokens(candidatos_sujeito)
                resultados.append(
                    Diagnostico(
                        codigo="CONCORDANCIA_VERBO_SUJEITO",
                        mensagem=f"Possível discordância de {' e '.join(campos)} entre "
                        f"“{sujeito_texto}” e “{segmento[indice_verbo].token.texto}”.",
                        inicio=candidatos_sujeito[0].token.inicio,
                        fim=segmento[indice_verbo].token.fim,
                        sugestao="Faça o verbo concordar com o núcleo do sujeito.",
                    )
                )
        return tuple(resultados)


class RegraCategoriaIncompativel:
    """Sinaliza quando a leitura escolhida por padrão (`AnaliseToken.principal`,
    sempre `leituras[0]`, cega a contexto) esconde um verbo real: a frase
    parece não ter nenhum verbo olhando só a leitura principal de cada
    token, mas algum token tem leitura de verbo entre as alternativas não
    escolhidas. Fatia estreita e honesta da técnica 8 (BERT/homónimos em
    contexto) -- não resolve homónimos em geral, só este caso específico e
    verificável.
    """

    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        resultados: list[Diagnostico] = []
        for segmento in _segmentos_frase(analises):
            tem_verbo_principal = any(
                analise.leituras and analise.principal.classe == ClasseGramatical.VERBO
                for analise in segmento
            )
            if tem_verbo_principal:
                continue
            for analise in segmento:
                if not analise.leituras or analise.principal.classe == ClasseGramatical.VERBO:
                    continue
                leitura_verbo = _qualquer_leitura_de_classe(
                    analise, ClasseGramatical.VERBO
                )
                if leitura_verbo is None:
                    continue
                resultados.append(
                    Diagnostico(
                        codigo="CATEGORIA_INCOMPATIVEL",
                        mensagem=f"“{analise.token.texto}” foi lido como "
                        f"{analise.principal.classe.value}, mas também pode ser verbo -- "
                        "nenhum outro token da frase tem leitura de verbo.",
                        inicio=analise.token.inicio,
                        fim=analise.token.fim,
                        sugestao="Confira se esta palavra deveria ter sido lida como verbo.",
                    )
                )
        return tuple(resultados)


class RegraConcordanciaNomeAdjetivo:
    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        resultados: list[Diagnostico] = []
        for esquerda, direita in zip(analises, analises[1:]):
            nome = _leitura_de_classe(esquerda, ClasseGramatical.SUBSTANTIVO)
            adjetivo = _leitura_de_classe(direita, ClasseGramatical.ADJETIVO)
            if nome is None or adjetivo is None:
                continue
            campos = _discordancias(nome, adjetivo)
            if campos:
                resultados.append(
                    Diagnostico(
                        codigo="CONCORDANCIA_NOME_ADJ",
                        mensagem=f"Possível discordância de {' e '.join(campos)} entre "
                        f"“{esquerda.token.texto}” e “{direita.token.texto}”.",
                        inicio=esquerda.token.inicio,
                        fim=direita.token.fim,
                        sugestao="Faça o adjetivo concordar com o substantivo.",
                    )
                )
        return tuple(resultados)


class AnalisadorGramatical:
    def __init__(self, regras: tuple[RegraGramatical, ...] | None = None) -> None:
        self.regras = regras or (
            RegraConcordanciaDeterminanteNome(),
            RegraConcordanciaNomeAdjetivo(),
            RegraConcordanciaVerboSujeito(),
            RegraCategoriaIncompativel(),
        )

    def verificar(self, analises: tuple[AnaliseToken, ...]) -> tuple[Diagnostico, ...]:
        return tuple(
            diagnostico
            for regra in self.regras
            for diagnostico in regra.verificar(analises)
        )

    def reconhecer_constituintes(
        self, analises: tuple[AnaliseToken, ...]
    ) -> tuple[Constituinte, ...]:
        constituintes: list[Constituinte] = []
        for segmento in _segmentos_frase(analises):
            for oracao in _dividir_em_oracoes(segmento):
                constituintes.extend(_constituintes_da_oracao(oracao))
        return tuple(constituintes)


def _segmentos_frase(
    analises: tuple[AnaliseToken, ...]
) -> tuple[tuple[AnaliseToken, ...], ...]:
    segmentos: list[tuple[AnaliseToken, ...]] = []
    atual: list[AnaliseToken] = []
    for analise in analises:
        if analise.token.texto in ".!?":
            if atual:
                segmentos.append(tuple(atual))
                atual = []
            continue
        atual.append(analise)
    if atual:
        segmentos.append(tuple(atual))
    return tuple(segmentos)


# Fecho curado, não exaustivo -- mesmo critério de `_PARTICIPIOS_IRREGULARES`
# em lexico_expansao.py: só as conjunções subordinativas mais frequentes que
# introduzem oração própria de forma inequívoca. Coordenativas ("e", "mas",
# "ou") ficam de fora de propósito: "pão e manteiga" (NP) é indistinguível de
# "comeu e saiu" (oração) sem uma gramática real, e um falso positivo quebra
# a leitura de sujeito/objeto da frase inteira.
_CONJUNCOES_SUBORDINATIVAS = {"que", "porque", "quando", "se", "embora", "pois", "caso"}
_VERBOS_LIGACAO = {"haver", "ser", "estar", "ficar", "parecer"}
_VERBOS_AUXILIARES = {"ser", "estar", "ter", "haver", "ir", "vir", "ficar", "andar"}
_VERBOS_IMPESSOAIS = {"chover", "nevar", "amanhecer", "anoitecer", "ventar", "trovejar", "haver"}


def _eh_nao_finito(leitura) -> bool:
    return leitura.atributos.get("tempo") in {"gerúndio", "particípio"}


def _indice_primeiro_verbo(segmento: tuple[AnaliseToken, ...]) -> int | None:
    """Localiza o verbo âncora pela leitura principal selecionada.

    A desambiguação já correu antes da gramática (`motor.py`), então
    `principal` já reflete o contexto quando há sinal suficiente -- por
    isso ela vem primeiro. Um homónimo puro como "casa" (substantivo
    "casa"/verbo "casar") tem leitura de verbo entre as alternativas não
    escolhidas mesmo depois de desambiguado; sem a preferência por
    `principal` aqui, "A casa é bonita" acharia o verbo em "casa", não em
    "é". Leituras alternativas ficam disponíveis para o diagnóstico de
    ambiguidade, mas nunca são promovidas implicitamente nesta etapa.
    """
    return next(
        (i for i, analise in enumerate(segmento) if analise.principal.classe == ClasseGramatical.VERBO),
        None,
    )


def _dividir_em_oracoes(
    segmento: tuple[AnaliseToken, ...]
) -> tuple[tuple[AnaliseToken, ...], ...]:
    """Separa uma frase com mais de um verbo em orações independentes.

    Só divide em conjunção subordinativa cuja leitura PRINCIPAL (não
    qualquer leitura alternativa) seja mesmo conjunção -- isso evita, por
    exemplo, dividir em "se" quando na verdade é o clítico reflexivo
    decomposto ("machucou-se"), que carrega uma leitura de conjunção
    residual entre as alternativas não escolhidas. Pelo mesmo motivo, a
    contagem de verbos usa só a leitura principal (ver `_indice_primeiro_verbo`).
    """
    indices_verbo = [
        i
        for i, analise in enumerate(segmento)
        if analise.principal.classe == ClasseGramatical.VERBO
    ]
    if len(indices_verbo) <= 1:
        return (segmento,)
    verbo_em = set(indices_verbo)
    oracoes: list[tuple[AnaliseToken, ...]] = []
    inicio = 0
    verbos_no_trecho = 0
    for i, analise in enumerate(segmento):
        if i in verbo_em:
            verbos_no_trecho += 1
        eh_subordinativa = (
            analise.principal.classe == ClasseGramatical.CONJUNCAO
            and analise.token.normalizado in _CONJUNCOES_SUBORDINATIVAS
        )
        resta_verbo_depois = any(idx > i for idx in indices_verbo)
        if eh_subordinativa and verbos_no_trecho >= 1 and resta_verbo_depois and i > inicio:
            oracoes.append(segmento[inicio:i])
            inicio = i + 1
            verbos_no_trecho = 0
    oracoes.append(segmento[inicio:])
    return tuple(oracao for oracao in oracoes if oracao)


def _constituintes_da_oracao(segmento: tuple[AnaliseToken, ...]) -> list[Constituinte]:
    resultado: list[Constituinte] = []
    indice_verbo = _indice_primeiro_verbo(segmento)
    if indice_verbo is None:
        return resultado

    verbo_principal = _leitura_de_classe(segmento[indice_verbo], ClasseGramatical.VERBO)
    indice_nucleo = indice_verbo
    nucleo_verbal = verbo_principal
    eh_cadeia_auxiliar = False
    if verbo_principal.lema in _VERBOS_AUXILIARES and indice_verbo + 1 < len(segmento):
        candidato_nucleo = _leitura_de_classe(segmento[indice_verbo + 1], ClasseGramatical.VERBO)
        if candidato_nucleo is not None and _eh_nao_finito(candidato_nucleo):
            eh_cadeia_auxiliar = True
            indice_nucleo = indice_verbo + 1
            nucleo_verbal = candidato_nucleo
            resultado.append(
                Constituinte(
                    "auxiliar_verbal",
                    segmento[indice_verbo].token.texto,
                    segmento[indice_verbo].token.inicio,
                    segmento[indice_verbo].token.fim,
                )
            )
    eh_passiva = (
        eh_cadeia_auxiliar
        and verbo_principal.lema == "ser"
        and nucleo_verbal.atributos.get("tempo") == "particípio"
    )

    indice_virgula = next(
        (i for i, item in enumerate(segmento[:indice_verbo]) if item.token.texto == ","),
        None,
    )
    palavras_antes = [
        item for item in segmento[:indice_verbo]
        if item.token.texto.strip() and item.token.texto not in ",;:"
    ]
    do_verbo_em_diante = [
        item for item in segmento[indice_verbo:]
        if item.token.texto not in ".!?,;:"
    ]
    sujeito_marcado = False
    if indice_virgula is not None and indice_virgula > 0:
        vocativo = [
            item for item in segmento[:indice_virgula]
            if item.token.tipo.value == "palavra"
        ]
        if vocativo:
            resultado.append(
                Constituinte(
                    "vocativo",
                    _juntar_tokens(vocativo),
                    vocativo[0].token.inicio,
                    vocativo[-1].token.fim,
                )
            )
        palavras_antes = []
    if palavras_antes:
        resultado.append(
            Constituinte(
                "sujeito_paciente" if eh_passiva else "sujeito",
                _juntar_tokens(palavras_antes),
                palavras_antes[0].token.inicio,
                palavras_antes[-1].token.fim,
            )
        )
        sujeito_marcado = True
    if do_verbo_em_diante:
        resultado.append(
            Constituinte(
                "predicado",
                _juntar_tokens(do_verbo_em_diante),
                do_verbo_em_diante[0].token.inicio,
                do_verbo_em_diante[-1].token.fim,
            )
        )

    posteriores = [
        item for item in segmento[indice_nucleo + 1 :]
        if item.token.tipo.value == "palavra"
    ]
    if eh_passiva:
        agente = None
        for i, item in enumerate(posteriores):
            if item.token.normalizado in {"por", "pelo", "pela", "pelos", "pelas"}:
                seguinte = next(
                    (p for p in posteriores[i + 1 :] if p.token.tipo.value == "palavra"),
                    None,
                )
                if seguinte is not None and (
                    _leitura_de_classe(seguinte, ClasseGramatical.SUBSTANTIVO) is not None
                    or _leitura_de_classe(seguinte, ClasseGramatical.PRONOME) is not None
                ):
                    agente = seguinte
                break
        if agente is not None:
            resultado.append(
                Constituinte(
                    "agente_da_passiva",
                    agente.token.texto,
                    agente.token.inicio,
                    agente.token.fim,
                )
            )
    else:
        nominal_posterior = next(
            (
                item
                for item in posteriores
                if _leitura_de_classe(item, ClasseGramatical.SUBSTANTIVO) is not None
                or (
                    (pronome := _leitura_de_classe(item, ClasseGramatical.PRONOME)) is not None
                    and pronome.atributos.get("funcao") != "clitico"
                )
            ),
            None,
        )
        verbo_sem_objeto_nominal = nucleo_verbal.lema in _VERBOS_LIGACAO
        if nominal_posterior is not None and not verbo_sem_objeto_nominal:
            funcao = "objeto_direto" if palavras_antes else "sujeito_posposto"
            if funcao == "sujeito_posposto":
                sujeito_marcado = True
            resultado.append(
                Constituinte(
                    funcao,
                    nominal_posterior.token.texto,
                    nominal_posterior.token.inicio,
                    nominal_posterior.token.fim,
                )
            )
        if not eh_cadeia_auxiliar and nucleo_verbal.lema in {"ser", "estar", "ficar", "parecer"}:
            predicativo = next(
                (
                    item for item in posteriores
                    if _leitura_de_classe(item, ClasseGramatical.ADJETIVO) is not None
                ),
                None,
            )
            if predicativo is not None:
                resultado.append(
                    Constituinte(
                        "predicativo",
                        predicativo.token.texto,
                        predicativo.token.inicio,
                        predicativo.token.fim,
                    )
                )

    if verbo_principal.lema in _VERBOS_IMPESSOAIS or nucleo_verbal.lema in _VERBOS_IMPESSOAIS:
        sujeito_marcado = True
    if (
        not sujeito_marcado
        and not _eh_nao_finito(verbo_principal)
        and verbo_principal.atributos.get("forma") != "infinitivo"
    ):
        resultado.append(
            Constituinte(
                "sujeito_oculto",
                "",
                segmento[indice_verbo].token.inicio,
                segmento[indice_verbo].token.inicio,
            )
        )
    return resultado
