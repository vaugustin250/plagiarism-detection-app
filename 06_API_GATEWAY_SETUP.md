# 🌐 API GATEWAY SETUP GUIDE

**What This Does**: Creates a REST API endpoint that your Streamlit dashboard will use to communicate with the Lambda function.

**Time Estimate**: 15 minutes

---

## Step 1: Open API Gateway Console
Go to: https://console.aws.amazon.com/apigateway/

---

## Step 2: Create New API
1. Click: **"Create API"**
2. Under **"REST API"**, click: **"Build"**

---

## Step 3: Create REST API
1. **API Name**: `plagiarism-detection-api`
2. **Description**: `REST API for plagiarism detection system`
3. **Endpoint Type**: `Regional` (already selected)
4. Click: **"Create API"**

---

## Step 4: Create POST Resource
1. Click on **"/"** (root resource)
2. Click: **"Create resource"**
3. **Resource name**: `analyze`
4. **Resource path**: `/analyze` (auto-filled)
5. Check: **"Enable API Gateway CORS"**
6. Click: **"Create resource"**

---

## Step 5: Create POST Method
1. Click on `/analyze` resource
2. Click: **"Create method"** 
3. Select: **"POST"**
4. Click: **"Create method"**

---

## Step 6: Configure Lambda Integration
1. **Integration type**: `Lambda Function` (select this)
2. **Lambda Function**: `us-east-2`
3. **Lambda Function**: Type `plagiarism-detection` and select it
4. **Default timeout**: Keep as is
5. Click: **"Create method"**

---

## Step 7: Enable CORS (if not auto-enabled)
1. Click on `/analyze` resource
2. Click: **"Enable CORS"**
3. Click: **"Enable CORS and replace existing CORS headers"**
4. Click: **"Yes, replace existing values"**

---

## Step 8: Deploy API
1. Click: **"Deploy API"**
2. **Stage name**: `prod`
3. **Stage description**: `Production stage`
4. Click: **"Deploy"**

---

## Step 9: Get API Endpoint
1. After deployment, copy the **Invoke URL**
   - Format: `https://[api-id].execute-api.us-east-2.amazonaws.com/prod`
2. Save this URL (you'll need it for Streamlit)

---

## Step 10: Test API Endpoint
```powershell
$api_url = "https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod/analyze"
$headers = @{"Content-Type"="application/json"}
$body = @{
    "action" = "detect-plagiarism"
    "document_name" = "test.pdf"
    "s3_key" = "test.pdf"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$api_url" -Method POST -Headers $headers -Body $body
```

If you get a response, API Gateway is working! ✅

---

## 📝 Next Step

Tell me: **"API Gateway created at https://[YOUR_API_ID].execute-api.us-east-2.amazonaws.com/prod"**

Then I'll update the Streamlit dashboard with your API endpoint and deploy it.

