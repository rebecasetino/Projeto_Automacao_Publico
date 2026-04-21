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


def acessar_sistema_e_preencher_login():
    driver.get(config.link)

    campo_a = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#campo_a"))
    )
    campo_a.click()
    campo_a.send_keys(config.corretora)

    campo_b = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#campo_b"))
    )
    campo_b.click()
    campo_b.send_keys(config.usuario)

    campo_c = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#campo_c"))
    )
    campo_c.click()
    campo_c.send_keys(config.senha)


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


def localizar_registro_por_criterio_1(valor_criterio_1, pendentes_criterio_2, indice):
    time.sleep(1)

    try:
        linhas = driver.find_elements(By.XPATH, "//td[@aria-describedby='Grid_Coluna1']")
        print(f"Total de registros encontrados: {len(linhas)}")

        if len(linhas) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"CRITERIO 1 NAO LOCALIZADO NO SISTEMA: {valor_criterio_1}")
            except TimeoutException:
                pass

            pendentes_criterio_2.append({"criterio_1": valor_criterio_1, "indice": indice})
            driver.switch_to.frame("ZonaInterna")
            return None

        registro = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{valor_criterio_1}')]"))
        )
        print("Registro localizado:", registro.text)
        return registro

    except StaleElementReferenceException:
        registro = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@id, ',0,1')]/td[7]"))
        )
        print("Registro relocalizado:", registro.text)
        return registro

    except TimeoutException:
        driver.switch_to.default_content()
        botao_alerta = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
        )
        botao_alerta.click()
        pendentes_criterio_2.append({"criterio_1": valor_criterio_1, "indice": indice})
        print(f"CRITERIO 1 NAO LOCALIZADO: {valor_criterio_1}")
        switch_to_iframe_with_element("#seletor_criterio_1")
        return None


def buscar_por_criterio_1(valor_criterio_1, pendentes_criterio_2, indice):
    time.sleep(1)

    def _buscar(tentativa=1, max_tentativas=3):
        try:
            campo_busca = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#seletor_criterio_1"))
            )
            campo_busca.clear()
            campo_busca.send_keys(str(valor_criterio_1))
            campo_busca.send_keys(Keys.ENTER)

            print(f"Consulta realizada para criterio_1: {valor_criterio_1}")

            return localizar_registro_por_criterio_1(
                valor_criterio_1, pendentes_criterio_2, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/{max_tentativas} para criterio_1: {valor_criterio_1}")
            if tentativa < max_tentativas:
                time.sleep(2)
                return _buscar(tentativa + 1, max_tentativas)
            else:
                print(f"Todas as tentativas esgotadas para criterio_1: {valor_criterio_1}")
                return False

    return _buscar()


def localizar_registro_por_criterio_2(valor_criterio_2, pendentes_criterio_3, df, indice):
    time.sleep(1)

    try:
        linhas = driver.find_elements(By.XPATH, "//td[@aria-describedby='Grid_Coluna1']")
        print(f"Total de registros encontrados: {len(linhas)}")

        if len(linhas) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"CRITERIO 2 NAO LOCALIZADO NO SISTEMA: {valor_criterio_2}")
            except TimeoutException:
                pass

            pendentes_criterio_3.append({"indice": indice})
            driver.switch_to.frame("ZonaInterna")
            return None

        data_referencia_excel = df.loc[indice, "CAMPO3"]
        data_referencia_str = str(data_referencia_excel)

        if isinstance(data_referencia_excel, (datetime.datetime, pd.Timestamp)):
            data_excel = data_referencia_excel.to_pydatetime() if hasattr(data_referencia_excel, "to_pydatetime") else data_referencia_excel
            data_referencia_str = data_excel.strftime("%d/%m/%Y")
        else:
            data_referencia_str = str(data_referencia_excel).strip()
            try:
                data_excel = datetime.datetime.strptime(data_referencia_str, "%d/%m/%Y")
            except ValueError:
                data_excel = datetime.datetime.strptime(data_referencia_str, "%d/%m/%y")

        registro_encontrado = None

        for celula in linhas:
            driver.execute_script("arguments[0].scrollIntoView(true);", celula)
            time.sleep(0.3)

            data_sistema = celula.get_attribute("title").strip()
            try:
                data_site = datetime.datetime.strptime(data_sistema, "%d/%m/%Y")
            except ValueError:
                data_site = datetime.datetime.strptime(data_sistema, "%d/%m/%y")

            if data_site.month == data_excel.month and data_site.year == data_excel.year:
                registro_encontrado = celula
                break

        if registro_encontrado:
            print("Criterio 2 localizado com data de referencia correta:", valor_criterio_2, f"{data_excel.month:02d}/{data_excel.year}")
            return registro_encontrado
        else:
            print(f"Criterio 2 {valor_criterio_2} encontrado, mas data de referencia {data_excel.month:02d}/{data_excel.year} nao confere")
            pendentes_criterio_3.append({"indice": indice})
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
        pendentes_criterio_3.append({"indice": indice})
        print(f"CRITERIO 2 NAO LOCALIZADO: {valor_criterio_2}")
        driver.switch_to.frame("ZonaInterna")
        return None


