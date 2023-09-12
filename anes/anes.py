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
data_de_abertura = None      # Variável global para ser usada num escopo específico
url = "https://transparencia.e-publica.net/epublica-portal/#/chapeco/portal/compras/licitacaoTable"    # Link do site da prefeitura
driver = webd1.Chrome(executable_path="C:/Users/Desenvolvimento/.wdm/drivers/chromedriver/win64/115.0.5790.111/chromedriver.exe")
driver.get(url)
time.sleep(5)
links_dos_editais = []       # Lista dos links dos editais
nomes_dos_editais = []       # Nomes dos arquivos PDFs dos editais
tabela_paginas = []          # Lista de sub-listas dos dados extraídos das páginas Web, eventualmente sendo convertida em um Dataframe
data_atual = date.today()    # Data atual
ano_atual = data_atual.year  # Ano atual
data_atual_str = str(data_atual.strftime('%d/%m/%Y'))          # String da data atual
inicio_ano = "01/01/" + str(ano_atual)                         # Primeiro dia do ano
periodo_atual = inicio_ano + " - " + data_atual_str            # Periodo do início do ano ao dia de hoje, que será usado para extrair os editais DL e de Inexigibilidade
posicoes = ['Dispensa por Justificativa', 'Inexigibilidade']   # Posições das Modalidades DL e Inexigibilidade dentro da caixa "Modalidades" no site

#---------------------------------------------------------------------------------------------------------
# Raspagem dos editais em Aberto

# Deixa o texto "Aberto" visível
expor_texto = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div/div/div/a/div/b")
expor_texto.click()
time.sleep(1)

# Achar a tag "Select" que contem a opção "Aberto"
achar_select = driver.find_element(By.XPATH, "//*[text()='Situação']/../../../div[@class='filtro-espacamento col-xs-12 col-sm-8']/div/div/div/select")
select_object = Select(achar_select)
time.sleep(1)

# Encontrar o elemento para seleção ("Aberto")
element_for_select = driver.find_element(By.XPATH, "//*[@id='advancedSearchModal']/div/div/div/div/div/div[4]/div/div[2]/div/div/div/div/div/ul/li[1]")
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

while True:
    # Extrai o código fonte com Beautiful Soup
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')

    # Encontra os links dos Editais
    editais = soup.findAll('tr', {'ng-repeat-start': '(rowIndex, row) in tableReq.rows'})

    for edital in editais:
        # Extrai primeiro as datas até chegar à data atual, e converte para o formato "Date"
        data_de_abertura = edital.findAll('td')[3].findAll('div')[1].find('span').text
        data_de_abertura = datetime.datetime.strptime(data_de_abertura, '%d/%m/%Y').date()

        # Compara com a data atual
        if data_de_abertura >= data_atual:
            # Extrai os links e coloca-os em uma lista
            link_do_edital = str(edital.findAll('td')[5].find('p-actions').find('div').findAll('ng-repeat')[1].find('a')['href'])
            modalidade = edital.findAll('td')[1].findAll('div')[1].find('span').get_text()
            links_dos_editais.append([TRANSPARENCIA + link_do_edital, modalidade])
        else:
            break

    # Quebra o laço True ao achar a data atual
    if data_de_abertura < data_atual:
        break

    # Clica para acessar os próximos links na página dinâmica
    proxima.click()
    time.sleep(3)

# Limpa a caixa "Situação"
driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div/div/div/a/abbr").click()
time.sleep(1)

#---------------------------------------------------------------------------------------------------------
# Raspar editais de modalidades DL e Inexigibilidade

# Acha a caixa de "Periodo", limpa-a e substituí pelo texto do início do ano até o dia atual (variável "periodo_1")
periodo = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/input")
periodo.clear()
time.sleep(1)
periodo.send_keys(periodo_atual)
time.sleep(1)
aplicar = driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div/button[1]")    # Acha o botão "Aplicar"
aplicar.click()                                                                      # Clica no botão para selecionar o periodo específicado
time.sleep(1)

