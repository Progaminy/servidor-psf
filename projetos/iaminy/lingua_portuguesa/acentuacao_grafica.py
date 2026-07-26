"""Regra de acentuação gráfica do português (Acordo Ortográfico de 1990).

Fecha, com tabela testada, três limites operacionais reais do conhecimento
puro (`regra de oxítona`, `regra de paroxítona`, `regra de monossílabo
tônico`, conceitos 433/434/436 em `conhecimento_puro.py`): dada a posição
já CONHECIDA da sílaba tônica (contada a partir do fim da palavra) e a
terminação da palavra, decide se a acentuação gráfica é exigida.

Descobrir QUAL sílaba é tônica a partir da escrita pura continua sendo o
problema geral em aberto (conceito "tonicidade", limite operacional
separado) -- não pode ser decidido em geral sem dicionário de pronúncia
ou marca gráfica já existente. Este módulo não tenta resolver isso; recebe
a posição tônica como dado e decide só a metade seguinte, mecânica.

Achado real ao validar contra o léxico vivo antes de escrever a regra:
palavras terminadas em ditongo oral tônico ("-eu"/"-ei"/"-oi") NÃO seguem
regra mecânica segura -- "valeu" (oxítona, "-eu") não tem acento, mas
"chapéu" (oxítona, "-éu") tem. A diferença é abertura vocálica (vogal
fechada em "valeu", aberta em "chapéu"), um facto lexical/fonético, não
recuperável da grafia sem acento. Por isso `decidir_acento_grafico`
devolve `exige_acento=None` (não decidido, motivo explícito) para essa
família, em vez de arriscar uma resposta errada -- mesma disciplina do
motor de Matemática ("não coberto pelo modelo finito", nunca resposta
fingida).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClasseTonica(Enum):
    MONOSSILABO_TONICO = "monossílabo tônico"
    OXITONA = "oxítona"
    PAROXITONA = "paroxítona"
    PROPAROXITONA = "proparoxítona"


def classificar_tonicidade(numero_silabas: int, indice_silaba_tonica: int) -> ClasseTonica:
    """`indice_silaba_tonica` conta a partir de 0 na primeira sílaba e
    precisa ser a sílaba tônica já conhecida (marca gráfica existente,
    dado de pronúncia ou convenção) -- esta função não a descobre."""
    if numero_silabas < 1:
        raise ValueError(f"número de sílabas inválido: {numero_silabas}")
    if not 0 <= indice_silaba_tonica < numero_silabas:
        raise ValueError(
            f"índice de sílaba tônica fora do intervalo: {indice_silaba_tonica} de {numero_silabas}"
        )
    if numero_silabas == 1:
        return ClasseTonica.MONOSSILABO_TONICO
    posicao_a_partir_do_fim = numero_silabas - indice_silaba_tonica
    if posicao_a_partir_do_fim == 1:
        return ClasseTonica.OXITONA
    if posicao_a_partir_do_fim == 2:
        return ClasseTonica.PAROXITONA
    return ClasseTonica.PROPAROXITONA


# Terminações "sem marca" -- o próprio facto de a palavra ser oxítona/
# paroxítona/monossílabo tônico sem exceder este conjunto já decide a
# acentuação, sem precisar de nenhuma lista lexical de exceções.
_TERMINACAO_VOGAL_A_E_O = ("a", "as", "e", "es", "o", "os")
_TERMINACAO_EM_ENS = ("em", "ens")
_TERMINACAO_AM = ("am",)
# Ditongo oral tônico final -- depende de abertura vocálica lexical, não
# decidido mecanicamente aqui (ver achado no docstring do módulo).
_TERMINACAO_DITONGO_ORAL_AMBIGUA = ("eu", "eus", "ei", "eis", "oi", "ois")


@dataclass(frozen=True, slots=True)
class DecisaoAcento:
    exige_acento: "bool | None"
    motivo: str


def decidir_acento_grafico(classe: ClasseTonica, palavra_sem_acento: str) -> DecisaoAcento:
    """Decide se `palavra_sem_acento` (já classificada em `classe`) exige
    marca gráfica de tonicidade -- ou devolve `exige_acento=None` quando a
    terminação foge da tabela mecânica conhecida (ditongo oral tônico
    ambíguo).

    `palavra_sem_acento` remove só o acento de tonicidade (agudo/
    circunflexo) que esta função decide -- o til de nasalidade ("ão",
    "õe", "ãe") é obrigatório e estrutural, não o acento em questão, e
    deve continuar presente na entrada (ex.: "órgão" -> "orgão", nunca
    "orgao"). Esta função não decide nasalidade, só tonicidade."""
    palavra = palavra_sem_acento.strip().casefold()
    if not palavra:
        raise ValueError("palavra vazia")

    if palavra.endswith(_TERMINACAO_DITONGO_ORAL_AMBIGUA) and classe in (
        ClasseTonica.MONOSSILABO_TONICO,
        ClasseTonica.OXITONA,
    ):
        return DecisaoAcento(
            None,
            "Ditongo oral tônico final ('-eu'/'-ei'/'-oi') depende de abertura "
            "vocálica lexical (ex.: 'valeu' sem acento, 'chapéu' com acento) -- "
            "não decidido por regra mecânica de terminação.",
        )

    if classe is ClasseTonica.PROPAROXITONA:
        return DecisaoAcento(True, "Toda proparoxítona recebe acento gráfico, sem exceção.")

    if classe is ClasseTonica.MONOSSILABO_TONICO:
        exige = palavra.endswith(_TERMINACAO_VOGAL_A_E_O)
        return DecisaoAcento(
            exige,
            "Monossílabo tônico terminado em a(s)/e(s)/o(s) recebe acento."
            if exige
            else "Monossílabo tônico fora de a(s)/e(s)/o(s) não recebe acento por esta regra.",
        )

    if classe is ClasseTonica.OXITONA:
        exige = palavra.endswith(_TERMINACAO_VOGAL_A_E_O + _TERMINACAO_EM_ENS)
        return DecisaoAcento(
            exige,
            "Oxítona terminada em a(s)/e(s)/o(s)/em/ens recebe acento."
            if exige
            else "Oxítona fora de a(s)/e(s)/o(s)/em/ens não recebe acento por esta regra.",
        )

    if classe is ClasseTonica.PAROXITONA:
        termina_sem_marca = palavra.endswith(_TERMINACAO_VOGAL_A_E_O + _TERMINACAO_EM_ENS + _TERMINACAO_AM)
        exige = not termina_sem_marca
        return DecisaoAcento(
            exige,
            "Paroxítona fora de a(s)/e(s)/o(s)/em/ens/am recebe acento."
            if exige
            else "Paroxítona terminada em a(s)/e(s)/o(s)/em/ens/am não recebe acento.",
        )

    raise ValueError(f"classe tônica desconhecida: {classe!r}")


# Acento diferencial: inventário fechado e explícito (não produtivo -- não
# cresce por regra, só por facto lexical documentado). Cobre os dois pares
# clássicos citados no conceito 438 e a família de verbos derivados de
# "ter"/"vir", que marcam a 3ª pessoa do plural com acento circunflexo pra
# distinguir da 3ª do singular (mesma forma sem o circunflexo).
ACENTO_DIFERENCIAL: "tuple[tuple[str, str, str], ...]" = (
    ("pôr", "por", "verbo 'pôr' (infinitivo) vs preposição 'por'."),
    ("pôde", "pode", "pretérito perfeito de 'poder' (3ª sg.) vs presente do indicativo (3ª sg.)."),
    ("têm", "tem", "presente do indicativo de 'ter', 3ª pl. vs 3ª sg."),
    ("vêm", "vem", "presente do indicativo de 'vir', 3ª pl. vs 3ª sg."),
    ("contêm", "contém", "presente do indicativo de 'conter', 3ª pl. vs 3ª sg."),
    ("convêm", "convém", "presente do indicativo de 'convir', 3ª pl. vs 3ª sg."),
    ("detêm", "detém", "presente do indicativo de 'deter', 3ª pl. vs 3ª sg."),
    ("mantêm", "mantém", "presente do indicativo de 'manter', 3ª pl. vs 3ª sg."),
    ("obtêm", "obtém", "presente do indicativo de 'obter', 3ª pl. vs 3ª sg."),
    ("retêm", "retém", "presente do indicativo de 'reter', 3ª pl. vs 3ª sg."),
    ("intervêm", "intervém", "presente do indicativo de 'intervir', 3ª pl. vs 3ª sg."),
    ("provêm", "provém", "presente do indicativo de 'provir', 3ª pl. vs 3ª sg."),
    ("sobrevêm", "sobrevém", "presente do indicativo de 'sobrevir', 3ª pl. vs 3ª sg."),
)
