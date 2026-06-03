def comparar_campo_1(texto_site, texto_excel):
    if not texto_site or not texto_excel:
        return "DADO AUSENTE"

    # tira o código numérico e o hífen do Excel (ex: "126213-CORRETORA..." → "CORRETORA...")
    texto_excel_str = str(texto_excel).strip()
    if "-" in texto_excel_str:
        texto_excel_limpo = texto_excel_str.split("-", 1)[1].strip()
    else:
        texto_excel_limpo = texto_excel_str

    # limita a 48 caracteres
    texto_excel_limpo = texto_excel_limpo[:48]

    # texto do site já vem limpo
    texto_site_limpo = texto_site.strip()

    if texto_excel_limpo == texto_site_limpo or texto_excel_limpo.startswith(texto_site_limpo):
        return "IGUAL"
    else:
        return "DIFERENTE"
