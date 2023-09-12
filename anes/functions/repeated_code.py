from datetime import date, timedelta
import pandas as pd
import datetime

#---------------------------------------------------------------------------------------------------------
# Função que remove itens repetidos
def remover_repetidos(lista):
    l = []
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
    return l

#---------------------------------------------------------------------------------------------------------
# Funções para formatar listas
def format_linha(linha):
    # Função que formata as linhas em lista quando fazer uso da biblioteca CSV
    linha = str(linha)
    linha = linha.replace("['", '')
    linha = linha.replace("']", '')
    linha = linha.replace("', '", ';')

    return linha

def extrair_indices(indexes):
    # Função que extrai indices mal-formatados, se livrando de Chars desnecessários e, sendo convertido em String, é desmembrado para depois voltar a ser Lista
    indexes = str(indexes).replace(u'Int64Index([', u'')
    indexes = indexes.replace(u"], dtype='int64')", u"")
    indexes = indexes.replace(u"]", u"")
    indexes = indexes.replace(u"[", u"")
    indexes = indexes.replace(u" ", u"")
    indexes = indexes.split(',')

    return indexes

#---------------------------------------------------------------------------------------------------------
# Função que extrai dataframes, com base nos indices
def extrair_dataframes(indexes, df):
    linhas = []
    # Lista que conterá sub-listas com os dados extraídos do dataframe para formar o novo dataframe

    for index in indexes:
        # Extrai os dados de cada linha, um por um
        data = df.iloc[int(index)]['Data']
        horario = df.iloc[int(index)]['Horario']
        edital = df.iloc[int(index)]['Edital']
        local = df.iloc[int(index)]['Local']
        modalidade = df.iloc[int(index)]['Modalidade']
        julgamento = df.iloc[int(index)]['Forma julgamento']
        gestora = df.iloc[int(index)]['Unidade gestora']
        secretaria = df.iloc[int(index)]['Secretária']
        objeto = df.iloc[int(index)]['Objeto']
        montante = df.iloc[int(index)]['Montante']
        tipo = df.iloc[int(index)]['Tipo']
        link = df.iloc[int(index)]['Link da Página']

        # Coloca-os em uma sub-lista
        linha = [data, horario, edital, local, modalidade, julgamento, gestora, secretaria, objeto, montante, tipo, link]
        linhas.append(linha)

    # Cria um Dataframe com os dados
    result_df = pd.DataFrame(linhas, columns=['Data', 'Horario', 'Edital', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Montante', 'Tipo', 'Link da Página'])

    return result_df
