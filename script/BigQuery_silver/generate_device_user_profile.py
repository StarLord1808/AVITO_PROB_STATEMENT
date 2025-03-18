from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("DeviceUserProfile").getOrCreate()
print("✅ Spark session initialized!")
# Define BigQuery dataset
BQ_PROJECT = "ordinal-reason-449406-f0"
BQ_DATASET = "avito_silver"

# Load UserInfo table
userinfo_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.userinfo") \
    .load() \
    .select("UserID", "UserDeviceID")
print("✅ UserInfo table loaded!")
# Load SearchStream table
searchstream_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.searchstream") \
    .load() \
    .select("ID", "SearchID", "AdID", "inserted_at")
print   ("✅ SearchStream table loaded!")
# Load PhoneRequestsStream table
phonerequests_df = spark.read.format("bigquery") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.phonerequestsstream") \
    .load() \
    .select("UserID", "AdID", "PhoneRequestDate", "inserted_at")
print("✅ PhoneRequestsStream table loaded!")
# Join UserInfo with SearchStream on UserID
device_user_profile_df = searchstream_df.alias("s") \
    .join(userinfo_df.alias("u"), col("s.ID") == col("u.UserID"), "left") \
    .select(col("u.UserID"), col("u.UserDeviceID"), col("s.SearchID"), col("s.AdID"), col("s.inserted_at"))
print("✅ Joined UserInfo with SearchStream!")
# Join with PhoneRequestsStream to capture phone interactions
device_user_profile_df = device_user_profile_df.alias("d") \
    .join(phonerequests_df.alias("p"), ["UserID", "AdID"], "left") \
    .select(col("d.UserID"), col("d.UserDeviceID"), col("d.SearchID"),
            col("d.AdID"), col("p.PhoneRequestDate"), col("d.inserted_at"))
print("✅ Joined with PhoneRequestsStream!")
# Write to BigQuery
device_user_profile_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", f"{BQ_PROJECT}.{BQ_DATASET}.device_user_profile") \
    .mode("overwrite") \
    .save()
print("✅ Data written to BigQuery!")
# Stop Spark session
spark.stop()
