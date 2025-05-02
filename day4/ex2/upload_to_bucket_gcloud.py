from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the GCS bucket."""
    storage_client = storage.Client.from_service_account_json('./credentials/service-account-key.json')

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


bucket_name = 'bucket-create-by-terraform'
source_file_name = './gau.jpeg'
destination_blob_name = 'gau.jpg'

upload_blob(bucket_name, source_file_name, destination_blob_name)
