"""Teorema de Pitágoras — Etapa 1090.

`nucleo/trigonometria_natural.py::TrianguloRetangulo` (Etapa 1033) já
sabe TUDO sobre razões trigonométricas de um triângulo retângulo -- mas
exige os três lados prontos, com hipotenusa inteira (ele só valida
a²+b²=h², nunca resolve h a partir de a,b). Isso cobre ternos
pitagóricos (3-4-5, 6-8-10...), mas não o caso comum de sala de aula
-- catetos pequenos quaisquer, hipotenusa irracional (2 e 3 -> h=√13).

Esta etapa fecha exatamente essa pergunta: dados os dois catetos,
constrói h² = a²+b² (Etapa 1076, potenciação por repetição, mais soma)
e resolve h por raiz quadrada dígito a dígito (Etapa 1089) -- a mesma
peça que faltava no exemplo original que motivou a Etapa 1089.

Regra 17 (REGRA_INTEGRIDADE.md): o PSF resolve tudo pela via própria
("humana") e PODE, além disso, usar uma máquina de calcular quando
ajuda -- nunca em vez da via própria. `conferir_com_calculadora=True`
liga esse apoio opcional: tenta consultar `cao_de_caca/PSF-Calculadora`
(`MotorPitagoras`, que usa `decimal.Decimal.sqrt()`) só para CONFERIR o
valor que a Etapa 1089 já construiu sozinha, nunca para produzi-lo. Sem
o cão de caça instalado (projeto separado, fora do núcleo), o resultado
é idêntico em todos os campos -- só `conferencia_cao_de_caca` fica
`None` em vez de `True`/`False`.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

from .raiz_quadrada import RaizQuadradaPSF, raiz_quadrada_por_digitos

_RAIZ_PROJETO = Path(__file__).resolve().parents[1]
_CAMINHO_CAO_DE_CACA = _RAIZ_PROJETO / "cao_de_caca" / "PSF-Calculadora"


def _validar_natural_positivo(n: int, nome: str) -> None:
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"{nome} deve ser um natural positivo (lado de triângulo)")


@dataclass(frozen=True, slots=True)
class HipotenusaPSF:
    cateto_a: int
    cateto_b: int
    soma_quadrados: int
    raiz: RaizQuadradaPSF
    exata: bool
    passos: tuple[str, ...]
    conferencia_cao_de_caca: bool | None = None

    @property
    def decimal(self) -> str:
        return self.raiz.decimal


def _conferir_com_cao_de_caca(cateto_a: int, cateto_b: int, raiz: RaizQuadradaPSF) -> bool | None:
    """Compara o valor já construído pela Etapa 1089 com o do cão de
    caça (calculadora externa) -- não produz nenhum dígito da resposta.
    Qualquer ausência ou falha (projeto não instalado, import quebrado,
    resposta inesperada) devolve `None`: o cão de caça é sempre
    dispensável, nunca uma dependência real (Regra 17)."""
    if not _CAMINHO_CAO_DE_CACA.is_dir():
        return None
    caminho_str = str(_CAMINHO_CAO_DE_CACA)
    inseriu_caminho = caminho_str not in sys.path
    if inseriu_caminho:
        sys.path.insert(0, caminho_str)
    try:
        from assistente_psf import MotorPitagoras

        resposta = MotorPitagoras().calcular(f"pitagoras hipotenusa {cateto_a} {cateto_b}")
    except Exception:
        return None
    finally:
        if inseriu_caminho and caminho_str in sys.path:
            sys.path.remove(caminho_str)

    if not isinstance(resposta, dict) or "resultado" not in resposta:
        return None
    try:
        valor_calculadora = Decimal(resposta["resultado"])
    except Exception:
        return None

    quantizador = Decimal("1." + "0" * raiz.casas) if raiz.casas else Decimal("1")
    truncado_calculadora = valor_calculadora.quantize(quantizador, rounding=ROUND_DOWN)
    valor_psf = Decimal(raiz.decimal.replace(",", "."))
    return truncado_calculadora == valor_psf


def hipotenusa(
    cateto_a: int,
    cateto_b: int,
    casas: int = 4,
    conferir_com_calculadora: bool = False,
) -> HipotenusaPSF:
    """Constrói a hipotenusa de um triângulo retângulo dados os dois
    catetos, pelo Teorema de Pitágoras: h² = a² + b², h = √(a²+b²).

    Nunca finge um valor exato quando a raiz não fecha: `exata` diz se
    a²+b² é quadrado perfeito; senão, `decimal` é uma aproximação
    honesta truncada em `casas` (nunca arredondada por fora, ver Etapa
    1089), e `raiz.resto_final` continua não-zero para provar isso.

    O resultado (`decimal`, `exata`, `passos`) vem sempre e só da
    construção PSF, independentemente de `conferir_com_calculadora`.
    Com `conferir_com_calculadora=True`, tenta também comparar contra o
    cão de caça (Regra 17) -- resultado da comparação em
    `conferencia_cao_de_caca` (`None` quando indisponível).
    """
    _validar_natural_positivo(cateto_a, "cateto_a")
    _validar_natural_positivo(cateto_b, "cateto_b")

    quadrado_a = cateto_a * cateto_a
    quadrado_b = cateto_b * cateto_b
    soma_quadrados = quadrado_a + quadrado_b
    raiz = raiz_quadrada_por_digitos(soma_quadrados, casas=casas)

    passos = (
        f"Teorema de Pitágoras: h² = a² + b², com a={cateto_a}, b={cateto_b}.",
        f"h² = {cateto_a}² + {cateto_b}² = {quadrado_a} + {quadrado_b} = {soma_quadrados}.",
        (
            f"h = √{soma_quadrados} = {raiz.parte_inteira} exatamente "
            f"(quadrado perfeito)."
            if raiz.exato
            else
            f"√{soma_quadrados} não é exata (Etapas 1080-1083: irracional sempre que "
            f"{soma_quadrados} tem algum primo com expoente ímpar na fatoração) -- "
            f"h ≈ {raiz.decimal}, aproximado dígito a dígito (Etapa 1089), truncado em "
            f"{casas} casas, nunca arredondado por fora."
        ),
    )

    conferencia = _conferir_com_cao_de_caca(cateto_a, cateto_b, raiz) if conferir_com_calculadora else None

    return HipotenusaPSF(
        cateto_a=cateto_a,
        cateto_b=cateto_b,
        soma_quadrados=soma_quadrados,
        raiz=raiz,
        exata=raiz.exato,
        passos=passos,
        conferencia_cao_de_caca=conferencia,
    )