def buscar_por_criterio_2(valor_criterio_2, pendentes_criterio_3, df, indice):
    time.sleep(1)

    def _buscar(tentativa=1, max_tentativas=3):
        try:
            campo_busca = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#seletor_criterio_2"))
            )
            campo_busca.click()
            campo_busca.clear()
            campo_busca.send_keys(str(valor_criterio_2))
            campo_busca.send_keys(Keys.ENTER)

            print(f"Consulta realizada para criterio_2: {valor_criterio_2}")

            return localizar_registro_por_criterio_2(
                valor_criterio_2, pendentes_criterio_3, df, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/{max_tentativas} para criterio_2: {valor_criterio_2}")
            if tentativa < max_tentativas:
                time.sleep(2)
                return _buscar(tentativa + 1, max_tentativas)
            else:
                print(f"Todas as tentativas esgotadas para criterio_2: {valor_criterio_2}")
                return False

        except Exception as e:
            print(f"Erro ao buscar criterio_2 {valor_criterio_2}: {e}")
            return False

    return _buscar()


def localizar_registro_por_criterio_3(valor_criterio_3, itens_nao_localizados, df, indice):
    time.sleep(1)

    try:
        celulas_data = driver.find_elements(By.XPATH, "//td[@aria-describedby='Grid_Coluna1']")
        celulas_tipo = driver.find_elements(By.XPATH, "//td[@aria-describedby='Grid_Coluna2']")
        print(f"Total de registros encontrados: {len(celulas_data)}")

        if len(celulas_data) == 0:
            try:
                driver.switch_to.default_content()
                botao_alerta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
                )
                botao_alerta.click()
                print(f"CRITERIO 3 NAO LOCALIZADO NO SISTEMA: {valor_criterio_3}")
            except TimeoutException:
                pass

            itens_nao_localizados.append(indice)
            driver.switch_to.frame("ZonaInterna")
            return None, "resultado_3"

        data_referencia_excel = df.loc[indice, "CAMPO3"]
        tipo_referencia_excel = str(df.loc[indice, "CAMPO7"]).strip()

        if isinstance(data_referencia_excel, (datetime.datetime, pd.Timestamp)):
            data_excel = data_referencia_excel.to_pydatetime() if hasattr(data_referencia_excel, "to_pydatetime") else data_referencia_excel
            data_referencia_str = data_excel.strftime("%d/%m/%Y")
        else:
            data_referencia_str = str(data_referencia_excel).strip()
            try:
                data_excel = datetime.datetime.strptime(data_referencia_str, "%d/%m/%Y")
            except ValueError:
                data_excel = datetime.datetime.strptime(data_referencia_str, "%d/%m/%y")

        registro_encontrado = None
        resultado_parcial   = None

        for celula_data, celula_tipo in zip(celulas_data, celulas_tipo):
            driver.execute_script("arguments[0].scrollIntoView(true);", celula_data)
            time.sleep(0.3)

            data_sistema = celula_data.get_attribute("title").strip()
            tipo_sistema = celula_tipo.text.strip()

            try:
                data_site = datetime.datetime.strptime(data_sistema, "%d/%m/%Y")
            except ValueError:
                data_site = datetime.datetime.strptime(data_sistema, "%d/%m/%y")

            print(f"Sistema → Data referencia: {data_sistema} | Tipo: {tipo_sistema}")

            data_igual = (data_site.day == data_excel.day and
                          data_site.month == data_excel.month and
                          data_site.year  == data_excel.year)
            tipo_igual = (tipo_sistema == tipo_referencia_excel)

            if data_igual and tipo_igual:
                print("Registro localizado com data e tipo corretos!")
                return celula_data, "resultado_1"
            elif data_igual and not tipo_igual:
                resultado_parcial = (celula_data, "resultado_2")

        if resultado_parcial:
            print("Data de referencia igual mas tipo diferente.")
            return resultado_parcial

        print(f"Nenhum registro com data {data_referencia_str} e tipo {tipo_referencia_excel}")
        itens_nao_localizados.append(indice)
        return None, "resultado_3"

    except TimeoutException:
        driver.switch_to.default_content()
        botao_alerta = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.btn.btn-success"))
        )
        botao_alerta.click()
        itens_nao_localizados.append(indice)
        print(f"INDICE NAO LOCALIZADO: {indice}")
        switch_to_iframe_with_element("#seletor_criterio_3")
        return None, "resultado_3"


