# Terraform Configuration for AOV Analytics Pipeline

This directory contains Terraform configuration to deploy infrastructure for the Arena of Valor (AOV) analytics pipeline on Google Cloud Platform.

## Resources Created

- **Google Compute Engine VM Instance**: For running Kafka and Spark
- **Service Account**: With permissions to access BigQuery and Cloud Storage
- **Cloud Storage Bucket**: For temporary BigQuery data processing
- **BigQuery Dataset and Tables**: Schema optimized for AOV match data

## Schema Design

The BigQuery tables follow this schema:

### Matches Table

Stores general information about each match:
- `id` (STRING): Unique match ID
- `start_time` (TIMESTAMP): Match start time
- `end_time` (TIMESTAMP): Match end time
- `duration_seconds` (INTEGER): Total match duration

### Teams Table

Stores team performance in each match:
- `id` (INTEGER): Unique team record ID
- `match_id` (STRING): Reference to match
- `team_id` (INTEGER): Team identifier (1 or 2)
- `win` (BOOLEAN): Whether team won
- `dragons`, `barons`, `towers`, etc: Objective counts
- Various team statistics like `total_kills` and `total_gold`

### Players Table

Stores detailed player statistics:
- `id` (INTEGER): Unique player record ID
- `match_id` (STRING): Reference to match
- `participant_id` (INTEGER): Player participant ID (1-10)
- `team_id` (INTEGER): Team identifier (1 or 2)
- `champion` (STRING): Champion name
- `kills`, `deaths`, `assists`: Player KDA
- `total_damage_dealt`, `total_damage_taken`: Damage statistics
- `gold_earned`: Gold earned
- `win` (BOOLEAN): Whether player won

## Authentication

This configuration uses Google Cloud credentials authentication rather than SSH keys.

## Usage

1. Create a service account in Google Cloud Console and download its JSON key
2. Place the credentials JSON file in a secure location

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Create a `terraform.tfvars` file with your specific values:
   ```
   project_id = "your-gcp-project-id"
   credentials_file = "path/to/your/credentials.json"
   ```

5. Review the planned changes:
   ```bash
   terraform plan
   ```

6. Apply the configuration:
   ```bash
   terraform apply
   ```

7. Connect to the VM using Google Cloud Console or gcloud:
   ```bash
   gcloud compute ssh --zone "us-central1-a" "aov-analytics-vm" --project "your-project-id"
   ```

## Clean Up

To destroy all resources:
```bash
terraform destroy
```

## Notes

- The VM comes with Docker, Python, and Java pre-installed
- The service account has permissions to write to BigQuery and Storage
- This setup uses OS Login for VM access rather than SSH keys
- You'll need to manually upload your Kafka and Spark code to the VM
