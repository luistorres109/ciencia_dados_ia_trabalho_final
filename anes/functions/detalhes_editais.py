from tika import parser
import datetime
import re

#---------------------------------------------------------------------------------------------------------
# Função que extrai dados dos PDFs
def get_detalhes_editais(caminho_arquivo):
    # Lê o arquivo
    raw = parser.from_file(caminho_arquivo)
    dados = raw['content']
    dados = dados.replace("\n", " ") # Resolve espaçamentos em quebra de linha
    dados = dados.replace("  ", " ") # Garante que não haverá mais de dois espaçamentos em um espaço em branco

    # Procurar nº do Edital
    try:
        # Caso do edital seja de Concurso
        edital = str(re.search(r'CONCURSO [a-zA-Z0-9]{1,5}/\d{4}', dados).group())
        edital = re.sub(r'CONCURSO ', '', edital)
    except:
        # Casos gerais
        edital_1 = str(re.search(r'([Cc][Oo][Nn][Cc][Oo][Rr][Rr][Êê][Nn][Cc][Ii][Aa]|[Cc][Oo][Nn][Cc][Uu][Rr][Ss][Oo]|[Cc][Oo][Nn][Vv][Ii][Tt][Ee]|[Cc][Rr][Ee][Dd][Ee][Nn][Cc][Ii][Aa][Mm][Ee][Nn][Tt][Oo]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa] [Pp][Oo][Rr] [Jj][Uu][Ss][Tt][Ii][Ff][Ii][Cc][Aa][Tt][Ii][Vv][Aa]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa] [Dd][Ee] [Ll][Ii][Cc][Ii][Tt][Aa][Çç][Ãã][Oo]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa]|[Ii][Nn][Ee][Xx][Ii][Gg][Ii][Bb][Ii][Ll][Ii][Dd][Aa][Dd][Ee]|[Ii][Nn][Ee][Xx][Ii][Gg][Ii][Bb][Ii][Ll][Ii][Dd][Aa][Dd][Ee] [Dd][Ee] [Ll][Ii][Cc][Ii][Tt][Aa][Çç][Ãã][Oo]|[Ll][Ee][Ii][Ll][Ãã][Oo]|[Tt][Oo][Mm][Aa][Dd][Aa] [Dd][Ee] [Pp][Rr][Ee][Çç][Oo][Ss]|[Pp][Rr][Ee][Gg][Ãã][Oo] [Ee][Ll][Ee][Tt][Rr][Ôô][Nn][Ii][Cc][Oo]|[Pp][Rr][Ee][Gg][Ãã][Oo] [Pp][Rr][Ee][Ss][Ee][Nn][Cc][Ii][Aa][Ll]|[Cc][Hh][Aa][Mm][Aa][Mm][Ee][Nn][Tt][Oo] [Pp][Úú][Bb][Ll][Ii][Cc][Oo])? ?(n|N).?(°|º) [a-zA-Z0-9]{1,5}/\d{4}', dados).group())

        # Padroniza o edital |(isso serve se o edital for alfa numérico)
        edital_1 = padronizar_edital('Inexigibilidade de licitação', 'IL', edital_1)
        edital_1 = padronizar_edital('Dispensa por Justificativa', 'DL', edital_1)
        edital_1 = padronizar_edital('DISPENSA DE LICITAÇÃO', 'DL', edital_1)
        edital_1 = padronizar_edital('EGÃO PRESENCIAL', 'PR', edital_1)
        edital_1 = padronizar_edital('EGÃO ELETRÔNICO', 'PR', edital_1)  # Nestas duas últimas a palavra "PREGÃO" precisou ser cortada se não o algoritmo enterpretaria a silga PR como parte
        edital_1 = padronizar_edital('CONVITE', 'CV', edital_1)
        edital_1 = re.sub(r'[Cc][Oo][Nn][Cc][Oo][Rr][Rr][Êê][Nn][Cc][Ii][Aa]|[Cc][Oo][Nn][Cc][Uu][Rr][Ss][Oo]|[Cc][Oo][Nn][Vv][Ii][Tt][Ee]|[Cc][Rr][Ee][Dd][Ee][Nn][Cc][Ii][Aa][Mm][Ee][Nn][Tt][Oo]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa] [Pp][Oo][Rr] [Jj][Uu][Ss][Tt][Ii][Ff][Ii][Cc][Aa][Tt][Ii][Vv][Aa]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa] [Dd][Ee] [Ll][Ii][Cc][Ii][Tt][Aa][Çç][Ãã][Oo]|[Dd][Ii][Ss][Pp][Ee][Nn][Ss][Aa]|[Ii][Nn][Ee][Xx][Ii][Gg][Ii][Bb][Ii][Ll][Ii][Dd][Aa][Dd][Ee]|[Ii][Nn][Ee][Xx][Ii][Gg][Ii][Bb][Ii][Ll][Ii][Dd][Aa][Dd][Ee] [Dd][Ee] [Ll][Ii][Cc][Ii][Tt][Aa][Çç][Ãã][Oo]|[Ll][Ee][Ii][Ll][Ãã][Oo]|[Tt][Oo][Mm][Aa][Dd][Aa] [Dd][Ee] [Pp][Rr][Ee][Çç][Oo][Ss]|[Pp][Rr][Ee][Gg][Ãã][Oo] [Ee][Ll][Ee][Tt][Rr][Ôô][Nn][Ii][Cc][Oo]|[Pp][Rr][Ee][Gg][Ãã][Oo] [Pp][Rr][Ee][Ss][Ee][Nn][Cc][Ii][Aa][Ll]|[Cc][Hh][Aa][Mm][Aa][Mm][Ee][Nn][Tt][Oo] [Pp][Úú][Bb][Ll][Ii][Cc][Oo]', '', edital_1)
        edital_1 = re.sub(r'(n|N).?(°|º) ', '', edital_1)
        edital_1 = edital_1.replace(u' ', u'')

        # Procura o nº de novo caso a numeração não seja alfa-numérica
        edital_2 = re.search(r'(n|N).?(°|º) [a-zA-Z0-9]{1,5}/\d{4}', dados).group()
        edital_2 = re.sub(r'(n|N).?(°|º) ', '', edital_2)

        # Compara as nunerações extraídas
        if edital_1 == edital_2:
            edital = edital_2
        else:
            # Se forem diferentes, virá uma lista
            edital = [edital_1, edital_2]

        # Garantir que o primeiro caractere da String Edital não seja zero se tiver mais de 8 caracteres (caso a prefeitura tente burlar o sistema)
        if type(edital) is list:
            for edital1_1 in edital:
                if (len(edital1_1) > 8) and (edital1_1[0] == '0'):
                    edital1_1 = edital1_1[1:]
        else:
            if (len(edital) > 8) and (edital[0] == '0'):
                edital = edital[1:]

    # Procurar e padronizar dados
    secretaria = re.search(r'(Secret(á|a)ri(o|a) ?(Municipal)?|(Procurad|Diret|Coordenad)or((i)?a)? ?(Geral)?|Fundação Cultural|Assessori?a?) (d(e|a|o))? ?(Efapi|Comunicação Social|Regularização Fundiária e Habitação|Família e Proteção Social|Município|Chapecó|Serviços Urbanos|Segurança( Pública)?|Juventude, Esporte e Lazer|Governo|(Fazenda e )?Administração|Saúde|Planejamento e Desenvolvimento|Gestão Administrativa|Infraestrutura Urbana|Assistência Social|Educação|Coordenação de Governo e Gestão|Defesa do Cidadão e Mobilidade Urbana|Desenvolvimento (Rural( e Meio Ambiente)?|Urbano|Sustentável e Obras Estruturantes)|Cultura|Comunicação)|Superintend(ente|ência) (Regional)? ?(do|da) (Prefeitura Municipal de Chapecó|Grande Efapi|Distrito (d(o|e))? ?Marechal Bormann)|Câmara Municipal de Chapecó', dados).group()
    secretaria = re.sub(r'Assessora?', r'Assessoria', secretaria)
    secretaria = re.sub(r'Secret(a|á)ri(o|a)', r'Secretaria', secretaria)
    secretaria = re.sub(r'Procurador(a)?', r'Procuradoria', secretaria)
    secretaria = re.sub(r'Coordenador(a)?', r'Coordenadoria', secretaria)
    secretaria = secretaria.replace(u'Superintendente', u'Superintendência')
    secretaria = re.sub(r'Diretor((i)?a)?', r'Diretoria', secretaria)

    # Dicionário para armazenar os dados
    detalhes_editais = dict()
    try:
        # Procurar e padronizar data
        data = re.search(r'\d{2}/\d{2}/\d{4}|\d{2} de (janeiro|Janeiro|Fevereiro|fevereiro|Março|março|Abril|abril|Maio|maio|Junho|junho|julho|Julho|agosto|Agosto|setembro|Setembro|outubro|Outubro|novembro|Novembro|dezembro|Dezembro) de \d{4}', dados).group()
        data = padronizar_data(data)
        data = datetime.datetime.strptime(str(data), '%d/%m/%Y').date()
        detalhes_editais['data'] = data
    except:
        detalhes_editais['data'] = None
    detalhes_editais['edital'] = edital
    detalhes_editais['secretaria'] = secretaria

    return detalhes_editais

