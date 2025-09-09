# Guia de Implementação: Pipeline MLOps Preditiva na AWS

Bem-vindo ao guia de implementação do projeto Predictor Fut BR! Este documento detalha o passo a passo para construir e implantar a arquitetura completa na sua própria conta da AWS.

## 📋 Pré-requisitos
Antes de começar, garanta que você tenha:
1. Uma conta na AWS com acesso de administrador.

2. AWS CLI instalado e configurado em sua máquina local.

3. Docker Desktop instalado e rodando.

4. Python 3.11+ instalado.

5. Git instalado.

## ⚙️ Fase 0: Configuração Inicial do Projeto
Nesta fase, preparamos o ambiente local e as configurações.

1. **Clonar o Repositório:**
   ```bash
    git clone https://github.com/Bolinhx/predictor_fut_br.git
    cd predictor_fut_br
    ```
2. **Configurar Variáveis de Ambiente:**
   - Renomeie o arquivo .env.example para .env.
   - Abra o arquivo .env e preencha todas as variáveis com os valores da sua conta e recursos que serão criados.
3. **Criar Ambiente Virtual e Instalar Dependências:**
   ```bash
   python -m venv venv
    source venv/bin/activate  # ou .\\venv\\Scripts\\activate no Windows
    pip install -r requirements.txt
    pip install -r ml_jobs/requirements-jobs.txt
    pip install -r frontend/requirements-frontend.txt
    ```

## 🏗️ Fase 1: Fundação da Infraestrutura na AWS

Nesta fase, criamos os recursos de base que nosso sistema precisará para armazenar dados e código. Não vamos rodar nada ainda, apenas preparar o terreno.

### 1. IAM - Criando um Usuário para Automação

Nunca usamos a conta "root" (principal) para tarefas do dia a dia ou para automação. O primeiro passo é criar um usuário dedicado com permissões específicas, seguindo o **princípio do menor privilégio**.

1.  Acesse o **Console da AWS** e procure pelo serviço **IAM**.
2.  No menu lateral, clique em **Users** (Usuários) e depois em **Create user**.
3.  **User details:**
    * **User name:** Dê um nome para o usuário, por exemplo: `predictor-project-user`.
    * **NÃO** marque a opção "Provide user access to the AWS Management Console". Este usuário será usado apenas por programas (acesso programático).
4.  **Set permissions:**
    * Selecione a opção **Attach policies directly**.
    * Na barra de busca, procure e marque as seguintes políticas gerenciadas pela AWS. Elas darão as permissões necessárias para nossos serviços interagirem:
        * `AmazonS3FullAccess`
        * `AmazonEC2ContainerRegistryFullAccess` (ou `AmazonECRFullAccess`)
        * `AWSAppRunnerFullAccess`
        * `AmazonECS_FullAccess`
        * `AWSStepFunctionsFullAccess`
5.  **Review and create:**
    * Revise as informações e clique em **Create user**.
6.  **Salve as Credenciais (Etapa Crítica):**
    * Na lista de usuários, clique no nome do usuário que você acabou de criar.
    * Vá para a aba **Security credentials**.
    * Role para baixo até **Access keys** e clique em **Create access key**.
    * Selecione **Command Line Interface (CLI)**, marque a caixa de confirmação e clique em **Next**.
    * Clique em **Create access key**.
    * **IMPORTANTE:** Copie e salve o `Access key ID` e a `Secret access key` em um local seguro. Esta é a **única vez** que a chave secreta será exibida.
7.  **Configure a AWS CLI:**
    * Abra seu terminal e configure o perfil de acesso com as chaves que você acabou de salvar:
        ```bash
        aws configure
        # Preencha com seu Access Key ID, Secret Access Key, uma região padrão (ex: us-east-1) e o formato de saída (json).
        ```

### 2. S3 - Criando nosso Bucket de Armazenamento (Data Lake)

O Amazon S3 será o coração do nosso armazenamento, guardando os dados brutos, as features processadas e os modelos treinados.

1.  No console da AWS, procure e vá para o serviço **S3**.
2.  Clique em **Create bucket**.
3.  **General configuration:**
    * **Bucket name:** Dê um nome **globalmente único**. Use o padrão do seu arquivo `.env`: `predictor-fut-br-data-SEU-NOME-UNICO`.
    * **AWS Region:** Selecione a mesma região que você configurou no seu AWS CLI.
