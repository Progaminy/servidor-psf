# PSF-IAminy — Marcador histórico 1080: irracionalidade de raiz de dois

## Construção pura

O rant original pedia o fim do fluxo aritmético: "os números decimais
nascem os números com dízima periódica, irracionais". A expansão decimal
(Etapa 1078) e o período da dízima (Etapa 1079) já mostraram que TODA
fração p/q gera decimal exato ou dízima periódica — nunca uma dízima
sem período. Por contraposição: um número cuja expansão decimal nunca
repete não pode ser fração nenhuma — é irracional. Esta etapa constrói o
primeiro exemplo certificado: √2.

A prova é a clássica de Euclides (Elementos, Livro X), sem aproximar √2
em nenhum momento:

```text
suponha p,q naturais, q>0, mdc(p,q)=1 (fração já reduzida), com p²=2q²
→ p² é par (é 2×q²)
→ p é par (lema: par ao quadrado é par, ímpar ao quadrado é ímpar --
  Etapa 1049, paridade)
→ p = 2k para algum natural k
→ 4k² = 2q² => q² = 2k² => q² é par => q é par (mesmo lema)
→ 2 divide p e 2 divide q => mdc(p,q) é par
→ contradiz mdc(p,q) = 1, assumido no início
→ a suposição não pode ser satisfeita por nenhum par real: não existe
  p,q assim -- √2 não é racional
```

A prova não busca o par p,q — não pode (ele não existe), e não precisa:
mostra que a PRÓPRIA existência de um par satisfazendo as três condições
já força uma contradição, então nenhum par as satisfaz. Isto é diferente
de testar exaustivamente candidatos (que nunca terminaria); é uma
dedução finita, válida para qualquer p,q hipotético, apoiada num único
lema testado em código: `n par ⟺ n² par`.

## Exemplo

- Se `p/q = √2` em forma reduzida, `p²=2q²` — a prova mostra que isso
  força `mdc(p,q)` par, nunca `1`. Nenhum `p,q` concreto satisfaz as
  premissas — testável a partir de qualquer candidato: `mdc_por_retirada`
  nunca devolve `1` para um par que satisfizesse `p²=2q²`, porque tal par
  não existe.

## Dependências permitidas

- paridade

## Implementação

```text
nucleo/irracionalidade_raiz_de_dois.py
```

`quadrado_e_par_see_base_e_par` (o lema, testado por alcance finito real
— custo O(valor) do predecessor nativo, mesma fronteira já documentada
no módulo de reais aproximados, torna alcance grande impraticável) e
`prova_raiz_de_dois_irracional` (o certificado, combinando o lema
verificado com a dedução da Construção pura acima).

## Validação

```text
testes/test_irracionalidade_raiz_de_dois.py
```

## Estado

Irracionalidade de √2 construída e certificada pela prova clássica de
Euclides, apoiada num lema de paridade testado em código (não decorado)
e numa dedução finita (não uma busca infinita). Primeiro número
irracional certificado nesta linha — generalizar para "√n irracional
quando n não é quadrado perfeito" e ligar à completude dos reais (Etapas
1034-1068, "lei geradora de aproximação real") continuam como próximo
alvo.
