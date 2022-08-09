
from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
with DAG(
    'admin_media_report',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Admin reports DAG',
    schedule_interval='@daily',
    start_date=datetime(2021, 1, 1),
    catchup=False
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    report_status = BashOperator(
        task_id='report_status',
        bash_command='python ~/airflow/dependencies/admin-media-report/report-staus.py',
    )
    report_status.doc_md = dedent('''
        # Admin status report e-mail
        this generates a simple report showing the percentages by media type, codec, etc.
    ''')

    report_status