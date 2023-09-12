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
