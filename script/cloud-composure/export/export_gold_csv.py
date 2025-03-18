from pyspark.sql import SparkSession
from google.cloud import storage
from datetime import datetime

# GCP Config
PROJECT_ID = "ordinal-reason-449406-f0"
DATASET_ID = "avito_gold"
GCS_BUCKET_NAME = "avito-gold-bucket-central1"
GCS_BUCKET = f"gs://{GCS_BUCKET_NAME}"
TEMP_BUCKET = f"{GCS_BUCKET_NAME}/temp"

# JAR Path
BIGQUERY_JAR = f"{GCS_BUCKET}/jars/spark-bigquery-with-dependencies_2.12-0.36.1.jar"

# Tables to Export
TABLES = ["click_through_rate", "ad_performance_by_region_category", "device_usage_analytics",
          "revenue_by_category_region", "user_engagement_analysis", "user_profile_enriched"
]

print("🟢 Spark Session Initializing...")

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("BigQuery-to-GCS") \
    .config("spark.jars", BIGQUERY_JAR) \
    .config("spark.driver.extraClassPath", "/usr/lib/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/usr/lib/spark/jars/*") \
    .getOrCreate()

# Initialize GCS Client
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

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

        if df.count() == 0:
            print(f"⚠️ Warning: Table {table} is empty")
            continue

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"{GCS_BUCKET}/export/csv/{table}/"
        final_filename = f"{table}-{timestamp}.csv"

        # Write as a single CSV file
        df.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .option("encoding", "UTF-8") \
            .option("quoteAll", "true") \
            .option("sep", ",") \
            .csv(output_path)

        # Rename the generated part file
        blobs = list(bucket.list_blobs(prefix=f"export/csv/{table}/"))

        for blob in blobs:
            if "part-" in blob.name and blob.name.endswith(".csv"):
                new_blob = bucket.rename_blob(blob, f"export/csv/{table}/{final_filename}")
                print(f"✅ Renamed {blob.name} to {final_filename}")
                break

    except Exception as e:
        print(f"🔥 Error exporting table {table}: {str(e)}")
        continue

spark.stop()
print("🎉 Export completed.")
