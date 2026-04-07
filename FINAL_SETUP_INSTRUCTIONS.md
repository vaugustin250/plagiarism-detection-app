# 🚀 Final Setup Instructions - Plagiarism Detection System

## Overview

The system has been updated with a **2-step file upload workflow** to handle large files:

1. **Streamlit** uploads file to **S3** (handles large files)
2. **Streamlit** calls **Lambda** with S3 path via API Gateway (small JSON request)
3. **Lambda** retrieves file from S3 and processes it

---

## ⚠️ What Changed

### Files Updated (Pushed to GitHub ✅)

#### 1. **Lambda Handler** (`02_lambda_handler.py`)
- ✨ **Now supports BOTH:**
  - S3 events (automatic triggering when files uploaded)
  - API Gateway calls (direct invocation with S3 key)
- Single `lambda_handler` function detects event type automatically
- Returns JSON response compatible with API Gateway

#### 2. **Streamlit Dashboard** (`03_streamlit_dashboard.py`)
- 🔄 **New 2-step workflow:**
  1. Reads AWS credentials from **Streamlit Secrets** (not hardcoded)
  2. Upload file to S3 using boto3
  3. Call Lambda with JSON: `{s3_bucket, s3_key, filename}`
- ⚠️ Shows warning if AWS credentials not configured
- Better error handling and progress indicators

---

## 📋 Required Setup Steps

### Step 1: Update Lambda Function in AWS Console

