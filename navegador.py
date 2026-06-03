from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import pandas as pd
import time

import config
from driver import driver


def pesquisar_portal_e_preencher_login():
    driver.get(config.link)

    corretora = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#Corretor"))
    )
    corretora.click()
    corretora.send_keys(config.corretora)

    usuario = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#Usuario"))
    )
    usuario.click()
    usuario.send_keys(config.usuario)

    senha = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#Senha"))
    )
    senha.click()
    senha.send_keys(config.senha)


def switch_to_iframe_with_element(selector, by=By.CSS_SELECTOR):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i, iframe in enumerate(iframes):
        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)
        try:
            driver.find_element(by, selector)
            print(f"Elemento encontrado no iframe {i}")
            return True
        except:
            continue
    driver.switch_to.default_content()
    return False


def localizar_linha_cadastro_pela_criterio_1(numero_criterio_1, busca_criterio_2_criterio_1_nao_localizadas, indice):
    time.sleep(1)

    try:
        linhas = driver.find_elements(By.XPATH, "//td[@aria-describedby='GridConsulta_InicioVigencia']")
        print(f"Total de células encontradas na coluna vigência: {len(linhas)}")

        if len(linhas) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"criterio_1 NAO LOCALIZADA NO SITE: {numero_criterio_1}")
            except TimeoutException:
                pass

            busca_criterio_2_criterio_1_nao_localizadas.append({"criterio_1": numero_criterio_1, "indice": indice})
            driver.switch_to.frame("ZonaInterna")
            return None

        linha_cadastro = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{numero_criterio_1}')]"))
        )
        print("Texto da célula:", linha_cadastro.text)
        return linha_cadastro

    except StaleElementReferenceException:
        linha_cadastro = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@id, ',0,1')]/td[7]"))
        )
        print("Texto da célula (relocalizado):", linha_cadastro.text)
        return linha_cadastro

    except TimeoutException:
        driver.switch_to.default_content()
        botao_alerta = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
        )
        botao_alerta.click()
        busca_criterio_2_criterio_1_nao_localizadas.append({"criterio_1": numero_criterio_1, "indice": indice})
        print(f"criterio_1 NAO LOCALIZADA: {numero_criterio_1}")
        switch_to_iframe_with_element("#Nocriterio_1Cia")
        return None


def buscar_criterio_1(numero_criterio_1, busca_criterio_2_criterio_1_nao_localizadas, indice):
    time.sleep(1)

    for tentativa in range(1, 4):
        try:
            barra_pesquisa_criterio_1 = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#Nocriterio_1Cia"))
            )
            barra_pesquisa_criterio_1.clear()
            barra_pesquisa_criterio_1.send_keys(str(numero_criterio_1))
            barra_pesquisa_criterio_1.send_keys(Keys.ENTER)

            print(f"Consulta realizada para criterio_1 {numero_criterio_1}")

            return localizar_linha_cadastro_pela_criterio_1(
                numero_criterio_1, busca_criterio_2_criterio_1_nao_localizadas, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/3 para criterio_1 {numero_criterio_1}")
            if tentativa < 3:
                time.sleep(2)

                raise Exception(f"Tentativas esgotadas para criterio_1 {numero_criterio_1}")

    print(f"Todas as tentativas esgotadas para criterio_1 {numero_criterio_1}")
    raise Exception(f"Tentativas esgotadas para criterio_1 {numero_criterio_1}")


def localizar_linha_cadastro_pelo_criterio_2(criterio_2, busca_criterio_3_criterio_3_criterio_2s_nao_localizados, df, indice):
    time.sleep(1)

    try:
        linhas = driver.find_elements(By.XPATH, "//td[@aria-describedby='GridConsulta_InicioVigencia']")
        print(f"Total de células encontradas na coluna vigência: {len(linhas)}")

        if len(linhas) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"criterio_2 NAO LOCALIZADO NO SITE: {criterio_2}")
            except TimeoutException:
                pass

            busca_criterio_3_criterio_2_nao_localizados.append({"indice": indice})
            driver.switch_to.frame("ZonaInterna")
            return None

        vigencia_excel = df.loc[indice, "CAMPO3"]
        vigencia_excel_str = str(vigencia_excel)

        if isinstance(vigencia_excel, (datetime.datetime, pd.Timestamp)):
            data_excel = vigencia_excel.to_pydatetime() if hasattr(vigencia_excel, "to_pydatetime") else vigencia_excel
            vigencia_excel_str = data_excel.strftime("%d/%m/%Y")
        else:
            vigencia_excel_str = str(vigencia_excel).strip()
            try:
                data_excel = datetime.datetime.strptime(vigencia_excel_str, "%d/%m/%Y")
            except ValueError:
                data_excel = datetime.datetime.strptime(vigencia_excel_str, "%d/%m/%y")

        linha_cadastro = None

        for celula in linhas:
            driver.execute_script("arguments[0].scrollIntoView(true);", celula)
            time.sleep(0.3)

            vigencia_site = celula.get_attribute("title").strip()
            try:
                data_site = datetime.datetime.strptime(vigencia_site, "%d/%m/%Y")
            except ValueError:
                data_site = datetime.datetime.strptime(vigencia_site, "%d/%m/%y")

            if data_site.month == data_excel.month and data_site.year == data_excel.year:
                linha_cadastro = celula
                break

        if linha_cadastro:
            print("criterio_2 localizado com vigência correta:", criterio_2, f"{data_excel.month:02d}/{data_excel.year}")
            return linha_cadastro
        else:
            print(f"criterio_2 {criterio_2} encontrado no site, mas vigência {data_excel.month:02d}/{data_excel.year} não bate")
            busca_criterio_3_criterio_2s_nao_localizados.append({"indice": indice})
            return None

    except TimeoutException:
        driver.switch_to.default_content()
        try:
            botao_alerta = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
            )
            botao_alerta.click()
        except TimeoutException:
            pass
        busca_criterio_3_criterio_2s_nao_localizados.append({"indice": indice})
        print(f"criterio_2 NAO LOCALIZADO: {criterio_2}")
        driver.switch_to.frame("ZonaInterna")
        return None


