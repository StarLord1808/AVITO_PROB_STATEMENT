from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, current_timestamp

# Initialize Spark session
spark = SparkSession.builder.appName("MockDataGeneration").getOrCreate()

# Define BigQuery dataset
BQ_PROJECT = "ordinal-reason-449406-f0"
BQ_DATASET = "avito_silver"

# Load searchstream table (contains all UserID, AdID)
searchstream_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.searchstream") \
    .load() \
    .selectExpr("ID as UserID", "AdID", "inserted_at") \
    .distinct()

# Load visitsstream and phonerequestsstream
visits_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.visitsstream") \
    .load() \
    .select("UserID", "AdID", "ViewDate", "inserted_at") \
    .distinct()

phone_requests_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .load() \
    .select("UserID", "AdID", "PhoneRequestDate", "inserted_at") \
    .distinct()

# Find missing UserID-AdID pairs in visitsstream
missing_visits_df = searchstream_df.alias("s") \
    .join(visits_df.alias("v"), ["UserID", "AdID"], "left_anti") \
    .select("UserID", "AdID") \
    .withColumn("ViewDate", expr("current_date() - int(rand() * 10)")) \
    .withColumn("inserted_at", current_timestamp())

# Find missing UserID-AdID pairs in phonerequestsstream
missing_phone_requests_df = searchstream_df.alias("s") \
    .join(phone_requests_df.alias("p"), ["UserID", "AdID"], "left_anti") \
    .select("UserID", "AdID") \
    .withColumn("PhoneRequestDate", expr("current_date() - int(rand() * 5)")) \
    .withColumn("inserted_at", current_timestamp())

# Union missing records with existing ones
updated_visits_df = visits_df.union(missing_visits_df)
updated_phone_requests_df = phone_requests_df.union(missing_phone_requests_df)

# Write back to BigQuery
updated_visits_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.visitsstream") \
    .mode("overwrite") \
    .save()

updated_phone_requests_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .mode("overwrite") \
    .save()

# Stop Spark session
spark.stop()
