import os
from google.cloud import storage
from datetime import datetime
from dotenv import load_dotenv


def test_cloud_storage():
    """Test tạo bucket và upload file vào Cloud Storage"""
    try:
        load_dotenv()
        storage_client = storage.Client(project=os.getenv('GCP_PROJECT_ID'))

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        bucket_name = f"sonhs-bucket"

        print(f"Creating bucket: {bucket_name}")
        bucket = storage_client.create_bucket(bucket_name, location="asia-southeast1")

        test_file_name = "hello.txt"
        test_blob = bucket.blob(test_file_name)
        test_blob.upload_from_string("Hello, Google Cloud Storage!")

        print(f"Created bucket: {bucket.name}")
        print(f"Uploaded file: {test_file_name}")

        print("\nAll buckets:")
        for bucket in storage_client.list_buckets():
            print(f"- {bucket.name}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("Testing Google Cloud Storage API...")
    test_cloud_storage()