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

1. **IAM - Usuário Programático:**
   Nunca usamos a conta "root" (principal) para tarefas do dia a dia ou para automação. O primeiro passo é criar um usuário dedicado com permissões específicas, seguindo o princípio do menor privilégio.

    1. Acesse o **Console da AWS** e procure pelo serviço IAM.

    2. No menu lateral, clique em **Users** (Usuários) e depois em Create user.

    3. **User details:**

   *  User name: Dê um nome para o usuário, por exemplo: predictor-project-user.

    *  NÃO marque a opção "Provide user access to the AWS Management Console". Este usuário será usado apenas  1. por programas (acesso programático).
    *  
    4. **Set permissions:**
   *   Selecione a opção Attach policies directly.

   *   Na barra de busca, procure e marque as seguintes políticas gerenciadas pela AWS. Elas darão as permissões necessárias para nossos serviços interagirem:

       *   `AmazonS3FullAccess`

       *   `AmazonEC2ContainerRegistryFullAccess` (ou `AmazonECRFullAccess`)

       *   `AWSAppRunnerFullAccess`

       *   `AmazonECS_FullAccess`

       *   `AWSStepFunctionsFullAccess`
    5. **Review and create:**
   *   Revise as informações e clique em *Create user*.
    6. **Salve as Credenciais (Etapa Crítica):**
   *   Na lista de usuários, clique no nome do usuário que você acabou de criar.
   *   Vá para a aba **Security credentials**.
   *   Role para baixo até **Access keys** e clique em **Create access key.**
   *   Selecione **Command Line Interface (CLI)**, marque a caixa de confirmação e clique em **Next**.
   *   Clique em **Create access key**.
   *   ***IMPORTANTE:*** Copie e salve o `Access key ID` e a `Secret access key` em um local seguro. Esta é a única vez que a chave secreta será exibida.
    7. **Configure a AWS CLI:**
   *   Abra seu terminal e configure o perfil de acesso com as chaves que você acabou de salvar:
        ```bash
        aws configure (ENTER)

        Preencha com seu Access Key ID, Secret Access Key, uma região padrão (ex: us-east-1) e o formato de saída (json).
        ```

#

2. **S3 - Criando nosso Bucket de Armazenamento (nosso "Data Lake")**
   O Amazon S3 será o coração do nosso armazenamento, guardando os dados brutos, as features processadas e os modelos treinados.

   1. No console da AWS, procure e vá para o serviço **S3**.
   2. Clique em **Create bucket.**
   3. **General configuration:**
   *   **Bucket name:** Dê um nome **globalmente único**. Use o padrão do seu arquivo `.env`: `predictor-fut-br-data-SEU-NOME-UNICO.`
   *   **AWS Region:** Selecione a mesma região que você configurou no seu AWS CLI.
   4. **Block Public Access settings:**
   *   Mantenha a opção **Block all public access** LIGADA (marcada). Nossos dados são privados.
   5. **Bucket Versioning:**
   *   Selecione **Enable.** Isso nos protege contra exclusões acidentais.
   6. **Default encryption:**
   *   Selecione **Enable**. Garanta que a opção `Amazon S3-managed keys (SSE-S3)` esteja selecionada (esta opção não tem custo).
   7. **Clique em Create bucket.**

   8. **Crie as Pastas:**
   *   Dentro do bucket, clique em **Create folder** e crie as três pastas necessárias: `raw`, `processed` e `models`.
   9. **Faça o Upload do Dado Inicial:**
   *   Navegue até a pasta `raw` e faça o upload do arquivo `campeonato-brasileiro-full.csv` do seu computador.
     
   <img width="2111" height="708" alt="S3 - Raiz" src="https://github.com/user-attachments/assets/11a625dc-de39-463a-a276-26fd0c7a6170" />


#

3. **ECR - Criando os Repositórios para as Imagens Docker**
O Elastic Container Registry (ECR) é o nosso "Docker Hub" privado na AWS, onde guardaremos as imagens prontas para serem usadas pelo App Runner e Fargate.

   1. No console da AWS, procure e vá para o serviço **Elastic Container Registry (ECR).**
   2. Clique em **Create repository.**
   3. Configure o primeiro repositório:
   *   **Visibility settings**: `Private`
   *   **Repository name:** Use o nome que está no seu arquivo `.env`: `prediction-api` (ou o que você definiu).
   *   Clique em **Create repository.**
   4. **Repita o processo** para criar o segundo repositório com o nome `ml-jobs`.
   
   <img width="2116" height="822" alt="ECR-Repositorys" src="https://github.com/user-attachments/assets/df06fc01-99a4-466b-bd66-a919bfcef2d9" />

   

