from googleapiclient.discovery import build
from google.oauth2 import service_account
import os.path
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)  # Pega as variáveis de ambiente

SAMPLE_SPREADSHEET_ID = os.getenv("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = os.getenv("SAMPLE_RANGE_NAME")
ID_GRUPO = os.getenv("ID_GRUPO")
FOLDER_PATH = os.getenv("FOLDER_PATH")
credenciais_arquivo = FOLDER_PATH + "credentials.json"  # Substitua pelo caminho para o arquivo JSON de credenciais

def get_emails_from_api():
    credentials = service_account.Credentials.from_service_account_file(credenciais_arquivo, scopes=['https://www.googleapis.com/auth/spreadsheets'])

    service = build('sheets', 'v4', credentials=credentials)

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME+ 'B:B').execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return []

        emails = [row[0] for row in values if (row != [])]
        if emails != []:
            print("Emails resgatados!")
        
        request = service.spreadsheets().values().clear(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME + 'A:B',
            body={}
        )

        response = request.execute()

        print("Itens apagados com sucesso.")

        return emails

    except Exception as e:
        print('Erro:', str(e))
        return []

# Define as informações do grupo
    
def add_emails_to_group(email_list, group_email):    
    if os.path.exists(credenciais_arquivo):
        credentials = service_account.Credentials.from_service_account_file(credenciais_arquivo, scopes=["https://www.googleapis.com/auth/admin.directory.group"])
    else:
        print("Arquivo de credenciais não encontrado.")
        exit()

    # Cria uma instância da API de Administração do Google Workspace
    service = build('admin', 'directory_v1', credentials=credentials)

    for email in email_list:
        member_body = {
            'email': email,
            'role': 'MEMBER'  # Defina o papel do membro conforme necessário
        }
        request = service.members().insert(groupKey=group_email, body=member_body)
        response = request.execute()

        # Verifica se o membro foi adicionado com sucesso
        if 'email' in response:
            print('Membro adicionado com sucesso:', response['email'])
        else:
            print('Erro ao adicionar membro:', response)

add_emails_to_group(['lmtorres2012@hotmail.com'], 'anesedt@googlegroups.com')