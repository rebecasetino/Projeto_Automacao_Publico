def comparar_campo_a(valor_sistema, valor_planilha):
    if not valor_sistema or not valor_planilha:
        return "DADO AUSENTE"

    valor_planilha_str = str(valor_planilha).strip()
    if "-" in valor_planilha_str:
        valor_planilha_limpo = valor_planilha_str.split("-", 1)[1].strip()
    else:
        valor_planilha_limpo = valor_planilha_str

    valor_planilha_limpo = valor_planilha_limpo[:48]

    valor_sistema_limpo = valor_sistema.strip()

    if valor_planilha_limpo == valor_sistema_limpo or valor_planilha_limpo.startswith(valor_sistema_limpo):
        return "IGUAL"
    else:
        return "DIFERENTE"
