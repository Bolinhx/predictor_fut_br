# Predictor Fut BR: Análise Preditiva do Brasileirão

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)

## 📖 Descrição do Projeto

Este é um projeto completo de Machine Learning e MLOps que visa prever os resultados de partidas de futebol do Campeonato Brasileiro. O sistema vai desde a engenharia de features a partir de dados brutos até a implantação de um modelo preditivo como uma API RESTful containerizada com Docker.

O objetivo principal foi construir um produto de dados de ponta a ponta, demonstrando habilidades em Engenharia de Dados, modelagem de IA e práticas de DevOps.

## 📊 Fonte dos Dados

Os dados utilizados neste projeto foram obtidos através do Kaggle, no dataset **"Campeonato Brasileiro de Futebol"**, compilado por Ado Duque. O dataset contém informações detalhadas sobre as partidas do Brasileirão de 2003 a 2024.

* **Link para o Dataset:** [https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol](https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol)

Foram explorados múltiplos arquivos, mas o arquivo `campeonato-brasileiro-full.csv` foi selecionado como a fonte principal de verdade para o modelo final, devido à sua consistência e riqueza de informações ao longo do tempo.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Análise de Dados:** Pandas, NumPy
* **Machine Learning:** Scikit-learn, XGBoost
* **Serviço de API:** FastAPI, Uvicorn
* **Serialização do Modelo:** Joblib
* **Containerização:** Docker
  
## 💻 Ambiente de Desenvolvimento

Este projeto foi desenvolvido em um **ambiente local(Fedora - Linux)** utilizando **VS Code e Jupyter Notebooks**. A IA generativa **Gemini (Google)** foi utilizada como assistente de programação para acelerar o desenvolvimento, auxiliar na depuração de erros complexos, refatorar código para melhores práticas e para brainstorming de estratégias e arquitetura do projeto.


## 📂 Estrutura do Projeto

```
predictor_fut_br/
├── api/              # Código da aplicação FastAPI (main.py)
├── data/             # Dados brutos e processados
├── models/           # Modelo de ML treinado (.joblib)
├── notebooks/        # Notebooks para exploração e prototipagem
├── gerar_features.py # Script CLI para gerar features de um jogo
├── .dockerignore     # Arquivos a serem ignorados pelo Docker
├── .gitignore        # Arquivos a serem ignorados pelo Git
├── Dockerfile        # Receita para construir a imagem Docker da API
├── requirements.txt  # Dependências do projeto Python
└── README.md         # Documentação do projeto
```

## 🚀 Como Executar

### Pré-requisitos

* Python 3.11+
* Docker Desktop

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/bolinhx/predictor_fut_br.git
    cd predictor_fut_br
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Explore a análise (Opcional):**
    Abra e execute o Jupyter Notebook na pasta `notebooks/` para ver todo o processo de análise e treinamento do modelo.

5.  **Construa a imagem Docker:**
    ```bash
    docker build -t predictor-fut-br .
    ```

6.  **Execute o contêiner:**
    ```bash
    docker run -p 8000:80 predictor-fut-br
    ```

7.  **Teste a API:**
    Abra seu navegador e acesse `http://127.0.0.1:8000/docs` para interagir com a API e fazer previsões.

### 🔧 Usando o Gerador de Features

O projeto inclui uma ferramenta de linha de comando, `gerar_features.py`, para automatizar a criação do JSON de features para qualquer confronto.

1.  **Abra um novo terminal** na pasta raiz do projeto.
2.  **Execute o script** passando o nome do mandante e do visitante entre aspas. O script é tolerante a maiúsculas/minúsculas.

    **Exemplo:**
    ```bash
    python gerar_features.py "Palmeiras" "Corinthians"
    ```

3.  **O script irá gerar e imprimir o JSON formatado**, pronto para ser copiado e colado no corpo da requisição do endpoint `/predict` na documentação interativa da API.


## 🧭 Jornada do Projeto e Decisões Estratégicas

Este projeto é um reflexo de um ciclo de desenvolvimento de dados real, onde a estratégia inicial precisou ser adaptada em resposta às descobertas feitas durante a fase de análise exploratória.

#### **Plano Inicial**
A concepção original era construir um modelo preditivo utilizando estatísticas detalhadas de jogo (chutes a gol, posse de bola, etc.), disponíveis no arquivo `estatisticas-full.csv`. A hipótese era que essas features detalhadas gerariam um modelo com alta acurácia.

#### **Plot Twist**
Durante a análise e limpeza dos dados, um problema crítico de qualidade foi identificado: o arquivo de estatísticas detalhadas continha muitos dados faltantes ou zerados, especialmente nos períodos mais antigos (pré-2014) e nos mais recentes (pós-2022). Prosseguir com este plano significaria construir um modelo que não seria confiável para prever os jogos atuais.

#### **A Decisão**
Diante do desafio, uma decisão estratégica foi tomada: **abandonar a fonte de dados inconsistente e focar 100% no arquivo `full.csv`**. A análise mostrou que este arquivo, apesar de ter menos detalhes estatísticos, era extremamente rico em informações contextuais e táticas (`formação`, `técnico`, `estado`) e, o mais importante, era **consistente e confiável** para todo o período desejado (2014-2024).

#### **O Caminho Final e Principais Aprendizados**
A nova estratégia focou em extrair o máximo valor da fonte de dados mais confiável. Isso levou à criação de um sistema de features robusto, baseado em dois pilares: a **"forma"** recente das equipes (performance baseada em resultados) e o **"contexto"** do jogo (fatores táticos e circunstanciais).

Esta jornada reforçou aprendizados cruciais:
* **A qualidade dos dados supera a quantidade:** É melhor ter um modelo baseado em features consistentes e confiáveis do que um modelo baseado em dados "detalhados", mas de baixa qualidade.
* **Adaptabilidade é chave:** A capacidade de pivotar uma estratégia com base nas evidências encontradas na fase de exploração é fundamental para o sucesso de um projeto de dados.
* **Engenharia de Features é o coração do projeto:** O valor do modelo final foi derivado diretamente da habilidade de traduzir conceitos do futebol (forma, tática, rivalidade) em representações matemáticas que a IA pudesse entender.

## 🔮 Próximos Passos

* **Hyperparameter Tuning:** Otimizar os parâmetros do modelo XGBoost para extrair o máximo de acurácia.
* **Expandir a API:** Criar novos endpoints, como um que retorne as probabilidades de cada resultado (`/predict_proba`).
* **Pipeline de CI/CD:** Automatizar os testes e o deployment de novas versões da API usando ferramentas como GitHub Actions.