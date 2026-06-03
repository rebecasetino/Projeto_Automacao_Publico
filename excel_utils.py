import pandas as pd
import re
from comparadores import comparar_campo_1


def ler_criterio_1s_excel_e_limpar():
    df = pd.read_excel("base.xlsx")
    itens_fechados = df[df["RESPOSTA"] == "RESPOSTA_1"]


    criterio_1_validas = []
    busca_criterio_2_criterio_1_nao_localizadas = []

    for indice, valor in itens_fechados["criterio_1"].items():
        
        status = "NAO DEFINIDO"

        # pula se já foi buscada anteriormente
        if "CRITERIO_1_BUSCADO" in df.columns:
            status = str(df.loc[indice, "CRITERIO_1_BUSCADO"])

            if status == "NAO LOCALIZADA":
                busca_criterio_2_criterio_1_nao_localizadas.append({"criterio_1": str(valor), "indice": indice})
                continue
            if status == "LOCALIZADA":
                continue


        if pd.isna(valor):
            busca_criterio_2_criterio_1_nao_localizadas.append({"criterio_1": "", "indice": indice})
            continue

        criterio_1_str = str(valor).replace("\xa0", "").strip().replace(" ", "").replace("-", "")

        if criterio_1_str == "" or re.search(r"[A-Za-z]", criterio_1_str) or len(criterio_1_str) < 6:
            busca_criterio_2_criterio_1_nao_localizadas.append({"criterio_1": criterio_1_str, "indice": indice})
        else:
            criterio_1_validas.append({"criterio_1": criterio_1_str, "indice": indice})

        

    return criterio_1_validas, busca_criterio_2_criterio_1_nao_localizadas


def ler_criterio_2_excel(busca_criterio_2_criterio_1_nao_localizadas):
    df = pd.read_excel("base.xlsx")

    criterio_2_validos = []
    busca_nome_criterio_3_criterio_2s_nao_localizados = []
    indices_processados = set()

    for item in busca_criterio_2_criterio_1_nao_localizadas:
        indice = item["indice"]

        if indice in indices_processados:
            continue
        indices_processados.add(indice)

         # pula se já foi buscado pelo criterio_2
        if "criterio_2_BUSCADO" in df.columns:
            if str(df.loc[indice, "criterio_2_BUSCADO"]).strip() == "NAO LOCALIZADO":
                busca_nome_criterio_3_criterio_2s_nao_localizados.append({"indice": indice})
                continue

        if "criterio_2_BUSCADO" in df.columns:
            if str(df.loc[indice, "criterio_2_BUSCADO"]).strip() == "LOCALIZADO":
                continue
        
        criterio_2 = str(df.loc[indice, "CAMPO13"]).strip()

        if criterio_2 in ("", "0", "nan") or "-" in criterio_2:
            busca_nome_criterio_3_criterio_2s_nao_localizados.append({"indice": indice})
            continue

        criterio_2_validos.append({
            "criterio_2": criterio_2,
            "indice": indice
        })

    return criterio_2_validos, busca_nome_criterio_3_criterio_2s_nao_localizados, df


def ler_criterio_3_excel(busca_nome_criterio_3_criterio_2s_nao_localizados):
    df = pd.read_excel("base.xlsx")

    nome_criterio_3_validos = []
    itens_nao_localizados = []

    for item in busca_nome_criterio_3_criterio_2s_nao_localizados:
        indice = item["indice"]

        criterio_3 = str(df.loc[indice, "CLIENTE"]).strip()

        if criterio_3 in ("", "0", "nan"):
            itens_nao_localizados.append(indice)
            continue

        nome_criterio_3_validos.append({
            "criterio_3": criterio_3,
            "indice": indice
        })

    return nome_criterio_3_validos, itens_nao_localizados, df


def salvar_resultados_excel(resultados, nao_localizados_por_nome=None):
    df = pd.read_excel("base.xlsx")

    # só cria as colunas se não existirem — preserva o progresso anterior
    if "CRITERIO_1_BUSCADO" not in df.columns:
        df["CRITERIO_1_BUSCADO"]      = ""
    if "criterio_2_BUSCADO" not in df.columns:
        df["criterio_2_BUSCADO"]        = ""
    if "campo_1_LOCALIZADO" not in df.columns:
        df["campo_1_LOCALIZADO"] = ""
    if "CAMPO_2_LOCALIZADO" not in df.columns:
        df["CAMPO_2_LOCALIZADO"]   = ""
    if "CAMPO_3_LOCALIZADO" not in df.columns:
        df["CAMPO_3_LOCALIZADO"]   = ""
    if "RESULTADO_FINAL" not in df.columns:
        df["RESULTADO_FINAL"]       = ""

    

    df['CRITERIO_1_BUSCADO'] = df['CRITERIO_1_BUSCADO'].astype(str)
    df['criterio_2_BUSCADO'] = df['criterio_2_BUSCADO'].astype(str)
    df['campo_1_LOCALIZADO'] = df['campo_1_LOCALIZADO'].astype(str)
    df['CAMPO_2_LOCALIZADO'] = df['CAMPO_2_LOCALIZADO'].astype(str)
    df['CAMPO_3_LOCALIZADO'] = df['CAMPO_3_LOCALIZADO'].astype(str)
    df['RESULTADO_FINAL'] = df['RESULTADO_FINAL'].astype(str)
        

    for resultado in resultados:
        if resultado["tipo_busca"] == "criterio_1":
            filtro = df["criterio_1"].astype(str).str.replace("\xa0", "").str.split(".").str[0].str.replace(" ", "").str.replace("-", "") == str(resultado["chave"]).strip()
            df.loc[filtro, "CRITERIO_1_BUSCADO"] = resultado.get("criterio_1_buscado", "LOCALIZADA")
            if resultado.get("criterio_1_buscado") == "NAO LOCALIZADA":
                continue

        elif resultado["tipo_busca"] == "criterio_2":
            filtro = df["CAMPO13"].astype(str).str.replace("\xa0", "").str.strip() == str(resultado["chave"]).strip()
            df.loc[filtro, "criterio_2_BUSCADO"] = resultado.get("criterio_2_buscado", "LOCALIZADO")
            if resultado.get("criterio_2_buscado") == "NAO LOCALIZADO":
                continue

        else:
            filtro = df["CLIENTE"].astype(str).str.replace("\xa0", "").str.strip() == str(resultado["chave"]).strip()

        df.loc[filtro, "campo_1_LOCALIZADO"] = resultado["campo_1"]
        df.loc[filtro, "CAMPO_2_LOCALIZADO"]   = resultado["campo_2"]
        df.loc[filtro, "CAMPO_3_LOCALIZADO"]   = resultado["campo_3"]

        # COMPARAR campo_1 INATIVO POR ENQUANTO
        # campo9_valor = df.loc[filtro, "CAMPO9"].values[0]
        # comparacao = comparar_campo_1(resultado["campo_1"], campo9_valor)
        # df.loc[filtro, "COMPARACAO_campo_1"] = comparacao

        df.loc[filtro, "RESULTADO_FINAL"] = resultado.get("resultado_final", "LOCALIZADO")

    if nao_localizados_por_nome:
        for indice in nao_localizados_por_nome:
            df.loc[indice, "RESULTADO_FINAL"] = "NAO LOCALIZADO"

    df.to_excel("base_conferida.xlsx", index=False)
    print("Arquivo salvo: base_conferida.xlsx")
