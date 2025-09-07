import pandas as pd
import numpy as np
import sys

def process_data(input_path_hist, input_path_new, output_path_features):
    """
    Função completa para carregar, limpar, combinar e "engenheirar" features.
    Lê dados históricos e novos, aplica todas as transformações do notebook
    e salva um arquivo parquet final pronto para o treinamento.
    """
    print("--- Iniciando o Job de Processamento de Dados ---")

    # 1. CARGA E COMBINAÇÃO DOS DADOS
    print(f"Carregando dados históricos de: {input_path_hist}")
    df_hist = pd.read_csv(input_path_hist)
    print(f"Carregando novos dados de: {input_path_new}")
    df_new = pd.read_csv(input_path_new)
    df = pd.concat([df_hist, df_new], ignore_index=True)
    print(f"Dados combinados. Total de {len(df)} linhas.")

    # 2. LIMPEZA E FILTRO INICIAL (Lógica do Notebook)
    print("Aplicando limpeza e filtros iniciais...")
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df = df[df['data'].dt.year >= 2014].copy()
    df.sort_values(by='data', inplace=True)
    
    # PADRONIZAÇÃO DE NOMES DAS COLUNAS (Lógica do Notebook)
    df.columns = df.columns.str.lower()
    # A coluna 'rodata' parece ser um typo de 'rodada', vamos padronizar
    if 'rodata' in df.columns:
        df.rename(columns={'rodata': 'rodada'}, inplace=True)

    # 3. CRIAÇÃO DA VARIÁVEL ALVO (target) (Lógica do Notebook)
    print("Criando a variável alvo 'target'...")
    def criar_target(row):
        if row['vencedor'] == row['mandante']:
            return 0  # Vitória do Mandante
        elif row['vencedor'] == '-':
            return 1  # Empate
        else:
            return 2  # Vitória do Visitante
    df['target'] = df.apply(criar_target, axis=1)

    # 4. ENGENHARIA DE "FORMA" (Lógica do Notebook)
    print("Iniciando engenharia de features de 'Forma'...")
    df['pontos_mandante'] = np.where(df['target'] == 0, 3, np.where(df['target'] == 1, 1, 0))
    df['pontos_visitante'] = np.where(df['target'] == 2, 3, np.where(df['target'] == 1, 1, 0))
    
    df_unpivot = df.reset_index()
    
    df_team_stats = pd.concat([
        df_unpivot.rename(columns={'mandante': 'time', 'visitante': 'oponente', 'mandante_placar': 'gols_feitos', 'visitante_placar': 'gols_sofridos', 'pontos_mandante': 'pontos'}),
        df_unpivot.rename(columns={'visitante': 'time', 'mandante': 'oponente', 'visitante_placar': 'gols_feitos', 'mandante_placar': 'gols_sofridos', 'pontos_visitante': 'pontos'})
    ]).sort_values(by=['time', 'data'])

    stats_to_roll = ['gols_feitos', 'gols_sofridos', 'pontos']
    rolling_stats = df_team_stats.groupby('time')[stats_to_roll].rolling(window=5, min_periods=1).mean().shift(1)
    rolling_stats.rename(columns=lambda x: f'form_{x}', inplace=True)

    df_team_stats.reset_index(drop=True, inplace=True)
    df_form = pd.concat([df_team_stats[['index', 'time']], rolling_stats.reset_index(drop=True)], axis=1)

    df_final = df_unpivot.merge(df_form, left_on=['index', 'mandante'], right_on=['index', 'time'], suffixes=('', '_mandante'))
    df_final = df_final.merge(df_form, left_on=['index', 'visitante'], right_on=['index', 'time'], suffixes=('_mandante', '_visitante'))
    df_final.drop(columns=['time_mandante', 'time_visitante'], inplace=True)
    print("Engenharia de 'Forma' concluída.")

    # 5. ENGENHARIA DE "CONTEXTO" (Lógica do Notebook)
    print("Iniciando engenharia de features de 'Contexto'...")
    df_final['eh_classico'] = (df_final['mandante_estado'] == df_final['visitante_estado']).astype(int)

    def extrair_partes_formacao(formacao):
        if pd.isna(formacao) or '-' not in str(formacao): return [4, 4, 2]
        parts = str(formacao).split('-')
        try:
            if len(parts) == 3: return [int(p) for p in parts]
            if len(parts) == 4: return [int(parts[0]), sum(int(p) for p in parts[1:-1]), int(parts[-1])]
            return [4, 4, 2]
        except (ValueError, TypeError):
            return [4, 4, 2]

    formacoes_mandante = df_final['formacao_mandante'].apply(extrair_partes_formacao)
    formacoes_visitante = df_final['formacao_visitante'].apply(extrair_partes_formacao)

    df_final[['mandante_def', 'mandante_mid', 'mandante_att']] = pd.DataFrame(formacoes_mandante.tolist(), index=df_final.index)
    df_final[['visitante_def', 'visitante_mid', 'visitante_att']] = pd.DataFrame(formacoes_visitante.tolist(), index=df_final.index)

    df_final['diff_def'] = df_final['mandante_def'] - df_final['visitante_def']
    df_final['diff_mid'] = df_final['mandante_mid'] - df_final['visitante_mid']
    df_final['diff_att'] = df_final['mandante_att'] - df_final['visitante_att']
    print("Engenharia de 'Contexto' concluída.")
    
    # 6. PREPARAR DATAFRAME FINAL (Lógica do Notebook)
    print("Preparando e salvando o dataframe final...")
    feature_cols = [
        'form_gols_feitos_mandante', 'form_gols_sofridos_mandante', 'form_pontos_mandante',
        'form_gols_feitos_visitante', 'form_gols_sofridos_visitante', 'form_pontos_visitante',
        'eh_classico',
        'mandante_def', 'mandante_mid', 'mandante_att',
        'visitante_def', 'visitante_mid', 'visitante_att',
        'diff_def', 'diff_mid', 'diff_att'
    ]
    target_col = 'target'
    
    df_model = df_final[feature_cols + [target_col]].copy()
    df_model.dropna(inplace=True)

    # SALVAR EM FORMATO PARQUET
    df_model.to_parquet(output_path_features, index=False)
    print(f"Tabela de features salva com sucesso em: {output_path_features}")
    print(f"Dimensões do output: {df_model.shape}")
    print("--- Job de Processamento de Dados Concluído ---")

if __name__ == "__main__":
    # Este bloco permite que o script seja executado via linha de comando
    # Ex: python data_processor.py <caminho_dados_hist> <caminho_dados_novos> <caminho_saida>
    if len(sys.argv) != 4:
        print("Uso: python data_processor.py <input_hist> <input_new> <output>")
        sys.exit(1)
    
    input_path_hist = sys.argv[1]
    input_path_new = sys.argv[2]
    output_path_features = sys.argv[3]
    
    process_data(input_path_hist, input_path_new, output_path_features)