# Pega a lista "posicoes" e repete o processo abaixo para as duas modalidades
for posicao in posicoes:
    # Deixa o texto "Aberto" visível
    expor_texto = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[3]/div/div[2]/div/div/div/div/a/div/b")    
    actions = ActionChains(driver)
    actions.move_to_element(expor_texto).perform()   # Deixa o elemento "expor_texto" visível através da Scrol
    expor_texto.click()
    time.sleep(1)

    # Achar a tag "Select" que contem a opção "Aberto"
    achar_select = driver.find_element(By.XPATH, "//*[text()='Modalidade']/../../../div[@class='filtro-espacamento col-xs-12 col-sm-8']/div/div/div/select")
    select_object = Select(achar_select)
    time.sleep(1)

    # Encontrar o elemento para seleção
    element_for_select = driver.find_element(By.XPATH, "/html/body/div[1]/div/portal-shell/section/div/div[1]/div/div/div/div[2]/div/div[1]/div/div[1]/div/div/div/div/div/div/div[3]/div/div[2]/div/div/div/div/div/ul/li[contains(text(), '"+posicao+"')]")
    time.sleep(1)

    # Clica no elemento para seleção
    element_for_select.click()

    # Isola as "unused" variáveis
    _ = select_object

    # Clica em "Consultar"
    consultar = driver.find_element(By.XPATH, "//div[@class='row epublica-search-row epublica-search-row-group']/div/div/button[@class='btn-filtrar col-xs-12 col-sm-4 epublica-portal-search-button pull-right']")
    consultar.click()
    time.sleep(5)

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
    time.sleep(5)

driver.close()

# For raspa os links e seus dados e editais um-por-um
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

# Deleta os arquivos (sem interromper o processo de Extração de Dados)
for nome_do_edital in nomes_dos_editais:
    try:
        caminho_arquivo = "C:/Users/Desenvolvimento/Downloads/" + str(nome_do_edital) + ".pdf"
        os.remove(caminho_arquivo)
    except:
        continue

# Tira da tabela dados de editais homologados (com excecção dos de Inexigibilidade e Dispensa de Licitação) e coloca o resto em ordem cronológica
df.order_dates(FOLDER_PATH + "editais_dados.csv")
df.del_data(FOLDER_PATH + "editais_dados.csv")

#---------------------------------------------------------------------------------------------------------
# Envia e-mail para o Observatório Social e registro dos envios das mensagens, editais contidos nelas e para quais entidades
# Algoritmo adaptado de "https://medium.com/@asttrodev/tutorial-enviando-e-mail-utilizando-a-biblioteca-smtplib-do-python-2adfb3768a08"

from functions.html_functions import gerar_tabela as gt # Biblioteca local
from functions.repeated_code import funcoes as fc
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import date, timedelta
from email.utils import formataddr
from datetime import datetime
from email import encoders
import mysql.connector
import smtplib
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)

# Variáveis de datas e da tabela na mensagem
agora = date.today()                             # Data atual
depois = agora + timedelta(30)                   # Data daqui a um mês
gerar_tabela = gt.gerar_tabela()                 # Tabela HTML gerada para ser enviada no E-mail e postada no site do OSB
editais_mensagem = gerar_tabela['Editais']       # Lista dos editais que serão vistos na tabela

# Variáveis "None" que serão reutilizadas
condicao = None          # Condição binária se o Banco de Dados existe ou está ativado
entidades_banco = None   # Variável que armazerará as entidades que fazem parte da cidade de Chapecó
banco_editais = None     # Variável que armazerará os editais e seus IDs que tem a data maior que a atual
banco_envios = None      # Variável que armazerará os IDs dos Envios
cnx = None               # Variável que fará conexão com o Banco
cursor = None            # Variável que sera o Cursor do Banco
item_maximo = None       # ID máximo da tabela "Envios", que será Primary Key e se conectará com a tabela "Editais" (está variável se faz necessária para termos os IDs dos novos envios e conectar à tabela "Editais" por meio da tabela "Mensagens")

try:
    # Conexão com o Banco de Dados
    cnx = mysql.connector.connect(user='root', password='', host="127.0.0.1", database="Observatorio")
    cursor = cnx.cursor()
    condicao = True
except:
    condicao = False    # Condição é False e não será feito mais nada em relação ao Banco
    print("\n---------------------\nBanco de dados desativado!")

# Listas vázias do Banco
ids_entidades = []      # Lista dos IDs das entidades
editais_id = []         # Lista dos IDs dos editais
ids_envios = []         # Lista dos IDs dos envios

