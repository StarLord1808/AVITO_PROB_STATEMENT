from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.utils.dates import days_ago
import datetime

# DAG Config
DAG_NAME = "export_silver_bq_to_gcs_CSV"
PROJECT_ID = "ordinal-reason-449406-f0"
REGION = "us-central1"
CLUSTER_NAME = "avito-dataproc"
BUCKET_NAME = "avito-silver-bucket-central1"

# PySpark Job Config
PYSPARK_FILE = f"gs://{BUCKET_NAME}/scripts/export_silver_csv.py"
BIGQUERY_JAR = f"gs://{BUCKET_NAME}/jars/spark-bigquery-with-dependencies_2.12-0.36.1.jar"

PYSPARK_JOB = {
    "reference": {"job_id": f"{DAG_NAME}-job-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": PYSPARK_FILE,
        "jar_file_uris": [BIGQUERY_JAR],  # ✅ Include BigQuery Connector JAR
    },
}

# DAG Definition
with DAG(
    DAG_NAME,
    default_args={
        "owner": "airflow",
        "start_date": days_ago(1),
        "retries": 3,
        "retry_delay": datetime.timedelta(minutes=5),
    },
    schedule_interval="@daily",
    catchup=False,
) as dag:

    submit_pyspark_job = DataprocSubmitJobOperator(
        task_id="submit_pyspark_job",
        project_id=PROJECT_ID,
        region=REGION,
        job=PYSPARK_JOB,
        dag=dag,
    )

    submit_pyspark_job
