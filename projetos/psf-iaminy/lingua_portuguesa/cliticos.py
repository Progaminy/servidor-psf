"""Decomposição conservadora de formas verbais com pronome clítico."""
from __future__ import annotations

from .lexico import Dicionario
from .normalizacao import normalizar_chave
from .tipos import ClasseGramatical, TipoToken, Token


_CLITICOS = frozenset({"me", "te", "se", "nos", "vos", "o", "a", "os", "as", "lhe", "lhes"})
_TERMINACOES_VERBAIS = (
    "am", "em", "aram", "eram", "iram", "ou", "ei", "ava", "iam", "asse", "esse", "isse"
)


def decompor_cliticos(
    tokens: tuple[Token, ...], dicionario: Dicionario
) -> tuple[Token, ...]:
    """Separa ``verbo-clítico`` apenas quando o radical é verbo no léxico.

    Palavras lexicais hifenizadas comuns permanecem intactas. Os offsets
    continuam apontando para o texto original, inclusive o hífen.
    """
    resultado: list[Token] = []
    for token in tokens:
        partes = token.texto.split("-")
        if token.tipo != TipoToken.PALAVRA or len(partes) != 2:
            resultado.append(token)
            continue
        forma_verbal, clitico = partes
        verbo_lexical = any(
            entrada.classe == ClasseGramatical.VERBO
            for entrada in dicionario.buscar(forma_verbal)
        )
        verbo_regular_provavel = forma_verbal.casefold().endswith(_TERMINACOES_VERBAIS)
        if clitico.casefold() not in _CLITICOS or not (verbo_lexical or verbo_regular_provavel):
            resultado.append(token)
            continue
        meio = token.inicio + len(forma_verbal)
        resultado.extend(
            (
                Token(
                    forma_verbal,
                    normalizar_chave(forma_verbal),
                    TipoToken.PALAVRA,
                    token.inicio,
                    meio,
                ),
                Token("-", "-", TipoToken.PONTUACAO, meio, meio + 1),
                Token(
                    clitico,
                    normalizar_chave(clitico),
                    TipoToken.PALAVRA,
                    meio + 1,
                    token.fim,
                ),
            )
        )
    return tuple(resultado)
