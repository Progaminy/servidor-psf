# PSF-IAminy — Marcador histórico 1088: números harmônicos

## Construção pura

O número harmônico H(n) soma os inversos dos primeiros n naturais —
usa racionais (Etapa 1084) exatos, nunca aproximação decimal:

```text
H(0) = 0
H(n) = 1/n + H(n-1)          (simplificado a cada passo pelo MDC)
```

Simplificar a cada passo (não só no final) importa de verdade: sem
isso, o denominador de H(n) cresce por multiplicação cruzada bruta (um
mmc(1..n) não reduzido) e ultrapassa depressa o que a reconstrução
unária processa — mesma lição já registada em "raiz quadrada
aproximada" (Etapa 1085) sobre custo de racionais não simplificados.

## Exemplo

- `H(5) = 1 + 1/2 + 1/3 + 1/4 + 1/5 = 137/60`

## Dependências permitidas

- racionais

## Implementação

```text
nucleo/harmonicos.py
```

`HARMONICO` (recursão sobre `RAC`/`SOMA_RAC`/`SIMPLIFICAR`, já
construídos).

## Validação

```text
testes/test_nucleo.py
```

## Estado

Números harmônicos construídos e testados como racional exato — H(5) =
137/60 confirmado. Escopo testado honesto: n=1..5 rápido, n=6,7 completam
devagar (5-7s), n>=8 não verificado — mesmo teto de desempenho do núcleo
unário já documentado em várias outras etapas (custo O(valor) de
SUB/MOD sobre racionais de magnitude crescente).