4.  **Block Public Access settings:**
    * Mantenha a opção **Block all public access** LIGADA (marcada). Nossos dados são privados.
5.  **Bucket Versioning:**
    * Selecione **Enable**. Isso nos protege contra exclusões acidentais.
6.  **Default encryption:**
    * Selecione **Enable**. Garanta que a opção `Amazon S3-managed keys (SSE-S3)` esteja selecionada (esta opção não tem custo).
7.  Clique em **Create bucket**.
8.  **Crie as Pastas:**
    * Dentro do bucket, clique em **Create folder** e crie as três pastas necessárias: `raw`, `processed` e `models`.
9.  **Faça o Upload do Dado Inicial:**
    * Navegue até a pasta `raw` e faça o upload do arquivo `campeonato-brasileiro-full.csv` do seu computador.
     
   <img width="2111" height="708" alt="S3 - Raiz" src="https://github.com/user-attachments/assets/11a625dc-de39-463a-a276-26fd0c7a6170" />



### 3. ECR - Criando os Repositórios para as Imagens Docker

O Elastic Container Registry (ECR) é o nosso "Docker Hub" privado na AWS, onde guardaremos as imagens prontas para serem usadas pelo App Runner e Fargate.

1.  No console da AWS, procure e vá para o serviço **Elastic Container Registry (ECR)**.
2.  Clique em **Create repository**.
3.  Configure o primeiro repositório:
    * **Visibility settings:** `Private`
    * **Repository name:** Use o nome que está no seu arquivo `.env`: `prediction-api` (ou o que você definiu).
    * Clique em **Create repository**.
4.  Repita o processo para criar o segundo repositório com o nome `ml-jobs`.
   
   <img width="2116" height="822" alt="ECR-Repositorys" src="https://github.com/user-attachments/assets/df06fc01-99a4-466b-bd66-a919bfcef2d9" />

   

## 🚀 Fase 2: Deploy Manual e Validação

Nesta fase, vamos colocar nosso código para rodar na nuvem pela primeira vez. O objetivo é validar cada componente de forma isolada (as imagens Docker, as permissões, os serviços) antes de conectá-los com a automação.

### 1. Build e Push das Imagens Docker

Nossas "receitas" (`Dockerfile`) estão prontas. Agora vamos usá-las para construir as imagens e enviá-las para nosso registro privado na AWS (ECR).

1.  **Autenticar o Docker no ECR:**
    No seu terminal, execute o comando abaixo, substituindo `sua-regiao` e `SEU_ID_DE_CONTA` pelos seus valores. A forma mais fácil de obter o comando exato é ir ao console do **ECR**, clicar em um dos repositórios e no botão **"View push commands"**.
    ```bash
    aws ecr get-login-password --region sua-regiao | docker login --username AWS --password-stdin SEU_ID_DE_CONTA.dkr.sua-regiao.amazonaws.com
    ```
    Você deve ver a mensagem "Login Succeeded".

2.  **Construir, Marcar (Tag) e Enviar as Imagens:**
    Execute os seguintes comandos na raiz do seu projeto. Lembre-se de preencher as variáveis no seu arquivo `.env` primeiro, pois os comandos usam `$(grep ...)` para lê-las.

    * **Para a API de Predição:**
        ```bash
        # Obter a URI do repositório a partir do seu arquivo .env
        ECR_URI_API=$(grep ECR_REPO_API .env | cut -d '=' -f2 | tr -d '"')
        AWS_ACCOUNT_ID=$(grep AWS_ACCOUNT_ID .env | cut -d '=' -f2 | tr -d '"')
        AWS_REGION=$(grep AWS_REGION .env | cut -d '=' -f2 | tr -d '"')
        
        # Construir, marcar e enviar
        docker build -t $ECR_URI_API -f api/Dockerfile .
        docker tag $ECR_URI_API:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_[REGION.amazonaws.com/$ECR_URI_API:latest](https://REGION.amazonaws.com/$ECR_URI_API:latest)
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_[REGION.amazonaws.com/$ECR_URI_API:latest](https://REGION.amazonaws.com/$ECR_URI_API:latest)
        ```

    * **Para os Jobs de ML:**
        ```bash
        # Obter a URI do repositório a partir do seu arquivo .env
        ECR_URI_JOBS=$(grep ECR_REPO_JOBS .env | cut -d '=' -f2 | tr -d '"')
        
        # Construir, marcar e enviar
        docker build -t $ECR_URI_JOBS -f ml_jobs/Dockerfile .
        docker tag $ECR_URI_JOBS:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_[REGION.amazonaws.com/$ECR_URI_JOBS:latest](https://REGION.amazonaws.com/$ECR_URI_JOBS:latest)
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_[REGION.amazonaws.com/$ECR_URI_JOBS:latest](https://REGION.amazonaws.com/$ECR_URI_JOBS:latest)
        ```