# Consultas ao Banco de Dados
consulta_entidades = "select id, email from entidade where id_cidade = 1"
consulta_editais = 'select id, edital from edital where data > CURRENT_DATE()'
consulta_envios = 'select id from mensagem'

# Inserir dados no Banco
insert_data_mensagens = ("INSERT INTO envio (id_mensagem, id_edital) " + "VALUES (%(id_mensagem)s, %(id_edital)s)")
insert_data_envios = ("INSERT INTO mensagem (id, id_entidade, data_hora) " + "VALUES (%(id)s, %(id_entidade)s, %(data_hora)s)")

# Verifica se as variáveis não estão vázias e, se não estiverem, preenchem as variaveis "agora" e "depois"
if gerar_tabela['Ultima data'] != None:    # Se a variável do Dicionário "Ultima data" não for "None" (pode ser se não existirem editais nos próximos sete dias), a última data dos editais registrados que estará no título da mensagem
    depois = gerar_tabela['Ultima data']   # Variável "depois" susbtituida já que ela que aparece no título da mensagem

# Realizando consultas
if condicao:
    cursor.execute(consulta_entidades)   # Consultando as entidades que fazem parte da cidade de Chapecó
    entidades_banco = cursor.fetchall()

    cursor.execute(consulta_editais)     # Pegando os editais que tem a data maior que a atual
    banco_editais = cursor.fetchall()

    cursor.execute(consulta_envios)      # Pega os IDs dos envios
    banco_envios = cursor.fetchall()

# E-mails e formação da mensagem
fromaddr = os.getenv("LOGIN_ANES_OBSERVATORIO")
toaddr = ''

# Pegando os IDs e os e-mails das entidades
if condicao:
    for id, email in entidades_banco:
        toaddr += str(email) + ';'   # Forma uma String com as entidades dentro do Banco para formar o cabeçalho do E-mail
        ids_entidades.append(id)     # Armazena na "ids_entidades" os IDs das entidades dentro do Banco
    toaddr += 'radames@unochapeco.edu.br;monica@unochapeco.edu.br'
else:
    toaddr = 'chapeco.adm@osbrasil.org.br;executivo@sicom.com.br;executivo@acichapeco.com.br;executivo@chapeco.cdl-SC.org.br;radames@unochapeco.edu.br;monica@unochapeco.edu.br'

# Formando o cabeçalho
msg = MIMEMultipart()
msg['From'] = formataddr(('Anes C.', fromaddr))
msg['To'] = toaddr
msg['Subject'] = ''

# Formando o título da mensagem
if str(agora) == str(depois):   # Como em algumas situações as duas várivaeis podem ser iguais, o título só comportará uma delas
    msg['Subject'] += "Editais: " + str(agora) + " - OSB Chapecó/SC"
else:                           # Se forem diferentes, o título seguirá o "normal"
    msg['Subject'] += "Editais: " + str(agora) + " a " + str(depois) + " - OSB Chapecó/SC"

if condicao:
    # Pega os IDs dos editais enviados nas mensagens dentro do Banco
    for id_edital, edital in banco_editais:
        try:
            if edital in editais_mensagem:
                editais_id.append(id_edital)
        except:
            None

    try:
        editais_id = fc.remover_repetidos(editais_id)
    except:
        None

    # Próximos blocos populam o Banco de Dados
    try:
        # Popula tabela "Envios"
        if banco_envios == []:
            # Cria um erro propositalmente para cair na excecção e inserir os dados caso a tabela/lista esteja vázia
            raise Exception("O Banco de Dados está vázio!")
        else:
            # Pega o ID maximo dos editais dentro do Banco para que não se repitam
            item_maximo = max(int(id[0]) for id in banco_envios)
            for id_entidade in ids_entidades:
                item_maximo = item_maximo + 1                # Faz o ID se auto-incrementar
                envios_banco = dict()                        # Dicionario para armazenar os dados no Banco
                envios_banco['id'] = item_maximo    # IDs da própria tabela "Envios" (Primary Key)
                envios_banco['id_entidade'] = id_entidade   # IDs das entidades da tabela "Entidades" (Foreign Key)
                envios_banco['data_hora'] = datetime.now()   # Horário do envio das mensagens
                cursor.execute(insert_data_envios, envios_banco)
                cnx.commit()
                ids_envios.append(item_maximo)               # IDs dos envio são armazenados em uma lista para serem conectados à "Editais" pela tabela "Mensagens"
    except:
        # Se o Banco de dados está vazio é feito do zero (0)
        item_maximo = 0
        for id_entidade in ids_entidades:
            item_maximo = item_maximo + 1
            envios_banco = dict()
            envios_banco['id'] = item_maximo
            envios_banco['id_entidade'] = id_entidade
            envios_banco['data_hora'] = datetime.now()
            cursor.execute(insert_data_envios, envios_banco)
            cnx.commit()
            ids_envios.append(item_maximo)

    if editais_id != []:        
        # Se há editais maiores que a data atual dentro da tabela HTML, a tabela "Mensagens" é populada 
        for id_envio in ids_envios:
            for edital_id in editais_id:
                mensagens = dict()
                mensagens['id_mensagem'] = id_envio    # IDs dos envios para as entidades
                mensagens['id_edital'] = edital_id  # IDs de cada edital enviado
                cursor.execute(insert_data_mensagens, mensagens)
                cnx.commit()
    cursor.close()
    cnx.close()

