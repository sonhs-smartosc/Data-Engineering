terraform {
  required_version = ">= 0.13"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Biến toàn cục
variable "project_id" {
  description = "ID dự án duy nhất, bạn cần thay bằng của bạn"
  default     = "your-unique-project-id-123"  # Thay bằng ID của bạn
}

variable "project_name" {
  default = "Data Lake Project"
}

variable "region" {
  default = "us-central1"
}

# Provider Google Cloud
provider "google" {
  credentials = file("path/to/your/credentials.json") # Thay bằng đường dẫn thật của bạn
  project     = var.project_id
  region      = var.region
}

# Tạo dự án mới
resource "google_project" "my_project" {
  name                = var.project_name
  project_id          = var.project_id
  auto_create_network = true
  billing_account     = "your-billing-account-id"  # Thay bằng Billing Account của bạn
}

# Bật API cần thiết
resource "google_project_service" "enable_apis" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com"
  ])

  project = google_project.my_project.project_id
  service = each.key
}

# Tạo Storage Bucket cho Data Lake
resource "google_storage_bucket" "data_lake_bucket" {
  name                        = "${var.project_id}-datalake"
  location                    = var.region
  project                     = google_project.my_project.project_id
  uniform_bucket_level_access = true
  force_destroy               = true

  versioning {
    enabled = true
  }
}

# Tạo Service Account để dùng cho Data Lake
resource "google_service_account" "datalake_sa" {
  account_id   = "datalake-sa"
  display_name = "Data Lake Service Account"
}

# Cấp quyền cho Service Account
resource "google_project_iam_member" "storage_admin" {
  project = google_project.my_project.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.datalake_sa.email}"
}

resource "google_project_iam_member" "bigquery_dataeditor" {
  project = google_project.my_project.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.datalake_sa.email}"
}

# Output các thông tin quan trọng
output "project_id" {
  value = google_project.my_project.project_id
}

output "bucket_name" {
  value = google_storage_bucket.data_lake_bucket.name
}

output "service_account_email" {
  value = google_service_account.datalake_sa.email
}