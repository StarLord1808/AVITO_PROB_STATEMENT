from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, avg, when, expr

# Initialize Spark Session with temporary GCS bucket for BigQuery writes
spark = SparkSession.builder \
    .appName("Gold Layer Transformations") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2") \
    .config("viewsEnabled", "true") \
    .config("materializationDataset", "avito_temp") \
    .config("temporaryGcsBucket", "gs://avito-gold-bucket-central1/temp") \
    .getOrCreate()

print("🟢 Spark Session Created!")

# Define input BigQuery tables (Silver Layer)
silver_dataset = "ordinal-reason-449406-f0.avito_silver"

searchstream_enriched_table = f"{silver_dataset}.searchstream_enriched"
adsinfo_table = f"{silver_dataset}.adsinfo"
location_enriched_table = f"{silver_dataset}.Location_Enriched"
device_user_profile_table = f"{silver_dataset}.device_user_profile"
user_interactions_table = f"{silver_dataset}.user_interactions"
userinfo_table = f"{silver_dataset}.userinfo"
userinfo_synthetic_table = f"{silver_dataset}.UserInfo_Synthetic"

# Define output BigQuery dataset
gold_dataset = "ordinal-reason-449406-f0.avito_gold"

# Load data from BigQuery
searchstream_enriched_df = spark.read.format("bigquery").option("table", searchstream_enriched_table).load()
adsinfo_df = spark.read.format("bigquery").option("table", adsinfo_table).load()
location_enriched_df = spark.read.format("bigquery").option("table", location_enriched_table).load()
device_user_profile_df = spark.read.format("bigquery").option("table", device_user_profile_table).load()
user_interactions_df = spark.read.format("bigquery").option("table", user_interactions_table).load()
userinfo_df = spark.read.format("bigquery").option("table", userinfo_table).load()
userinfo_synthetic_df = spark.read.format("bigquery").option("table", userinfo_synthetic_table).load()

print("🟢 Data Loaded from BigQuery!")

# =====================================================
# 🟢 1️⃣ Click-Through Rate (CTR) Calculation
# =====================================================
ctr_df = searchstream_enriched_df.groupBy("AdID") \
    .agg(
        count("*").alias("Total_Impressions"),
        sum(when(col("HistCTR") > 0, 1).otherwise(0)).alias("Total_Clicks"),
        expr("(sum(CASE WHEN HistCTR > 0 THEN 1 ELSE 0 END) / count(*)) * 100").alias("CTR")
    )

print("🟢 CTR Calculated!")

# Save CTR results to BigQuery
ctr_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.click_through_rate") \
    .mode("overwrite") \
    .save()
print("🟢 CTR Results Saved to BigQuery!")

# =====================================================
# 🟢 2️⃣ Ad Performance by Region & Category
# =====================================================

# Using aliases to prevent ambiguity
search_alias = searchstream_enriched_df.alias("search")
ads_alias = adsinfo_df.alias("ads")
location_alias = location_enriched_df.alias("loc")

ad_performance_df = search_alias \
    .join(ads_alias, col("search.AdID") == col("ads.AdID"), "left") \
    .join(location_alias, col("search.LocationID") == col("loc.LocationID"), "left") \
    .groupBy(col("loc.RegionName"), col("ads.CategoryID")) \
    .agg(
        count("search.AdID").alias("Total_Impressions"),
        sum(when(col("search.HistCTR") > 0, 1).otherwise(0)).alias("Total_Clicks"),
        expr("(sum(CASE WHEN search.HistCTR > 0 THEN 1 ELSE 0 END) / count(*)) * 100").alias("CTR")
    )

print("🟢 Ad Performance Calculated!")

# Save to BigQuery
ad_performance_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.ad_performance_by_region_category") \
    .mode("overwrite") \
    .save()

print("🟢 Ad Performance Results Saved to BigQuery!")

# =====================================================
# 🟢 3️⃣ Device Usage Analytics
# =====================================================
device_usage_df = device_user_profile_df.groupBy("UserDeviceID") \
    .agg(
        count("AdID").alias("Total_Interactions"),
        sum(when(col("PhoneRequestDate").isNotNull(), 1).otherwise(0)).alias("Total_PhoneRequests"),
        expr("(sum(CASE WHEN PhoneRequestDate IS NOT NULL THEN 1 ELSE 0 END) / count(*)) * 100").alias("PhoneRequest_Rate")
    )

print("🟢 Device Usage Analytics Calculated!")

# Save to BigQuery
device_usage_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.device_usage_analytics") \
    .mode("overwrite") \
    .save()

print("🟢 Device Usage Analytics Saved to BigQuery!")

# =====================================================
# 🟢 4️⃣ Revenue by Category & Region
# =====================================================
revenue_df = search_alias \
    .join(ads_alias, col("search.AdID") == col("ads.AdID"), "left") \
    .join(location_alias, col("search.LocationID") == col("loc.LocationID"), "left") \
    .groupBy(col("loc.RegionName"), col("ads.CategoryID")) \
    .agg(
        sum(col("ads.Price")).alias("Total_Revenue"),
        count("search.AdID").alias("Total_Ads"),
        sum(when(col("search.HistCTR") > 0, col("ads.Price")).otherwise(0)).alias("Revenue_from_Clicks")
    )

print("🟢 Revenue Calculated!")

# Save to BigQuery
revenue_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.revenue_by_category_region") \
    .mode("overwrite") \
    .save()

print("🟢 Revenue Results Saved to BigQuery!")

# =====================================================
# 🟢 5️⃣ User Engagement Analysis
# =====================================================
user_engagement_df = user_interactions_df.groupBy("UserID") \
    .agg(
        count("AdID").alias("Total_Ads_Interacted"),
        sum(when(col("PhoneRequestDate").isNotNull(), 1).otherwise(0)).alias("Total_PhoneRequests"),
        avg("ViewTimestamp").alias("Avg_View_Time"),
        expr("(sum(CASE WHEN PhoneRequestDate IS NOT NULL THEN 1 ELSE 0 END) / count(*)) * 100").alias("PhoneRequest_Rate")
    )

print("🟢 User Engagement Analysis Calculated!")

# Save to BigQuery
user_engagement_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.user_engagement_analysis") \
    .mode("overwrite") \
    .save()

print("🟢 User Engagement Analysis Saved to BigQuery!")

# =====================================================
# 🟢 6️⃣ User Profile Enrichment
# =====================================================
user_profile_enriched_df = userinfo_synthetic_df.alias("synthetic").join(
    userinfo_df.alias("user"), col("synthetic.UserID") == col("user.UserID"), "left"
).select(
    col("synthetic.UserID"), col("synthetic.FullName"), col("synthetic.Email"),
    col("synthetic.PhoneNumber"), col("synthetic.Address"),
    col("user.UserAgentID"), col("user.UserAgentOSID"), col("user.UserDeviceID"), col("user.UserAgentFamilyID")
)

print("🟢 User Profile Enriched!")

# Save to BigQuery
user_profile_enriched_df.write.format("bigquery") \
    .option("table", f"{gold_dataset}.user_profile_enriched") \
    .mode("overwrite") \
    .save()

print("🟢 User Profile Enriched Saved to BigQuery!")

# Stop Spark Session
spark.stop()