def buscar_criterio_2(criterio_2, busca_criterio_3_criterio_3_criterio_2s_nao_localizados, df, indice):
    time.sleep(1)

    for tentativa in range(1, 4):
        try:
            barra_pesquisa_criterio_2 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#criterio_2"))
            )
            barra_pesquisa_criterio_2.click()
            barra_pesquisa_criterio_2.clear()
            barra_pesquisa_criterio_2.send_keys(str(criterio_2))
            barra_pesquisa_criterio_2.send_keys(Keys.ENTER)

            print(f"Consulta realizada para o criterio_2 {criterio_2}")

            return localizar_linha_cadastro_pelo_criterio_2(
                criterio_2, busca_criterio_3_criterio_3_criterio_2s_nao_localizados, df, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/3 para criterio_2 {criterio_2}")
            if tentativa < 3:
                time.sleep(2)

                raise Exception(f"Tentativas esgotadas para criterio_2 {criterio_2}")

    print(f"Todas as tentativas esgotadas para criterio_2 {criterio_2}")
    raise Exception(f"Tentativas esgotadas para criterio_2 {criterio_2}")


def localizar_linha_cadastro_pelo_criterio_3(criterio_3, itens_nao_localizados, df, indice):
    time.sleep(1)

    try:
        celulas_vigencia = driver.find_elements(By.XPATH, "//td[@aria-describedby='GridConsulta_InicioVigencia']")
        celulas_produto  = driver.find_elements(By.XPATH, "//td[@aria-describedby='GridConsulta_Produto1']")
        print(f"Total de linhas encontradas: {len(celulas_vigencia)}")

        if len(celulas_vigencia) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"CRITERIO 3 NAO LOCALIZADO NO SITE: {criterio_3}")
            except TimeoutException:
                pass

            itens_nao_localizados.append(indice)
            driver.switch_to.frame("ZonaInterna")
            return None, "NAO LOCALIZADO"

        vigencia_excel = df.loc[indice, "CAMPO3"]
        produto_excel  = str(df.loc[indice, "CAMPO7"]).strip()

        if isinstance(vigencia_excel, (datetime.datetime, pd.Timestamp)):
            data_excel = vigencia_excel.to_pydatetime() if hasattr(vigencia_excel, "to_pydatetime") else vigencia_excel
            vigencia_excel_str = data_excel.strftime("%d/%m/%Y")
        else:
            vigencia_excel_str = str(vigencia_excel).strip()
            try:
                data_excel = datetime.datetime.strptime(vigencia_excel_str, "%d/%m/%Y")
            except ValueError:
                data_excel = datetime.datetime.strptime(vigencia_excel_str, "%d/%m/%y")

        linha_cadastro    = None
        resultado_parcial = None

        for celula_vig, celula_prod in zip(celulas_vigencia, celulas_produto):
            driver.execute_script("arguments[0].scrollIntoView(true);", celula_vig)
            time.sleep(0.3)

            vigencia_site = celula_vig.get_attribute("title").strip()
            produto_site  = celula_prod.text.strip()

            try:
                data_site = datetime.datetime.strptime(vigencia_site, "%d/%m/%Y")
            except ValueError:
                data_site = datetime.datetime.strptime(vigencia_site, "%d/%m/%y")

            print(f"Site → Início vigência: {vigencia_site} | produto: {produto_site}")

            data_igual    = (data_site.day == data_excel.day and
                             data_site.month == data_excel.month and
                             data_site.year  == data_excel.year)
            produto_igual = (produto_site == produto_excel)

            if data_igual and produto_igual:
                print("Localizado com início de vigência e produto corretos!")
                return celula_vig, "LOCALIZADO"
            elif data_igual and not produto_igual:
                resultado_parcial = (celula_vig, "INICIO VIGENCIA IGUAL, PRODUTO DIFERENTE")

        if resultado_parcial:
            print("Início de vigência igual mas produto diferente.")
            return resultado_parcial

        print(f"Nenhuma linha com início de vigência {vigencia_excel_str} e produto {produto_excel}")
        itens_nao_localizados.append(indice)
        return None, "NAO LOCALIZADO"

    except TimeoutException:
        driver.switch_to.default_content()
        botao_alerta = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
        )
        botao_alerta.click()
        itens_nao_localizados.append(indice)
        print(f"ÍNDICE NAO LOCALIZADO: {indice}")
        switch_to_iframe_with_element("#criterio3")
        return None, "NAO LOCALIZADO"


