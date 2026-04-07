#!/usr/bin/env python3
"""
Update Lambda function with new handler code
"""

import boto3
import zipfile
import os
import subprocess

print("🔄 Updating Lambda function...")

# Create new ZIP file with updated handler
print("📦 Creating updated lambda_function.zip...")

# Remove old zip if it exists
if os.path.exists('lambda_function.zip'):
    os.remove('lambda_function.zip')

# Create ZIP
with zipfile.ZipFile('lambda_function.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add main handler
    zf.write('02_lambda_handler.py', arcname='lambda_function.py')
    
    # Add dependencies from venv/lib/python3.10/site-packages
    site_packages = 'venv/Lib/site-packages'
    if os.path.exists(site_packages):
        for root, dirs, files in os.walk(site_packages):
            # Skip unnecessary directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.dist-info', 'tests']]
            
            for file in files:
                if not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, site_packages)
                    zf.write(file_path, arcname=relative_path)

zip_size = os.path.getsize('lambda_function.zip') / 1024 / 1024
print(f"✅ Created: lambda_function.zip ({zip_size:.1f} MB)")

# Update Lambda function
print("\n📤 Uploading to AWS Lambda...")
lambda_client = boto3.client('lambda', region_name='us-east-2')

try:
    with open('lambda_function.zip', 'rb') as f:
        lambda_client.update_function_code(
            FunctionName='plagiarism-detection',
            ZipFile=f.read()
        )
    print("✅ Lambda function updated successfully!")
    
    # Wait for update to complete
    print("⏳ Waiting for Lambda update to complete...")
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='plagiarism-detection')
    print("✅ Lambda is ready!")
    
except Exception as e:
    print(f"❌ Error updating Lambda: {str(e)}")
    print("\n💡 If authentication issues occur, run:")
    print("   aws configure --profile default")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Go to Lambda function in Console")
print("2. Verify the code changes")
print("3. Test using 'Test' button in Lambda")
print("4. Refresh Streamlit Cloud app in browser")
print("5. Try uploading a document again")
