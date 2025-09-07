# Importando as bibliotecas necessárias
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import boto3
import os
import tempfile # Importa a biblioteca de arquivos temporários

# --- LÓGICA DE CARREGAMENTO DO MODELO DO S3 (BLOCO ATUALIZADO E UNIVERSAL) ---

# Define os detalhes do nosso modelo no S3.
BUCKET_NAME = "predictor-fut-br-data-bolinhx-2025"
MODEL_FILE_KEY = "models/modelo_final.joblib" # O caminho para o modelo no S3

# Cria um caminho de arquivo temporário que funciona em qualquer sistema operacional
temp_dir = tempfile.gettempdir()
LOCAL_MODEL_PATH = os.path.join(temp_dir, "modelo_final.joblib")

print("Iniciando a API... Baixando o modelo mais recente do S3...")

try:
    # Baixa o modelo do S3 para o caminho temporário correto
    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET_NAME, MODEL_FILE_KEY, LOCAL_MODEL_PATH)
    print(f"Modelo baixado com sucesso em: {LOCAL_MODEL_PATH}")

    # Carrega o modelo que acabamos de baixar
    model = joblib.load(LOCAL_MODEL_PATH)
    print("Modelo carregado com sucesso. API pronta para receber requisições.")

except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo. {e}")
    model = None

# --- FIM DO BLOCO ATUALIZADO ---


# 1. Criar a instância da aplicação FastAPI
app = FastAPI(title="Futebol BR Predictor API", description="API para prever resultados de jogos do Brasileirão")


# 3. Definir o formato dos dados de entrada usando Pydantic
class MatchFeatures(BaseModel):
    form_gols_feitos_mandante: float
    form_gols_sofridos_mandante: float
    form_pontos_mandante: float
    form_gols_feitos_visitante: float
    form_gols_sofridos_visitante: float
    form_pontos_visitante: float
    eh_classico: int
    mandante_def: int
    mandante_mid: int
    mandante_att: int
    visitante_def: int
    visitante_mid: int
    visitante_att: int
    diff_def: int
    diff_mid: int
    diff_att: int

# 4. Criar o endpoint de previsão
@app.post("/predict", tags=["Predictions"])
def predict(features: MatchFeatures):
    """
    Recebe as features de uma partida e retorna a previsão do resultado.
    - **0**: Vitória do Mandante
    - **1**: Empate
    - **2**: Vitória do Visitante
    """
    if model is None:
        return {"error": "Modelo não está carregado. Verifique os logs da API."}
        
    # Converter os dados de entrada em um DataFrame do Pandas
    input_df = pd.DataFrame([features.dict()])

    # Fazer a previsão com o modelo carregado
    prediction_numeric = model.predict(input_df)[0]

    # Mapear o resultado numérico para um texto mais claro
    resultado_map = {0: "Vitória do Mandante", 1: "Empate", 2: "Vitória do Visitante"}
    prediction_text = resultado_map.get(int(prediction_numeric), "Resultado Desconhecido")

    # Retornar a previsão em formato JSON
    return {
        "prediction_numeric": int(prediction_numeric),
        "prediction_text": prediction_text
    }

# Endpoint de health check para verificar se a API está online
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API está online e funcionando!"}

