# General GCP Configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "credentials_file" {
  description = "Path to GCP credentials JSON file"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "storage_location" {
  description = "Location for GCS Buckets and BigQuery Datasets"
  type        = string
  default     = "US"
}

# Storage Buckets
variable "bronze_bucket" {
  description = "GCS Bucket for Bronze Layer"
  type        = string
}

variable "silver_bucket" {
  description = "GCS Bucket for Silver Layer"
  type        = string
}

variable "gold_bucket" {
  description = "GCS Bucket for Gold Layer"
  type        = string
}

variable "landing_bucket" {
  description = "GCS Bucket for Landing Data"
  type        = string
}

# BigQuery Datasets
variable "bq_silver_dataset" {
  description = "BigQuery Dataset for Silver Layer"
  type        = string
}

variable "bq_gold_dataset" {
  description = "BigQuery Dataset for Gold Layer"
  type        = string
}

variable "bq_reference_dataset" {
  description = "BigQuery Dataset for Reference Tables"
  type        = string
}

# Cloud SQL Configuration
variable "db_instance_name" {
  description = "Cloud SQL Instance Name"
  type        = string
}

variable "db_name" {
  description = "Cloud SQL Database Name"
  type        = string
}

variable "db_tier" {
  description = "Cloud SQL Machine Tier"
  type        = string
  default     = "db-f1-micro"
}

# Dataproc Cluster Configuration
variable "dataproc_cluster_name" {
  description = "Name of the Dataproc Cluster"
  type        = string
}

variable "dataproc_master_type" {
  description = "Machine type for Dataproc Master Node"
  type        = string
  default     = "n1-standard-2"
}

variable "dataproc_worker_type" {
  description = "Machine type for Dataproc Worker Nodes"
  type        = string
  default     = "n1-standard-2"
}

variable "dataproc_worker_count" {
  description = "Number of Dataproc Worker Nodes"
  type        = number
  default     = 2
}

# Compute Engine (VM)
variable "vm_name" {
  description = "Compute Engine VM Instance Name"
  type        = string
}

variable "vm_machine_type" {
  description = "Machine Type for VM"
  type        = string
  default     = "e2-medium"
}

variable "vm_zone" {
  description = "Zone for Compute Engine VM"
  type        = string
  default     = "us-central1-a"
}

# Cloud Composer
variable "composer_env" {
  description = "Cloud Composer Environment Name"
  type        = string
}