def buscar_por_criterio_3(valor_criterio_3, pendentes_criterio_3, df, indice):
    time.sleep(1)

    def _buscar(tentativa=1, max_tentativas=3):
        try:
            campo_busca = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#seletor_criterio_3"))
            )
            campo_busca.click()
            campo_busca.clear()
            campo_busca.send_keys(str(valor_criterio_3))
            campo_busca.send_keys(Keys.ENTER)

            print(f"Consulta realizada para criterio_3: {valor_criterio_3}")

            return localizar_registro_por_criterio_3(
                valor_criterio_3, pendentes_criterio_3, df, indice
            )

        except TimeoutException:
            print(f"Timeout na tentativa {tentativa}/{max_tentativas} para criterio_3: {valor_criterio_3}")
            if tentativa < max_tentativas:
                time.sleep(2)
                return _buscar(tentativa + 1, max_tentativas)
            else:
                print(f"Todas as tentativas esgotadas para criterio_3: {valor_criterio_3}")
                return False

        except Exception as e:
            print(f"Erro ao buscar criterio_3 {valor_criterio_3}: {e}")
            return False

    return _buscar()


def abrir_registro(registro):
    time.sleep(1)

    tag = registro.tag_name.lower()
    if tag == "td":
        elemento_clicavel = registro.find_element(By.XPATH, "./ancestor::tr[1]")
        print("Elemento era <td>, subindo para <tr> pai")
    else:
        elemento_clicavel = registro

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento_clicavel)
    time.sleep(0.5)

    try:
        actions = ActionChains(driver)
        actions.double_click(elemento_clicavel).perform()
    except Exception:
        print("double_click normal falhou, tentando via JavaScript...")
        driver.execute_script("""
            var evt = new MouseEvent('dblclick', {bubbles: true, cancelable: true});
            arguments[0].dispatchEvent(evt);
        """, elemento_clicavel)

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

    print("Entrando no iframe de conteudo (nivel 1)...")
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "ZonaInterna"))
    )

    print("Entrando no iframe de conteudo (nivel 2, aninhado)...")
    WebDriverWait(driver, 30).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "ZonaInterna"))
    )


