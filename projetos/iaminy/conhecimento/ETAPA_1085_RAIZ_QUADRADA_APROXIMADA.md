# PSF-IAminy — Marcador histórico 1085: raiz quadrada aproximada

## Construção pura

A inversa da potência (Etapa 1077) busca a base exata: encontra `a`
inteiro tal que `a²=c`, e declara honestamente quando não existe (√2 não
tem base inteira exata — é irracional, Etapas 1080-1083). Esta etapa
constrói o que fazer QUANDO não existe base exata: aproximar por
frações (Etapa 1084), cada vez mais próximas, sem nunca usar `math.sqrt`
nem qualquer aproximação nativa.

```text
Newton-Raphson sobre racionais exatos:
x0 = piso(√alvo)                          (chute inicial, por busca barata)
x_(n+1) = (x_n + alvo/x_n) / 2            (média entre o chute e alvo/chute)
```

Cada passo aproxima melhor: se `x_n >= √alvo`, então `alvo/x_n <= √alvo`,
e a média fica mais perto da raiz verdadeira que `x_n` estava — a mesma
ideia de encaixar `√alvo` entre dois racionais cada vez mais próximos
(compare com "ponte racionais reais", Etapa 1034, que faz o encaixe de
um jeito mais geral).

## Exemplo

- `√2 ≈ 577/408 ≈ 1,414` (3 iterações de Newton, exato em racionais)
- `√3 ≈ 1,732`, `√5 ≈ 2,236`, `√8 ≈ 2,828`, `√10 ≈ 3,162`, `√11 ≈ 3,317`

## Dependências permitidas

- racionais
- inversa da potencia

## Implementação

```text
nucleo/reais.py
```

`RAIZ_PISO_PURA` (chute inicial por busca), `RAIZ_QUADRADA_RAC_N`
(Newton com número de iterações explícito), `RAIZ_QUADRADA_RAC` (atalho
com 3 iterações padrão).

## Validação

```text
testes/test_nucleo.py
```

## Estado

Aproximação de raiz quadrada por Newton-Raphson construída e testada
para alvo ∈ {2, 3, 5, 8, 9, 10, 11, 12, 20} — honesto sobre o alcance:
outros valores (6, 7, 13, 15, 17...) falham na mesma janela de tempo,
porque `SUB`/`DIV` sobre numerais unários custam O(n·m) quando os dois
racionais têm magnitude comparável (documentado em detalhe no próprio
módulo). Consertar isso de verdade exigiria representação posicional
(binária) em vez de unária — projeto à parte, não ajuste local. Sem
essa fronteira, a lei geradora mais geral (Etapa 1035, sobre
`reais_intervalos_naturais.py`) já cobre o caso completo sem esse
limite de desempenho.
