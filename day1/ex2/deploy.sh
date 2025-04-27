#!/bin/bash

# Exit on any error
set -e

# Variables
PROJECT_ID="boreal-album-457603-u0"
ZONE="asia-southeast1-a"
INSTANCE_NAME="instance-sonhs-01"
MACHINE_TYPE="e2-small"

# Create VM instance
echo "Creating VM instance..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=663895004419-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=env=prod

# Wait for VM to be ready
echo "Waiting for VM to be ready..."
sleep 30

#gcloud compute --project $PROJECT_ID ssh --zone $ZONE $INSTANCE_NAME
# Install Docker and dependencies
echo "Installing Docker and dependencies..."
gcloud compute --project $PROJECT_ID ssh $INSTANCE_NAME --zone=$ZONE --command='
    sudo apt-get update && \
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    sudo apt-get update && \
    sudo apt-get install -y docker-ce docker-compose && \
    sudo usermod -aG docker $USER
'

# Create necessary directories on VM
echo "Creating directories..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='
    mkdir -p ~/app/credentials
'

# Copy application files
echo "Copying application files..."
gcloud compute scp --recurse ./* $INSTANCE_NAME:~/app --zone=$ZONE

# Copy .env file separately
echo "Copying .env file..."
gcloud compute scp .env $INSTANCE_NAME:~/app/.env --zone=$ZONE

# Start application
echo "Starting application..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='
    cd ~/app && \
    sudo docker-compose up -d
'

echo "Deployment completed successfully!"
echo "Application should be running at: http://$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'):8080"


