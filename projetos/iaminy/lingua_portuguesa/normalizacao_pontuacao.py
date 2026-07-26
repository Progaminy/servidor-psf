"""Normalização mecânica de texto corrido: espaçamento, maiúscula de
início de frase, pontuação final ausente, parágrafo.

Fase 1-B do plano de corretor: o autor pediu poder colar "uma palavra,
texto ou mesmo livro" e receber de volta com "vírgula no lugar, pontos,
espaço, indentação, letras maiúsculas". O que este módulo faz é
deliberadamente limitado ao que é **mecanicamente decidível sem adivinhar
intenção**:

- espaço correto ao redor de pontuação já existente;
- maiúscula no início de cada frase já delimitada por `.`/`!`/`?`/`…`;
- ponto final no fim do texto, se faltar;
- separador de parágrafo consistente (uma linha em branco, nunca mais).

O que este módulo **não** faz, de propósito: inserir vírgula ou ponto no
meio de um texto que não tem pontuação nenhuma. Isso exigiria julgamento
sintático/semântico real sobre onde termina uma oração — o motor de
gramática (`gramatica.py`) ainda não tem essa maturidade (só concordância
determinante/nome e nome/adjetivo; concordância verbal é a Fase 2 deste
plano). Fingir esse julgamento seria inventar pontuação, não corrigi-la;
fica registado como fronteira aberta, não como capacidade escondida.

Capitalização de nomes próprios também fica fora: exigiria uma lista real
de nomes próprios que o projeto não tem — capitalizar por adivinhação
seria o mesmo tipo de erro.
"""
from __future__ import annotations

import re

from .tokenizacao import Tokenizador

_FECHAMENTO = frozenset(",.;:!?…)]}»")
_ABERTURA = frozenset("([{«")
_FIM_DE_FRASE = re.compile(r"[.!?…]+")
_ABERTURA_PRECEDENTE = frozenset("\"'«([{")
_FECHAMENTO_FINAL = frozenset("\"'”’»)]}")


# Trechos cujo conteúdo tem gramática própria. Pontos, dois-pontos e barras
# neles não são sinais de frase e, portanto, ficam opacos durante cada etapa
# mecânica. A ordem é deliberada: blocos/aspas primeiro, endereços e tokens
# técnicos depois, para padrões menores nunca recortarem um trecho maior.
_PADROES_CODIGO: tuple[re.Pattern[str], ...] = (
    re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~"),
    re.compile(r"`[^`\n]*`"),
)
_PADROES_ASPAS: tuple[re.Pattern[str], ...] = (
    re.compile(r'"(?:\\.|[^"\\])*"'),
    re.compile(r"“[^”]*”|‘[^’]*’|«[^»]*»"),
    re.compile(r"(?<!\w)'(?:\\.|[^'\\])*'(?!\w)"),
)
_PADROES_TECNICOS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bhttps?://[^\s<>\"'`]+", re.IGNORECASE),
    re.compile(
        r"(?<![\w.+-])[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Z0-9-]+(?:\.[A-Z0-9-]+)+(?![\w.-])",
        re.IGNORECASE,
    ),
    re.compile(r"(?<!\w)[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*"),
    re.compile(r"(?<!\w)/(?:[\w.@~+-]+/)*[\w.@~+-]+"),
    re.compile(r"(?<!\w)(?:[A-Za-z0-9_.~+-]+/)+[A-Za-z0-9_.~+-]+"),
    re.compile(r"(?<![\w@])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?:/[^\s<>\"'`]*)?"),
    re.compile(r"(?<!\w)\d{1,2}:\d{2}(?::\d{2})?(?!\w)"),
    re.compile(r"(?<!\w)[vV]?\d+(?:\.\d+){1,}(?![\w.])"),
    re.compile(r"(?<!\w)(?:[^\W\d_]\.){2,}", re.UNICODE),
    re.compile(r"(?<!\w)(?:Sr|Sra|Dr|Dra|Prof|Profa|etc|ex)\.(?!\w)", re.IGNORECASE),
)

_tokenizador = Tokenizador()


def _sufixo_alfabetico(indice: int) -> str:
    """Índice em letras, mantendo o marcador como um único token estável."""
    letras: list[str] = []
    atual = indice
    while True:
        atual, resto = divmod(atual, 26)
        letras.append(chr(ord("A") + resto))
        if atual == 0:
            return "".join(reversed(letras))
        atual -= 1


def _proteger_trechos(
    texto: str, *, proteger_aspas: bool = True
) -> tuple[str, dict[str, str]]:
    protegidos: dict[str, str] = {}
    resultado = texto

    def substituir(ocorrencia: re.Match[str]) -> str:
        indice = len(protegidos)
        marcador = f"PSFTRECHOPROTEGIDO{_sufixo_alfabetico(indice)}FIM"
        while marcador in resultado or marcador in protegidos:
            indice += 1
            marcador = f"PSFTRECHOPROTEGIDO{_sufixo_alfabetico(indice)}FIM"
        protegidos[marcador] = ocorrencia.group(0)
        return marcador

    padroes = _PADROES_CODIGO + (
        _PADROES_ASPAS if proteger_aspas else ()
    ) + _PADROES_TECNICOS
    for padrao in padroes:
        resultado = padrao.sub(substituir, resultado)
    return resultado, protegidos


def _restaurar_trechos(texto: str, protegidos: dict[str, str]) -> str:
    for marcador, original in protegidos.items():
        texto = texto.replace(marcador, original)
    return texto