def buscar_criterio_3(criterio_3, busca_criterio_3_criterio_2_nao_localizados, df, indice):
    time.sleep(1)

    for tentativa in range(1, 4):
        try:
            barra_pesquisa_criterio_3 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#criterio_3"))
            )
            barra_pesquisa_criterio_3.click()
            barra_pesquisa_criterio_3.clear()
            barra_pesquisa_criterio_3.send_keys(str(criterio_3))
            barra_pesquisa_criterio_3.send_keys(Keys.ENTER)

            print(f"Consulta realizada para o criterio_3/ {criterio_3}")

            return localizar_linha_cadastro_pelo_criterio_3(
                criterio_3, busca_criterio_3_criterio_3_criterio_2s_nao_localizados, df, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/3 para criterio_3/ {criterio_3}")
            if tentativa < 3:
                time.sleep(2)

                raise Exception(f"Tentativas esgotadas para criterio_3 {criterio_3}")


    print(f"Todas as tentativas esgotadas para criterio_3/ {criterio_3}")
    raise Exception(f"Tentativas esgotadas para criterio_3 {criterio_3}")


def abrir_cadastro(linha_cadastro):
    time.sleep(1)

    tag = linha_cadastro.tag_name.lower()
    if tag == "td":
        linha_para_clicar = linha_cadastro.find_element(By.XPATH, "./ancestor::tr[1]")
        print("Elemento era <td>, subindo para <tr> pai")
    else:
        linha_para_clicar = linha_cadastro

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", linha_para_clicar)
    time.sleep(0.5)

    try:
        actions = ActionChains(driver)
        actions.double_click(linha_para_clicar).perform()
    except Exception:
        print("double_click normal falhou, tentando via JavaScript...")
        driver.execute_script("""
            var evt = new MouseEvent('dblclick', {bubbles: true, cancelable: true});
            arguments[0].dispatchEvent(evt);
        """, linha_para_clicar)

    driver.switch_to.default_content()

    try:
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#imgCarregando"))
        )
    except TimeoutException:
        pass

    wait = WebDriverWait(driver, 30)
    wait.until(lambda d: d.execute_script("return jQuery.active == 0"))
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

    print("Entrando no iframe ZonaInterna (nível 1)...")
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "ZonaInterna"))
    )

    print("Entrando no iframe ZonaInterna (nível 2, aninhado)...")
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "ZonaInterna"))
    )


