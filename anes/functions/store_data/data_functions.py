from functions.capture_data import detalhes_editais as de
from functions.repeated_code import funcoes as fc
from functions.store_data import commit as cm
from datetime import date
import pandas as pd
import datetime
import csv

#---------------------------------------------------------------------------------------------------------
# Insere os dados na tabela e no Banco de Dados
def insert_data(tabela, caminho_arquivo, pdf, df):
    # Pega os valores dos editais
    detalhes_editais = de.get_detalhes_editais(caminho_arquivo)

    # Armazenando os dados
    edital = detalhes_editais['edital']
    secretaria = detalhes_editais['secretaria']

    if type(edital) is list:
        editais_1 = df['Edital'].tolist()
        edital_1 = edital[0]
        edital_2 = edital[1]

        if edital_1 in editais_1:
            edital = edital_1
        elif edital_2 in editais_1:
            edital = edital_2

    # Procurando "Data"
    if (detalhes_editais['data'] == None) or (detalhes_editais['data'] < date.today()):
        df3 = df.loc[df['Edital'] == str(edital)] 
        data_1 = df3['Data'].tolist()[0]
    else:
        data_1 = detalhes_editais['data']
    # Extrai os dados do Dataframe
    df2 = df.loc[df['Edital'] == str(edital)]
    df1 = df2.loc[df2['Data'] == data_1]
    data = df1['Data'].tolist()[0]
    horario = df1['Horario'].tolist()[0]
    # edital
    local = df1['Local'].tolist()[0]
    modalidade = df1['Modalidade'].tolist()[0]
    julgamento = df1['Forma julgamento'].tolist()[0]
    gestora = df1['Unidade gestora'].tolist()[0]
    # secretaria
    objeto = df1['Objeto'].tolist()[0]
    montante = df1['Montante'].tolist()[0]
    tipo = df1['Tipo'].tolist()[0]
    link = df1['Link da Página'].tolist()[0]

    if (((modalidade == 'Inexigibilidade') or (modalidade == 'Dispensa De Licitação') or (modalidade == 'Dispensa Por Justificativa')) and (horario != '')) != True:
        # Colunas e seus dados
        colunas = "Data;Horario;Edital;Local;Modalidade;Forma julgamento;Unidade gestora;Secretária;Objeto;Montante;Tipo;Link da Página"
        dados = "\n" + str(data) + ";" + str(horario) + ";" + str(edital) + ";" + str(local) + ";" + str(modalidade) + ";" + str(julgamento) + ";" + str(gestora) + ";" + str(secretaria) + ";" + str(objeto) + ";" + str(montante) + ";" + str(tipo) + ";" + str(link)
        dados_2 = dados.replace(u'\n', u'')
        dados_2 = dados_2.replace(u'"', u'')

        # Resultado que será "True" ou "False" para averiguar se o nº do Edital está na Tabela CSV ou não
        resultado = None

        try:
            with open(tabela, 'r', newline='', encoding='utf-8-sig') as file:
                reader_obj = csv.reader(file, delimiter=';')

                for linha in reader_obj:
                    linha = fc.format_linha(linha)
                    if dados_2 == linha:
                        resultado = True
                        break
                    else:
                        resultado = False
                file.close()
        except:
            print("\n---------------------\nTabela não exise!")
            resultado = False

        # Cria um arquivo CSV
        with open(tabela, 'a+', newline='', encoding='utf-8-sig') as arquivo:
            try:
                # Faz a contagem de linhas
                df_arquivo = pd.read_csv(tabela, delimiter=';').reset_index(drop=True)
                qtd_linhas = len(df_arquivo) + 1

                # Escreve os dados se a quantidade de linhas for maior que 1 e se o Edital já não tiver escrito
                if qtd_linhas > 1:
                    if resultado:
                        print("\n---------------------\nEdital já existe na tabela!")
                    else:
                        arquivo.write(dados.replace(u'"', u''))
                        print("\n---------------------\nDados Adicionados!")
            except:
                arquivo.write(colunas)
                arquivo.write(dados.replace(u'"', u''))
                print("\n---------------------\nTabela Criada e Dados Adicionados!")
            # Fecha o arquivo
            arquivo.close()
        cm.commit(caminho_arquivo, pdf, df)
    else:
        print('\n---------------------\nEdital Inválido!')

#---------------------------------------------------------------------------------------------------------
# Função que remove editais homologados ou invalidos
def del_data(tabela):
    try:
        # Ler a tabela e converter coluna 'Data' para datetime
        df = pd.read_csv(tabela, delimiter=';', parse_dates=['Data']).reset_index(drop=True)

        # Filtrar linhas com datas homologadas
        today = date.today()

        # Sub-função que confere linha por linha se ela é valida ou não
        def is_valid_date(row):
            data = row['Data'].date()
            if data >= today:
                return True
            elif data < today and row['Modalidade'] in ['Inexigibilidade', 'Dispensa por Justificativa', 'Dispensa De Licitação']:
                if data.year == today.year:
                    return True
            return False

        # Remover dados
        df = df[df.apply(is_valid_date, axis=1)]
        df = df.drop_duplicates(subset=['Data', 'Horario', 'Edital', 'Objeto'])

        # Salvar a tabela modificada
        df.to_csv(tabela, index=False, encoding='utf-8-sig', sep=";")
        print("\n---------------------\nDatas deletadas!")
    except:
        print("\n---------------------\nErro ao processar o arquivo!")

#---------------------------------------------------------------------------------------------------------
# Função para por as datas em Ordem Cronológica
def order_dates(tabela):
    # Listas vázias
    indexes = []

    # Lê as datas
    df = pd.read_csv(tabela, delimiter=';').reset_index(drop=True)
    datas = df['Data'].tolist()

    # Coloca as datas em Ordem Cronológica, dentro de uma Lista
    datas.sort(key = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d'))

    # Removê datas repetidas
    datas = fc.remover_repetidos(datas)

    # Pega os índices
    for data in datas:
        indexes.append(df[df['Data'] == str(data)].index)

    # Se livra de Chars desnecessários e, sendo convertido em String, é desmembrado para depois voltar a ser Lista
    indexes = fc.extrair_indices(indexes)
    
    df1 = fc.extrair_dataframes(indexes, df)

    # Coloca o Dataframe dentro da Tabela CSV
    df1.to_csv(tabela, index = False, encoding = 'utf-8-sig', sep = ";")
    print("\n---------------------\nDatas em ordem!")