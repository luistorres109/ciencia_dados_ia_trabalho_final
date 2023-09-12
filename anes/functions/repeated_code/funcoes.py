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
# Funções para extraem dataframes para serem usados na tabela HTML
def extrair_dataframes(indexes, df):
    # Função que se repete em "extrair_dataframes_tabela_html"
    # Ela serve para extrair qualquer dataframe, com base no índice

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

def extrair_dataframes_tabela_html(indexes, df):
    # Função que se repete em "extract_week_dates"
    # Ela serve para criar os Dataframes e tratar de exceções caso estejam vazios
    indexes = extrair_indices(indexes)

    try:
        result_df = extrair_dataframes(indexes, df)
    except:
        result_df = pd.DataFrame(columns=['Data', 'Horario', 'Edital', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Montante', 'Tipo', 'Link da Página'])

    return result_df

def extract_month_dfs(tabela):
    # Função para extrai dois dataframes
    # Um com as datas de um mês depois e outro com os editais homologados (de modalidades de Inexigibilidade e Dispensa)
    datas_mes = []             # Lista que terá os editais menores do que a data daqui a 30 dias a partir da data atual
    datas_abertos = []         # Lista com as datas dos editais em aberto
    datas_homologados = []     # Lista com a data dos editais homologados
    indexes_abertos = []       # Lista com os indices dos editais em aberto
    indexes_homologados = []   # Lista com os indices dos editais homologados

    # Lê as datas
    df = pd.read_csv(tabela, delimiter=';').reset_index(drop=True)
    datas = df['Data'].tolist()

    # Coloca as datas em Ordem Cronológica, dentro de uma Lista
    datas.sort(key = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d'))

    # Pega a data de agora e a daqui um mês
    agora = date.today()
    depois = timedelta(30)

    # Pega as datas menores do que a data daqui a 30 dias a partir da data atual
    for data in datas:
        if datetime.datetime.strptime(data, '%Y-%m-%d').date() <= (agora + depois):
            datas_mes.append(data)

    # Garante que as datas não se repitam
    datas_mes = remover_repetidos(datas_mes)

    for data in datas_mes:
        if datetime.datetime.strptime(str(data), '%Y-%m-%d').date() >= agora:
            datas_abertos.append(data)
        elif datetime.datetime.strptime(str(data), '%Y-%m-%d').date() < agora:
            datas_homologados.append(data)           

    datas_homologados = remover_repetidos(datas_homologados)

    # Pega os índices
    for data in datas_abertos:
        indexes_abertos.append(df[df['Data'] == str(data)].index)

    for data in datas_homologados:
        indexes_homologados.append(df[df['Data'] == str(data)].index)

    # Gera os dois Dataframes
    df1 = extrair_dataframes_tabela_html(indexes_abertos, df)       # Este contem as datas maiores que a data atual até uma semana depois
    df2 = extrair_dataframes_tabela_html(indexes_homologados, df)   # Este contem os editais de Inexigiblidade e DL

    # Cria um Dataframe com os dados
    dataframes = dict()
    dataframes['df1'] = df1
    dataframes['df2'] = df2

    return dataframes