def verificar_campo_1():
    try:
        campo_1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'select2-Documento_GrupoHierarquicoSelect-container')]"))
        )
        campo_1_texto = campo_1_element.get_attribute("title")
        print("CAMPO_1 LOCALIZADO:", campo_1_texto)
        return campo_1_texto

    except StaleElementReferenceException:
        campo_1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'select2-Documento_GrupoHierarquicoSelect-container')]"))
        )
        campo_1_texto = campo_1_element.get_attribute("title")
        print("CAMPO_1 RELOCALIZADO", campo_1_texto)
        return campo_1_texto

    except TimeoutException:
        print("Tempo esgotado para localizar campo_1")

    except Exception as e:
        print("Erro ao localizar campo_1:", e)


def verificar_campo_2():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIVDocumento_campo_2')]"))
        )
        print("CAMPO_2 LOCALIZADO")

        radios = [
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_21"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_22"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_23"),
        ]

        for radio in radios:
            if radio.is_selected():
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
                campo_2_texto = label.text
                print(f"Selecionado: {campo_2_texto}")
                return campo_2_texto

    except StaleElementReferenceException:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIVDocumento_campo_2')]"))
        )
        print("CAMPO_2 RELOCALIZADO")

        radios = [
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_21"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_22"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_23"),
        ]

        for radio in radios:
            if radio.is_selected():
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
                campo_2_texto = label.text
                print(f"Selecionado: {campo_2_texto}")
                return campo_2_texto

    except TimeoutException:
        print("Tempo esgotado para localizar campo_2")

    except Exception as e:
        print("Erro ao localizar campo_2:", e)


def verificar_campo_3():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIVDocumento_campo_3')]"))
        )
        print("CAMPO_3 LOCALIZADO")

        radios = [
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_31"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_32"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_33"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_35"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_36"),
        ]

        for radio in radios:
            if radio.is_selected():
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
                campo_3_texto = label.text
                print(f"Selecionado: {campo_3_texto}")
                return campo_3_texto

    except StaleElementReferenceException:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIVDocumento_campo_3')]"))
        )
        print("CAMPO_3 RELOCALIZADO")

        radios = [
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_31"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_32"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_33"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_35"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_36"),
            driver.find_element(By.CSS_SELECTOR, "#Documento_campo_37"),
        ]

        for radio in radios:
            if radio.is_selected():
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio.get_attribute('id')}']")
                campo_3_texto = label.text
                print(f"Selecionado: {campo_3_texto}")
                return campo_3_texto

    except TimeoutException:
        print("Tempo esgotado para localizar campo_3")

    except Exception as e:
        print("Erro ao localizar campo_3:", e)


def voltar_para_a_busca():
    try:
        botao_voltar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#Button1"))
        )
        botao_voltar.click()
        driver.switch_to.default_content()
        driver.switch_to.frame("ZonaInterna")
        print("Voltando para a busca...")

    except StaleElementReferenceException:
        botao_voltar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#Button1"))
        )
        botao_voltar.click()
        driver.switch_to.default_content()
        driver.switch_to.frame("ZonaInterna")
        print("Voltando para a busca (RELOCALIZADO)...")

    except TimeoutException:
        print("Tempo esgotado para localizar botão de voltar")

    except Exception as e:
        print("Erro ao clicar no botão de voltar:", e)


def mudar_tipo_busca(tipo):
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#select2-TipoConsulta2-container"))
        )
        container.click()

        barra = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > span.select2-container.select2-containerS.select2-container--default.select2-container--open > span > span.select2-search.select2-search--dropdown > input"))
        )
        barra.click()
        barra.clear()
        barra.send_keys(tipo)

        opcao = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@id, 'select2-TipoConsulta2-result-')]"))
        )
        opcao.click()
        print(f"Tipo de busca alterado para: {tipo}")

    except Exception as e:
        print(f"Erro ao mudar tipo de busca para {tipo}:", e)


