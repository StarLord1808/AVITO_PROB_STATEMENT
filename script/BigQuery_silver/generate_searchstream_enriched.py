from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("AdMetadataEnrichment").getOrCreate()
print("✅ Spark session initialized!")
# Define BigQuery dataset
PROJECT_ID = "ordinal-reason-449406-f0"
DATASET = "avito_silver"

# Read SearchStream data
searchstream_df = spark.read.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.searchstream") \
    .load()
print("✅ SearchStream data loaded!")
# Read AdsInfo data
adsinfo_df = spark.read.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.adsinfo") \
    .load()
print("✅ AdsInfo data loaded!")
# Perform INNER JOIN on AdID to enrich search data with ad metadata
search_enriched_df = searchstream_df.alias("s") \
    .join(adsinfo_df.alias("a"), col("s.AdID") == col("a.AdID"), "inner") \
    .select(
        col("s.ID"),
        col("s.SearchID"),
        col("s.AdID"),
        col("s.Position"),
        col("s.ObjectType"),
        col("s.HistCTR"),
        col("s.inserted_at"),
        col("a.LocationID"),
        col("a.CategoryID"),
        col("a.Price"),
        col("a.Title"),
        col("a.IsContext"),
        col("a.inserted_at").alias("ad_inserted_at")
    )
print("✅ SearchStream data enriched with Ad Metadata!")
# Write enriched data back to BigQuery as searchstream_enriched table
search_enriched_df.write.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.searchstream_enriched") \
    .option("writeMethod", "direct") \
    .mode("overwrite") \
    .save()


print("✅ Ad Metadata Enrichment Completed Successfully!")
