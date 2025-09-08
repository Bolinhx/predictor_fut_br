import boto3
import sys

def trigger_app_runner_deployment(service_arn):
    """
    Aciona um novo deploy para um serviço App Runner específico.
    """
    print("--- Iniciando o Job de Deploy da API ---") # 'f' removido
    print(f"Acionando deploy para o serviço com ARN: {service_arn}")
    
    try:
        apprunner_client = boto3.client('apprunner')
        response = apprunner_client.start_deployment(ServiceArn=service_arn)
        operation_id = response['OperationId']
        print("Comando de deploy enviado com sucesso!") # 'f' removido
        print(f"ID da Operação: {operation_id}")
        print("Acompanhe o status do deploy no console do App Runner.")
        print("--- Job de Deploy da API Concluído ---")
    except Exception as e:
        print(f"ERRO ao acionar o deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python deploy_api.py <app_runner_service_arn>")
        sys.exit(1)
        
    service_arn = sys.argv[1]
    trigger_app_runner_deployment(service_arn)