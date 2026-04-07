#!/usr/bin/env python3
"""
Git Setup Script for Streamlit Deployment
Prepares local git repository and shows GitHub instructions
"""

import os
import subprocess

def run_command(cmd, description):
    """Run a shell command and report results"""
    print(f"\n▶️  {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    print(f"      {line}")
            return True
        else:
            print(f"   ⚠️  {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def setup_git():
    print("\n" + "="*70)
    print("🔧 GIT SETUP FOR STREAMLIT DEPLOYMENT")
    print("="*70)
    
    # Step 1: Check if git is initialized
    print("\n[STEP 1] Checking git status...")
    if os.path.exists(".git"):
        print("✅ Git repository already initialized")
    else:
        print("⚠️  Git not initialized yet - will initialize now")
        run_command("git init", "Initialize git repository")
    
    # Step 2: Check git config
    print("\n[STEP 2] Setting up git configuration...")
    run_command('git config user.email "developer@plagiarism-detection.local"', "Set git email")
    run_command('git config user.name "Plagiarism Detection Developer"', "Set git name")
    
    # Step 3: Create .gitignore
    print("\n[STEP 3] Creating .gitignore file...")
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local
.env.*.local

# Secrets
secrets.json
credentials.json

# Streamlit
.streamlit/secrets.toml

# MacOS
.DS_Store

# Project specific
lambda_function.zip
*.pyc
*.log
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ .gitignore created")
    
    # Step 4: Stage files
    print("\n[STEP 4] Staging files for deployment...")
    files_to_add = [
        "03_streamlit_dashboard.py",
        "requirements-streamlit.txt",
        ".streamlit/config.toml",
        ".gitignore"
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            run_command(f'git add "{file}"', f"Add {file}")
        else:
            print(f"⚠️  File not found: {file}")
    
    # Step 5: Check git status
    print("\n[STEP 5] Checking staged files...")
    result = subprocess.run("git status", shell=True, capture_output=True, text=True)
    print(result.stdout)
    
    # Step 6: Create initial commit (if not already committed)
    print("\n[STEP 6] Creating initial commit...")
    result = subprocess.run("git log -1 --oneline", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        # No commits yet
        run_command(
            'git commit -m "Add plagiarism detection Streamlit app with API integration"',
            "Create initial commit"
        )
    else:
        print("✅ Repository already has commits")
    
    # Step 7: Show branch status
    print("\n[STEP 7] Checking branch...")
    result = subprocess.run("git branch", shell=True, capture_output=True, text=True)
    current_branch = result.stdout.strip()
    print(f"✅ Current branch: {current_branch}")
    
    # Summary and instructions
    print("\n" + "="*70)
    print("✅ LOCAL GIT SETUP COMPLETE!")
    print("="*70)
    
    print("\n📋 NEXT STEPS - GITHUB SETUP (Required):")
    print("""
1️⃣  GO TO GITHUB:
    https://github.com/new

2️⃣  CREATE REPOSITORY:
    • Repository name: plagiarism-detection-app
    • Description: AI-powered plagiarism detection system
    • Visibility: PUBLIC (required for Streamlit Cloud)
    • Do NOT initialize with README or gitignore
    • Click "Create repository"

3️⃣  AFTER CREATING THE REPO, RUN THESE COMMANDS:
    
    $repo_url = "https://github.com/YOUR_USERNAME/plagiarism-detection-app.git"
    git remote add origin $repo_url
    git branch -M main
    git push -u origin main

    (Replace YOUR_USERNAME with your GitHub username)

4️⃣  DEPLOY TO STREAMLIT:
    • Go to: https://share.streamlit.io/
    • Click: "New app"
    • Select GitHub repo: YOUR_USERNAME/plagiarism-detection-app
    • Branch: main
    • Main file path: 03_streamlit_dashboard.py
    • Click: "Deploy"

5️⃣  WAIT FOR DEPLOYMENT:
    Streamlit will build and deploy your app (~2-3 minutes)
    You'll get a URL like: https://[your-app-name].streamlit.app
""")
    
    print("\n" + "="*70)
    print("📢 IMPORTANT:")
    print("   Your repo is ready to push!")
    print("   1. Create the GitHub repo first (Step 1-2 above)")
    print("   2. Then run the git push commands (Step 3)")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        setup_git()
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
