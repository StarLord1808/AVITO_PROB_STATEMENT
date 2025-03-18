from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, when
import json

# Load config file
CONFIG_FILE_PATH = "config.json"

with open(CONFIG_FILE_PATH, "r") as config_file:
    config = json.load(config_file)

# Extract Cloud SQL and GCS details from config
MYSQL_HOST = config["mysql"]["host"]
MYSQL_PORT = config["mysql"]["port"]
MYSQL_USER = config["mysql"]["user"]
MYSQL_PASSWORD = config["mysql"]["password"]
MYSQL_DATABASE = config["mysql"]["database"]
GCS_BUCKET = config["gcs"]["error_bucket"]

# MySQL JDBC URL
jdbc_url = f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Define table names
TABLE_VISITS = "VisitsStream"
TABLE_PHONE_REQUESTS = "PhoneRequestsStream"
TABLE_TARGET = "VisitPhoneRequestStream"
print(f"Writing bad records to: gs://{GCS_BUCKET}/BadFiles/")

# Initialize Spark session
spark = SparkSession.builder.appName("Load_VisitPhoneRequestStream").getOrCreate()

# Read VisitsStream from Cloud SQL
try:
    visits_df = spark.read.format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", TABLE_VISITS) \
        .option("user", MYSQL_USER) \
        .option("password", MYSQL_PASSWORD) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load()
except Exception as e:
    error_message = f"Error reading {TABLE_VISITS}: {str(e)}"
    print(error_message)
    spark.createDataFrame([(error_message,)], ["ErrorMessage"]).write.mode("append").csv(f"gs://{GCS_BUCKET}/BadFiles/")
    spark.stop()
    raise

# Read PhoneRequestsStream from Cloud SQL
try:
    phone_requests_df = spark.read.format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", TABLE_PHONE_REQUESTS) \
        .option("user", MYSQL_USER) \
        .option("password", MYSQL_PASSWORD) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load()
except Exception as e:
    error_message = f"Error reading {TABLE_PHONE_REQUESTS}: {str(e)}"
    print(error_message)
    spark.createDataFrame([(error_message,)], ["ErrorMessage"]).write.mode("append").csv(f"gs://{GCS_BUCKET}/BadFiles/")
    spark.stop()
    raise

# Filter out invalid PhoneRequestDate values (1970-01-01 00:00:00)
invalid_date = "1970-01-01 00:00:00"
bad_records_df = phone_requests_df.filter(col("PhoneRequestDate") == invalid_date)

# Save bad records to GCS
if bad_records_df.count() > 0:
    bad_records_df.write.mode("append").csv(f"gs://{GCS_BUCKET}/BadFiles/")

# Replace invalid values with NULL
phone_requests_df = phone_requests_df.withColumn(
    "PhoneRequestDate",
    when(col("PhoneRequestDate") == invalid_date, None).otherwise(col("PhoneRequestDate"))
)

# Perform the join
try:
    joined_df = visits_df.join(
        phone_requests_df,
        ["UserID", "AdID", "IPID"],
        "left_outer"
    ).select(
        col("UserID"),
        col("IPID"),
        col("AdID"),
        col("ViewDate"),
        col("PhoneRequestDate"),
        current_timestamp().alias("inserted_at")  # Only add inserted_at in final table
    )
except Exception as e:
    error_message = f"Error joining tables: {str(e)}"
    print(error_message)
    spark.createDataFrame([(error_message,)], ["ErrorMessage"]).write.mode("append").csv(f"gs://{GCS_BUCKET}/BadFiles/")
    spark.stop()
    raise

# Write to Cloud SQL
try:
    joined_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", TABLE_TARGET) \
        .option("user", MYSQL_USER) \
        .option("password", MYSQL_PASSWORD) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .mode("append") \
        .save()
    print("Data successfully loaded into Cloud SQL.")
except Exception as e:
    error_message = f"Error writing to {TABLE_TARGET}: {str(e)}"
    print(error_message)
    spark.createDataFrame([(error_message,)], ["ErrorMessage"]).write.mode("append").csv(f"gs://{GCS_BUCKET}/BadFiles/")
    spark.stop()
    raise

# Stop Spark session
spark.stop()
