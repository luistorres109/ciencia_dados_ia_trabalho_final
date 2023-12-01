# AVISO LEGAL!!!
# Isto se trata de um trabalho acadêmico e não está sendo feita nenhuma acusação de fato se há alguma ilegalidade ou não nas licitações
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)  # Pega as variáveis de ambiente
FOLDER_PATH = os.getenv("FOLDER_PATH")

# Ler os dados
df = pd.read_csv(FOLDER_PATH + 'editais_dados.csv', delimiter=';')

# Substituir vírgulas por pontos e converter a coluna "Montante" para valores float
df['Montante'] = df['Montante'].replace('\.', '', regex=True)
df['Montante'] = df['Montante'].str.replace(',', '.').astype(float)

# Separar as características (features) e o alvo (target)
df_features = df.drop(["Montante", "Link da Página", "Horario", "Local"], axis=1)
df_target = df['Montante']

# Separar variáveis categóricas
categorical_cols = ['Data', 'Edital', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Tipo']  # Substitua com suas colunas categóricas

# Inicializar o codificador de categorias
encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)

# Ajustar e transformar as variáveis categóricas
df_encoded = encoder.fit_transform(df_features[categorical_cols])

# Obter os nomes das colunas codificadas
encoded_columns = [f"{col}_{val}" for col, values in zip(categorical_cols, encoder.categories_) for val in values]

# Adicionar as colunas codificadas ao conjunto de dados
df_features_encoded = pd.concat([df_features.drop(categorical_cols, axis=1), pd.DataFrame(df_encoded, columns=encoded_columns)], axis=1)

# Inicializar o modelo Random Forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Treinar o modelo
rf_model.fit(df_features_encoded, df_target)

# Fazer previsões em todo o conjunto de dados
df['Montante_Pred'] = rf_model.predict(df_features_encoded)

# Calcular a diferença entre os valores reais e previstos
df['Desvio'] = df['Montante'] - df['Montante_Pred']

# Definição de um limiar para identificar desvios significativos
limiar_desvio = 1000000

# Filtrar licitações com desvios significativos
df = df[abs(df['Desvio']) > limiar_desvio].drop(['Data', 'Horario', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Tipo', 'Link da Página'], axis=1)
df = df.loc[df['Desvio'] >= 0]

# Visualizar as licitações irregulares
print("Dataframe com os editais (SUPOSTAMENTE) irregulares:")
print(df)
print(f"\nO numero total dessas licitacoes eh: {df[df.columns[0]].count()}")