# Mensagem em HTML
body = '''<!DOCTYPE html>
<html style="height: 100%;">
    <head>
        <title>Mensagem de e-mail</title>
        <meta charset="utf-8">
    </head>
    <body style="height: 100%;width: 100%;background-color:#E5FFE5">
        <div align="center" style="height: 100%;width: 100%;font-size:medium;font-family:Times New Roman;">
            <div align="center" style="height: 100%;width: 100%;font-size:medium;">
                <div align="center" style="height: 100%;width: 100%;font-size:medium;">
                    <div align="center" style="height: 100%;width: 100%;font-size:medium;">
                        <br>
                        <div align="center" style="font-size:11pt;font-family:Calibri,sans-serif;text-align:center;margin:0 0;">
                            <a href='https://chapeco.osbrasil.org.br/processos-licitatorios/'>
                                <img src="cid:image1" class="media-object img-responsive img-thumbnail">
                            </a>
                        </div>
                        <br>
                        <br>
                        <p style="font-family:Calibri,sans-serif;text-align:center;margin:0;"><span style="font-size:9pt;">&nbsp;''' + gerar_tabela['Frase'] + '''</span></p>
                        <br>''' + gerar_tabela['HTML'] + '''
                        <br>
                        <p style="font-family:Calibri,sans-serif;text-align:center;margin:0;"><span style="font-size:9pt;">&nbsp;O Observatório Social do Brasil, disponibiliza, através da “Escola da Cidadania”, Capacitações sobre Licitações, on-line, totalmente gratuitas.<br>Link de Acesso:<br><a href="https://escoladacidadania.osbrasil.org.br/cursos-sobre-licitacao/" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" style="color:blue;text-decoration:underline;" data-safelink="true" data-linkindex="0">https://escoladacidadania.osbrasil.org.br/cursos-sobre-licitacao/</a>.</span></p>
                        <br>
                        <p style="font-family:Calibri,sans-serif;text-align:center;margin:0;"><span style="font-size:9pt;">O Observatório Social do Brasil de Chapecó estará promovendo no primeiro semestre de 2023, capacitação teórica e prática sobre a nova lei de licitações, Lei nº 14.133/2021, totalmente gratuita.<br>Faça sua inscrição prévia no link abaixo:<br><a href="https://docs.google.com/forms/d/e/1FAIpQLSdflbOZIhz7SuMIF1jiNMcFaPuHItrzVDjQ7w3_9IrdZ-70QQ/viewform" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" style="color:blue;text-decoration:underline;" data-safelink="true" data-linkindex="0">https://docs.google.com/forms/d/e/1FAIpQLSdflbOZIhz7SuMIF1jiNMcFaPuHItrzVDjQ7w3_9IrdZ-70QQ/viewform</a>.</span></p>
                        <br>
                        <div>
                            <p text-align="center" style="font-size:11pt;font-family:Calibri,sans-serif;text-align:center;margin:0;">
                                <b>
                                    <span style="font-size:16pt;">Observatório Social do Brasil – Chapecó/SC</span>
                                </b>
                            </p>
                            <p align="center" style="font-size:11pt;font-family:Calibri,sans-serif;text-align:center;margin:0;">
                                <span style="font-size:9pt;">Avenida Getúlio Vargas, 1748 N, Centro | Condomínio Coworking – sala 3| CEP 89805-000</span>
                            </p>
                            <p align="center" style="font-size:11pt;font-family:Calibri,sans-serif;text-align:center;margin:0;">
                                <span style="font-size:9pt;">E-mail:<span>&nbsp;</span></span>
                                <a href="mailto:chapeco@osbrasil.org.br" target="_blank" rel="noopener noreferrer" data-auth="NotApplicable" style="color:blue;text-decoration:underline;" data-safelink="true" data-linkindex="0">
                                    <span style="font-size:9pt;">chapeco@osbrasil.org.br</span>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>'''

