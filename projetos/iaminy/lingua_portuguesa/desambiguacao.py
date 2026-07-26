"""Desambiguação de leitura por gramática real -- Fase 6.2 do plano de
corretor, substituto honesto da técnica 8 (BERT/homónimos em contexto).

`AnaliseToken.principal` é sempre `leituras[0]`, cego a contexto -- quando
uma palavra tem leituras de classes diferentes (ex.: "banco" substantivo
vs "bancar" verbo), a primeira leitura pode ser a errada para a frase.
`escolher_leitura()` usa gramática real (a mesma deteção de verbo ausente
de `gramatica.RegraCategoriaIncompativel`) para escolher, não um
transformer treinado em contexto.

**Limite de escopo declarado, não escondido**: isto resolve homónimo ENTRE
classes diferentes (a mesma forma lida como substantivo ou como verbo).
Não resolve homónimo semântico DENTRO da mesma classe (ex.: "manga" fruta
vs "manga" de camisa, ambos substantivo) -- isso exigiria dado de
regência/seleção verbal que o projeto não tem. Fica registado como decisão
de dado futura e separada, mesmo status da fonte de vocabulário da Fase 3.
"""
from __future__ import annotations

from .tipos import AnaliseToken, ClasseGramatical, LeituraMorfologica


def escolher_leitura(
    analise: AnaliseToken,
    vizinhanca: tuple[AnaliseToken, ...],
    *,
    verbo_coordenado: bool = False,
    verbo_em_cadeia: bool = False,
) -> LeituraMorfologica:
    """Escolhe, entre as leituras de `analise`, a que melhor se encaixa no
    contexto sintático dado por `vizinhanca` (o resto da frase, sem
    incluir `analise`)."""
    if len(analise.leituras) <= 1:
        return analise.principal

    ha_verbo_na_vizinhanca = any(
        outro.leituras and outro.principal.classe == ClasseGramatical.VERBO
        for outro in vizinhanca
    )
    leitura_nao_verbo = next(
        (leitura for leitura in analise.leituras if leitura.classe != ClasseGramatical.VERBO), None
    )
    leitura_verbo = next(
        (leitura for leitura in analise.leituras if leitura.classe == ClasseGramatical.VERBO), None
    )

    if verbo_em_cadeia and leitura_verbo is not None:
        # O auxiliar fornece evidência local suficiente para escolher a forma
        # não finita: ``foram escritas``, ``estão estudando``, ``vai cantar``.
        return leitura_verbo

    if verbo_coordenado and leitura_verbo is not None:
        # Em ``Eu como e bebo``/``Eu banco e pago``, a existência do segundo
        # verbo é evidência a favor da leitura verbal do primeiro, não contra
        # ela. A pista é deliberadamente estreita: conjunção ``e`` adjacente
        # ligando esta forma a outra forma cuja leitura PRINCIPAL já é verbo.
        return leitura_verbo

    if ha_verbo_na_vizinhanca and leitura_nao_verbo is not None:
        # a frase já tem verbo em outro token -- a leitura de verbo desta
        # palavra provavelmente está errada aqui.
        return leitura_nao_verbo

    if not ha_verbo_na_vizinhanca and leitura_verbo is not None:
        # a frase parece sem verbo nenhum, e esta palavra pode ser um --
        # é exatamente o caso que RegraCategoriaIncompativel sinaliza.
        return leitura_verbo

    return analise.principal


_VERBOS_AUXILIARES = frozenset({"ser", "estar", "ter", "haver", "ir", "vir", "ficar", "andar"})


def _esta_em_cadeia_verbal(
    segmento: tuple[AnaliseToken, ...], indice: int
) -> bool:
    """Seleciona infinitivo/gerúndio/particípio imediatamente após auxiliar."""
    if indice < 1:
        return False
    auxiliar = segmento[indice - 1].principal
    if (
        auxiliar.classe != ClasseGramatical.VERBO
        or auxiliar.lema not in _VERBOS_AUXILIARES
    ):
        return False
    if auxiliar.lema in {"estar", "ficar"} and any(
        leitura.classe == ClasseGramatical.ADJETIVO for leitura in segmento[indice].leituras
    ):
        return False
    return any(
        leitura.classe == ClasseGramatical.VERBO
        and (
            leitura.atributos.get("tempo") in {"gerúndio", "particípio"}
            or leitura.atributos.get("forma") == "infinitivo"
        )
        for leitura in segmento[indice].leituras
    )


def _esta_em_coordenacao_verbal(
    segmento: tuple[AnaliseToken, ...], indice: int
) -> bool:
    """Reconhece somente o padrão local ``verbo e verbo``.

    Não tenta resolver coordenação nominal nem procura verbos em leituras
    alternativas: pelo menos o outro membro precisa já ter sido selecionado
    como verbo pela morfologia.
    """
    ligado_a_esquerda = (
        indice >= 2
        and segmento[indice - 1].token.normalizado == "e"
        and segmento[indice - 2].principal.classe == ClasseGramatical.VERBO
    )
    ligado_a_direita = (
        indice + 2 < len(segmento)
        and segmento[indice + 1].token.normalizado == "e"
        and segmento[indice + 2].principal.classe == ClasseGramatical.VERBO
    )
    return ligado_a_esquerda or ligado_a_direita


def desambiguar_analises(
    analises: tuple[AnaliseToken, ...]
) -> tuple[AnaliseToken, ...]:
    """Promove a leitura contextual para a primeira posição.

    A operação conserva todas as leituras originais e trabalha por frase,
    impedindo que um verbo de outra frase influencie a decisão local.
    """
    resultado: list[AnaliseToken] = []
    inicio = 0
    for indice in range(len(analises) + 1):
        terminou = indice == len(analises)
        if not terminou and analises[indice].token.texto not in ".!?":
            continue
        segmento = analises[inicio:indice]
        for posicao, analise in enumerate(segmento):
            vizinhanca = segmento[:posicao] + segmento[posicao + 1 :]
            escolhida = escolher_leitura(
                analise,
                vizinhanca,
                verbo_coordenado=_esta_em_coordenacao_verbal(segmento, posicao),
                verbo_em_cadeia=_esta_em_cadeia_verbal(segmento, posicao),
            )
            if escolhida is analise.principal:
                resultado.append(analise)
            else:
                restantes = tuple(item for item in analise.leituras if item is not escolhida)
                resultado.append(AnaliseToken(analise.token, (escolhida,) + restantes))
        if not terminou:
            resultado.append(analises[indice])
        inicio = indice + 1
    return tuple(resultado)
