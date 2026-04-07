#!/usr/bin/env python3
"""
Streamlit Secrets Setup Guide - AWS Credentials for S3
"""

guide = """
╔════════════════════════════════════════════════════════════════════╗
║  ⚠️  AWS CREDENTIALS NEEDED FOR S3 ACCESS                         ║
╚════════════════════════════════════════════════════════════════════╝

Your Streamlit Cloud dashboard needs AWS credentials to upload files to S3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STEP 1: Get Your AWS Credentials
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Go to: AWS Console → IAM → Users → augustin

Click: "Security credentials" tab

Scroll: "Access keys"

Click: "Create access key" (if you don't have one)

Copy:
  • Access Key ID: AKIA...
  • Secret Access Key: ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STEP 2: Add to Streamlit Secrets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://share.streamlit.io/

2. Click your app: plagiarism-detection-app

3. Click: "⋮" menu → "Settings"

4. Click: "Secrets"

5. Paste this with YOUR credentials:

```
AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY"
AWS_DEFAULT_REGION = "us-east-2"
```

⚠️ IMPORTANT: Replace YOUR_ACCESS_KEY_ID and YOUR_SECRET_ACCESS_KEY with your actual values!

6. Click: "Save"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Your Dashboard Will Now:

1. Read AWS credentials from Streamlit Secrets
2. Upload PDF to S3 directly
3. Call Lambda with S3 path (small request)
4. Get results back

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(guide)
