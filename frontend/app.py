import streamlit as st
import pandas as pd
import numpy as np
import requests
import boto3
import os
from io import StringIO
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES GERAIS (LIDAS DO AMBIENTE) ---
# Ler as configurações do ambiente
NOME_DO_BUCKET_S3 = os.getenv("S3_BUCKET_NAME")
URL_DA_API_APPRUNNER = os.getenv("APP_RUNNER_SERVICE_URL")

CAMINHO_DADOS_HISTORICOS = "raw/dados_producao_inicial.csv"


# --- FUNÇÕES DE ENGENHARIA DE FEATURES (Adaptadas do data_processor.py) ---
@st.cache_data(ttl=3600)
def carregar_dados_s3():
    print("Carregando dados do S3...")
    if not NOME_DO_BUCKET_S3:
        raise ValueError("A variável de ambiente S3_BUCKET_NAME não está configurada no arquivo .env")
    
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=NOME_DO_BUCKET_S3, Key=CAMINHO_DADOS_HISTORICOS)
    df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
    
    df.columns = df.columns.str.lower()
    if 'rodata' in df.columns:
        df.rename(columns={'rodata': 'rodada'}, inplace=True)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    print("Dados carregados e pré-processados.")
    return df

def extrair_partes_formacao(formacao):
    if pd.isna(formacao) or '-' not in str(formacao):
        return [4, 4, 2]
    parts = str(formacao).split('-')
    try:
        if len(parts) == 3:
            return [int(p) for p in parts]
        if len(parts) == 4:
            return [int(parts[0]), sum(int(p) for p in parts[1:-1]), int(parts[-1])]
        return [4, 4, 2]
    except (ValueError, TypeError):
        return [4, 4, 2]

def gerar_features_para_confronto(df_historico, time_mandante, time_visitante):
    # ... (parte inicial da função continua a mesma)
    ultimos_jogos_mandante = df_historico[
        (df_historico['mandante'] == time_mandante) | (df_historico['visitante'] == time_mandante)
    ].sort_values(by='data', ascending=False).head(5)

    ultimos_jogos_visitante = df_historico[
        (df_historico['visitante'] == time_visitante) | (df_historico['mandante'] == time_visitante)
    ].sort_values(by='data', ascending=False).head(5)

    def calcular_forma(df_time, nome_time):
        gols_feitos = []
        gols_sofridos = []
        pontos = []
        for _, row in df_time.iterrows():
            if row['mandante'] == nome_time:
                gols_feitos.append(row['mandante_placar'])
                gols_sofridos.append(row['visitante_placar'])
                vencedor = row['vencedor']
                if vencedor == nome_time:
                    pontos.append(3)
                elif vencedor == '-':
                    pontos.append(1)
                else:
                    pontos.append(0)
            else: # Time era visitante
                gols_feitos.append(row['visitante_placar'])
                gols_sofridos.append(row['mandante_placar'])
                vencedor = row['vencedor']
                if vencedor == nome_time:
                    pontos.append(3)
                elif vencedor == '-':
                    pontos.append(1)
                else:
                    pontos.append(0)
        
        return np.mean(gols_feitos), np.mean(gols_sofridos), np.mean(pontos)

    form_gols_feitos_m, form_gols_sofridos_m, form_pontos_m = calcular_forma(ultimos_jogos_mandante, time_mandante)
    form_gols_feitos_v, form_gols_sofridos_v, form_pontos_v = calcular_forma(ultimos_jogos_visitante, time_visitante)

    ultimo_jogo_mandante = ultimos_jogos_mandante.iloc[0]
    ultimo_jogo_visitante = ultimos_jogos_visitante.iloc[0]

    formacao_mandante = ultimo_jogo_mandante['formacao_mandante'] if ultimo_jogo_mandante['mandante'] == time_mandante else ultimo_jogo_mandante['formacao_visitante']
    formacao_visitante = ultimo_jogo_visitante['formacao_visitante'] if ultimo_jogo_visitante['visitante'] == time_visitante else ultimo_jogo_visitante['formacao_mandante']

    m_def, m_mid, m_att = extrair_partes_formacao(formacao_mandante)
    v_def, v_mid, v_att = extrair_partes_formacao(formacao_visitante)

    estado_mandante = ultimo_jogo_mandante['mandante_estado'] if ultimo_jogo_mandante['mandante'] == time_mandante else ultimo_jogo_mandante['visitante_estado']
    estado_visitante = ultimo_jogo_visitante['visitante_estado'] if ultimo_jogo_visitante['visitante'] == time_visitante else ultimo_jogo_visitante['mandante_estado']
    eh_classico = 1 if estado_mandante == estado_visitante else 0

    payload = {
        "form_gols_feitos_mandante": form_gols_feitos_m, "form_gols_sofridos_mandante": form_gols_sofridos_m, "form_pontos_mandante": form_pontos_m,
        "form_gols_feitos_visitante": form_gols_feitos_v, "form_gols_sofridos_visitante": form_gols_sofridos_v, "form_pontos_visitante": form_pontos_v,
        "eh_classico": eh_classico, "mandante_def": m_def, "mandante_mid": m_mid, "mandante_att": m_att,
        "visitante_def": v_def, "visitante_mid": v_mid, "visitante_att": v_att,
        "diff_def": m_def - v_def, "diff_mid": m_mid - v_mid, "diff_att": m_att - v_att
    }
    return payload

# --- INTERFACE DO STREAMLIT ---

st.set_page_config(page_title="Previsor do Brasileirão", layout="wide")
st.title("🤖 Previsor de Partidas do Brasileirão")
st.markdown("Selecione os times mandante e visitante para obter a previsão de resultado com base no modelo de Machine Learning.")

try:
    df_historico_completo = carregar_dados_s3()
    lista_times = sorted(df_historico_completo['mandante'].unique())
    
    col1, col2 = st.columns(2)

    with col1:
        time_mandante = st.selectbox("Escolha o Time Mandante", lista_times, index=0)
    with col2:
        opcoes_visitante = [t for t in lista_times if t != time_mandante]
        time_visitante = st.selectbox("Escolha o Time Visitante", opcoes_visitante, index=1)

    if st.button("Analisar e Prever Resultado"):
        if not URL_DA_API_APPRUNNER:
            st.error("ERRO: A variável de ambiente APP_RUNNER_SERVICE_URL não foi configurada. Preencha o arquivo .env.")
        else:
            with st.spinner(f"Analisando o confronto: {time_mandante} vs {time_visitante}..."):
                try:
                    features_payload = gerar_features_para_confronto(df_historico_completo, time_mandante, time_visitante)
                    api_url = f"{URL_DA_API_APPRUNNER}/predict"
                    response = requests.post(api_url, json=features_payload)
                    response.raise_for_status()
                    
                    resultado = response.json()
                    
                    if 'prediction_text' in resultado:
                        st.success("Previsão gerada com sucesso!")
                        st.write(f"### O resultado mais provável é: **{resultado['prediction_text']}**")
                    else:
                        st.error("A API retornou uma resposta inesperada.")
                        st.write("Resposta recebida da API:")
                        st.json(resultado)

                    with st.expander("Ver features enviadas para o modelo"):
                        st.json(features_payload)

                except requests.exceptions.RequestException as e:
                    st.error(f"Erro ao se comunicar com a API de previsão: {e}")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado durante a geração das features: {e}")

except Exception as e:
    st.error(f"Erro fatal ao carregar os dados históricos do S3: {e}")
    st.info("Verifique se o nome do bucket S3 está correto no arquivo .env e se as credenciais da AWS estão configuradas.")