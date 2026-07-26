# PSF-IAminy — Marcador histórico 1090: Teorema de Pitágoras

## Construção pura

`nucleo/trigonometria_natural.py` (Etapa 1033) já usa a relação
a²+b²=h² para certificar razões trigonométricas -- mas exige os três
lados já prontos (`TrianguloRetangulo.__post_init__` só VALIDA a
igualdade, com h inteiro; nunca RESOLVE h a partir de a,b). Isso cobre
ternos pitagóricos (3-4-5, 6-8-10...), mas não o caso comum de sala de
aula: catetos pequenos quaisquer, hipotenusa em geral irracional.

Esta etapa fecha a pergunta que faltava: dados os catetos a e b,
constrói h² = a²+b² (soma de quadrados, Etapa 1076 de potenciação mais
adição) e resolve h por raiz quadrada dígito a dígito (Etapa 1089).

```text
a, b catetos conhecidos
h² = a² + b²                      (Pitágoras)
h² é quadrado perfeito? -> h = raiz inteira exata
h² não é quadrado perfeito?       (Etapas 1080-1083: acontece sempre
                                    que h² tem algum primo com expoente
                                    ímpar na fatoração)
  -> h ≈ raiz_quadrada_por_digitos(h², casas), truncado, honesto sobre
     não ser exato (resto final ≠ 0)
```

## Exemplo

- Catetos 3 e 4: h² = 9+16 = 25, h = 5 (exato -- terno pitagórico).
- Catetos 2 e 3: h² = 4+9 = 13, h ≈ 3,6055 (4 casas, truncado) -- o
  exemplo concreto que expôs a lacuna da Etapa 1085 e motivou a
  construção da Etapa 1089.

## Dependências permitidas

- raiz quadrada por dígitos
- potenciação por repetição

## Implementação

```text
matematica/pitagoras.py
```

`hipotenusa`/`HipotenusaPSF` -- devolve os quadrados, a soma, a raiz
completa (Etapa 1089, com `exato` e `passos` próprios) e uma narrativa
`passos` de três linhas (fórmula, substituição, resultado).

Regra 17: com `conferir_com_calculadora=True`, tenta comparar o
resultado (já construído sozinho) contra `cao_de_caca/PSF-Calculadora`
(`MotorPitagoras`, `decimal.Decimal.sqrt()`), guardando o veredito em
`conferencia_cao_de_caca` (`None` quando o cão de caça está ausente
desta máquina). Por omissão a conferência não é pedida e o campo fica
`None` -- em nenhum dos dois casos isso muda `decimal`/`exata`/`passos`,
que vêm sempre só da construção PSF.

## Validação

```text
testes/test_pitagoras.py
```

Cobre terno pitagórico exato (3,4,5), o caso irracional do exemplo
original (2,3 -> h≈3,6055) e catetos inválidos (zero/negativo).

## Estado

Teorema de Pitágoras materializado para QUALQUER par de catetos
naturais positivos, exato ou aproximado, sem lista de casos especiais
-- construído sobre a Etapa 1089, que por sua vez fecha a lacuna de
desempenho documentada na Etapa 1085 (Regra 16).