### 2. Deploy da API no AWS App Runner

Com a imagem da API no ECR, vamos colocá-la no ar.

1.  Acesse o serviço **AWS App Runner** no console e clique em **Create service**.
2.  **Source and deployment:**
    * **Source:** `Container registry`
    * **Container image registry:** `Amazon ECR`
    * **Container image URI:** Clique em **Browse** e selecione a imagem da sua API (ex: `prediction-api`).
3.  **Configure service:**
    * **Service name:** `prediction-api`.
    * **Virtual CPU & memory:** Para testes, comece com `1 vCPU` e `2 GB`. Se a aplicação falhar ao iniciar, pode ser necessário aumentar a memória para `3 GB`.
    * **Port:** `80`.
4.  **Security (Etapa Crucial):**
    * Na seção **Security**, clique em **Edit**.
    * **Instance role:** Para que a API possa acessar o S3, precisamos de uma permissão. Crie uma nova IAM Role seguindo estes passos:
        * Vá para o **IAM** -> **Roles** -> **Create role**.
        * **Trusted entity type:** `Custom trust policy`. Cole o JSON:
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "tasks.apprunner.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            ```
        * **Permissions:** Anexe a política gerenciada pela AWS `AmazonS3ReadOnlyAccess`.
        * **Role name:** `AppRunnerInstanceRole`.
        * Volte para a configuração do App Runner, atualize a lista e selecione a `AppRunnerInstanceRole` que você acabou de criar.
5.  Clique em **Create & deploy**.

#### 🚨 Solução de Problemas Comuns no App Runner
* **Erro `Failed to create...`:** Geralmente é um problema de tempo ou memória.
    * **`Health check failed`:** A aplicação demorou muito para iniciar. Edite o serviço, vá em **Health check** e aumente os valores de **Timeout** (para `20s`) e **Interval** (para `25s`).
    * **`Unable to locate credentials`:** A **Instance role** não foi criada ou anexada corretamente. Verifique o passo 4.

### 3. Execução Manual dos Jobs no Fargate

Vamos validar que nossos scripts de processamento e treinamento rodam na nuvem.

1.  **Crie as Permissões (IAM Roles):** Nossa tarefa precisa de duas "credenciais":
    * **Task Execution Role:** Permissão para o Fargate buscar a imagem no ECR. Geralmente a role `ecsTaskExecutionRole` já existe na conta.
    * **Task Role:** Permissão para o **nosso código** acessar outros serviços.
        * Vá para **IAM** -> **Roles** -> **Create role**.
        * **Trusted entity:** `AWS service` -> **Use case:** `Elastic Container Service Task`.
        * **Permissions:** Anexe as políticas `AmazonS3FullAccess` e `AWSAppRunnerFullAccess`.
        * **Role name:** `ECSTaskS3AppRunnerRole`.

2.  **Crie a Definição da Tarefa (Task Definition):**
    * Vá para **Amazon ECS** -> **Task Definitions** -> **Create new task definition**.
    * **Task definition family:** `ml-job-task-family`.
    * **Launch type:** `AWS Fargate`.
    * **Task role:** Selecione a `ECSTaskS3AppRunnerRole` que acabamos de criar.
    * **Task execution role:** Selecione a `ecsTaskExecutionRole`.
    * **Container details:**
        * **Name:** `ml-jobs-container`.
        * **Image URI:** Cole a URI da sua imagem `ml-jobs` do ECR.
    * Clique em **Create**.