## 🚀 Fase 2: Deploy Manual e Validação
Nesta fase, vamos colocar nosso código para rodar na nuvem pela primeira vez. O objetivo é validar cada componente de forma isolada (as imagens Docker, as permissões, os serviços) antes de conectá-los com a automação.

1. **Build e Push das Imagens Docker:**
   Nossas "receitas" (`Dockerfile`) estão prontas. Agora vamos usá-las para construir as imagens e enviá-las para nosso registro privado na AWS (ECR).

   1. **Autenticar o Docker no ECR:**
   No seu terminal, execute o comando abaixo, substituindo `sua-regiao` e `SEU_ID_DE_CONTA` pelos seus valores. A forma mais fácil de obter o comando exato é ir ao console do **ECR**, clicar em um dos repositórios e no botão **"View push commands".**
   ```bash
   aws ecr get-login-password --region sua-regiao | docker login --username AWS --password-stdin SEU_ID_DE_CONTA.dkr.sua-regiao.amazonaws.com
   ```
   Você deve ver a mensagem "Login Succeeded".

    2. **Construir, Marcar (Tag) e Enviar as Imagens:**
   Execute os seguintes comandos na raiz do seu projeto. Lembre-se de preencher as variáveis no seu arquivo `.env` primeiro, pois os comandos usam `$(grep ...)` para lê-las. 
   *    **Para a API de Predição:**
        ```bash
        # Obter a URI do repositório a partir do seu arquivo .env
        ECR_URI_API=$(grep ECR_REPO_API .env | cut -d '=' -f2 | tr -d '"')
        AWS_ACCOUNT_ID=$(grep AWS_ACCOUNT_ID .env | cut -d '=' -f2 | tr -d '"')
        AWS_REGION=$(grep AWS_REGION .env | cut -d '=' -f2 | tr -d '"')

        # Construir, marcar e enviar
        docker build -t $ECR_URI_API -f api/Dockerfile .
        docker tag $ECR_URI_API:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_URI_API:latest
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_URI_API:latest
        ```
   *    **Para os Jobs de ML:**
        ```bash
        # Obter a URI do repositório a partir do seu arquivo .env
        ECR_URI_JOBS=$(grep ECR_REPO_JOBS .env | cut -d '=' -f2 | tr -d '"')

        # Construir, marcar e enviar
        docker build -t $ECR_URI_JOBS -f ml_jobs/Dockerfile .
        docker tag $ECR_URI_JOBS:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_URI_JOBS:latest
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_URI_JOBS:latest
        ```

#

2. **Deploy da API no App Runner:**
    Com a imagem da API no ECR, vamos colocá-la no ar.

    1. Acesse o serviço **AWS App Runner** no console e clique em Create service
    2. **Source and deployment:**
*   **Source:** `Container registry`
*   **Container image registry:** `Amazon ECR`
*   **Container image URI:** `Container registry`
    3. **Configure service:**
*   **Service name:** `prediction-api`.
*   **Virtual CPU & memory:** Para testes, comece com `1 vCPU` e `2 GB`. Se a aplicação falhar ao iniciar, pode ser necessário aumentar a memória para `3 GB`.
*   **Port:** `80`
    4. **Security (Etapa Crucial):**
*   Na seção **Security**, clique em **Edit.**
*   **Instance role:** Para que a API possa acessar o S3, precisamos de uma permissão. Crie uma nova IAM Role seguindo estes passos:
    *   **Vá para o IAM -> Roles -> Create role.**
    *   **Trusted entity type:** `Custom trust policy`. Cole o JSON:
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
    *   **Permissions:** Anexe a política gerenciada pela AWS `AmazonS3ReadOnlyAccess`.
    *   **Role name:** `AppRunnerInstanceRole.`
    *   Volte para a configuração do App Runner, atualize a lista e selecione a `AppRunnerInstanceRole` que você acabou de criar.
    5. Clique em **Create & deploy**.

### ***🚨 Solução de Problemas Comuns no App Runner***

*   Erro` Failed to create...`: Geralmente é um problema de tempo ou memória.
*   `Health check failed:` A aplicação demorou muito para iniciar. Edite o serviço, vá em **Health check** e aumente os valores de Timeout (para `20s`) e Interval (para `25s`).
*   `Unable to locate credentials`: A **Instance role** não foi criada ou anexada corretamente. Verifique o passo 4.


# 

3. **Execução Manual dos Jobs no Fargate:**
   Vamos validar que nossos scripts de processamento e treinamento rodam na nuvem.
    1. **Crie as Permissões (IAM Roles)**: Nossa tarefa precisa de duas "credenciais":
