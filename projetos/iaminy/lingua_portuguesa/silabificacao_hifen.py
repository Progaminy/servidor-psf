# -*- coding: utf-8 -*-
"""Módulo de Divisão Silábica e Hifenização do PSF-IAminy.

Construção pura baseada em encontros vocálicos (hiatos vs ditongos/tritongos),
encontros consonânticos separáveis e inseparáveis, e regras mecânicas de hifenização
do Acordo Ortográfico para combinação de prefixo + base.
"""
from __future__ import annotations

import re

# Vogais e semivogais
_VOGAIS_TODAS = set("aeiouáéíóúâêôãõàüAEIOUÁÉÍÓÚÂÊÔÃÕÀÜ")
_VOGAIS_CENTRAIS = set("aeoáéóâêôãõàAEOÁÉÓÂÊÔÃÕÀ")
_SEMIVOGAIS = set("iuíúüIUÍÚÜ")

# Dígrafos e encontros consonânticos
_DIGRAFOS_INSEPARAVEIS = {"ch", "lh", "nh", "CH", "LH", "NH", "Ch", "Lh", "Nh"}
_DIGRAFOS_SEPARAVEIS = {"rr", "ss", "sc", "sç", "xc", "RR", "SS", "SC", "SÇ", "XC"}

_ENCONTROS_INSEPARAVEIS_L_R = {
    "bl", "cl", "dl", "fl", "gl", "pl", "tl",
    "br", "cr", "dr", "fr", "gr", "pr", "tr", "vr",
    "BL", "CL", "DL", "FL", "GL", "PL", "TL",
    "BR", "CR", "DR", "FR", "GR", "PR", "TR", "VR"
}


def eh_vogal(caractere: str) -> bool:
    """Verifica se um caractere é vogal em português."""
    return caractere in _VOGAIS_TODAS


def eh_consoante(caractere: str) -> bool:
    """Verifica se um caractere é consoante."""
    return caractere.isalpha() and not eh_vogal(caractere)


def dividir_silabas(palavra: str) -> tuple[str, ...]:
    """Divide uma palavra em suas sílabas constituintes.

    Exemplos:
        "caixa" -> ("cai", "xa")
        "saúde" -> ("sa", "ú", "de")
        "cachorro" -> ("ca", "chor", "ro")
        "pássaro" -> ("pás", "sa", "ro")
        "brasil" -> ("bra", "sil")
        "poeta" -> ("po", "e", "ta")
    """
    if not palavra or not palavra.isalpha():
        return (palavra,) if palavra else ()

    if len(palavra) <= 2:
        return (palavra,)

    # Casos simples com hífen já presente (ex.: palavras compostas)
    if "-" in palavra:
        partes_hifen = palavra.split("-")
        resultado = []
        for p in partes_hifen:
            resultado.extend(dividir_silabas(p))
        return tuple(resultado)

    # Identificar posições dos núcleos vocálicos e realizar corte
    corte_indices: list[int] = []
    tamanho = len(palavra)

    i = 0
    while i < tamanho - 1:
        c1 = palavra[i]
        c2 = palavra[i + 1]
        c3 = palavra[i + 2] if i + 2 < tamanho else ""
        c4 = palavra[i + 3] if i + 3 < tamanho else ""

        par = (c1 + c2).casefold()

        # Dígrafos separáveis (rr, ss, sc, sç, xc) -> corta entre as duas consoantes
        if par in _DIGRAFOS_SEPARAVEIS:
            corte_indices.append(i + 1)
            i += 2
            continue

        # Dígrafos inseparáveis (ch, lh, nh) ou encontros consonânticos com l/r (br, pr, cl...)
        if par in _DIGRAFOS_INSEPARAVEIS or par in _ENCONTROS_INSEPARAVEIS_L_R:
            # Se havia uma consoante antes que não faz parte do grupo, corta antes do grupo
            if i > 0 and eh_consoante(palavra[i - 1]) and i not in corte_indices:
                corte_indices.append(i)
            i += 2
            continue

        # Encontro Vogal + Vogal (Hiato vs Ditongo)
        if eh_vogal(c1) and eh_vogal(c2):
            c1_l = c1.casefold()
            c2_l = c2.casefold()

            # Hiato evidente: vogais iguais (ex.: "cooperar" -> co-o-pe-rar, "vôo" -> vô-o, "saara" -> sa-a-ra)
            if c1_l == c2_l:
                corte_indices.append(i + 1)
            # Hiato com segunda vogal tônica acentuada (ex.: "sa-ú-de", "ba-ú", "pa-ís")
            elif c2_l in "áéíóúà":
                corte_indices.append(i + 1)
            # Hiato entre vogais centrais/abertas diferentes (ex.: "po-e-ta", "te-a-tro", "mo-eda")
            elif c1_l in "aeo" and c2_l in "aeo":
                corte_indices.append(i + 1)
            i += 1
            continue

        # Encontro Vogal + Consoante + Vogal (V-C-V -> corta antes da consoante)
        if eh_vogal(c1) and eh_consoante(c2) and eh_vogal(c3):
            corte_indices.append(i + 1)
            i += 1
            continue

        # Encontro Vogal + Consoante + Consoante + Vogal (V-C-C-V)
        if eh_vogal(c1) and eh_consoante(c2) and eh_consoante(c3) and eh_vogal(c4):
            par_cc = (c2 + c3).casefold()
            if par_cc in _DIGRAFOS_INSEPARAVEIS or par_cc in _ENCONTROS_INSEPARAVEIS_L_R:
                corte_indices.append(i + 1)
            else:
                corte_indices.append(i + 2)
            i += 2
            continue

        i += 1

    # Construir fatias de sílabas ordenando os cortes
    corte_indices = sorted(list(set(corte_indices)))
    silabas: list[str] = []
    inicio = 0

    for idx in corte_indices:
        if idx > inicio and idx < tamanho:
            silabas.append(palavra[inicio:idx])
            inicio = idx

    if inicio < tamanho:
        silabas.append(palavra[inicio:])

    return tuple(silabas) if silabas else (palavra,)


