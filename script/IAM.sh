PROJECT_ID="ordinal-reason-449406-f0"
DATAFLOW_SA="service-674629315151@dataflow-service-producer-prod.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DATAFLOW_SA" \
    --role="roles/dataflow.worker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DATAFLOW_SA" \
    --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DATAFLOW_SA" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$DATAFLOW_SA" \
    --role="roles/cloudsql.client"
