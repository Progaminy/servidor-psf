"""Irracionalidade de √2 — prova clássica de Euclides (Elementos, Livro X).

Não aproxima √2 em nenhum momento (compare com `nucleo/reais.py`, que
aproxima por Newton-Raphson — pergunta diferente). Aqui a pergunta é:
existe algum par de naturais p,q, com q>0 e mdc(p,q)=1 (fração já
reduzida — toda fração reduz a essa forma via `mdc_por_retirada`), tal
que p²=2q²? Se existisse, p/q seria exatamente √2, e √2 seria racional.

A prova não busca esse par — não pode, e não precisa: mostra que
QUALQUER par hipotético que satisfizesse as três condições (q>0,
mdc(p,q)=1, p²=2q²) seria forçado, pela álgebra, a ter mdc(p,q) par —
contradizendo mdc(p,q)=1 assumido. Uma suposição que se contradiz não
pode ser satisfeita por nenhum par real: não existe p,q assim, logo √2
não é racional.

  p²=2q² => p² é par (é 2×q²)
         => p é par (lema: par ao quadrado é par, ímpar ao quadrado é ímpar)
         => p = 2k para algum natural k
         => 4k² = 2q² => q² = 2k² => q² é par => q é par (mesmo lema)
         => 2 divide p e 2 divide q => mdc(p,q) é par
         => contradiz mdc(p,q) = 1 assumido.

Apoia-se num único lema, testado aqui e nunca aceito só pela álgebra: n é
par se e somente se n² é par (`nucleo/paridade.py`, Etapa 1049).

Nota de desempenho, mesma classe de `nucleo/reais.py`: `predecessor` (e
por isso `subtrair`, `dividir_com_resto`, `eh_par`) é O(valor) nesta
reconstrução unária nativa — testar o lema para n muito grande fica caro
rápido (`eh_par(900)` já mede ~0,13s medido). O alcance de verificação
por isso é pequeno de propósito, não por preguiça — a prova de que o
lema vale para TODO n está na álgebra do texto acima, não na varredura.
"""
from __future__ import annotations

from dataclasses import dataclass

from .aritmetica_escolar_nativa import multiplicar, validar_natural
from .paridade import eh_par


def quadrado_e_par_see_base_e_par(n: int) -> bool:
    """n par <=> n² par — testado, não decorado.

    Par ao quadrado é par: (2k)²=4k², múltiplo de 2. Ímpar ao quadrado é
    ímpar: (2k+1)²=4k²+4k+1=2(2k²+2k)+1, um par mais um. Confere
    calculando o quadrado de verdade, comparando as duas paridades.
    """
    validar_natural(n, "n")
    return eh_par(n) == eh_par(multiplicar(n, n))


@dataclass(frozen=True, slots=True)
class ProvaIrracionalidadeRaizDeDois:
    lema_paridade_verificado: bool
    alcance_verificacao: int
    conclusao: str
    valida: bool
    limite: str


def prova_raiz_de_dois_irracional(alcance_verificacao: int = 20) -> ProvaIrracionalidadeRaizDeDois:
    """Certifica a irracionalidade de √2 pela prova de Euclides.

    Verifica o lema de paridade num alcance finito real (nunca aceito só
    pela álgebra). A partir do lema verificado, a suposição p²=2q² com
    mdc(p,q)=1 força p par, depois q par, logo mdc(p,q) par — contradição
    com mdc(p,q)=1, válida para QUALQUER p,q hipotético (a dedução usa só
    o lema e propriedades de mdc, nunca um valor concreto de p,q), não
    apenas os n testados aqui.
    """
    lema = all(quadrado_e_par_see_base_e_par(n) for n in range(alcance_verificacao))
    return ProvaIrracionalidadeRaizDeDois(
        lema_paridade_verificado=lema,
        alcance_verificacao=alcance_verificacao,
        conclusao="Não existe p,q natural com mdc(p,q)=1 e p²=2q² -- √2 não é racional.",
        valida=lema,
        limite=(
            "O lema de paridade é verificado neste alcance, não por busca "
            "infinita -- a prova de que vale para TODO n está na álgebra do "
            "docstring do módulo, não nesta varredura (custo O(valor) do "
            "predecessor nativo torna alcance grande impraticável, mesma "
            "fronteira documentada em nucleo/reais.py). A dedução final "
            "(mdc par contradiz mdc=1) não depende de nenhum p,q concreto -- "
            "é isso, não a varredura, que prova a irracionalidade."
        ),
    )
