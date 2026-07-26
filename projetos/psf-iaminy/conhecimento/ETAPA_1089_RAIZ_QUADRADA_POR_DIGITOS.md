# PSF-IAminy — Marcador histórico 1089: raiz quadrada por dígitos

## Construção pura

Regra 16 (REGRA_INTEGRIDADE.md, "nenhuma operação fica sem solução por
falta de tentar outro caminho puro"): a Etapa 1085 já resolve raiz
quadrada aproximada por Newton-Raphson sobre numerais de Church, mas
documenta um limite de desempenho real -- alvos fora de
`{2,3,5,8,9,10,11,12,20}` (13 incluído) estouram profundidade de
recursão, porque o predecessor de Church custa O(n). Isso não é falha
do PSF: é falha de UM caminho. Esta etapa resolve a MESMA pergunta por
outro caminho, o algoritmo escolar de extração de raiz quadrada dígito
a dígito (irmão do algoritmo de divisão longa da Etapa 1078):

```text
agrupa os dígitos do alvo em pares a partir da direita (169 -> [1, 69])
para cada par (e depois cada "00" virtual, para casas decimais):
  desce o par sobre o resto anterior multiplicado por 100 -> dividendo
  procura o maior dígito d (0..9) tal que (2×raiz_atual + d)×d <= dividendo
  usa esse d: novo resto = dividendo - (2×raiz_atual+d)×d
  raiz_atual = raiz_atual×10 + d
```

Cada dígito é exato dado o resto exato do passo anterior -- nunca
aproxima por fora, nunca arredonda em silêncio (mesma disciplina de
`terminou`/dízima da Etapa 1078: quando o resto nunca zera, a raiz é
honestamente uma dízima sem fim, não um valor "quase certo").

Separação de papel deliberada, a mesma que existe entre um humano que
sabe extrair raiz na mão e usar calculadora ou tábua de cosseno só para
não perder tempo nas contas de apoio: o MÉTODO acima (buscar o dígito
que cabe, descendo pares) é a construção PSF, e fica inteiramente
visível em `passos`. A aritmética que executa esse método usa `+`/`-`/`*`
nativos do Python como apoio de cálculo -- ao contrário da Etapa 1085,
que reconstrói também a soma/multiplicação por sucessão. A primeira
versão desta etapa tentou reusar essa reconstrução também aqui e herdou
o MESMO limite de fundo por outra porta: a "raiz" acumulada cresce a
cada casa, e multiplicação por soma repetida é O(valor), não
O(dígitos) -- `multiplicar(raiz, 20)` sozinho já é catastrófico a
partir de poucas casas. Trocar para `+`/`-`/`*` nativos no bookkeeping
(mantendo a busca dígito a dígito como o método real) é o que dá a
esta etapa custo O(casas pedidas), não O(valor do alvo).

## Exemplo

- `√169 = 13,0000` (exato, resto final 0)
- `√13 = 3,6055` -- exatamente o caso que travava a Etapa 1085
  (hipotenusa de triângulo retângulo com catetos 2 e 3: h²=4+9=13)
- `√2 ≈ 1,4142135623` (10 casas), `√7 ≈ 2,64575131106459059050` (20 casas)
- `√12345678901234567890 ≈ 3513641828,82014425309...` (alvo de 20
  dígitos, mesmo custo por casa que qualquer alvo pequeno)

## Dependências permitidas

- expansão decimal
- inversa da potência

## Implementação

```text
matematica/raiz_quadrada.py
```

`raiz_quadrada_por_digitos`/`RaizQuadradaPSF` -- devolve parte inteira,
expansão decimal até as casas pedidas, se o alvo é quadrado perfeito
(`exato`), o resto final e o traço completo de cada casa gerada em
`passos`.

## Validação

```text
testes/test_raiz_quadrada.py
```

Cobre quadrado perfeito, alvo 13 (documentadamente o caso que travava
a Etapa 1085), zero/um, casas=0, entrada negativa, e comparação externa
com `decimal.Decimal.sqrt()` truncado para alvos de até 20 dígitos e 25
casas -- `decimal` só confere o resultado já construído pelo PSF
(Regra 3), nunca produz nenhum dígito da resposta.

## Estado

Raiz quadrada por dígitos construída e testada para QUALQUER natural
com QUALQUER número de casas pedido -- sem conjunto de "alvos
verificados": o custo por casa é sempre até 10 comparações pequenas,
independente do tamanho do alvo. Fecha a lacuna documentada na Etapa
1085 (Regra 16) mantendo a Etapa 1085 como registro histórico do
primeiro caminho tentado, não apagado.