def verificar_campo_a():
    try:
        elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'select2-campo_a-container')]"))
        )
        valor = elemento.get_attribute("title")
        print("CAMPO A LOCALIZADO:", valor)
        return valor

    except StaleElementReferenceException:
        elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'select2-campo_a-container')]"))
        )
        valor = elemento.get_attribute("title")
        print("CAMPO A RELOCALIZADO:", valor)
        return valor

    except TimeoutException:
        print("Tempo esgotado para localizar campo A")

    except Exception as e:
        print("Erro ao localizar campo A:", e)


def verificar_campo_b():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIV_campo_b')]"))
        )
        print("CAMPO B LOCALIZADO")

        opcoes = [
            driver.find_element(By.CSS_SELECTOR, "#campo_b_1"),
            driver.find_element(By.CSS_SELECTOR, "#campo_b_2"),
            driver.find_element(By.CSS_SELECTOR, "#campo_b_3"),
        ]

        for opcao in opcoes:
            if opcao.is_selected():
                rotulo = driver.find_element(By.CSS_SELECTOR, f"label[for='{opcao.get_attribute('id')}']")
                valor = rotulo.text
                print(f"Selecionado: {valor}")
                return valor

    except StaleElementReferenceException:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIV_campo_b')]"))
        )
        print("CAMPO B RELOCALIZADO")

        opcoes = [
            driver.find_element(By.CSS_SELECTOR, "#campo_b_1"),
            driver.find_element(By.CSS_SELECTOR, "#campo_b_2"),
            driver.find_element(By.CSS_SELECTOR, "#campo_b_3"),
        ]

        for opcao in opcoes:
            if opcao.is_selected():
                rotulo = driver.find_element(By.CSS_SELECTOR, f"label[for='{opcao.get_attribute('id')}']")
                valor = rotulo.text
                print(f"Selecionado: {valor}")
                return valor

    except TimeoutException:
        print("Tempo esgotado para localizar campo B")

    except Exception as e:
        print("Erro ao localizar campo B:", e)


def verificar_campo_c():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIV_campo_c')]"))
        )
        print("CAMPO C LOCALIZADO")

        opcoes = [
            driver.find_element(By.CSS_SELECTOR, "#campo_c_1"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_2"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_3"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_4"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_5"),
        ]

        for opcao in opcoes:
            if opcao.is_selected():
                rotulo = driver.find_element(By.CSS_SELECTOR, f"label[for='{opcao.get_attribute('id')}']")
                valor = rotulo.text
                print(f"Selecionado: {valor}")
                return valor

    except StaleElementReferenceException:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'DIV_campo_c')]"))
        )
        print("CAMPO C RELOCALIZADO")

        opcoes = [
            driver.find_element(By.CSS_SELECTOR, "#campo_c_1"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_2"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_3"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_4"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_5"),
            driver.find_element(By.CSS_SELECTOR, "#campo_c_6"),
        ]

        for opcao in opcoes:
            if opcao.is_selected():
                rotulo = driver.find_element(By.CSS_SELECTOR, f"label[for='{opcao.get_attribute('id')}']")
                valor = rotulo.text
                print(f"Selecionado: {valor}")
                return valor

    except TimeoutException:
        print("Tempo esgotado para localizar campo C")

    except Exception as e:
        print("Erro ao localizar campo C:", e)


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
        print("Tempo esgotado para localizar botao de voltar")

    except Exception as e:
        print("Erro ao clicar no botao de voltar:", e)


def mudar_modo_busca(modo):
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#select2-seletor_modo_busca-container"))
        )
        container.click()

        barra = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > span.select2-container.select2-containerS.select2-container--default.select2-container--open > span > span.select2-search.select2-search--dropdown > input"))
        )
        barra.click()
        barra.clear()
        barra.send_keys(modo)

        opcao = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@id, 'select2-seletor_modo_busca-result-')]"))
        )
        opcao.click()
        print(f"Modo de busca alterado para: {modo}")

    except Exception as e:
        print(f"Erro ao mudar modo de busca para {modo}:", e)
