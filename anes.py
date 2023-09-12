from functions.store_data import data_functions as df # Biblioteca local
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from functions.repeated_code import funcoes as fc
from selenium.webdriver.common.by import By
from seleniumwire import webdriver as webd2
from selenium import webdriver as webd1
from bs4 import BeautifulSoup
from datetime import date
import pandas as pd
import datetime
import dotenv
import time
import os
import re

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)  # Pega as variáveis de ambiente

FOLDER_PATH = os.getenv("FOLDER_PATH")
TRANSPARENCIA = os.getenv("TRANSPARENCIA")

#---------------------------------------------------------------------------------------------------------
# Declaração de variáveis e listas
periodo_atual = "01/05/2023 - 01/08/2023"            # Periodo do início do ano ao dia de hoje, que será usado para extrair os editais DL e de Inexigibilidade
data_de_abertura = None                              # Variável global para ser usada num escopo específico
url = "https://transparencia.e-publica.net/epublica-portal/#/chapeco/portal/compras/licitacaoTable"    # Link do site da prefeitura
driver = webd1.Chrome(executable_path="C:/Users/Desenvolvimento/.wdm/drivers/chromedriver/win64/115.0.5790.111/chromedriver.exe")
driver.get(url)
time.sleep(5)
links_dos_editais = []
nomes_dos_editais = []
tabela_paginas = []

#---------------------------------------------------------------------------------------------------------
# Raspagem dos editais Homologados

# Deixa o texto "Homologado" visível
expor_texto = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div/div/div/a/div/b")
expor_texto.click()
time.sleep(1)

# Achar a tag "Select" que contem a opção "Homologado"
achar_select = driver.find_element(By.XPATH, "//*[text()='Situação']/../../../div[@class='filtro-espacamento col-xs-12 col-sm-8']/div/div/div/select")
select_object = Select(achar_select)
time.sleep(1)

# Encontrar o elemento para seleção ("Homologado")
element_for_select = driver.find_element(By.XPATH, "//*[@id='advancedSearchModal']/div/div/div/div/div/div[4]/div/div[2]/div/div/div/div/div/ul/li[7]")
time.sleep(1)

# Clica no elemento para seleção
element_for_select.click()
time.sleep(1)

# Isola as "unused" variáveis
_ = select_object

# Clica em "Consultar"
consultar = driver.find_element(By.XPATH, "//div[@class='row epublica-search-row epublica-search-row-group']/div/div/button[@class='btn-filtrar col-xs-12 col-sm-4 epublica-portal-search-button pull-right']")
consultar.click()
time.sleep(5)

# Encontra o botão "Próxima" para extrair mais links
proxima = driver.find_element(By.XPATH, "//*[text()='Próxima']")

# Pegar os editais do periodo "01/07/2023 - 01/08/2023"
periodo = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/input")
periodo.clear()
time.sleep(1)
periodo.send_keys(periodo_atual)
time.sleep(1)
aplicar = driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div/button[1]")    # Acha o botão "Aplicar"
aplicar.click()                                                                      # Clica no botão para selecionar o periodo específicado
time.sleep(1)

# Consulta os editais filtrados
consultar = driver.find_element(By.XPATH, "//div[@class='row epublica-search-row epublica-search-row-group']/div/div/button[@class='btn-filtrar col-xs-12 col-sm-4 epublica-portal-search-button pull-right']")
consultar.click()
time.sleep(5)

# Extrai os links desses editais
while True:
    # Extrai o código fonte com Beatiful Soup
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')

    # Encontra os links dos Editais
    editais = soup.findAll('tr', {'ng-repeat-start': '(rowIndex, row) in tableReq.rows'})

    for edital in editais:
        link_do_edital = str(edital.findAll('td')[5].find('p-actions').find('div').findAll('ng-repeat')[1].find('a')['href'])
        modalidade = edital.findAll('td')[1].findAll('div')[1].find('span').get_text()
        links_dos_editais.append([TRANSPARENCIA + link_do_edital, modalidade])

    try:
        time.sleep(5)
        element = driver.find_element(By.XPATH, "//*[text()='Próxima']")
        element.click()
    except:
        break
driver.close()
time.sleep(5)

