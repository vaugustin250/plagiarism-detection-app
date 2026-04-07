# AI Plagiarism Detection System - API & Deployment Guide

## System Architecture

```
┌─────────────────┐
│  User Upload    │  (Streamlit Dashboard)
│  (Browser)      │
└────────┬────────┘
         │ (HTTPS)
         ▼
┌──────────────────────┐
│  API Gateway         │  (REST Endpoint)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Lambda Function     │  (Serverless Processing)
│  - Extract text      │
│  - Generate embeddings
│  - Find similar docs │
└──────┬───────────────┘
       │
   ┌───┼────┬─────────────┐
   ▼   ▼    ▼             ▼
  S3  RDS Pinecone  HuggingFace
 (PDF) (Data) (Vectors)  (Models)
```

---

## API Endpoints

### 1. Upload Document

**Endpoint:** `POST /api/upload`

**Request:**
```bash
curl -X POST https://your-api-gateway.amazonaws.com/upload \
  -F "file=@assignment.pdf" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "document_id": 42,
  "status": "processing",
  "message": "Document uploaded. Lambda function triggered."
}
```

---

### 2. Get Report

**Endpoint:** `GET /api/report/{document_id}`

**Request:**
```bash
curl -X GET https://your-api-gateway.amazonaws.com/report/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "document_id": 42,
  "filename": "assignment.pdf",
  "overall_plagiarism_score": 23.5,
  "ai_detection_score": 15.2,
  "total_similar_documents": 3,
  "similar_documents": [
    {
      "document_id": 15,
      "filename": "related_paper.pdf",
      "similarity_score": 0.756
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. List All Documents

**Endpoint:** `GET /api/documents`

**Query Parameters:**
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset (default: 0)
- `status`: Filter by status (processing, completed, error)

**Response:**
```json
{
  "documents": [
    {
      "id": 42,
      "filename": "assignment.pdf",
      "upload_time": "2024-01-15T10:20:00Z",
      "status": "completed",
      "plagiarism_score": 23.5
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### 4. Delete Document

**Endpoint:** `DELETE /api/documents/{document_id}`

**Request:**
```bash
curl -X DELETE https://your-api-gateway.amazonaws.com/documents/42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## Deployment Steps

### Step 1: Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourusername/plagiarism-detection.git
cd plagiarism-detection

# Create .env file
cp .env.example .env
# Edit .env with your AWS credentials and API keys

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Deploy Infrastructure (Terraform Alternative)

```bash
# Initialize Terraform
cd infrastructure/
terraform init

# Plan deployment
terraform plan -var-file="production.tfvars"

# Apply configuration
terraform apply -var-file="production.tfvars"
```

### Step 3: Deploy Lambda Function

```bash
# Build Docker image
docker build -f Dockerfile.lambda -t plagiarism-detection:latest .

# Tag for ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag plagiarism-detection:latest \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:latest

# Push to ECR
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:latest

# Create/Update Lambda function
aws lambda create-function \
  --function-name plagiarism-detection \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/plagiarism-lambda-role \
  --code ImageUri=YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:latest \
  --package-type Image \
  --timeout 300 \
  --memory-size 3008 \
  --environment Variables='{
    "RDS_HOST=your-endpoint.rds.amazonaws.com",
    "S3_BUCKET=plagiarism-documents",
    "PINECONE_API_KEY=your-key",
    "HUGGINGFACE_TOKEN=your-token"
  }' \
  --region us-east-1

# Configure Lambda environment variables
aws lambda update-function-configuration \
  --function-name plagiarism-detection \
  --environment Variables='{key1=value1,key2=value2}'
```

### Step 4: Setup API Gateway

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
  --name plagiarism-api \
  --description "Plagiarism Detection API" \
  --query 'id' --output text)

# Create /upload resource
RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' --output text)

UPLOAD_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $RESOURCE_ID \
  --path-part upload \
  --query 'id' --output text)

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $UPLOAD_RESOURCE \
  --http-method POST \
  --authorization-type AWS_IAM

# Create Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $UPLOAD_RESOURCE \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:plagiarism-detection/invocations

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name production
```

### Step 5: Deploy Streamlit Dashboard

**Option A: Streamlit Cloud (Easiest)**

```bash
# Push code to GitHub
git add .
git commit -m "Deploy plagiarism detection system"
git push origin main

# Go to https://share.streamlit.io/
# Click "New app"
# Connect your GitHub repo
# Select branch and main file: streamlit_dashboard.py
# Deploy!
```

**Option B: Google Cloud Run**

```bash
# Create Docker image for Streamlit
cat > Dockerfile.streamlit << EOF
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit_dashboard.py .
COPY .streamlit/ .streamlit/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py"]
EOF

# Build and push
docker build -f Dockerfile.streamlit -t plagiarism-dashboard:latest .
docker tag plagiarism-dashboard \
  gcr.io/YOUR_PROJECT_ID/plagiarism-dashboard:latest
docker push gcr.io/YOUR_PROJECT_ID/plagiarism-dashboard:latest

# Deploy to Cloud Run
gcloud run deploy plagiarism-dashboard \
  --image gcr.io/YOUR_PROJECT_ID/plagiarism-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 6: Configure S3 Trigger

```bash
# Add Lambda permission for S3
aws lambda add-permission \
  --function-name plagiarism-detection \
  --statement-id AllowS3Invoke \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::plagiarism-documents

# Add S3 event notification
aws s3api put-bucket-notification-configuration \
  --bucket plagiarism-documents \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [
      {
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:plagiarism-detection",
        "Events": ["s3:ObjectCreated:*"],
        "Filter": {
          "Key": {
            "FilterRules": [
              {
                "Name": "prefix",
                "Value": "submissions/"
              }
            ]
          }
        }
      }
    ]
  }'
```

### Step 7: Configure CI/CD Pipeline

```bash
# Add GitHub secrets
gh secret set AWS_ACCESS_KEY_ID -b "your-key-id"
gh secret set AWS_SECRET_ACCESS_KEY -b "your-secret-key"
gh secret set SLACK_WEBHOOK -b "your-slack-webhook-url"

# Create .github/workflows/deploy.yml
mkdir -p .github/workflows
cp .github_workflows_deploy.yml .github/workflows/deploy.yml

# Push to trigger pipeline
git add .
git commit -m "Setup CI/CD pipeline"
git push origin main
```

---

## Testing

### Unit Tests

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Check coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
# Test Lambda locally with SAM
sam local start-api

# Test upload endpoint
curl -X POST http://localhost:3000/upload \
  -F "file=@test_document.pdf"

# Test report endpoint
curl -X GET http://localhost:3000/report/1
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class PlagiarismUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_report(self):
        self.client.get("/report/1")
    
    @task(3)
    def list_documents(self):
        self.client.get("/documents")
EOF

# Run load test
locust -f locustfile.py --host=https://your-api.amazonaws.com
```

---

## Monitoring & Logging

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/plagiarism-detection --follow

# View specific errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/plagiarism-detection \
  --filter-pattern "ERROR"
```

### Set CloudWatch Alarms

```bash
# Alert on high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name plagiarism-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=plagiarism-detection

# Alert on timeout
aws cloudwatch put-metric-alarm \
  --alarm-name plagiarism-lambda-duration \
  --alarm-description "Alert on long duration" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 60000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=plagiarism-detection
```

---

## Cost Optimization

1. **Lambda**: 
   - Use Reserved Concurrency for predictable workloads
   - Optimize memory allocation (3GB reduces CPU time)

2. **RDS**:
   - Use db.t3.micro for development (free tier)
   - Enable auto-pause for development databases

3. **S3**:
   - Enable lifecycle policies to move old documents to Glacier
   - Use S3 Intelligent-Tiering

4. **Pinecone**:
   - Use Starter tier (free) for development
   - Scale to production tier as needed

---

## Security Best Practices

1. **Store secrets in AWS Secrets Manager**
   ```bash
   aws secretsmanager create-secret --name plagiarism/api-key --secret-string "your-key"
   ```

2. **Enable VPC for RDS**
   - Restrict database access to Lambda only

3. **Use IAM roles**
   - Principle of least privilege
   - Separate roles for different functions

4. **Enable encryption**
   - S3: Server-side encryption (SSE-S3)
   - RDS: Encrypted storage & backups
   - API: Use HTTPS only

5. **Enable logging & monitoring**
   - CloudTrail for API calls
   - VPC Flow Logs for network traffic

---

## Troubleshooting

### Lambda Timeout
- Increase timeout to 5 minutes
- Increase memory allocation
- Optimize document processing code

### RDS Connection Failed
- Check security group rules
- Verify RDS is publicly accessible
- Check credentials in environment variables

### Pinecone API Errors
- Verify API key is correct
- Check index name matches
- Ensure sufficient quota

### Streamlit Not Loading
- Check environment variables are set
- Verify database connection
- Check browser console for errors

---

## Rollback Procedure

```bash
# Rollback Lambda to previous version
aws lambda update-function-code \
  --function-name plagiarism-detection \
  --image-uri YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:previous-tag

# Rollback API Gateway deployment
aws apigateway update-stage \
  --rest-api-id YOUR_API_ID \
  --stage-name production \
  --patch-operations 'op=replace,path=/deploymentId,value=PREVIOUS_DEPLOYMENT_ID'
```

---

## Support & Documentation

- AWS Lambda: https://docs.aws.amazon.com/lambda/
- API Gateway: https://docs.aws.amazon.com/apigateway/
- Pinecone: https://docs.pinecone.io/
- Streamlit: https://docs.streamlit.io/
- PostgreSQL: https://www.postgresql.org/docs/
