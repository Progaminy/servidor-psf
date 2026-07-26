"""Tokenizador Unicode com posições no texto original."""
from __future__ import annotations

import re
import unicodedata

from .normalizacao import normalizar_chave
from .tipos import TipoToken, Token

_NUMERO = (
    r"(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|"
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|"
    r"\d+(?:[.,]\d+)?)"
)
_LIGACOES_PALAVRA = "-'’‐‑"
_TOKEN = re.compile(
    _NUMERO
    + rf"|[^\W\d_]+(?:[{re.escape(_LIGACOES_PALAVRA)}][^\W\d_]+)*"
    + r"|_|[^\w\s]",
    re.UNICODE,
)
_PONTUACAO = frozenset(".,;:!?…()[]{}«»“”\"'’—–‐‑-")


def _texto_nfc_e_mapa(texto: str) -> tuple[str, tuple[tuple[int, int], ...]]:
    """Normaliza NFC sem perder a correspondência com os offsets originais.

    O tokenizador precisa reconhecer ``na\u0303o`` como a mesma palavra que
    ``não``, mas a API continua a devolver posições no texto recebido. Cada
    carácter NFC fica associado ao intervalo do seu grupo base+diacríticos.
    """
    partes: list[str] = []
    mapa: list[tuple[int, int]] = []
    inicio = 0

    def anexar(fim: int) -> None:
        trecho = texto[inicio:fim]
        normalizado = unicodedata.normalize("NFC", trecho)
        partes.append(normalizado)
        if len(normalizado) == len(trecho):
            mapa.extend((inicio + indice, inicio + indice + 1) for indice in range(len(trecho)))
        else:
            mapa.extend((inicio, fim) for _ in normalizado)

    for indice, caractere in enumerate(texto):
        if indice > inicio and unicodedata.combining(caractere) == 0:
            anexar(indice)
            inicio = indice
    if inicio < len(texto):
        anexar(len(texto))
    return "".join(partes), tuple(mapa)


class Tokenizador:
    """Converte texto em tokens, preservando grafia e offsets."""

    def tokenizar(self, texto: str) -> tuple[Token, ...]:
        if not isinstance(texto, str):
            raise TypeError("texto deve ser uma string")
        texto_nfc, mapa = _texto_nfc_e_mapa(texto)
        resultado: list[Token] = []
        for ocorrencia in _TOKEN.finditer(texto_nfc):
            valor_nfc = ocorrencia.group(0)
            inicio_nfc, fim_nfc = ocorrencia.span()
            inicio_original = mapa[inicio_nfc][0]
            fim_original = mapa[fim_nfc - 1][1]
            valor_original = texto[inicio_original:fim_original]
            if valor_nfc[0].isdigit():
                tipo = TipoToken.NUMERO
            elif valor_nfc[0].isalpha():
                tipo = TipoToken.PALAVRA
            elif valor_nfc in _PONTUACAO:
                tipo = TipoToken.PONTUACAO
            else:
                tipo = TipoToken.SIMBOLO
            resultado.append(
                Token(
                    texto=valor_original,
                    normalizado=normalizar_chave(valor_nfc),
                    tipo=tipo,
                    inicio=inicio_original,
                    fim=fim_original,
                )
            )
        return tuple(resultado)
