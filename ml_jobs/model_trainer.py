# ml_jobs/model_trainer.py
import pandas as pd
import joblib
import sys
import boto3
from urllib.parse import urlparse
import tempfile 
import os       
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(features_path, model_output_path):
    """
    Carrega a tabela de features, treina o modelo de ML e salva o artefato do modelo no S3.
    """
    print("--- Iniciando o Job de Treinamento do Modelo ---")

    # ... (a lógica de carregar e treinar continua exatamente a mesma)
    print(f"Carregando features de: {features_path}")
    df_model = pd.read_parquet(features_path)
    print(f"Features carregadas. Dimensões: {df_model.shape}")

    X = df_model.drop('target', axis=1)
    y = df_model['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Dados divididos. Treino: {X_train.shape[0]} amostras, Teste: {X_test.shape[0]} amostras.")

    print("\\n--- Treinando Modelo Baseline (Regressão Logística) ---")
    log_reg = LogisticRegression(max_iter=1000)
    log_reg.fit(X_train, y_train)
    predictions_log_reg = log_reg.predict(X_test)
    accuracy_log_reg = accuracy_score(y_test, predictions_log_reg)
    print(f"Acurácia da Regressão Logística: {accuracy_log_reg:.4f}")

    print("\\n--- Treinando Modelo Avançado (XGBoost) ---")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    xgb_model.fit(X_train, y_train)
    predictions_xgb = xgb_model.predict(X_test)
    accuracy_xgb = accuracy_score(y_test, predictions_xgb)
    print(f"Acurácia do XGBoost: {accuracy_xgb:.4f}")

    # --- LÓGICA DE SALVAMENTO CORRIGIDA E UNIVERSAL ---
    print(f"\\nIniciando o processo de salvamento do modelo em: {model_output_path}")

    # 3. Criar um caminho de arquivo temporário que funciona em qualquer sistema operacional
    temp_dir = tempfile.gettempdir()
    local_temp_path = os.path.join(temp_dir, "modelo_final.joblib")
    
    print(f"Salvando modelo temporariamente em: {local_temp_path}")
    joblib.dump(xgb_model, local_temp_path)

        # 4. Fazer upload do arquivo salvo para o S3
    print("Iniciando upload para o S3...")
    s3_client = boto3.client('s3')

    parsed_s3_path = urlparse(model_output_path, allow_fragments=False)
    bucket_name = parsed_s3_path.netloc
    object_key = parsed_s3_path.path.lstrip('/')
    
    s3_client.upload_file(local_temp_path, bucket_name, object_key)
    
    print("Upload para o S3 concluído com sucesso!")
    print("--- Job de Treinamento do Modelo Concluído ---")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python model_trainer.py <features_input_path> <model_output_path>")
        sys.exit(1)
        
    features_path = sys.argv[1]
    model_output_path = sys.argv[2]
    
    train_model(features_path, model_output_path)