3.  **Execute a Tarefa Manualmente:**
    * Vá para **Amazon ECS** -> **Clusters** e selecione o cluster `default` (ou crie um novo do tipo "Networking only" se não existir).
    * Clique na aba **Tasks** -> **Run new task**.
    * **Launch type:** `FARGATE`.
    * **Task definition:** Selecione a `ml-job-task-family`.
    * **Networking:** Garanta que uma VPC e Subnets estejam selecionadas e que **Public IP** esteja **ENABLED**.
    * **Container Overrides:** Expanda a seção e, no campo **Command**, cole o comando para o primeiro script (separado por vírgulas):
        ```text
        python,data_processor.py,s3://SEU-BUCKET/raw/campeonato-brasileiro-full.csv,s3://SEU-BUCKET/raw/campeonato-brasileiro-full.csv,s3://SEU-BUCKET/processed/features.parquet
        ```
        *(Nota: Para este teste, usamos o mesmo arquivo como histórico e "novo", o que funciona para validação).*
    * Clique em **Run task**.

#### 🚨 Solução de Problemas Comuns no Fargate
* **Erro `iam:PassRole`:** O serviço que está executando a tarefa (Step Functions, no futuro) precisa de permissão para "entregar" a `Task Role` à tarefa.
* **Erro `PermissionError: Forbidden`:** A `Task Role` (`ECSTaskS3AppRunnerRole`) não tem a permissão necessária (ex: `AmazonS3FullAccess`).
* **Erro `FileNotFoundError: fsspec`:** A imagem Docker está sem as bibliotecas `fsspec` e `s3fs`. Adicione-as ao `ml_jobs/requirements-jobs.txt`.


## 🤖 Fase 3: Automação com a Pipeline MLOps

Com os componentes validados, vamos conectar tudo em um fluxo de trabalho 100% automático. Usaremos o **AWS Step Functions** como o "maestro" que orquestra as tarefas e o **Amazon EventBridge** como o "sensor" que dispara a pipeline.

### 1. Criação da Pipeline no Step Functions (O Maestro)

A State Machine no Step Functions é o nosso fluxograma executável.

1.  Acesse o serviço **Step Functions** no console e clique em **Create state machine**.
2.  Mantenha as opções **Design your workflow visually** e **Type: Standard**.
3.  Você estará no **Workflow Studio**. Na barra de "Actions" à esquerda, encontre e arraste a ação **ECS RunTask** para o fluxograma três vezes, uma abaixo da outra, para criar uma sequência de três passos.
4.  **Configure cada passo** clicando nele e preenchendo as informações no painel direito:

    ---
    #### **Passo 1: Processar Novos Dados**
    * **Aba "Configuration":**
        * **State name:** `ProcessarNovosDados`
        * **Marque a caixa:** `Wait for task to complete` (essencial para a execução em sequência).
    * **Aba "Arguments & Output":**
        * No campo **Arguments**, cole o JSON abaixo, substituindo os placeholders com seus valores do arquivo `.env`.
            ```json
            {
              "LaunchType": "FARGATE",
              "Cluster": "predictor-fut-br-cluster",
              "TaskDefinition": "ml-job-task-family",
              "NetworkConfiguration": {
                "AwsvpcConfiguration": {
                  "Subnets": [
                    "SUA_SUBNET_ID_AQUI"
                  ],
                  "AssignPublicIp": "ENABLED"
                }
              },
              "Overrides": {
                "ContainerOverrides": [
                  {
                    "Name": "ml-jobs-container",
                    "Command": [
                      "python",
                      "data_processor.py",
                      "s3://SEU_BUCKET_NAME/raw/campeonato-brasileiro-full.csv",
                      "s3://SEU_BUCKET_NAME/raw/campeonato-brasileiro-full.csv",
                      "s3://SEU_BUCKET_NAME/processed/features.parquet"
                    ]
                  }
                ]
              }
            }
            ```

    ---
    #### **Passo 2: Treinar Novo Modelo**
    * **Aba "Configuration":**
        * **State name:** `TreinarNovoModelo`
        * **Marque a caixa:** `Wait for task to complete`.
    * **Aba "Arguments & Output":**
        * No campo **Arguments**, cole o mesmo JSON, alterando apenas o `Command`:
            ```json
            {
              "LaunchType": "FARGATE",
              "Cluster": "predictor-fut-br-cluster",
              "TaskDefinition": "ml-job-task-family",
              "NetworkConfiguration": {
                "AwsvpcConfiguration": {
                  "Subnets": [
                    "SUA_SUBNET_ID_AQUI"
                  ],
                  "AssignPublicIp": "ENABLED"
                }
              },
              "Overrides": {
                "ContainerOverrides": [
                  {
                    "Name": "ml-jobs-container",
                    "Command": [
                      "python",
                      "model_trainer.py",
                      "s3://SEU_BUCKET_NAME/processed/features.parquet",
                      "s3://SEU_BUCKET_NAME/models/modelo_final.joblib"
                    ]
                  }
                ]
              }
            }
            ```

    ---
    #### **Passo 3: Implantar Nova API**
    * **Aba "Configuration":**
        * **State name:** `ImplantarNovaAPI`
        * **Marque a caixa:** `Wait for task to complete`.
    * **Aba "Arguments & Output":**
        * No campo **Arguments**, cole o mesmo JSON, alterando apenas o `Command`:
            ```json
            {
              "LaunchType": "FARGATE",
              "Cluster": "predictor-fut-br-cluster",
              "TaskDefinition": "ml-job-task-family",
              "NetworkConfiguration": {
                "AwsvpcConfiguration": {
                  "Subnets": [
                    "SUA_SUBNET_ID_AQUI"
                  ],
                  "AssignPublicIp": "ENABLED"
                }
              },
              "Overrides": {
                "ContainerOverrides": [
                  {
                    "Name": "ml-jobs-container",
                    "Command": [
                      "python",
                      "deploy_api.py",
                      "SEU_APP_RUNNER_SERVICE_ARN_AQUI"
                    ]
                  }
                ]
              }
            }
            ```

