# Importando as bibliotecas necessárias
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import boto3
import os
import tempfile
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# --- LÓGICA DE CARREGAMENTO DO MODELO DO S3 (BLOCO ATUALIZADO) ---

# Ler as configurações a partir das variáveis de ambiente
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
MODEL_FILE_KEY = "models/modelo_final.joblib"

temp_dir = tempfile.gettempdir()
LOCAL_MODEL_PATH = os.path.join(temp_dir, "modelo_final.joblib")

print("Iniciando a API... Baixando o modelo mais recente do S3...")

# Validação para garantir que a variável de ambiente foi configurada
if not BUCKET_NAME:
    print("ERRO CRÍTICO: A variável de ambiente S3_BUCKET_NAME não está configurada.")
    model = None
else:
    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(BUCKET_NAME, MODEL_FILE_KEY, LOCAL_MODEL_PATH)
        print(f"Modelo baixado com sucesso de s3://{BUCKET_NAME}/{MODEL_FILE_KEY}")

        model = joblib.load(LOCAL_MODEL_PATH)
        print("Modelo carregado com sucesso. API pronta para receber requisições.")

    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o modelo. {e}")
        model = None

# --- FIM DO BLOCO ATUALIZADO ---


# Criar a instância da aplicação FastAPI
app = FastAPI(title="Futebol BR Predictor API", description="API para prever resultados de jogos do Brasileirão")


# Definir o formato dos dados de entrada usando Pydantic
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

# Criar o endpoint de previsão
@app.post("/predict", tags=["Predictions"])
def predict(features: MatchFeatures):
    if model is None:
        return {"error": "Modelo não está carregado. Verifique os logs da API ou o arquivo .env."}
        
    input_df = pd.DataFrame([features.dict()])
    prediction_numeric = model.predict(input_df)[0]
    resultado_map = {0: "Vitória do Mandante", 1: "Empate", 2: "Vitória do Visitante"}
    prediction_text = resultado_map.get(int(prediction_numeric), "Resultado Desconhecido")
    return {
        "prediction_numeric": int(prediction_numeric),
        "prediction_text": prediction_text
    }

# Endpoint de health check para verificar se a API está online
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API está online e funcionando!"}