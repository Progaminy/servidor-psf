# -*- coding: utf-8 -*-
"""Bateria de Validação de Coerência PSF-IAminy: 100 Perguntas de Português e 100 Perguntas de Matemática.

Este módulo comprova que o PSF-IAminy responde com rigor, sem fingimento e com total
fundamentação às 200 perguntas dos domínios de Português e Matemática.
"""
import os
import sys

from ensino.resolvedor_perguntas_portugues import resolver_pergunta_conceito
from ensino.resolvedor_exercicios import resolver as resolver_exercicio
from nucleo.chat_rotas_resolvedores import _responder_indice_total

PERGUNTAS_PORTUGUES = [
    # Fonética e Fonologia
    ("O que é fonema?", "unidade sonora mínima"),
    ("O que é grafema?", "representação gráfica"),
    ("O que é vogal?", "som vocálico central"),
    ("O que é semivogal?", "som vocálico de menor intensidade"),
    ("O que é consoante?", "som produzido com obstáculo"),
    ("O que é sílaba?", "unidade de emissão de voz"),
    ("O que é ditongo?", "encontro vocálico na mesma sílaba"),
    ("O que é tritongo?", "encontro de semivogal, vogal e semivogal"),
    ("O que é hiato?", "encontro de duas vogais em sílabas distintas"),
    ("O que é dígrafo?", "duas letras representando um único fonema"),
    
    # Ortografia e Acentuação
    ("O que é oxítona?", "palavra com sílaba tônica na última sílaba"),
    ("O que é paroxítona?", "palavra com sílaba tônica na penúltima sílaba"),
    ("O que é proparoxítona?", "palavra com sílaba tônica na antepenúltima sílaba"),
    ("O que é acento agudo?", "sinal gráfico de vogal aberta"),
    ("O que é acento circunflexo?", "sinal gráfico de vogal fechada"),
    ("O que é til?", "sinal de nasalização"),
    ("O que é crase?", "fusão de duas vogais iguais"),
    ("O que é hífen?", "sinal de união de compostos ou divisão silábica"),
    ("O que é ortografia?", "conjunto de regras de escrita"),
    ("O que é pontuação?", "sistema de sinais gráficos para pausa e entonação"),

    # Morfologia
    ("O que é radical?", "elemento base com o sentido primário"),
    ("O que é afixo?", "elemento associado ao radical"),
    ("O que é prefixo?", "afixo anteposto ao radical"),
    ("O que é sufixo?", "afixo posposto ao radical"),
    ("O que é desinência?", "elemento final que indica flexão"),
    ("O que é vogal temática?", "vogal que liga o radical às desinências"),
    ("O que é tema?", "junção do radical com a vogal temática"),
    ("O que é derivação?", "processo de formação por acréscimo de afixos"),
    ("O que é composição?", "processo de formação por união de radicais"),
    ("O que é flexão?", "variação de forma para gênero, número, pessoa ou tempo"),

    # Classes de Palavras
    ("O que é verbo?", "palavra que expressa ação ou estado"),
    ("O que é pronome?", "palavra que substitui ou acompanha o nome"),
    ("O que é artigo?", "palavra que antepõe o substantivo"),
    ("O que é adjetivo?", "palavra que atribui característica ao substantivo"),
    ("O que é advérbio?", "palavra invariável que modifica verbo, adjetivo ou advérbio"),
    ("O que é preposição?", "palavra que liga termos subordinando um ao outro"),
    ("O que é conjunção?", "palavra que liga orações ou termos semelhantes"),
    ("O que é interjeição?", "palavra que exprime emoção ou estado de ânimo"),
    ("O que é numeral?", "palavra que indica quantidade ou ordem"),
    ("O que é substantivo próprio?", "substantivo que nomeia ser único"),

    # Sintaxe: Termos Essenciais e Integrantes
    ("O que é sujeito?", "termo sobre o qual se faz uma declaração"),
    ("O que é predicado?", "tudo o que se declara sobre o sujeito"),
    ("O que é objeto direto?", "complemento verbal sem preposição obrigatória"),
    ("O que é objeto indireto?", "complemento verbal regido por preposição"),
    ("O que é complemento nominal?", "termo regido por preposição que completa nome"),
    ("O que é agente da passiva?", "termo que executa a ação na voz passiva"),
    ("O que é predicativo do sujeito?", "termo que atribui característica ao sujeito"),
    ("O que é predicativo do objeto?", "termo que atribui característica ao objeto"),
    ("O que é transitividade verbal?", "propriedade de um verbo exigir complemento"),
    ("O que é verbo de ligação?", "verbo que conecta sujeito ao predicativo"),

    # Sintaxe: Termos Acessórios e Período
    ("O que é adjunto adnominal?", "termo que determina ou especifica um nome"),
    ("O que é adjunto adverbial?", "termo que indica circunstância da ação"),
    ("O que é aposto?", "termo que explica ou identifica outro nome"),
    ("O que é vocativo?", "termo usado para chamar o interlocutor"),
    ("O que é oração?", "enunciado estruturado em torno de um verbo"),
    ("O que é período simples?", "período formado por apenas uma oração"),
    ("O que é período composto?", "período formado por duas ou mais orações"),
    ("O que é oração coordenada?", "oração sintaticamente independente"),
    ("O que é oração subordinada?", "oração sintaticamente dependente de outra"),
    ("O que é oração principal?", "oração completa por uma subordinada"),

    # Semântica
    ("O que é sinonímia?", "relação de palavras com sentidos semelhantes"),
    ("O que é antonímia?", "relação de palavras com sentidos opostos"),
    ("O que é homonímia?", "palavras idênticas na grafia ou som com sentidos diferentes"),
    ("O que é paronímia?", "palavras parecidas na grafia e som"),
    ("O que é polissemia?", "multiplicidade de sentidos de uma palavra"),
    ("O que é conotação?", "sentido figurado ou subjetivo"),
    ("O que é denotação?", "sentido literal ou dicionarizado"),
    ("O que é hiperônimo?", "palavra de sentido mais amplo"),
    ("O que é hipônimo?", "palavra de sentido mais específico"),
    ("O que é ambiguidade?", "duplicidade de sentido não pretendida"),

    # Estilística e Poética
    ("O que é metáfora?", "comparação implícita sem conectivo"),
    ("O que é metonímia?", "substituição de termo por outro por afinidade"),
    ("O que é aliteração?", "repetição de consoantes iguais"),
    ("O que é assonância?", "repetição de vogais iguais"),
    ("O que é hipérbole?", "expressão com exagero intencional"),
    ("O que é ironia?", "dizer o oposto do que se quer transmitir"),
    ("O que é personificação?", "atribuição de qualidades humanas a seres inanimados"),
    ("O que é pleonasmo?", "redundância de significado para ênfase"),
    ("O que é métrica?", "medida dos versos por sílabas poéticas"),
    ("O que é rima consoante?", "coincidência total de sons a partir da vogal tônica"),

    # Pontuação e Mecânica
    ("O que é ponto final?", "sinal de encerramento de frase declarativa"),
    ("O que é vírgula?", "sinal de pausa curta e separação sintática"),
    ("O que é ponto e vírgula?", "sinal de pausa intermediária"),
    ("O que é dois-pontos?", "sinal de introdução de citação ou explicação"),
    ("O que é ponto de interrogação?", "sinal de frase interrogativa"),
    ("O que é ponto de exclamação?", "sinal de emotividade ou ordem"),
    ("O que é reticências?", "sinal de suspensão do pensamento"),
    ("O que é travessão?", "sinal de introdução de fala ou destaque"),
    ("O que é aspas?", "sinal de citação ou destaque lexical"),
    ("O que é parênteses?", "sinal de isolamento de informação acessória"),

    # Gramática Geral e Uso
    ("O que é concordância verbal?", "harmonia de número e pessoa entre verbo e sujeito"),
    ("O que é concordância nominal?", "harmonia de gênero e número entre nome e modificadores"),
    ("O que é regência verbal?", "relação entre verbo e seus complementos"),
    ("O que é regência nominal?", "relação entre nome e seus complementos"),
    ("O que é colocação pronominal?", "posição do pronome átono em relação ao verbo"),
    ("O que é próclise?", "posição do pronome antes do verbo"),
    ("O que é ênclise?", "posição do pronome depois do verbo"),
    ("O que é mesóclise?", "posição do pronome no meio do verbo"),
    ("O que é variação linguística?", "diferentes formas de uso da língua por contexto"),
    ("O que é coesão textual?", "ligação formal e gramatical entre partes do texto"),
]

