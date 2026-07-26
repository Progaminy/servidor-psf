"""Irracionalidade de √p para qualquer primo p — generaliza a Etapa 1080.

A Etapa 1080 provou √2 irracional usando paridade ("n par ⟺ n² par").
Paridade é exatamente a instância p=2 de um fato mais geral: o lema de
Euclides (Etapa 18) — se p é primo e p | a·b, então p | a ou p | b.
Tomando a=b=n: se p é primo e p | n², então p | n. Esta etapa generaliza
a mesma descida por contradição para QUALQUER primo p, trocando
"par/ímpar" por "múltiplo de p/não múltiplo de p":

  suponha a,b naturais, b>0, mdc(a,b)=1, a²=p·b² (isto é, √p=a/b reduzida)
  → a² é múltiplo de p (é p·b²)
  → a é múltiplo de p (lema acima, especializado a a=b=a: p|a·a ⟹ p|a)
  → a = p·k para algum natural k
  → p²k² = p·b² ⟹ p·k² = b² ⟹ b² é múltiplo de p ⟹ b é múltiplo de p
  → p divide a e p divide b ⟹ mdc(a,b) é múltiplo de p ⟹ mdc(a,b) ≥ p
  → contradiz mdc(a,b) = 1 assumido

Mesmo formato da Etapa 1080 (não busca o par a,b — mostra que a
suposição se contradiz sozinha), só o "2" virou "p" genérico.
"""
from __future__ import annotations

from dataclasses import dataclass

from .aritmetica_escolar_nativa import dividir_com_resto, multiplicar, validar_natural


def eh_primo_pequeno(n: int) -> bool:
    """Primalidade por divisão experimental — só para primos pequenos
    (o alcance desta etapa: 2, 3, 5, 7, 11, 13, ...), não uma construção
    de primalidade geral (essa já existe em `nucleo/primalidade_pura.py`,
    camada pura separada). Divide por todo d de 2 até n-1; ineficiente de
    propósito simples, adequado só ao tamanho pequeno que esta prova usa.
    """
    validar_natural(n, "n")
    if n < 2:
        return False
    for d in range(2, n):
        if dividir_com_resto(n, d)[1] == 0:
            return False
    return True


def primo_divide_quadrado_implica_primo_divide_base(p: int, n: int) -> bool:
    """p primo, p | n² ⟹ p | n — testado por instância, não decorado.

    Instância do lema de Euclides (Etapa 18) com a=b=n: p | n·n implica
    p | n ou p | n, ou seja p | n sempre que p | n². Verificado calculando
    o quadrado e os dois restos de verdade — devolve `True` quando a
    implicação se sustenta para este p,n (o caso interessante é quando
    p | n², que é quando a implicação tem conteúdo real).
    """
    validar_natural(p, "p")
    validar_natural(n, "n")
    n_quadrado = multiplicar(n, n)
    p_divide_quadrado = dividir_com_resto(n_quadrado, p)[1] == 0
    if not p_divide_quadrado:
        return True  # premissa falsa -- implicação vale por vacuidade
    return dividir_com_resto(n, p)[1] == 0


@dataclass(frozen=True, slots=True)
class ProvaIrracionalidadeRaizPrima:
    primo: int
    lema_verificado: bool
    alcance_verificacao: int
    conclusao: str
    valida: bool
    limite: str


def prova_raiz_prima_irracional(p: int, alcance_verificacao: int = 20) -> ProvaIrracionalidadeRaizPrima:
    """Certifica a irracionalidade de √p, p primo, generalizando a Etapa 1080.

    Exige p primo (verificado por `eh_primo_pequeno`, adequado ao alcance
    pequeno desta prova). Verifica o lema generalizado num alcance finito
    real. A partir do lema, a suposição a²=p·b² com mdc(a,b)=1 força a
    múltiplo de p, depois b múltiplo de p, logo mdc(a,b) múltiplo de p —
    contradição com mdc(a,b)=1, válida para qualquer a,b hipotético, não
    apenas os n testados aqui.
    """
    if not eh_primo_pequeno(p):
        raise ValueError(f"{p} não é primo -- esta prova exige p primo")
    lema = all(
        primo_divide_quadrado_implica_primo_divide_base(p, n)
        for n in range(1, alcance_verificacao + 1)
    )
    return ProvaIrracionalidadeRaizPrima(
        primo=p,
        lema_verificado=lema,
        alcance_verificacao=alcance_verificacao,
        conclusao=f"Não existe a,b natural com mdc(a,b)=1 e a²={p}·b² -- √{p} não é racional.",
        valida=lema,
        limite=(
            "O lema é verificado neste alcance, não por busca infinita -- a "
            "prova de que vale para TODO n está no lema de Euclides (Etapa "
            "18), não nesta varredura. A dedução final (mdc múltiplo de p "
            "contradiz mdc=1) não depende de nenhum a,b concreto -- é isso, "
            "não a varredura, que prova a irracionalidade."
        ),
    )
