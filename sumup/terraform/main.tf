provider "google" {
  project     = var.project_id
  region      = var.region
  zone        = var.zone
  credentials = file(var.credentials_file)
}

# Create a Google Compute Engine VM instance
resource "google_compute_instance" "kafka_spark_vm" {
  name         = "${var.kafka_spark_vm_name}-vm"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral public IP
    }
  }

  # Remove SSH key metadata and use OS Login instead
  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = <<-SCRIPT
    apt-get update
    apt-get install -y docker.io docker-compose python3-pip openjdk-11-jdk
    pip3 install kafka-python pyspark google-cloud-bigquery google-cloud-storage google-auth
    systemctl enable docker
    systemctl start docker
    # No need for usermod since we're using OS Login
  SCRIPT

  tags = ["kafka", "spark", "bigdata"]
}

resource "google_compute_instance" "aov_api_vm" {
  name         = "aov-api-vm"
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

  metadata_startup_script = <<-SCRIPT
    apt-get update
    apt-get install -y docker.io docker-compose python3-pip
    pip3 install kafka-python pyspark google-cloud-bigquery google-cloud-storage google-auth
    systemctl enable docker
    systemctl start docker
    # No need for usermod since we're using OS Login
  SCRIPT
}

# Create a service account for the VM
# resource "google_service_account" "spark_service_account" {
#   account_id   = "${var.kafka_spark_vm_name}-sa"
#   display_name = "Service Account for Spark BigQuery Integration"
# }

# Grant permissions to the service account
# resource "google_project_iam_member" "bigquery_admin" {
#   project = var.project_id
#   role    = "roles/bigquery.admin"
#   member  = "serviceAccount:${google_service_account.spark_service_account.email}"
# }
#
# resource "google_project_iam_member" "storage_admin" {
#   project = var.project_id
#   role    = "roles/storage.admin"
#   member  = "serviceAccount:${google_service_account.spark_service_account.email}"
# }

# Create a GCS bucket for BigQuery temporary files
resource "google_storage_bucket" "temp_bucket" {
  name          = "${var.project_id}-${var.kafka_spark_vm_name}-temp"
  location      = var.region
  force_destroy = true
  storage_class = "STANDARD"
}

# Create a BigQuery dataset
resource "google_bigquery_dataset" "aov_analytics_dataset" {
  dataset_id                  = "aov_analytics"
  friendly_name               = "AOV Analytics Data"
  description                 = "Dataset containing AOV match results"
  location                    = var.bigquery_location
  delete_contents_on_destroy  = true
}

# Create BigQuery tables
resource "google_bigquery_table" "matches_table" {
  dataset_id = google_bigquery_dataset.aov_analytics_dataset.dataset_id
  table_id   = "matches"
  
  schema = <<EOF
  [
    {
      "name": "id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "Unique match ID"
    },
    {
      "name": "start_time",
      "type": "TIMESTAMP",
      "mode": "REQUIRED",
      "description": "Match start time"
    },
    {
      "name": "end_time",
      "type": "TIMESTAMP",
      "mode": "REQUIRED",
      "description": "Match end time"
    },
    {
      "name": "duration_seconds",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Match duration in seconds"
    }
  ]
  EOF
}

resource "google_bigquery_table" "teams_table" {
  dataset_id = google_bigquery_dataset.aov_analytics_dataset.dataset_id
  table_id   = "teams"
  
  schema = <<EOF
  [
    {
      "name": "id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "Unique team record ID"
    },
    {
      "name": "match_id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "ID of the match this team participated in"
    },
    {
      "name": "team_id",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Team identifier (1 or 2)"
    },
    {
      "name": "win",
      "type": "BOOLEAN",
      "mode": "REQUIRED",
      "description": "Whether this team won the match"
    },
    {
      "name": "dragons",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of dragons killed by the team"
    },
    {
      "name": "barons",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of barons killed by the team"
    },
    {
      "name": "towers",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of towers destroyed by the team"
    },
    {
      "name": "total_kills",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Total kills by the team"
    },
    {
      "name": "total_gold",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Total gold earned by the team"
    }
  ]
  EOF
}

resource "google_bigquery_table" "players_table" {
  dataset_id = google_bigquery_dataset.aov_analytics_dataset.dataset_id
  table_id   = "players"
  
  schema = <<EOF
  [
    {
      "name": "id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "Unique player record ID"
    },
    {
      "name": "match_id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "ID of the match this player participated in"
    },
    {
      "name": "team_id",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Team ID (1 or 2)"
    },
    {
      "name": "champion",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "Champion name"
    },
    {
      "name": "kills",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of kills"
    },
    {
      "name": "deaths",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of deaths"
    },
    {
      "name": "assists",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Number of assists"
    },
    {
      "name": "total_damage_dealt",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Total damage dealt"
    },
    {
      "name": "total_damage_taken", 
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Total damage taken"
    },
    {
      "name": "gold_earned",
      "type": "INTEGER",
      "mode": "REQUIRED",
      "description": "Gold earned"
    },
    {
      "name": "win",
      "type": "BOOLEAN",
      "mode": "REQUIRED",
      "description": "Whether this player won the match"
    }
  ]
  EOF
}
