# Complete API & Services Setup Guide

## 🎯 All Services Needed for This Project

### Service Dependencies Map
```
YOUR PROJECT
    ├── AWS Account (Main cloud provider)
    │   ├── S3 (File storage)
    │   ├── Lambda (Processing engine)
    │   ├── RDS PostgreSQL (Database)
    │   ├── API Gateway (REST API)
    │   ├── Secrets Manager (Store API keys)
    │   └── CloudWatch (Logging)
    │
    ├── Pinecone (Vector database) - AI embeddings search
    │
    ├── HuggingFace (ML models) - Text embeddings & AI detection
    │
    ├── Streamlit Cloud (Optional - dashboard hosting)
    │
    └── GitHub (Optional - CI/CD deployment)
```

---

## 📋 Complete Setup Checklist

### ✅ Step 1: AWS Account Setup (5 minutes)
**Cost: FREE for first 12 months with free tier**

1. Go to https://aws.amazon.com/
2. Click "Create AWS Account"
3. Fill in email, password, and billing info (credit card required but won't charge)
4. Select "Basic Plan"
5. Verify phone number
6. **Your Account ID:** (You'll need this later)

**After Account Creation:**
```bash
# Install AWS CLI (if not already installed)
# Windows: Use AWS CLI installer from https://aws.amazon.com/cli/

# Configure AWS CLI with your credentials
aws configure
# It will ask for:
# - AWS Access Key ID: (Get from AWS Console > IAM > Users > Security Credentials)
# - AWS Secret Access Key: (Same location)
# - Default region name: us-east-1
# - Default output format: json
```

---

### ✅ Step 2: AWS S3 (File Storage) - 5 minutes
**Cost: FREE (5GB/month free)**

```bash
# Run this command to create S3 bucket
aws s3 mb s3://plagiarism-detection-documents-yourname --region us-east-1

# Store bucket name in .env file
# S3_BUCKET_NAME=plagiarism-detection-documents-yourname
```

✅ **Done!** S3 is now ready.

---

### ✅ Step 3: AWS RDS PostgreSQL (Database) - 15 minutes
**Cost: FREE (750 hours/month on db.t3.micro)**

**Via AWS Console (Easiest):**
1. Go to https://console.aws.amazon.com/rds/
2. Click "Create database"
3. Select "PostgreSQL"
4. Under "Templates" → Select "Free tier"
5. Set:
   - **DB instance identifier:** plagiarism-db
   - **Master username:** postgres
   - **Password:** YourSecurePassword123!
6. Click "Create database"
7. Wait 5-10 minutes for it to be created

**Get Connection Details:**
1. Click on your database name
2. Find "Endpoint" (example: plagiarism-db.c9akciq32.us-east-1.rds.amazonaws.com)
3. Copy to `.env`:
```
RDS_HOST=plagiarism-db.c9akciq32.us-east-1.rds.amazonaws.com
RDS_PORT=5432
RDS_USER=postgres
RDS_PASSWORD=YourSecurePassword123!
RDS_DB=plagiarism_db
```

**Create Database Schema (Run once):**
```bash
# Install psql (PostgreSQL client)
# Download from: https://www.postgresql.org/download/

# Connect to RDS and create database
psql -h your-rds-endpoint.amazonaws.com -U postgres -d postgres -c "CREATE DATABASE plagiarism_db;"

# Connect to new database
psql -h your-rds-endpoint.amazonaws.com -U postgres -d plagiarism_db

# Paste this SQL:
```

**SQL Schema:**
```sql
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
  source_url VARCHAR(500)
);

CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  document_id INT REFERENCES documents(id),
  status VARCHAR(100),
  message TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_plagiarism_document ON plagiarism_reports(document_id);
```

✅ **Done!** Database is ready.

---

### ✅ Step 4: Pinecone Vector Database - 10 minutes
**Cost: FREE (Starter tier - 100K vectors)**

**What it does:** Stores document embeddings for fast similarity search

1. Go to https://www.pinecone.io/
2. Click "Sign up free"
3. Create account with email
4. Click "Create index"
5. Set:
   - **Name:** plagiarism-vectors
   - **Dimension:** 384
   - **Metric:** cosine
   - **Environment:** Starter (free tier)
6. Click "Create Index"
7. Go to "API Keys" and copy your key

**Add to .env:**
```
PINECONE_API_KEY=your-copied-api-key-here
PINECONE_INDEX_NAME=plagiarism-vectors
PINECONE_ENVIRONMENT=us-west1-gcp
```

✅ **Done!** Pinecone is ready.

---

### ✅ Step 5: HuggingFace API (ML Models) - 5 minutes
**Cost: FREE (Public APIs with rate limits)**

**What it does:** Generates embeddings and detects AI content

1. Go to https://huggingface.co/
2. Click "Sign Up"
3. Create account
4. Go to Settings → Access Tokens
5. Click "New token"
6. Give it a name: "plagiarism-detection"
7. Select "read" access
8. Copy the token

**Add to .env:**
```
HUGGINGFACE_API_KEY=hf_your_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

✅ **Done!** HuggingFace is ready.

---

### ✅ Step 6: AWS Lambda & API Gateway - 10 minutes
**Cost: FREE (1M requests/month)**

**Create Lambda Function:**
```bash
# 1. Go to AWS Lambda console: https://console.aws.amazon.com/lambda/
# 2. Click "Create function"
# 3. Set:
#    - Function name: plagiarism-detection
#    - Runtime: Python 3.9
#    - Architecture: x86_64
# 4. Click "Create function"

# 5. Build and push Docker image (we'll do this later)
docker build -f Dockerfile.lambda -t plagiarism-detection:latest .
```

**Create API Gateway:**
```bash
# 1. Go to API Gateway: https://console.aws.amazon.com/apigateway/
# 2. Click "Create API" → REST API
# 3. Set name: plagiarism-detection-api
# 4. Click "Create API"
# 5. Add Lambda integration (connect to your Lambda function)
# 6. Deploy to stage "prod"
# 7. You'll get an API URL like:
#    https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

**Add to .env:**
```
LAMBDA_FUNCTION_NAME=plagiarism-detection
API_GATEWAY_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

✅ **Done!** Lambda & API Gateway ready.

---

### ✅ Step 7: AWS Secrets Manager (Store Keys Safely) - 5 minutes
**Cost: FREE**

Instead of storing API keys in .env, store them in AWS Secrets Manager:

```bash
# Store Pinecone key
aws secretsmanager create-secret \
  --name plagiarism/pinecone-api-key \
  --secret-string "your-pinecone-api-key"

# Store HuggingFace token
aws secretsmanager create-secret \
  --name plagiarism/huggingface-token \
  --secret-string "your-huggingface-token"

# Store RDS password
aws secretsmanager create-secret \
  --name plagiarism/rds-password \
  --secret-string "YourSecurePassword123!"
```

✅ **Done!** Keys are secure.

---

## 📊 Complete .env File Template

Copy this to `.env` after setting up all services:

```env
# ===== AWS Configuration =====
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# ===== S3 (File Storage) =====
S3_BUCKET_NAME=plagiarism-detection-documents-yourname

# ===== RDS PostgreSQL (Database) =====
RDS_HOST=plagiarism-db.abc123.us-east-1.rds.amazonaws.com
RDS_PORT=5432
RDS_USER=postgres
RDS_PASSWORD=YourSecurePassword123!
RDS_DB=plagiarism_db

# ===== Pinecone (Vector Database) =====
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=plagiarism-vectors
PINECONE_ENVIRONMENT=us-west1-gcp

# ===== HuggingFace (ML Models) =====
HUGGINGFACE_API_KEY=hf_your_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ===== Lambda & API Gateway =====
LAMBDA_FUNCTION_NAME=plagiarism-detection
API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod

# ===== Streamlit Configuration =====
STREAMLIT_PORT=8501
STREAMLIT_SERVER_HEADLESS=true

# ===== Model Thresholds =====
PLAGIARISM_THRESHOLD=0.7
AI_DETECTION_THRESHOLD=0.6
```

---

## 🚀 Quick Setup Command Reference

```bash
# 1. Configure AWS
aws configure

# 2. Create S3 bucket
aws s3 mb s3://plagiarism-detection-documents-yourname --region us-east-1

# 3. Store secrets
aws secretsmanager create-secret --name plagiarism/pinecone-api-key --secret-string "your-key"
aws secretsmanager create-secret --name plagiarism/huggingface-token --secret-string "your-token"

# 4. Create .env file
cp .env.example .env
# Edit .env with your actual values

# 5. Test database connection
psql -h your-rds-endpoint.amazonaws.com -U postgres -d plagiarism_db

# 6. Test Pinecone connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='your-key'); print(pc.list_indexes())"

# 7. Test HuggingFace
curl -X POST https://api-inference.huggingface.co/pipeline/feature-extraction \
  -H "Authorization: Bearer your-token" \
  -d '{"inputs":"test"}'
```

---

## 💰 Total Cost Breakdown

| Service | Free Tier | Paid | Notes |
|---------|-----------|------|-------|
| **AWS S3** | 5 GB/month | $0.023/GB | Free for small projects |
| **AWS Lambda** | 1M requests/month | Pay per use | Probably free for you |
| **AWS RDS** | 750 hours/month | $0/month on t3.micro | Free for 12 months |
| **Pinecone** | 100K vectors | $0.25M more | Starter tier is free |
| **HuggingFace** | Unlimited read | Unlimited | Free APIs |
| **API Gateway** | 1M requests/month | $3.50/M more | Likely free for you |
| **Secrets Manager** | 40 free secrets | $0.40 more | Very cheap |
| **TOTAL** | **FREE** | **$0-5/month** | Within free tier! |

---

## ⚠️ Common Issues & Fixes

### Issue: "Access Denied" when running AWS commands
**Fix:** Run `aws configure` and provide correct Access Key ID and Secret Access Key

### Issue: RDS connection refused
**Fix:** 
- Check security group allows port 5432
- Make sure RDS is "publicly accessible" 
- Test with: `psql -h endpoint -U postgres`

### Issue: Pinecone API key not working
**Fix:** 
- Copy key again from Pinecone console
- Make sure you're using the right index name
- Check environment matches your region

### Issue: HuggingFace rate limited
**Fix:**
- Add delays between API calls
- Use model downloads locally instead of API
- Upgrade HuggingFace to Pro ($9/month)

---

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# ✅ AWS CLI
aws s3 ls

# ✅ S3 Bucket
aws s3 ls s3://plagiarism-detection-documents-yourname/

# ✅ RDS Database
psql -h your-endpoint -U postgres -d plagiarism_db -c "SELECT 1;"

# ✅ Pinecone
python -c "from pinecone import Pinecone; print('✅ Pinecone OK')"

# ✅ HuggingFace
curl -X POST https://api-inference.huggingface.co/pipeline/feature-extraction \
  -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
  -d '{"inputs":"test"}' | grep -q inputs && echo "✅ HuggingFace OK"

# ✅ All dependencies installed
python -c "import boto3; import psycopg2; import pinecone; import streamlit; print('✅ All packages OK')"
```

---

## 🎯 What Each API Does in Your Project Flow

```
User uploads PDF
        ↓
[S3] - Store file in bucket
        ↓
[Lambda] - Triggered by S3 upload event
        ↓
        ├─→ [HuggingFace] - Generate embeddings
        │        ↓
        │   [Pinecone] - Store vectors for search
        │
        ├─→ [HuggingFace] - Detect if AI-generated
        │
        └─→ [RDS Database] - Store results & reports
        ↓
[Streamlit Dashboard] - Display results to user
        ↓
User sees plagiarism score & AI detection results
```

---

## 📞 Support Links

- AWS Help: https://console.aws.amazon.com/support/
- Pinecone Docs: https://docs.pinecone.io/
- HuggingFace Docs: https://huggingface.co/docs
- Streamlit Docs: https://docs.streamlit.io/
