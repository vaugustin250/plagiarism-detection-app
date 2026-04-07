# ✅ END-TO-END TESTING GUIDE

**What This Does**: Verifies that your entire plagiarism detection system works from start to finish.

**Time Estimate**: 15 minutes

**Prerequisites**:
- Lambda configured ✅
- API Gateway deployed ✅
- Streamlit dashboard live ✅

---

## Test 1: Verify Lambda Function

### Check CloudWatch Logs
```powershell
# Get recent Lambda invocations
aws logs describe-log-streams `
  --log-group-name "/aws/lambda/plagiarism-detection" `
  --region us-east-2
```

Expected: Log stream exists with timestamp showing recent activity.

---

## Test 2: Test API Gateway Endpoint Directly

```powershell
# Test the API endpoint
$api_url = "https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod/analyze"
$headers = @{"Content-Type"="application/json"}

# Simple test payload
$body = @{
    "action" = "health-check"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$api_url" -Method POST -Headers $headers -Body $body -ErrorAction SilentlyContinue

if ($response) {
    Write-Host "✅ API Gateway is responding" -ForegroundColor Green
    $response | ConvertTo-Json
} else {
    Write-Host "❌ API Gateway not responding" -ForegroundColor Red
}
```

Expected output:
```
statusCode: 200
body: {"message": "Lambda invoked successfully"}
```

---

## Test 3: Check RDS Database Connection

```powershell
# Test PostgreSQL connection
$pghost = "plagiarism-db.cpmigym2oym2.us-east-2.rds.amazonaws.com"
$pguser = "postgres"
$pgpassword = "Plagiarism123!"
$pgdb = "plagiarism_db"

# Using AWS CLI to test via Lambda
aws lambda invoke `
  --function-name plagiarism-detection `
  --payload '{"test":"db-connection"}' `
  --region us-east-2 `
  response.json

# Check response
Get-Content response.json
```

Expected: Log shows successful database connection.

---

## Test 4: Verify S3 Bucket Access

```powershell
# List S3 bucket contents
aws s3 ls s3://plagiarism-detection-docs-augustin/ --region us-east-2
```

Expected: Bucket accessible (may be empty initially).

---

## Test 5: Test Pinecone Connection

```powershell
# Check if embeddings can be generated
# This is tested when Lambda processes a document

# For now, verify Pinecone API key works:
$pinecone_key = "pcsk_4GCKs_B8a5w9CopdoZvS5pW4ky6HnB6AZ4N6A57C8wkgafQDNLsPA63K4RRqykYakdMcZ"

# Create Python test script
@"
import requests
headers = {'Api-Key': '$pinecone_key'}
response = requests.get('https://api.pinecone.io/indexes', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
"@ | Out-File test_pinecone.py

python test_pinecone.py
```

Expected: Status 200, indexes list returned.

---

## Test 6: Full System Test via Streamlit Dashboard

1. **Open your Streamlit app**: `https://[your-app-name].streamlit.app`

2. **Upload a test document**:
   - Use a simple PDF or DOCX file
   - File size: < 5MB
   - Recommended: Create a test PDF with sample text

3. **Click "Analyze"**

4. **Monitor CloudWatch Logs** (in separate terminal):
   ```powershell
   aws logs tail "/aws/lambda/plagiarism-detection" --follow --region us-east-2
   ```

5. **Wait for Results** (1-2 minutes):
   - Lambda processes document
   - Extracts text from PDF/DOCX
   - Generates embeddings via HuggingFace
   - Searches Pinecone for similar documents
   - Stores results in RDS
   - Returns plagiarism score

6. **Verify Results Display**:
   - ✅ Document name shows correctly
   - ✅ Processing status updates in real-time
   - ✅ Final report shows plagiarism score (0-100%)
   - ✅ AI detection score displays
   - ✅ Similar documents/sources listed

---

## Test 7: Database Verification

After test document is processed, verify RDS data:

