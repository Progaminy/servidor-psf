# PSF-IAminy — Marcador histórico 1081: irracionalidade de raiz de primo

## Construção pura

A Etapa 1080 provou √2 irracional usando paridade ("n par ⟺ n² par").
Paridade é exatamente a instância p=2 de um fato mais geral: o lema de
Euclides (Etapa 18) — se p é primo e p divide a·b, então p divide a ou p
divide b. Tomando a=b=n: se p é primo e p divide n², então p divide n.
Esta etapa generaliza a mesma descida por contradição para QUALQUER
primo p, trocando "par/ímpar" por "múltiplo de p/não múltiplo de p":

```text
suponha a,b naturais, b>0, mdc(a,b)=1, a²=p·b² (isto é, √p=a/b reduzida)
→ a² é múltiplo de p (é p·b²)
→ a é múltiplo de p (lema de Euclides, especializado a a=b=a)
→ a = p·k para algum natural k
→ p²k² = p·b² => p·k² = b² => b² é múltiplo de p => b é múltiplo de p
→ p divide a e p divide b => mdc(a,b) é múltiplo de p => mdc(a,b) >= p
→ contradiz mdc(a,b) = 1, assumido no início
→ nenhum par real satisfaz as premissas -- √p não é racional
```

Mesmo formato da Etapa 1080 (não busca o par a,b — mostra que a própria
suposição se contradiz), só o "2" virou "p" genérico. Cobre √2, √3, √5,
√7, √11, √13, ... — todo primo — num único argumento parametrizado, sem
repetir a prova primo a primo.

## Exemplo

- `p=3`: se `a/b=√3` reduzida, `a²=3b²` força `a` múltiplo de 3, depois
  `b` múltiplo de 3, logo `mdc(a,b)` múltiplo de 3 — contradiz mdc=1.
- `p=7`: mesmo argumento, "múltiplo de 3" vira "múltiplo de 7" — nenhum
  passo da dedução depende de qual primo é, só de que é primo.

## Dependências permitidas

- lema de euclides

## Implementação

```text
nucleo/irracionalidade_raiz_prima.py
```

`primo_divide_quadrado_implica_primo_divide_base` (o lema generalizado,
testado por instância para vários primos) e `prova_raiz_prima_irracional`
(o certificado, generalizando `prova_raiz_de_dois_irracional` da Etapa
1080 para qualquer primo p verificado por `eh_primo_pequeno`).

## Validação

```text
testes/test_irracionalidade_raiz_prima.py
```

## Estado

Irracionalidade de √p construída e certificada para qualquer primo p
(testado explicitamente com 2, 3, 5, 7, 11, 13), generalizando a Etapa
1080 (que cobria só p=2, via paridade) através do lema de Euclides.
Cobre só primos — √4 (=2, racional) e √p² em geral ficam corretamente
fora, e √n para n composto livre de quadrados (como √6, √10, √15) ainda
não está coberto por este argumento direto (precisaria decompor n em
fatores primos e aplicar o lema a cada um) — próximo alvo natural, se
quiser generalizar mais.
