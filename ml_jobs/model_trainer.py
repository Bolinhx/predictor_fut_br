# ml_jobs/model_trainer.py
import pandas as pd
import joblib
import sys
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(features_path, model_output_path):
    """
    Carrega a tabela de features, treina o modelo de ML e salva o artefato do modelo.
    """
    print("--- Iniciando o Job de Treinamento do Modelo ---")
    
    # 1. CARREGAR DADOS PROCESSADOS
    print(f"Carregando tabela de features de: {features_path}")
    df_model = pd.read_parquet(features_path)
    print(f"Features carregadas. Dimensões: {df_model.shape}")

    # 2. SEPARAR FEATURES (X) E ALVO (y)
    X = df_model.drop('target', axis=1)
    y = df_model['target']

    # 3. DIVIDIR DADOS EM TREINO E TESTE
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Dados divididos. Treino: {X_train.shape[0]} amostras, Teste: {X_test.shape[0]} amostras.")

    # 4. TREINAR E AVALIAR MODELO BASELINE (Regressão Logística)
    print("\\n--- Treinando Modelo Baseline (Regressão Logística) ---")
    log_reg = LogisticRegression(max_iter=1000) 
    log_reg.fit(X_train, y_train)
    predictions_log_reg = log_reg.predict(X_test)
    accuracy_log_reg = accuracy_score(y_test, predictions_log_reg)
    print(f"Acurácia da Regressão Logística: {accuracy_log_reg:.4f}")

    # 5. TREINAR E AVALIAR MODELO AVANÇADO (XGBoost)
    print("\\n--- Treinando Modelo Avançado (XGBoost) ---")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    xgb_model.fit(X_train, y_train)
    predictions_xgb = xgb_model.predict(X_test)
    accuracy_xgb = accuracy_score(y_test, predictions_xgb)
    print(f"Acurácia do XGBoost: {accuracy_xgb:.4f}")

    # 6. SALVAR O MODELO FINAL
    print(f"\\nSalvando o modelo XGBoost treinado em: {model_output_path}")
    joblib.dump(xgb_model, model_output_path)
    print("Modelo salvo com sucesso!")
    print("--- Job de Treinamento do Modelo Concluído ---")


if __name__ == "__main__":
    # Ex: python model_trainer.py <caminho_features> <caminho_saida_modelo>
    if len(sys.argv) != 3:
        print("Uso: python model_trainer.py <features_input_path> <model_output_path>")
        sys.exit(1)
        
    features_path = sys.argv[1]
    model_output_path = sys.argv[2]
    
    train_model(features_path, model_output_path)