#---------------------------------------------------------------------------------------------------------
# Funções acopladas à função princípal

def padronizar_data(dado_data):
    # Função que padroniza a data
    dado_data = dado_data.replace(u' de ', u'/')
    dado_data = dado_data.replace(u'janeiro', u'01')
    dado_data = dado_data.replace(u'Janeiro', u'01')
    dado_data = dado_data.replace(u'fevereiro', u'02')
    dado_data = dado_data.replace(u'Fevereiro', u'02')
    dado_data = dado_data.replace(u'março', u'03')
    dado_data = dado_data.replace(u'Março', u'03')
    dado_data = dado_data.replace(u'abril', u'04')
    dado_data = dado_data.replace(u'Abril', u'04')
    dado_data = dado_data.replace(u'maio', u'05')
    dado_data = dado_data.replace(u'Maio', u'05')
    dado_data = dado_data.replace(u'junho', u'06')
    dado_data = dado_data.replace(u'Junho', u'06')
    dado_data = dado_data.replace(u'julho', u'07')
    dado_data = dado_data.replace(u'Julho', u'07')
    dado_data = dado_data.replace(u'agosto', u'08')
    dado_data = dado_data.replace(u'Agosto', u'08')
    dado_data = dado_data.replace(u'setembro', u'09')
    dado_data = dado_data.replace(u'Setembro', u'09')
    dado_data = dado_data.replace(u'outubro', u'10')
    dado_data = dado_data.replace(u'Outubro', u'10')
    dado_data = dado_data.replace(u'novembro', u'11')
    dado_data = dado_data.replace(u'Novembro', u'11')
    dado_data = dado_data.replace(u'dezembro', u'12')
    dado_data = dado_data.replace(u'Dezembro', u'12')

    return dado_data

def padronizar_edital(texto, numeracao, edital):
    # Função que padroniza a numeração
    texto = texto.upper() + ' '
    edital = edital.upper()

    if texto in edital:
        if numeracao not in edital:
            edital = edital.replace(texto, numeracao)
        elif numeracao in edital:
            edital = edital.replace(texto, u'')

    return edital
