"""Irracionalidade de √n para QUALQUER n que não seja quadrado perfeito
— fecha a generalização (Etapas 1080, 1081, 1082 cobriam casos parciais:
só p=2, só primos, só compostos com um fator de multiplicidade 1).

A peça que faltava é a valoração p-ádica: v_p(n), a maior potência de p
que divide n. Pelo Teorema Fundamental da Aritmética — existência
(Etapa 13) e unicidade via lema de Euclides (Etapa 14/tfa unicidade) —,
a fatoração em primos é única, e por isso v_p é bem definida e ADITIVA:
v_p(x·y) = v_p(x) + v_p(y). Isto é o que faltava para tratar QUALQUER n,
não só os com um fator "simples":

```text
n não é quadrado perfeito
  <=> algum primo p divide n com expoente ÍMPAR (v_p(n) ímpar) --
      se todo expoente fosse par, n = (produto de p^(expoente/2))²

suponha a,b naturais, b>0, a²=n·b² (não precisa nem de mdc(a,b)=1 aqui)
→ v_p(a²) = 2·v_p(a) -- sempre par, qualquer que seja a
→ v_p(n·b²) = v_p(n) + 2·v_p(b) -- mesma paridade de v_p(n), que é ímpar
→ a² = n·b² exige v_p(a²) = v_p(n·b²), ou seja par = ímpar -- impossível
→ nenhum a,b satisfaz a²=n·b² -- √n não é racional
```

Mais simples que a Etapa 1082 (nem precisa de mdc(a,b)=1 -- a
contradição de paridade do expoente já basta sozinha), e cobre TODO n
que não é quadrado perfeito, incluindo os casos que a Etapa 1082
recusava (8=2³, 16=2⁴, 32=2⁵ — aqui v_2 é 3, 4, 5; só 4 é par, então
8, 32 têm v_2 ímpar e caem aqui; 16 tem v_2=4 par, e de facto 16=4² É
quadrado perfeito, corretamente fora do alcance de qualquer prova de
irracionalidade).
"""
from __future__ import annotations

from dataclasses import dataclass

from .aritmetica_escolar_nativa import dividir_com_resto, dividir_exato, validar_natural
from .irracionalidade_raiz_prima import eh_primo_pequeno
from .paridade import eh_impar


def valoracao_p_adica(p: int, n: int) -> int:
    """v_p(n): maior k tal que p^k divide n -- conta as divisões exatas
    por p até parar de dividir certo, uma a uma, nunca por logaritmo."""
    validar_natural(p, "p")
    validar_natural(n, "n")
    if n == 0:
        raise ValueError("valoração p-ádica não definida para n=0")
    if not eh_primo_pequeno(p):
        raise ValueError(f"{p} não é primo -- valoração exige base prima")
    contagem = 0
    resto = n
    while dividir_com_resto(resto, p)[1] == 0:
        resto = dividir_exato(resto, p)
        contagem += 1
    return contagem


def fator_com_valoracao_impar(n: int) -> int | None:
    """Menor primo p tal que v_p(n) é ímpar, ou `None` se todos os
    expoentes forem pares (isto é, n é quadrado perfeito ou n=1).
    """
    validar_natural(n, "n")
    if n < 2:
        return None
    for candidato in range(2, n + 1):
        if dividir_com_resto(n, candidato)[1] != 0:
            continue
        if not eh_primo_pequeno(candidato):
            continue
        if eh_impar(valoracao_p_adica(candidato, n)):
            return candidato
    return None


@dataclass(frozen=True, slots=True)
class ProvaIrracionalidadeRaizGeral:
    n: int
    fator_usado: int
    valoracao_do_fator: int
    conclusao: str
    valida: bool
    limite: str


def prova_raiz_n_irracional_geral(n: int) -> ProvaIrracionalidadeRaizGeral:
    """Certifica √n irracional para qualquer n que não seja quadrado
    perfeito, via um primo de valoração ímpar. Levanta `ValueError`
    quando `n` É quadrado perfeito (não existe primo assim) -- correto:
    √(quadrado perfeito) é racional (é o próprio inteiro), não há nada
    para provar irracional.
    """
    fator = fator_com_valoracao_impar(n)
    if fator is None:
        raise ValueError(
            f"{n} não tem primo de valoração ímpar -- é 1 ou quadrado perfeito, "
            "√n é racional (não há irracionalidade para certificar)"
        )
    v = valoracao_p_adica(fator, n)
    return ProvaIrracionalidadeRaizGeral(
        n=n,
        fator_usado=fator,
        valoracao_do_fator=v,
        conclusao=f"√{n} não é racional (via primo {fator}, v_{fator}({n})={v}, ímpar).",
        valida=eh_impar(v),
        limite=(
            "A prova usa a aditividade de v_p sob multiplicação, garantida pelo "
            "Teorema Fundamental da Aritmética (existência + unicidade da "
            "fatoração, Etapas 13/14) -- não é uma varredura de a,b (não "
            "precisaria, nem poderia: são infinitos). A contradição de "
            "paridade (par ≠ ímpar) é válida para qualquer a,b hipotético."
        ),
    )
