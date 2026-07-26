"""Raiz quadrada reconstruída dígito a dígito — Etapa 1089.

Regra 16 (REGRA_INTEGRIDADE.md): uma lacuna de UM caminho puro não pode
virar limite aceito do PSF enquanto existir outro caminho puro não
tentado. `nucleo/reais.py` (Etapa 1085) aproxima raiz quadrada por
Newton-Raphson sobre numerais de Church -- método honesto, mas que
esbarra num limite de desempenho real (predecessor de Church custa
O(n), então até alvos pequenos como 13 estouram profundidade de
recursão). Este módulo resolve a MESMA pergunta por outro caminho PSF
puro: o algoritmo escolar de extração de raiz quadrada dígito a dígito
(o mesmo ensinado antes das calculadoras, irmão do algoritmo da divisão
longa já reconstruído em `expandir_decimal`, Etapa 1078).

Separação deliberada de papel (a mesma que existe entre um humano que
sabe extrair raiz na mão e uma tábua/calculadora usada só para não
perder tempo nas contas de apoio -- ele não deixa de saber o método
por isso; a conta não é sobre "como se soma 36 vezes 20"): a primeira
tentativa deste módulo reusava `nucleo/aritmetica_escolar_nativa.py`
(soma por sucessão, multiplicação por soma repetida) também para o
bookkeeping -- e herdava o MESMO limite de fundo dos numerais de
Church por outra porta: aquelas primitivas são O(valor), não O(dígitos),
então a "raiz" acumulada (que cresce a cada casa) tornava
`multiplicar(raiz, 20)` sozinho catastroficamente lento a partir de
poucas casas decimais. O MÉTODO (buscar o maior dígito 0..9 que ainda
cabe, "descendo" pares de dígitos como no papel -- nunca `math.sqrt`,
nunca `** 0.5`, nunca `decimal`/`float`) é a construção PSF e fica
inteiramente visível em `passos`. A aritmética que executa esse método
(somar, multiplicar, comparar) usa `+`/`-`/`*` nativos do Python como
apoio de cálculo, exatamente como a tabela de cosseno ou a calculadora
do humano que já sabe o método -- não como resposta pronta substituindo
a construção.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RaizQuadradaPSF:
    alvo: int
    exato: bool
    parte_inteira: int
    decimal: str
    casas: int
    resto_final: int
    passos: tuple[str, ...]


def _validar_natural(n: int, nome: str) -> None:
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"{nome} deve ser natural finito")


def _digitos_base_dez(n: int) -> list[int]:
    """Dígitos de `n` do mais significativo ao menos significativo,
    extraídos por divisões sucessivas por dez -- mesma ideia de
    `nucleo/aritmetica_escolar_nativa.py::dividir_com_resto` ("Base
    nativa para extrair dígitos"), só que em aritmética nativa: extrair
    dígito é bookkeeping, não o método sendo demonstrado aqui."""
    if n == 0:
        return [0]
    digitos: list[int] = []
    restante = n
    while restante > 0:
        restante, digito = divmod(restante, 10)
        digitos.append(digito)
    digitos.reverse()
    return digitos


def _pares_inteiros(n: int) -> list[int]:
    """Agrupa os dígitos de `n` em pares a partir da direita (Etapa
    escolar de extração de raiz): '169' -> [1, 69], '100' -> [1, 0]."""
    digitos = _digitos_base_dez(n)
    if len(digitos) % 2 == 1:
        digitos = [0] + digitos
    pares = []
    i = 0
    while i < len(digitos):
        pares.append(digitos[i] * 10 + digitos[i + 1])
        i += 2
    return pares


def raiz_quadrada_por_digitos(alvo: int, casas: int = 4) -> RaizQuadradaPSF:
    """Extrai √alvo casa a casa, exatamente como no algoritmo escolar
    em papel: a cada passo, "desce" o próximo par de dígitos (real,
    enquanto sobrarem dígitos de `alvo`; '00' depois, para as casas
    decimais) e procura o maior dígito 0..9 que ainda cabe -- nunca
    aproxima, nunca arredonda por fora: cada dígito produzido é exato
    dado o resto exato do passo anterior. Sem conjunto de "alvos
    verificados": o custo por casa é sempre até 10 comparações
    pequenas, não cresce com o tamanho de `alvo`.
    """
    _validar_natural(alvo, "alvo")
    if casas < 0:
        raise ValueError("casas não pode ser negativo")

    pares = _pares_inteiros(alvo)
    total_passos = len(pares) + casas

    raiz = 0
    resto = 0
    digitos_raiz: list[int] = []
    passos: list[str] = []
    exato: bool | None = None

    for indice in range(total_passos):
        if indice == len(pares):
            exato = resto == 0
        grupo = pares[indice] if indice < len(pares) else 0
        dividendo = resto * 100 + grupo
        prefixo = raiz * 20

        melhor_d = 0
        usado = 0
        for candidato_digito in range(10):
            candidato_usado = (prefixo + candidato_digito) * candidato_digito
            if candidato_usado <= dividendo:
                melhor_d = candidato_digito
                usado = candidato_usado
            else:
                break

        resto = dividendo - usado
        raiz = raiz * 10 + melhor_d
        digitos_raiz.append(melhor_d)
        casa = "inteira" if indice < len(pares) else f"decimal {indice - len(pares) + 1}"
        passos.append(
            f"desce {grupo:02d} -> dividendo {dividendo}; ({prefixo}+{melhor_d})×{melhor_d}={usado} "
            f"<= {dividendo}; resto {resto}; casa {casa} = {melhor_d}."
        )

    if exato is None:  # alvo já esgotado dentro das próprias casas inteiras (casas=0)
        exato = resto == 0

    parte_inteira_str = "".join(str(d) for d in digitos_raiz[: len(pares)]) or "0"
    parte_inteira = int(parte_inteira_str)
    digitos_decimais = digitos_raiz[len(pares) :]
    decimal = (
        f"{parte_inteira}," + "".join(str(d) for d in digitos_decimais)
        if digitos_decimais
        else str(parte_inteira)
    )

    return RaizQuadradaPSF(
        alvo=alvo,
        exato=exato,
        parte_inteira=parte_inteira,
        decimal=decimal,
        casas=casas,
        resto_final=resto,
        passos=tuple(passos),
    )