for url, modalidade in links_dos_editais:
    try:
        # Usa o seleniumwire, poís extrairá os nomes dos Editais por uma XHR
        driver_1 = webd2.Chrome(executable_path="C:/Users/Desenvolvimento/.wdm/drivers/chromedriver/win64/115.0.5790.111/chromedriver.exe")
        driver_1.get(url)
        time.sleep(5)

        # Encontra e filtra a data e horario
        data_xpath_list = [
            "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[12]/p-list/dl/ng-repeat[1]/dd",
            "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[8]/p-list/dl/ng-repeat[1]/dd"
        ]
        for data_xpath in data_xpath_list:
            data = driver_1.find_element(By.XPATH, data_xpath).text
            if data == '-':
                horario = ''
                pass
            else:
                horario = data[11:]
                data = data[:10]
                break
        data = datetime.datetime.strptime(str(data), '%d/%m/%Y').date()

        # Pega o nº do Edital
        n0_edital = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[2]/p-h2/h2").text
        n0_edital = re.search(r'[a-zA-Z0-9]{1,5}/\d{4}', n0_edital).group()

        # Filtra outros dados
        local_xpath_list = [
            "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[10]/p-list/dl/ng-repeat[2]/dd",
            "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[15]/p-list/dl/ng-repeat[2]/dd",
        ]
        for local_xpath in local_xpath_list:
            try:
                local = driver_1.find_element(By.XPATH, local_xpath).text.replace('.', '')
                break
            except:
                pass

        gestora = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[3]/div/div/div/div/span").text
        tipo = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[8]/p-list/dl/ng-repeat[3]/dd").text
        julgamento = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[8]/p-list/dl/ng-repeat[4]/dd").text

        # Pega o Objeto do Edital
        objeto = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[6]/div/div/div/div/div/span").text

        # Pega a quantidade de dinheiro, em Real
        quantia_dinheiro = driver_1.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[4]/p-h3/h3").text
        quantia_dinheiro = quantia_dinheiro.replace(u'Valor Total R$ ', u'')

        # Infunde o "Dataframe" criado com a variável Tabela
        dados_resgatados = [data, horario, n0_edital, local, modalidade, julgamento, gestora, objeto, quantia_dinheiro, tipo, url]
        tabela_paginas.append(dados_resgatados)
        time.sleep(3)

        # Faz Download dos Editais
        contagem = 1
        while True:
            try:
                try:
                    edital_click = driver_1.find_element(By.XPATH, f"/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[14]/div/div/div[2]/div/div/div/div/table/tbody/tr[{contagem}]/td[3]/p-actions/div/ng-repeat[2]")
                except:
                    try:
                        edital_click = driver_1.find_element(By.XPATH, f"/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/ng-transclude/div/div/div/form/div[1]/ng-form/div[15]/div/div/div[2]/div/div/div/div/table/tbody/tr[{contagem}]/td[3]/p-actions/div/ng-repeat[2]")
                    except:
                        break
                edital_click.click()
                time.sleep(3)

                # Extrai os nomes da XHR
                for request in driver_1.requests:
                    if request.response:
                        if request.response.headers['x-amz-meta-nome'] is not None:
                            nomes_dos_editais.append(str(request.response.headers['x-amz-meta-nome']))
                            nomes_dos_editais.append(str(request.response.headers['x-amz-meta-nome']) + ' (1)')
                            time.sleep(3)
                contagem += 1
            except NoSuchElementException:
                break
        # fecha o driver após terminar a busca de editais
        driver_1.close()
    except:
        # fecha o driver em caso de erro
        driver_1.close()
        continue

# Garante que os nomes não se repitam
nomes_dos_editais = fc.remover_repetidos(nomes_dos_editais)

df1 = pd.DataFrame(tabela_paginas, columns=['Data', 'Horario', 'Edital', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Objeto', 'Montante', 'Tipo', 'Link da Página'])

# Raspa os arquivos
for nome_do_edital in nomes_dos_editais:
    try:
        caminho_arquivo = "C:/Users/Desenvolvimento/Downloads/" + nome_do_edital + ".pdf"

        # Converte para arquivo binário
        arquivo = open(caminho_arquivo, 'rb')
        pdf = arquivo.read()
        arquivo.close()

        # Insere os dados na Tabela e no Banco de Dados
        df.insert_data(FOLDER_PATH + "editais_dados.csv", caminho_arquivo, pdf, df1) # Insere os dados numa tabela CSV
    except:
        try:
            # Deleta os arquivos em caso de erro
            caminho_arquivo = "C:/Users/Desenvolvimento/Downloads/" + str(nome_do_edital) + ".pdf"
            os.remove(caminho_arquivo)
            print("\n---------------------\nArquivo Removido!")
            continue
        except:
            continue
    else:
        print("\n---------------------\nArquivo Inexistente!")

# Ordenar datas
df.order_dates(FOLDER_PATH + "editais_dados.csv")
