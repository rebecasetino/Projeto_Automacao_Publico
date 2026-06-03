from navegador import (
    pesquisar_portal_e_preencher_login,
    switch_to_iframe_with_element,
    buscar_criterio_1,
    buscar_criterio_2,
    buscar_criterio_3,
    abrir_cadastro,
    verificar_campo_1,
    verificar_campo_2,
    verificar_campo_3,
    voltar_para_a_busca,
    mudar_tipo_busca,
)
from excel_utils import (
    ler_criterio_1s_excel_e_limpar,
    ler_criterio_2_excel,
    ler_criterio_3_excel,
    salvar_resultados_excel,
)


def main():

    pesquisar_portal_e_preencher_login()
    input("Resolva o captcha e pressione Enter para continuar...")

    try:
        switch_to_iframe_with_element("#Nocriterio_1Cia")
    except Exception as e:
        print("Erro ao trocar de frame:", e)
        input("Pressione Enter para inspecionar manualmente...")

    criterio_1_validas, busca_criterio_2_criterio_1_nao_localizadas = ler_criterio_1s_excel_e_limpar()
    print("criterio_1s válidas:", criterio_1_validas)

    resultados_busca  = []
    itens_nao_localizados = []

    try:
        # --- busca por criterio_1 ---
        for item in criterio_1_validas:
            numero_criterio_1 = item["criterio_1"]
            indice = item["indice"]
            linha_cadastro = buscar_criterio_1(numero_criterio_1, busca_criterio_2_criterio_1_nao_localizadas, indice)
            if linha_cadastro:
                abrir_cadastro(linha_cadastro)
                grupo    = verificar_campo_1()
                tipo     = verificar_campo_2()
                campo_3 = verificar_campo_3()
                resultados_busca.append({
                    "tipo_busca": "criterio_1",
                    "chave":      numero_criterio_1,
                    "campo_1": grupo    or "",
                    "campo_2":   tipo     or "",
                    "campo_3":   campo_3 or "",
                    "resultado_final": "LOCALIZADO",
                    
                })
                voltar_para_a_busca()


            else:                                     
                resultados_busca.append({
                "tipo_busca":       "criterio_1",
                "chave":            numero_criterio_1,
                "campo_1":       "",
                "campo_2":         "",
                "campo_3":         "",
                "criterio_1_buscado": "NAO LOCALIZADA",
                })
            

        # --- busca por criterio_2 ---
        criterio_2_validos, busca_nome_criterio_3_criterio_2s_nao_localizados, df = ler_criterio_2_excel(busca_criterio_2_criterio_1_nao_localizadas)
        print("criterio_2s válidos:", criterio_2_validos)

        if criterio_2_validos:
            mudar_tipo_busca("criterio_2")

            for item in criterio_2_validos:
                criterio_2 = item["criterio_2"]
                indice = item["indice"]
                linha_cadastro = buscar_criterio_2(criterio_2, busca_nome_criterio_3_criterio_2s_nao_localizados, df, indice)
                if linha_cadastro:
                    abrir_cadastro(linha_cadastro)
                    grupo    = verificar_campo_1()
                    tipo     = verificar_campo_2()
                    campo_3 = verificar_campo_3()
                    resultados_busca.append({
                        "tipo_busca": "criterio_2",
                        "chave":      criterio_2,
                        "campo_1": grupo    or "",
                        "campo_2":   tipo     or "",
                        "campo_3":   campo_3 or "",
                        "resultado_final": "LOCALIZADO",
                    })

                    voltar_para_a_busca()

                else:                                      
                    resultados_busca.append({
                    "tipo_busca":    "criterio_2",
                    "chave":         criterio_2,
                    "campo_1":    "",
                    "campo_2":      "",
                    "campo_3":      "",
                    "criterio_2_buscado": "NAO LOCALIZADO",
                    })


            # --- busca por nome/razão social ---
            nome_criterio_3_validos, itens_nao_localizados, df = ler_criterio_3_excel(busca_nome_criterio_3_criterio_2s_nao_localizados)
            print("Nomes/Razões sociais válidos:", nome_criterio_3_validos)

            if nome_criterio_3_validos:
                mudar_tipo_busca("criterio_3")

                for item in nome_criterio_3_validos:
                    nome   = item["criterio_3"]
                    indice = item["indice"]

                    resultado = buscar_criterio_3(nome, itens_nao_localizados, df, indice)

                    if isinstance(resultado, tuple):
                        linha_cadastro, status = resultado
                    else:
                        linha_cadastro, status = None, "NAO LOCALIZADO"

                    if status == "LOCALIZADO" and linha_cadastro:
                        abrir_cadastro(linha_cadastro)
                        grupo    = verificar_campo_1()
                        tipo     = verificar_campo_2()
                        campo_3 = verificar_campo_3()
                        resultados_busca.append({
                            "tipo_busca":      "nome",
                            "chave":           nome,
                            "campo_1":      grupo    or "",
                            "campo_2":        tipo     or "",
                            "campo_3":        campo_3 or "",
                            "resultado_final": "LOCALIZADO",
                        })
                        voltar_para_a_busca()

                    elif status == "INICIO VIGENCIA IGUAL, PRODUTO DIFERENTE":
                        resultados_busca.append({
                            "tipo_busca":      "nome",
                            "chave":           nome,
                            "campo_1":      "",
                            "campo_2":        "",
                            "campo_3":        "",
                            "resultado_final": "INICIO VIGENCIA IGUAL, PRODUTO DIFERENTE",
                        })

                    else:
                        resultados_busca.append({
                            "tipo_busca":      "nome",
                            "chave":           nome,
                            "campo_1":      "",
                            "campo_2":        "",
                            "campo_3":        "",
                            "resultado_final": "NAO LOCALIZADO",
                        })

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        salvar_resultados_excel(resultados_busca, itens_nao_localizados)
        print("Execução finalizada.")

    finally:
        print("Itens não localizados por nome:", itens_nao_localizados)
        salvar_resultados_excel(resultados_busca, itens_nao_localizados)
        print("Execução finalizada.")


if __name__ == "__main__":
    main()
