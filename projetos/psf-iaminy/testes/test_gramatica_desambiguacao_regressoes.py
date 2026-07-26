"""Regressões para a fronteira entre desambiguação e concordância."""

from lingua_portuguesa import ClasseGramatical, MotorPortugues, OpcoesAnalise


def _analisar(texto: str):
    return MotorPortugues(opcoes=OpcoesAnalise.leve()).analisar(texto)


def _codigos(texto: str) -> tuple[str, ...]:
    return tuple(diagnostico.codigo for diagnostico in _analisar(texto).diagnosticos)


def test_homografo_nominal_nao_ressuscita_como_primeiro_verbo():
    analise = _analisar("As casas caiu.")

    casas = next(item for item in analise.morfologia if item.token.normalizado == "casas")
    assert casas.principal.classe is ClasseGramatical.SUBSTANTIVO
    assert "CONCORDANCIA_VERBO_SUJEITO" in tuple(
        diagnostico.codigo for diagnostico in analise.diagnosticos
    )


def test_homografo_nominal_plural_preserva_concordancia_correta():
    analise = _analisar("Muitas casas caíram.")

    casas = next(item for item in analise.morfologia if item.token.normalizado == "casas")
    assert casas.principal.classe is ClasseGramatical.SUBSTANTIVO
    assert "CONCORDANCIA_VERBO_SUJEITO" not in tuple(
        diagnostico.codigo for diagnostico in analise.diagnosticos
    )


def test_forma_verbal_sincretica_aceita_leitura_compativel_com_sujeito():
    for frase in ("Ela disse.", "Ela quis."):
        assert "CONCORDANCIA_VERBO_SUJEITO" not in _codigos(frase), frase


def test_coordenacao_local_promove_homografo_para_verbo():
    analise = _analisar("Eu banco e pago.")
    classes = {
        item.token.normalizado: item.principal.classe for item in analise.morfologia
    }

    assert classes["banco"] is ClasseGramatical.VERBO
    assert classes["pago"] is ClasseGramatical.VERBO
    assert "CONCORDANCIA_VERBO_SUJEITO" not in tuple(
        diagnostico.codigo for diagnostico in analise.diagnosticos
    )


def test_coordenacao_local_nao_rebaixa_verbo_ambiguo():
    analise = _analisar("Eu como e bebo.")
    classes = {
        item.token.normalizado: item.principal.classe for item in analise.morfologia
    }

    assert classes["como"] is ClasseGramatical.VERBO
    assert classes["bebo"] is ClasseGramatical.VERBO
    assert "CONCORDANCIA_VERBO_SUJEITO" not in tuple(
        diagnostico.codigo for diagnostico in analise.diagnosticos
    )
