variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "boreal-album-457603-u0"
}

variable "kafka_spark_vm_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "kafka_aov-analytics"
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "asia-southeast1-a"
}

variable "machine_type" {
  description = "VM instance machine type"
  type        = string
  default     = "e2-small" # 4 vCPUs, 16GB memory
}

variable "bigquery_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

# Add credentials file variable instead of SSH variables
variable "credentials_file" {
  description = "Path to the Google Cloud credentials JSON file"
  type        = string
  default     = "../credentials/service-account.json"
}