def normalizar_espacos_pontuacao(texto: str) -> str:
    """Sem espaço antes de `,.;:!?…)]}»`; exatamente um espaço depois
    (exceto fim de texto ou antes de outra pontuação de fechamento); sem
    espaço depois de `([{«`. Quebras de linha na lacuna original nunca são
    tocadas — preserva separação de parágrafo, que é assunto de
    `normalizar_paragrafos`, não desta função.
    """
    texto_protegido, protegidos = _proteger_trechos(texto)
    tokens = _tokenizador.tokenizar(texto_protegido)
    if not tokens:
        return texto
    partes: list[str] = [texto_protegido[: tokens[0].inicio]]
    total = len(tokens)
    for indice, token in enumerate(tokens):
        partes.append(token.texto)
        if indice + 1 >= total:
            partes.append(texto_protegido[token.fim :])
            break
        proximo = tokens[indice + 1]
        lacuna_original = texto_protegido[token.fim : proximo.inicio]
        if "\n" in lacuna_original:
            partes.append(lacuna_original)
            continue
        if proximo.texto in _FECHAMENTO:
            partes.append("")
        elif token.texto in _ABERTURA:
            partes.append("")
        elif token.texto in _FECHAMENTO:
            partes.append(" ")
        elif proximo.texto in _ABERTURA:
            partes.append(" ")
        elif lacuna_original:
            partes.append(" ")
        else:
            partes.append("")
    return _restaurar_trechos("".join(partes), protegidos)


def _capitalizar_primeira_letra(segmento: str) -> str:
    indice = 0
    while indice < len(segmento) and (
        segmento[indice].isspace() or segmento[indice] in _ABERTURA_PRECEDENTE
    ):
        indice += 1
    if indice < len(segmento) and segmento[indice].isalpha():
        return segmento[:indice] + segmento[indice].upper() + segmento[indice + 1 :]
    return segmento


def capitalizar_inicio_de_frases(texto: str) -> str:
    """Maiúscula na primeira letra do texto e após cada `.`/`!`/`?`/`…`.

    Só atua onde a pontuação de fim de frase já existe — não inventa
    limite de frase novo (ver limite de escopo no docstring do módulo).
    """
    if not texto:
        return texto
    # Capitalização no início de uma citação é uma normalização já suportada
    # pela API. Aspas ficam visíveis nesta etapa; URLs, abreviaturas e código
    # dentro delas continuam protegidos pelos respetivos padrões.
    texto_protegido, protegidos = _proteger_trechos(texto, proteger_aspas=False)
    partes = _FIM_DE_FRASE.split(texto_protegido)
    delimitadores = _FIM_DE_FRASE.findall(texto_protegido)
    resultado: list[str] = []
    deve_capitalizar = True
    for indice, parte in enumerate(partes):
        if deve_capitalizar:
            parte = _capitalizar_primeira_letra(parte)
            if parte.strip():
                deve_capitalizar = False
        resultado.append(parte)
        if indice < len(delimitadores):
            resultado.append(delimitadores[indice])
            deve_capitalizar = True
    return _restaurar_trechos("".join(resultado), protegidos)


def garantir_pontuacao_final(texto: str) -> str:
    """Acrescenta `.` ao final do texto se não terminar em `./!/…/?`.

    Extensão direta do padrão já real de
    `lingua_portuguesa/motor.py::MotorPortugues.produzir_texto` (que já faz
    isto por unidade gerada internamente) para texto arbitrário de entrada.
    """
    aparado = texto.rstrip()
    if not aparado:
        return texto
    candidato = aparado
    while candidato and candidato[-1] in _FECHAMENTO_FINAL:
        candidato = candidato[:-1].rstrip()
    if candidato and candidato[-1] in ".!?…":
        return texto
    sufixo = texto[len(aparado) :]
    return aparado + "." + sufixo


_QUEBRA_MULTIPLA = re.compile(r"\n[ \t]*\n(?:[ \t]*\n)*")
_ESPACO_ANTES_DE_QUEBRA = re.compile(r"[ \t]+\n")


def normalizar_paragrafos(texto: str) -> str:
    """Separador de parágrafo consistente: uma linha em branco, nunca mais.
    Também apara espaço em branco nas duas pontas do texto inteiro (mas
    nunca no meio) — mecânico e seguro, sem exigir julgamento nenhum.

    Estende o padrão já real de
    `ensino/leitura_documentos.py::_LINHAS_VAZIAS` (que colapsa linhas
    vazias múltiplas) para qualquer texto de entrada, não só extração de
    `.docx`.
    """
    texto_protegido, protegidos = _proteger_trechos(texto)
    normalizado = texto_protegido.replace("\r\n", "\n").replace("\r", "\n")
    normalizado = _ESPACO_ANTES_DE_QUEBRA.sub("\n", normalizado)
    normalizado = _QUEBRA_MULTIPLA.sub("\n\n", normalizado)
    return _restaurar_trechos(normalizado.strip(), protegidos)


def normalizar_texto_corrido(texto: str) -> str:
    """Aplica as quatro normalizações mecânicas da Fase 1-B, em ordem.

    Ponto de entrada único para o resto do pipeline (Fase 1-C liga isto ao
    chat). Nunca insere pontuação que exigiria julgamento sintático não
    construído ainda — ver limite de escopo no docstring do módulo.
    """
    texto = normalizar_espacos_pontuacao(texto)
    texto = capitalizar_inicio_de_frases(texto)
    texto = garantir_pontuacao_final(texto)
    texto = normalizar_paragrafos(texto)
    return texto
