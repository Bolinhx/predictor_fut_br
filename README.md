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

_WIP diagrama da arquitetura_

➡️ **[Acesse a Legenda Detalhada da Arquitetura aqui!](./ARCHITECTURE_LEGEND.md)**

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

## 🚀 Como Começar

Tudo o que você precisa para colocar a mão na massa está no nosso manual detalhado.

➡️ **[Acesse o Guia de Implementação Completo aqui!](./IMPLEMENTATION_GUIDE.md)**

---

## 💬 Uma Nota Sobre Erros

Quase todos os erros documentados na seção "Solução de Problemas" do guia de implementação foram problemas reais encontrados durante a construção deste projeto. Se você encontrar um obstáculo diferente, não desista e nem desespere! A depuração na nuvem é uma habilidade fundamental e e onde passamos mais tempo haha, tentei prever a maioria dos erros mas sabemos como as coisas são... vão ter outros erros. Use as ferramentas de log da AWS, consulte uma IA e, se encontrar algo novo, sinta-se à vontade para abrir uma *issue* ou me contatar. Sua contribuição pode enriquecer ainda mais este guia!