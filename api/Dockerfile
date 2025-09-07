# api/Dockerfile
FROM python:3.11-slim

WORKDIR /code

# Adicionamos boto3 ao requirements.txt, então ele será instalado aqui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/

EXPOSE 80

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]