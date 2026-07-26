from lingua_portuguesa.lexico import Dicionario
from lingua_portuguesa.tipos import ClasseGramatical, EntradaLexical, Genero, Numero


def test_dicionario_padrao_cacheia_construcao_mas_isola_chamadores():
    # Achado real de desempenho (auditoria externa): reconstruir o léxico
    # padrão inteiro em cada `Dicionario.padrao()` era o maior custo de
    # inicialização do motor. A construção cara agora é cacheada
    # (`_construir_padrao`), mas cada chamada devolve uma CÓPIA -- nunca a
    # mesma instância -- pra `.adicionar()` num dicionário devolvido aqui
    # continuar isolado do resto do processo, mesmo uso real já
    # demonstrado em `testes/test_lingua_portuguesa.py`.
    primeiro = Dicionario.padrao()
    segundo = Dicionario.padrao()
    assert primeiro is not segundo
    assert primeiro.lemas() == segundo.lemas()


def test_mutar_dicionario_padrao_nao_vaza_para_proxima_chamada():
    dicionario = Dicionario.padrao()
    dicionario.adicionar(
        EntradaLexical(
            lema="zeta",
            forma="zeta",
            classe=ClasseGramatical.SUBSTANTIVO,
            definicoes=("Nome da letra z no alfabeto grego.",),
            genero=Genero.FEMININO,
            numero=Numero.SINGULAR,
        )
    )
    assert "zeta" in dicionario
    assert "zeta" not in Dicionario.padrao()


def test_dicionario_padrao_continua_com_o_mesmo_conteudo_da_construcao_cacheada():
    base = Dicionario._construir_padrao()
    copia = Dicionario.padrao()
    assert base.lemas() == copia.lemas()
    assert base.total_formas() == copia.total_formas()
