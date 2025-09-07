import pandas as pd

# --- CONFIGURAÇÕES ---
# Certifique-se de que o caminho para o seu arquivo CSV principal está correto
ARQUIVO_ORIGINAL_PATH = 'data/raw/campeonato-brasileiro-full.csv'
# Intervalo de datas para separar como "novos dados"
DATA_INICIO_NOVOS_DADOS = '2024-11-01'
DATA_FIM_NOVOS_DADOS = '2024-12-08'

# --- LÓGICA ---
print("Carregando o dataset original...")
try:
    df = pd.read_csv(ARQUIVO_ORIGINAL_PATH)
except FileNotFoundError:
    print(f"ERRO: O arquivo '{ARQUIVO_ORIGINAL_PATH}' não foi encontrado. Verifique o caminho.")
    exit()

# Converter a coluna 'data' para o formato de data, essencial para a filtragem
# O formato '%d/%m/%Y' é comum em dados do Brasil. Se der erro, pode ser outro formato.
print("Convertendo a coluna 'data' para o formato de data...")
try:
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
except Exception as e:
    print(f"ERRO ao converter a coluna 'data'. Verifique o formato das datas no CSV. Erro: {e}")
    exit()

# Definir as datas de corte como objetos de data
start_date = pd.to_datetime(DATA_INICIO_NOVOS_DADOS)
end_date = pd.to_datetime(DATA_FIM_NOVOS_DADOS)

print(f"Separando os dados no intervalo de {DATA_INICIO_NOVOS_DADOS} a {DATA_FIM_NOVOS_DADOS}...")

# Criar a máscara para identificar as "novas rodadas"
mask_novas_rodadas = (df['data'] >= start_date) & (df['data'] <= end_date)

# Separar os dataframes
# Dados de produção são todos ANTES da data de início dos novos dados
df_producao_inicial = df[df['data'] < start_date]
# Dados novos são os que estão DENTRO do intervalo
df_novas_rodadas = df[mask_novas_rodadas]

# Salvar os novos arquivos
PATH_PRODUCAO_INICIAL = 'data/dados_producao_inicial.csv'
PATH_NOVAS_RODADAS = 'data/novas_rodadas_simuladas.csv'

# Para salvar o CSV com a data no formato original, podemos reformatar a coluna
df_producao_inicial['data'] = df_producao_inicial['data'].dt.strftime('%d/%m/%Y')
df_novas_rodadas['data'] = df_novas_rodadas['data'].dt.strftime('%d/%m/%Y')

df_producao_inicial.to_csv(PATH_PRODUCAO_INICIAL, index=False)
df_novas_rodadas.to_csv(PATH_NOVAS_RODADAS, index=False)

print("-" * 30)
print("Dados de simulação preparados com sucesso!")
print(f"Dados iniciais (até {DATA_INICIO_NOVOS_DADOS}) salvos em: {PATH_PRODUCAO_INICIAL} ({len(df_producao_inicial)} linhas)")
print(f"Dados novos ({DATA_INICIO_NOVOS_DADOS} a {DATA_FIM_NOVOS_DADOS}) salvos em: {PATH_NOVAS_RODADAS} ({len(df_novas_rodadas)} linhas)")