def decidir_hifen_prefixo(prefixo: str, base: str) -> dict[str, str | bool | None]:
    """Decide mecanicamente a junção de um prefixo com uma palavra base.

    Regras do Acordo Ortográfico:
    1. Base começa com 'h' -> sempre usa hífen (ex: anti-higiênico, super-homem).
    2. Prefixo termina na mesma vogal em que a base começa -> hífen (ex: micro-onda, anti-inflamatório).
    3. Prefixo termina em vogal e a base começa com vogal diferente -> junta sem hífen (ex: autoescola, semianalfabeto).
    4. Prefixo termina em vogal e a base começa com 'r' ou 's' -> dobra 'rr'/'ss' e junta sem hífen (ex: minissaia, autorreferência).
    5. Prefixo termina em 'r' e a base começa com 'r' -> hífen (ex: inter-relação, super-resistente).
    6. Prefixo termina em consoante e a base começa com vogal/outra consoante -> junta sem hífen (ex: superinteressante, subcategoria).

    Retorna um dicionário com o resultado formado e o motivo da decisão.
    """
    pref = prefixo.strip().casefold()
    bas = base.strip().casefold()

    if not pref or not bas:
        return {"resultado": f"{prefixo}{base}", "usa_hifen": False, "motivo": "Entrada inválida ou vazia"}

    ult_pref = pref[-1]
    pri_base = bas[0]

    # Regra 1: Base inicia com 'h'
    if pri_base == "h":
        return {
            "resultado": f"{prefixo}-{base}",
            "usa_hifen": True,
            "motivo": "Base iniciada por 'h' exige hífen",
        }

    # Prefixo termina em vogal
    if eh_vogal(ult_pref):
        # Regra 2: Mesma vogal
        if ult_pref == pri_base:
            return {
                "resultado": f"{prefixo}-{base}",
                "usa_hifen": True,
                "motivo": "Vogais iguais no encontro entre prefixo e base exigem hífen",
            }
        # Regra 4: Base começa com 'r' ou 's'
        if pri_base in ("r", "s"):
            base_dobrada = pri_base + base
            return {
                "resultado": f"{prefixo}{base_dobrada}",
                "usa_hifen": False,
                "motivo": "Prefixo terminado em vogal + base com 'r'/'s' dobra a consoante sem hífen",
            }
        # Regra 3: Vogais diferentes ou consoante normal
        return {
            "resultado": f"{prefixo}{base}",
            "usa_hifen": False,
            "motivo": "Vogais diferentes ou prefixo em vogal seguido de consoante simples unem-se sem hífen",
        }

    # Prefixo termina em consoante
    if eh_consoante(ult_pref):
        # Regra 5: Consoantes iguais (ex: inter-relação, sub-bibliotecário)
        if ult_pref == pri_base:
            return {
                "resultado": f"{prefixo}-{base}",
                "usa_hifen": True,
                "motivo": "Consoantes iguais no encontro entre prefixo e base exigem hífen",
            }
        # Regra 6: Consoantes diferentes ou consoante + vogal
        return {
            "resultado": f"{prefixo}{base}",
            "usa_hifen": False,
            "motivo": "Consoantes diferentes unem-se sem hífen",
        }

    return {"resultado": f"{prefixo}{base}", "usa_hifen": False, "motivo": "Caso geral sem hífen"}
