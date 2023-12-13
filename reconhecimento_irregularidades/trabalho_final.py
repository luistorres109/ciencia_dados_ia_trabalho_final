# AVISO LEGAL!!!
# Isto se trata de um trabalho acadêmico e não está sendo feita nenhuma acusação de fato se há alguma ilegalidade ou não nas licitações
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import dotenv
import os

# Avaliar os modelos
def evaluate_model(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return mae, mse, r2

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

# Criado DF com as colunas codificadas
df_features_encoded = pd.DataFrame(df_encoded, columns=encoded_columns)

# Dividir os dados em treino, validação e teste (70-10-20)
X_train, X_temp, y_train, y_temp = train_test_split(df_features_encoded, df_target, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.66, random_state=42)

# Inicializar o modelo Random Forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Treinar o modelo
rf_model.fit(X_train, y_train)

# Fazer previsões em partes do conjunto de dados
y_val_pred = rf_model.predict(X_val)
y_test_pred = rf_model.predict(X_test)

# Avaliar modelo
test_rf_metrics_test = evaluate_model(y_test, y_test_pred)
val_rf_metrics_val = evaluate_model(y_val, y_val_pred)

print("\nTeste - Random Forest:")
print("- MAE (Mean Absolute Error):", test_rf_metrics_test[0])
print("- MSE (Mean Squared Error):", test_rf_metrics_test[1])
print("- R2 Score:", test_rf_metrics_test[2])

print("\nValidação - Random Forest:")
print("- MAE (Mean Absolute Error):", val_rf_metrics_val[0])
print("- MSE (Mean Squared Error):", val_rf_metrics_val[1])
print("- R2 Score:", val_rf_metrics_val[2])

# Fazer previsões em todo o conjunto de dados
df['Montante_Pred'] = rf_model.predict(df_features_encoded)

# Calcular a diferença entre os valores reais e previstos
df['Desvio'] = (df['Montante'] - df['Montante_Pred']) / df['Montante']

# Definição de um limiar para identificar desvios significativos
limiar_desvio = 0.25

# Filtrar licitações com desvios significativos
df = df[abs(df['Desvio']) > limiar_desvio].drop(['Data', 'Horario', 'Local', 'Modalidade', 'Forma julgamento', 'Unidade gestora', 'Secretária', 'Objeto', 'Tipo', 'Link da Página'], axis=1)
df = df.loc[df['Desvio'] >= 0]

# Visualizar as licitações irregulares
print("Dataframe com os editais (SUPOSTAMENTE) irregulares:")
print(df)
print(f"\nO numero total dessas licitacoes eh: {df[df.columns[0]].count()}")