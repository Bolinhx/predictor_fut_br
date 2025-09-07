# Dockerfile para os jobs de ML
FROM python:3.11-slim

WORKDIR /app

# Copia apenas os arquivos necessários para os jobs de ML
COPY ml_jobs/requirements-jobs.txt .
COPY ml_jobs/data_processor.py .
COPY ml_jobs/model_trainer.py .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements-jobs.txt

# Por padrão, não executa nada. O Step Functions dirá qual script rodar.
CMD ["--help"]