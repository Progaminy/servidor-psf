# PSF-IAminy — Marcador histórico 1079: período da dízima

## Construção pura

A expansão decimal (Etapa 1078) já distingue decimal exato de dízima
periódica (`terminou`), mas só sabia DIZER que o resto não zerou — não
onde exatamente o ciclo de dígitos começa a se repetir. Esta etapa fecha
isso: o resto de uma divisão nunca assume mais que `denominador` valores
distintos (0 até denominador-1). Pelo princípio da casa dos pombos, dentro
de no máximo `denominador` casas decimais, ou o resto chega a zero
(divisão termina) ou um resto JÁ VISTO se repete — e a partir da primeira
vez que um resto reaparece, a sequência de dígitos gerados também se
repete para sempre, porque a divisão só depende do resto atual.

```text
expansão decimal (Etapa 1078) -- gera um dígito e um resto novo por casa
→ guarda cada resto visto e em que casa apareceu
→ resto = 0: termina, não é dízima (devolve nada -- não é o caso desta etapa)
→ resto já visto antes: achou o ciclo -- a casa onde apareceu pela
  primeira vez marca o início do período; os dígitos entre essa casa e a
  casa atual são o período inteiro
→ a busca nunca passa de `denominador` casas -- não é um limite
  arbitrário escolhido à parte, é a própria contagem de restos possíveis
```

## Exemplo

- `1/3 = 0,(3)` — período `"3"`, sem dígitos antes (posição de início 0).
- `1/6 = 0,1(6)` — o `"1"` não repete; o período `"6"` começa na 2ª casa.
- `1/7 = 0,(142857)` — período de 6 dígitos, o máximo possível para
  denominador 7 (6 restos não nulos: 1..6).
- `1/17` — período de 16 dígitos, o máximo possível para denominador 17.

## Dependências permitidas

- expansao decimal

## Implementação

```text
matematica/divisao.py
```

`periodo_da_divisao`/`PeriodoDecimal` — busca limitada pelo próprio
denominador, guardando resto → casa num dicionário; devolve `None`
quando a divisão termina exatamente (não é dízima).

## Validação

```text
testes/test_periodo_decimal.py
```

## Estado

Período da dízima construído e testado: casos sem ante-período (1/3),
com ante-período (1/6) e com período no tamanho máximo possível para o
denominador (1/7, 1/17) — prova de que a busca não desiste antes do
limite que o próprio denominador garante. Divisão por zero continua
rejeitada explicitamente. O caso irracional (nenhum resto jamais se
repete porque não há denominador inteiro nenhum por trás — dízima sem
período) não é alcançável por esta construção, que parte sempre de
`numerador/denominador` inteiros; exigiria reais completos, mesma
fronteira que várias etapas 1000+ já deixam em aberto.
