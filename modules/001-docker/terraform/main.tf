terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "de_course_bucket" {
  name     = var.gcs_bucket_name
  location = var.location

  storage_class               = var.gcs_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90 // days
    }
    action {
      type = "Delete"
    }
  }

  force_destroy = true
}

resource "google_bigquery_dataset" "de_dataset" {
  dataset_id = var.bq_dataset_name
  project    = var.project
  location   = var.location
}

resource "google_bigquery_dataset" "de_taxi_rides_ny" {
  dataset_id = var.bq_dataset_taxi_rides_ny_name
  project    = var.project
  location   = var.location
}

resource "google_dataproc_cluster" "de_spark_cluster" {
  name   = var.dataproc_cluster_name
  region = var.region

  project = var.project

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "e2-medium"
      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 4
      machine_type  = "e2-medium"
      disk_config {
        boot_disk_size_gb = 30
        num_local_ssds    = 1
      }
    }
  }
}
