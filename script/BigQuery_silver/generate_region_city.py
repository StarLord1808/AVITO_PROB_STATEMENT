from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit, udf
from pyspark.sql.types import StringType, IntegerType
from faker import Faker

# Initialize Spark session
spark = SparkSession.builder.appName("GenerateCityRegionReference").getOrCreate()

# Initialize Faker
faker = Faker()

# Function to generate a fake city name
def generate_city():
    return faker.city()

# Function to generate a fake region name
def generate_region():
    return faker.state()

# Define UDFs
fake_city_udf = udf(generate_city, StringType())
fake_region_udf = udf(generate_region, StringType())

# Create City Reference Table with Audit Fields
city_ids = spark.range(1, 3724).withColumnRenamed("id", "CityID")  # 3723 unique city IDs
city_reference_df = city_ids.withColumn("CityName", fake_city_udf()) \
                            .withColumn("CR_DB_TS", current_timestamp()) \
                            .withColumn("UPDT_DB_TS", current_timestamp()) \
                            .withColumn("IsActive", lit(1))

# Create Region Reference Table with Audit Fields
region_ids = spark.range(1, 85).withColumnRenamed("id", "RegionID")  # 84 unique region IDs
region_reference_df = region_ids.withColumn("RegionName", fake_region_udf()) \
                                .withColumn("CR_DB_TS", current_timestamp()) \
                                .withColumn("UPDT_DB_TS", current_timestamp()) \
                                .withColumn("IsActive", lit(1))

# Save City Reference Table to BigQuery in `avito_reference`
city_reference_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", "ordinal-reason-449406-f0.avito_reference.City_Reference") \
    .mode("overwrite") \
    .save()

# Save Region Reference Table to BigQuery in `avito_reference`
region_reference_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", "ordinal-reason-449406-f0.avito_reference.Region_Reference") \
    .mode("overwrite") \
    .save()

# Stop Spark session
spark.stop()
print("✅ Spark session stopped!")