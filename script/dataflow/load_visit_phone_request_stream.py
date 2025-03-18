import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import mysql.connector
import yaml

# Load configuration from YAML file
with open("/home/jiraiya/GCP_Problem_Statement/script/dataflow/config.yaml", "r") as file:
    config = yaml.safe_load(file)

DB_CONFIG = config["database"]
GCP_CONFIG = config["gcp"]

# Function to read data from Cloud SQL
def read_from_mysql(query):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Function to join VisitsStream and PhoneRequestsStream
def join_visits_phone_requests(visit, phone_request):
    return {
        'UserID': visit['UserID'],
        'IPID': visit['IPID'],
        'AdID': visit['AdID'],
        'ViewDate': visit['ViewDate'],
        'PhoneRequestDate': phone_request['PhoneRequestDate']
    }

# Function to write results back to Cloud SQL
def write_to_mysql(row):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO VisitPhoneRequestStream (UserID, IPID, AdID, ViewDate, PhoneRequestDate)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (row['UserID'], row['IPID'], row['AdID'], row['ViewDate'], row['PhoneRequestDate']))
    conn.commit()
    cursor.close()
    conn.close()

# Apache Beam Pipeline
pipeline_options = PipelineOptions(
    runner='DataflowRunner',
    project=GCP_CONFIG["project"],
    region=GCP_CONFIG["region"],
    temp_location=GCP_CONFIG["temp_bucket"],
    staging_location=GCP_CONFIG["staging_bucket"]
)

with beam.Pipeline(options=pipeline_options) as p:
    visits = p | "Read VisitsStream" >> beam.Create(read_from_mysql("SELECT * FROM VisitsStream"))
    phone_requests = p | "Read PhoneRequestsStream" >> beam.Create(read_from_mysql("SELECT * FROM PhoneRequestsStream"))

    joined_data = (
        {"visits": visits, "phone_requests": phone_requests}
        | "Group By Keys" >> beam.CoGroupByKey()
        | "Flatten Joins" >> beam.FlatMap(lambda x: [join_visits_phone_requests(v, p) for v in x['visits'] for p in x['phone_requests']])
    )

    joined_data | "Write to Cloud SQL" >> beam.Map(write_to_mysql)

print("✅ Dataflow Job Submitted Successfully")
