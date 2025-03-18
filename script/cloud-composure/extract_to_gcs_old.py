from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_sql import CloudSQLExecuteQueryOperator
from airflow.providers.google.cloud.hooks.cloud_sql import CloudSQLDatabaseHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
from io import BytesIO
import logging  # <-- Added logging for execution status

# Cloud SQL Connection Info (Set in Airflow UI > Connections)
CLOUD_SQL_CONN_ID = "cloud_sql_mysql"
GCS_BUCKET = "avito-bronze-bucket-central1"

# List of tables to export
TABLES = [
    "AdsInfo",
    "Category",
    "Location",
    "PhoneRequestsStream",
    "SearchInfo",
    "SearchStream",
    "UserInfo",
    "VisitPhoneRequestStream",
    "VisitsStream"
]

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 2,
}

def export_table_to_gcs(table_name, **kwargs):
    """Extracts data from Cloud SQL, converts it to JSON/Parquet, and uploads to GCS."""
    logging.info(f"🚀 Starting export for table: {table_name}")  # Log start

    try:
        sql_hook = CloudSQLDatabaseHook(gcp_cloudsql_conn_id=CLOUD_SQL_CONN_ID)
        gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

        # Execute SQL Query
        records = sql_hook.get_pandas_df(f"SELECT * FROM {table_name};")
        logging.info(f"✅ Successfully retrieved {len(records)} records from {table_name}")

        if records.empty:
            raise ValueError(f"❌ No data found for table: {table_name}")

        # Convert to JSON and save
        json_buffer = BytesIO()
        records.to_json(json_buffer, orient="records", lines=True)
        gcs_hook.upload(bucket_name=GCS_BUCKET, object_name=f"exports/{table_name}.json", data=json_buffer.getvalue())
        logging.info(f"✅ JSON export completed for {table_name}")

        # Convert to Parquet and save
        parquet_buffer = BytesIO()
        records.to_parquet(parquet_buffer, engine="pyarrow", index=False)
        gcs_hook.upload(bucket_name=GCS_BUCKET, object_name=f"exports/{table_name}.parquet", data=parquet_buffer.getvalue())
        logging.info(f"✅ Parquet export completed for {table_name}")

        return f"🎯 Exported {table_name} to GCS successfully."

    except Exception as e:
        logging.error(f"🔥 ERROR exporting {table_name}: {str(e)}", exc_info=True)
        raise  # Re-raise the exception so Airflow marks it as failed

with DAG(
    "export_cloudsql_to_gcs",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    for table in TABLES:
        extract_and_upload = PythonOperator(
            task_id=f"extract_{table}_to_gcs",
            python_callable=export_table_to_gcs,
            provide_context=True,
            op_kwargs={"table_name": table},
        )
