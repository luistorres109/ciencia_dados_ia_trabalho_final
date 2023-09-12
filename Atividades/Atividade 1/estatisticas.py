import matplotlib.pyplot as plt
import pandas as pd
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv('.env'), override=True)  # Pega as variáveis de ambiente

FOLDER_PATH = os.getenv("FOLDER_PATH")

df = pd.read_csv(FOLDER_PATH + 'editais_dados.csv', delimiter=';').reset_index(drop=True)

# Substituir vírgulas por pontos e converter a coluna "Montante" para valores float
df['Montante'] = df['Montante'].str.replace('.', '')
df['Montante'] = df['Montante'].str.replace(',', '.').astype(float)

# Estatísticas descritivas para a coluna "Montante"
estatisticas_descritivas = df['Montante'].describe()

# Exibe as estatísticas descritivas
print(estatisticas_descritivas)

df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')

# Histograma
plt.figure(figsize=(10, 6))
plt.hist(df['Montante'], bins=20, color='skyblue', edgecolor='black')
plt.title('Histograma de Montante')
plt.xlabel('Montante')
plt.ylabel('Frequência')
plt.show()

# Gráfico de Dispersão com a coluna de Datas
plt.figure(figsize=(10, 6))
plt.scatter(df['Data'], df['Montante'], alpha=0.5)
plt.title('Gráfico de Dispersão de Montante por Data')
plt.xlabel('Data')
plt.ylabel('Montante')
plt.xticks(rotation=45)
plt.show()

# Box Plot
plt.figure(figsize=(10, 6))
plt.boxplot(df['Montante'], vert=False)
plt.title('Box Plot de Montante')
plt.xlabel('Montante')
plt.show()

# Análise Temporal
df['Data'] = pd.to_datetime(df['Data'])
df.set_index('Data', inplace=True)
df.resample('M')['Montante'].sum().plot(figsize=(10, 6))
plt.title('Soma Mensal de Montante ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('Soma de Montante')
plt.show()
