from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

BASE_DIR = "/Users/juanzinser/Documents/projects/data-engineering-certificate/etl/airflow/dags/finalassignment"

default_args = {
    'owner': 'Juan',
    'start_date': datetime(2024, 1, 1),
    'email': ['juanzinser@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    schedule=timedelta(days=1),
    description='Apache Airflow Final Assignment',
)

unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command=f'tar -xvzf {BASE_DIR}/tolldata.tgz -C {BASE_DIR}',
    dag=dag,
)

extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command=f'cut -d"," -f1-4 {BASE_DIR}/vehicle-data.csv > {BASE_DIR}/csv_data.csv',
    dag=dag,
)

extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command=f'cut -f5-7 {BASE_DIR}/tollplaza-data.tsv | tr "\t" "," | tr -d "\r" > {BASE_DIR}/tsv_data.csv',
    dag=dag,
)

extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command=f'cut -c59-67 {BASE_DIR}/payment-data.txt | tr " " "," > {BASE_DIR}/fixed_width_data.csv',
    dag=dag,
)

consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command=f'paste -d"," {BASE_DIR}/csv_data.csv {BASE_DIR}/tsv_data.csv {BASE_DIR}/fixed_width_data.csv > {BASE_DIR}/extracted_data.csv',
    dag=dag,
)

transform_data = BashOperator(
    task_id='transform_data',
    bash_command=f'awk -F\',\' \'{{print $1","$2","$3","toupper($4)","$5","$6","$7","$8","$9}}\' < {BASE_DIR}/extracted_data.csv > {BASE_DIR}/transformed_data.csv',
    dag=dag,
)

unzip_data >> [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width] >> consolidate_data >> transform_data