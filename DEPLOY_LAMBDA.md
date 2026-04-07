# 🚀 DEPLOY LAMBDA FUNCTION

Your Lambda function deployment has two options. Choose the easiest one.

---

## 🔧 OPTION 1: Use Docker (Recommended) - 30 minutes

### Step 1: Verify Docker is Installed
```bash
docker --version
# You should see: Docker version XX.X.X
```

If not installed, download from: https://www.docker.com/products/docker-desktop/

### Step 2: Build Docker Image
```bash
cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"

docker build -f Dockerfile.lambda -t plagiarism-detection:latest .

# Wait for build to complete (2-5 minutes)
# You should see: Successfully tagged plagiarism-detection:latest
```

### Step 3: Create ECR Repository
```bash
aws ecr create-repository \
  --repository-name plagiarism-detection \
  --region us-east-2
```

### Step 4: Login to ECR
```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 093954665664.dkr.ecr.us-east-2.amazonaws.com

# You should see: Login Succeeded
```

### Step 5: Tag Docker Image
```bash
docker tag plagiarism-detection:latest 093954665664.dkr.ecr.us-east-2.amazonaws.com/plagiarism-detection:latest
```

### Step 6: Push to AWS
```bash
docker push 093954665664.dkr.ecr.us-east-2.amazonaws.com/plagiarism-detection:latest

# Wait for upload to complete (5-10 minutes)
# You should see: latest: digest: sha256:...
```

### Step 7: Create Lambda Function in AWS Console
1. Go to: https://console.aws.amazon.com/lambda/
2. Click "Create function"
3. Select "Container image"
4. Fill in:
   - Function name: plagiarism-detection
   - Container image URI: 093954665664.dkr.ecr.us-east-2.amazonaws.com/plagiarism-detection:latest
   - Role: plagiarism-lambda-role
5. Click "Create function"

### Step 8: Configure Lambda
1. Click "Configuration" tab
2. Click "General configuration"
3. Set:
   - Timeout: 300 seconds (5 minutes)
   - Memory: 3008 MB
4. Click "Save"

### Step 9: Add Environment Variables
1. Click "Environment variables"
2. Click "Edit"
3. Add all your .env variables:
   - RDS_HOST
   - RDS_USER
   - RDS_PASSWORD
   - RDS_DB
   - S3_BUCKET_NAME
   - PINECONE_API_KEY
   - HUGGINGFACE_API_KEY
   - etc.
4. Click "Save"

---

## 📦 OPTION 2: Manual ZIP Upload - 15 minutes (SIMPLER)

### Step 1: Create ZIP File
```bash
cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"

# Create a package directory
mkdir lambda_package
cd lambda_package

# Copy your handler
copy ..\02_lambda_handler.py lambda_function.py

# Copy requirements
copy ..\requirements.txt .

# Install dependencies into package
pip install -r requirements.txt -t .

# Create ZIP
Compress-Archive -Path .\ -DestinationPath ..\lambda_function.zip

cd ..
```

### Step 2: Create Lambda Function via Console
1. Go to: https://console.aws.amazon.com/lambda/
2. Click "Create function"
3. Select "Author from scratch"
4. Fill in:
   - Function name: plagiarism-detection
   - Runtime: Python 3.9
   - Role: plagiarism-lambda-role
5. Click "Create function"

### Step 3: Upload Code
1. In function page, scroll to "Code source"
2. Click "Upload from" → ".zip file"
3. Upload your lambda_function.zip
4. Click "Save"

### Step 4: Set Handler
1. Under "Runtime settings", change handler to:
   lambda_function.lambda_handler

### Step 5: Configure
Same as Option 1 Step 8-9 above

---

## ✅ After Deployment

Come back and tell me:
1. Lambda function name: plagiarism-detection
2. Status: Active

Then I'll:
- Setup API Gateway
- Deploy Streamlit dashboard
- Test everything!
