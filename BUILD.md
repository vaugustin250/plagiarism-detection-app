# AI Plagiarism Detection System - Build Instructions

This file documents how the project was built locally.

## Environment Setup Completed ✅

### Environment Details
- **Python Version:** 3.10.11
- **Python Location:** `C:/Users/Nandha Kumar S K/AppData/Local/Programs/Python/Python310/python.exe`

### Files Created
1. **requirements.txt** - All Python dependencies (40+ packages)
2. **.env.example** - Environment variables template
3. **Dockerfile.lambda** - Docker container for AWS Lambda

### Packages Installed
Core AWS & Cloud Services:
- boto3, botocore

Database & Storage:
- psycopg2-binary, pinecone-client

Document Processing:
- PyPDF2, python-docx

Machine Learning:
- sentence-transformers, huggingface-hub, torch, transformers

Web Framework:
- streamlit, streamlit-option-menu

Data & Visualization:
- pandas, numpy, plotly, matplotlib, scikit-learn

Utilities:
- python-dotenv, requests, Pillow

## Next Steps to Deploy

### Step 1: Configure Environment Variables
```bash
# Copy example to .env
copy .env.example .env

# Edit .env with your actual values:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - RDS_HOST, RDS_USER, RDS_PASSWORD
# - S3_BUCKET_NAME
# - PINECONE_API_KEY
# - HUGGINGFACE_API_KEY
```

### Step 2: Test Local Deployment (Optional)
```bash
# Run Streamlit dashboard locally
streamlit run 03_streamlit_dashboard.py
# Access at http://localhost:8501
```

### Step 3: Deploy to AWS
```bash
# 1. Setup AWS infrastructure (follow 01_AWS_SETUP_GUIDE.md)
aws configure  # Set your AWS credentials

# 2. Create S3 bucket
aws s3 mb s3://plagiarism-detection-documents-yourname --region us-east-1

# 3. Build and push Lambda Docker image
docker build -f Dockerfile.lambda -t plagiarism-detection:latest .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag plagiarism-detection:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plagiarism-detection:latest

# 4. Deploy Streamlit dashboard
git push  # If using GitHub
# Or manually deploy to Streamlit Cloud: https://streamlit.io/cloud
```

### Step 4: Testing
```bash
# Test Lambda function
aws lambda invoke --function-name plagiarism-detection response.json

# Check CloudWatch logs
aws logs tail /aws/lambda/plagiarism-detection --follow
```

## Project Structure
```
.
├── 00_QUICK_START.md                 # Quick reference guide
├── 01_AWS_SETUP_GUIDE.md             # AWS infrastructure setup
├── 02_lambda_handler.py              # Lambda function (core)
├── 03_streamlit_dashboard.py         # Web dashboard
├── 04_DEPLOYMENT_GUIDE.md            # Detailed deployment
├── 05_PROJECT_REPORT.md              # Academic report template
├── requirements.txt                  # Python dependencies ✅
├── .env.example                      # Environment template ✅
└── Dockerfile.lambda                 # Lambda container ✅
```

## Key AWS Resources to Create (from 01_AWS_SETUP_GUIDE.md)
1. ✅ S3 Bucket - Document storage
2. ✅ RDS PostgreSQL - Data persistence
3. ✅ Lambda IAM Role - Execution permissions
4. ✅ Pinecone Index - Vector embeddings
5. ✅ HuggingFace Account - ML models
6. ✅ API Gateway - REST API
7. ✅ CloudWatch - Logging & monitoring

## Architecture
```
Student Upload (PDF/DOCX)
        ↓
   Streamlit UI
        ↓
   API Gateway
        ↓
  AWS Lambda (Serverless Processing)
        ↓
   ┌────────┬──────┬──────────┬────────────┐
   ↓        ↓      ↓          ↓            ↓
  S3      RDS  Pinecone  HuggingFace   SageMaker
Files    Data  Vectors   Embeddings   (Optional)
```

## Common Issues & Fixes

### Issue: ImportError for dependencies
**Solution:** Reinstall packages
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: AWS credentials not found
**Solution:** Configure AWS CLI
```bash
aws configure
```

### Issue: PostgreSQL connection failed
**Solution:** Update RDS_HOST, RDS_USER, RDS_PASSWORD in .env

## Cost Estimation (AWS Free Tier)
- S3 Storage: Free (5GB/month)
- RDS: Free (750 hours/month on db.t3.micro)
- Lambda: Free (1M requests/month)
- **Total Cost:** $0-5/month typically
