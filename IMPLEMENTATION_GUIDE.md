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
Aqui, criamos os recursos de base que nosso sistema precisará.

1. **IAM - Usuário Programático:**
   - WIP (Descrever o passo a passo para criar o usuário predictor-project-user com as políticas necessárias)
2. **S3 - Bucket de Armazenamento:**
   - WIP (Descrever como criar o bucket S3, habilitar o versionamento e a criptografia, e criar as pastas raw, processed e models).
3. **ECR - Registro de Contêineres:**
   - WIP (Descrever como criar os dois repositórios no ECR: prediction-api e ml-jobs).

## 🚀 Fase 2: Deploy Manual e Validação
Nesta fase, validamos cada componente manualmente antes de automatizar.

1. **Build e Push das Imagens Docker:**
   - WIP (Inclir os comandos docker build, tag e push para as duas imagens, explicando como obter a URI do ECR).
2. **Deploy da API no App Runner:**
   - WIP (Detalhe o processo de criação do serviço no App Runner, a configuração da porta, CPU/Memória e, crucialmente, a criação da Instance Role para acesso ao S3).
   - WIP Solução de Problemas: Mencionar os erros comuns, como o timeout do Health Check e a necessidade de aumentar a memória.
3. **Execução Manual dos Jobs no Fargate:**
   - WIP (Explicar como criar a Task Definition, a ECSTaskS3AccessRole e a ecsTaskExecutionRole. Mostre como executar a tarefa manualmente com o "Command Override" e como depurar os logs).
   - WIP (Solução de Problemas: Detalhar os erros de permissão (iam:PassRole, AccessDenied) e como corrigi-los editando as políticas do IAM.)

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

- (Listar a ordem correta para deletar todos os recursos da AWS: App Runner, EventBridge, Step Functions, ECS, ECR, S3, IAM Roles).