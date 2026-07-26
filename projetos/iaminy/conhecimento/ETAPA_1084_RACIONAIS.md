# PSF-IAminy — Marcador histórico 1084: racionais

## Construção pura

Um racional é um par ordenado (numerador, denominador) — a mesma ideia
de "quociente puro" (Etapa 7), só que guardado sem executar a divisão,
para poder operar com frações que não fecham exatas. Igualdade não
compara numerador e denominador diretamente (frações diferentes podem
valer o mesmo, 1/2 = 2/4): compara por multiplicação cruzada.

```text
a/b == c/d  <=>  a×d == c×b        (multiplicação cruzada, nunca divisão)
a/b + c/d = (a×d + c×b) / (b×d)    (denominador comum por produto)
a/b × c/d = (a×c) / (b×d)          (numerador com numerador, denominador com denominador)
a/b ÷ c/d = a/b × d/c              (dividir é multiplicar pelo inverso)
simplificar(a/b) = (a÷mdc(a,b)) / (b÷mdc(a,b))     (MDC, Etapa 4)
```

Subtração usa a SUB truncada do núcleo sobre os numeradores cruzados —
só é a diferença verdadeira quando o primeiro racional é numericamente
maior; frações que dão diferença negativa exigem racionais assinados
(mesma lacuna já documentada para inteiros, Etapa 16 — fora do escopo
desta etapa, que trata só frações não negativas).

## Exemplo

- `1/2 == 4/8` (multiplicação cruzada: 1×8 == 4×2)
- `1/3 + 1/6 = 1/2` (via denominador comum, depois simplificado pelo MDC)
- `3/4 − 1/4 = 8/16` (não simplificado — simplificar é passo separado)
- `1/2 ÷ 1/4 = 4/2`, recíproco de `2/5` é `5/2`

## Dependências permitidas

- multiplicacao
- mdc puro

## Implementação

```text
nucleo/racionais.py
```

`RAC`/`NUM`/`DEN` (o par), `EQ_RAC`, `SOMA_RAC`, `SUB_RAC`, `MULT_RAC`,
`DIV_RAC`, `RECIPROCO_RAC`, `SIMPLIFICAR`.

## Validação

```text
testes/test_nucleo.py
```

## Estado

Racionais como pares ordenados construídos e testados: igualdade,
soma, subtração (só quando não negativa), multiplicação, divisão,
recíproco e simplificação via MDC — tudo verificado com exemplos
concretos, nunca aceito só pela álgebra. Racionais assinados (frações
que podem ser negativas) continuam em aberto, mesma fronteira que
inteiros relativos (Etapa 16) já documenta.
