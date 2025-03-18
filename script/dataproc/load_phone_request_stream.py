from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_timestamp, when
import pymysql
import pandas as pd
from google.cloud import storage
from io import StringIO

# Initialize Spark session
spark = SparkSession.builder.appName("GCS-to-CloudSQL-PhoneRequests").getOrCreate()

# Cloud Storage and Cloud SQL details
GCS_BUCKET = "avito-landing-bucket-central1"
GCS_FILE = "PhoneRequestsStream.csv"
ERROR_FILE = f"error_{GCS_FILE}"
gcs_path = f"gs://{GCS_BUCKET}/{GCS_FILE}"
error_gcs_path = f"gs://{GCS_BUCKET}/{ERROR_FILE}"

# MySQL credentials
db_user = "thiru"
db_password = "thiru"
db_name = "avito_db"
db_host = "35.239.147.18"

# ✅ Load data from GCS
def load_data_from_gcs():
    try:
        df = spark.read.option("header", "true").csv(gcs_path)
        print(f"Successfully loaded data from GCS: {gcs_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading data from GCS: {str(e)}")
        return None

# ✅ Fix `PhoneRequestDate` column
def clean_data(df):
    # Convert column names to lowercase
    df = df.toDF(*[c.lower() for c in df.columns])

    # Check if required columns exist
    required_columns = ["userid", "ipid", "adid", "phonerequestdate"]
    for col_name in required_columns:
        if col_name not in df.columns:
            print(f"❌ Missing column: {col_name}. Aborting!")
            return None

    # ✅ Convert `PhoneRequestDate` from HH:MM.S format to proper timestamp
    df = df.withColumn(
        "phonerequestdate",
        when((col("phonerequestdate").isNull()) | (col("phonerequestdate") == ""), None)
        .otherwise(to_timestamp(col("phonerequestdate"), "HH:mm.s"))
    )

    # ✅ Ensure MySQL gets `NULL` for missing values instead of '1970-01-01 00:00:00'
    df = df.withColumn("inserted_at", current_timestamp())

    return df

# ✅ Write to MySQL
def write_to_mysql(df):
    try:
        pdf = df.toPandas()

        conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO PhoneRequestsStream (UserID, IPID, AdID, PhoneRequestDate, inserted_at)
        VALUES (%s, %s, %s, %s, %s)
        """

        error_rows = []

        for _, row in pdf.iterrows():
            try:
                cursor.execute(insert_sql, (
                    row["userid"],
                    row["ipid"],
                    row["adid"],
                    None if pd.isna(row["phonerequestdate"]) else row["phonerequestdate"],
                    row["inserted_at"]
                ))
            except Exception as e:
                print(f"⚠️ Error inserting record {row['userid']}: {str(e)}")
                error_rows.append(row)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Successfully loaded {len(pdf) - len(error_rows)} records.")

        if error_rows:
            error_df = pd.DataFrame(error_rows)
            save_error_records(error_df)

    except Exception as e:
        print(f"❌ Error writing to MySQL: {str(e)}")

# ✅ Save error records
def save_error_records(error_df):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(ERROR_FILE)

        csv_buffer = StringIO()
        error_df.to_csv(csv_buffer, index=False)
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

        print(f"🚨 Error records saved to GCS: {error_gcs_path}")
    except Exception as e:
        print(f"❌ Error saving error records: {str(e)}")

# ✅ Execute
if __name__ == "__main__":
    df = load_data_from_gcs()
    if df is not None:
        cleaned_df = clean_data(df)
        if cleaned_df is not None:
            write_to_mysql(cleaned_df)
