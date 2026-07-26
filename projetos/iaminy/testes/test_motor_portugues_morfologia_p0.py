import pytest

from lingua_portuguesa import (
    ClasseGramatical,
    Genero,
    MotorPortugues,
    Numero,
    OpcoesAnalise,
)
from lingua_portuguesa.lexico_expansao import _forma_adj, _plural_composto


@pytest.fixture(scope="module")
def motor() -> MotorPortugues:
    return MotorPortugues(opcoes=OpcoesAnalise.leve())


@pytest.mark.parametrize(
    ("sujeito", "forma"),
    [
        ("Eu", "falava"),
        ("Ele", "falava"),
        ("Eu", "comia"),
        ("Ele", "comia"),
        ("Eu", "partia"),
        ("Ele", "partia"),
    ],
)
def test_imperfeito_regular_singular_e_sincretico_sem_falso_alerta(
    motor: MotorPortugues,
    sujeito: str,
    forma: str,
) -> None:
    analise = motor.analisar(f"{sujeito} {forma}.")

    assert "CONCORDANCIA_VERBO_SUJEITO" not in {
        diagnostico.codigo for diagnostico in analise.diagnosticos
    }
    leituras = [
        entrada
        for entrada in motor.dicionario.buscar(forma)
        if entrada.classe == ClasseGramatical.VERBO
        and entrada.atributos.get("tempo") == "pretérito imperfeito"
    ]
    assert leituras
    assert all(entrada.pessoa is None for entrada in leituras)
    assert all(entrada.numero == Numero.SINGULAR for entrada in leituras)


@pytest.mark.parametrize(
    "forma",
    ["era", "estava", "tinha", "continha", "obtinha", "mantinha"],
)
def test_imperfeito_irregular_singular_do_json_preserva_sincretismo(
    motor: MotorPortugues,
    forma: str,
) -> None:
    leituras = [
        entrada
        for entrada in motor.dicionario.buscar(forma)
        if entrada.classe == ClasseGramatical.VERBO
        and entrada.atributos.get("tempo") == "pretérito imperfeito"
    ]

    assert leituras
    assert all(entrada.pessoa is None for entrada in leituras)
    assert all(entrada.numero == Numero.SINGULAR for entrada in leituras)


def test_formas_geradas_de_cansado_carregam_genero_e_numero() -> None:
    tracos = {
        (entrada.forma, entrada.genero, entrada.numero)
        for entrada in _forma_adj("cansado", "teste")
    }

    assert tracos == {
        ("cansado", Genero.MASCULINO, Numero.SINGULAR),
        ("cansada", Genero.FEMININO, Numero.SINGULAR),
        ("cansados", Genero.MASCULINO, Numero.PLURAL),
        ("cansadas", Genero.FEMININO, Numero.PLURAL),
    }


@pytest.mark.parametrize(
    ("frase", "tem_discordancia"),
    [
        ("menina cansada.", False),
        ("meninos cansados.", False),
        ("menina cansados.", True),
        ("meninos cansada.", True),
    ],
)
def test_tracos_de_cansada_e_cansados_alimentam_concordancia(
    motor: MotorPortugues,
    frase: str,
    tem_discordancia: bool,
) -> None:
    codigos = {
        diagnostico.codigo for diagnostico in motor.analisar(frase).diagnosticos
    }

    assert ("CONCORDANCIA_NOME_ADJ" in codigos) is tem_discordancia


def test_fiel_pluraliza_com_acento_e_preserva_tracos() -> None:
    tracos = {
        (entrada.forma, entrada.genero, entrada.numero)
        for entrada in _forma_adj("fiel", "teste")
    }

    assert tracos == {
        ("fiel", Genero.COMUM, Numero.SINGULAR),
        ("fiéis", Genero.COMUM, Numero.PLURAL),
    }
    assert _plural_composto("aliado fiel") == "aliados fiéis"


def test_fiels_nao_e_indexado_como_forma_de_fiel(motor: MotorPortugues) -> None:
    assert not motor.dicionario.buscar("fiels")
    assert any(
        entrada.lema == "fiel"
        and entrada.classe == ClasseGramatical.ADJETIVO
        and entrada.genero == Genero.COMUM
        and entrada.numero == Numero.PLURAL
        for entrada in motor.dicionario.buscar("fiéis")
    )
