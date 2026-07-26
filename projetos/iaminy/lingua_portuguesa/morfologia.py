"""Análise morfológica híbrida: léxico explícito e heurísticas transparentes."""
from __future__ import annotations

from .lexico import Dicionario
from .tipos import (
    AnaliseToken,
    ClasseGramatical,
    LeituraMorfologica,
    Numero,
    TipoToken,
    Token,
)


class AnalisadorMorfologico:
    def __init__(self, dicionario: Dicionario) -> None:
        self.dicionario = dicionario

    def analisar(self, tokens: tuple[Token, ...]) -> tuple[AnaliseToken, ...]:
        analises = tuple(self.analisar_token(token) for token in tokens)
        return tuple(
            self._inferir_por_contexto(item, analises, indice)
            for indice, item in enumerate(analises)
        )

    @staticmethod
    def _inferir_por_contexto(
        analise: AnaliseToken,
        analises: tuple[AnaliseToken, ...],
        indice: int,
    ) -> AnaliseToken:
        leitura = analise.principal
        if (
            indice > 0
            and analises[indice - 1].token.texto == "-"
            and analise.token.normalizado in {"me", "te", "se", "nos", "vos", "o", "a", "os", "as", "lhe", "lhes"}
        ):
            clitico = LeituraMorfologica(
                token=analise.token,
                lema=analise.token.normalizado,
                classe=ClasseGramatical.PRONOME,
                atributos={"funcao": "clitico"},
                confianca=0.95,
                origem="decomposicao_clitica",
            )
            restantes = tuple(
                item for item in analise.leituras if item.classe != ClasseGramatical.PRONOME
            )
            return AnaliseToken(analise.token, (clitico,) + restantes)
        if leitura.classe != ClasseGramatical.DESCONHECIDA:
            return analise
        texto = analise.token.texto
        if analise.token.normalizado in {"muito", "muita", "muitos", "muitas", "pouco", "pouca", "poucos", "poucas"}:
            nova = LeituraMorfologica(
                token=analise.token,
                lema=analise.token.normalizado.rstrip("s"),
                classe=ClasseGramatical.DETERMINANTE,
                numero=Numero.PLURAL if analise.token.normalizado.endswith("s") else Numero.SINGULAR,
                confianca=0.70,
                origem="heuristica_contextual",
            )
            return AnaliseToken(analise.token, (nova,))
        if texto[:1].isupper() and texto[1:].islower():
            nova = LeituraMorfologica(
                token=analise.token,
                lema=analise.token.normalizado,
                classe=ClasseGramatical.SUBSTANTIVO,
                numero=Numero.SINGULAR,
                atributos={"tipo": "nome_proprio"},
                confianca=0.55,
                origem="heuristica_contextual",
            )
            return AnaliseToken(analise.token, (nova,))
        if analise.token.normalizado in {"cedo", "amanhã", "ontem", "hoje", "logo"}:
            nova = LeituraMorfologica(
                token=analise.token,
                lema=analise.token.normalizado,
                classe=ClasseGramatical.ADVERBIO,
                confianca=0.65,
                origem="heuristica_contextual",
            )
            return AnaliseToken(analise.token, (nova,))
        # Forma desconhecida entre um nominal e um complemento tende a ser
        # verbal. A confiança baixa mantém a inferência explicitamente
        # distinta de uma entrada lexical comprovada.
        antes = analises[indice - 1].principal if indice > 0 else None
        depois = analises[indice + 1].principal if indice + 1 < len(analises) else None
        if (
            antes is not None
            and antes.classe in {ClasseGramatical.SUBSTANTIVO, ClasseGramatical.PRONOME}
            and depois is not None
            and depois.classe in {
                ClasseGramatical.NUMERAL,
                ClasseGramatical.DETERMINANTE,
                ClasseGramatical.SUBSTANTIVO,
            }
        ):
            nova = LeituraMorfologica(
                token=analise.token,
                lema=analise.token.normalizado,
                classe=ClasseGramatical.VERBO,
                atributos={"forma": "finita_inferida"},
                confianca=0.40,
                origem="heuristica_contextual",
            )
            return AnaliseToken(analise.token, (nova,))
        return analise

    def analisar_token(self, token: Token) -> AnaliseToken:
        if token.tipo == TipoToken.NUMERO:
            leitura = LeituraMorfologica(
                token, token.normalizado, ClasseGramatical.NUMERAL, origem="tokenizador"
            )
            return AnaliseToken(token, (leitura,))
        if token.tipo != TipoToken.PALAVRA:
            leitura = LeituraMorfologica(
                token, token.normalizado, ClasseGramatical.DESCONHECIDA,
                origem="tokenizador",
            )
            return AnaliseToken(token, (leitura,))

        entradas = self.dicionario.buscar(token.normalizado)
        if entradas:
            leituras = tuple(
                LeituraMorfologica(
                    token=token,
                    lema=entrada.lema,
                    classe=entrada.classe,
                    genero=entrada.genero,
                    numero=entrada.numero,
                    pessoa=entrada.pessoa,
                    definicoes=entrada.definicoes,
                    atributos=entrada.atributos,
                )
                for entrada in entradas
            )
            return AnaliseToken(token, leituras)

        return AnaliseToken(token, (self._inferir(token),))

    @staticmethod
    def _inferir(token: Token) -> LeituraMorfologica:
        palavra = token.normalizado
        classe = ClasseGramatical.DESCONHECIDA
        lema = palavra
        atributos: dict[str, str] = {}
        confianca = 0.20
        numero: Numero | None = None

        if palavra.endswith("mente") and len(palavra) > 6:
            classe = ClasseGramatical.ADVERBIO
            confianca = 0.72
        elif palavra.endswith(("ar", "er", "ir")) and len(palavra) > 3:
            classe = ClasseGramatical.VERBO
            atributos["forma"] = "infinitivo"
            confianca = 0.68
        elif palavra.endswith(("aram", "eram", "iram", "am", "em")) and len(palavra) > 4:
            classe = ClasseGramatical.VERBO
            numero = Numero.PLURAL
            atributos["forma"] = "finita_regular_inferida"
            confianca = 0.45
        elif palavra.endswith(("ou", "iu", "eu", "ei")) and len(palavra) > 4:
            classe = ClasseGramatical.VERBO
            numero = Numero.SINGULAR
            atributos["forma"] = "preterito_inferido"
            confianca = 0.48
        elif palavra.endswith(("ção", "ções", "dade", "dades", "mento", "mentos")):
            classe = ClasseGramatical.SUBSTANTIVO
            confianca = 0.58

        numero = numero or (Numero.PLURAL if palavra.endswith("s") and len(palavra) > 2 else None)
        return LeituraMorfologica(
            token=token,
            lema=lema,
            classe=classe,
            numero=numero,
            atributos=atributos,
            confianca=confianca,
            origem="heuristica",
        )
