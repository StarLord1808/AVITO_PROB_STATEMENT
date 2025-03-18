from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from faker import Faker
import random

# Initialize Spark session
spark = SparkSession.builder.appName("GenerateSyntheticUsers").getOrCreate()
print("✅ Spark session started!")

# Load UserInfo table from BigQuery
user_info_df = spark.read.format("bigquery").option("table", "ordinal-reason-449406-f0.avito_silver.userinfo").load()
print("✅ UserInfo table loaded from BigQuery!")

# Initialize Faker
faker = Faker()

# Define valid phone number format
def generate_valid_phone():
    country_code = random.choice(["+1", "+44", "+91", "+33", "+49"])  # USA, UK, India, France, Germany
    return f"{country_code} {random.randint(600, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

# Define UDFs for synthetic data generation
fake_name = udf(lambda: faker.name(), StringType())
fake_email = udf(lambda: faker.email(), StringType())
fake_phone = udf(generate_valid_phone, StringType())  # Uses custom valid phone number generator
fake_address = udf(lambda: faker.address(), StringType())

print("✅ UDFs defined for synthetic data generation!")

# Generate synthetic user details
synthetic_users_df = user_info_df.withColumn("FullName", fake_name()) \
                                 .withColumn("Email", fake_email()) \
                                 .withColumn("PhoneNumber", fake_phone()) \
                                 .withColumn("Address", fake_address())

print("✅ Synthetic user details generated!")

# Save transformed data to BigQuery
synthetic_users_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", "ordinal-reason-449406-f0.avito_silver.UserInfo_Synthetic") \
    .mode("overwrite") \
    .save()

print("🎉 Synthetic user details successfully created in BigQuery!")

# Stop Spark session
spark.stop()
print("✅ Spark session stopped!")
