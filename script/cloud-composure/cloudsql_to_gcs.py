from pyspark.sql import SparkSession
import os
import sys
import subprocess

# Install missing dependencies
subprocess.run(["pip", "install", "mysql-connector-python", "google-cloud-secret-manager"], check=True)

from google.cloud import secretmanager  # Now this should work
import mysql.connector  # MySQL connection
from pyspark.sql.utils import AnalysisException

# Install MySQL Connector at runtime
try:
    import mysql.connector
except ModuleNotFoundError:
    print("⚠️ 'mysql-connector-python' not found. Installing it now...")
    os.system("pip install mysql-connector-python")
    import mysql.connector

# GCP Project and Secret Name
PROJECT_ID = "ordinal-reason-449406-f0"
SECRET_ID = "mysql_credential"

# Cloud SQL Database Details
CLOUDSQL_INSTANCE_IP = "35.239.147.18"
CLOUDSQL_PORT = "3306"
DATABASE_NAME = "avito_db"

# GCS Bucket
GCS_BUCKET = "gs://avito-bronze-bucket-central1"

# Tables to Extract
TABLES = [
    "AdsInfo", "Category", "Location", "PhoneRequestsStream", "SearchInfo", "SearchStream", "UserInfo", "VisitPhoneRequestStream", "VisitsStream"
]

def get_mysql_credentials():
    """Fetches MySQL credentials from Google Secret Manager."""
    try:
        # client = secretmanager.SecretManagerServiceClient()
        # secret_name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
        # response = client.access_secret_version(request={"name": secret_name})
        # secret_value = response.payload.data.decode("UTF-8")
        mysql_user = "thiru"
        mysql_password = "thiru"
        return mysql_user, mysql_password
    except Exception as e:
        print(f"🔥 Error fetching credentials: {e}")
        sys.exit(1)

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("CloudSQL-to-GCS") \
        .config("spark.jars", "/usr/lib/spark/jars/mysql-connector-java-8.0.33.jar") \
        .getOrCreate()

    # Fetch MySQL credentials
    mysql_user, mysql_password = get_mysql_credentials()
    
    for table in TABLES:
        try:
            print(f"🚀 Starting export for table: {table}")

            # Read Data from MySQL
            df = spark.read.format("jdbc") \
                .option("url", f"jdbc:mysql://{CLOUDSQL_INSTANCE_IP}:{CLOUDSQL_PORT}/{DATABASE_NAME}") \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .option("dbtable", table) \
                .option("user", mysql_user) \
                .option("password", mysql_password) \
                .load()
            
            print(f"✅ Successfully loaded {table} from Cloud SQL.")

            # Save to GCS in Parquet format
            output_path = f"{GCS_BUCKET}/{table}/"
            df.write.mode("overwrite").parquet(output_path)

            print(f"📁 Table {table} exported to {output_path}")

        except AnalysisException as e:
            print(f"⚠️ Table {table} does not exist in MySQL: {e}")
        except Exception as e:
            print(f"🔥 Error processing table {table}: {e}")

    spark.stop()
    print("🎉 Export process completed successfully.")

if __name__ == "__main__":
    main()
