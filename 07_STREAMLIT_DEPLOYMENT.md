# 🎨 STREAMLIT DASHBOARD DEPLOYMENT GUIDE

**What This Does**: Deploys your plagiarism detection web interface to Streamlit Cloud.

**Time Estimate**: 10 minutes

**Prerequisites**:
- API Gateway endpoint created and tested (from previous step)
- GitHub account (free)

---

## Step 1: Update Streamlit Code with API Endpoint

Edit your `03_streamlit_dashboard.py` file and replace the API endpoint:

```python
# At the top of the file, replace with YOUR API endpoint
API_ENDPOINT = "https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod/analyze"
```

Save the file.

---

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. **Repository name**: `plagiarism-detection-app`
3. **Description**: `AI-powered plagiarism detection system`
4. **Public** (important for Streamlit Cloud)
5. Click: **"Create repository"**

---

## Step 3: Upload Project Files to GitHub

1. From your local folder (`c:\Users\Nandha Kumar S K\Downloads\files (3)`)
2. Upload these files to GitHub:
   - `03_streamlit_dashboard.py` (main app)
   - `requirements.txt` (dependencies)
   - `.streamlit/` folder (if config exists)

Or use Git commands:
```powershell
cd "c:\Users\Nandha Kumar S K\Downloads\files (3)"
git init
git add 03_streamlit_dashboard.py requirements.txt
git commit -m "Add Streamlit dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/plagiarism-detection-app.git
git push -u origin main
```

---

## Step 4: Create Streamlit Config (Optional)

Create `.streamlit/config.toml` in your GitHub repo:

```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "minimal"

[server]
port = 8501
maxUploadSize = 200
```

---

## Step 5: Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Click: **"New app"**
3. **GitHub repository**: `YOUR_USERNAME/plagiarism-detection-app`
4. **Branch**: `main`
5. **Main file path**: `03_streamlit_dashboard.py`
6. Click: **"Deploy"**

---

## Step 6: Wait for Deployment

Streamlit will:
1. Clone your GitHub repo
2. Install dependencies from `requirements.txt`
3. Run the Streamlit app
4. Give you a unique URL: `https://[your-app-name].streamlit.app`

**Deployment takes 2-3 minutes** ⏳

---

## Step 7: Test the Dashboard

1. When deployment is done, you'll see the app at `https://[your-app-name].streamlit.app`
2. Test by:
   - Uploading a PDF or DOCX document
   - Clicking "Analyze"
   - Wait for processing (typically 30-60 seconds)
   - See plagiarism report with:
     - **Overall Plagiarism Score** (0-100%)
     - **AI Detection Score** (ChatGPT/GPT-4 detection)
     - **Similar Documents** (matched sources)

---

## Step 8: Update Dashboard Settings (Optional)

To change appearance, edit `.streamlit/config.toml` and push to GitHub. Streamlit auto-reloads.

---

## 📊 Environment Variables for Streamlit

If you need to store sensitive data, use Streamlit Secrets:

1. Go to: `https://share.streamlit.io/`
2. Click on your app → Settings → Secrets
3. Add:
```
API_ENDPOINT = "https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod/analyze"
```

4. In your code:
```python
import streamlit as st
api_endpoint = st.secrets["API_ENDPOINT"]
```

---

## ✅ When Dashboard is Live

Tell me: **"Streamlit dashboard deployed at https://[your-app-name].streamlit.app"**

Then I'll create the **end-to-end testing guide** to verify everything works together!

