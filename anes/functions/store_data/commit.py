from functions.capture_data import detalhes_editais as de
from mysql.connector import errorcode
from datetime import date
import mysql.connector
import pandas as pd

#---------------------------------------------------------------------------------------------------------
# Função que "commita" os dados no Banco
def commit(caminho_arquivo, pdf, df):
    try:
        condicoes_2 = []

        # Pega o nº do Edital
        edital = de.get_detalhes_editais(caminho_arquivo)['edital']

        # Se a variável edital for lista (caso seja DL ou Inexigibilidade), pega qual das duas versões está de acordo com o Dataframe
        if type(edital) is list:
            editais_1 = df['Edital'].tolist()
            edital_1 = edital[0]
            edital_2 = edital[1]

            if edital_1 in editais_1:
                edital = edital_1
            elif edital_2 in editais_1:
                edital = edital_2

        # Abrir conexão com Banco de Dados
        cnx = mysql.connector.connect(user='root', password='', host="127.0.0.1", database="Observatorio")

        # Consultas e Inserção de Dados
        consulta_editais = "select edital from edital"
        consulta_sql = "select * from edital where edital = '" + str(edital) + "'"
        insert_sql = ("INSERT INTO edital (data, edital, secretaria, pdf, horario, forma_julgamento, objeto, montante, link_pagina, local, modalidade, unidade_gestora, tipo, id_cidade) " +
        "VALUES (%(data)s, %(edital)s, %(secretaria)s, %(pdf)s, %(horario)s, %(forma_julgamento)s, %(objeto)s, %(montante)s, %(link_pagina)s, %(local)s, %(modalidade)s, %(unidade_gestora)s, %(tipo)s, %(id_cidade)s)")

        # Pega os dados do Edital (junta com a data)
        detalhes_editais = de.get_detalhes_editais(caminho_arquivo, pdf)

        # Procurando "Data"
        if (detalhes_editais['data'] == None) or (detalhes_editais['data'] < date.today()):
            # Quando não achou nenhuma data, ela é substituida pela data do Dataframe
            df3 = df.loc[df['Edital'] == str(edital)] 
            data_1 = df3['Data'].tolist()[0]
        else:
            data_1 = detalhes_editais['data']   # "data_1" é a variável que irá comparar a data do dicionário com a data do Dataframe

        # Extraí os dados do Dataframe
        df2 = df.loc[df['Edital'] == str(edital)]
        df1 = df2.loc[df2['Data'] == data_1]
        detalhes_editais_2 = dict()
        detalhes_editais_2['data'] = df1['Data'].tolist()[0]
        detalhes_editais_2['horario'] = df1['Horario'].tolist()[0]
        if pd.isna(detalhes_editais_2['horario']):
            detalhes_editais_2['horario'] = None 
        # edital
        detalhes_editais_2['forma_julgamento'] = df1['Forma julgamento'].tolist()[0]
        detalhes_editais_2['modalidade'] = df1['Modalidade'].tolist()[0]
        detalhes_editais_2['objeto'] = df1['Objeto'].tolist()[0]
        # secretaria
        detalhes_editais_2['montante'] = df1['Montante'].tolist()[0]
        detalhes_editais_2['link_pagina'] = df1['Link da Página'].tolist()[0]
        # pdf
        detalhes_editais_2['local'] = df1['Local'].tolist()[0]
        if pd.isna(detalhes_editais_2['local']):
            detalhes_editais_2['local'] = None      
        detalhes_editais_2['unidade_gestora'] = df1['Unidade gestora'].tolist()[0]
        detalhes_editais_2['tipo'] = df1['Tipo'].tolist()[0]     
        detalhes_editais_2['id_cidade'] = 1   # ID da cidade de Chapecó no Banco de Dados  

        # Subtitui os ponto para não serem usados no Banco
        detalhes_editais_2['montante'] = detalhes_editais_2['montante'].replace(u".", u"")
        detalhes_editais_2['montante'] = detalhes_editais_2['montante'].replace(u",", u".")

        # "Atualiza" o dicionário "detalhes_editais"
        detalhes_editais.update(detalhes_editais_2)
        detalhes_editais['edital'] = edital
        cursor = cnx.cursor()

        # Pega os n° dos Editais
        cursor.execute(consulta_editais)
        editais = cursor.fetchall()

        # Percorre o Banco de Dados para averiguar se o nº do Edital já não foi adicionado
        try:
            if editais == []:
                # Cria um erro propositalmente para cair na excecção e inserir os dados caso a lista esteja vázia
                raise Exception("O Banco de Dados está vázio!")
            else:
                # Valida uma condição se o Edital está no Banco
                cursor.execute(consulta_sql)
                editais_2 = cursor.fetchall()

                if editais_2 != []:
                    # Percorre a lista dos editais com a mesma numeração do atual
                    for no_edital in editais_2: 
                        condicoes = []
                        banco_dados = dict()
                        banco_dados['data'] = no_edital[1]
                        banco_dados['horario'] = no_edital[2]
                        banco_dados['edital'] = no_edital[3]
                        banco_dados['forma_julgamento'] = no_edital[4]
                        banco_dados['modalidade'] = no_edital[5]
                        banco_dados['objeto'] = no_edital[6]
                        banco_dados['secretaria'] = no_edital[7]

                        # Comparar e valida a condição se as variáveis são iguais às do Banco
                        verificar_condicao(banco_dados['data'], detalhes_editais['data'], condicoes)
                        verificar_condicao(banco_dados['horario'], detalhes_editais['horario'], condicoes)
                        verificar_condicao(banco_dados['edital'], detalhes_editais['edital'], condicoes)
                        verificar_condicao(banco_dados['forma_julgamento'], detalhes_editais['forma_julgamento'], condicoes)
                        verificar_condicao(banco_dados['modalidade'], detalhes_editais['modalidade'], condicoes)
                        verificar_condicao(banco_dados['objeto'], detalhes_editais['objeto'], condicoes)
                        verificar_condicao(banco_dados['secretaria'], detalhes_editais['secretaria'], condicoes)
                        condicoes = set(condicoes)
                        if False in condicoes:
                            condicao = False
                            condicoes_2.append(condicao)
                        else:
                            condicao = True
                            condicoes_2.append(condicao)
                    # Se o edital não está no banco, cai na exceção e é adicionado
                    condicoes_2 = set(condicoes_2)
                    if True in condicoes_2:
                        # Se não ha condição "Verdadeira" cria uma exceção para inserir o Edital, que não está no Banco
                        raise Exception("O Edital não está no Banco de Dados!")
                    else:
                        print("\n---------------------\nDados já existem no Banco!")
                else:
                    # Se a condição for "Falsa" cria uma exceção para inserir o Edital, que não está no Banco
                    raise Exception("O Edital não está no Banco de Dados!")
        except Exception:
            # Se o Banco de Dados estiver vázio automaticamente adicionará os dados do Edital
            cursor.execute(insert_sql, detalhes_editais)
            cnx.commit()
            print("\n---------------------\nDados adicionados ao Banco!")

        # Fecha cursor e conexão
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Algo esta errado com seu usuario e senha!")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("O Banco de Dados não existe!")
        else:
            print(err)
    else:
        cnx.close()

def verificar_condicao(elem_dict, elem_datab, condicoes):
    if str(elem_dict) == str(elem_datab):
        condicao = True
    else:
        condicao = False
    condicoes.append(condicao)