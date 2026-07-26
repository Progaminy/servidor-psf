"""Irracionalidade de √n para n composto com um fator de multiplicidade 1
— generaliza a Etapa 1081 (que exigia n primo) para muitos compostos.

A Etapa 1081 provou √p irracional para p primo, usando "p | k² ⟹ p | k"
(lema de Euclides, Etapa 18). Esta etapa nota que a mesma descida
funciona sempre que n tem AO MENOS UM fator primo p que aparece
exatamente uma vez em n (isto é, p | n mas p² ∤ n — n = p·m com p∤m),
mesmo que n não seja primo nem livre de quadrados por completo:

  suponha a,b naturais, b>0, mdc(a,b)=1, a²=n·b², n=p·m com p primo, p∤m
  → a² é múltiplo de p (é n·b² = p·m·b²)
  → a é múltiplo de p (mesmo lema da Etapa 1081, aplicado a k=a)
  → a = p·k para algum natural k
  → p²k² = p·m·b² ⟹ p·k² = m·b²
  → p | m·b² (é p·k², múltiplo de p) e p∤m ⟹ p | b² (lema de Euclides:
    p primo, p∤m, p|m·b² ⟹ p|b², já que p não pode "vir" do fator m)
  → b é múltiplo de p (mesmo lema, aplicado a k=b)
  → p divide a e p divide b ⟹ mdc(a,b) é múltiplo de p ⟹ mdc(a,b) ≥ p
  → contradiz mdc(a,b) = 1, assumido no início

Cobre todo n com um fator de multiplicidade 1 (todo squarefree composto,
mais muitos outros: 12=2²·3 cobre via p=3, 24=2³·3 via p=3, ...). NÃO
cobre n onde nenhum primo tem multiplicidade exatamente 1 (8=2³, 16=2⁴,
32=2⁵, 72=2³·3² — nestes, todo primo aparece 0, 2, 3+ vezes sem nenhum
"exatamente 1"); esses exigiriam o argumento geral por valoração p-ádica
(expoente do primo, não só "aparece uma vez"), próximo alvo natural.
"""
from __future__ import annotations

from dataclasses import dataclass

from .aritmetica_escolar_nativa import dividir_com_resto, multiplicar, validar_natural
from .irracionalidade_raiz_prima import (
    eh_primo_pequeno,
    primo_divide_quadrado_implica_primo_divide_base,
)


def fator_multiplicidade_um(n: int) -> int | None:
    """Menor primo p tal que p | n e p² ∤ n, ou `None` se não existir
    (n=1, n é quadrado perfeito, ou todo fator primo de n aparece 0, 2,
    3+ vezes sem nenhum aparecer exatamente uma). Busca direta por
    divisão experimental, adequada só ao tamanho pequeno desta etapa.
    """
    validar_natural(n, "n")
    if n < 2:
        return None
    for candidato in range(2, n + 1):
        if dividir_com_resto(n, candidato)[1] != 0:
            continue
        if not eh_primo_pequeno(candidato):
            continue
        p_ao_quadrado = multiplicar(candidato, candidato)
        if dividir_com_resto(n, p_ao_quadrado)[1] != 0:
            return candidato
    return None


@dataclass(frozen=True, slots=True)
class ProvaIrracionalidadeRaizComposta:
    n: int
    fator_usado: int
    lema_verificado: bool
    alcance_verificacao: int
    conclusao: str
    valida: bool
    limite: str


def prova_raiz_n_irracional(n: int, alcance_verificacao: int = 20) -> ProvaIrracionalidadeRaizComposta:
    """Certifica a irracionalidade de √n, generalizando a Etapa 1081 para
    n composto com um fator de multiplicidade 1.

    Levanta `ValueError` quando `n` não tem fator assim (n=1, quadrado
    perfeito, ou nenhum primo de multiplicidade exatamente 1) -- este
    argumento simplesmente não se aplica a esses casos, não finge cobrir.
    """
    fator = fator_multiplicidade_um(n)
    if fator is None:
        raise ValueError(
            f"{n} não tem fator primo de multiplicidade 1 -- este argumento não se aplica "
            "(pode ser quadrado perfeito ou exigir o caso geral por valoração p-ádica)"
        )
    lema = all(
        primo_divide_quadrado_implica_primo_divide_base(fator, k)
        for k in range(1, alcance_verificacao + 1)
    )
    return ProvaIrracionalidadeRaizComposta(
        n=n,
        fator_usado=fator,
        lema_verificado=lema,
        alcance_verificacao=alcance_verificacao,
        conclusao=(
            f"Não existe a,b natural com mdc(a,b)=1 e a²={n}·b² -- "
            f"√{n} não é racional (via fator {fator}, multiplicidade 1)."
        ),
        valida=lema,
        limite=(
            "O lema é verificado neste alcance para o fator escolhido, não por "
            "busca infinita -- a prova de que vale para TODO k está no lema de "
            "Euclides (Etapa 18). A dedução final (mdc múltiplo do fator "
            "contradiz mdc=1) não depende de nenhum a,b concreto."
        ),
    )