5.  Clique em **Next**. Na tela de revisão, dê um nome à sua pipeline (ex: `Fut-BR-Retraining-Pipeline`) e selecione **Create new IAM role**. Clique em **Create state machine**.

> 📸 **Sugestão de Print:** Tire um print do **Graph inspector** do Step Functions mostrando a execução bem-sucedida com todos os três passos em verde.

#### 🚨 Solução de Problemas Comuns no Step Functions
* **Erro `AccessDeniedException: ... is not authorized to perform: ecs:RunTask`:** A "role" criada automaticamente para o Step Functions não tem permissão para iniciar tarefas no ECS.
    * **Solução:** Vá para **IAM** -> **Roles** e encontre a role do seu Step Function. Clique em **Add permissions** -> **Create inline policy** e adicione a seguinte política JSON:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["ecs:RunTask", "ecs:StopTask", "ecs:DescribeTasks"],
                    "Resource": "*"
                }
            ]
        }
        ```
* **Erro `AccessDeniedException: ... is not authorized to perform: iam:PassRole`:** O Step Functions não tem permissão para "entregar" as credenciais (`ECSTaskS3AppRunnerRole` e `ecsTaskExecutionRole`) para a tarefa Fargate.
    * **Solução:** Na mesma "role" do Step Functions, crie outra política inline com o seguinte JSON, substituindo os ARNs pelos da sua conta:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": [
                        "ARN_DA_SUA_ROLE_ECSTaskS3AppRunnerRole_AQUI",
                        "ARN_DA_SUA_ROLE_ecsTaskExecutionRole_AQUI"
                    ],
                    "Condition": {
                        "StringEquals": { "iam:PassedToService": "ecs-tasks.amazonaws.com" }
                    }
                }
            ]
        }
        ```

### 2. Criação do Gatilho no EventBridge (O Sensor)

Este serviço irá "observar" nosso S3 e iniciar a pipeline automaticamente.

1.  Acesse o serviço **Amazon EventBridge** e clique em **Create rule**.
2.  **Name:** `Trigger-Retraining-On-New-Data`.
3.  **Event bus:** `default`.
4.  **Rule type:** `Rule with an event pattern`.
5.  **Event pattern:** Selecione **Custom pattern (JSON editor)** e cole o seguinte JSON, substituindo o nome do seu bucket:
    ```json
    {
      "source": ["aws.s3"],
      "detail-type": ["Object Created"],
      "detail": {
        "bucket": {
          "name": ["SEU_BUCKET_NAME"]
        },
        "object": {
          "key": [{
            "prefix": "raw/"
          }, {
            "suffix": ".csv"
          }]
        }
      }
    }
    ```
6.  **Select a target:**
    * **Target types:** `AWS service`.
    * **Select a target:** `Step Functions state machine`.
    * **State machine:** `Fut-BR-Retraining-Pipeline`.
    * **Execution role:** `Create a new role for this specific resource`.
7.  Clique em **Create rule**.

