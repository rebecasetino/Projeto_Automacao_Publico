import pandas as pd
import re
from comparadores import comparar_campo_a


def ler_criterio_1_planilha():
    df = pd.read_excel("base.xlsx")
    registros_fechados = df[df["RESPOSTA"] == "FECHADO"]

    criterio_1_validos = []
    pendentes_criterio_2 = []

    for indice, valor in registros_fechados["COLUNA1"].items():
        if pd.isna(valor):
            pendentes_criterio_2.append({"criterio_1": "", "indice": indice})
            continue

        valor_str = str(valor).strip().replace(" ", "").replace("-", "")

        if valor_str == "" or re.search(r"[A-Za-z]", valor_str):
            pendentes_criterio_2.append({"criterio_1": valor_str, "indice": indice})
        else:
            criterio_1_validos.append({"criterio_1": valor_str, "indice": indice})

    return criterio_1_validos, pendentes_criterio_2


def ler_criterio_2_planilha(pendentes_criterio_2):
    df = pd.read_excel("base.xlsx")

    criterio_2_validos = []
    pendentes_criterio_3 = []
    indices_processados = set()

    for item in pendentes_criterio_2:
        indice = item["indice"]

        if indice in indices_processados:
            continue
        indices_processados.add(indice)

        valor = str(df.loc[indice, "CAMPO13"]).strip()

        if valor in ("", "0", "nan") or "-" in valor:
            pendentes_criterio_3.append({"indice": indice})
            continue

        criterio_2_validos.append({
            "criterio_2": valor,
            "indice": indice
        })

    return criterio_2_validos, pendentes_criterio_3, df


def ler_criterio_3_planilha(pendentes_criterio_3):
    df = pd.read_excel("base.xlsx")

    criterio_3_validos = []
    itens_nao_localizados = []

    for item in pendentes_criterio_3:
        indice = item["indice"]

        valor = str(df.loc[indice, "CLIENTE"]).strip()

        if valor in ("", "0", "nan"):
            itens_nao_localizados.append(indice)
            continue

        criterio_3_validos.append({
            "criterio_3": valor,
            "indice": indice
        })

    return criterio_3_validos, itens_nao_localizados, df


def salvar_resultados_planilha(resultados, nao_localizados_por_criterio_3=None):
    df = pd.read_excel("base.xlsx")

    df["CAMPO_A_LOCALIZADO"] = ""
    df["COMPARACAO_CAMPO_A"] = ""
    df["CAMPO_B_LOCALIZADO"] = ""
    df["CAMPO_C_LOCALIZADO"] = ""
    df["RESULTADO_FINAL"]    = ""

    for resultado in resultados:
        if resultado["tipo_busca"] == "criterio_1":
            filtro = df["COLUNA1"].astype(str).str.replace(" ", "").str.replace("-", "") == str(resultado["chave"]).strip()
        elif resultado["tipo_busca"] == "criterio_2":
            filtro = df["CAMPO13"].astype(str).str.strip() == str(resultado["chave"]).strip()
        else:
            filtro = df["CLIENTE"].astype(str).str.strip() == str(resultado["chave"]).strip()

        df.loc[filtro, "CAMPO_A_LOCALIZADO"] = resultado["campo_a"]
        df.loc[filtro, "CAMPO_B_LOCALIZADO"] = resultado["campo_b"]
        df.loc[filtro, "CAMPO_C_LOCALIZADO"] = resultado["campo_c"]

        valor_referencia = df.loc[filtro, "CAMPO9"].values[0]
        comparacao = comparar_campo_a(resultado["campo_a"], valor_referencia)
        df.loc[filtro, "COMPARACAO_CAMPO_A"] = comparacao

        df.loc[filtro, "RESULTADO_FINAL"] = resultado.get("resultado_final", "LOCALIZADO")

    if nao_localizados_por_criterio_3:
        for indice in nao_localizados_por_criterio_3:
            df.loc[indice, "RESULTADO_FINAL"] = "NAO LOCALIZADO"

    df.to_excel("base_conferida.xlsx", index=False)
    print("Arquivo salvo: base_conferida.xlsx")
