### Legenda do Diagrama de Arquitetura

O diagrama ilustra os três principais fluxos de trabalho que compõem o sistema, cada um representado por um subgráfico.

#### 1. Fluxo da Aplicação do Usuário

Este fluxo descreve como o usuário final interage com o sistema para obter uma previsão.

* **Jornalista (Usuário Final):** O ator que inicia o processo.
* **Streamlit Cloud:** A aplicação web (frontend). **Sua responsabilidade é crucial:**
    1.  Ao iniciar, busca os dados históricos do **Amazon S3 (/raw)**.
    2.  Com base nos times selecionados pelo usuário, **calcula em tempo real as features** de "forma" e "contexto".
    3.  Envia o JSON com as features calculadas para a API de previsão.
* **AWS App Runner:** O serviço serverless que hospeda nossa API. Sua única função é receber as features já prontas e retornar uma previsão.
* **Amazon S3 (/models):** O local onde o modelo de Machine Learning treinado fica armazenado. A API o carrega na inicialização.

#### 2. Pipeline Automática de Retreinamento de Modelo

Este é o coração da automação MLOps. Ele descreve como o sistema se atualiza sozinho quando novos dados chegam.

* **Amazon S3 (Novos dados em /raw):** A chegada de um novo arquivo `.csv` nesta pasta inicia todo o processo.
* **Amazon EventBridge:** O "sensor" que detecta o novo arquivo e dispara um evento.
* **AWS Step Functions:** O "maestro" que recebe o evento e orquestra uma sequência de tarefas.
* **AWS Fargate (Jobs):** O serviço que executa nossos contêineres sob demanda para as três etapas principais:
    1.  **ETL:** Processa os dados brutos e salva as features tratadas no S3.
    2.  **Treinamento:** Carrega as features, treina um novo modelo e o salva no S3.
    3.  **Deploy:** Comanda o App Runner para iniciar uma nova implantação da API, que passará a usar o novo modelo.

#### 3. Fluxo de Atualização de Código (CI)

Este fluxo descreve como as atualizações no código-fonte são **validadas e implantadas manualmente** no ambiente da AWS.

* **GitHub:** Onde o código é armazenado. Um `push` na branch `main` inicia o processo de validação.
* **GitHub Actions:** A ferramenta de CI que executa um workflow automatizado para **verificar a qualidade do código** (linting) e **validar se as imagens Docker podem ser construídas**, mas não as envia para a AWS.
* **Desenvolvedor (Local):** Após a validação no GitHub Actions passar, o desenvolvedor, de sua máquina local, executa o comando `docker push` para enviar as imagens atualizadas para o ECR.
* **Amazon ECR:** O registro privado onde as novas imagens Docker são armazenadas.
* **AWS App Runner:** O serviço que utiliza a imagem mais recente do ECR para suas implantações (que podem ser iniciadas manualmente ou pela pipeline de retreinamento).

#### 4. Possíveis Dúvidas (FAQ)

* **Por que o fluxo de CI/CD não faz o deploy automático para a AWS (Continuous Deployment)?**
    * **Resposta:** Esta foi uma decisão estratégica para o escopo deste projeto-guia. Como a infraestrutura na AWS é frequentemente desmontada após os estudos, uma pipeline de CD completa falharia a cada novo `commit` por não encontrar os recursos (ECR, App Runner). A implementação, no entanto, seria um próximo passo lógico e envolveria adicionar as credenciais da AWS como *secrets* no GitHub e incluir os comandos `aws ecr get-login-password` e `docker push` no arquivo `.github/workflows/ci-cd.yml`.

* **Por que o frontend não foi hospedado na AWS também?**
    * **Resposta:** A escolha pelo Streamlit Community Cloud foi intencional por dois motivos: 1) Simular um cenário realista onde o cliente (frontend) consome a API a partir de uma rede externa à AWS. 2) Manter o foco do guia na pipeline de MLOps. Hospedar o frontend na AWS exigiria uma nova cadeia de automação (ex: S3 para site estático + CloudFront, ou outro serviço App Runner), o que sairia do escopo principal deste tutorial.

* **A lógica de geração de features parece estar duplicada (no frontend e no job de ETL). Por quê?**
    * **Resposta:** Essa é uma excelente observação e representa uma decisão de arquitetura comum. O **job de ETL** precisa calcular as features em *lote* para todo o dataset histórico durante o treinamento. O **frontend**, por outro lado, precisa calcular as features *em tempo real* para um único confronto, sob demanda. Manter a lógica separada simplifica os dois casos de uso. Uma arquitetura mais complexa poderia utilizar um "Feature Store" centralizado para evitar essa duplicação, mas a abordagem atual é uma solução prática e eficiente para a escala deste projeto.

