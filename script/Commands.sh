#Commands used to create Service Account
gcloud iam service-accounts create terraform-sa \
    --description="Terraform Service Account" \
    --display-name="Terraform SA"


#Command to grant the Service Account the necessary permissions
gcloud projects add-iam-policy-binding ordinal-reason-449406-f0 \
    --member="serviceAccount:terraform-sa@ordinal-reason-449406-f0.iam.gserviceaccount.com" \
    --role="roles/editor"
    
#if you want to give more permissions to the service account, you can use the following command
gcloud projects add-iam-policy-binding ordinal-reason-449406-f0 \
    --member="serviceAccount:service-674629315151@gcp-sa-datafusion.iam.gserviceaccount.com" \
   --role="roles/cloudsql.client" \
    --role="roles/cloudsql.editor" \
    --role="roles/cloudsql.admin" \
    --role="roles/datafusion.runner"
#Command to list the IAM policy for the project

gcloud projects get-iam-policy ordinal-reason-449406-f0 \
    --flatten="bindings[].members" \
    --format="table(bindings.role, bindings.members)" \
    | grep "cloud-function-sa@ordinal-reason-449406-f0.iam.gserviceaccount.com"

#Command to Generate a Service Account Key (JSON File)

gcloud iam service-accounts keys create ~/GCP_Problem_Statement/Avito-ad-sense/Terraform_scripts/terraform-sa-key.json \
    --iam-account=terraform-sa@ordinal-reason-449406-f0.iam.gserviceaccount.com

#Command to set the GOOGLE_CREDENTIALS environment variable
export GOOGLE_CREDENTIALS=/home/jiraiya/GCP_Problem_Statement/Avito-ad-sense/Terraform_scripts/terraform-sa-key.json

#Command to list the service accounts

gcloud iam service-accounts list


#Command to upload the 7z files to the bucket
gsutil -m cp Ads* gs://avito-landing-bucket-central1/

#Command to list the bucket
gsutil ls

#Command to create a bucket in the us-central1 region
gsutil mb -l us-central1 gs://avito-landing-bucket-central1/

#Command to delete the files in the bucket
gsutil -m rm gs://avito-bronze-bucket-central1/**

#Command to delete a bucket
gsutil rm -r gs://avito-gold-bucket

# Cloud FUncitons
#Command to deploy the Cloud Function
gcloud functions deploy extract_7z     
    --region=us-central1     
    --runtime python310     
    --trigger-resource avito-bronze-bucket-central1     
    --trigger-event google.storage.object.finalize     
    --entry-point extract_files     
    --memory 512MB     
    --timeout 300s

#Command to list the deployed functions
gcloud functions list --region=us-central1

#Command to get the log of the function
gcloud functions logs read extract_7z --region=us-central1

#Command to delete the function
gcloud functions delete extract_7z --region=us-central1

#Command used to create Secret Manager

gcloud secrets create avito-db-password --replication-policy automatic

echo '{"user":"your_db_user","password":"your_db_password","database":"your_db_name","instance":"your_cloud_sql_instance"}' | gcloud secrets versions add cloud-sql-creds --data-file=-

#Command to list the secrets

gcloud secrets list

#Command to get the secret

gcloud secrets versions access latest --secret=avito-db-password

#Command to load a file from WSL to GCP VM
gcloud compute scp AdsInfo.csv dark_knight_180899@avito-vm:/home/dark_knight_180899/Avito-ad-sense/avito_data --zone=us-central1-a

#Command to restart Data Fusion Insatance

gcloud beta data-fusion instances restart load-searchstream --location=us-central1

#Command to query the Parquet file
pip install pyarrow pandas
python3 -c "
import pyarrow.parquet as pq;
table = pq.read_table('AdsInfo_part-00000-97bb04bf-81a4-4bcc-aeca-9b55559c529c-c000.snappy.parquet');
print(table.to_pandas().head())"