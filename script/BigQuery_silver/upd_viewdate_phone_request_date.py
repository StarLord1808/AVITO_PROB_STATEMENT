from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, rand, current_timestamp, lit, from_unixtime, floor

# Initialize Spark session
spark = SparkSession.builder.appName("UpdateRandomTimestamps").getOrCreate()
print("Spark session started!")

# Define BigQuery dataset and table names
BQ_PROJECT = "ordinal-reason-449406-f0"
BQ_DATASET = "avito_silver"

# Load phonerequestsstream data from BigQuery
phone_requests_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .load()

# Load visitsstream data from BigQuery
visits_stream_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.visitsstream") \
    .load()

print("Data loaded from BigQuery!")

# Generate a random timestamp within the last 3 years
three_years_seconds = 3 * 365 * 24 * 60 * 60  # Total seconds in 3 years

updated_phone_requests_df = phone_requests_df.withColumn(
    "PhoneRequestDate",
    from_unixtime(
        lit(1609459200) + floor(rand() * three_years_seconds)  # Random timestamp from 2021-01-01
    )
)

updated_visits_stream_df = visits_stream_df.withColumn(
    "ViewDate",
    from_unixtime(
        lit(1609459200) + floor(rand() * three_years_seconds)  # Random timestamp from 2021-01-01
    )
)

print("Random timestamps assigned successfully!")

# Write the updated phonerequestsstream data back to BigQuery
updated_phone_requests_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .mode("overwrite") \
    .save()

# Write the updated visitsstream data back to BigQuery
updated_visits_stream_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.visitsstream") \
    .mode("overwrite") \
    .save()

print("Timestamps updated and saved to BigQuery!")

# Stop Spark session
spark.stop()
print("Spark session stopped.")
