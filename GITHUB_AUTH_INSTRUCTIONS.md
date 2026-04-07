# GitHub Authentication Setup

## Problem
Git push failed with: "Permission to vaugustin250/plagiarism-detection-app.git denied"

This is because GitHub requires authentication via Personal Access Token (PAT) instead of passwords.

## Solution

### Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens/new
2. Enter name: "Streamlit Deployment"  
3. Select Expiration: "90 days"
4. Check scope: "repo" (full control of private repositories)
5. Scroll down, click "Generate token"
6. COPY THE TOKEN IMMEDIATELY (you won't see it again!)
   - Looks like: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

### Step 2: Use Token to Push to GitHub

Run these PowerShell commands:

```powershell
# Replace YOUR_TOKEN_HERE with the token you copied above
$pat = "ghp_YOUR_TOKEN_HERE"
$repo = "https://github.com/vaugustin250/plagiarism-detection-app.git"
$url = $repo -replace "https://", "https://oauth2:$pat@"

cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"

# Remove old origin if it exists
git remote remove origin 2>$null

# Add new origin with authentication
git remote add origin $url

# Push to GitHub
git push -u origin main
```

### Example
```powershell
$pat = "ghp_1234567890abcdefghijklmnop"
$repo = "https://github.com/vaugustin250/plagiarism-detection-app.git"
$url = $repo -replace "https://", "https://oauth2:$pat@"

cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"
git remote remove origin 2>$null
git remote add origin $url
git push -u origin main
```

### Expected Output
You should see:
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 2.34 KiB
Total 5 (delta 0), reused 0 (delta 0)
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

## Verify Push Success

Go to: https://github.com/vaugustin250/plagiarism-detection-app

You should see your files:
- 03_streamlit_dashboard.py
- requirements-streamlit.txt  
- .streamlit/config.toml
- .gitignore

## Next: Deploy to Streamlit Cloud

Once verified:
1. Go to: https://share.streamlit.io/
2. Click: "New app"
3. Select repo: vaugustin250/plagiarism-detection-app
4. Branch: main
5. File: 03_streamlit_dashboard.py
6. Click: "Deploy"

Wait 2-3 minutes, then get your live URL!
