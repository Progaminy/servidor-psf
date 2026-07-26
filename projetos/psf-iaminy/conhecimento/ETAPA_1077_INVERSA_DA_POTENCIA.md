# PSF-IAminy — Marcador histórico 1077: raiz e logaritmo como a inversa da potência

## Construção pura

Potenciação (Etapa 1076) fecha a caixa `{base, expoente, potência}`:
dados `base` e `expoente`, `POT` calcula `potência`. Do mesmo jeito que a
adição abre a pergunta inversa de onde nasce a subtração ("que número
somado a 3 dá 5?", Etapa 1073), a potenciação abre DUAS perguntas
inversas — uma para cada lado que falta na mesma caixa:

```text
⟦base, expoente⟧ = potência              (potenciação — dados base e expoente, acha potência)
⟦   ?, expoente⟧ = potência  ->  base     (radiciação: acha a base que falta)
⟦base,    ?    ⟧ = potência  ->  expoente (logaritmo: acha o expoente que falta)
```

As duas buscas percorrem os mesmos candidatos que `POT` já usa (0, 1, 2,
...), testando `POT(candidato)(b) = c` (radiciação) ou
`POT(a)(candidato) = c` (logaritmo) a cada passo, parando no primeiro que
bater ou ao ultrapassar `c` (não existe solução inteira exata nesse caso —
honesto, nunca aproxima o que deveria ser exato). Não são duas construções
separadas: são a MESMA busca por potência, aplicada à posição que falta —
por isso vivem juntas nesta etapa, não uma para "radiciação" e outra para
"logaritmo" espalhadas em documentos diferentes.

## Exemplo

- `⟦2, 3⟧ = 8` (potenciação: 2³=8)
- `⟦?, 3⟧ = 8 → 2` (radiciação: raiz cúbica de 8 é 2)
- `⟦2, ?⟧ = 8 → 3` (logaritmo: log₂8 = 3)
- `⟦?, 2⟧ = 49 → 7` e `⟦3, ?⟧ = 81 → 4` — a mesma busca, lado que falta muda.

## Dependências permitidas

- potenciação por repetição

## Implementação

```text
nucleo/inversa_potencia.py
caixa.py
```

`INV_BASE`/`INV_EXPO` fazem a busca pura sobre `POT`, `IGUAL`, `MAIOR` e
`Y` (recursão via ponto fixo) — sem `math.sqrt`, `math.log` ou qualquer
outra dependência externa. `caixa()` expõe as três portas de entrada
(potenciação, radiciação, logaritmo) como uma função só, em `int` nativo
do Python, por cima das primitivas.

## Validação

```text
testes/test_nucleo.py
```

## Estado

Radiciação e logaritmo exatos construídos como busca inversa sobre a
mesma potenciação (Etapa 1076), nunca como duas ideias separadas — fecha
o pedido do autor de unir os dois cálculos numa única forma de
representar, sem precisar de símbolo de raiz ou de log distintos. Cobre
o caso exato (existe candidato inteiro que bate) para expoente qualquer.

Correção de honestidade (Regra 16): o caso `⟦?, 2⟧` (raiz quadrada) do
"caso geral" citado aqui como aberto já FECHOU — `raiz_quadrada_por_
digitos` (Etapa 1089) resolve exato-ou-aproximado para essa posição
específica da caixa, sem lista de alvos verificados. O que continua
genuinamente aberto é mais estreito: expoente diferente de 2 (raiz
cúbica, quarta, ...) sem candidato inteiro exato, e base/expoente não
inteiros em qualquer posição — nenhum dos dois tem construção PSF ainda.