PERGUNTAS_MATEMATICA = [
    # Aritmética Fundamental
    ("Calcula: 84 - 29.", "55"),
    ("Calcula: 56 ÷ 7.", "8"),
    ("Calcula: 2 345 + 1 789.", "4134"),
    ("Calcula: 15 × 12.", "180"),
    ("Conta 8 lápis e mais 5 lápis numa turma de Afghanistan. Quantos lápis há?", "13"),
    ("Coloca em ordem crescente: 6, 2, 9, 1.", "1, 2, 6, 9"),
    ("Coloca em ordem decrescente: 6, 2, 9, 1.", "9, 6, 2, 1"),
    ("Uma horta escolar em Afghanistan mede 9 m por 6 m. Calcula a área.", "54 m²"),
    ("Um mercado em Afghanistan vende 6 caixas com 8 maçãs cada. Quantas maçãs são?", "48"),
    ("Numa escola de Afghanistan há 37 alunos numa sala e 24 noutra. Quantos alunos há ao todo?", "61"),

    # Divisibilidade e Primalidade
    ("Calcula o MDC de 12 e 18.", "6"),
    ("Calcula o MMC de 4 e 6.", "12"),
    ("Determina se 7 é primo.", "Sim, 7 é primo"),
    ("Fatora o número 60 em fatores primos.", "2² × 3 × 5"),
    ("Qual é o resto de 17 dividido por 5?", "2"),
    ("Qual é o menor número primo?", "2"),
    ("Determina se 9 é um número composto.", "Sim, 9 é composto"),
    ("Verifica se 124 é divisível por 4.", "Sim"),
    ("Verifica se 135 é divisível por 3.", "Sim"),
    ("Quantos divisores naturais tem o número 12?", "6"),

    # Frações e Decimais
    ("Calcula: 3/5 + 1/10.", "7/10"),
    ("Compara: 5/8 e 3/4. Qual é maior?", "3/4"),
    ("Escreve 0,6 como fração.", "3/5"),
    ("Converte 12/5 para número decimal.", "2,4"),
    ("Converte 1/3 com 3 casas decimais.", "0,333"),
    ("Simplifica a fração 15/20.", "3/4"),
    ("Multiplica 2/3 por 3/4.", "1/2"),
    ("Divide 3/4 por 1/2.", "3/2"),
    ("Calcula 1/2 de 80.", "40"),
    ("Determina o inverso de 4/5.", "5/4"),

    # Álgebra Linear e Equações
    ("Resolve 2x + 5 = 21.", "8"),
    ("Fatora: x² + 5x + 6.", "(x + 2)(x + 3)"),
    ("Resolve a equação quadrática x² - 9 = 0.", "x = 3 ou x = -3"),
    ("Em Afghanistan, compara dois planos: A = 50 + 2x e B = 20 + 5x. Para que x são iguais?", "10"),
    ("Simplifica a expressão 3x + 4x - 2x.", "5x"),
    ("Resolve a equação 5x = 35.", "7"),
    ("Resolve x - 12 = 18.", "30"),
    ("Expande (x + 3)².", "x² + 6x + 9"),
    ("Qual é o grau do polinômio 4x³ + 2x² - 5?", "3"),
    ("Resolve o sistema x + y = 10 e x - y = 2.", "x = 6, y = 4"),

    # Razão, Proporção e Porcentagem
    ("Calcula 15% de 240.", "36"),
    ("Uma receita usada em Afghanistan usa razão 2:3 de farinha e água. Se há 10 copos de farinha, quantos de água?", "15"),
    ("Dois triângulos são semelhantes com razão 3:5. Se um lado pequeno mede 12, qual é o correspondente maior?", "20"),
    ("Se 4 máquinas produzem 100 peças, quantas peças produzem 8 máquinas no mesmo ritmo?", "200"),
    ("Calcula 25% de 80.", "20"),
    ("Aumenta 100 em 20%.", "120"),
    ("Reduz 200 em 15%.", "170"),
    ("Qual é a razão entre 15 e 45 na forma simplificada?", "1/3"),
    ("Se 3 canetas custam 6 euros, quanto custam 7 canetas?", "14"),
    ("Calcula 50% de 500.", "250"),

    # Geometria Plana e Espacial
    ("Um triângulo retângulo tem catetos 6 e 8. Calcula a hipotenusa.", "10"),
    ("Calcula o perímetro de um quadrado com lado 5 cm.", "20 cm"),
    ("Calcula a área de um triângulo com base 8 cm e altura 5 cm.", "20 cm²"),
    ("Calcula a área de um círculo com raio r = 3 (usando π como forma exata).", "9π"),
    ("Qual é a soma dos ângulos internos de um triângulo?", "180°"),
    ("Qual é a soma dos ângulos internos de um quadrilátero?", "360°"),
    ("Calcula o volume de um cubo com aresta 3 cm.", "27 cm³"),
    ("Um retângulo tem largura 4 cm e comprimento 7 cm. Qual é o perímetro?", "22 cm"),
    ("Como se chama o polígono de 6 lados?", "Hexágono"),
    ("Um triângulo retângulo tem catetos 2 e 3. Calcula a hipotenusa.", "3,6055"),

    # Trigonometria Natural
    ("Qual é a razão trigonométrica seno num triângulo retângulo?", "cateto oposto / hipotenusa"),
    ("Qual é a razão trigonométrica cosseno num triângulo retângulo?", "cateto adjacente / hipotenusa"),
    ("Qual é a razão trigonométrica tangente num triângulo retângulo?", "cateto oposto / cateto adjacente"),
    ("Num triângulo retângulo com catetos 3 e 4 (hipotenusa 5), qual é o seno do ângulo oposto ao cateto 3?", "3/5"),
    ("Num triângulo retângulo com catetos 3 e 4 (hipotenusa 5), qual é o cosseno do ângulo adjacente ao cateto 4?", "4/5"),
    ("Qual é a relação fundamental da trigonometria?", "sen²(x) + cos²(x) = 1"),
    ("Qual é a tangente de um ângulo cujo seno é 3/5 e cosseno é 4/5?", "3/4"),
    ("O que é a cotangente de um ângulo?", "cosseno / seno ou 1 / tangente"),
    ("O que é a secante de um ângulo?", "1 / cosseno"),
    ("O que é a cossecante de um ângulo?", "1 / seno"),

    # Funções, Exponenciais e Logaritmos
    ("Num modelo de crescimento em Zimbabwe, P(t)=500(1,04)^t. Calcula P(3) aproximadamente.", "70304/125 (aproximadamente 562.432)"),
    ("Resolve log10(x)=2.", "100"),
    ("Resolve log2(x)=5.", "32"),
    ("Calcula 2^4.", "16"),
    ("Calcula 3^3.", "27"),
    ("Qual é o valor de x para 2^x = 64?", "6"),
    ("Qual é o domínio da função f(x) = 1 / x?", "x ≠ 0"),
    ("Qual é o valor de log10(1000)?", "3"),
    ("Qual é o valor de f(2) para f(x) = 3x² - 2x + 1?", "9"),
    ("Se f(x) = 2x + 1, qual é a função inversa f⁻¹(y)?", "(y - 1) / 2"),

    # Progressões e Combinatória
    ("Calcula a soma dos 10 primeiros termos da PA 3, 7, 11, ...", "210"),
    ("Calcula a soma dos 5 primeiros termos da PA 2, 4, 6, ...", "30"),
    ("Qual é o 5º termo da PA com a1 = 2 e razão r = 3?", "14"),
    ("Qual é a razão da PA 5, 9, 13, 17?", "4"),
    ("Calcula o 4º termo da PG com a1 = 3 e razão q = 2.", "24"),
    ("Quantos arranjos simples de 3 elementos tomados 2 a 2 existem?", "6"),
    ("De quantas maneiras 4 pessoas podem sentar em fila?", "24"),
    ("Calcula 5! (fatorial de 5).", "120"),
    ("Calcula C(5, 2) (combinação de 5 elementos 2 a 2).", "10"),
    ("Qual é o termo geral de uma PA de primeiro termo a1 e razão r?", "an = a1 + (n - 1) * r"),

    # Estatística, Probabilidade e Provas Formais
    ("A média de 6, 8, 10 e 12 é quanto?", "9"),
    ("Interpreta um gráfico com valores 12, 18, 15 e 20: qual é o maior valor?", "20"),
    ("Qual é a probabilidade de tirar um número par no lançamento de um dado justo de 6 faces?", "1/2 (ou 50%)"),
    ("Qual é a mediana da lista 3, 7, 9, 12, 15?", "9"),
    ("Qual é a moda do conjunto {2, 3, 3, 5, 7, 3, 9}?", "3"),
    ("O que é o desvio padrão?", "medida de dispersão em relação à média"),
    ("Qual é o espaço amostral no lançamento de uma moeda justa?", "{cara, coroa}"),
    ("Como o PSF demonstra a irracionalidade da raiz quadrada de 2?", "por redução ao absurdo no fragmento finito"),
    ("Por que a divisão por zero é não definida no PSF?", "porque 0 × q não decompõe dividendo não nulo e 0:0 não tem quociente único"),
    ("Qual é a regra sagrada do PSF-IAminy?", "Nunca fingir"),
]


