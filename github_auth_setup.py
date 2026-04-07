#!/usr/bin/env python3
"""
GitHub Authentication Setup Guide
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║       🔐 GITHUB AUTHENTICATION SETUP                              ║
╚════════════════════════════════════════════════════════════════════╝

❌ ERROR: Git push failed - GitHub authentication required

To fix this, you need to create a Personal Access Token (PAT):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STEP 1: Create Personal Access Token on GitHub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://github.com/settings/tokens/new

2. Fill in the form:
   • Token name: "Streamlit Deployment"
   • Expiration: "90 days" (or as needed)
   • Scopes: REQUIRED: 
     ✓ repo (Full control of private repositories)
       └─ repo:status
       └─ repo_deployment
       └─ public_repo
       └─ repo:invite
       └─ security_events

3. Click: "Generate token"

4. **COPY THE TOKEN IMMEDIATELY** ⚠️
   (You won't see it again!)
   
   It looks like: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STEP 2: Use Token for Git Authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this PowerShell command (paste your token):

$pat = "ghp_YOUR_TOKEN_HERE"  # Replace with your token
$repo = "https://github.com/vaugustin250/plagiarism-detection-app.git"
$url = $repo -replace "https://", "https://oauth2:$pat@"

cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"
git remote remove origin 2>$null
git remote add origin $url
git push -u origin main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 ALTERNATIVE: Use SSH Key (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you have SSH key already configured:

cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"
git remote remove origin 2>$null
git remote add origin git@github.com:vaugustin250/plagiarism-detection-app.git
git push -u origin main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ AFTER PUSH SUCCEEDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You'll see:
  Enumerating objects: 5, done.
  Counting objects: 100% (5/5), done.
  Delta compression using up to 8 threads
  Writing objects: 100% (5/5), 2.34 KiB
  ...
  Branch 'main' set up to track remote branch 'main' from 'origin'

Then go to: https://github.com/vaugustin250/plagiarism-detection-app
Verify your files are there ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 STEP 3: Deploy to Streamlit Cloud
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once code is on GitHub:

1. Go to: https://share.streamlit.io/
2. Click: "New app"
3. Fill in:
   • GitHub repo: vaugustin250/plagiarism-detection-app
   • Branch: main
   • Main file path: 03_streamlit_dashboard.py
4. Click: "Deploy"

⏳ Wait 2-3 minutes for deployment

Your URL: https://[your-app-name].streamlit.app

╔════════════════════════════════════════════════════════════════════╗
║  Follow the STEP 2 above with your Personal Access Token!        ║
╚════════════════════════════════════════════════════════════════════╝
""")
