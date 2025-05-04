variable "project_id" {
  description = "The ID of the project"
  type        = string
  default     = "boreal-album-457603-u0"
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "The zone to deploy resources"
  type        = string
  default     = "asia-southeast1-a"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "sonhs-data-lake"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "storage_class" {
  description = "The storage class for the bucket"
  type        = string
  default     = "STANDARD"
}

variable "bucket_location" {
  description = "The location for the bucket"
  type        = string
  default     = "ASIA-SOUTHEAST1"
}

variable "dataset_location" {
  description = "The location for the BigQuery dataset"
  type        = string
  default     = "asia-southeast1"
}
