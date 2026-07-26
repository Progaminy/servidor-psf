# PSF-IAminy — Marcador histórico 1078: expansão decimal

## Construção pura

A divisão (quociente e resto, Etapas 7 e 8) nasce os números decimais:
quando o resto não é zero, ele pode ser "transportado" para a casa
seguinte multiplicando por dez e repartindo de novo pelo mesmo divisor —
a mesma pergunta de quociente/resto, repetida uma casa decimal de cada
vez.

```text
quociente e resto (Etapas 7 e 8)
→ resto = 0: divisão termina, número é decimal exato (ex.: 12:5 = 2,4)
→ resto ≠ 0: multiplica o resto por dez, repete quociente/resto -- uma
  casa decimal nova a cada repetição
→ o resto nunca pode assumir mais que `divisor` valores distintos (0 até
  divisor-1) -- se a divisão nunca termina, o resto tem que repetir um
  valor já visto dentro desse limite, e a partir daí os dígitos gerados
  se repetem também: dízima periódica
```

A construção nunca finge terminar: se o resto não chega a zero dentro
das casas pedidas, o resultado é honestamente marcado como não
terminado (`terminou=False`), nunca arredondado em silêncio para parecer
exato.

## Exemplo

- `12:5 = 2,4` (resto zero na 1ª casa, termina)
- `1:3 = 0,333...` (resto sempre 1, dízima periódica de período 1)
- `2:3 = 0,666...` (mesma ideia, resto sempre 2)

## Dependências permitidas

- quociente puro
- resto e divisão euclidiana

## Implementação

```text
matematica/divisao.py
```

`expandir_decimal`/`ExpansaoDecimalPSF` — transporta o resto multiplicado
por dez e repete quociente/resto, casa a casa, controlando o número de
casas pedido e o modo (truncar/arredondar); `terminou` regista se o resto
chegou a zero.

## Validação

```text
testes/test_motores_dominio_comum.py
```

## Estado

Expansão decimal construída por transporte repetido do resto — decimal
exato quando o resto zera, dízima periódica quando não (testado com 1:3,
2:3, com controle explícito de casas e modo de arredondamento, via
`MotorMatematica.calcular`). Detecção explícita de ONDE o período começa
a repetir (marcar o ciclo de dígitos, não só saber que ele existe) fica
na Etapa 1079, logo a seguir. O caso irracional (nenhum resto jamais se
repete, dízima sem período — exige reais completos) continua em aberto,
fora do alcance de uma construção que parte de numerador/denominador
inteiros.
