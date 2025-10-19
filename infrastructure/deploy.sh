#!/bin/bash

set -e

echo "====================================="
echo "LeniLani Lead Generation Platform"
echo "Deployment Script"
echo "====================================="

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Building Backend Docker Image${NC}"
cd ../backend
docker build -t gcr.io/${GCP_PROJECT_ID}/lenilani-backend:latest .

echo -e "${BLUE}Step 2: Pushing Backend to Google Container Registry${NC}"
docker push gcr.io/${GCP_PROJECT_ID}/lenilani-backend:latest

echo -e "${BLUE}Step 3: Deploying Backend to Cloud Run${NC}"
gcloud run deploy lenilani-backend \
  --image gcr.io/${GCP_PROJECT_ID}/lenilani-backend:latest \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars="ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY},GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY},OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

BACKEND_URL=$(gcloud run services describe lenilani-backend --platform managed --region us-west1 --format 'value(status.url)')
echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

echo -e "${BLUE}Step 4: Building Frontend${NC}"
cd ../frontend
export NEXT_PUBLIC_API_URL=$BACKEND_URL
npm install
npm run build

echo -e "${BLUE}Step 5: Deploying Frontend to Vercel${NC}"
if command -v vercel &> /dev/null; then
    vercel --prod --yes
else
    echo "Vercel CLI not found. Please install with: npm i -g vercel"
    echo "Then run: vercel --prod"
fi

echo -e "${GREEN}====================================="
echo "Deployment Complete!"
echo "=====================================${NC}"
echo "Backend URL: ${BACKEND_URL}"
echo "Frontend: Check Vercel output for URL"
