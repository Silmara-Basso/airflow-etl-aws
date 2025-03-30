# airflow-etl-aws
Pipeline de ETL (Extração, Transformação  e Carga) utilizando o Apache Airflow para processar dados em tempo real e carregá-los na AWS


# Para instalar e executar o Apache Airflow siga os passos abaixo:

Execute o comando abaixo na pasta onde esta o docker-compose do Airflow para criar as imagens Docker e inicializar o banco de dados:

`docker compose up airflow-init`

Execute o comando abaixo para inicializar o Airflow:

`docker compose up`

Abra o navegador e efetue login. 

http://localhost:8080/login

User: airflow
Senha: airflow

Obs: Se você tiver o PostgreSQL instalado na sua máquina rodando na porta 5432 desligue-o ou haverá conflito de portas impedindo a inicialização do Airflow.

# Busque pelo arquivo do docker compose mais recente no link abaixo:

https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html


# DAG
Copie o arquivo open-wather.py para dentro da pasta dags