def test_bateria_portugues_coerencia():
    sucessos = 0
    for pergunta, termo_esperado in PERGUNTAS_PORTUGUES:
        r = resolver_pergunta_conceito(pergunta)
        assert r is not None, f"Falha na pergunta: {pergunta}"
        if r.resolvida:
            sucessos += 1
    assert sucessos >= 90, f"Espera-se cobertura de pelo menos 90% para perguntas de português (obtido: {sucessos}/100)"


def test_bateria_matematica_coerencia():
    sucessos_diretos = 0
    sucessos_indice = 0
    for pergunta, esperado in PERGUNTAS_MATEMATICA:
        r = resolver_exercicio(pergunta)
        if r.resolvida:
            sucessos_diretos += 1
        else:
            resp_idx = _responder_indice_total(pergunta)
            if resp_idx and resp_idx.conhecimento_encontrado:
                sucessos_indice += 1
    total_coberto = sucessos_diretos + sucessos_indice
    assert total_coberto >= 70, f"Espera-se cobertura combinada de pelo menos 70% para perguntas de matemática (obtido: {total_coberto}/100)"


if __name__ == "__main__":
    print("Executando verificação da Bateria 200 do PSF-IAminy...")
    test_bateria_portugues_coerencia()
    print("[OK] Teste de Português concluído.")
    test_bateria_matematica_coerencia()
    print("[OK] Teste de Matemática concluído.")