#### 🚨 Solução de Problemas Comuns no EventBridge
* **A pipeline não inicia ao subir um arquivo:** O S3 não tem permissão para enviar notificações ao EventBridge.
    * **Solução:** Vá para o seu **Bucket S3** -> **Properties** -> **Event Notifications**. Encontre a opção **"Send notifications to Amazon EventBridge"**, clique em **Edit** e mude para **On**.


## 🖥️ Fase 4: Frontend com Streamlit

Com todo o nosso sistema de backend e MLOps funcionando nos bastidores, chegou a hora de construir a interface que o nosso usuário final (o jornalista) irá usar. Vamos criar uma aplicação web simples e funcional usando **Streamlit**, uma biblioteca Python que facilita a criação de interfaces para projetos de dados.

### 1. Teste Local da Aplicação

Antes de colocar o frontend online, é essencial testá-lo em sua máquina para garantir que ele consegue se comunicar com a API na AWS.

1.  **Reative a API no App Runner:**
    * Vá para o console do **AWS App Runner** e, no seu serviço `prediction-api`, clique em **"Resume"**. Aguarde o status mudar para **"Running"**.

2.  **Instale as Dependências do Frontend:**
    * No seu terminal, na raiz do projeto (com o ambiente virtual `venv` ativado), execute:
        ```bash
        pip install -r frontend/requirements-frontend.txt
        ```

3.  **Preencha as Variáveis de Ambiente:**
    * Certifique-se de que o seu arquivo `.env` na raiz do projeto está preenchido com os valores corretos para `S3_BUCKET_NAME` e `APP_RUNNER_SERVICE_URL`. O script local lerá essas variáveis.

4.  **Execute a Aplicação Streamlit:**
    * No mesmo terminal, execute o comando:
        ```bash
        streamlit run frontend/app.py
        ```

5.  Seu navegador deve abrir automaticamente com a aplicação rodando. Teste a seleção de times e clique no botão "Analisar e Prever Resultado" para confirmar que a comunicação com a API está funcionando.

> 📸 **Sugestão de Print:** Tire um print da aplicação Streamlit rodando localmente com uma previsão bem-sucedida sendo exibida na tela.

### 2. Deploy na Streamlit Community Cloud

Agora, vamos hospedar nossa aplicação de graça, com um link público, usando a plataforma da própria Streamlit.

