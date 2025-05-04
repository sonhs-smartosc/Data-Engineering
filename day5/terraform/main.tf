terraform {
  required_version = ">= 0.13"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    null = {
      source  = "hashicorp/null"
    }
  }
}

provider "google" {
  credentials = file("../credentials/service-account-key.json")
  project     = "boreal-album-457603-u0"
  region      = "asia-southeast1"
}

resource "google_storage_bucket" "my_bucket" {
  name          = "bucket-save-csv"
  location      = "ASIA-SOUTHEAST1"
  force_destroy = true
}

resource "null_resource" "upload_csv" {
  provisioner "local-exec" {
    command = <<EOT
      gsutil cp ../SalesData.csv gs://${google_storage_bucket.my_bucket.name}/SalesData.csv
    EOT
  }

  depends_on = [google_storage_bucket.my_bucket]
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "my_sales_dataset"
  location   = "ASIA-SOUTHEAST1"
  friendly_name = "My Sales Data Dataset"
}

resource "google_bigquery_table" "sales_table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "my_sales_table"
  schema     = <<EOF
[
  {"name": "Date", "type": "DATE", "mode": "NULLABLE"},
  {"name": "Salesperson", "type": "STRING", "mode": "NULLABLE"},
  {"name": "Lead_Name", "type": "STRING", "mode": "NULLABLE"},
  {"name": "Segment", "type": "STRING", "mode": "NULLABLE"},
  {"name": "Region", "type": "STRING", "mode": "NULLABLE"},
  {"name": "Target_Close", "type": "DATE", "mode": "NULLABLE"},
  {"name": "Forecasted_Monthly_Revenue", "type": "NUMERIC", "mode": "NULLABLE"},
  {"name": "Opportunity_Stage", "type": "STRING", "mode": "NULLABLE"},
  {"name": "Weighted_Revenue", "type": "NUMERIC", "mode": "NULLABLE"},
  {"name": "Closed_Opportunity", "type": "BOOLEAN", "mode": "NULLABLE"},
  {"name": "Active_Opportunity", "type": "BOOLEAN", "mode": "NULLABLE"},
  {"name": "Latest_Status_Entry", "type": "BOOLEAN", "mode": "NULLABLE"}
]
EOF
}

resource "null_resource" "load_csv_into_bq" {
  depends_on = [google_bigquery_table.sales_table, null_resource.upload_csv]

  provisioner "local-exec" {
    command = <<EOT
      bq load --replace --skip_leading_rows=1 --source_format=CSV \
        --autodetect \
        "boreal-album-457603-u0:${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.sales_table.table_id}" \
        "gs://${google_storage_bucket.my_bucket.name}/SalesData.csv"
    EOT
  }
}


resource "google_compute_instance" "backend_vm" {
  name         = "backend-instance"
  machine_type = "e2-small"
  zone         = "asia-southeast1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
    }
  }

}