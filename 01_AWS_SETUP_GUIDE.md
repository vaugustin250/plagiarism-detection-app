# AI Plagiarism Detection System - AWS Setup Guide

## Project Overview
A cloud-native AI system that detects plagiarism and AI-generated content in academic documents using serverless computing, machine learning, and vector databases.

---

## Prerequisites
- AWS Account (Free Tier eligible)
- GitHub Account
- Docker installed locally
- Python 3.9+
- AWS CLI configured

---

## Part 1: AWS Services Setup

### 1.1 Create S3 Bucket for Document Storage

```bash
# Set your bucket name
BUCKET_NAME="plagiarism-detection-documents-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "S3 Bucket created: $BUCKET_NAME"
```

### 1.2 Create RDS PostgreSQL Database

```bash
# Create security group for RDS
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name plagiarism-rds-sg \
  --description "Security group for plagiarism detection RDS" \
  --query 'GroupId' \
  --output text)

# Allow PostgreSQL port
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier plagiarism-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password "YourSecurePassword123!" \
  --allocated-storage 20 \
  --vpc-security-group-ids $SECURITY_GROUP_ID \
  --publicly-accessible \
  --no-copy-tags-from-source \
  --storage-type gp2

echo "RDS instance being created..."
echo "Wait 5-10 minutes for it to be ready"
```

### 1.3 Create Lambda IAM Role

```bash
# Create IAM role for Lambda
LAMBDA_ROLE=$(aws iam create-role \
  --role-name plagiarism-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }' \
  --query 'Role.Arn' \
  --output text)

# Attach policies
aws iam attach-role-policy \
  --role-name plagiarism-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name plagiarism-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name plagiarism-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

echo "Lambda IAM Role: $LAMBDA_ROLE"
```

### 1.4 Setup Pinecone Vector Database

```bash
# Create Pinecone account at https://www.pinecone.io/
# Create index via console:
# - Index name: plagiarism-vectors
# - Dimension: 384 (for all-MiniLM-L6-v2 model)
# - Metric: cosine
# - Environment: Starter (free tier)

# Store API key in AWS Secrets Manager
PINECONE_API_KEY="your-pinecone-api-key"
aws secretsmanager create-secret \
  --name plagiarism/pinecone-api-key \
  --secret-string $PINECONE_API_KEY

echo "Pinecone index created and API key stored"
```

### 1.5 Setup HuggingFace Model Access

```bash
# HuggingFace setup (free)
# 1. Create account at https://huggingface.co/
# 2. Get API token from Settings > Access Tokens
# 3. Store in AWS Secrets Manager

HUGGINGFACE_TOKEN="your-huggingface-token"
aws secretsmanager create-secret \
  --name plagiarism/huggingface-token \
  --secret-string $HUGGINGFACE_TOKEN

echo "HuggingFace token stored"
```

### 1.6 Create SageMaker Notebook (Optional - for model training)

```bash
# Create SageMaker notebook for AI detection model training
aws sagemaker create-notebook-instance \
  --notebook-instance-name plagiarism-training \
  --instance-type ml.t3.medium \
  --role-arn arn:aws:iam::ACCOUNT-ID:role/SageMakerRole

echo "SageMaker notebook created"
echo "Access at: https://console.aws.amazon.com/sagemaker/home"
```

---

## Part 2: Environment Variables & Secrets

Create `.env.example`:
```
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
RDS_HOST=your-rds-endpoint.amazonaws.com
RDS_PORT=5432
RDS_USER=postgres
RDS_PASSWORD=your-password
RDS_DB=plagiarism_db

PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=plagiarism-vectors
PINECONE_ENVIRONMENT=us-west1-gcp

HUGGINGFACE_TOKEN=your-hf-token
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## Part 3: Database Schema

```sql
-- Create tables in PostgreSQL RDS

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  user_email VARCHAR(255),
  upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_size INT,
  s3_path VARCHAR(500),
  status VARCHAR(50) DEFAULT 'processing'
);

CREATE TABLE plagiarism_reports (
  id SERIAL PRIMARY KEY,
  document_id INT REFERENCES documents(id),
  overall_plagiarism_score FLOAT,
  ai_detection_score FLOAT,
  total_similar_documents INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  report_json JSONB
);

CREATE TABLE similarity_matches (
  id SERIAL PRIMARY KEY,
  report_id INT REFERENCES plagiarism_reports(id),
  matched_document_id INT REFERENCES documents(id),
  similarity_score FLOAT,
  matched_percentage FLOAT,
  source_url VARCHAR(500)
);

CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  document_id INT REFERENCES documents(id),
  status VARCHAR(100),
  message TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  error_details TEXT
);

-- Create indexes
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_plagiarism_document ON plagiarism_reports(document_id);
CREATE INDEX idx_similarity_report ON similarity_matches(report_id);
```

---

## Part 4: Cost Estimation

| Service | Monthly Cost (Free Tier) |
|---------|--------------------------|
| S3 Storage | $0 (1GB free, then $0.023/GB) |
| Lambda | $0 (1M requests free) |
| RDS | $0 (750 hours t3.micro free) |
| Pinecone Vector DB | $0 (Starter tier free) |
| **Total** | **~$0-5** |

---

## Part 5: Deployment Checklist

- [ ] AWS Account created
- [ ] S3 bucket configured
- [ ] RDS instance running
- [ ] Lambda IAM role created
- [ ] Pinecone account & index created
- [ ] HuggingFace token obtained
- [ ] Database schema created
- [ ] Environment variables set
- [ ] Docker installed locally
- [ ] GitHub repo created

---

## Troubleshooting

### Lambda Timeout Issues
- Increase timeout to 5 minutes in Lambda console
- Increase memory to 3008 MB

### RDS Connection Error
- Check security group allows port 5432
- Verify RDS is publicly accessible
- Test with: `psql -h <rds-endpoint> -U postgres`

### Pinecone Connection Failed
- Verify API key is correct
- Check index name matches configuration
- Ensure index dimension is 384

---

## Next Steps
1. Deploy Lambda function
2. Setup API Gateway
3. Deploy Streamlit frontend
4. Configure CI/CD pipeline

