from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("UserInteractionNormalization").getOrCreate()
print("Spark session started!")

# Define BigQuery dataset
BQ_PROJECT = "ordinal-reason-449406-f0"
BQ_DATASET = "avito_silver"

# Load tables from BigQuery
search_stream_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.searchstream") \
    .load()

visits_stream_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.visitsstream") \
    .load()

phone_requests_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .load()

print("Data loaded from BigQuery!")

# ✅ Rename columns for clarity
search_stream_df = search_stream_df.withColumnRenamed("ID", "UserID")

# ✅ Join on correct columns
normalized_df = search_stream_df.alias("s") \
    .join(visits_stream_df.alias("v"), ["UserID", "AdID"], "left") \
    .join(phone_requests_df.alias("p"), ["UserID", "AdID"], "left") \
    .select(
        col("s.UserID"),
        col("s.AdID"),
        col("s.SearchID"),
        col("s.inserted_at").alias("SearchDate"),
        col("v.ViewDate"),
        col("v.inserted_at").alias("ViewTimestamp"),
        col("p.PhoneRequestDate"),
        col("p.inserted_at").alias("PhoneRequestTimestamp")
    )

# Fill missing values
# normalized_df = normalized_df.fillna({"PhoneRequestDate": None})
normalized_df = normalized_df.fillna({"PhoneRequestDate": ""})


print("User Interaction Normalization completed successfully!")

# Save normalized data back to BigQuery
normalized_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.user_interactions") \
    .mode("overwrite") \
    .save()

print("Normalized data saved to BigQuery!")

# Stop Spark session
spark.stop()
print("Spark session stopped.")
