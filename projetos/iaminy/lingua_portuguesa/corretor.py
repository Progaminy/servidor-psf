"""Orquestrador do corretor -- Fase 6.3 do plano: substituto honesto da
técnica 10 (Learning to Rank / XGBoost) mais a fachada `Corretor`, que
compõe todas as peças construídas nas Fases 1-6.

`pontuar()` é uma soma ponderada simples e documentada -- cada sinal
contribuinte é nomeado e recomputável à mão, ao contrário de um modelo de
ranqueamento treinado. Nunca aprende pesos por gradiente; os pesos em
`PESOS_PADRAO` são hand-set, cada um com racional inline, pensados para
serem ajustados manualmente com o tempo, não re-treinados.

`Corretor` segue o mesmo desenho de fachada de `motor.MotorPortugues`:
componentes injetáveis e opcionais. Um `Corretor()` construído hoje já
funciona com o que existe (Fases 1-2, 4-6); qualquer sinal cuja fonte de
dado ainda não foi decidida (frequência de corpus geral, fonte de lemas da
Fase 3) simplesmente não contribui para o candidato -- nunca é fingido.
"""
from __future__ import annotations

from typing import Mapping

from .canal_ruidoso import PESOS_ERRO_BASE, classificar_erro
from .cliticos import decompor_cliticos
from .corretor_ortografico_sessao import corrigir_ortografia
from .distancia_edicao import distancia_damerau_levenshtein
from .desambiguacao import desambiguar_analises
from .fonetica_computavel import codigo_fonetico
from .frequencia import frequencia_de
from .gramatica import AnalisadorGramatical
from .lexico import Dicionario
from .modelo_ngramas import ModeloNGrama
from .morfologia import AnalisadorMorfologico
from .normalizacao import sem_acentos
from .normalizacao_pontuacao import normalizar_texto_corrido
from .paronimos_comuns import buscar_par
from .proximidade_semantica import proximidade
from .tipos import TipoToken, Token
from .tipos_corretor import Candidato, ResultadoCorrecao
from .tokenizacao import Tokenizador

# cada peso tem um racional próprio -- soma não precisa dar 1.0, é só uma
# combinação linear explicável, nunca um modelo treinado.
PESOS_PADRAO: dict[str, float] = {
    # distância de edição pesa mais porque é o sinal mais confiável quando
    # existe -- entra como 1/(1+distância) (mais perto = melhor), não a
    # distância crua.
    "distancia_edicao": 0.30,
    # compatibilidade gramatical (Fase 2/6.2) é um sinal forte quando
    # disponível -- hoje não está ligado ao ranking automático de
    # candidatos (exigiria reanalisar a frase inteira por candidato);
    # fica documentado como sinal presente na estrutura, não fingido.
    "compatibilidade_gramatical": 0.20,
    # contexto (Fase 5.1) ajuda a desempatar entre candidatos plausíveis.
    "probabilidade_contexto": 0.15,
    # semelhança fonética (Fase 4.1) é útil mas mais fraca que edição.
    "similaridade_fonetica": 0.15,
    # peso do tipo de erro (canal ruidoso, Fase 5.2) refina o resto.
    "peso_erro": 0.10,
    # frequência (Fase 4.2) ainda vem de um corpus pequeno e enviesado --
    # peso baixo de propósito, enquanto a Fase 3 (fonte de vocabulário
    # maior) continuar decisão em aberto.
    "frequencia": 0.05,
    # proximidade semântica (Fase 6.1) é o sinal mais indireto -- só
    # ajuda a desempatar entre candidatos já próximos nos outros sinais.
    "proximidade_semantica": 0.05,
}


def pontuar(candidato: Candidato, pesos: Mapping[str, float] | None = None) -> float:
    """Soma ponderada dos sinais disponíveis do candidato. Um sinal
    ausente (`None`) contribui exatamente 0 -- nunca um valor inventado."""
    pesos_reais = pesos if pesos is not None else PESOS_PADRAO
    total = 0.0
    if candidato.distancia_edicao is not None:
        total += pesos_reais["distancia_edicao"] * (1.0 / (1 + candidato.distancia_edicao))
    if candidato.compatibilidade_gramatical is not None:
        total += pesos_reais["compatibilidade_gramatical"] * (1.0 if candidato.compatibilidade_gramatical else 0.0)
    if candidato.probabilidade_contexto is not None:
        total += pesos_reais["probabilidade_contexto"] * candidato.probabilidade_contexto
    if candidato.similaridade_fonetica is not None:
        total += pesos_reais["similaridade_fonetica"] * candidato.similaridade_fonetica
    if candidato.peso_erro is not None:
        total += pesos_reais["peso_erro"] * candidato.peso_erro
    if candidato.frequencia is not None:
        total += pesos_reais["frequencia"] * candidato.frequencia
    if candidato.proximidade_semantica is not None:
        total += pesos_reais["proximidade_semantica"] * candidato.proximidade_semantica
    return total


