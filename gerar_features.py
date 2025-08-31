# Arquivo: gerar_features.py (Versão 2.0 - Robusta)

import pandas as pd
import numpy as np
import json
import argparse
import sys
import warnings

# Ignorar avisos futuros do pandas para uma saída mais limpa
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Funções de Ajuda ---

def extrair_partes_formacao(formacao):
    if pd.isna(formacao) or '-' not in str(formacao):
        return [3, 4, 3]
    parts = str(formacao).split('-')
    try:
        if len(parts) == 3:
            return [int(p) for p in parts]
        elif len(parts) == 4:
            return [int(parts[0]), sum(int(p) for p in parts[1:-1]), int(parts[-1])]
        else:
            return [3, 4, 3]
    except (ValueError, TypeError):
        return [3, 4, 3]

# --- Função Principal de Geração ---

def gerar_features_para_jogo(mandante, visitante, df_historico):
    print(f"\nGerando features para o confronto: {mandante} (Mandante) vs. {visitante} (Visitante)")
    features = {}

    for time_nome, tipo in [(mandante, 'mandante'), (visitante, 'visitante')]:
        ultimos_jogos = df_historico[
            (df_historico['mandante'] == time_nome) | (df_historico['visitante'] == time_nome)
        ].tail(5)

        if ultimos_jogos.empty:
            print(f"ERRO FATAL: Não foram encontrados dados históricos para o time '{time_nome}'.", file=sys.stderr)
            sys.exit(1)
        elif len(ultimos_jogos) < 5:
            print(f"Aviso: '{time_nome}' tem apenas {len(ultimos_jogos)} jogos históricos. A 'forma' pode ser menos precisa.")

        pontos = np.where(ultimos_jogos['mandante'] == time_nome, ultimos_jogos['pontos_mandante'], ultimos_jogos['pontos_visitante']).mean()
        gols_feitos = np.where(ultimos_jogos['mandante'] == time_nome, ultimos_jogos['mandante_placar'], ultimos_jogos['visitante_placar']).mean()
        gols_sofridos = np.where(ultimos_jogos['mandante'] == time_nome, ultimos_jogos['visitante_placar'], ultimos_jogos['mandante_placar']).mean()

        features[f'form_pontos_{tipo}'] = round(pontos, 4)
        features[f'form_gols_feitos_{tipo}'] = round(gols_feitos, 4)
        features[f'form_gols_sofridos_{tipo}'] = round(gols_sofridos, 4)

    ultimo_jogo_mandante = df_historico[df_historico['mandante'] == mandante].iloc[-1]
    ultimo_jogo_visitante = df_historico[df_historico['visitante'] == visitante].iloc[-1]

    features['eh_classico'] = 1 if ultimo_jogo_mandante['mandante_estado'] == ultimo_jogo_visitante['visitante_estado'] else 0
    
    formacao_mandante = extrair_partes_formacao(ultimo_jogo_mandante['formacao_mandante'])
    formacao_visitante = extrair_partes_formacao(ultimo_jogo_visitante['formacao_visitante'])

    features['mandante_def'], features['mandante_mid'], features['mandante_att'] = formacao_mandante
    features['visitante_def'], features['visitante_mid'], features['visitante_att'] = formacao_visitante
    features['diff_def'] = formacao_mandante[0] - formacao_visitante[0]
    features['diff_mid'] = formacao_mandante[1] - formacao_visitante[1]
    features['diff_att'] = formacao_mandante[2] - formacao_visitante[2]

    return features

# --- Função de Validação e Execução ---

def main():
    parser = argparse.ArgumentParser(description="Gera o JSON de features para um confronto do Brasileirão.")
    parser.add_argument("mandante", type=str, help="Nome do time mandante.")
    parser.add_argument("visitante", type=str, help="Nome do time visitante.")
    args = parser.parse_args()

    try:
        df = pd.read_csv('data/raw/campeonato-brasileiro-full.csv')
        df.columns = df.columns.str.lower()
    except FileNotFoundError:
        print("ERRO: Arquivo 'data/raw/campeonato-brasileiro-full.csv' não encontrado.", file=sys.stderr)
        sys.exit(1)

    # Criar uma lista de times únicos para validação
    times_validos = pd.concat([df['mandante'], df['visitante']]).unique()
    times_validos_lower = {time.lower(): time for time in times_validos}

    # Validar time mandante
    mandante_lower = args.mandante.lower()
    if mandante_lower not in times_validos_lower:
        print(f"ERRO: Time mandante '{args.mandante}' não encontrado.", file=sys.stderr)
        print(f"Exemplos de times válidos: {', '.join(times_validos[:5])}", file=sys.stderr)
        sys.exit(1)
    
    # Validar time visitante
    visitante_lower = args.visitante.lower()
    if visitante_lower not in times_validos_lower:
        print(f"ERRO: Time visitante '{args.visitante}' não encontrado.", file=sys.stderr)
        print(f"Exemplos de times válidos: {', '.join(times_validos[:5])}", file=sys.stderr)
        sys.exit(1)

    # Obter os nomes corretos (com maiúsculas/minúsculas)
    mandante_correto = times_validos_lower[mandante_lower]
    visitante_correto = times_validos_lower[visitante_lower]
        
    # Preparar o restante do dataframe histórico
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df = df[df['data'].dt.year >= 2014].copy()
    df.sort_values(by='data', inplace=True)
    df['vencedor'] = df['vencedor'].astype(str)
    df['target'] = np.where(df['vencedor'] == df['mandante'], 0, np.where(df['vencedor'] == '-', 1, 2))
    df['pontos_mandante'] = np.where(df['target'] == 0, 3, np.where(df['target'] == 1, 1, 0))
    df['pontos_visitante'] = np.where(df['target'] == 2, 3, np.where(df['target'] == 1, 1, 0))

    features_jogo = gerar_features_para_jogo(mandante_correto, visitante_correto, df)

    print("\nJSON de features gerado com sucesso:")
    print(json.dumps(features_jogo, indent=4))

if __name__ == "__main__":
    main()