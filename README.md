# Predictor Fut BR: Guia de Implementação de Pipeline MLOps na AWS

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

## 📖 Introdução

Este repositório é mais do que um projeto de Machine Learning; é um **guia prático e completo** para quem deseja construir uma pipeline (nesse caso de Machine Learning) de ponta a ponta na AWS. Ele foi projetado para ser o mais **"Plug-and-Play"** possível, fornecendo uma base de código sólida para que você não precise se precupar com o codigo/produto em si e possa focar em aprender e implementar a arquitetura na AWS.

A intenção é preencher uma lacuna comum em tutoriais, oferecendo um projeto que integra múltiplos serviços da AWS de forma coesa, incluindo processamento de dados, treinamento de modelo, deploy de API, orquestração de eventos e uma interface para o usuário final.

---

## 🧭 A Jornada do Projeto

Este projeto nasceu de uma jornada de aprendizado pessoal e evoluiu para um recurso para a comunidade.

### Fase 1: A Prova de Conceito Local ([v1.0](https://github.com/bolinhx/predictor_fut_br/releases/tag/v1.0))
O projeto começou como um desafio pessoal: construir um sistema preditivo completo, passando por todas as etapas clássicas: Análise Exploratória de Dados (EDA), Engenharia de Features, treinamento de um modelo de Machine Learning e a criação de uma API RESTful em Docker.

Uma particularidade desta fase foi a utilização de uma IA Generativa como agente de desenvolvimento, com o objetivo de praticar a revisão e depuração de código gerado por IA – um fluxo de trabalho cada vez mais comum. O resultado foi uma aplicação funcional, porém estática, que validou a lógica do modelo e da API.

### Fase 2: A Evolução para MLOps na Nuvem ([v2.0](https://github.com/Bolinhx/predictor_fut_br/releases/tag/v2.0))
Após a validação do protótipo, o desafio evoluiu: como transformar uma aplicação local em um sistema de produção resiliente, escalável e que se atualiza sozinho? Foi aí que nasceu a ideia de migrar tudo para a AWS e, mais importante, documentar cada passo para criar um guia para a comunidade. Esta versão implementa uma arquitetura serverless completa, com uma pipeline de retreinamento totalmente automatizada.

### Fase 2.1: A Transformação em um Guia para a Comunidade(v2.1)
Após a finalização da arquitetura V2.0, o projeto tomou um novo rumo: transformar todo o conhecimento adquirido em um recurso de aprendizado. Esta fase focou em refatorar o código para ser mais didático, introduzindo um arquivo `.env` para facilitar a configuração, e na criação de um guia de implementação detalhado para que outras pessoas pudessem recriar a solução, aprendendo com os desafios e soluções encontradas.

## 🏛️ Arquitetura da Solução