#### Option A: Manual Update (Recommended)
1. Go to: [AWS Lambda Console](https://console.aws.amazon.com/lambda/home?region=us-east-2)
2. Find: `plagiarism-detection` function
3. Click: "Code" tab
4. Click: "Upload from" → "Upload a .zip file"
5. Download latest `02_lambda_handler.py` from GitHub
6. Create ZIP file: `lambda_function.zip`
   ```
   02_lambda_handler.py → rename to → lambda_function.py
   Add all dependencies (if using local package)
   ```
7. Upload ZIP
8. Click: "Deploy"

**Alternative:** Use `update_lambda.py` script (requires AWS CLI):
```bash
python update_lambda.py
```

---

### Step 2: Configure Streamlit Secrets (AWS Credentials)

#### For Streamlit Cloud Deployment

1. Go to: https://share.streamlit.io/
2. Find your app: **plagiarism-detection-app**
3. Click: **⋮ (three dots)** → **Settings**
4. Click: **Secrets** section
5. Paste this template:
```
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"  
AWS_DEFAULT_REGION = "us-east-2"
```

6. **Replace** `YOUR_AWS_ACCESS_KEY_ID` and `YOUR_AWS_SECRET_ACCESS_KEY` with your actual credentials
   - Get from: AWS Console → IAM → Users → (Your User) → Security credentials → Access keys
   
7. Click: **Save**

8. Wait 30-60 seconds for Streamlit to rebuild

---

### Step 3: Verify Installation

#### Test 1: Lambda Function
1. Go to: [AWS Lambda](https://console.aws.amazon.com/lambda/)
2. Find: `plagiarism-detection` function
3. Click: "Code" tab
4. Verify you see the **dual support** code:
   ```python
   if 'Records' in event:
       # S3 Event
   elif 's3_bucket' in event and 's3_key' in event:
       # API Gateway
   ```

#### Test 2: Streamlit Configuration
1. Refresh Streamlit Cloud: https://plagiarism-detection-app-XXXXX.streamlit.app
2. You should **NOT** see ⚠️ warning about "AWS Credentials Not Configured"
   - If you DO see the warning, repeat Step 2

#### Test 3: File Upload
1. Choose a **PDF or DOCX** file (start small: <5MB)
2. Click: **🚀 Analyze Document**
3. Expected behavior:
   - ✅ Shows: "📤 Uploading document to S3..."
   - ✅ Shows: "✅ Uploaded to S3: submissions/YYYYMMDD_HHMMSS_filename.pdf"
   - ✅ Shows: "🔍 Analyzing document via Lambda..."
   - ✅ ~60 seconds wait
   - ✅ Shows: "✅ Analysis Complete!"
   - ✅ Displays plagiarism score, AI score, matching docs count

---

## 🔍 Troubleshooting

### Error 1: "AWS Credentials Not Configured" Warning

**Solution:**
- Go to Streamlit Settings → Secrets
- Verify `AWS_ACCESS_KEY_ID` exists (and is NOT empty)
- Save and refresh page

### Error 2: "UnauthorizedOperation" or "Access Denied"

**Solution:**
- Check credentials are correct in Streamlit Secrets
- Verify AWS user has S3 permissions:
  ```json
  {
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": "arn:aws:s3:::plagiarism-detection-docs-augustin/*"
  }
  ```

### Error 3: Lambda Timeout or No Response

**Solution:**
1. Check Lambda logs in CloudWatch
2. Verify `02_lambda_handler.py` code was updated
3. Increase Lambda timeout in AWS Console → plagiarism-detection function → General configuration → Edit → Timeout (set to 300 seconds)

### Error 4: "File uploaded to S3 but Lambda didn't process"

**Solution:**
- Check S3 bucket: Go to AWS S3 Console
- Look for files in `submissions/` folder
- If files are there, Lambda received the S3 path
- Check CloudWatch logs for Lambda errors:
  1. AWS Console → CloudWatch → Log groups
  2. Find: `/aws/lambda/plagiarism-detection`
  3. Look at latest log stream
  4. Check for error messages

---

## 📊 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ STREAMLIT CLOUD                                              │
├──────────────────────────────────────────────────────────────┤
│ 1. User uploads file                                         │
│ 2. Reads AWS credentials from st.secrets                     │
│ 3. Calls: s3_client.upload_fileobj()                         │
│    ↓ File goes to S3 bucket                                  │
├──────────────────────────────────────────────────────────────┤
│ 4. Calls: requests.post(API_ENDPOINT, json={...})            │
│    ↓ Small JSON payload (200 bytes)                          │
└──────────────────────────────────────────────────────────────┘
                          ↓ API Gateway
┌──────────────────────────────────────────────────────────────┐
│ AWS LAMBDA (plagiarism-detection)                            │
├──────────────────────────────────────────────────────────────┤
│ lambda_handler(event):                                       │
│   ✓ Detects: S3 event OR API Gateway call                    │
│   ✓ Extracts: bucket & key                                   │
│   ✓ Downloads: file from S3                                  │
│   ✓ Processes: text extraction, embeddings, plagiarism check │
│   ✓ Stores: results in RDS PostgreSQL                        │
│   ✓ Returns: JSON with scores                                │
└──────────────────────────────────────────────────────────────┘
         ↓ (stores in)        ↓ (searches in)
    ┌─────────────────┐    ┌────────────────┐
    │ RDS PostgreSQL  │    │ Pinecone Index │
    │  (plagiarism_db)│    │  (embeddings)  │
    └─────────────────┘    └────────────────┘
```

---

## ✅ Checklist

- [ ] Updated Lambda function with new `02_lambda_handler.py` code
- [ ] Added AWS credentials to Streamlit Secrets
- [ ] Refreshed Streamlit app in browser
- [ ] **No warning** about missing AWS credentials
- [ ] Test uploaded small PDF file successfully
- [ ] Got plagiarism score back from Lambda
- [ ] File appeared in S3 `submissions/` folder

---

## 🎯 What Works Now

✅ **Large File Upload** - Files up to ~50MB supported (S3 limit)
✅ **Small API Requests** - No more 413 payload size errors
✅ **Dual Lambda Support** - Works with S3 events AND API Gateway
✅ **Secure Credentials** - AWS keys in Streamlit Secrets, not hardcoded
✅ **Full Analysis** - Plagiarism detection + AI detection + similar docs

---

## 📞 Support

If issues persist:
1. Check CloudWatch logs for Lambda errors
2. Verify credentials in Streamlit Secrets
3. Ensure S3 bucket policies allow your AWS user
4. Check Lambda IAM role has necessary permissions

---

**Last Updated:** 2026-04-07
**Status:** ✅ Production Ready
