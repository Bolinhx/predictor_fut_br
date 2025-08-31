# Importando as bibliotecas necessárias
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# 1. Criar a instância da aplicação FastAPI
app = FastAPI(title="Futebol BR Predictor API", description="API para prever resultados de jogos do Brasileirão")

# 2. Carregar o nosso modelo treinado
model = joblib.load('models/fut_br_predictor_model.joblib')
print("Modelo carregado com sucesso.")

# 3. Definir o formato dos dados de entrada usando Pydantic
# As features aqui devem ser EXATAMENTE as mesmas que usamos para treinar o modelo
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