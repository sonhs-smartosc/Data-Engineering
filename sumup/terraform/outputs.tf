output "vm_name" {
  value       = google_compute_instance.kafka_spark_vm.name
  description = "Name of the VM instance"
}

output "vm_external_ip" {
  value       = google_compute_instance.kafka_spark_vm.network_interface[0].access_config[0].nat_ip
  description = "External IP address of the VM instance"
}

output "bigquery_dataset" {
  value       = google_bigquery_dataset.aov_analytics_dataset.dataset_id
  description = "BigQuery dataset ID"
}

output "temp_bucket" {
  value       = google_storage_bucket.temp_bucket.name
  description = "GCS bucket for BigQuery temporary files"
}

output "service_account" {
  value       = google_service_account.spark_service_account.email
  description = "Service account for Spark to access BigQuery"
}
