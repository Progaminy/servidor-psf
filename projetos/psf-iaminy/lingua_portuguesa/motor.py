"""Fachada do motor de língua portuguesa."""
from __future__ import annotations

from .cliticos import decompor_cliticos
from .corretor import Corretor
from .desambiguacao import desambiguar_analises
from .fonetica_computavel import codigo_fonetico
from .fluxo import ConstrutorFluxoNatural
from .gramatica import AnalisadorGramatical
from .conhecimento_puro import ConceitoPortugues, ConstrutorConhecimentoPortugues
from .lexico import Dicionario
from .morfologia import AnalisadorMorfologico
from .modelo_ngramas import ModeloNGrama
from .normalizacao import normalizar_texto
from .ponte_matematica import (
    AuditoriaMatematicaPortugues,
    ComparacaoGramaticalFinita,
    PonteMatematicaPortugues,
    ProvaReescritaTerminologica,
)
from .tipos import AnaliseTexto, Diagnostico, FluxoLinguistico, OpcoesAnalise, TipoToken
from .tokenizacao import Tokenizador
from .uso_do_se import identificar_uso_de_se


class MotorPortugues:
    """Orquestra o pipeline sem acoplar as suas etapas.

    Componentes podem ser injetados, permitindo trocar léxico, tokenizador ou
    regras gramaticais sem alterar a API de quem consome o motor.
    """

    def __init__(
        self,
        dicionario: Dicionario | None = None,
        tokenizador: Tokenizador | None = None,
        gramatica: AnalisadorGramatical | None = None,
        modelo_ngrama: ModeloNGrama | None = None,
        corretor: Corretor | None = None,
        opcoes: OpcoesAnalise | None = None,
    ) -> None:
        self.dicionario = dicionario or Dicionario.padrao()
        self.tokenizador = tokenizador or Tokenizador()
        self.morfologia = AnalisadorMorfologico(self.dicionario)
        self.gramatica = gramatica or AnalisadorGramatical()
        self.opcoes = opcoes or OpcoesAnalise.completa()
        self.modelo_ngrama = modelo_ngrama or (
            corretor.modelo_ngrama if corretor is not None else None
        )
        self.corretor = corretor
        if self.opcoes.calcular_contexto:
            self._obter_modelo_ngrama()
        if self.opcoes.corrigir_ortografia:
            self._obter_corretor()
        self.construtor_fluxo = ConstrutorFluxoNatural()
        self.conhecimento_portugues = ConstrutorConhecimentoPortugues()
        self.ponte_matematica = PonteMatematicaPortugues(self.conhecimento_portugues)

    def analisar(
        self, texto: str, *, opcoes: OpcoesAnalise | None = None
    ) -> AnaliseTexto:
        opcoes_reais = opcoes or self.opcoes
        if opcoes_reais.calcular_contexto:
            self._obter_modelo_ngrama()
        tokens = decompor_cliticos(self.tokenizador.tokenizar(texto), self.dicionario)
        morfologia_bruta = self.morfologia.analisar(tokens)
        # Preserva o aviso que explica uma promoção contextual, mas a
        # gramática e o fluxo passam a consumir a leitura promovida.
        diagnosticos_ambiguidade = tuple(
            item
            for item in self.gramatica.verificar(morfologia_bruta)
            if item.codigo == "CATEGORIA_INCOMPATIVEL"
        )
        morfologia = desambiguar_analises(morfologia_bruta)
        diagnosticos = diagnosticos_ambiguidade + tuple(
            item
            for item in self.gramatica.verificar(morfologia)
            if item.codigo != "CATEGORIA_INCOMPATIVEL"
        )
        correcao = None
        if opcoes_reais.corrigir_ortografia:
            correcao = self._obter_corretor().corrigir_texto(
                texto,
                usar_contexto=opcoes_reais.calcular_contexto,
                usar_fonetica=opcoes_reais.calcular_fonetica,
            )
            diagnosticos += self._diagnosticos_correcao(texto, correcao)
        usos_do_se = self._usos_do_se(texto)
        constituintes = self.gramatica.reconhecer_constituintes(morfologia)
        if "indeterminacao" in usos_do_se:
            constituintes = tuple(
                item for item in constituintes if item.funcao != "sujeito_posposto"
            )
        fluxo = self.construtor_fluxo.construir(
            texto, tokens, morfologia, diagnosticos, constituintes
        )
        return AnaliseTexto(
            texto=texto,
            texto_normalizado=normalizar_texto(texto),
            tokens=tokens,
            morfologia=morfologia,
            diagnosticos=diagnosticos,
            constituintes=constituintes,
            fluxo=fluxo,
            correcao=correcao,
            probabilidades_contextuais=(
                self._probabilidades_contextuais(morfologia)
                if opcoes_reais.calcular_contexto
                else ()
            ),
            codigos_foneticos=(
                tuple(
                    (item.token.texto, codigo_fonetico(item.token.texto))
                    for item in morfologia
                    if item.token.tipo == TipoToken.PALAVRA
                )
                if opcoes_reais.calcular_fonetica
                else ()
            ),
            usos_do_se=usos_do_se,
            recursos_executados=(
                "tokenizacao",
                "cliticos",
                "morfologia",
                "desambiguacao",
                "gramatica",
                "uso_do_se",
                "fluxo",
            )
            + (("correcao",) if opcoes_reais.corrigir_ortografia else ())
            + (("ngramas",) if opcoes_reais.calcular_contexto else ())
            + (("fonetica",) if opcoes_reais.calcular_fonetica else ()),
        )

    def _obter_modelo_ngrama(self) -> ModeloNGrama:
        if self.modelo_ngrama is None:
            self.modelo_ngrama = ModeloNGrama()
        if self.corretor is not None and self.corretor.modelo_ngrama is None:
            self.corretor.modelo_ngrama = self.modelo_ngrama
        return self.modelo_ngrama

    def _obter_corretor(self) -> Corretor:
        if self.corretor is None:
            self.corretor = Corretor(
                dicionario=self.dicionario,
                modelo_ngrama=self.modelo_ngrama,
                gramatica=self.gramatica,
                tokenizador=self.tokenizador,
                carregar_modelo=False,
            )
        return self.corretor

    def _probabilidades_contextuais(self, morfologia) -> tuple[tuple[str, float], ...]:
        resultado: list[tuple[str, float]] = []
        anterior: str | None = None
        for item in morfologia:
            if item.token.tipo != TipoToken.PALAVRA:
                if item.token.texto in ".!?":
                    anterior = None
                continue
            resultado.append(
                (
                    item.token.texto,
                    self._obter_modelo_ngrama().probabilidade_condicional(
                        item.principal.lema, anterior
                    ),
                )
            )
            anterior = item.principal.lema
        return tuple(resultado)

    def _usos_do_se(self, texto: str) -> tuple[str, ...]:
        uso = identificar_uso_de_se(texto, self.dicionario)
        return (uso.value,) if uso is not None else ()

    @staticmethod
    def _diagnosticos_correcao(texto: str, correcao) -> tuple[Diagnostico, ...]:
        resultado: list[Diagnostico] = []
        texto_cf = texto.casefold()
        for palavra, sugestoes in correcao.sugestoes_ortografia:
            inicio = texto_cf.find(palavra.casefold())
            inicio = max(inicio, 0)
            resultado.append(
                Diagnostico(
                    codigo="ORTOGRAFIA_SUGESTAO",
                    mensagem=f"Palavra possivelmente desconhecida: “{palavra}”.",
                    inicio=inicio,
                    fim=inicio + len(palavra),
                    sugestao=", ".join(sugestoes),
                )
            )
        for antes, depois, motivo in correcao.alteracoes_whitelist:
            inicio = texto_cf.find(antes.casefold())
            inicio = max(inicio, 0)
            resultado.append(
                Diagnostico(
                    codigo="ORTOGRAFIA_CORRECAO_CONHECIDA",
                    mensagem=f"“{antes}” corresponde a um erro conhecido ({motivo}).",
                    inicio=inicio,
                    fim=inicio + len(antes),
                    sugestao=depois,
                )
            )
        for nota in correcao.notas_paronimo:
            resultado.append(Diagnostico("PARONIMO", nota, 0, len(texto)))
        return tuple(resultado)

    def ler(
        self, texto: str, *, opcoes: OpcoesAnalise | None = None
    ) -> AnaliseTexto:
        """Leitura operacional: conserva o texto e devolve análise auditável."""
        return self.analisar(texto, opcoes=opcoes)

    def interpretar_sentido(self, texto: str) -> dict[str, object]:
        """Interpretação interna limitada ao léxico e à gramática materializados."""
        analise = self.analisar(texto, opcoes=OpcoesAnalise.completa())
        lemas = tuple(
            item.leituras[0].lema
            for item in analise.morfologia
            if item.leituras
        )
        return {
            "texto": texto,
            "lemas_reconhecidos": lemas,
            "diagnosticos": tuple(d.mensagem for d in analise.diagnosticos),
            "probabilidades_contextuais": analise.probabilidades_contextuais,
            "codigos_foneticos": analise.codigos_foneticos,
            "limite": "Não inventa contexto externo nem intenção não sustentada pelo texto.",
        }

    def revisar_escrita(self, texto: str) -> dict[str, object]:
        """Revisa sem apagar o original e sem aplicar correção silenciosa."""
        analise = self.analisar(texto, opcoes=OpcoesAnalise.completa())
        return {
            "original": texto,
            "normalizado_para_analise": analise.texto_normalizado,
            "diagnosticos": tuple(d.mensagem for d in analise.diagnosticos),
            "correcao_proposta": analise.correcao.corrigido,
            "sugestoes_ortografia": analise.correcao.sugestoes_ortografia,
            "alteracoes_conhecidas": analise.correcao.alteracoes_whitelist,
            "estado": "REVISÃO_ASSISTIDA; nenhuma alteração automática foi imposta",
        }

    def produzir_texto(self, unidades: tuple[str, ...] | list[str]) -> str:
        """Compõe unidades fornecidas; não inventa factos ou conteúdo ausente."""
        partes: list[str] = []
        for unidade in unidades:
            trecho = " ".join(str(unidade).strip().split())
            if not trecho:
                continue
            if trecho[-1] not in ".!?":
                trecho += "."
            partes.append(trecho)
        return " ".join(partes)

    def escrever(self, unidades: tuple[str, ...] | list[str]) -> str:
        """Alias explícito de produção textual controlada."""
        return self.produzir_texto(unidades)

    def fluxo_natural(
        self, texto: str, *, opcoes: OpcoesAnalise | None = None
    ) -> FluxoLinguistico:
        """Devolve a escada som → letra → palavra → significado → texto."""
        fluxo = self.analisar(texto, opcoes=opcoes).fluxo
        assert fluxo is not None
        return fluxo

    def explicar_fluxo(self, texto: str) -> tuple[str, ...]:
        fluxo = self.fluxo_natural(texto)
        return tuple(
            f"{estagio.ordem}. {estagio.nome}: {estagio.descricao} "
            f"({estagio.quantidade})"
            for estagio in fluxo.estagios
        )


    def conhecimento_puro(self) -> tuple[ConceitoPortugues, ...]:
        """Devolve os conceitos puros de Português construídos no PSF."""
        return self.conhecimento_portugues.todos()

    def caminho_conhecimento_portugues(self) -> tuple[str, ...]:
        """Caminho natural: diferença → som → grafema → palavra → texto."""
        return self.conhecimento_portugues.caminho_natural()

    def funcionamento_portugues(self) -> tuple[str, ...]:
        """Funcionamento objetivo do conhecimento de Português no motor."""
        return self.conhecimento_portugues.funcionamento()

    def definir_conceito_puro(self, nome: str) -> str | None:
        conceito = self.conhecimento_portugues.buscar(nome)
        if conceito is None:
            return None
        return conceito.construcao

    def funcao_conceito_puro(self, nome: str) -> str | None:
        conceito = self.conhecimento_portugues.buscar(nome)
        if conceito is None:
            return None
        return conceito.funcao

    def dependencias_conceito_puro(self, nome: str) -> tuple[str, ...]:
        return self.conhecimento_portugues.dependencias_de(nome)

    def trilho_ate_conceito_puro(self, nome: str) -> tuple[str, ...]:
        return self.conhecimento_portugues.trilho_ate(nome)

    def lacunas_conhecimento_portugues(self) -> tuple[str, ...]:
        return self.conhecimento_portugues.lacunas()

    def fronteiras_abertas_portugues(self) -> dict[str, str]:
        """Fronteiras do português vivo que dependem de contexto ou dados reais."""
        return self.conhecimento_portugues.fronteiras_abertas()

    def limites_operacionais_portugues(self) -> dict[str, str]:
        """Conceitos construídos cuja automatização ainda pode ser parcial."""
        return self.conhecimento_portugues.limites_operacionais()

    def mestria_conceitual_portugues(self) -> bool:
        """Confirma domínio interno sem lacunas, sem prometer mundo fechado."""
        return self.conhecimento_portugues.mestria_conceitual()

    def dependencias_transitivas_conceito_puro(self, nome: str) -> tuple[str, ...]:
        """Devolve todas as dependências anteriores necessárias ao conceito."""
        return self.conhecimento_portugues.dependencias_transitivas_de(nome)

    def temas_consulta_conhecimento_portugues(self) -> tuple[str, ...]:
        """Lista índices temáticos sem lhes dar autoridade estrutural."""
        return self.conhecimento_portugues.temas_consulta()

    def conceitos_por_tema(self, tema: str) -> tuple[ConceitoPortugues, ...]:
        """Consulta por tema; a linha real continua definida por ordem e dependências."""
        return self.conhecimento_portugues.por_tema(tema)

    def camadas_conhecimento_portugues(self) -> tuple[str, ...]:
        """Compatibilidade legada. As antigas camadas são apenas temas de consulta."""
        return self.temas_consulta_conhecimento_portugues()

    def conceitos_por_camada(self, camada: str) -> tuple[ConceitoPortugues, ...]:
        """Compatibilidade legada. Use :meth:`conceitos_por_tema`."""
        return self.conceitos_por_tema(camada)

    def buscar_conceitos_puros(self, trecho: str) -> tuple[ConceitoPortugues, ...]:
        """Busca por nome, construção ou função dentro do conhecimento puro."""
        return self.conhecimento_portugues.buscar_texto(trecho)

    def estatisticas_conhecimento_portugues(self) -> dict[str, int]:
        """Mede o conhecimento materializado sem fingir completude."""
        return self.conhecimento_portugues.estatisticas()

    def aliases_conhecimento_portugues(self) -> dict[str, str]:
        """Termos equivalentes que apontam para um conceito canónico único."""
        return self.conhecimento_portugues.aliases()

    def auditar_estrutura_portugues(self) -> AuditoriaMatematicaPortugues:
        """Usa relações e grafos como validação, nunca como fonte linguística."""
        return self.ponte_matematica.auditar_dependencias()

    def caminho_minimo_conceito_puro(self, nome: str) -> tuple[str, ...]:
        """Menor caminho real de dependências até um conceito."""
        return self.ponte_matematica.caminho_minimo_ate(nome)

    def conceitos_estruturais_portugues(self, limite: int = 10) -> tuple[tuple[str, int], ...]:
        """Conceitos que sustentam mais dependentes diretos."""
        return self.ponte_matematica.conceitos_estruturais(limite)

    def comparar_padrao_gramatical_finito(
        self, texto: str, limite_passos: int = 12
    ) -> ComparacaoGramaticalFinita:
        """Compara, sem declarar completude, o padrão morfológico do texto."""
        return self.ponte_matematica.comparar_gramatica_finita(
            self.analisar(texto), limite_passos
        )

    def provar_equivalencia_terminologica(
        self, termo: str
    ) -> ProvaReescritaTerminologica:
        """Mostra a reescrita auditável de alias para conceito canónico."""
        return self.ponte_matematica.provar_alias(termo)

    def definir(self, palavra: str) -> tuple[str, ...]:
        return self.dicionario.definir(palavra)

    def sugerir(self, palavra: str, limite: int = 5) -> tuple[str, ...]:
        return self.dicionario.sugerir(palavra, limite)

    def estatisticas_lexico(self) -> dict[str, int]:
        """Resumo do dicionário interno, útil para auditoria do português amplo."""
        return {
            "lemas": len(self.dicionario.lemas()),
            "formas": self.dicionario.total_formas(),
            "leituras": len(self.dicionario),
        }
