from navegador import (
    acessar_sistema_e_preencher_login,
    switch_to_iframe_with_element,
    buscar_por_criterio_1,
    buscar_por_criterio_2,
    buscar_por_criterio_3,
    abrir_registro,
    verificar_campo_a,
    verificar_campo_b,
    verificar_campo_c,
    voltar_para_a_busca,
    mudar_modo_busca,
)
from excel_utils import (
    ler_criterio_1_planilha,
    ler_criterio_2_planilha,
    ler_criterio_3_planilha,
    salvar_resultados_planilha,
)


def main():

    acessar_sistema_e_preencher_login()
    input("Conclua a etapa de verificacao e pressione Enter para continuar...")

    try:
        switch_to_iframe_with_element("#seletor_criterio_1")
    except Exception as e:
        print("Erro ao trocar de frame:", e)
        input("Pressione Enter para inspecionar manualmente...")

    criterio_1_validos, pendentes_criterio_2 = ler_criterio_1_planilha()
    print("Criterio 1 validos:", criterio_1_validos)

    resultados_busca      = []
    itens_nao_localizados = []

    try:
        # --- busca por criterio 1 ---
        for item in criterio_1_validos:
            valor_criterio_1 = item["criterio_1"]
            indice = item["indice"]
            registro = buscar_por_criterio_1(valor_criterio_1, pendentes_criterio_2, indice)
            if registro:
                abrir_registro(registro)
                campo_a = verificar_campo_a()
                campo_b = verificar_campo_b()
                campo_c = verificar_campo_c()
                resultados_busca.append({
                    "tipo_busca": "criterio_1",
                    "chave":      valor_criterio_1,
                    "campo_a":    campo_a or "",
                    "campo_b":    campo_b or "",
                    "campo_c":    campo_c or "",
                })
                voltar_para_a_busca()

        # --- busca por criterio 2 ---
        criterio_2_validos, pendentes_criterio_3, df = ler_criterio_2_planilha(pendentes_criterio_2)
        print("Criterio 2 validos:", criterio_2_validos)

        if criterio_2_validos:
            mudar_modo_busca("modo_criterio_2")

            for item in criterio_2_validos:
                valor_criterio_2 = item["criterio_2"]
                indice = item["indice"]
                registro = buscar_por_criterio_2(valor_criterio_2, pendentes_criterio_3, df, indice)
                if registro:
                    abrir_registro(registro)
                    campo_a = verificar_campo_a()
                    campo_b = verificar_campo_b()
                    campo_c = verificar_campo_c()
                    resultados_busca.append({
                        "tipo_busca": "criterio_2",
                        "chave":      valor_criterio_2,
                        "campo_a":    campo_a or "",
                        "campo_b":    campo_b or "",
                        "campo_c":    campo_c or "",
                    })
                    voltar_para_a_busca()

            # --- busca por criterio 3 ---
            criterio_3_validos, itens_nao_localizados, df = ler_criterio_3_planilha(pendentes_criterio_3)
            print("Criterio 3 validos:", criterio_3_validos)

            if criterio_3_validos:
                mudar_modo_busca("modo_criterio_3")

                for item in criterio_3_validos:
                    valor_criterio_3 = item["criterio_3"]
                    indice = item["indice"]

                    resultado = buscar_por_criterio_3(valor_criterio_3, itens_nao_localizados, df, indice)

                    if isinstance(resultado, tuple):
                        registro, status = resultado
                    else:
                        registro, status = None, "resultado_3"

                    if status == "resultado_1" and registro:
                        abrir_registro(registro)
                        campo_a = verificar_campo_a()
                        campo_b = verificar_campo_b()
                        campo_c = verificar_campo_c()
                        resultados_busca.append({
                            "tipo_busca":      "criterio_3",
                            "chave":           valor_criterio_3,
                            "campo_a":         campo_a or "",
                            "campo_b":         campo_b or "",
                            "campo_c":         campo_c or "",
                            "resultado_final": "resultado_1",
                        })
                        voltar_para_a_busca()

                    elif status == "resultado_2":
                        resultados_busca.append({
                            "tipo_busca":      "criterio_3",
                            "chave":           valor_criterio_3,
                            "campo_a":         "",
                            "campo_b":         "",
                            "campo_c":         "",
                            "resultado_final": "resultado_2",
                        })

                    else:
                        resultados_busca.append({
                            "tipo_busca":      "criterio_3",
                            "chave":           valor_criterio_3,
                            "campo_a":         "",
                            "campo_b":         "",
                            "campo_c":         "",
                            "resultado_final": "resultado_3",
                        })

    except Exception as e:
        print(f"Erro durante a execucao: {e}")

    finally:
        print("Itens nao localizados por criterio 3:", itens_nao_localizados)
        salvar_resultados_planilha(resultados_busca, itens_nao_localizados)
        print("Execucao finalizada.")


if __name__ == "__main__":
    main()