![predictor_archtecture](https://github.com/user-attachments/assets/97ba478b-c136-4adc-9107-701c1dc780ae)


➡️ **[Acesse a Legenda Detalhada da Arquitetura aqui!](./LEGENDA_ARQUITETURA.md)**

---

## 🎯 Para Quem é Este Guia?

* **Estudantes e Desenvolvedores Iniciantes em Nuvem:** Para quem busca um projeto prático e completo na AWS que vai além dos tutoriais básicos, integrando contêineres, eventos e serviços de ML.
* **Profissionais em Transição:** Para quem já entende os conceitos de nuvem, mas precisa de um projeto coeso e realista para aplicar e solidificar seus conhecimentos.
* **Candidatos a Certificações AWS:** Para quem está estudando para a certificação **Solutions Architect - Associate** e quer uma experiência prática que cubra múltiplos domínios do exame.

---

## 🛠️ O Que Você Vai Construir

Seguindo o guia, você irá provisionar e configurar uma arquitetura completa na AWS, composta por:
* Um **Data Lake** no Amazon S3.
* Uma **API de previsão** serverless rodando no AWS App Runner.
* **Jobs de ETL e Treinamento** em contêineres executados sob demanda com AWS Fargate.
* Uma **pipeline de orquestração** inteligente com AWS Step Functions.
* Um **gatilho automático** baseado em eventos com Amazon EventBridge.
* Uma **interface web interativa** para o usuário final com Streamlit.

---

## ✅ Habilidades para a Certificação AWS Solutions Architect - Associate

Este projeto fornece experiência prática em conceitos cobrados em todos os domínios da prova SAA-C03:

- **[x] Domain 1: Design Secure Architectures**
  - Implementação de **IAM Roles** com o princípio do menor privilégio (`ECSTaskRole`, `AppRunnerInstanceRole`, `StepFunctionsRole`).
  - Uso de políticas customizadas e gerenciadas.
  - Configuração de buckets **S3** privados.

- **[x] Domain 2: Design Resilient Architectures**
  - Construção de uma **arquitetura desacoplada** e orientada a eventos com **EventBridge** e **Step Functions**.
  - Utilização de serviços gerenciados e serverless (**App Runner**, **Fargate**) que aumentam a resiliência.

- **[x] Domain 3: Design High-Performing Architectures**
  - Seleção de serviços de computação adequados para cada tarefa (App Runner para serviços web, Fargate para jobs em lote).
  - Utilização do **S3** como uma camada de armazenamento performática.

- **[x] Domain 4: Design Cost-Optimized Architectures**
  - Adoção de uma abordagem **serverless-first**, onde você só paga pelos recursos quando eles estão em uso, minimizando custos ociosos.
  - Estratégia de "pausar" serviços como o App Runner para controlar os custos de desenvolvimento.

---

## 💡 Dicas Importantes para o Sucesso

Antes de mergulhar na implementação, leia estas dicas. Elas foram aprendidas durante a construção deste projeto e podem economizar muito tempo e frustração.

* **Foco na Nuvem, não no Machine Learning!**
    Mesmo que seu objetivo não seja aprender Machine Learning, este projeto é um excelente exercício de AWS. As práticas de automação, orquestração com Step Functions, deploy de contêineres e gerenciamento de permissões com IAM são universais e se aplicam a quase qualquer área de desenvolvimento na nuvem. Você não precisa entender a lógica por trás do modelo para implementar a arquitetura com sucesso.

* **Um Passo de Cada Vez.**
    A tentação de construir tudo de uma vez é grande, mas a chave para o sucesso na nuvem é a iteração. Siga o guia fase por fase. Após cada etapa importante (ex: criar uma IAM Role, subir uma imagem Docker), **teste e valide** que aquele componente está funcionando antes de seguir para o próximo. Isso torna a depuração infinitamente mais fácil.

* **Abrace a Depuração.**
    Você vai encontrar erros. Permissões que faltam, nomes incorretos, timeouts. Isso não é um sinal de falha, mas sim a **parte mais importante do aprendizado**. Use os logs da AWS (CloudWatch, os logs de deploy do App Runner, os logs da tarefa no ECS) como suas ferramentas de detetive. Cada erro resolvido é um conhecimento consolidado.

* **⚠️ Gerenciamento de Custos é SUA Responsabilidade!**
    Este projeto foi projetado para ter um custo próximo de zero se for implementado em um curto período e os recursos forem devidamente limpos depois. O autor original, por exemplo, implementou tudo em um domingo sem incorrer em custos significativos. No entanto, **não deixe os serviços rodando indefinidamente**, pois isso **VAI** gerar custos inesperados.
    * **PAUSE O APP RUNNER:** Sempre que não estiver usando ativamente a API, vá ao console do App Runner e **pause** o serviço.
    * **LIMPE TUDO:** Ao finalizar os estudos, siga rigorosamente a **Fase 5** do guia de implementação para deletar todos os recursos. O autor deste guia não se responsabiliza por quaisquer cobranças geradas na sua conta AWS.

---

## 🚀 Como Começar

Tudo o que você precisa para colocar a mão na massa está no nosso manual detalhado.

➡️ **[Acesse o Guia de Implementação Completo aqui!](./IMPLEMENTATION_GUIDE.md)**

---

## 💬 Uma Nota Sobre Erros

Quase todos os erros documentados na seção "Solução de Problemas" do guia de implementação foram problemas reais encontrados durante a construção deste projeto. Se você encontrar um obstáculo diferente, não desista e nem desespere! A depuração na nuvem é uma habilidade fundamental e e onde passamos mais tempo haha, tentei prever a maioria dos erros mas sabemos como as coisas são... vão ter outros erros. Use as ferramentas de log da AWS, consulte uma IA e, se encontrar algo novo, sinta-se à vontade para abrir uma *issue* ou me contatar. Sua contribuição pode enriquecer ainda mais este guia!
