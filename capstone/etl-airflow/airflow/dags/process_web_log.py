from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta, datetime

BASE_PATH = '/Users/juanzinser/Documents/projects/data-engineering-certificate/capstone/etl-airflow/airflow/dags/capstone'

default_args = {
    'owner': 'Juan',
    'email': ['juanzinser@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='process_web_log',
    default_args=default_args,
    description='Final Project of IBM Data Pipelines Using Apache Airflow',
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    extract_data = BashOperator(
        task_id='extract_data',
        bash_command=f'cut -d" " -f1 {BASE_PATH}/accesslog.txt > {BASE_PATH}/extracted-data.txt',
    )

    transform_data = BashOperator(
        task_id='transform_data',
        bash_command=f'grep -v "198.46.149.143" {BASE_PATH}/extracted-data.txt > {BASE_PATH}/transformed_data.txt',
    )

    load_data = BashOperator(
        task_id='load_data',
        bash_command=f'tar cvf {BASE_PATH}/weblog.tar {BASE_PATH}/transformed_data.txt',
    )

    extract_data >> transform_data >> load_data