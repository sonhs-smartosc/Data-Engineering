terraform {
  required_version = ">= 0.13"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project     = "boreal-album-457603-u0"
  region      = "asia-southeast1"
}

# Tạo một Storage Bucket
resource "google_storage_bucket" "bucket-terraform" {
  name                        = "bucket-create-by-terraform"
  location                    = "asia-southeast1"
  uniform_bucket_level_access = true
  force_destroy               = false
  versioning {
    enabled = true
  }
}


resource "google_storage_bucket_iam_binding" "public_read" {
  bucket = google_storage_bucket.bucket-terraform.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers",
  ]
}
