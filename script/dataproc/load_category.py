from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
import pymysql
import os
import pandas as pd
from google.cloud import storage
from io import StringIO

# Initialize Spark session
spark = SparkSession.builder.appName("GCS-to-CloudSQL-Category").getOrCreate()

# Cloud Storage and Cloud SQL details
GCS_BUCKET = "avito-landing-bucket-central1"
GCS_FILE = "Category.csv"
ERROR_FILE = f"error_{GCS_FILE}"

gcs_path = f"gs://{GCS_BUCKET}/{GCS_FILE}"
error_gcs_path = f"gs://{GCS_BUCKET}/BadFiles/{ERROR_FILE}"

# Fetch MySQL credentials from environment variables
db_user = "thiru"
db_password = "thiru"
db_name = "avito_db"
db_host = "35.239.147.18"

# ✅ Function to load data from GCS
def load_data_from_gcs():
    """Load CSV from GCS into a Spark DataFrame."""
    try:
        df = spark.read.option("header", "true").csv(gcs_path)
        return df
    except Exception as e:
        print(f"❌ Error loading data from GCS: {str(e)}")
        return None

# ✅ Function to clean data
def clean_data(df):
    """Ensures correct column mapping and converts data types."""
    required_columns = ["CategoryID", "Level", "ParentCategoryID", "SubcategoryID"]

    # Convert DataFrame column names to lower case
    df = df.toDF(*[c.lower() for c in df.columns])

    # Ensure all required columns exist
    for col in required_columns:
        if col.lower() not in df.columns:
            print(f"❌ Missing column: {col}. Aborting!")
            return None

    # Add inserted_at column with current timestamp
    df = df.withColumn("inserted_at", current_timestamp())

    return df

# ✅ Function to write valid records to MySQL and log errors
def write_to_mysql(df):
    """Writes valid records to Cloud SQL, logs errors separately."""
    try:
        # Convert Spark DataFrame to Pandas
        pdf = df.toPandas()

        # Establish MySQL connection
        conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()

        # Insert statement
        insert_sql = """
        INSERT INTO Category (CategoryID, Level, ParentCategoryID, SubcategoryID, inserted_at)
        VALUES (%s, %s, %s, %s, %s)
        """

        # Error handling
        error_rows = []

        # Insert records
        for _, row in pdf.iterrows():
            try:
                cursor.execute(insert_sql, (
                    row["categoryid"],
                    row["level"],
                    row["parentcategoryid"],
                    row["subcategoryid"],
                    row["inserted_at"]
                ))
            except Exception as e:
                print(f"⚠️ Error inserting record {row['categoryid']}: {str(e)}")
                error_rows.append(row)

        # Commit transaction
        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Successfully loaded {len(pdf) - len(error_rows)} records from GCS.")

        # Save error records
        if error_rows:
            error_df = pd.DataFrame(error_rows)
            save_error_records(error_df)

    except Exception as e:
        print(f"❌ Error writing to MySQL: {str(e)}")

# ✅ Function to save error records to GCS
def save_error_records(error_df):
    """Saves error records to GCS as CSV."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(ERROR_FILE)

        # Convert DataFrame to CSV string
        csv_buffer = StringIO()
        error_df.to_csv(csv_buffer, index=False)
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

        print(f"🚨 Error records saved to GCS: {error_gcs_path}")
    except Exception as e:
        print(f"❌ Error saving error records: {str(e)}")

# ✅ Main Execution
if __name__ == "__main__":
    df = load_data_from_gcs()
    if df is not None:
        cleaned_df = clean_data(df)
        if cleaned_df is not None:
            write_to_mysql(cleaned_df)