*   **Task Execution Role:** Permissão para o Fargate buscar a imagem no ECR. Geralmente a role `ecsTaskExecutionRole` já existe na conta.
*   **Task Role:** Permissão para o nosso código acessar outros serviços.
    *   **Vá para IAM -> Roles -> Create role.**
    *   **Trusted entity:** `AWS service` -> **Use case**: `Elastic Container Service Task`.
    *   **Permissions**: Anexe as políticas `AmazonS3FullAccess` e `AWSAppRunnerFullAccess`.
    *   **Role name:** `ECSTaskS3AppRunnerRole.`
    1. **Crie a Definição da Tarefa (Task Definition)**:
*   **Vá para Amazon ECS -> Task Definitions -> Create new task definition.**
*   **Task definition family**: `ml-job-task-family`.
*   **Launch type:** `AWS Fargate`.
*   **Task role:** Selecione a `ECSTaskS3AppRunnerRole` que acabamos de criar.
*   **Task execution role:** Selecione a `ecsTaskExecutionRole`.
*   **Container details:**
    *   **Name:** `ml-jobs-container`.
    *   **Image URI:** Cole a URI da sua imagem `ml-jobs` do ECR.
*   Clique em **Create**.
    1. **Execute a Tarefa Manualmente:**
*   Vá para **Amazon ECS** -> Clusters e selecione o cluster `default` (ou crie um novo do tipo "Networking only" se não existir).
*   Clique na aba **Tasks -> Run new task.**
*   Launch type: `FARGATE`.
*   **Task definition:** Selecione a `ml-job-task-family`.
*   **Networking:** Garanta que uma VPC e Subnets estejam selecionadas e que **Public IP** esteja **ENABLED**.
*   **Container Overrides:** Expanda a seção e, no campo **Command**, cole o comando para o primeiro script (separado por vírgulas) NAO ESQUECE DE SUBSTITUIR O NOME DO SEU BUCKET!!!:
    ```bash
    python,data_processor.py,s3://SEU-BUCKET/raw/campeonato-brasileiro-full.csv,s3://SEU-BUCKET/raw/campeonato-brasileiro-full.csv,s3://SEU-BUCKET/processed/features.parquet
    ```
    (Nota: Para este teste, usamos o mesmo arquivo como histórico e "novo", o que funciona para validação).
*   Clique em **Run task**.

Se correr tudo bem, na pasta `processed` do seu bucket vai ter um arquivo com nome `features.parquet`

### ***🚨 Solução de Problemas Comuns no Fargate***

*   **Erro** `iam:PassRole`: O serviço que está executando a tarefa (Step Functions, no futuro)precisa     de permissão para "entregar" a `Task Role` à tarefa.
*   **Erro** `PermissionError`: `Forbidden`: A `Task Role` (`ECSTaskS3AppRunnerRole`) não tem a    permissão necessária (ex: `AmazonS3FullAccess`).
*   **Erro** `FileNotFoundError`: `fsspec`: A imagem Docker está sem as bibliotecas `fsspec` e`s3fs`.  Adicione-as ao `ml_jobs/requirements-jobs.txt`.

# 


## 🤖 Fase 3: Automação com a Pipeline MLOps
Agora, conectamos tudo em um fluxo automático.

1. **Criação da Pipeline no Step Functions:**
   - WIP (Mostrar como criar a State Machine visualmente, adicionando os três passos (ECS RunTask). Inclua os JSONs de configuração para cada passo).
   - WIP Solução de Problemas: Explicar a importância do .sync ("Wait for task to complete") e como depurar as permissões da "role" do Step Functions.
2. **Criação do Gatilho no EventBridge:**
   - WIP (Mostrar como criar a regra, usando o JSON do "Event Pattern" para filtrar os eventos do S3. Explique a configuração do alvo).
   - WIP Solução de Problemas: Destacar a necessidade de habilitar as "Event Notifications" nas propriedades do bucket S3.

## 🖥️ Fase 4: Frontend com Streamlit
A interface para o usuário final.

1. **Teste Local:**
   - WIP (Explicar como rodar o streamlit run localmente para testar a interface).
1. **Deploy na Streamlit Community Cloud:**
   - WIP (Descrever o passo a passo para conectar o repositório do GitHub ao Streamlit Cloud e fazer o deploy).

## 🧹 Fase 5: Limpeza dos Recursos
Um guia essencial para evitar custos inesperados.

- WIP (Listar a ordem correta para deletar todos os recursos da AWS: App Runner, EventBridge, Step Functions, ECS, ECR, S3, IAM Roles).
