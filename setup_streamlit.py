#!/usr/bin/env python3
"""
Streamlit Dashboard Automation Script
Updates code with API endpoint and prepares for deployment
"""

import os
import shutil
from pathlib import Path

def setup_streamlit():
    print("\n" + "="*60)
    print("🎨 STREAMLIT DEPLOYMENT - SETUP")
    print("="*60)
    
    # The API endpoint
    api_endpoint = "https://uvwsd5vxgc.execute-api.us-east-2.amazonaws.com/prod/analyze"
    
    # Step 1: Read the dashboard code
    print("\n[1/4] Reading Streamlit dashboard code...")
    dashboard_file = "03_streamlit_dashboard.py"
    
    if not os.path.exists(dashboard_file):
        print(f"❌ Error: {dashboard_file} not found")
        return
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✅ Dashboard code loaded ({len(content)} bytes)")
    
    # Step 2: Update API endpoint in code
    print("\n[2/4] Updating API endpoint in code...")
    
    # Replace placeholder API endpoint
    old_patterns = [
        'API_ENDPOINT = "https://',
        "API_ENDPOINT = 'https://",
        'api_url = "https://',
        "api_url = 'https://",
        'endpoint = "https://',
        "endpoint = 'https://",
    ]
    
    updated = False
    for pattern in old_patterns:
        if pattern in content:
            # Find the line and replace the entire URL
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if pattern in line and 'execute-api' not in line:
                    # This is an old placeholder
                    prefix = line.split(pattern)[0] + pattern
                    new_line = f'{prefix}{api_endpoint}"'
                    new_lines.append(new_line)
                    updated = True
                elif api_endpoint in line:
                    # Already has correct endpoint
                    new_lines.append(line)
                    updated = True
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
    
    if not updated:
        # Add API endpoint at the top if not found
        insert_point = content.find("import streamlit")
        if insert_point > 0:
            insert_point = content.find("\n", insert_point) + 1
            new_code = f'API_ENDPOINT = "{api_endpoint}"\n'
            content = content[:insert_point] + new_code + content[insert_point:]
            updated = True
    
    if updated:
        print(f"✅ API endpoint updated: {api_endpoint}")
    else:
        print(f"⚠️  API endpoint may need manual update")
    
    # Step 3: Create .streamlit config
    print("\n[3/4] Creating Streamlit configuration...")
    
    streamlit_dir = ".streamlit"
    os.makedirs(streamlit_dir, exist_ok=True)
    
    config_content = """[theme]
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
headless = true

[logger]
level = "info"
"""
    
    config_file = os.path.join(streamlit_dir, "config.toml")
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Config file created: {config_file}")
    
    # Step 4: Create requirements.txt for Streamlit
    print("\n[4/4] Creating Streamlit requirements...")
    
    streamlit_reqs = """streamlit==1.28.1
pandas==2.0.3
psycopg2-binary==2.9.7
plotly==5.17.0
boto3==1.28.50
requests==2.31.0
python-dotenv==1.0.0
"""
    
    # Check if requirements.txt exists and update it
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            original_reqs = f.read()
        print("✅ Original requirements.txt preserved")
    
    streamlit_reqs_file = "requirements-streamlit.txt"
    with open(streamlit_reqs_file, 'w') as f:
        f.write(streamlit_reqs)
    
    print(f"✅ Streamlit requirements file created: {streamlit_reqs_file}")
    
    # Save updated dashboard
    print("\n[SAVE] Writing updated dashboard code...")
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Updated: {dashboard_file}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ STREAMLIT SETUP COMPLETE!")
    print("="*60)
    print(f"\n📌 Files Created/Updated:")
    print(f"   • 03_streamlit_dashboard.py (updated with API endpoint)")
    print(f"   • .streamlit/config.toml (created)")
    print(f"   • requirements-streamlit.txt (created)")
    print(f"\n📌 API Endpoint Configured:")
    print(f"   {api_endpoint}")
    print(f"\n📌 Next Steps for Deployment:")
    print(f"   1. Create GitHub repo: plagiarism-detection-app")
    print(f"   2. Push these files:")
    print(f"      - 03_streamlit_dashboard.py")
    print(f"      - requirements-streamlit.txt → rename to requirements.txt")
    print(f"      - .streamlit/config.toml")
    print(f"   3. Go to https://share.streamlit.io/")
    print(f"   4. Deploy from GitHub")
    print(f"\n📝 GitHub Setup Commands:")
    print(f"   git init")
    print(f"   git add 03_streamlit_dashboard.py .streamlit/ requirements-streamlit.txt")
    print(f"   git commit -m 'Add Streamlit plagiarism detection app'")
    print(f"   git branch -M main")
    print(f"   git remote add origin https://github.com/YOUR_USERNAME/plagiarism-detection-app.git")
    print(f"   git push -u origin main")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    setup_streamlit()
