# PSF-IAminy — Marcador histórico 1087: verificação de indução

## Construção pura

Indução matemática prova P(n) para TODO n mostrando P(0) e "P(k) implica
P(k+1)" para todo k — um argumento válido para infinitos casos de uma
vez. Um PSF finito não pode EXECUTAR essa prova por busca (buscar
"para todo k" percorrendo infinitos k nunca termina); o que se pode
honestamente construir é um VERIFICADOR limitado: confirma P(0) e
confirma "P(k) implica P(k+1)" para todo k dentro de um limite finito —
evidência computacional forte, nunca uma prova universal fingida.

```text
verificar_inducao(P, limite):
  P(0) vale?
  para cada k em [0, limite): P(k) implica P(k+1)?
  -- ambos verdadeiros: evidência de que P vale em [0, limite]
  -- qualquer falha: P não é universal (contraexemplo real, não suposto)
```

Isto é diferente de "provar por indução" (que exigiria verificar a
implicação simbolicamente, para k genérico, não instância a instância) —
por isso é chamado verificador, não provador, e o limite testado faz
parte honesta do resultado, nunca escondido.

## Exemplo

- P(n): "Σ_{i=0}^{n} i = n(n+1)/2" (soma de Gauss) — verificado para
  todo k em [0, 50]: P(0) vale (0=0), e P(k)⟹P(k+1) vale em cada passo.

## Dependências permitidas

- logica booleana
- somatorio e produtorio

## Implementação

```text
nucleo/calculo_discreto.py
```

`VERIFICAR_INDUCAO` (confirma P(0) e a implicação P(k)⟹P(k+1) para todo
k num intervalo finito, via `INTERVALO` e `IMPLICA` já construídos).

## Validação

```text
testes/test_nucleo.py
```

## Estado

Verificador de indução construído e testado com a soma de Gauss até
limite 50 — honesto sobre ser evidência computacional num alcance
finito, nunca uma prova universal simbólica (essa exigiria manipular
P(k) algebricamente para k genérico, fora do escopo de busca).
