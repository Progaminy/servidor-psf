# PSF-IAminy — Marcador histórico 1083: irracionalidade de raiz geral

## Construção pura

As Etapas 1080-1082 cobriram casos parciais: só √2 (paridade), só √p
primo (lema de Euclides), só compostos com um fator de multiplicidade 1
(12, 18, 24...) — mas não 8=2³, 16=2⁴, 32=2⁵, onde nenhum primo aparece
exatamente uma vez. Esta etapa fecha a generalização completa: √n é
irracional para QUALQUER n que não seja quadrado perfeito.

A peça que faltava é a valoração p-ádica: v_p(n), a maior potência de p
que divide n. Pelo Teorema Fundamental da Aritmética — existência
(Etapa 13) e unicidade via lema de Euclides (tfa unicidade) —, a
fatoração em primos é única, e por isso v_p é bem definida e ADITIVA:
v_p(x·y) = v_p(x) + v_p(y).

```text
n não é quadrado perfeito
  <=> algum primo p divide n com expoente ÍMPAR (v_p(n) ímpar) --
      se todo expoente fosse par, n = (produto de p^(expoente/2))²

suponha a,b naturais, b>0, a²=n·b² (nem precisa de mdc(a,b)=1 aqui)
→ v_p(a²) = 2·v_p(a) -- sempre par, qualquer que seja a
→ v_p(n·b²) = v_p(n) + 2·v_p(b) -- mesma paridade de v_p(n), que é ímpar
→ a² = n·b² exige v_p(a²) = v_p(n·b²), ou seja par = ímpar -- impossível
→ nenhum a,b satisfaz a²=n·b² -- √n não é racional
```

Mais simples que a Etapa 1082 (nem precisa de mdc(a,b)=1 — a contradição
de paridade do expoente já basta sozinha), e cobre TODO n que não é
quadrado perfeito, incluindo os casos que a Etapa 1082 recusava.

## Exemplo

- `n=8=2³`: v_2(8)=3, ímpar — √8 irracional (a Etapa 1082 recusava este
  caso, por não ter fator de multiplicidade 1).
- `n=16=2⁴`: v_2(16)=4, par — nenhum primo de valoração ímpar, e de
  facto 16=4² é quadrado perfeito, corretamente fora do alcance.
- `n=50=2·5²`: v_2(50)=1, ímpar — √50 irracional via o primo 2, mesmo
  com 5 aparecendo ao quadrado.

## Dependências permitidas

- tfa unicidade

## Implementação

```text
nucleo/irracionalidade_raiz_geral.py
```

`valoracao_p_adica` (conta a multiplicidade), `fator_com_valoracao_impar`
(busca o primo certo) e `prova_raiz_n_irracional_geral` (o certificado).

## Validação

```text
testes/test_irracionalidade_raiz_geral.py
```

## Estado

Irracionalidade de √n construída e certificada para todo n que não é
quadrado perfeito — caso geral fechado, testado explicitamente incluindo
os casos que as Etapas 1080-1082 não cobriam (8, 16, 24, 27, 32) e
confirmando corretamente que quadrados perfeitos (1, 4, 9, 16, 25, 36,
49) ficam fora (não há irracionalidade para certificar). Fecha o item
final do fluxo aritmético natural descrito pelo autor: contar → adição →
subtração → multiplicação → potenciação → raiz/log → divisibilidade →
MDC → negativos → quociente → resto → decimais → dízima periódica →
irracionais, do caso mais específico (√2) ao mais geral (qualquer não-
quadrado), sem nenhum salto não construído no meio.