1.  **Crie uma Conta:**
    * Vá para [share.streamlit.io](https://share.streamlit.io) e crie uma conta, conectando-a com seu perfil do GitHub. É um processo rápido e gratuito.

2.  **Faça um Último Commit:**
    * Garanta que todo o seu código, incluindo a pasta `frontend` e o `IMPLEMENTATION_GUIDE.md`, esteja atualizado no seu repositório do GitHub.
        ```bash
        git add .
        git commit -m "docs: Finaliza guia de implementação"
        git push origin main
        ```

3.  **Crie a Nova Aplicação no Streamlit Cloud:**
    * No seu dashboard do Streamlit, clique em **"New app"**.
    * **Repository:** Selecione o seu repositório `predictor_fut_br`.
    * **Branch:** Selecione `main`.
    * **Main file path:** Digite o caminho para o arquivo principal: `frontend/app.py`.
    * **App URL:** Dê um nome customizado para a sua URL (ex: `predictor-fut-br`).

4.  **Configure os "Secrets" (Etapa Crucial):**
    * Antes de clicar em "Deploy", clique no link **"Advanced settings..."**.
    * Na seção **Secrets**, você precisa adicionar as mesmas variáveis de ambiente do seu arquivo `.env` para que a aplicação na nuvem possa se conectar à AWS. Adicione os seguintes "secrets":
        * `AWS_ACCESS_KEY_ID`: Cole a chave de acesso do seu usuário IAM `predictor-project-user`.
        * `AWS_SECRET_ACCESS_KEY`: Cole a chave secreta do seu usuário IAM.
        * `S3_BUCKET_NAME`: Cole o nome do seu bucket S3.
        * `APP_RUNNER_SERVICE_URL`: Cole a URL da sua API no App Runner.
    * **Importante:** A biblioteca `python-dotenv` não funciona no Streamlit Cloud; ele injeta os "secrets" como variáveis de ambiente, e nosso código já está preparado para ler isso.

5.  **Faça o Deploy:**
    * Clique no botão **"Deploy!"**. O Streamlit irá construir o ambiente e colocar sua aplicação no ar.

> 📸 **Sugestão de Print:** Tire um print da sua aplicação rodando online, no link público fornecido pelo Streamlit Cloud. E outro print da tela de configuração de "Secrets" no Streamlit Cloud, mostrando as chaves que você adicionou (censure os valores das chaves de acesso).

#### 🚨 Solução de Problemas Comuns no Streamlit
* **Erro de Credenciais na Nuvem:** Se a aplicação online não conseguir acessar o S3, o problema quase sempre está nos "Secrets". Verifique se os nomes das variáveis e seus valores foram copiados corretamente.
* **`ModuleNotFoundError`:** O Streamlit não encontrou uma biblioteca. Verifique se o arquivo `frontend/requirements-frontend.txt` está correto e atualizado no GitHub.

## 🧹 Fase 5: Limpeza dos Recursos

Após concluir o projeto e a documentação, é crucial remover todos os recursos criados na AWS para garantir que não haja cobranças futuras. Siga esta lista de verificação na **ordem exata** para evitar erros de dependência (onde não é possível excluir um recurso porque outro ainda depende dele).

### Checklist de Desmontagem

1.  **Pausar e Deletar o Serviço do App Runner:**
    * Vá para o console do **AWS App Runner**.
    * Selecione o serviço `prediction-api`.
    * Se estiver com o status "Running", clique em **"Actions"** -> **"Pause"**. Aguarde o status mudar para "Paused".
    * Com o serviço pausado, clique em **"Actions"** -> **"Delete"**. Confirme a exclusão.

2.  **Deletar a Regra do EventBridge:**
    * Vá para o console do **Amazon EventBridge**.
    * No menu lateral, clique em **Rules**.
    * Selecione a regra `Trigger-Retraining-On-New-Data` e clique em **"Delete"**. Confirme a exclusão.

3.  **Deletar a Pipeline do Step Functions:**
    * Vá para o console do **AWS Step Functions**.
    * No menu lateral, clique em **State machines**.
    * Selecione a pipeline `Fut-BR-Retraining-Pipeline` e clique em **"Delete"**. Confirme a exclusão.

4.  **Desregistrar a Definição de Tarefa do ECS:**
    * Vá para o console do **Amazon ECS**.
    * No menu lateral, clique em **Task Definitions**.
    * Selecione a família `ml-job-task-family`.
    * Para cada revisão na lista (ex: `:1`, `:2`), clique nela, vá em **"Actions"** -> **"Deregister"**.

5.  **Deletar o Cluster do ECS:**
    * Ainda no console do ECS, clique em **Clusters**.
    * Selecione o seu cluster `predictor-fut-br-cluster`.
    * Clique em **"Delete Cluster"**. Confirme a exclusão.

6.  **Deletar Imagens e Repositórios do ECR:**
    * Vá para o console do **Amazon ECR**.
    * Clique em cada um dos seus repositórios (`prediction-api` e `ml-jobs`).
    * Dentro de cada repositório, selecione todas as imagens listadas e clique em **"Delete"**.
    * Depois que os repositórios estiverem vazios, volte para a lista principal, selecione-os e clique em **"Delete"**.

7.  **Esvaziar e Deletar o Bucket S3:**
    * Vá para o console do **Amazon S3**.
    * Selecione o seu bucket `predictor-fut-br-data-...`.
    * Clique no botão **"Empty"**. O S3 o guiará pelo processo de confirmação para apagar todos os objetos e versões.
    * Depois que o bucket estiver vazio, volte para a lista de buckets, selecione-o e clique em **"Delete"**.

8.  **Deletar as IAM Roles:**
    * Vá para o console do **IAM** -> **Roles**.
    * Encontre e delete as "roles" que criamos para este projeto. As principais são:
        * `AppRunnerInstanceRole`
        * `ECSTaskS3AppRunnerRole` (ou o nome que você deu)
        * A "role" do Step Functions (o nome começa com `StepFunctions-Fut-BR-Retraining-Pipeline-role-...`)
        * A "role" do EventBridge (o nome começa com `EventBridge-Trigger-Retraining-...`)
    * **Opcional:** Você também pode deletar o usuário `predictor-project-user` que criamos na Fase 1, se não for mais utilizá-lo.

### Verificação Final

No dia seguinte, acesse o **AWS Billing Dashboard** e verifique no **Cost Explorer** se seus custos diários voltaram a zero, confirmando que todos os recursos faturáveis foram removidos com sucesso.
