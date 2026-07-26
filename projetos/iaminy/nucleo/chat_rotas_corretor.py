# -*- coding: utf-8 -*-
"""Rota de correção linguística do Chat Vivo (Fase 1-C, ligada ao
orquestrador completo na Fase 6.4 do plano de corretor).

Liga ao chat o pipeline inteiro construído nas Fases 1-6:
normalização mecânica de texto corrido (Fase 1-B), whitelist ortográfica
conservadora, aviso de parônimo, e sugestão ranqueada (Fase 6.3 --
distância de edição + fonética + frequência + contexto + canal ruidoso +
proximidade semântica, nunca um único sinal isolado) via
`lingua_portuguesa.motor.MotorPortugues`.

Ordem de prioridade preservada (nunca correção silenciosa de significado):
1. normalização mecânica (pontuação/espaço/maiúscula/parágrafo);
2. whitelist de erros aprovados;
3. parônimo: nota consultiva, nunca troca automática;
4. palavra ausente do dicionário: sugestão ranqueada, nunca substituição.
"""
from __future__ import annotations

from functools import lru_cache
import re

from lingua_portuguesa import MotorPortugues
from nucleo.chat_tipos import RespostaChat


@lru_cache(maxsize=1)
def _motor_portugues() -> MotorPortugues:
    return MotorPortugues()


_COMANDO_CORRECAO = re.compile(
    r"^\s*(?:por\s+favor[,\s]+)?(?:pode\s+)?(?:"
    r"corrigir(?:\s+a)?\s+(?:resposta|texto)|"
    r"corrige\s+a\s+resposta|"
    r"corrija(?:\s+(?:esta|este|a|o))?\s*(?:resposta|texto)?|"
    r"revise(?:\s+(?:esta|este|a|o))?\s*(?:resposta|texto)?"
    r")\s*(?:por\s+favor)?\s*[:,-]?\s*",
    re.IGNORECASE,
)


def _texto_sem_comando(texto: str) -> str:
    """Retira somente um pedido explícito no início; conserva o texto citado."""
    restante = _COMANDO_CORRECAO.sub("", texto, count=1)
    return restante if restante.strip() else texto


def _responder_corrigir(texto: str, tom: str) -> RespostaChat:
    texto_alvo = _texto_sem_comando(texto)
    analise = _motor_portugues().analisar(texto_alvo)
    resultado = analise.correcao
    assert resultado is not None

    linhas: list[str] = []
    if resultado.normalizado != resultado.original:
        linhas.append(f"Normalizado (pontuação/espaço/maiúscula/parágrafo): {resultado.normalizado}")
    if resultado.alteracoes_whitelist:
        linhas.append(f"Ortografia (erro conhecido corrigido): {resultado.corrigido}")
        for antes, depois, motivo in resultado.alteracoes_whitelist:
            linhas.append(f"  - {antes} -> {depois} ({motivo})")
    if resultado.notas_paronimo:
        linhas.append("Parônimos possíveis (confira o sentido, não troquei sozinho):")
        linhas.extend(f"  - {nota}" for nota in resultado.notas_paronimo)
    if resultado.sugestoes_ortografia:
        linhas.append("Palavras que não reconheço no dicionário, com sugestões próximas:")
        linhas.extend(
            f'  - "{palavra}" -> talvez: {", ".join(candidatas)}'
            for palavra, candidatas in resultado.sugestoes_ortografia
        )
    diagnosticos_gramaticais = tuple(
        diagnostico
        for diagnostico in analise.diagnosticos
        if diagnostico.codigo not in {
            "ORTOGRAFIA_SUGESTAO",
            "ORTOGRAFIA_CORRECAO_CONHECIDA",
            "PARONIMO",
        }
    )
    if diagnosticos_gramaticais:
        linhas.append("Gramática (avisos auditáveis; confirme os casos ambíguos):")
        for diagnostico in diagnosticos_gramaticais:
            detalhe = diagnostico.mensagem
            if diagnostico.sugestao:
                detalhe += f" Sugestão: {diagnostico.sugestao}"
            linhas.append(f"  - [{diagnostico.codigo}] {detalhe}")

    if not linhas:
        corpo = f"Não encontrei nada para corrigir. Texto:\n{resultado.corrigido}"
        confianca = 70
    else:
        corpo = "\n".join(linhas) + f"\n\nTexto final sugerido: {resultado.corrigido}"
        confianca = 80

    return RespostaChat(
        corpo,
        "corrigir",
        tom,
        confianca,
        origem="lingua_portuguesa.motor",
        conhecimento_encontrado=True,
        contexto_chat={"ultimo_titulo": "correção de texto", "ultima_origem": "lingua_portuguesa.motor"},
    )
