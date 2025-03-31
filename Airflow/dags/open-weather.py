# Pipeline ETL no Airflow Para Carga de Dados na AWS

# Imports
import os
import boto3  #conectar via Python na AWS
import requests #extrair dados da API
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Definição dos argumentos para a DAG
default_args = {
    "owner": "Silmara Basso",
    "depends_on_past": False,
    "start_date": datetime(2024, 5, 3),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Criação da DAG com o intervalo de agendamento especificado
sil_dag = DAG(
    "Weather-AWS",
    default_args=default_args,
    schedule_interval="* * * * *",  # Este agendamento deve ser ajustado conforme necessário
    catchup=False
)

# No formato de cron (cron expression), "* * * * *" significa que a DAG será executada a cada minuto. 

# Cada asterisco representa:

# Primeiro *: Minuto (0-59)
# Segundo *: Hora (0-23)
# Terceiro *: Dia do mês (1-31)
# Quarto *: Mês (1-12)
# Quinto *: Dia da semana (0-6, onde 0 é Domingo)

# Função para extrair dados da API
def extrai_dados():

    # Definição da URL base e da chave da API 
    URL_BASE = "https://api.openweathermap.org/data/2.5/weather?" # http://api.openweathermap.org/
    API_KEY = "minha_key"
    CIDADE = "Curitiba"

    # Construção da URL completa para a requisição
    url = f"{URL_BASE}q={CIDADE}&appid={API_KEY}"

    # Realiza a requisição e retorna a resposta em formato JSON
    response = requests.get(url).json()
    return response

# Função para transformar os dados extraídos
def transforma_dados(response):

    # Extrai e formata os dados de interesse utcfromtimestamp -> timezone-aware
    dados_tempo = {
        "date": datetime.utcfromtimestamp(response['dt']).strftime('%Y-%m-%d'),
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "weather": response['weather'][0]['description']
    }
    
    # Cria uma string formatada com os dados do tempo
    dados_transformados = f"Em {dados_tempo['date']}, o tempo será < {dados_tempo['weather']} > com temperatura de {dados_tempo['temperature']}°C."
    return dados_transformados

# Função para carregar os dados transformados
def carrega_dados(dados_transformados):

    # Configura as credenciais da AWS
    os.environ['AWS_ACCESS_KEY_ID'] = 'coloque-aqui-sua-api-key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'coloque-aqui-sua-api-key'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'

    # Gera um timestamp único para o nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    local_file_path = f'/opt/airflow/dags/dados_previsao_tempo_{timestamp}.txt'

    # Salva os dados transformados em um arquivo local
    with open(local_file_path, 'w') as file:
        file.write(f"Aqui está a previsão do tempo para a cidade escolhida:\n")
        file.write(dados_transformados + '\n')

    # Faz o upload do arquivo para um bucket S3
    # Substitua pelo nome do seu bucket S3
    s3_bucket = "nome-bucket-s3"  
    s3_key = f"dados_previsao_tempo_{timestamp}.txt"

    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path, s3_bucket, s3_key)

# Define a tarefa para extrair dados
tarefa_extrai_dados = PythonOperator(task_id = 'extraindo_dados',
                                     python_callable = extrai_dados,
                                     dag = sil_dag)

# Define a tarefa para transformar dados que recebe como entrada o output da tarefa_transforma_dados
tarefa_transforma_dados = PythonOperator(task_id = 'transformando_dados',
                                         python_callable = transforma_dados,
                                         op_args = [tarefa_extrai_dados.output],
                                         dag = sil_dag)

# Define a tarefa para carregar dados
tarefa_carrega_dados = PythonOperator(task_id = 'carregando_dados',
                                      python_callable = carrega_dados,
                                      op_args = [tarefa_transforma_dados.output],
                                      dag = sil_dag)

# Define a sequência das tarefas
tarefa_extrai_dados >> tarefa_transforma_dados >> tarefa_carrega_dados

# Resumo:

# Bloco de Imports: Importação das bibliotecas necessárias para o DAG.
# default_args: Definição dos argumentos padrão para o DAG.
# sil_dag: Criação do DAG com o intervalo de agendamento especificado.
# extrai_dados: Função que extrai dados da API.
# transforma_dados: Função que transforma os dados extraídos.
# carrega_dados: Função que carrega os dados transformados para um arquivo local e faz upload para o S3.
# tarefa_extrai_dados: Definição da tarefa para extrair dados.
# tarefa_transforma_dados: Definição da tarefa para transformar dados.
# tarefa_carrega_dados: Definição da tarefa para carregar dados.
# Sequência das Tarefas: Define a ordem de execução das tarefas no DAG.
