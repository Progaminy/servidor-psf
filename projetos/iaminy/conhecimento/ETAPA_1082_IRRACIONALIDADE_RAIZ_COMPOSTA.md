# PSF-IAminy — Marcador histórico 1082: irracionalidade de raiz de composto

## Construção pura

A Etapa 1081 provou √p irracional só para p primo. Esta etapa nota que a
mesma descida funciona sempre que n tem AO MENOS UM fator primo p que
aparece exatamente uma vez em n (isto é, n = p·m com p∤m — "multiplicidade
1"), mesmo que n não seja primo nem livre de quadrados por completo:

```text
suponha a,b naturais, b>0, mdc(a,b)=1, a²=n·b², n=p·m com p primo, p∤m
→ a² é múltiplo de p (é n·b² = p·m·b²)
→ a é múltiplo de p (lema de Euclides, Etapa 18, aplicado a k=a)
→ a = p·k para algum natural k
→ p²k² = p·m·b² => p·k² = m·b²
→ p | m·b² (é p·k², múltiplo de p) e p∤m => p | b² (lema de Euclides:
  p primo, p∤m, p|m·b² => p|b², já que p não pode "vir" do fator m)
→ b é múltiplo de p (mesmo lema, aplicado a k=b)
→ p divide a e p divide b => mdc(a,b) é múltiplo de p => mdc(a,b) >= p
→ contradiz mdc(a,b) = 1, assumido no início
```

Cobre todo n com um fator de multiplicidade 1 (todo composto squarefree,
mais muitos outros: 12=2²·3 cobre via p=3, 18=2·3² via p=2, 24=2³·3 via
p=3). NÃO cobre n onde nenhum primo tem multiplicidade exatamente 1
(4=2², 8=2³, 9=3², 16=2⁴ — nestes, todo fator aparece 0, 2, 3+ vezes sem
nenhum "exatamente 1"); esses exigiriam o caso geral por valoração
p-ádica (o expoente do primo, não só "aparece uma vez").

## Exemplo

- `n=6=2·3`: fator 2 (multiplicidade 1) — √6 irracional.
- `n=12=2²·3`: fator 3, não 2 (2 tem multiplicidade 2 em 12) — √12
  irracional pelo mesmo argumento, usando o fator certo.
- `n=8=2³`: nenhum fator de multiplicidade 1 — fora do alcance deste
  argumento (√8=2√2 é irracional de qualquer forma, mas por outro
  caminho: reduzir 8=4·2 e usar a Etapa 1081 direto sobre o primo 2,
  não este argumento).

## Dependências permitidas

- irracionalidade raiz prima

## Implementação

```text
nucleo/irracionalidade_raiz_composta.py
```

`fator_multiplicidade_um` (busca o primo certo) e `prova_raiz_n_irracional`
(o certificado, reaproveitando o lema já verificado na Etapa 1081).

## Validação

```text
testes/test_irracionalidade_raiz_composta.py
```

## Estado

Irracionalidade construída e certificada para todo n com um fator de
multiplicidade 1 (testado com 6, 10, 12, 14, 15, 18, 20, 21, 24).
Explicitamente recusa (levanta erro, não finge cobrir) n=1, quadrados
perfeitos (4, 9) e potências puras de um só primo sem multiplicidade 1
(8, 16) — esses continuam como próximo alvo, exigindo o argumento geral
por valoração p-ádica.
