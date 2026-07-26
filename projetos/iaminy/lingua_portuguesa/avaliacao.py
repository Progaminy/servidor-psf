"""Avaliação reproduzível do analisador contra um pequeno corpus dourado."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from importlib.resources import files
from typing import Iterable

from .motor import MotorPortugues
from .tipos import ClasseGramatical, OpcoesAnalise, TipoToken


@dataclass(frozen=True, slots=True)
class MetricasClassificacao:
    verdadeiros_positivos: int
    falsos_positivos: int
    falsos_negativos: int

    @property
    def precisao(self) -> float:
        denominador = self.verdadeiros_positivos + self.falsos_positivos
        return self.verdadeiros_positivos / denominador if denominador else 1.0

    @property
    def revocacao(self) -> float:
        denominador = self.verdadeiros_positivos + self.falsos_negativos
        return self.verdadeiros_positivos / denominador if denominador else 1.0

    @property
    def f1(self) -> float:
        soma = self.precisao + self.revocacao
        return 2 * self.precisao * self.revocacao / soma if soma else 0.0


@dataclass(frozen=True, slots=True)
class FalhaCaso:
    caso: str
    categoria: str
    esperado: tuple[str, ...]
    obtido: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RelatorioAvaliacao:
    total_casos: int
    diagnosticos: MetricasClassificacao
    constituintes: MetricasClassificacao
    acuracia_morfologica: float
    cobertura_lexical: float
    taxa_falso_positivo_textos_corretos: float
    sugestoes_corretas: int
    sugestoes_esperadas: int
    falhas: tuple[FalhaCaso, ...]


def carregar_corpus() -> tuple[dict, ...]:
    caminho = files("lingua_portuguesa.dados").joinpath("corpus_avaliacao_portugues.json")
    with caminho.open("r", encoding="utf-8") as arquivo:
        return tuple(json.load(arquivo))


def _comparar_contagens(esperado: Counter, obtido: Counter) -> tuple[int, int, int]:
    verdadeiros = sum((esperado & obtido).values())
    falsos_positivos = sum((obtido - esperado).values())
    falsos_negativos = sum((esperado - obtido).values())
    return verdadeiros, falsos_positivos, falsos_negativos


def avaliar_motor(
    motor: MotorPortugues | None = None,
    casos: Iterable[dict] | None = None,
    *,
    opcoes: OpcoesAnalise | None = None,
) -> RelatorioAvaliacao:
    motor = motor or MotorPortugues()
    casos_reais = tuple(casos) if casos is not None else carregar_corpus()
    contagem_diagnosticos = [0, 0, 0]
    contagem_constituintes = [0, 0, 0]
    morfologia_certa = morfologia_total = 0
    palavras_reconhecidas = palavras_total = 0
    corretos_com_alerta = total_corretos = 0
    sugestoes_corretas = sugestoes_esperadas = 0
    falhas: list[FalhaCaso] = []

    for caso in casos_reais:
        analise = motor.analisar(caso["texto"], opcoes=opcoes)
        esperados_diag = Counter(caso.get("diagnosticos", ()))
        obtidos_diag = Counter(item.codigo for item in analise.diagnosticos)
        for indice, valor in enumerate(_comparar_contagens(esperados_diag, obtidos_diag)):
            contagem_diagnosticos[indice] += valor
        if esperados_diag != obtidos_diag:
            falhas.append(
                FalhaCaso(
                    caso["id"],
                    "diagnosticos",
                    tuple(esperados_diag.elements()),
                    tuple(obtidos_diag.elements()),
                )
            )

        if "constituintes" in caso:
            esperados_const = Counter(tuple(item) for item in caso["constituintes"])
            obtidos_const = Counter((item.funcao, item.texto) for item in analise.constituintes)
            for indice, valor in enumerate(_comparar_contagens(esperados_const, obtidos_const)):
                contagem_constituintes[indice] += valor
            if esperados_const != obtidos_const:
                falhas.append(
                    FalhaCaso(
                        caso["id"],
                        "constituintes",
                        tuple(f"{a}: {b}" for a, b in esperados_const.elements()),
                        tuple(f"{a}: {b}" for a, b in obtidos_const.elements()),
                    )
                )

        for token, classe in caso.get("classes", ()):
            morfologia_total += 1
            leitura = next(
                (item.principal for item in analise.morfologia if item.token.texto == token),
                None,
            )
            if leitura is not None and leitura.classe.value == classe:
                morfologia_certa += 1
            else:
                falhas.append(
                    FalhaCaso(
                        caso["id"],
                        f"classe:{token}",
                        (classe,),
                        (leitura.classe.value if leitura is not None else "ausente",),
                    )
                )

        for item in analise.morfologia:
            if item.token.tipo == TipoToken.PALAVRA:
                palavras_total += 1
                if item.principal.classe != ClasseGramatical.DESCONHECIDA:
                    palavras_reconhecidas += 1

        if caso.get("correto", False):
            total_corretos += 1
            inesperados = obtidos_diag - esperados_diag
            if inesperados:
                corretos_com_alerta += 1

        sugestoes = dict(analise.correcao.sugestoes_ortografia) if analise.correcao else {}
        alteracoes = {
            antes: depois for antes, depois, _motivo in analise.correcao.alteracoes_whitelist
        } if analise.correcao else {}
        for palavra, esperada in caso.get("sugestoes", ()):
            sugestoes_esperadas += 1
            if esperada in sugestoes.get(palavra, ()) or alteracoes.get(palavra) == esperada:
                sugestoes_corretas += 1
            else:
                falhas.append(
                    FalhaCaso(
                        caso["id"], "sugestao", (f"{palavra}->{esperada}",), ()
                    )
                )

        uso_esperado = tuple(caso.get("uso_do_se", ()))
        if uso_esperado != analise.usos_do_se:
            falhas.append(
                FalhaCaso(caso["id"], "uso_do_se", uso_esperado, analise.usos_do_se)
            )

    return RelatorioAvaliacao(
        total_casos=len(casos_reais),
        diagnosticos=MetricasClassificacao(*contagem_diagnosticos),
        constituintes=MetricasClassificacao(*contagem_constituintes),
        acuracia_morfologica=morfologia_certa / morfologia_total if morfologia_total else 1.0,
        cobertura_lexical=palavras_reconhecidas / palavras_total if palavras_total else 1.0,
        taxa_falso_positivo_textos_corretos=(
            corretos_com_alerta / total_corretos if total_corretos else 0.0
        ),
        sugestoes_corretas=sugestoes_corretas,
        sugestoes_esperadas=sugestoes_esperadas,
        falhas=tuple(falhas),
    )


def main() -> int:
    """Imprime o relatório em JSON para uso local e em integração contínua."""
    print(json.dumps(asdict(avaliar_motor()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
