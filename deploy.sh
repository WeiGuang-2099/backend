#!/bin/bash

# FastAPI Backend Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [REGION] [SERVICE_NAME]

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"asia-east1"}
SERVICE_NAME=${3:-"fastapi-backend"}
DB_INSTANCE_NAME=${4:-"mysql-instance"}
DB_NAME=${5:-"jwt_auth_db"}
DB_USER=${6:-"jwt_user"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== FastAPI Cloud Run Deployment ===${NC}"
echo ""

# Validate project
echo -e "${YELLOW}Checking GCP project...${NC}"
if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
    echo -e "${RED}Error: Project '$PROJECT_ID' not found or not authenticated${NC}"
    echo "Please run: gcloud init"
    exit 1
fi
echo -e "${GREEN}✓ Project validated${NC}"
echo ""

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Create Artifact Registry repository (if not exists)
REPO_NAME="fastapi-repo"
echo -e "${YELLOW}Checking Artifact Registry repository...${NC}"
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "Creating repository..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="FastAPI Docker repository" \
        --project="$PROJECT_ID"
fi
echo -e "${GREEN}✓ Repository ready${NC}"
echo ""

# Build and push Docker image
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"
IMAGE_TAG="${IMAGE_NAME}:$(date +%s)"
echo -e "${YELLOW}Building Docker image...${NC}"
echo "Image: $IMAGE_TAG"

gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker build -t "$IMAGE_TAG" .
docker push "$IMAGE_TAG"
echo -e "${GREEN}✓ Image built and pushed${NC}"
echo ""

# Get Cloud SQL connection name
echo -e "${YELLOW}Getting Cloud SQL instance info...${NC}"
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
    --format="value(connectionName)" \
    --project="$PROJECT_ID")

if [ -z "$INSTANCE_CONNECTION_NAME" ]; then
    echo -e "${RED}Error: Cloud SQL instance '$DB_INSTANCE_NAME' not found${NC}"
    echo ""
    echo "Please create the instance first:"
    echo "  gcloud sql instances create $DB_INSTANCE_NAME \\"
    echo "    --database-version=MYSQL_8_0 \\"
    echo "    --tier=db-f1-micro \\"
    echo "    --region=$REGION \\"
    echo "    --storage-auto-increase \\"
    echo "    --storage-size=10GB \\"
    echo "    --project=$PROJECT_ID"
    echo ""
    echo "Then create database and user:"
    echo "  gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME --project=$PROJECT_ID"
    echo "  gcloud sql users create $DB_USER --instance=$DB_INSTANCE_NAME --password=YOUR_PASSWORD --project=$PROJECT_ID"
    exit 1
fi
echo -e "${GREEN}✓ Instance: $INSTANCE_CONNECTION_NAME${NC}"
echo ""

# Prompt for database password
echo -e "${YELLOW}Enter database password for user '$DB_USER':${NC}"
read -s DB_PASSWORD
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_TAG" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --allow-unauthenticated \
    --add-cloudsql-instances="$INSTANCE_CONNECTION_NAME" \
    --set-env-vars="DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@/cloudsql/${INSTANCE_CONNECTION_NAME}/${DB_NAME}" \
    --set-env-vars="SECRET_KEY=$(openssl rand -base64 32)" \
    --set-env-vars="ALLOWED_ORIGINS=https://your-frontend-domain.com" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --min-instances=0 \
    --max-instances=10

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")

echo ""
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}API Docs:   ${SERVICE_URL}/docs${NC}"
echo ""
echo "To test your deployment:"
echo "  curl $SERVICE_URL"
echo ""
echo "To view logs:"
echo "  gcloud run logs tails $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
