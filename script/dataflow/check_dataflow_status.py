from googleapiclient.discovery import build
from google.oauth2 import service_account

# Replace with your project ID and region
PROJECT_ID = "ordinal-reason-449406-f0"
REGION = "us-central1"

# Authenticate using your default credentials (ensure `gcloud auth application-default login` is done)
dataflow = build("dataflow", "v1b3")

def list_dataflow_jobs():
    """Lists all Dataflow jobs in the project and their statuses."""
    request = dataflow.projects().locations().jobs().list(
        projectId=PROJECT_ID,
        location=REGION
    )
    response = request.execute()

    if "jobs" in response:
        print("\n🔹 Dataflow Jobs in Project:")
        for job in response["jobs"]:
            print(f"Job ID: {job['id']} | Name: {job['name']} | State: {job['currentState']}")
    else:
        print("No Dataflow jobs found.")

def check_job_status(job_id):
    """Checks the status of a specific Dataflow job."""
    request = dataflow.projects().locations().jobs().get(
        projectId=PROJECT_ID,
        location=REGION,
        jobId=job_id
    )
    response = request.execute()
    
    print(f"\n🔍 Job Status:\n- Job ID: {response['id']}\n- Name: {response['name']}\n- State: {response['currentState']}")

if __name__ == "__main__":
    list_dataflow_jobs()
    
    # If you have a specific Job ID, replace it here to check its status
    job_id_to_check = input("\nEnter Job ID to check status (or press Enter to skip): ").strip()
    if job_id_to_check:
        check_job_status(job_id_to_check)