msg.attach(MIMEText(body, 'html'))

# Imagem anexada
image = MIMEImage(open(FOLDER_PATH + "logo_osb_chapeco_header.png", 'rb').read())
image.add_header('Content-ID', '<image1>')
msg.attach(image)

# Anexando primeira planilha
filename = ''

if str(agora) == str(depois):
    filename += "Editais_" + str(agora) + ".csv"
else:
    filename += 'Editais_' + str(agora) + '_' + str(depois) + '.csv'

attachment = open(FOLDER_PATH + "editais_dados.csv",'rb')

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

attachment.close()

# Envio do e-mail
server = smtplib.SMTP('smtp-mail.outlook.com', 587)
server.starttls()
server.login(fromaddr, os.getenv("SENHA_ANES_OBSERVATORIO"))
text = msg.as_string().encode('utf-8')
server.sendmail(fromaddr, toaddr.split(";"), text)
server.quit()
print('\n---------------------\nE-mail enviado com sucesso!')

############################################### "Injetando" a tabela no site ###############################################
import os
import time
import dotenv
import pyperclip as pc
import selenium.webdriver as webd1
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)
tabela_gerada = gerar_tabela['HTML']
if tabela_gerada == '':
    tabela_gerada = '<p style="font-family:Calibri,sans-serif;text-align:center;margin:0;"><span style="font-size:9pt;">&nbsp;Não haverá editais para os próximos sete dias. Mas fique de olho! Em breve serão liberados novos.</span></p>'
else:
    tabela_gerada = tabela_gerada.replace(u'60%', u'80%')
login = os.getenv("LOGIN_OBS_CHAPECO")
senha = os.getenv("SENHA_OBS_CHAPECO")
url = "https://chapeco.osbrasil.org.br/wp-admin/post.php?post=1424&action=elementor"
driver = webd1.Chrome(executable_path="C:/Users/Desenvolvimento/.wdm/drivers/chromedriver/win64/115.0.5790.111/chromedriver.exe")
driver.get(url)
wait = WebDriverWait(driver, 10)
time.sleep(5)

# Logando no site para editar
login_html = driver.find_element(By.XPATH, "/html/body/div[1]/form/p[1]/input")
senha_html = driver.find_element(By.XPATH, "/html/body/div[1]/form/div/div/input[1]")
acessar_html = driver.find_element(By.XPATH, "/html/body/div[1]/form/p[3]/input[1]")

login_html.send_keys(login)
senha_html.send_keys(senha)
acessar_html.click()
time.sleep(5)

# Acessando a área de texto
element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/aside[2]/div[1]/div[1]/button[1]/i')))
element.click()
time.sleep(3)

botao_texto = driver.find_element(By.XPATH, "/html/body/div[4]/aside[2]/div[1]/div[2]/div/div/div/div[2]/div/div[2]/div/div[1]/div[2]/i")
botao_texto.click()
time.sleep(3)

botao_texto_2 = driver.find_element(By.XPATH, "/html/body/div[4]/aside[1]/div[1]/main/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/button[2]")
botao_texto_2.click()
time.sleep(3)

# Inserindo o HTML da tabela
caixa_tabela = driver.find_element(By.XPATH, "/html/body/div[4]/aside[1]/div[1]/main/div[1]/div[2]/div[2]/div/div/div[2]/div/div[2]/textarea")
caixa_tabela.clear()
pc.copy(tabela_gerada)
caixa_tabela.send_keys(Keys.CONTROL, 'v')
time.sleep(3)

# Atualizado a página
botao_atualizar = driver.find_element(By.XPATH, "/html/body/div[4]/aside[1]/div[1]/footer/nav/div[1]/button")
botao_atualizar.click()
time.sleep(3)

driver.close()
print("\n---------------------\nTabela atualizada!")