```powershell
# Connect to PostgreSQL
# Using psql (if installed) or AWS RDS Query Editor

# Quick AWS CLI method:
$conn_string = "postgresql://postgres:Plagiarism123!@plagiarism-db.cpmigym2oym2.us-east-2.rds.amazonaws.com:5432/plagiarism_db"

# Or use RDS Query Editor in AWS Console:
# 1. AWS Console → RDS → Databases → plagiarism-db
# 2. Click "Query editor"
# 3. Run:

SELECT COUNT(*) FROM documents;
SELECT COUNT(*) FROM plagiarism_reports;
SELECT COUNT(*) FROM similarity_matches;
```

Expected:
- `documents` table has 1+ rows (uploaded file)
- `plagiarism_reports` table has 1+ rows (analysis result)
- `similarity_matches` table has 1+ rows (matched sources)

---

## Test 8: Error Handling Test

1. **Upload invalid file** (e.g., .txt instead of PDF)
   - Expected: Dashboard shows error message
   - Lambda logs show detailed error

2. **Upload oversized file** (> 50MB)
   - Expected: S3 upload fails gracefully
   - Error message displayed in dashboard

3. **Upload with no internet** (local test)
   - Expected: Timeouts handled properly
   - Retry mechanism works

---

## Test Results Checklist

- [ ] Lambda function is active and responding
- [ ] API Gateway returns 200 status code
- [ ] RDS database connection successful
- [ ] S3 bucket accessible
- [ ] Pinecone embeddings working
- [ ] HuggingFace API responding
- [ ] Document uploads to S3 successfully
- [ ] Lambda processes document without errors
- [ ] Results stored in RDS database
- [ ] Streamlit dashboard displays results
- [ ] Plagiarism score calculated (0-100%)
- [ ] AI detection score shows
- [ ] Similar documents listed

---

## Performance Benchmarks

**Typical Processing Times**:
- Document upload: 5-30 seconds (depends on file size)
- Text extraction: 2-5 seconds
- Embedding generation: 10-20 seconds
- Pinecone search: 3-5 seconds
- Results storage: 2-3 seconds
- **Total end-to-end: 30-60 seconds**

**Cost Estimate (First Month)**:
- Lambda: ~$0.10-0.50
- RDS: ~$5.00 (db.t3.micro free tier)
- API Gateway: ~$0.50-2.00
- Pinecone: ~$0.50-5.00
- HuggingFace: ~$0.00-2.00
- **Total: $6-10** (well under free tier limits)

---

## ✅ All Tests Pass?

Congratulations! Your plagiarism detection system is **fully operational** 🎉

**Next Steps**:
1. Share Streamlit link with users
2. Monitor CloudWatch logs for issues
3. Optimize based on usage patterns
4. Consider Streamlit multi-user authentication (optional)

---

## 🐛 Troubleshooting

### Lambda Not Responding
```powershell
# Check function status
aws lambda get-function-configuration --function-name plagiarism-detection --region us-east-2
```

### API Gateway 502 Error
- Check Lambda IAM role has correct permissions
- Verify handler is set to `lambda_function.lambda_handler`
- Check Lambda timeout: should be 300 seconds

### Document Upload Fails
- Verify S3 bucket exists and is accessible
- Check IAM role has S3FullAccess
- Ensure file size < 5MB

### No Results Show
- Check CloudWatch logs for Lambda errors
- Verify RDS password is correct
- Check Pinecone API key is valid
- Confirm HuggingFace API token working

---

## 📊 Monitoring Commands

```powershell
# Monitor Lambda invocations
aws cloudwatch get-metric-statistics `
  --namespace AWS/Lambda `
  --metric-name Invocations `
  --dimensions Name=FunctionName,Value=plagiarism-detection `
  --start-time $(Get-Date).AddHours(-1).ToUniversalTime().ToString('s')Z `
  --end-time $(Get-Date).ToUniversalTime().ToString('s')Z `
  --period 300 `
  --statistics Sum `
  --region us-east-2

# Monitor API Gateway requests
aws cloudwatch get-metric-statistics `
  --namespace AWS/ApiGateway `
  --metric-name Count `
  --start-time $(Get-Date).AddHours(-1).ToUniversalTime().ToString('s')Z `
  --end-time $(Get-Date).ToUniversalTime().ToString('s')Z `
  --period 300 `
  --statistics Sum `
  --region us-east-2
```

