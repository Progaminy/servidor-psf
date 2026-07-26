"""Detetor ortográfico persistente do PSF — Etapa 36.

Regra permanente desta etapa:
antes de interpretar uma pergunta, o PSF deve passar a entrada por uma
camada conservadora de deteção/correção ortográfica.

A correção é conservadora porque não pode alterar a matemática:
- números ficam intactos;
- sinais como +, -, x, ÷, %, frações e horas ficam intactos;
- unidades monetárias e medidas ficam intactas;
- só palavras/frases conhecidas como erro são corrigidas.

Isto não usa internet, API, modelo externo nem biblioteca de IA. É memória
local + comparação textual simples + pares de correção aprovados.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class AlteracaoOrtografica:
    antes: str
    depois: str
    motivo: str = "correção aprovada"


@dataclass(frozen=True, slots=True)
class ResultadoOrtografico:
    original: str
    corrigido: str
    alteracoes: tuple[AlteracaoOrtografica, ...]

    @property
    def houve_correcao(self) -> bool:
        return bool(self.alteracoes)


# Pares aprovados. A lista deve crescer com cada sessão, mas sempre de modo
# explícito e rastreável. Não há correção automática agressiva.
CORRECOES_BASE: tuple[tuple[str, str, str], ...] = (
    ("detenção de erros", "detecção de erros", "o contexto é encontrar erros, não prender erros"),
    ("detencao de erros", "detecção de erros", "normalização sem acento do mesmo erro"),
    ("erros ortográfico", "erros ortográficos", "concordância no plural"),
    ("erros ortograficos", "erros ortográficos", "acento e plural"),
    ("em todas sessões", "em todas as sessões", "artigo necessário"),
    ("reposta média", "resposta média", "troca comum de letras"),
    ("reposta media", "resposta média", "troca comum de letras"),
    # Esta entrada é mantida para compatibilidade com a memória de erros e
    # com o canal ruidoso, mas a aplicação é condicionada por
    # `_correcao_permitida`: "reposta" também é particípio legítimo de
    # "repor" e nunca pode ser trocada fora de um contexto inequívoco de
    # resposta textual.
    ("reposta", "resposta", "troca comum de letras"),
    ("duna si vez", "de uma só vez", "frase natural corrigida"),
    ("aprimure", "aprimore", "verbo correto"),
)


_CONTEXTO_RESPOSTA_INEQUIVOCO = re.compile(
    r"(?<!\w)(?:(?:a|esta|essa|minha|sua)\s+)?reposta\s+"
    r"(?:est[aá]|parece)\s+correta(?!\w)",
    re.IGNORECASE,
)


def _padrao_token_ou_frase(texto: str) -> re.Pattern[str]:
    """Compila uma correção literal que nunca casa dentro de outra palavra.

    `\b` não é suficiente para todos os sinais e alfabetos aceites pelo
    motor. Os limites negativos de ``\w`` mantêm a comparação Unicode e
    impedem corrupções como ``repostagem``/``preposta``.
    """
    return re.compile(rf"(?<!\w){re.escape(texto)}(?!\w)", re.IGNORECASE)


def _preservar_caixa(correcao: str, encontrado: str) -> str:
    """Transfere padrões inequívocos de caixa sem adivinhar caixa mista."""
    if encontrado.isupper():
        return correcao.upper()
    if encontrado.islower():
        return correcao.lower()
    if encontrado.istitle():
        return correcao.title()
    if encontrado[:1].isupper() and encontrado[1:].islower():
        return correcao[:1].upper() + correcao[1:]
    return correcao


def _correcao_permitida(errado: str, texto: str) -> bool:
    """Bloqueia pares lexical ou semanticamente ambíguos fora de contexto."""
    if errado.casefold() == "reposta":
        return _CONTEXTO_RESPOSTA_INEQUIVOCO.search(texto) is not None
    return True

# Memória local opcional. Se o projeto estiver em modo de escrita, pares novos
# podem ser acrescentados manualmente por ferramenta futura sem internet.
CAMINHO_MEMORIA = Path(__file__).resolve().parent / "dados" / "memoria_ortografica.tsv"


def _pares_memoria() -> tuple[tuple[str, str, str], ...]:
    if not CAMINHO_MEMORIA.exists():
        return ()
    pares: list[tuple[str, str, str]] = []
    for linha in CAMINHO_MEMORIA.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        partes = linha.split("\t")
        if len(partes) >= 2:
            motivo = partes[2] if len(partes) >= 3 else "memória local aprovada"
            pares.append((partes[0], partes[1], motivo))
    return tuple(pares)


def pares_aprovados() -> tuple[tuple[str, str, str], ...]:
    return CORRECOES_BASE + _pares_memoria()


def corrigir_ortografia(texto: str) -> ResultadoOrtografico:
    """Corrige apenas erros aprovados, sem tocar em números e símbolos.

    A implementação usa substituição de frases; isso é intencionalmente mais
    seguro que tentar adivinhar palavras desconhecidas. Quando o PSF não tem
    certeza, ele pode registrar sugestão, mas não deve alterar o pedido.
    """
    original = str(texto)
    corrigido = original
    alteracoes: list[AlteracaoOrtografica] = []

    for errado, certo, motivo in pares_aprovados():
        # Pares idênticos não são alterações e não devem produzir diagnóstico.
        if errado.casefold() == certo.casefold():
            continue
        if not _correcao_permitida(errado, corrigido):
            continue
        padrao = _padrao_token_ou_frase(errado)
        corrigido_novo, quantidade = padrao.subn(
            lambda ocorrencia: _preservar_caixa(certo, ocorrencia.group(0)),
            corrigido,
        )
        if quantidade:
            corrigido = corrigido_novo
            alteracoes.append(AlteracaoOrtografica(errado, certo, motivo))

    return ResultadoOrtografico(original=original, corrigido=corrigido, alteracoes=tuple(alteracoes))


def preparar_entrada_para_interpretacao(texto: str) -> str:
    """Entrada única que os motores devem chamar antes de interpretar."""
    return corrigir_ortografia(texto).corrigido


def aprender_correcao(errado: str, certo: str, motivo: str = "correção ensinada pelo utilizador") -> None:
    """Guarda um novo par de correção local.

    O PSF deve usar isto somente quando o utilizador ensina explicitamente a
    correção. Assim o motor melhora de sessão para sessão sem depender de
    dicionário externo.
    """
    CAMINHO_MEMORIA.parent.mkdir(parents=True, exist_ok=True)
    linha = f"{errado}\t{certo}\t{motivo}\n"
    existentes = CAMINHO_MEMORIA.read_text(encoding="utf-8") if CAMINHO_MEMORIA.exists() else ""
    if linha not in existentes:
        with CAMINHO_MEMORIA.open("a", encoding="utf-8") as f:
            f.write(linha)


def relatorio_correcao(texto: str) -> str:
    resultado = corrigir_ortografia(texto)
    if not resultado.houve_correcao:
        return "Ortografia: nenhuma correção aprovada necessária."
    linhas = ["Ortografia: correções aplicadas antes da interpretação:"]
    contador = 1
    for alt in resultado.alteracoes:
        linhas.append(f"{contador}. {alt.antes} -> {alt.depois} ({alt.motivo})")
        contador = contador + 1
    return "\n".join(linhas)
