# PSF-IAminy — Marcador histórico 1086: somatório e produtório

## Construção pura

Σ e Π são só nomes para "repetir adição/multiplicação sobre um
intervalo", em vez de uma escrita nova: percorrem `[a,b]` acumulando
com a operação já construída, começando do elemento neutro certo (zero
para soma, um para produto — mesma escolha que a potenciação, Etapa
1076, faz para `m^0`).

```text
Σ_{i=a}^{b} f(i) = percorrer [a,b], acumular com adição, começando de zero
Π_{i=a}^{b} f(i) = percorrer [a,b], acumular com multiplicação, começando de um
```

Fatorial (Etapa 40) já é um caso particular de produtório (f=identidade,
a=1); esta etapa não repete essa construção — generaliza para qualquer
`f`, o que fatorial sozinho não precisa mas somatório/produtório de
funções arbitrárias exige (ex.: soma de quadrados, produto de termos de
uma progressão).

## Exemplo

- `Σ_{i=1}^{10} i = 55` (soma de Gauss, os 10 primeiros naturais)
- `Π_{i=1}^{5} i = 120` (é 5!, fatorial como caso particular)

## Dependências permitidas

- adicao
- multiplicacao

## Implementação

```text
nucleo/calculo_discreto.py
```

`SOMATORIO`, `PRODUTORIO` (percorrem o intervalo com `INTERVALO`,
acumulando com `SOMA`/`MULT` já construídos).

## Validação

```text
testes/test_nucleo.py
```

## Estado

Somatório e produtório construídos e testados sobre função arbitrária
(soma de Gauss até 10, produtório até 5 batendo com 5!). `FATORIAL` e
`FIBONACCI` também vivem neste mesmo arquivo, mas são versões mais
antigas já substituídas por construções próprias e testadas à parte
(Etapas 40 e 50, em `nucleo/combinatoria_natural.py`) — não duplicadas
aqui, para manter a linha única.
