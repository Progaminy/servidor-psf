"""Fecha um achado real: 26 substantivos em `lexico_base.json` (adição,
divisor, múltiplo, quociente, resto, função, relação, grafo, conceito,
fórmula, pacote e outros -- todos de uso comum em Matemática/Português)
tinham SÓ a forma singular registada, sem género nem plural nenhum
("formas": {"divisor": {}}) -- por isso "divisores"/"funções"/"grafos"
não existiam no léxico, mesma classe de lacuna já fechada para os verbos
hollow em `test_verbos_irregulares_preterito.py`. Corrigido: cada
entrada ganhou género real e a forma plural (reaproveitando
`_plural_substantivo`, mesma regra já usada pelo resto do léxico), sem
tocar em nenhuma outra entrada do ficheiro.
"""
from lingua_portuguesa.lexico import Dicionario
from lingua_portuguesa.tipos import ClasseGramatical, Genero, Numero


def test_substantivos_antes_so_singular_agora_tem_plural_real():
    dicionario = Dicionario.padrao()
    casos = {
        "divisor": "divisores",
        "múltiplo": "múltiplos",
        "quociente": "quocientes",
        "função": "funções",
        "relação": "relações",
        "grafo": "grafos",
        "conceito": "conceitos",
        "fórmula": "fórmulas",
        "pacote": "pacotes",
        "adição": "adições",
    }
    for singular, plural in casos.items():
        leituras_singular = dicionario.buscar(singular)
        leituras_plural = dicionario.buscar(plural)
        assert leituras_singular, f"'{singular}' deveria continuar no léxico"
        assert leituras_plural, f"'{plural}' deveria existir agora"
        assert any(leitura.numero == Numero.PLURAL for leitura in leituras_plural)


def test_substantivos_antes_hollow_agora_tem_genero_real():
    dicionario = Dicionario.padrao()
    singulares_divisor = [l for l in dicionario.buscar("divisor") if l.numero == Numero.SINGULAR]
    assert singulares_divisor and all(l.genero == Genero.MASCULINO for l in singulares_divisor)
    singulares_funcao = [l for l in dicionario.buscar("função") if l.numero == Numero.SINGULAR]
    assert singulares_funcao and all(l.genero == Genero.FEMININO for l in singulares_funcao)


def test_gentilicos_espanhol_e_frances_tem_paradigma_completo():
    # achado real: "espanhol"/"francês" ficaram de fora de propósito numa
    # sessão anterior (registado em conversa.md) porque `_plural_substantivo`/
    # `_forma_adj` não tratam "-ol"/"-ês" (precisam de acento novo:
    # espanhol->espanhóis, e "-ês" perde o circunflexo: francês->franceses).
    # Fechados à mão, mesmo padrão já usado pra "português" (substantivo E
    # adjetivo, 4 formas cada, hand-crafted no JSON -- gentílico não é
    # regra de sufixo genérica, é exceção fechada, mesma disciplina de
    # `_PLURAIS_AO_IRREGULARES`).
    dicionario = Dicionario.padrao()
    casos = {
        "espanhol": ("espanhóis", "espanhola", "espanholas"),
        "francês": ("franceses", "francesa", "francesas"),
    }
    for masc_sg, (masc_pl, fem_sg, fem_pl) in casos.items():
        for forma in (masc_sg, masc_pl, fem_sg, fem_pl):
            leituras = dicionario.buscar(forma)
            assert leituras, f"{forma!r} deveria estar no dicionário"
            classes = {leitura.classe for leitura in leituras}
            assert ClasseGramatical.SUBSTANTIVO in classes
            assert ClasseGramatical.ADJETIVO in classes
