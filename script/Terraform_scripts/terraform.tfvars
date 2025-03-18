project_id       = "ordinal-reason-449406-f0"
region           = "us-central1"
storage_location = "US"
credentials_file = "terraform-sa-key.json"

# Storage Buckets
bronze_bucket  = "avito-bronze-bucket-central1"
silver_bucket  = "avito-silver-bucket-central1"
gold_bucket    = "avito-gold-bucket-central1"
landing_bucket = "avito-landing-bucket-central1"

# BigQuery Datasets
bq_silver_dataset    = "avito_silver"
bq_gold_dataset      = "avito_gold"
bq_reference_dataset = "avito_reference"

# Cloud SQL
db_instance_name = "avito-db-instance"
db_name          = "avito_db"
db_tier          = "db-f1-micro"

# Dataproc
dataproc_cluster_name = "avito-dataproc"
dataproc_master_type  = "n1-standard-2"
dataproc_worker_type  = "n1-standard-2"
dataproc_worker_count = 2

# Compute Engine
vm_name         = "avito-vm"
vm_machine_type = "e2-medium"
vm_zone         = "us-central1-a"

# Cloud Composer
composer_env = "avito-composer"
