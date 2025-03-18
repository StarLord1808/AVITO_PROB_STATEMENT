from pyspark.sql import SparkSession
from datetime import datetime

# GCP Config
PROJECT_ID = "ordinal-reason-449406-f0"
DATASET_ID = "avito_silver"
GCS_BUCKET = "gs://avito-silver-bucket-central1"
TEMP_BUCKET = "avito-silver-bucket-central1/temp"

# JAR Path
BIGQUERY_JAR = "gs://avito-silver-bucket-central1/jars/spark-bigquery-with-dependencies_2.12-0.36.1.jar"

# Tables to Export
TABLES = [
    "visitsstream", "adsinfo", "Location_Enriched", "userinfo", "phonerequestsstream",
    "searchstream", "device_user_profile", "location", "searchstream_enriched",
    "UserInfo_Synthetic", "user_interactions"
]

print("🟢 Spark Session Initializing...")

# Initialize Spark Session with Correct JAR Loading
spark = SparkSession.builder \
    .appName("BigQuery-to-GCS") \
    .config("spark.jars", BIGQUERY_JAR) \
    .config("spark.driver.extraClassPath", "/usr/lib/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/usr/lib/spark/jars/*") \
    .getOrCreate()

for table in TABLES:
    try:
        print(f"🚀 Exporting table: {table}")

        # Load table from BigQuery
        df = spark.read.format("bigquery") \
            .option("temporaryGcsBucket", TEMP_BUCKET) \
            .option("project", PROJECT_ID) \
            .option("dataset", DATASET_ID) \
            .option("table", table) \
            .load()

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"{GCS_BUCKET}/export/parquet/{table}/"
        output_file = f"{output_path}{table}-{timestamp}.snappy.parquet"

        # Write as a single file
        df.coalesce(1).write.mode("overwrite").parquet(output_path)

        # Rename the generated part file
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET.replace("gs://", ""))
        blobs = list(bucket.list_blobs(prefix=f"export/parquet/{table}/"))

        for blob in blobs:
            if "part-" in blob.name:  # Identify the generated part file
                bucket.rename_blob(blob, f"export/parquet/{table}/{table}-{timestamp}.snappy.parquet")
                print(f"✅ Renamed {blob.name} to {table}-{timestamp}.snappy.parquet")
                break

    except Exception as e:
        print(f"🔥 Error exporting table {table}: {e}")

spark.stop()
print("🎉 Export completed.")