def ranquear(candidatos: tuple[Candidato, ...], pesos: Mapping[str, float] | None = None) -> tuple[Candidato, ...]:
    """Ordena candidatos por `pontuar()` descendente. Desempate
    determinístico: maior frequência primeiro, depois ordem alfabética --
    nunca ordem de inserção arbitrária."""

    def chave(candidato: Candidato) -> tuple[float, float, str]:
        frequencia_desempate = candidato.frequencia if candidato.frequencia is not None else -1.0
        return (-pontuar(candidato, pesos), -frequencia_desempate, candidato.forma)

    return tuple(sorted(candidatos, key=chave))


class Corretor:
    """Fachada do corretor -- compõe dicionário, modelo de n-grama e
    tokenizador, todos injetáveis. Mesmo desenho de `motor.MotorPortugues`."""

    def __init__(
        self,
        dicionario: Dicionario | None = None,
        modelo_ngrama: ModeloNGrama | None = None,
        gramatica: AnalisadorGramatical | None = None,
        tokenizador: Tokenizador | None = None,
        carregar_modelo: bool = True,
    ) -> None:
        self.dicionario = dicionario or Dicionario.padrao()
        self.modelo_ngrama = modelo_ngrama or (
            ModeloNGrama() if carregar_modelo else None
        )
        self.gramatica = gramatica or AnalisadorGramatical()
        self.tokenizador = tokenizador or Tokenizador()

    def obter_modelo_ngrama(self) -> ModeloNGrama:
        if self.modelo_ngrama is None:
            self.modelo_ngrama = ModeloNGrama()
        return self.modelo_ngrama

    def candidatos_para(
        self,
        palavra: str,
        anterior: str | None = None,
        limite: int = 8,
        *,
        posterior: str | None = None,
        contexto: tuple[Token, ...] | None = None,
        indice_contexto: int | None = None,
        usar_contexto: bool = True,
        usar_fonetica: bool = True,
    ) -> tuple[Candidato, ...]:
        """Candidatos de correção para `palavra` (ausente do dicionário),
        já pontuados e ordenados -- o mais provável primeiro."""
        formas = self.dicionario.sugerir(palavra, limite=limite)
        if not formas:
            return ()
        candidatos: list[Candidato] = []
        codigo_original = codigo_fonetico(palavra) if usar_fonetica else None
        for forma in formas:
            distancia = distancia_damerau_levenshtein(
                sem_acentos(palavra), sem_acentos(forma)
            )
            mesma_foneticamente = (
                codigo_original == codigo_fonetico(forma)
                if usar_fonetica
                else None
            )
            probabilidades: list[float] = []
            if usar_contexto and anterior is not None:
                probabilidades.append(
                    self.obter_modelo_ngrama().probabilidade_condicional(
                        forma, anterior
                    )
                )
            if usar_contexto and posterior is not None:
                probabilidades.append(
                    self.obter_modelo_ngrama().probabilidade_condicional(
                        posterior, forma
                    )
                )
            prob_contexto = (
                sum(probabilidades) / len(probabilidades) if probabilidades else None
            )
            peso_erro = None
            if usar_fonetica and palavra != forma:
                peso_erro = PESOS_ERRO_BASE.get(classificar_erro(palavra, forma))
            candidatos.append(
                Candidato(
                    forma=forma,
                    distancia_edicao=distancia,
                    similaridade_fonetica=(
                        (1.0 if mesma_foneticamente else 0.0)
                        if mesma_foneticamente is not None
                        else None
                    ),
                    frequencia=frequencia_de(forma),
                    probabilidade_contexto=prob_contexto,
                    proximidade_semantica=proximidade(palavra, forma),
                    peso_erro=peso_erro,
                    compatibilidade_gramatical=self._compatibilidade_gramatical(
                        forma, contexto, indice_contexto
                    ),
                )
            )
        return ranquear(tuple(candidatos))

    def _compatibilidade_gramatical(
        self,
        forma: str,
        contexto: tuple[Token, ...] | None,
        indice: int | None,
    ) -> bool | None:
        """Reanalisa a frase com o candidato, sem alterar o texto original."""
        if contexto is None or indice is None or not (0 <= indice < len(contexto)):
            return None
        original = contexto[indice]
        substituto = Token(
            texto=forma,
            normalizado=original.normalizado if forma == original.texto else forma.casefold(),
            tipo=TipoToken.PALAVRA,
            inicio=original.inicio,
            fim=original.fim,
        )
        tokens = contexto[:indice] + (substituto,) + contexto[indice + 1 :]
        analises = AnalisadorMorfologico(self.dicionario).analisar(tokens)
        analises = desambiguar_analises(analises)
        return not self.gramatica.verificar(analises)

    def corrigir_texto(
        self,
        texto: str,
        *,
        usar_contexto: bool = True,
        usar_fonetica: bool = True,
    ) -> ResultadoCorrecao:
        """Pipeline completo, na ordem conservadora de sempre: 1)
        normalização mecânica de texto corrido (Fase 1-B); 2) whitelist de
        erro conhecido; 3) aviso de parônimo (consultivo, nunca troca
        sozinho); 4) sugestão ranqueada para palavra ausente do
        dicionário (nunca correção silenciosa)."""
        normalizado = normalizar_texto_corrido(texto)
        resultado_ortografico = corrigir_ortografia(normalizado)
        corrigido = resultado_ortografico.corrigido

        tokens = decompor_cliticos(self.tokenizador.tokenizar(corrigido), self.dicionario)
        analises_contextuais = AnalisadorMorfologico(self.dicionario).analisar(tokens)
        notas_paronimo: list[str] = []
        sugestoes: list[tuple[str, tuple[str, ...]]] = []
        vistos: set[str] = set()
        for indice, token in enumerate(tokens):
            if token.tipo != TipoToken.PALAVRA:
                continue
            if token.normalizado in vistos:
                continue
            vistos.add(token.normalizado)
            palavra_exibida = token.texto
            if indice == 0 and texto.lstrip()[:1].islower() and token.texto[:1].isupper():
                palavra_exibida = token.texto[:1].lower() + token.texto[1:]

            par = buscar_par(token.texto)
            if par is not None:
                outras = tuple(p for p in par.palavras if p.casefold() != token.normalizado)
                if outras:
                    notas_paronimo.append(
                        f'"{token.texto}" pode ser confundido com {", ".join(outras)} -- '
                        "confira o sentido antes de aceitar."
                    )

            parece_nome_proprio = (
                token.texto[:1].isupper()
                and token.texto[1:].islower()
                and token.normalizado != "nao"
                and (indice > 0 or texto.lstrip()[:1].isupper())
                and (
                    (indice + 1 < len(tokens) and tokens[indice + 1].texto == ",")
                    or (
                        indice + 1 < len(tokens)
                        and any(
                            entrada.classe.value == "verbo"
                            for entrada in self.dicionario.buscar(tokens[indice + 1].texto)
                        )
                    )
                    or indice > 0
                )
            )
            reconhecida_por_heuristica = (
                analises_contextuais[indice].principal.classe.value != "desconhecida"
                and analises_contextuais[indice].principal.origem.startswith("heuristica")
                and token.normalizado != "nao"
                and not (
                    indice == 0
                    and texto.lstrip()[:1].islower()
                    and analises_contextuais[indice].principal.atributos.get("tipo") == "nome_proprio"
                )
            )
            if (
                token.texto not in self.dicionario
                and not parece_nome_proprio
                and not reconhecida_por_heuristica
            ):
                anterior = None
                posterior = None
                if indice > 0 and tokens[indice - 1].tipo == TipoToken.PALAVRA:
                    anterior = tokens[indice - 1].normalizado
                if indice + 1 < len(tokens) and tokens[indice + 1].tipo == TipoToken.PALAVRA:
                    posterior = tokens[indice + 1].normalizado
                candidatos = self.candidatos_para(
                    palavra_exibida,
                    anterior=anterior,
                    posterior=posterior,
                    contexto=tokens,
                    indice_contexto=indice,
                    usar_contexto=usar_contexto,
                    usar_fonetica=usar_fonetica,
                )
                if candidatos:
                    sugestoes.append((palavra_exibida, tuple(c.forma for c in candidatos[:3])))

        return ResultadoCorrecao(
            original=texto,
            normalizado=normalizado,
            corrigido=corrigido,
            sugestoes_ortografia=tuple(sugestoes),
            notas_paronimo=tuple(notas_paronimo),
            alteracoes_whitelist=tuple(
                (alteracao.antes, alteracao.depois, alteracao.motivo)
                for alteracao in resultado_ortografico.alteracoes
            ),
        )
