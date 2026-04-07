# 📦 DEPLOY LAMBDA - SIMPLE WAY (ZIP Upload)

This is MUCH simpler and faster than Docker. Follow these exact steps.

---

## Step 1: Create Package Directory

```bash
cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"

# Create directory for Lambda package
mkdir lambda_package
cd lambda_package
```

---

## Step 2: Copy Files into Package

```bash
# Copy your handler
copy ..\02_lambda_handler.py lambda_function.py

# Copy lightweight requirements for Lambda
copy ..\requirements-lambda.txt requirements.txt
```

---

## Step 3: Install Dependencies

```bash
# Install all packages into the current directory
pip install -r requirements.txt -t .

# This creates all packages in the current folder
# (Don't use -q flag, we want to see the progress)
```

---

## Step 4: Create ZIP File

```bash
# Create the ZIP (PowerShell)
Compress-Archive -Path .\ -DestinationPath ..\plagiarism-lambda.zip

# Or on Linux/Mac:
# zip -r ../plagiarism-lambda.zip .

# Go back to main directory
cd ..

# Verify ZIP was created:
ls -la *.zip
```

---

## Step 5: Create Lambda Function in AWS Console

1. Go to: https://console.aws.amazon.com/lambda/
2. Click "Create function"
3. Select "Author from scratch"
4. Fill in:
   - **Function name:** plagiarism-detection
   - **Runtime:** Python 3.9
   - **Role:** plagiarism-lambda-role
5. Click "Create function"

---

## Step 6: Upload ZIP Code

1. In the Lambda function page, scroll to "Code source"
2. Click "Upload from" → ".zip file"
3. Select your `plagiarism-lambda.zip`
4. Click "Save"

---

## Step 7: Set Handler

1. Scroll to "Runtime settings"
2. Change Handler from `index.handler` to:
   ```
   lambda_function.lambda_handler
   ```
3. Click "Save"

---

## Step 8: Configure Timeout & Memory

1. Click "Configuration" tab
2. Click "General configuration" → "Edit"
3. Set:
   - **Timeout:** 300 seconds
   - **Memory:** 3008 MB
4. Click "Save"

---

## Step 9: Add Environment Variables

1. Click "Environment variables" → "Edit"
2. Add these variables (copy from your .env file):
   - RDS_HOST: plagiarism-db.cpmigym2oym2.us-east-2.rds.amazonaws.com
   - RDS_PORT: 5432
   - RDS_USER: postgres
   - RDS_PASSWORD: Plagiarism123!
   - RDS_DB: plagiarism_db
   - S3_BUCKET_NAME: plagiarism-detection-docs-augustin
   - PINECONE_API_KEY: pcsk_4GCKs...
   - HUGGINGFACE_API_KEY: hf_yAskBr...
   - PINECONE_INDEX_NAME: plagiarism-vectors
   - PINECONE_ENVIRONMENT: us-west1-gcp
   - EMBEDDING_MODEL: sentence-transformers/all-MiniLM-L6-v2
3. Click "Save"

---

## ✅ Done!

Your Lambda function is now deployed and configured!

Come back and tell me when Lambda shows "Active" status.
