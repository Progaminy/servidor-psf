"""Resolvedor de perguntas conceituais de português -- "o que é X".

Espelha `ensino/resolvedor_exercicios.py` (que liga perguntas de conta ao
`MotorMatematica`), mas para o outro domínio: o `MotorPortugues` já tem
1141+ conceitos puros documentados (`lingua_portuguesa/conhecimento_puro.py`)
com definição, função e exemplos -- "verbo", "poema", "rima consoante",
"substantivo" já existem, ricos, testados. O que faltava não era
conhecimento; era ligação: nenhuma rota do chat vivo consultava
`MotorPortugues().conhecimento_portugues` para responder uma pergunta
conceitual direta, então "o que é um verbo?" caía em "não materializado"
mesmo com o conceito pronto.

Nunca inventa: quando o termo não bate com nenhum conceito documentado
(nem exato, nem por busca textual), diz isso com honestidade -- mesma
disciplina de `ensino/resolvedor_exercicios.py`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from lingua_portuguesa import ConceitoPortugues, MotorPortugues

_MOTOR = MotorPortugues()

_GATILHOS = (
    "qual é o conceito de", "qual e o conceito de", "qual o conceito de", "conceito de",
    "qual é o significado de", "qual e o significado de", "significado de",
    "qual a definição de", "qual a definicao de", "definição de", "definicao de",
    "o que vem a ser", "o que se entende por", "o que quer dizer",
    "o que é", "o que e", "o que são", "o que sao", "o que significa", "o que significam",
    "como funciona", "como funcionam",
    "me fale sobre", "fale sobre", "diga o que é", "diga o que e",
    "defina", "define", "explica", "explique", "explicar",
)

_PADRAO_PERGUNTA_CONCEITO = re.compile(
    r"(?:" + "|".join(re.escape(g) for g in _GATILHOS) + r")\s+"
    r"(?:uma|um|as|os|o|a)?\b\s*([^?!.]+?)\s*[?!.]*$",
    re.IGNORECASE,
)

_MAXIMO_DEPENDENCIAS_EM_PROSA = 3


@dataclass(frozen=True, slots=True)
class RespostaConceitoPortugues:
    pergunta: str
    resolvida: bool
    termo: "str | None"
    resposta: "str | None"
    raciocinio: str


def _extrair_termo(pergunta: str) -> "str | None":
    m = _PADRAO_PERGUNTA_CONCEITO.search(pergunta)
    if not m:
        return None
    termo = m.group(1).strip()
    termo = re.sub(r"^(?:uma|um|as|os|o|a)\s+", "", termo, flags=re.IGNORECASE).strip()
    return termo or None


def _buscar_conceito(termo: str) -> "ConceitoPortugues | None":
    conceito = _MOTOR.conhecimento_portugues.buscar(termo)
    if conceito is not None:
        return conceito

    candidatos = _MOTOR.buscar_conceitos_puros(termo)
    exatos = [c for c in candidatos if c.nome.casefold() == termo.casefold()]
    if exatos:
        return exatos[0]

    # Verifica se há candidato cujo nome bate exatamente com o termo em palavras
    coincidentes = [c for c in candidatos if c.nome.casefold().strip() == termo.casefold().strip()]
    if coincidentes:
        return coincidentes[0]

    if len(candidatos) == 1:
        return candidatos[0]
    return None


def _compor_resposta(conceito: ConceitoPortugues) -> str:
    partes = [conceito.construcao]
    if conceito.funcao:
        partes.append(conceito.funcao)
    if conceito.exemplos_minimos:
        partes.append(f"Exemplo: {conceito.exemplos_minimos[0]}")
    if conceito.depende_de and len(conceito.depende_de) <= _MAXIMO_DEPENDENCIAS_EM_PROSA:
        partes.append("Depende de: " + ", ".join(conceito.depende_de) + ".")
    return " ".join(partes)


def resolver_pergunta_conceito(pergunta: str) -> RespostaConceitoPortugues:
    termo = _extrair_termo(pergunta)
    if termo is None:
        return RespostaConceitoPortugues(
            pergunta, False, None, None,
            "Não reconheço isto como uma pergunta conceitual sobre um termo de português.",
        )

    conceito = _buscar_conceito(termo)
    if conceito is None:
        candidatos = _MOTOR.buscar_conceitos_puros(termo)
        if candidatos:
            nomes = ", ".join(c.nome for c in candidatos[:5])
            return RespostaConceitoPortugues(
                pergunta, False, termo, None,
                f"\"{termo}\" não é, sozinho, um conceito exato que eu tenha documentado, "
                f"mas encontrei conceitos relacionados: {nomes}. Pergunta por um desses nomes exatos.",
            )
        return RespostaConceitoPortugues(
            pergunta, False, termo, None,
            f"Ainda não tenho \"{termo}\" como conceito de português documentado -- "
            "não invento definição para não fingir conhecimento que não tenho.",
        )

    resposta = _compor_resposta(conceito)
    raciocinio = (
        f"Encontrei \"{conceito.nome}\" no conhecimento puro de português "
        f"(tema: {conceito.camada}) e usei a construção e a função já documentadas."
    )
    return RespostaConceitoPortugues(pergunta, True, conceito.nome, resposta, raciocinio)

