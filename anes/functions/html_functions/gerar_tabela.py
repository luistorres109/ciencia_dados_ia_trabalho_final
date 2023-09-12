from functions.repeated_code import funcoes as fc
from datetime import date, timedelta
import pandas as pd
import datetime
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)

#---------------------------------------------------------------------------------------------------------
# Função que gera tabela com os editais dentro do espaço de uma semana para a mensagem do observatório
def gerar_tabela():
    editais = []
    tabela_1 = ''
    tabela_2 = ''

    # Forma os Cabeçarios da Tabela dos editais em aberto e da Tabela de DL e Inexigibildiade, nessa ordem
    cabecario_1 = gerar_cabecario()
    cabecario_2 = gerar_cabecario(instituicao="Dispensa De Licitação e Inexigibilidade")

    # Extraí as semanas da tabela
    dataframe = fc.extract_month_dfs(os.getenv("FOLDER_PATH") + "editais_dados.csv")
    df1 = dataframe['df1']
    df2 = dataframe['df2']

    # Possíveis frases para a mensagem
    frase_tabela_preenchida = 'Segue a planilha atualizada das licitações do dia ' + str(date.today().strftime('%d/%m/%Y')) + ' em diante, junto a uma tabela com os editais dos próximos trinta dias.'
    frase_tabela_vazia = 'Não foram encontrados editais para os próximos trinta dias, nem editais de Inexigibilidade e de Dispensa de Licitação. Entretanto, segue anexo o arquivo da planilha dos editais seguintes.'
    frase_tabela_vazia_inexi_dl = 'Não foram encontrados editais para os próximos trinta dias, somente os editais de Inexigibilidade e de Dispensa de Licitação deste ano. Entretanto, segue anexo o arquivo da planilha dos editais seguintes.'
    frase_tabela_preenchida_inexi_dl = 'Segue a planilha atualizada das licitações do dia ' + str(date.today().strftime('%d/%m/%Y')) + ' em diante, junto aos editais de Inexigibilidade e de Dispensa de Licitação e anexa uma tabela com os editais dos próximos trinta dias.'

    # Extraindo a primeira data para comparar com um mês depois da data atual
    try:
        primeira_data = df1.iloc[int(0)]['Data']
        primeira_data = datetime.datetime.strptime(primeira_data, '%Y-%m-%d').date()
        mes = date.today() + timedelta(30)
    except:
        primeira_data = date.today()
        mes = date.today() + timedelta(30)

    # Ao comparar, verifica se a primeira data que aparece no edital é maior que a data de um mês depois (se sim, cria-se um dataframe vázio)
    if primeira_data > mes:
        df1 = pd.DataFrame(columns=['Data', 'Horario', 'Edital', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Montante', 'Tipo', 'Link da Página'])

    # Corpo da mensagem, verificação se o dataframe é vázio e contagem para capturar o índice final
    html = ''
    condicao = df1.empty
    condicao_2 = df2.empty

    # Extrai os dados se o dataframe está preenchido
    dicionario_1 = extract_table_html(condicao, df1, editais)
    dicionario_2 = extract_table_html(condicao_2, df2)
    corpo_1 = dicionario_1['corpo']
    corpo_2 = dicionario_2['corpo']
    contagem = dicionario_1['contagem']

    # Construção da tabela
    if condicao == False:
        tabela_1 += cabecario_1 + corpo_1 

    if condicao_2 == False:
        tabela_2 += cabecario_2 + corpo_2

    # Incorpora tudo num HTML
    html += '''<table align="center" style="color: black;width: 60%;overflow-x: scroll;border: 1px solid black;border-collapse: collapse;">''' + tabela_1 + tabela_2 + '</table>'

    if condicao == False and condicao_2 == False:
        frase = frase_tabela_preenchida_inexi_dl
    elif condicao == False and condicao_2:
        frase = frase_tabela_preenchida
    elif condicao and condicao_2 == False:
        frase = frase_tabela_vazia_inexi_dl
    else:
        # Se o dataframe é vázio, retorna está mensagem
        frase = frase_tabela_vazia
        html = ''

    # Cria um dicionário que sera usado na mensagem do E-mail
    dicionario = dict()
    try:
        # Caso o Dataframe esteja preenchido
        dicionario['Ultima data'] = str(df1.iloc[int(contagem)]['Data'])
    except:
        # Caso o Dataframe esteja vázio
        dicionario['Ultima data'] = None
    dicionario['Frase'] = frase
    dicionario['HTML'] = html
    dicionario['Editais'] = editais

    return dicionario

def extract_table_html(condicao, df, editais=None):
    # Extrai os dados se o dataframe está preenchido
    contagem = None

    corpo = ''
    if condicao == False:
        for index in range(len(df)):
            data = df.iloc[int(index)]['Data']
            horario = df.iloc[int(index)]['Horario']
            if pd.isna(horario):
                horario = ''
            edital = df.iloc[int(index)]['Edital']
            link = df.iloc[int(index)]['Link da Página']
            objeto = df.iloc[int(index)]['Objeto']
            objeto = objeto.lower()
            objeto = objeto.title()
            montante = df.iloc[int(index)]['Montante']
            modalidade = df.iloc[int(index)]['Modalidade']
            gestora = df.iloc[int(index)]['Unidade gestora']
            secretaria = df.iloc[int(index)]['Secretária']

            corpo += '''
        <tr>
            <td style="background-color:#E5FFE5;text-align: center;border: 1px solid black;">''' + str(datetime.datetime.strptime(data, '%Y-%m-%d').date().strftime('%d/%m/%Y')) + '''</td>
            <td style="background-color:#E5FFE5;text-align: center;border: 1px solid black;">''' + str(horario) + '''</td>
            <td style="background-color:#E5FFE5;margin-left: 15px;margin-right: 15px;text-align: center;border: 1px solid black;"><a href='''+link+'''><b>''' + str(edital) +'''</b></a></td>
            <td style="background-color:#E5FFE5;text-align: justify;border: 1px solid black;">''' + str(objeto) + '''</td>
            <td style="background-color:#E5FFE5;text-align: right;border: 1px solid black;">''' + str(montante) + '''</td>
            <td style="background-color:#E5FFE5;text-align: left;border: 1px solid black;">''' + str(modalidade) + '''</td>
            <td style="background-color:#E5FFE5;text-align: justify;border: 1px solid black;">''' + str(gestora) + '''</td>
            <td style="background-color:#E5FFE5;text-align: justify;border: 1px solid black;">''' + str(secretaria) + '''</td>
        </tr>
            '''

            contagem = index
            try:
                editais.append(edital)
            except:
                None
    else:
        contagem = 0

    dicionario = dict()
    dicionario['corpo'] = '<tbody>' + corpo + '</tbody>'
    dicionario['contagem'] = contagem

    return dicionario

def gerar_cabecario(instituicao=None):
    if type(instituicao) is not str:
        instituicao = ''
    elif instituicao != '':
        instituicao = '''<tr>
        <th style="text-align: center;border: 1px solid black;" colspan="8">'''+instituicao+'''</th>
        </tr>'''
    cabecario = '''
        <thead style="background-color: #32CD32;">
            '''+instituicao+'''
            <tr>
                <th style="text-align: center;border: 1px solid black;">Data</th>
                <th style="text-align: center;border: 1px solid black;">Horario</th>
                <th style="text-align: center;border: 1px solid black;">Edital</th>
                <th style="text-align: center;border: 1px solid black;">Objeto</th>
                <th style="text-align: center;border: 1px solid black;">Montante</th>
                <th style="text-align: center;border: 1px solid black;">Modalidade</th>
                <th style="text-align: center;border: 1px solid black;">Gestora</th>
                <th style="text-align: center;border: 1px solid black;">Secretária</th>
            </tr>
        </thead>'''

    return cabecario