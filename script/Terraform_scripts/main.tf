terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
}

# Storage Buckets
resource "google_storage_bucket" "avito-bronze_bucket" {
  name     = var.bronze_bucket
  location = var.storage_location
}

resource "google_storage_bucket" "avito-silver_bucket" {
  name     = var.silver_bucket
  location = var.storage_location
}

resource "google_storage_bucket" "avito-gold_bucket" {
  name     = var.gold_bucket
  location = var.storage_location
}

resource "google_storage_bucket" "avito-landing_bucket" {
  name     = var.landing_bucket
  location = var.storage_location
}

# BigQuery Datasets
resource "google_bigquery_dataset" "silver" {
  dataset_id = var.bq_silver_dataset
  project    = var.project_id
  location   = var.storage_location
}

resource "google_bigquery_dataset" "gold" {
  dataset_id = var.bq_gold_dataset
  project    = var.project_id
  location   = var.storage_location
}

resource "google_bigquery_dataset" "reference" {
  dataset_id = var.bq_reference_dataset
  project    = var.project_id
  location   = var.storage_location
}

# Cloud SQL Instance
resource "google_sql_database_instance" "db_instance" {
  name             = var.db_instance_name
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier = var.db_tier
  }
}

resource "google_sql_database" "avito_db" {
  name     = var.db_name
  instance = google_sql_database_instance.db_instance.name
}

# Dataproc Cluster
resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = var.dataproc_cluster_name
  region = var.region

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = var.dataproc_master_type

      disk_config {
        boot_disk_size_gb = 100
      }
    }

    worker_config {
      num_instances = var.dataproc_worker_count
      machine_type  = var.dataproc_worker_type

      disk_config {
        boot_disk_size_gb = 100
      }
    }
  }
}

# Compute Engine (VM Instance)
resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name
  machine_type = var.vm_machine_type
  zone         = var.vm_zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<EOT
#!/bin/bash
sudo apt update -y
sudo apt install -y python3-pip mysql-client
pip3 install mysql-connector-python faker pymysql pandas google-cloud-bigquery google-cloud-storage
EOT
}

# Cloud Composer Environment
resource "google_composer_environment" "composer_env" {
  name   = var.composer_env
  region = var.region

  config {
    node_count = 3

    software_config {
      image_version = "composer-2-airflow-2"
      env_variables = {
        PROJECT_ID = var.project_id
      }
    }
  }
}

terraform {
  backend "gcs" {
    bucket  = "terraform-state-avito"
    prefix  = "terraform/state"
  }
}