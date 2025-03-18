from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, udf, lit, current_timestamp
from pyspark.sql.types import DoubleType, StringType, IntegerType
import requests

# Initialize Spark session
spark = SparkSession.builder.appName("LocationEnrichment").getOrCreate()
print("✅ Spark session started!")

# Load tables from BigQuery
location_df = spark.read.format("bigquery").option("table", "ordinal-reason-449406-f0.avito_silver.location").load()
city_ref_df = spark.read.format("bigquery").option("table", "ordinal-reason-449406-f0.avito_reference.City_Reference").load()
region_ref_df = spark.read.format("bigquery").option("table", "ordinal-reason-449406-f0.avito_reference.Region_Reference").load()

print("✅ Location, City_Reference, and Region_Reference tables loaded!")

# Google Maps API Key (Ensure it's securely stored)
GOOGLE_MAPS_API_KEY = "" # Add your Google Maps API Key here

# Function to fetch latitude, longitude, and country name
def get_lat_long_country(region_name):
    """Fetch latitude, longitude, and country name using Google Maps API."""
    if not region_name:
        return 0.0, 0.0, "Russia"  # Default values if no region is provided

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={region_name}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            lat_long = data["results"][0]["geometry"]["location"]
            country = None
            for comp in data["results"][0]["address_components"]:
                if "country" in comp["types"]:
                    country = comp["long_name"]
                    break
            return lat_long["lat"], lat_long["lng"], country if country else "Russia"

    return 0.0, 0.0, "Russia"  # Default if API fails

# Define UDFs for Spark
get_latitude_udf = udf(lambda region: get_lat_long_country(region)[0], DoubleType())
get_longitude_udf = udf(lambda region: get_lat_long_country(region)[1], DoubleType())
get_country_udf = udf(lambda region: get_lat_long_country(region)[2], StringType())

print("✅ UDFs defined for fetching Latitude, Longitude, and Country!")

# **STEP 1: Join Location with City_Reference & Region_Reference**
location_enriched_df = (
    location_df
    .join(city_ref_df, "CityID", "left")  # Get City Name
    .join(region_ref_df, "RegionID", "left")  # Get Region Name
    .select(
        location_df["*"],  # Keep all original fields from Location
        city_ref_df["CityName"],
        region_ref_df["RegionName"]
    )
)

print("✅ Location table joined with reference tables!")

# **STEP 2: Fetch Latitude, Longitude, and Country Name using RegionName**
location_enriched_df = location_enriched_df.withColumn("Latitude", get_latitude_udf(col("RegionName"))) \
                                           .withColumn("Longitude", get_longitude_udf(col("RegionName"))) \
                                           .withColumn("Country", get_country_udf(col("RegionName")))

print("✅ Latitude, Longitude, and Country Name fetched!")

# **STEP 3: Validate Country Consistency**
location_enriched_df = location_enriched_df.withColumn(
    "Valid_Country",
    when(col("Country").isNotNull(), True).otherwise(False)  # Check if country was fetched
)

# **STEP 4: Handle Invalid Country (Set to Russia & (0,0) if invalid)**
location_enriched_df = location_enriched_df.withColumn(
    "Latitude",
    when(~col("Valid_Country"), lit(0.0)).otherwise(col("Latitude"))
).withColumn(
    "Longitude",
    when(~col("Valid_Country"), lit(0.0)).otherwise(col("Longitude"))
).withColumn(
    "Country",
    when(~col("Valid_Country"), lit("Russia")).otherwise(col("Country"))
)

print("✅ Country consistency validated. Defaulted to Russia where necessary!")

# **STEP 5: Add Metadata Fields**
location_enriched_df = location_enriched_df.withColumn("cr_db_dt", current_timestamp()) \
                                           .withColumn("updt_db_dt", current_timestamp()) \
                                           .withColumn("is_active", when(col("Valid_Country"), 1).otherwise(0).cast(IntegerType()))

print("✅ Metadata fields (cr_db_dt, updt_db_dt, is_active) added!")

# **STEP 6: Save to BigQuery**
location_enriched_df.write \
    .format("bigquery") \
    .option("temporaryGcsBucket", "avito-silver-bucket-central1/temp") \
    .option("table", "ordinal-reason-449406-f0.avito_silver.Location_Enriched") \
    .mode("overwrite") \
    .save()

print("✅ Enriched Location table saved to BigQuery!")

# Stop Spark session
spark.stop()
print("✅ Spark session stopped.")
